import socket
import struct
import pickle
import time

SUBREF_ADDR = ***REMOVED***
SUBREF_PORT = ***REMOVED***
buffer_size = ***REMOVED***



# Opens and creates mirror samples of what the subreflector sends
#TODO: Local location due to IDE bug, FIX before release
location = "/home/ivan/PycharmProjects/Effelsberg/MT_Subreflector/Data/" \
           "Pickled_Subreflector_Output.p"
with open(location, "rb") as pickle_instance:
    unpickled_obj = pickle.load(pickle_instance)
    first_msg = unpickled_obj[:***REMOVED***]
    second_msg = unpickled_obj[***REMOVED***:]


def main():
    # create TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        server_address = (SUBREF_ADDR, SUBREF_PORT)
        print('starting up on %s port %s' % server_address)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
        sock.bind(server_address)
        sock.listen(1)
        server(sock)


def server(sock):
    # listen for incoming connections (server mode) with one connection a time

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

                data = connection.recv(buffer_size)
                if data == b"\n":
                    print("Initialization request received")

                    while True:
                        connection.send(second_msg)
                        time.sleep(1)
                        connection.send(first_msg)
                        
                else:
                    # print(msg)
                    # no more data -- quit the loop
                    print("Not correct initiation message")

        finally:
            # Clean up the connection
            connection.close()

if __name__ == '__main__':
    main()
