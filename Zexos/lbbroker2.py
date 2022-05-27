from __future__ import print_function

import time
import random

# from threading import Thread
import multiprocessing
from lib.utils import tprint, generation_nom_node

import zmq


NBR_CLIENTS = 100
NBR_WORKERS = 3


def client_task(ident):
    client = zmq.Context().socket(zmq.REQ)

    # We use a string identity for ease here
    nom = generation_nom_node()
    client.identity = f"clt-{ident}".encode()
    client.connect("ipc://frontend.ipc")

    # Tell the router we're ready for work
    # client.send(b"ping")
    client.send(b"get_services")
    rep = client.recv()
    print(f"{client.identity.decode()} : {rep.decode()}")

def worker_task(ident):
    worker = zmq.Context().socket(zmq.REQ)

    # We use a string identity for ease here
    nom = generation_nom_node()
    worker.identity = f"wrk-{ident}".encode()
    worker.connect("ipc://backend.ipc")

    worker.send(b"set_service")

    while True:
        addr, vide, request = worker.recv_multipart()
        if request.decode() == "service":
            print(f"{worker.identity.decode()} : service !")
        print(f"{worker.identity.decode()} : {request.decode()}")
        worker.send_multipart([addr, b"", b"OK"])



def broker():
    context = zmq.Context.instance()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("ipc://frontend.ipc")
    backend = context.socket(zmq.ROUTER)
    backend.bind("ipc://backend.ipc")

    def start(task, *args):
        proc = multiprocessing.Process(target=task, args=args)
        proc.daemon = True
        proc.start()

    for i in range(NBR_WORKERS):
        start(worker_task, i)
    for i in range(NBR_CLIENTS):
        start(client_task, i)

    count = NBR_CLIENTS
    backend_ready = False
    workers = []
    poller = zmq.Poller()

    poller.register(backend, zmq.POLLIN)

    while True:
        sockets = dict(poller.poll())

        if backend in sockets:
            request = backend.recv_multipart()
            print(request)
            worker, empty, client = request[:3]
            workers.append(worker)
            if workers and not backend_ready:
                poller.register(frontend, zmq.POLLIN)
                backend_ready = True
            if client == b"set_service":
                backend.send_multipart([worker,b'', b'service', b'', b'service'])
            else:
                empty, reply = request[3:]
                count -=1
                if not count:
                    break
        if frontend in sockets:
            client, empty, request = frontend.recv_multipart()
            # print(request)
            if request.decode() == 'get_services':
                frontend.send_multipart([client, b"", b"services"])
            else:
                worker = workers.pop(0)
                backend.send_multipart([worker, b'', client, b'', request])
                if not workers:
                    poller.unregister(frontend)
                    backend_ready = False

    backend.close()
    frontend.close()
    context.term()


if __name__ == "__main__": broker()
