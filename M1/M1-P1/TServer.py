import multiprocessing
import asyncio
import zmq
import zmq.asyncio
from lib.utils import generation_nom, dict_bytes, bytes_dict
from lib import couleurs, contantes
from random import randint
from lib.parametres import Params
from Client import ClientReq
from time import sleep


class ServerBase(multiprocessing.Process):
    """
    I6 : init
    I8 : init msg
    """

    def __init__(self, host: str, port: str, debug: bool = False):
        multiprocessing.Process.__init__(self)
        self.cnx = None
        self.sockets = []
        self.lst_nodes = {}
        self.client = None
        self._debug = debug
        self.boucle = 0
        self.host = host
        self.port = port
        self.__is_start = False
        self.node = []
        self.name = generation_nom()
        self.poller = zmq.Poller()
        self.timeout = 1000

    async def start(self):
        super().start()

    async def run(self):
        """Init"""
        self.cnx = zmq.asyncio.Context()

        """Run"""
        self.__is_start = True
        self.msg_welcome()

    async def stop(self):
        self.__is_start = False

    async def is_start(self):
        return self.__is_start

    def msg_welcome(self):
        couleurs.AffichageColor().msg_INFO(msg="""
           _____                                         _   __  __                  _              __      ___      _                           _ 
          / ____|                                       | | |  \/  |                (_)             \ \    / (_)    | |                         | |
         | |  __  ___   ___   ___   ___   ___   ___   __| | | \  / | ___  _ __ _ __  _ _ __   __ _   \ \  / / _  ___| |_ _ __ ___   __ _ _ __   | |
         | | |_ |/ _ \ / _ \ / _ \ / _ \ / _ \ / _ \ / _` | | |\/| |/ _ \| '__| '_ \| | '_ \ / _` |   \ \/ / | |/ _ \ __| '_ ` _ \ / _` | '_ \  | |
         | |__| | (_) | (_) | (_) | (_) | (_) | (_) | (_| | | |  | | (_) | |  | | | | | | | | (_| |    \  /  | |  __/ |_| | | | | | (_| | | | | |_|
          \_____|\___/ \___/ \___/ \___/ \___/ \___/ \__,_| |_|  |_|\___/|_|  |_| |_|_|_| |_|\__, |     \/   |_|\___|\__|_| |_| |_|\__,_|_| |_| (_)
                                                                                              __/ |                                                
                                                                                             |___/                                                 

         It's gonna be hot and wet! That's nice if you're with a lady, but it ain't no good if you're in the jungle.
         What does three up and three down mean to you Airman ? une pub Citroën ! (End of an inning !)""", bold=True)

    async def add_socket(self, model: int) -> zmq.Context.socket:
        tmp = self.cnx.socket(model)
        tmp.bind(f"tcp://{self.host}:{self.port}")
        await self.poller.register(tmp, zmq.POLLIN)
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Ajout du port {model}")
        return tmp

    async def suppr_socket(self, soc: zmq.Context.socket):
        await self.poller.unregister(soc)
        # soc.close()

class M1P1(ServerBase):

    def __init__(self, host, port, debug=False):
        super().__init__(host, port, debug)

    async def run(self):
        asyncio.run(super().run())
        couleurs.AffichageColor().msg_INFO(msg=f"Nom du server : {self.name}\n"
                                               f"Host : {self.host}\n"
                                               f"Port : {self.port}")
        self.sockets.append(await self.add_socket(zmq.ROUTER))
        await self.process_startup()
        while self.is_start():
            couleurs.AffichageColor().msg_INFO(f"boucle n°{self.boucle}")
            self.boucle += 1
            try:
                await self.msg_listen()
                await self.msg_send_like_exo()
            except KeyboardInterrupt:
                await self.stop()

    async def stop(self):
        await super().stop()
        couleurs.AffichageColor().msg_WARNING("Arrêt du serveur")

    async def msg_listen(self):
        try:
            socks = dict(self.poller.poll(1000))  # Tick

            if self.sockets[0] in socks:
                message = await self.sockets[0].recv_multipart()  # I8
                if self._debug: couleurs.AffichageColor().msg_DEBUG(f"(Srv) Message reçu : {message}")
                msg_rep = await self.trt_msg(*message)
                await self.msg_send_reponse(msg_rep)

        except KeyboardInterrupt:
            await self.stop()


    def bytes_2_each_elem_lst(self, *lst: list): # pour le turfu
        return [elem.encode() for elem in lst]

    async def process_startup(self):
        # init d'une connexion tmp
        # clt = ClientReq(Params().PARAMS['node_host2'], Params().PARAMS['node_port2'], self.name)

        # envoie d'un ping
        # clt.msg_send(**clt.msg_create(contantes.MSG_CTRL_PING))


        # envoie de la reconnaissance mutuelle
        nom = None
        # ajout du client
        # self.lst_nodes_add(Params().PARAMS['node_host2'], Params().PARAMS['node_port2'], nom)

        # envoie de la demande de table

    async def lst_nodes_add(self, host: str, port: str, nom: str = None):
        self.lst_nodes.update(ClientReq(host, port, nom))
        print(self.lst_nodes)

    async def msg_send_reponse (self, rep: list):
        await self.sockets[0].send_multipart(rep)
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Envoie de la confirmation  : {rep[2].decode()}")
        print(f"{rep[0].decode()}: {rep[2].decode()}")

    async def trt_msg(self, *msg: list): # -> list #I8 /I9
        # il manque plein de chose pour le moment
        rep = {}
        if len(msg) == 3:  # avec enveloppe
            t = dict_bytes(msg[2])
            if t['cmd'] == contantes.MSG_CTRL_PING:
                couleurs.AffichageColor().msg_OK("PING!")
                rep['cmd'] = contantes.MSG_CTRL_PONG
                env = [msg[0], msg[1], bytes_dict(**rep)]
            else:
                rep['cmd'] = contantes.MSG_CTRL_OK
                env = [msg[0], msg[1], bytes_dict(**rep)]
        elif len(msg) == 1:  # sans enveloppe (cas introuvable pour le moment)
            rep['cmd'] = contantes.MSG_CTRL_OK
            env = [msg[0], msg[1], bytes_dict(**rep)]
        else:
            rep['cmd'] = contantes.MSG_CTRL_KO
            env = [msg[0], msg[1], bytes_dict(**rep)]

        # Question : quelle fonction doit traiter la transformation en bytes du message ?

        return env

    async def msg_send_like_exo(self): #I11

        # phrases venant du site http://romainvaleri.online.fr/ générateur de phrase

        phrases = [
            "Les sénégalais aux pupilles dilatées s'inscrivaient.",
            "Une française allait réfléchir.",
            "Des justicières cryptent-elles le scaphandre ?",
            "Le marchand de sable se gavera de mes superbes péchés.",
            "Tu branches cette apparition en croquant la connerie.",
            "Pierre Bellemare s'entraine à s'attaquer à une pomme.",
            "Des amiraux rendaient ces frocs.",
            "Le pentagone ne s'inspire guère de seize cyclomotoristes.",
            "La chômeuse fait main basse sur une allégorie.",
            "La partenaire rapait tes genoux avec des choristes."
        ]

        #for node in self.

        try:
            delais = randint(1, 10)
            phrase = randint(0, 9)
            sleep(delais)
            if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Envoie du Ping")
            clt = ClientReq(self.node[0], self.node[1], self.name, debug=True)
            await clt.msg_send(**clt.msg_create(contantes.MSG_CTRL_PING))

        except KeyboardInterrupt:
            await self.stop()


def main():

    t = M1P1(Params().PARAMS['node_host'], Params().PARAMS['node_port'], debug=True)

    # Pour le moment
    t.node = [Params().PARAMS['node_host'], Params().PARAMS['node_port2']]

    # t = M1P1("192.168.1.9", "5555", debug=False)
    asyncio.run(t.start())
    try:
        t.join()
    except KeyboardInterrupt:
        t.terminate()


if __name__ == "__main__": main()
