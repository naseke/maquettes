"""
Partie client
"""

# Copyright (C) Nicolas SALLARES
# Distributed under the terms of the AGPL License.


import zmq
from lib import couleurs, contantes
from lib.utils import bytes_dict


class ClientBase:
    """
       I7 : init
       I8 : init msg
    """
    def __init__(self, host: str, port: str, name: str=None, debug :bool=False):
        self.cnx = zmq.Context()
        self.server_name = name
        self.sockets = []
        self.socket = None
        self._debug = debug
        self.poller = zmq.Poller()
        self.host = host
        self.port = port

    def send_msg(self, i: int, **dico):
        pass

    def create_msg(self, i: int=0, cmd_s :str='', cmd_c: str='', msg: str=''):
        pass

    def recv_rep(self):
        pass

    def trt_cmd_other(self):
        pass

    def est_avec_enveloppe(self):
        return self.server_name is not None

    def add_socket(self, model: int) -> zmq.Context.socket:
        tmp = self.cnx.socket(model)
        if self.est_avec_enveloppe:
            tmp.setsockopt(zmq.IDENTITY, self.server_name.encode())
        tmp.connect(f"tcp://{self.host}:{self.port}")
        self.poller.register(tmp, zmq.POLLIN )
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Ajout du port {model}")
        return tmp


class ClientReq(ClientBase):

    def __init__(self, host: str, port: str, name: str=None, debug: bool=False):
            super().__init__(host, port, name, debug)
            self.sockets.append(self.add_socket(zmq.REQ))

    def send_msg(self,i: int=0, **dico): # I8
        self.sockets[0].send(bytes_dict(**dico))

        socks = dict(self.poller.poll(1000))
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"poller : {socks} | sockets {self.sockets}")

        if self.sockets[0] in socks:
            message = self.sockets[0].recv()  # I8
            if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Message reçu : {message.decode()}")
            if message.decode() == contantes.MSG_CTRL_OK:
                couleurs.AffichageColor().msg_OK("message bien envoyé")
            else:
                couleurs.AffichageColor().msg_FAIL("Erreur durant l'envoie")

    def create_msg(self, i: int = 0, cmd_s: str = '', cmd_c: str = '', msg: str=''): # I8
            dico = {
                'data': msg
            }
            return dico
def main():
    host = '192.168.1.9'
    port = '5555'

    s = ClientReq(host, port, 'moi', True)
    s.send_msg(**s.create_msg(msg="toto"))

if __name__ == "__main__": main()