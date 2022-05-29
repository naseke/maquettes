import signal
import time

from lib import utils
import zmq
import multiprocessing
import workers

class BusDonnees:

    def __init__(self, debug: bool = False):
        self.context = zmq.Context()
        self.frontend = self.context.socket(zmq.ROUTER)
        self.frontend.bind("ipc://frontend.ipc")
        self.internalbe = self.context.socket(zmq.ROUTER)
        self.internalbe_url = 'ipc://internalbe.ipc'
        self.internalbe.bind(self.internalbe_url)
        self.pool = multiprocessing.Pool(5, utils.init_worker) # pool des worker ?
        self._debug = debug
        self.__is_start = False
        self.poller = zmq.Poller()
        self.local_wrk = []
        self.backend_ready = False
        self.local_services = {}
        # self.proxy = zmq.proxy(self.frontend, self.internalbe)

    def is_start(self) -> bool:
        return self.__is_start

    def start_wrk(self, task: any, *args: any) -> multiprocessing.Process:
        proc = multiprocessing.Process(target=task, args=args)
        proc.daemon = True
        proc.start()
        return proc

    def start(self):
        self.__is_start = True
        self.poller.register(self.internalbe, zmq.POLLIN)
        #self.poller.register(self.frontend, zmq.POLLIN)
        self.demarrage()

        while self.is_start():
            try:
                events = dict(self.poller.poll(1000 if self.local_wrk else None))
            except zmq.ZMQError:
                break  # interrupted
            except KeyboardInterrupt:
                exit()

            ### Partie workers internes ###
            if self.internalbe in events:
                msg = self.internalbe.recv_multipart()
                if msg[2] == b"set_services":
                    """
                        format de message init worker :
                        @wrk, '', set_services, '', [services]
                    """
                    if self._debug: print(msg)
                    # self.local_wrk.append(msg[0])
                    self._alim_local_services(utils.bytes2list(msg[4]), msg[0].decode())
                else:
                    """
                        format de message retour d'un worker :
                        @wrk, '', [services], '', @clt, '', <réponse>
                    """
                    self._alim_local_services(utils.bytes2list(msg[2]), msg[0].decode())
                    # self.local_wrk.append(msg[0])
                    if self._debug: print(msg)
                    if self._debug: print(self.local_services)
                    self.frontend.send_multipart([msg[4], b'', msg[6]])

                if self.local_services and not self.backend_ready:
                    self._debug: print("go!")
                    self.poller.register(self.frontend, zmq.POLLIN)
                    self.backend_ready = True

            ### Partie Clients ###
            elif self.frontend in events:
                """
                    format de message retour d'un worker :
                    @clt, '', service | commande, '', <données>
                    Dans un premier temps 1 service = 1 commande 
                """
                msg = self.frontend.recv_multipart()
                if self._debug: print(msg)
                if self._debug: print(self.local_services)

                if not self.local_services:
                    self.poller.unregister(self.frontend)
                    self.backend_ready = False

                if len(msg) >= 3:
                    if msg[2].decode() in self.local_services.keys():
                        if self._debug: print(f"pop : {self.local_services[msg[2].decode()]}")
                        if self.local_services[msg[2].decode()]:
                            wrk = self.local_services[msg[2].decode()].pop(0)
                            self.internalbe.send_multipart([wrk.encode(), b'', msg[0], b'', msg[2], b'', msg[4]])
                        else:
                            self.msg_pas_service(msg[0])
                    else:
                        print("pas de service")

    def _alim_local_services(self, svc_list: list, wrk: str) -> None:
        for svc in svc_list:
            if svc in self.local_services.keys():
                self.local_services[svc].append(wrk)
            else:
                self.local_services[svc] = [wrk]
        if self._debug: print(self.local_services)

    def demarrage(self) -> None:
        for _ in range(5):
            # self.pool.apply_async(workers.workerPrint_use, [self.internalbe_url, self._debug])
            # self.pool.apply_async(workers.workerPrint_use, [self.internalbe_url, True])
            self.start_wrk(workers.workerPrint_use, self.internalbe_url, self._debug)
            self.start_wrk(workers.workerAfficher_use, self.internalbe_url, self._debug)
        time.sleep(5)

    def msg_pas_service(self, clt: bytes) -> None:
        self.frontend.send_multipart([clt, b'', b"No_service"])


def bus_multi():
    b = BusDonnees()
    b.start()


def main():
    import clients

    def dem_print():
        for _ in range(10):
            proc = multiprocessing.Process(target=clients.clientTestPrint_use, args=["ipc://frontend.ipc", False])
            proc.daemon = True
            proc.start()

    def dem_afficher():
        for _ in range(10 ):
            proc = multiprocessing.Process(target=clients.clientTestAfficher_use, args=["ipc://frontend.ipc", False])
            proc.daemon = True
            proc.start()

    dem_afficher()
    dem_print()

    b = BusDonnees(False)
    b.start()


if __name__ == "__main__": main()
