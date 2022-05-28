"""
M1 All Servers
"""

import asyncio

from Server import M1P1
from lib.parametres import Params


def main():

    t = M1P1(Params().PARAMS['node_host'], Params().PARAMS['node_port2'], debug=False) #
    t.node = [Params().PARAMS['node_host'], Params().PARAMS['node_port']]
    # t = M1P1("192.168.1.9", "5555", debug=False)
    # asyncio.run(t.start())
    t.start()

def mainT():

    t = M1P1(Params().PARAMS['node_host'], Params().PARAMS['node_port2'], debug=True) #
    t.node = [Params().PARAMS['node_host'], Params().PARAMS['node_port']]
    # t = M1P1("192.168.1.9", "5555", debug=False)
    t.start()
    try :
        t.join()
    except KeyboardInterrupt:
        t.terminate()

if __name__ == "__main__": main()
