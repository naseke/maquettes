import sys
import time
import random
from lib import utils
# from lib.utils import generation_nom_node
from random import randint

import zmq

class BusDonnees:

    def __init__(self, bbhost: str, bbport: str, fehost: str, feport: str, behost: str, beport: str,) -> None:
        self.busbe_host = bbhost
        self.busbe_port = bbport
        self.frontend_host = fehost
        self.frontend_port = feport
        self.backend_host = behost
        self.backend_port = beport

        self.context = zmq.Context()
        self.busbe_soc = self.context.socket(zmq.PUB)
        self.frontend_soc = self.context.socket(zmq.ROUTER)
        self.backend_soc = self.context.socket(zmq.ROUTER)
        self.__is_start = False
        self.poller = zmq.Poller()
        self.name2node = {}
        self.services2name = {}


    def start(self):
        self.__is_start = True
        self.msg_welcome()
        self.busbe_soc.bind(f'tcp://{self.busbe_host}:{self.busbe_port}')
        self.frontend_soc.bind(f'tcp://{self.frontend_host}:{self.frontend_port}')
        self.backend_soc.bind(f'tcp://{self.backend_host}:{self.backend_port}')
        self.poller = zmq.Poller()
        self.poller.register(self.busbe_soc, zmq.POLLIN)
        self.poller.register(self.frontend_soc, zmq.POLLIN)
        self.poller.register(self.backend_soc, zmq.POLLIN)
        iteration = 0
        self.startup()
        while self.is_start():
            try:
                print(f'passe n° {time.clock():.3f}')
                socks = dict(self.poller.poll(1000))

                if socks.get(self.busbe_soc) == zmq.POLLIN:
                    msg = self.busbe_soc.recv_multipart()
                    self.trt_msg_busbe(msg)
                elif socks.get(self.frontend_soc) == zmq.POLLIN:
                    msg = self.frontend_soc.recv_multipart()
                    self.trt_msg_frontend(msg)
                elif socks.get(self.backend_soc) == zmq.POLLIN:
                    msg = self.backend_soc.recv_multipart()
                    self.trt_msg_backend(msg)

                else:
                    self.trt()
                iteration += 1
            except KeyboardInterrupt:
                self.stop()

        # nettoyage
        self.busbe_soc.close()
        self.frontend_soc.close()
        self.backend_soc.close()
        self.context.term()

    def stop(self) -> None:
        self.__is_start = False

    def is_start(self) -> bool:
        return self.__is_start

    def msg_welcome(self) -> None:
        print("Bus prêt")

    def trt(self) -> None:
        self.busbe_soc.send_multipart([b'bus', b'', b'sys_services', b'', utils.bytes_dict(self.services2name)])

    def trt_msg_busbe(self, tabl: dict) -> None:
        dest, vide, cmd, vide, data = tabl

        if dest == 'bus':
            if cmd == 'sys_services':
                print(data)


    def trt_msg_frontend(self, tabl: dict) -> None:
        dest, vide, cmd, vide, data = tabl
        if cmd == 'get_services':
            pass
    def trt_msg_backend(self, tabl: dict) -> None:
        pass




    def startup(self):
        pass

    def ajout_service(self, nom: str, service: str, hote: str, port: str) -> None:
        pass
