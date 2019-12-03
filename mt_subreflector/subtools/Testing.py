# import json
# import ast
#
# with open('getter_data.txt', 'r') as file:
#     for line in file:
#         name = line[:15].replace(' ', '')
#         data = line[43:-2]
#
#         data_as_dict = ast.literal_eval(data)
#         # print(data_as_dict)
#         print("\n \n" + f"# # # # # # # {name.upper()}" * 5)
#         for a, b in data_as_dict.items():
#             # Does not print lines where all values are exactly the same
#             if sum(b)/len(b) != b[0]: # and sum(b) != 0:  # For just 0 excluded, uncomment this
#                 print(a.ljust(50), [round(ba, 10) for ba in b])


#!/usr/bin/env python

import time
import json
import queue
import socket
import struct
import logging
import threading
from astropy.time import Time

SR_ADDR = "***REMOVED***"
LOCAL_ADDR = '***REMOVED***'
SR_PORT = ***REMOVED***
MULTICAST = ('***REMOVED***', ***REMOVED***)

class SubreflectorClient:

    def __init__(self, use_test_server=False):
        self.sock = None
        self.lock = threading.Lock()
        self.chosen_server = self.use_test_server(use_test_server)
        self.connection_flag = False
        self.starttime = time.time()

    def main(self):
        self.make_connection()

    def use_test_server(self, test_server):
        """
        Swaps real SR address for local if instance of class is needed for tests
        :param flag: bool
            if flag set to true, the address for the test server is used instead
        :return: IP address and port for the respective subreflector
        """

        if test_server:
            msg = "Connecting to local subreflector in MockSubreflector.py"
            print(msg)
            logging.debug(msg)
            return LOCAL_ADDR, SR_PORT

        else:
            msg = f"Connecting to mt_subreflector. IP: {SR_ADDR} - " \
                  f"Port: {SR_PORT}"
            print(msg)
            logging.debug(msg)
            return SR_ADDR, SR_PORT

    def make_connection(self):
        """
        Creates a TCP socket connection with the given server. This is done in
        a context manager to further guarantee no leakage of resources. Due
        to the nature of the context manager, the receive_data method is run
        in a while loop in this method, otherwise the socket instance variable
        in not accessible in other methods

        :return: N/A
        """
        # receive

        # Creates socket that receives from subreflector
        logging.debug("Creating TCP socket")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            logging.debug("TCP socket created. Connecting to specified address")

            try:
                # Change to local to use the MockSubreflector for testing
                self.sock.connect(self.chosen_server)
                logging.debug(f"TCP Socket connected at IP "
                              f"Address {self.sock.getsockname()[0]} and "
                              f"port {self.sock.getsockname()[1]}")
                self.sock.settimeout(8)
                logging.debug(f"socket timeout set to {self.sock.gettimeout()}")
                self.receive_data(self.sock)
            except ConnectionError as E:
                logging.exception("Error connecting to server. May not be found")
                print(f"Could not connect to the Subreflector: {E}")

    def receive_data(self, sock):
        """
        Method that runs indefinitly checking for data from the given server.
        It then finds a full message inside the data stream, and passes that
        along to other methods to correctly analyze the data. This date is
        then broadcasted to a multicast server at the end of this method.


        :param sock: self.sock from the make_connection method. Passed
        into here as it cannot be accessed as an instance variable if
        it's within a context manager.
        :return:
        """

        starttime = time.time()
        logging.debug("sending empty message to start")
        sock.send(b"\n")  # Initial message is needed to start stream
        count = 0
        data = b''
        while 1:
            # logging.debug("sleeping 0.5 seconds")
            # time.sleep(0.5)
            try:

                # Due to the nature of TCP/IP connections, and the properties
                # of the subreflector, it is safer to receive two messages and
                # find a full one inside between the flags. Explained in docs
                logging.debug("Trying to recieve data")
                packet = sock.recv((1760*2))
                logging.debug("Got data, adding to to master data")
                logging.debug(f"data was {len(packet)},  and data was {packet[20:-20]}")
                data += packet

                # packets come in size 736 or ***REMOVED***. Add packets until length is
                # twice the size of the message to ensure full message inside
                assert len(data) >= 1760 * 2

                # if not len(data) == (1760*2):
                #     logging.warning(f"{len(data)}Data was weird: {data}")

                if data == b'':
                    logging.warning(
                        f"data was empty bytes string. Counter at: {count}. "
                        f"It took {time.time()-self.starttime} seconds for "
                        f"an empty string to show")

            except socket.timeout:
                msg = f"Socket timed out after {sock.gettimeout()} seconds"
                logging.debug(msg)
                print(msg, " Trying again.")

            except AssertionError:
                pass

            else:
                # Finds a start flag and cuts everything before it
                startindex = (data.find(b"\x1a\xcf\xfc\x1d"))
                logging.debug("found start flag in data")
                data = data[startindex:]
                logging.debug("removed things before start flag from data")

                # Finds the first end flag afterwards and does the same
                endindex = (data.find(b"\xd1\xcf\xfc\xa1"))
                logging.debug("found end flag in data")
                full_msg = data[:endindex + 4]  # +4 as endindex is start string
                logging.debug("removed everything after end flag")
                # logging.debug(f"full_length msg is length {len(full_msg)}")
                if len(full_msg) > 1760:
                    msg = "The message didn't register the correct length, " \
                          "data may have been added/lost, changing the length."
                    logging.exception(msg)
                    logging.exception(f"Length is now {len(full_msg)}")
                    raise ValueError(msg)

                # Expected length of the message

                elif len(full_msg) == 1760:
                    data = b''

                    # Optional pickling of the message for storage
                    # pickle.dump(full_msg, open("Subreflector_Output_Nov-4.p", 'ab'))

                    count += 1
                    print(f"\rmessage sent x{count} at {time.time()-starttime}", end='')
                    # if count == 109:
                    #     print(time.time() -self.starttime)

                    # this block is just precautionary to avoid loops in queue

if __name__ == '__main__':
    logging.basicConfig(
        filename='debug/subreflector_client_debug.log', filemode='w',
        level=logging.DEBUG, format='%(asctime)s - %(levelname)s- %(message)s',
        datefmt='%d-%b-%y %H:%M:%S')

    SubreflectorClient(use_test_server=False).main()

