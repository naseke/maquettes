from lib import utils
import zmq
import multiprocessing
from random import randint
import time
import workers

class Client:
    """
    Class racine
    """
    def __init__(self, url: str = '', debug: bool = False) -> None:
        self.context = zmq.Context()
        self.soc = self.context.socket(zmq.REQ)
        self.url = url
        self._debug = debug
        self.name = utils.generation_nom_node()
        self.soc.identity = self.name.encode()
        self.soc.setsockopt(zmq.RCVTIMEO, 10000)
        self.soc.setsockopt(zmq.LINGER, 0)
        self.soc.connect(self.url)

    def start(self) -> None:
        self.demarrage()

        while True:
            self.soc.send_multipart(self.msg_envoie())

            if self._debug: print("send...")
            msg = None
            try:
                msg = self.soc.recv()
            except zmq.error.Again:
                print(f"pas de donnée")
                break
            except KeyboardInterrupt:
                exit()

            if msg is not None:
                self.trt_msg_recu(msg)

    def demarrage(self) -> None: ...

    def msg_envoie(self) -> list: ...

    def trt_msg_recu(self,msg: bytes) -> None: ...



class ClientTestPrint(Client):

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

    def __init__(self, url: str = '', debug: bool = False) -> None:
        super().__init__(url, debug)

    def start(self):

        while True:
            delais = randint(1, 10)
            phrase = self.phrases[randint(0, 9)]
            time.sleep(delais)
            """
                format de message init d'un client :
                service | commande, '', <données>
                Dans un premier temps 1 service = 1 commande 
            """
            self.soc.send_multipart([b"print", b"", phrase.encode()])
            if self._debug: print("send...")
            msg = None
            try:
                msg = self.soc.recv()
            except zmq.error.Again:
                print(f"pas de donnée")
                break
            except KeyboardInterrupt:
                exit()

            if msg is not None:
                if type(msg) == bytes:
                    print(f"reçu : {msg.decode()}")
            # time.sleep(1)


class ClientTestAfficher(Client):

    # phrases venant du site http://romainvaleri.online.fr/ générateur de phrase

    phrases = [
        "La Tunisie déferle au large des Philippines.",
        "Un tiers des violoncellistes blasphémeront.",
        "Est-ce que tu presseras un sujet avec les cheminots ?",
        "Des paléontologues adoraient grossièrement ces organigrammes.",
        "Ces gens-là renverseront du code Javascript avec brio !",
        "Barbara Bush portant Simone De Beauvoir sur son dos farfouille au Soudan.",
        "Pourquoi la présentatrice de la météo abandonnera-t-elle ?",
        "La Panthère Rose s'approche d'orphelins pendant les vacances scolaires.",
        "Un noctambule souhaitait méditer sur beaucoup de conciles.",
        "Dans quelle mesure oublierons-nous de prendre note d'un réacteur ?"
    ]

    def __init__(self, url: str = '', debug: bool = False) -> None:
        super().__init__(url, debug)

    def start(self):

        while True:
            delais = randint(1, 10)
            phrase = self.phrases[randint(0, 9)]
            time.sleep(delais)
            """
                format de message init d'un client :
                service | commande, '', <données>
                Dans un premier temps 1 service = 1 commande 
            """
            self.soc.send_multipart([b"Afficher", b"", phrase.encode()])
            if self._debug: print("send...")
            msg = None
            try:
                msg = self.soc.recv()
            except zmq.error.Again:
                print(f"pas de donnée")
                break
            except KeyboardInterrupt:
                exit()

            if msg is not None:
                if type(msg) == bytes:
                    print(f"reçu : {msg.decode()}")
            # time.sleep(1)


class ClientMultiCommand(Client):
    def __init__(self, url: str = '', debug: bool = False) -> None:
        super().__init__(url, debug)

    def start(self):
        pass


def clientTestPrint_use(url: str = '', debug: bool = False) -> None:
    o = ClientTestPrint(url, debug)
    o.start()

def clientTestAfficher_use(url: str = '', debug: bool = False) -> None:
    o = ClientTestAfficher(url, debug)
    o.start()


def main():

    proc = multiprocessing.Process(target=script)
    proc.daemon = True
    proc.start()

    def init_soc():
        soc = zmq.Context().socket(zmq.REP)
        soc.bind('ipc://frontend.ipc')
        return soc

    soc = init_soc()
    msg = soc.recv()
    print(f'main1 : {msg.decode("utf8")}')
    soc.send(b'ok')
    soc.close()
    soc = init_soc()



if __name__ == "__main__": main()