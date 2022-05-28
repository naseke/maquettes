"""
Partie client
"""

# Copyright (C) Nicolas SALLARES
# Distributed under the terms of the AGPL License.

import asyncio
import zmq
#import zmq.asyncio
import threading
from lib import couleurs, contantes
from lib.utils import bytes_dict, dict_bytes


class ClientBase(threading.Thread):
    """
       I7 : init
       I8 : init msg
    """
    def __init__(self, host: str, port: str, name: str=None, debug :bool=False):
        threading.Thread().__init__()
        self.cnx = zmq.Context()
        self.sockets = []
        self.server_name = name
        self.socket = None
        self._debug = debug
        self.poller = zmq.Poller()
        self.host = host
        self.port = port
        self.reply = 3
        self.cmd = ''

    def msg_send(self, i: int, **dico): ...
    def msg_create(self, i: int=0, cmd_s :str='', cmd_c: str='', msg: str=''): ...
    def recv_rep(self): ...
    def trt_cmd_other(self): ...
    def run(self): ...
    def start(self): ...

    def est_avec_enveloppe(self):
        return self.server_name is not None

    def add_socket(self, model: int) -> zmq.Context.socket:
        tmp = zmq.Socket(self.cnx, model)
        if self.est_avec_enveloppe:
            tmp.setsockopt(zmq.IDENTITY, self.server_name.encode())
        tmp.connect(f"tcp://{self.host}:{self.port}")
        self.poller.register(tmp, zmq.POLLOUT)
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Ajout du port {model}")
        return tmp


class ClientReq(ClientBase):

    def __init__(self, host: str, port: str, cmd: str='', name: str=None, debug: bool=False):
        super().__init__(host, port, name, debug)
        self.sockets.append(self.add_socket(zmq.REQ))
        self.cmd = cmd

    def run(self):
        # self.msg_send(self.msg_create(self.cmd))

    # def msg_send(self, i: int = 0, **dico):  # I8

        for i in range(1, self.reply):
            # gestion des exceptions à faire
            if self._debug: couleurs.AffichageColor().msg_DEBUG(f"tentative n° {i}")
            self.sockets[0].send(bytes_dict(**self.msg_create(self.cmd)))
            socks = dict(self.poller.poll(1000))
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
            if self._debug: couleurs.AffichageColor().msg_DEBUG(f"tentative n° {i} pas de retour du serveur ...")
            self.sockets[0].setsockopt(zmq.LINGER, 0)
            self.poller.unregister(self.sockets[0])
            self.sockets[0].close()
            self.sockets = []
            self.sockets.append(self.add_socket(zmq.REQ))
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

    s = ClientReq(host, port, contantes.MSG_CTRL_PING, 'Toi', True)
    s.start()


if __name__ == "__main__": main()