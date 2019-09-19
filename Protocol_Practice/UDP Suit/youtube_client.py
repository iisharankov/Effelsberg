import socket

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((socket.gethostname(), 1243))

while True:
    full_msg = ''
    new_msg = True
    while True:
        msg = s.recv(16)
        if new_msg:
            msglen = int(msg[:HEADERSIZE])
            new_msg = False
            print(f"full message length: {msglen}")

        full_msg += msg.decode("utf-8")

        if len(full_msg)-HEADERSIZE == msglen:
            print(f"all {(len(full_msg[HEADERSIZE:]))}  bytes recvd, printing message")
            print(full_msg[HEADERSIZE:])
            new_msg = True
            full_msg = ""