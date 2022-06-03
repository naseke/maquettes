import zmq


class CltBusWrkRoot:

    def __init__(self, debug: bool = False):
        self.context = zmq.Context()
        self._debug = debug
        self.__is_start = False

    def is_start(self) -> bool:
        return self.__is_start

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def __demarrage(self) -> None: ...