"""
M1 All Servers
"""

# Copyright (C) Nicolas SALLARES
# Distributed under the terms of the AGPL License.


import zmq
from lib.utils import generation_nom, bytes_list
from lib import couleurs, contantes
from time import sleep

class ServerBase:
    """
    I6 : init
    I8 : init msg
    """

    def __init__(self, host: str, port: str , debug: bool = False):
        self.cnx = zmq.Context()
        self.sockets = []
        self.client = None
        self.poller = zmq.Poller()
        self.poller.poll(500)
        self._debug = debug
        self.boucle = 0
        self.host = host
        self.port = port
        self.__is_start = False
        self.name = generation_nom()



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
        self.poller.register(tmp, zmq.POLLIN)
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Ajout du port {model}")
        return tmp

    def suppr_socket(self, soc: zmq.Context.socket):
        self.poller.unregister(soc)
        #soc.close()

class M1P1(ServerBase):

    def __init__(self, host, port, debug=False):
        super().__init__(host, port, debug)
        self.lst_nodes = []

    def start(self):
        super().start()
        self.sockets.append(self.add_socket(zmq.ROUTER))
        while self.is_start():
            try:
                socks = dict(self.poller.poll(1000))

                if self.sockets[0] in socks:
                    message = self.sockets[0].recv_multipart() # I8
                    if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Message reçu : {message}")

                    env = [message[0], message[1], contantes.MSG_CTRL_OK.encode()]
                    self.sockets[0].send_multipart(env)
                    if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Envoie de la confirmation  : {contantes.MSG_CTRL_OK}")
            except KeyboardInterrupt:
                self.stop()


    def stop(self):
        super().stop()
        couleurs.AffichageColor().msg_WARNING("Arrêt du serveur")




def main():
    host = '192.168.1.9'
    port = '5555'

    t = M1P1(host, port, debug=True)
    t.start()

if __name__ == "__main__": main()
