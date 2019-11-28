import threading
import logging
import pytest
import socket
import ctypes
import time

from subtools import mock_subreflector, subreflector_program, process_message
from subtools import start_mock_server, Receiver as MockReceiver, start_server

SUBREF_ADDR = ***REMOVED***
SUBREF_READ_PORT = ***REMOVED***
SUBREF_WRITE_PORT = ***REMOVED***
buffer_size = ***REMOVED***

# myPath = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, myPath + '/../')


def recv_msg(sock):
    # Receive data from the server
    try:
        # received = sock.recv(***REMOVED***)
        # print("Received: {}".format(received.decode('utf-8')))
        messages = []
        while True:
            received = sock.recv(***REMOVED***)
            time.sleep(0.1)
            if received != b'\nend':
                messages.append(received.decode('utf-8'))
                print(f"Received: {received.decode('utf-8')}")
            else:
                break

    except socket.timeout:
        print("Socket timed out, Try again")

    else:
        return messages


@pytest.fixture(scope="module")
def mock_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(4)
    destination_address = ('', ***REMOVED***)
    sock.sendto(str.encode("\n"), destination_address)

    sr_client, udp_client = start_server(True)

    mock_sr = MockReceiver()
    thread_mock = start_mock_server(mock_sr)

    yield (sock, mock_sr, destination_address)
    print("Finished the server")
    # udp_client.shutdown()
    print('killed udp_client')
    # mock_sr.shutdown()
    print('killed mock_sr')
    # sr_client.shutdown()
    #
    # print('killed sr_client')

@pytest.mark.usefixtures("mock_connection")
class TestCanTest():
    #
    # def setup(self):
    #
    #
    #
    # def teardown(self):
    #     self.sock.close()


    def test_can_send_elevation(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        assert mock_sr.elevation == None
        assert mock_sr.unpacked_data == 61
        data = 'EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 10'
        sock.sendto(str.encode(data), destination_address)

        # assert mock_sr.unpacked_data == 50
        assert mock_sr.elevation == 10

    def test_can_add(self):
        four = 4
        assert four == 4

    def test_can_is_one(self):
        assert 1 == 1

    def test_can_send_to_mt(self):
        data = "fail"

        assert data == 'fail'


    def test_can_reach(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        assert mock_sr
        real = mock_sr.unpacked_data
        assert real == 61

