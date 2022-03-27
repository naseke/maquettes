"""
Partie client
"""

# Copyright (C) Nicolas SALLARES
# Distributed under the terms of the AGPL License.


import zmq
from lib import couleurs, contantes
from lib.utils import bytes_dict, dict_bytes


class ClientBase:
    """
       I7 : init
       I8 : init msg
    """
    def __init__(self, host: str, port: str, name: str=None, debug :bool=False):
        self.cnx = zmq.Context()
        self.sockets = []
        self.server_name = name
        self.socket = None
        self._debug = debug
        self.poller = zmq.Poller()
        self.host = host
        self.port = port
        self.reply = 1

    def msg_send(self, i: int, **dico): ...
    def msg_create(self, i: int=0, cmd_s :str='', cmd_c: str='', msg: str=''): ...
    def recv_rep(self): ...
    def trt_cmd_other(self): ...
    def est_avec_enveloppe(self):
        return self.server_name is not None

    def add_socket(self, model: int) -> zmq.Context.socket:
        tmp = self.cnx.socket(model)
        if self.est_avec_enveloppe:
            tmp.setsockopt(zmq.IDENTITY, self.server_name.encode())
        tmp.connect(f"tcp://{self.host}:{self.port}")
        self.poller.register(tmp, zmq.POLLIN)
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Ajout du port {model}")
        return tmp


class ClientReq(ClientBase):

    def __init__(self, host: str, port: str, name: str=None, debug: bool=False):
            super().__init__(host, port, name, debug)
            self.sockets.append(self.add_socket(zmq.REQ))

    def msg_send(self, i: int = 0, **dico):  # I8

        for i in range(self.reply):
            # gestion des exceptions à faire
            self.sockets[0].send(bytes_dict(**dico))
            socks = dict(self.poller.poll(2000))
            if self._debug: couleurs.AffichageColor().msg_DEBUG(f"poller : {socks} | sockets {self.sockets}")

            if self.sockets[0] in socks:
                message = self.sockets[0].recv_multipart()  # I8
                if self._debug: couleurs.AffichageColor().msg_DEBUG(f"(Clt) Message reçu : {message}")
                if dict_bytes(message[0])['cmd'] == contantes.MSG_CTRL_OK:
                    couleurs.AffichageColor().msg_OK("message bien envoyé")
                    return 0
                if dict_bytes(message[0])['cmd'] == contantes.MSG_CTRL_PONG:
                    couleurs.AffichageColor().msg_OK("PONG!")
                    return 0

        couleurs.AffichageColor().msg_FAIL("Erreur durant l'envoie")
        return 1


    def msg_create(self,cmd: str, msg: str=''):  # I8
            dico = {
                'cmd': cmd,
            }

            if msg != '':
                dico.update({'data': msg})

            return dico
def main():
    host = '192.168.1.9'
    port = '5555'

    s = ClientReq(host, port, 'Toi', True)
    s.msg_send(**s.msg_create(contantes.MSG_CTRL_PING))
    s.msg_send(**s.msg_create(contantes.MSG_CTRL_PING))
    s.msg_send(**s.msg_create(contantes.MSG_CTRL_PING))

if __name__ == "__main__": main()