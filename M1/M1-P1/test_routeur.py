import zmq
from time import sleep
from lib.utils import generation_nom



def svr():
    cnx = zmq.Context()
    pol = zmq.Poller()
    soc = cnx.socket(zmq.ROUTER)
    soc.bind('tcp://192.168.1.9:5555')
    pol.register(soc, zmq.POLLOUT)
    while True:
        result = soc.recv_multipart()
        print(result)
        socks = dict(pol.poll(500))
        if soc in socks:
            env = [result[0], b"ok"]
            #sleep(1)
            soc.send_multipart(env)


def clt():
    nom = generation_nom()
    cnx = zmq.Context()
    pol = zmq.Poller()
    soc = cnx.socket(zmq.DEALER)
    soc.setsockopt(zmq.ROUTING_ID, nom.encode())
    soc.connect('tcp://192.168.1.9:5555')
    pol.register(soc, zmq.POLLIN)
    print(nom)

    for i in range(10):
        soc.send_string("coucou")
        socks = dict(pol.poll(10000))
        print(f"apres le poll {i}")
        if soc in socks:
            rep = soc.recv()
            print(rep)


def main():

    genre = 'clt'
    #genre = 'svr'

    if genre =='svr':
        svr()
    else:
        clt()


if __name__ == "__main__": main()