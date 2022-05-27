# encoding: utf-8
#
#   Custom routing Router to Mama (ROUTER to REQ)
#
#   Author: Jeremy Avnet (brainsik) <spork(dash)zmq(at)theory(dot)org>
#

import time
import random
from threading import Thread
from lib.utils import tprint, generation_nom_node

import zmq


NBR_WORKERS = 10


def worker_thread(context=None):
    context = context or zmq.Context.instance()
    worker = context.socket(zmq.DEALER)

    # We use a string identity for ease here
    nom = generation_nom_node()
    worker.setsockopt_string(zmq.IDENTITY, nom)
    worker.connect("tcp://localhost:5671")

    total = 0
    while True:
        # Tell the router we're ready for work
        worker.send_multipart([
            b'',
            b"ready"])

        # Get workload from router, until finished
        vide, workload = worker.recv_multipart()
        finished = workload == b"END"
        if finished:
            tprint("Processed: %d tasks" % total)
            break
        total += 1

        # Do some random work
        time.sleep(0.1 * random.random())


context = zmq.Context.instance()
client = context.socket(zmq.ROUTER)
client.bind("tcp://*:5671")

for _ in range(NBR_WORKERS):
    Thread(target=worker_thread).start()

for _ in range(NBR_WORKERS * 10):
    # LRU worker is next waiting in the queue
    address, empty, ready = client.recv_multipart()

    client.send_multipart([
        address,
        b'',
        b'This is the workload',
    ])

# Now ask mama to shut down and report their results
for _ in range(NBR_WORKERS):
    address, empty, ready = client.recv_multipart()
    client.send_multipart([
        address,
        b'',
        b'END',
    ])