from lib import utils
# from classroot import CltBusWrkRoot
import zmq
import multiprocessing


class Worker:
    """
    Class générique permettant de décrire le comportement générique de tout les workers
    """

    def __init__(self, url: str = '', debug: bool = False) -> None:
        """
        Constructeur de Worker
        :param url: url permettant de se connecter en ipc ou en tcp
        :param debug: permet d'afficher des informations supplémentaires pour du débogage
        """
        self.context = zmq.Context()
        self.url = url
        self.services = []
        self.vocabulaire = {'set_services': [f'{self.services}'], 'get_services': [f'{self.services}'], 'get_vocabulary': [], 'stop': [], }
        self.name = utils.generation_nom_node()
        self.soc = self.context.socket(zmq.REQ)
        self.soc.identity = self.name.encode()
        self.last_send = None
        self._debug = debug
        self.__is_start = False

    def is_start(self) -> bool:
        return self.__is_start

    def get_vocabulaire(self) -> dict:
        return self.vocabulaire

    def start(self) -> None:
        self.__is_start = True
        self.soc.connect(self.url)
        self.__demarrage()
        while self.is_start():
            try:
                """
                    format de message recv d'un worker :
                    @clt, '', service | commande, '', <données>
                    Dans un premier temps 1 service = 1 commande 
                """
                request = self.soc.recv_multipart()
                if self._debug: print(f"{request} : {len(request)}")
                cmd = request[2].decode('utf8')
                if self._debug: print(f"{len(cmd) >= 3} : {request[3] == b''} : {cmd in self.vocabulaire.keys()}")
                if cmd in self.vocabulaire.keys() and len(cmd) == 3:
                    if cmd == "stop":
                        self._req_stop()
                    elif cmd == "get_vocabulary":
                        self.soc.send_multipart([b'get_vocabulary', b'', utils.bytes_dict(self.vocabulaire)])
                    else:
                        if self._debug: print("pass")
                        pass
                elif len(cmd) > 3 and request[3] == b'' and cmd in self.vocabulaire.keys():
                    self.trt_autres_cmd(request[0].decode(), [cmd, '', request[4].decode()])
                else:
                    print('erreur')
            except KeyboardInterrupt:
                self._req_stop()

    def _req_stop(self) -> None:
        self.__is_start = False
        print("bye!")

    def _req_get_vocabulary(self) -> None:
        self.soc.send_multipart([b'get_vocabulary', b'', utils.bytes_dict(self.vocabulaire)])

    def _req_ok(self, clt: str) -> None:
        try:
            self.soc.send_multipart([utils.list2bytes(self.services), b'', clt.encode(), b'', b"OK"])
        except zmq.ZMQError:
            print("erreur ok")

    def _req_set_service(self):
        self.soc.send_multipart([b'set_services', b'', utils.list2bytes(self.services)])


    def __demarrage_old(self) -> None:
        """
            fonction contenant les premières actions à faire avant de se mettre en écoute
        """
        self.soc.send(b'set_services')
        if self._debug: print('demarrage')
        self.demarrage_autres_actions()

    def __demarrage(self) -> None:
        """
            fonction contenant les premières actions à faire avant de se mettre en écoute
        """
        self._req_set_service()
        if self._debug: print('demarrage')
        self.demarrage_autres_actions()

    def trt_autres_cmd(self,clt: str, msg: list) -> None: ...
    def demarrage_autres_actions(self) -> None: ...



class WorkerPrint(Worker):
    """
        Class de worker permettant d'afficher un texte
    """

    def __init__(self, url: str = '', debug: bool = False) -> None:
        """
        Constructeur de Worker
        :param url: url permettant de se connecter en ipc ou en tcp
        :param debug: permet d'afficher des informations supplémentaires pour du débogage
        """
        super().__init__(url, debug)
        self.services = ['print']
        self.vocabulaire['print'] = ['data']

    def trt_autres_cmd(self, clt: str, msg: list) -> None:
        cmd, vide, data = msg
        if self._debug: print(f'trt_autres_cmd')
        if cmd == "print":
            print(f"{cmd} : {data}")
        else:
            print(f"{self.soc.identity.decode()} : {msg}")
        self._req_ok(clt)


def workerPrint_use(url: str = '', debug: bool = False) -> None:
    ow = WorkerPrint(url, debug)
    ow.start()


class WorkerAfficher(Worker):
    """
        Class de worker permettant d'afficher un texte
    """

    def __init__(self, url: str = '', debug: bool = False) -> None:
        """
        Constructeur de Worker
        :param url: url permettant de se connecter en ipc ou en tcp
        :param debug: permet d'afficher des informations supplémentaires pour du débogage
        """
        super().__init__(url, debug)
        self.services = ['Afficher']
        self.vocabulaire['Afficher'] = ['data']

    def trt_autres_cmd(self, clt: str, msg: list) -> None:
        cmd, vide, data = msg
        if self._debug: print(f'trt_autres_cmd')
        if cmd == "Afficher":
            print(f"{cmd} : {data}")
        else:
            print(f"{self.soc.identity.decode()} : {msg}")
        self._req_ok(clt)


def workerAfficher_use(url: str = '', debug: bool = False) -> None:
    ow = WorkerAfficher(url, debug)
    ow.start()


def main():

    phase = {'1': 'get_vocabulary', '2': '["print", "", "tata"]', '3': 'stop'}
    debug = False
    # debug = True



    soc = zmq.Context().socket(zmq.ROUTER)
    soc.bind('ipc://wrksys.ipc')
    # w = Worker('ipc://wrksys.ipc')

    def start(task: any, *args: any) -> multiprocessing.Process:
        proc = multiprocessing.Process(target=task, args=args)
        proc.daemon = True
        proc.start()
        return proc

    p = multiprocessing.Pool(5, utils.init_worker)

    for _ in range(1000):
        p.apply_async(workerPrint_use, ['ipc://wrksys.ipc', debug])

    poller = zmq.Poller()
    poller.register(soc, zmq.POLLIN)

    # for i in range(len(phase)):
    while True:
        try:
            if debug: print('ecoute')
            sockets = dict(poller.poll(1000))
            if soc in sockets:
                msg = soc.recv_multipart()
                print(f'{msg[0].decode()} : {" : ".join([s.decode() for s in msg[2:] if s != b""])}')
                if msg[2].decode() == "ready":
                    soc.send_multipart([msg[0], b'', phase['1'].encode()])
                if msg[2].decode().find(phase['1']) >= 0:
                    soc.send_multipart([msg[0], b'', phase['2'].encode()])
                if msg[2].decode() == "OK":
                    soc.send_multipart([msg[0], b'', phase['3'].encode()])
                #soc.send_multipart([msg[0], b'', phase[str(i + 1)].encode()])
        except KeyboardInterrupt:
            print("Caught KeyboardInterrupt, terminating workers")
            p.terminate()
            p.join()
            print("c'est fini !")
            exit()


if __name__ == "__main__": main()