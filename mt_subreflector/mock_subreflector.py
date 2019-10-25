import socket
import pickle
import time

from mt_subreflector import subreflector_client

SUBREF_ADDR = ***REMOVED***
SUBREF_PORT = ***REMOVED***
buffer_size = ***REMOVED***



# Opens and creates mirror samples of what the subreflector sends
#TODO: Local location due to IDE bug, FIX before release
location = "/home/ivan/PycharmProjects/Effelsberg/mt_subreflector/data/" \
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

        # Sets the maximum buffersize of the socket to ***REMOVED***
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)

        # SO_REUSEADDR tells kernel to use socket even if in TIME_WAIT state
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)
        sock.listen(1)

        while True:
            server(sock)


def server(sock):
    # listen for incoming connections (server mode) with one connection a time

    print('waiting for a connection')
    connection, client_address = sock.accept()
    print("connection from", client_address)

    # receive the data in small chunks and print it
    while True:

        data = connection.recv(buffer_size)
        if data == b"\n":
            print("Initialization request received")

            while True:
                # Loop sending messages just like the real SR does
                try:
                    connection.send(second_msg)
                    time.sleep(1)
                    connection.send(first_msg)
                except ConnectionError:
                    # If broken pipe (disconected), break for next connection
                    connection.close()  # Close connection as well
                    break

        break


if __name__ == '__main__':
    main()
