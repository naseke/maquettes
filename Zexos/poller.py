import zmq


def main():

    ctx = zmq.Context()

    poll = zmq.Poller

    soc = ctx.socket(zmq.REQ)
    soc2 = ctx.socket(zmq.REP)

    soc2.bind("ipc://backend.ipc")
    soc.connect("ipc://backend.ipc")

    poll.register(soc2, zmq.POLLOUT)

    soc.send(b'ping')
    events=dict(poll.poll(1000))

    if soc2 in events:
        msg = soc2.recv()
        print(msg)


if __name__ == "__main__": main()