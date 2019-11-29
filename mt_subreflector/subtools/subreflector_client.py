#!/usr/bin/env python

import time
import json
import queue
import socket
import struct
import logging
import threading

from . import process_message, config
from .config import SR_IP, SR_READ_PORT, LOCAL_IP


MULTICAST = ('***REMOVED***', ***REMOVED***)

class SubreflectorClient:

    def __init__(self):
        self.sock = None
        self.lock = threading.Lock()
        self.chosen_server = self.get_server_adderss(config.USE_TEST_SERVER)
        self.connection_flag = False
        self.starttime = time.time()
        self.mcast_queue = queue.LifoQueue(maxsize=10)
        self.do_run = True

    def shutdown(self):
        print('SubreflectorClient shutdown')
        templock = threading.Lock()

        with templock:
            self.do_run = False

    def main(self):
        self.activate_multicasting()
        self.make_connection()

    def get_server_adderss(self, test_server):
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
            return LOCAL_IP, SR_READ_PORT

        else:
            msg = f"Connecting to mt_subreflector. IP: {SR_IP} - " \
                  f"Port: {SR_READ_PORT}"
            print(msg)
            logging.debug(msg)
            return SR_IP, SR_READ_PORT

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

    def activate_multicasting(self):
        # Sets up multicast socket for later use
        self.multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                            socket.IPPROTO_UDP)
        self.multicast_sock.setsockopt(socket.IPPROTO_IP,
                                       socket.IP_MULTICAST_TTL, 32 ) #1)

        logging.debug("Starting Multicast queue reader in thread")
        t = threading.Thread(target=self.send_mcast, args=(), name="Queue_Mcast")
        t.deamon = True
        t.start()

    def send_mcast(self):
        templock = threading.Lock()

        while True:
            with templock:
                status_message = self.mcast_queue.get()
                self.multicast_sock.sendto(status_message, MULTICAST)

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
        sock.send(b"\n")  # Initial message is needed to start stream
        data, count = b'', 0
        while self.do_run:
            # time.sleep(0.5)
            try:

                # Due to the nature of TCP/IP connections, and the properties
                # of the subreflector, it is safer to receive two messages and
                # find a full one inside between the flags. Explained in docs
                packet = sock.recv((1760*2))
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
                data = data[startindex:]

                # Finds the first end flag afterwards and does the same
                endindex = (data.find(b"\xd1\xcf\xfc\xa1"))
                full_msg = data[:endindex + 4]  # +4 as endindex is start string
                # logging.debug(f"full_length msg is length {len(full_msg)}")

                data = b''
                count += 1

                if len(full_msg) > 1760:
                    msg = "The message didn't register the correct length, " \
                          "data may have been added/lost, changing the length."
                    logging.exception(msg)
                    raise ValueError(msg)

                # Expected length of the message
                # Only manipulated data and sends to multicast every 10 mesages
                elif len(full_msg) == 1760 and count%10 == 0:

                    # Optional pickling of the message for storage
                    # pickle.dump(full_msg, open("Subreflector_Output.p", 'ab'))


                    print(f"\rmessage sent x{count/10}", end='')

                    processed_msg = process_message.package_msg(full_msg)

                    # this block is precautionary to avoid loops in queue
                    try:
                        assert not self.mcast_queue.full()

                        if self.mcast_queue.qsize() > 7:
                            # In case queue starts to reach max size, clear
                            # it and then add the queue object
                            self.mcast_queue.queue.clear()

                        self.mcast_queue.put(processed_msg)

                    except AssertionError:
                        logging.exception("Queue filled up!")

            finally:
                with self.lock:
                     if self.connection_flag:
                        self.connection_flag = False  # resets the flag
                        logging.debug("Socket closed")
                        break

    def end_connection(self):
        with self.lock:
            self.connection_flag = True

        logging.debug("flag to close socket triggered")



if __name__ == '__main__':
    logging.basicConfig(
        filename='/home/ivan/PycharmProjects/Effelsberg/mt_subreflector/debug/subreflector_client_debug.log', filemode='w',
        level=logging.DEBUG, format='%(asctime)s - %(levelname)s- %(message)s',
        datefmt='%d-%b-%y %H:%M:%S')

    SubreflectorClient().main()
