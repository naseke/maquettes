
import zmq
import sys
import threading
import time
from random import randint, random
from lib.utils import generation_nom_node, generation_code

__author__ = "Felipe Cruz <felipecruz@loogica.net>"
__license__ = "MIT/X11"

def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

class ClientTask(threading.Thread):
    """ClientTask"""
    def __init__(self):
        self.id = generation_nom_node()
        threading.Thread.__init__ (self)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        identity = f'client-{self.id}'
        socket.identity = identity.encode('ascii')
        socket.connect('tcp://localhost:5570')
        print('Client %s started' % (identity))
        poll = zmq.Poller()
        poll.register(socket, zmq.POLLIN)
        # reqs = '0'
        while True:
            #reqs = reqs + 1
            reqs = generation_code(4, 2)
            print(f'Req #{reqs} sent with {identity}')
            socket.send_string(f'request #{reqs}')
            for i in range(5):
                sockets = dict(poll.poll(1000))
                if socket in sockets:
                    msg = socket.recv()
                    tprint('Client %s received: %s' % (identity, msg))

        socket.close()
        context.term()

class ServerTask(threading.Thread):
    """ServerTask"""
    def __init__(self):
        threading.Thread.__init__ (self)

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind('tcp://*:5570')

        backend = context.socket(zmq.DEALER)
        backend.bind('inproc://backend')

        workers = []
        for i in range(5):
            worker = ServerWorker(context)
            worker.start()
            workers.append(worker)

        zmq.proxy(frontend, backend)

        frontend.close()
        backend.close()
        context.term()

class ServerWorker(threading.Thread):
    """ServerWorker"""
    def __init__(self, context):
        threading.Thread.__init__ (self)
        self.context = context

    def run(self):
        worker = self.context.socket(zmq.DEALER)
        worker.connect('inproc://backend')
        tprint('Worker started')
        while True:
            ident, msg = worker.recv_multipart()
            tprint(f'Worker received {msg} from {ident}')
            # replies = randint(0,4)
            replies = 1
            for i in range(replies):
                time.sleep(1. / (randint(1,10)))
                worker.send_multipart([ident, msg])

        worker.close()


def main():
    """main function"""
    server = ServerTask()
    server.start()
    for i in range(3):
        client = ClientTask()
        client.start()

    server.join()


if __name__ == "__main__":
    main()
