import socket
import time


HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((socket.gethostname(), 1243))


while True:
    # now our endpoint knows about the OTHER endpoint.
    clientsocket, address = s.recvfrom(16)
    print(f"Connection from {address} has been established.")

    msg = "Welcome to the server!"
    msg = f"{len(msg):<{HEADERSIZE}}"+msg

    clientsocket.send(bytes(msg,"utf-8"))

    while True:
        time.sleep(3)
        msg = f"The time is {time.time()}"
        msg = f"{len(msg):<{HEADERSIZE}}"+msg

        print(msg)

        clientsocket.send(bytes(msg,"utf-8"))