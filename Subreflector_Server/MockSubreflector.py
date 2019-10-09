import socket
import struct


SUBREF_ADDR = "***REMOVED***"
SUBREF_PORT = 10_000
buffer_size = ***REMOVED***

# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (SUBREF_ADDR, SUBREF_PORT)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

# listen for incoming connections (server mode) with one connection at a time
sock.listen(1)
while True:
    # wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()

    try:
        # show who connected to us
        print("connection from", client_address)
        msg = ""
        # receive the data in small chunks and print it
        while True:
            # TODO: USE PICKLE save.p
            with open('bytes.txt') as filename:
                msg = filename
                print(filename)
                print(type(filename))
            data = connection.recv(buffer_size)
            if data == b"\n":
                print("Initialization request received")

                print("sending message")
                sock.send(msg)
                print("Message sent")
            else:
                # print(msg)
                # no more data -- quit the loop
                print("no more data.")
                break
    finally:
        # Clean up the connection
        connection.close()