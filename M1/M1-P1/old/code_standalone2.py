import zmq

def main():
    """Constantes"""
    host = "192.168.1.9"
    port = "5555"
    port2 = "5556"
    MSG_CTRL_PING = "\002"
    MSG_CTRL_PONG = "\003"

    cnx = zmq.Context()
    pol = zmq.Poller()
    soc = cnx.socket(zmq.ROUTER)
    soc.bind(f"tcp://{host}:{port}")
    pol.register(soc, zmq.POLLOUT)
    print("demarrage du server...")
    while True:

        """Listen"""

        print("écoute...")
        socks = dict(pol.poll(1000))  # Tick

        if soc in socks:
            message = soc.recv_multipart() # I8
            print(message)
            env = [message[0], message[1], MSG_CTRL_PONG.encode()]
            soc.send_multipart(env)


        """Send PING"""

        print("Ping !")
        pol2 = zmq.Poller()
        soc2 = cnx.socket(zmq.REQ)
        soc2.connect(f"tcp://{host}:{port2}")
        pol2.register(soc, zmq.POLLIN)

        soc2.send(MSG_CTRL_PING.encode())

        socks = dict(pol2.poll(1000))  # Tick
        if soc2 in socks:
            message2 = soc2.recv_multipart()
            print(message2)






if __name__ == "__main__": main()
