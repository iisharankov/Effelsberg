import threading
import logging
import socket

from subtools import mock_subreflector, subreflector_program

SUBREF_ADDR = "***REMOVED***"
SUBREF_READ_PORT = ***REMOVED***
SUBREF_WRITE_PORT = ***REMOVED***
buffer_size = ***REMOVED***

# myPath = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, myPath + '/../')




class StartupMockSubreflector:
    """
    Simple class that correctly starts up the mock_subreflector.py script
    in a thread be tested
    """

    def __init__(self):
        self.thread = None

        self.receiver = mock_subreflector.Receiver()

    def start_sr_client(self):
        """
        This method sets up a non-daemon thread to initiate the
        subreflector_client.py in the background. It calls the next method which
        is what actually instantiates SubreflectorClient
        """

        try:
            logging.debug(f"Creating Thread")
            self.thread = threading.Thread(
                target=self.run_mock_sr, args=(), name='moch_sr_module')

            self.thread.daemon = True  # Demonize thread
            logging.debug(f"Threading set to {self.thread.daemon}.")
            self.thread.start()
            logging.debug(f"Thread started successfully with "
                          f"thread ID: {self.thread.ident}")
            # self.close_sr_client()
        except Exception as Er:
            print(Er)
            logging.exception("Exception starting StartupMockSubreflector")

    def run_mock_sr(self):
        """
        creates instance of SubreflectorClient which starts listening to the
        subreflector.
        """
        self.receiver.create_socket()

class StartupReflectorProgram:
    """
    Simple class that correctly starts up the mock_subreflector.py script
    in a thread be tested
    """

    def __init__(self):
        self.thread = None

    def start_program(self):
        """
        This method sets up a non-daemon thread to initiate the
        subreflector_client.py in the background. It calls the next method which
        is what actually instantiates SubreflectorClient
        """

        try:
            logging.debug(f"Creating Thread")
            self.thread = threading.Thread(
                target=self.run_sr_program, args=(), name='moch_sr_module')

            self.thread.daemon = True  # Demonize thread
            logging.debug(f"Threading set to {self.thread.daemon}.")
            self.thread.start()
            logging.debug(f"Thread started successfully with "
                          f"thread ID: {self.thread.ident}")
            # self.close_sr_client()
        except Exception as Er:
            print(Er)
            logging.exception("Exception starting StartupMockSubreflector")

    def run_sr_program(self):
        """
        creates instance of SubreflectorClient which starts listening to the
        subreflector.
        """
        subreflector_program.start_connections(True)



sr_inst = StartupReflectorProgram()
sr_inst.start_program()

mock_sr = StartupMockSubreflector()
mock_sr.start_sr_client()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)
destination_address = ('', ***REMOVED***)

class TestCanTest():

    def test_can_add(self):
        four = 4
        assert four == 4

    def test_can_is_one(self):
        assert 1 == 1

    def test_can_send_to_mt(self):
        data = "fail"

        assert data == 'fail'


    def test_can_reach(self):
        assert mock_sr
        real = mock_sr.receiver.unpacked_data
        assert real == 5

