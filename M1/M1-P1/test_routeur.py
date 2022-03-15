import zmq
from time import sleep
from lib.utils import generation_nom



def svr():
    cnx = zmq.Context()
    soc = cnx.socket(zmq.ROUTER)
    soc.bind('tcp://192.168.1.9:5555')
    while True:
        result = soc.recv_multipart()
        print(result)
        env = [result[0], result[1], b"ok"]
        soc.send_multipart(env)


def clt():
    nom = generation_nom()
    cnx = zmq.Context()
    soc = cnx.socket(zmq.REQ)
    soc.setsockopt(zmq.IDENTITY, nom.encode())
    soc.connect('tcp://192.168.1.9:5555')
    print(nom)
    soc.send_string("coucou")
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