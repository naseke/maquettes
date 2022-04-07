"""
M1 All Servers
"""

# Copyright (C) Nicolas SALLARES
# Distributed under the terms of the AGPL License.

import asyncio
import zmq
import zmq.asyncio
from threading import Thread
from lib.utils import generation_nom, dict_bytes, bytes_dict
from lib import couleurs, contantes, ordonnanceur
from random import randint
from lib.parametres import Params
from Client import ClientReq
from time import sleep


class ServerBase:
    """
    I6 : init
    I8 : init msg
    """

    def __init__(self, host: str, port: str , debug: bool = False):
        self.cnx = zmq.Context()
        self.sockets = []
        self.lst_nodes = {}
        self.client = None
        self.poller = zmq.Poller()
        self.poller.poll(1000)
        self._debug = debug
        self.boucle = 0
        self.host = host
        self.port = port
        self.__is_start = False
        self.name = generation_nom()
        self.node = []
        self.ordo = ordonnanceur.OrdoSvr()
        self.ordo_thread = None



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

    def start(self):
        self.__is_start = True
        self.msg_welcome()

    def stop(self):
        self.__is_start = False

    def is_start(self):
        return self.__is_start

    def add_socket(self, model: int) -> zmq.Context.socket:
        tmp = self.cnx.socket(model)
        tmp.bind(f"tcp://{self.host}:{self.port}")
        self.poller.register(tmp, zmq.POLLOUT)
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Ajout du port {model}")
        return tmp

    def suppr_socket(self, soc: zmq.Context.socket):
        self.poller.unregister(soc)
        #soc.close()

class M1P1(ServerBase):

    def __init__(self, host, port, debug=False):
        super().__init__(host, port, debug)


    def start(self):
        super().start()
        couleurs.AffichageColor().msg_INFO(msg=f"Nom du server : {self.name}\n"
                                               f"Host : {self.host}\n"
                                               f"Port : {self.port}")
        self.sockets.append(self.add_socket(zmq.ROUTER))
        self.ordo_thread = Thread(target=self.ordo.start, daemon=True)
        self.ordo_thread.start()
        self.process_startup()
        while self.is_start():
            couleurs.AffichageColor().msg_INFO(f"boucle n°{self.boucle}")
            delais = randint(1, 10)
            self.ordo.add_task('send_msg', False, self, seconds=delais)
            self.boucle += 1
            try:
                self.msg_listen()
            except KeyboardInterrupt:
                self.stop()


    def stop(self):
        super().stop()
        self.ordo.stop()
        couleurs.AffichageColor().msg_WARNING("Arrêt du serveur")

    def msg_listen(self):
        socks = dict(self.poller.poll(500))  # Tick

        if self.sockets[0] in socks:
            message = self.sockets[0].recv_multipart()  # I8
            if self._debug: couleurs.AffichageColor().msg_DEBUG(f"(Srv) Message reçu : {message}")
            msg_rep = self.trt_msg(*message)
            self.msg_send_reponse(msg_rep)


    def bytes_2_each_elem_lst(self, *lst: list): # pour le turfu
        return [elem.encode() for elem in lst]

    def process_startup(self):
        # init d'une connexion tmp
        # clt = ClientReq(Params().PARAMS['node_host2'], Params().PARAMS['node_port2'], self.name)

        # envoie d'un ping
        # clt.msg_send(**clt.msg_create(contantes.MSG_CTRL_PING))


        # envoie de la reconnaissance mutuelle
        nom = None
        # ajout du client
        # self.lst_nodes_add(Params().PARAMS['node_host2'], Params().PARAMS['node_port2'], nom)

        # envoie de la demande de table


    def lst_nodes_add(self, host: str, port: str, nom: str = None):
        self.lst_nodes.update(ClientReq(host, port, nom))
        print(self.lst_nodes)

    def msg_send_reponse (self, rep: list):
        self.sockets[0].send_multipart(rep)
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Envoie de la confirmation  : {rep[2].decode()}")
        print(f"{rep[0].decode()}: {rep[2].decode()}")


    def trt_msg(self, *msg: list): # -> list #I8 /I9
        # il manque plein de chose pour le moment
        rep = {}
        if len(msg) == 3:  # avec enveloppe
            t = dict_bytes(msg[2])
            if t['cmd'] == contantes.MSG_CTRL_PING:
                couleurs.AffichageColor().msg_OK("PING!")
                rep['cmd'] = contantes.MSG_CTRL_PONG
                env = [msg[0], msg[1], bytes_dict(**rep)]
            elif t['cmd'] == contantes.MSG_ORD_PRINT:
                couleurs.AffichageColor().msg_OK(t['data'])
                rep['cmd'] = contantes.MSG_CTRL_OK
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

    def msg_send_like_exo(self): #I11

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
            # sleep(delais)
            # if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Envoie du Ping")

            clt = ClientReq(self.node[0], self.node[1], self.name, debug=False)
            #clt.msg_send(**clt.msg_create(contantes.MSG_CTRL_PING))
            clt.msg_send(**clt.msg_create(contantes.MSG_ORD_PRINT, phrases[phrase]))

        except KeyboardInterrupt:
            self.stop()

def main():

    t = M1P1(Params().PARAMS['node_host'], Params().PARAMS['node_port'], debug=False)

    #Pour le moment
    t.node=[Params().PARAMS['node_host'], Params().PARAMS['node_port2']]

    # t = M1P1("192.168.1.9", "5555", debug=False)
    t.start()

if __name__ == "__main__": main()
