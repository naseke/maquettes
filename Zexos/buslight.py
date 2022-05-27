from lib import utils
from random import randint
import zmq
import multiprocessing


def worker(debug: bool = False):
    context = zmq.Context()
    services = []
    vocabulaire = {'set_services': [f'{services}'], 'get_services': [f'{services}'], 'get_vocabulary': [], 'stop': [], 'print': ['data']}
    name = utils.generation_nom_node()
    soc = context.socket(zmq.REQ)
    soc.identity = name.encode()
    _debug = debug

    soc.connect('ipc://internalbe.ipc')
    soc.send(b'ready')
    if _debug: print('demarrage')
    while True:
        try:
            request = soc.recv_multipart()
            if _debug: print(f"{request} : {len(request)}")
            req = request[2].decode('utf8')
            if _debug: print(f"{len(eval(req)) >= 3} : {eval(req)[1] == ''} : {eval(req)[0] in vocabulaire.keys()}")
            if len(eval(req)) >= 3 and eval(req)[1] == '' and eval(req)[0] in vocabulaire.keys():
                cmd, vide, data = eval(req)
                if _debug: print(f'trt_autres_cmd')
                if cmd == "print":
                    print(data)
                else:
                    print(f"{soc.identity.decode()} : {eval(req)}")
                soc.send_multipart([request[0],b'', b"OK"])
            else:
                print('erreur')
        except KeyboardInterrupt:
            print("bye!")
            break


def client(debug: bool = False):
    # phrases venant du site http://romainvaleri.online.fr/ générateur de phrase

    phrases = [
        "Les sénégalais aux pupilles dilatées s'inscrivaient.",
        "Une française allait réfléchir.",
        "Des justicières cryptent-elles le scaphandre ?",
        "Le marchand de sable se gavera de mes superbes péchés.",
        "Tu branches cette apparition en croquant la connerie.",
        "Pierre Bellemare s'entraine à s'attaquer à une pomme.",
        "Des amiraux rendaient ces frocs.",
        "Le pentagone ne s'inspire guère de seize cyclomotoristes.",
        "La chômeuse fait main basse sur une allégorie.",
        "La partenaire rapait tes genoux avec des choristes."
    ]
    soc = zmq.Context().socket(zmq.REQ)
    name = utils.generation_nom_node()
    soc.identity = name.encode()
    soc.connect('ipc://frontend.ipc')
    _debug = debug
    # soc.send(b"go")

    delais = randint(1, 10)
    phrase = phrases[randint(0, 9)]
    # time.sleep(delais)
    soc.send(f'["print","","{phrase}"]'.encode('utf8'))
    if _debug: print("send...")
    msg = soc.recv()
    print(f'recu : {msg.decode()}')


def fin(pool, pool2, internalbe, frontend, context):
    pool.close()
    pool2.close()
    internalbe.close()
    frontend.close()
    pool.join()
    pool2.join()
    context.term()
    exit()

def fin2(internalbe, frontend, context):
    internalbe.close()
    frontend.close()
    context.term()
    exit()


def start_proc(task, *args):
    proc = multiprocessing.Process(target=task, args=args)
    proc.daemon = True
    proc.start()


def main(debug: bool = False):

    # init
    context = zmq.Context()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("ipc://frontend.ipc")
    internalbe = context.socket(zmq.ROUTER)
    internalbe.bind('ipc://internalbe.ipc')
    pool = multiprocessing.Pool(5, utils.init_worker)
    pool2 = multiprocessing.Pool(10, utils.init_worker)
    _debug = debug
    poller = zmq.Poller()
    local_wrk = []
    backend_ready = False

   # demarrage
    poller.register(internalbe, zmq.POLLIN)
    for _ in range(10):
        # pool.apply_async(worker, [_debug])
        # pool.apply_async(worker, [True])
        pass

    for _ in range(10000):
        pool2.apply_async(client, [_debug])
        # pool2.apply_async(client, [True])
        pass

    for _ in range(10):
        start_proc(worker, _debug)

    # for _ in range(10000):
    #    start_proc(client, _debug)

    while True:
        try:
            events = dict(poller.poll(1000 if local_wrk else None))
        except zmq.ZMQError:
            break  # interrupted
        except KeyboardInterrupt:
            fin(pool, pool2, internalbe, frontend, context)
            # fin2(internalbe, frontend, context)

        # ### Partie workers internes ###
        if internalbe in events:
            msg = internalbe.recv_multipart()
            if msg[2] == b"ready":
                local_wrk.append(msg[0])
            else:
                local_wrk.append(msg[0])
                if _debug: print(msg)
                frontend.send_multipart([msg[2], b'', msg[4]])
            if local_wrk and not backend_ready:
                poller.register(frontend, zmq.POLLIN)
                backend_ready = True

        # ### Partie Clients ###
        elif frontend in events:
            msg = frontend.recv_multipart()
            if len(msg) == 3:
                wrk = local_wrk.pop(0)
                internalbe.send_multipart([wrk, b'', msg[0], b'', msg[2]])
            if not local_wrk:
                poller.unregister(frontend)
                backend_ready = False
        if _debug: print(local_wrk)


if __name__ == "__main__": main()