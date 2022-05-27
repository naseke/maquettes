#
#   Broker peering simulation (part 1) in Python
#   Prototypes the state flow
#
#   Author : Piero Cornice
#   Contact: root(at)pieroland(dot)net
#
import sys
import time
import random
# from lib.utils import generation_nom_node
from random import randint

import zmq

def generation_nom_node() -> str:
    """
    Créer le nom du node de cette manière 3EDE-A79A-744D-DDED

    :return: le nom du node
    """
    return "%04X-%04X-%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000), randint(0, 0x10000), randint(0, 0x10000))


def main(myself, others):
    print("Hello, I am %s" % myself)

    context = zmq.Context()

    # State Back-End
    statebe = context.socket(zmq.PUB)

    # State Front-End
    statefe = context.socket(zmq.SUB)
    statefe.setsockopt(zmq.SUBSCRIBE, b'')
    # statefe.setsockopt(zmq.SUBSCRIBE, f'{myself}'.encode())
    # statefe.setsockopt(zmq.SUBSCRIBE, b'ALL')

    bind_address = f"ipc://{myself}-state.ipc"
    statebe.bind(bind_address)

    for other in others:
        statefe.connect(f"ipc://{other}-state.ipc")
        time.sleep(1.0)

    # others.append('ALL')
    poller = zmq.Poller()
    poller.register(statefe, zmq.POLLIN)

    while True:

########## Solution with poll() ##########
        socks = dict(poller.poll(1000))

        # Handle incoming status message
        if socks.get(statefe) == zmq.POLLIN:
            msg = statefe.recv_multipart()
            print(f'{myself} Received: {msg}')

        else:
            # Send our address and a random value
            # for worker availability
            msg = [bind_address, (u'%i' % random.randrange(1, 10))]
            # msg = [others[random.randint(0, len(others) - 1)], generation_nom_node(), (u'%i' % random.randrange(1, 10))]
            # print(msg)
            msg = [m.encode('ascii') for m in msg]
            statebe.send_multipart(msg)
##################################

######### Solution with select() #########
#        pollin, pollout, pollerr = zmq.select([statefe], [], [], 1)
#
#        if pollin and pollin[0] == statefe:
#            # Handle incoming status message
#            msg = statefe.recv_multipart()
#            print 'Received:', msg
#
#        else:
#            # Send our address and a random value
#            # for worker availability
#            msg = [bind_address, str(random.randrange(1, 10))]
#            statebe.send_multipart(msg)
##################################


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        main(myself=sys.argv[1], others=sys.argv[2:])
    else:
        print("Usage: peering1.py <myself> <peer_1> ... <peer_N>")
        sys.exit(1)
