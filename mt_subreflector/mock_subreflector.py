import time
import ctypes
import socket
import pickle
import logging
import datetime
import threading

from mt_subreflector import subreflector_client
import mtcommand

SUBREF_ADDR = ***REMOVED***
SUBREF_READ_PORT = ***REMOVED***
SUBREF_WRITE_PORT = ***REMOVED***
buffer_size = ***REMOVED***

# TODO: ADD port ***REMOVED*** to receive commands, copy client.py methods to decode

# Opens and creates mirror samples of what the subreflector sends
#TODO: Local location, FIX before release
location = "/home/ivan/PycharmProjects/Effelsberg/mt_subreflector/data/" \
           "Pickled_Subreflector_Output.p"
with open(location, "rb") as pickle_instance:
    unpickled_obj = pickle.load(pickle_instance)
    first_msg = unpickled_obj[:***REMOVED***]
    second_msg = unpickled_obj[***REMOVED***:]


def main():
    T = threading.Thread(target=sender, args=(), name="***REMOVED*** Port")
    T.daemon = False
    T.start()

    T2 = threading.Thread(target=receiver, args=(), name="***REMOVED*** Port")
    T2.daemon = False
    T2.start()


def receiver():
    # create TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        server_address = (SUBREF_ADDR, SUBREF_WRITE_PORT)
        print('starting up on %s port %s' % server_address)

        # Sets the maximum buffersize of the socket to ***REMOVED***
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)

        # SO_REUSEADDR tells kernel to use socket even if in TIME_WAIT state
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)
        sock.listen(2)

        while True:
            time.sleep(1)
            # listen for incoming connections (server mode)
            # with one connection a time
            connection, client_address = sock.accept()

            # receive the data in small chunks and print it
            while True:
                time.sleep(1)

                pass
                # data = connection.recv(buffer_size)
                # mt = mtcommand.MTCommand(True)
                #
                # unpacked_data = mt.unpack(mt.interlock_command_to_struct(), data)
                #
                # print(unpacked_data)



def sender():
    # create TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        server_address = (SUBREF_ADDR, SUBREF_READ_PORT)
        print('starting up on %s port %s' % server_address)

        # Sets the maximum buffersize of the socket to ***REMOVED***
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)

        # SO_REUSEADDR tells kernel to use socket even if in TIME_WAIT state
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)
        sock.listen(2)

        while True:
            # listen for incoming connections (server mode)
            # with one connection a time
            print('waiting for a connection')
            connection, client_address = sock.accept()
            print("connection from", client_address)

            # receive the data in small chunks and print it
            while True:

                data = connection.recv(buffer_size)
                if data == b"\n":
                    print("Initialization request received")

                    while True:
                        time.sleep(0.001)
                        # Loop sending messages just like the real SR does
                        try:
                            connection.send(second_msg)
                            connection.send(first_msg)
                        except ConnectionError:
                            # If broken pipe, break for next connection
                            connection.close()  # Close connection as well
                            print("Connection broken, awaiting new connection")
                            break

                break


if __name__ == '__main__':
    main()
