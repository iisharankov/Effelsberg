import threading
import logging
import pytest
import socket
import ctypes
import time

from . import mock_subreflector, subreflector_program, process_message, config
from . import initialize_threaded_udp_server



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

            if received != b'\nend':
                messages.append(received.decode('utf-8'))

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

    mock_sr = Receiver()
    mock_sr.create_socket()

    udp_client = initialize_threaded_udp_server(None)
    yield (sock, mock_sr, destination_address)

    print("\n")
    udp_client.shutdown()
    print('killed udp_client')

    mock_sr.shutdown()
    print('killed mock_sr')


class Receiver:

    def __init__(self):
        self.lock = threading.Lock()
        self.connection = None

    def shutdown(self):

        with self.lock:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            print("Socket shutdown")

    @staticmethod
    def unpack(ctype, buf):
        """
        Opposite of pack. Takes a bytes string and creates a ctypes structure
        instance given the appropriate structure to model from
        :param ctype:  Ctype structure class for reference
        :param buf: bytes string to unpack to class instance
        :return: instance of a ctypes structure
        """
        cstring = ctypes.create_string_buffer(buf)
        ctype_instance = ctypes.cast(ctypes.pointer(cstring),
                                     ctypes.POINTER(ctype)).contents
        return ctype_instance

    def create_socket(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (config.LOCAL_IP, config.SR_WRITE_PORT)
        self.sock.settimeout(3)


        # SO_REUSEADDR tells kernel to use socket even if in TIME_WAIT state
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, config.BUFFER_SIZE)

        self.sock.bind(server_address)
        self.sock.listen(2)


    def get_message(self):

        try:
            assert self.sock

            # Connecction is made on first test, but kept at module level
            if not self.connection:
                self.connection, self.client_address = self.sock.accept()

            data = self.connection.recv(config.BUFFER_SIZE)
            self.find_structure_type(data)


        except BlockingIOError or ConnectionError:
            pass

        except AssertionError as E:
            raise E

    def find_structure_type(self, data):
        # This method unpacks the data message with a
        # BasicStructure class that can extract the command type

        try:
            _basic_unpack = self.unpack(process_message.BasicStructure, data)
            assert _basic_unpack.command in [100, 101, 102, 106]

        except AttributeError or AssertionError as E:
            print(f"WARNING: an exception occurred while unpacking. {E}")
            raise E

        else:

            if _basic_unpack.command == 100:
                unpacked_data = self.unpack(process_message.AsfStructure, data)

                assert unpacked_data.command == 100
                self.asf_mode = unpacked_data.mode
                self.asf_offset_dr_nr = unpacked_data.offset_dr_nr
                self.asf_offset_active = unpacked_data.offset_active
                self.asf_offset_active1 = unpacked_data.offset_active1
                self.asf_offset_active2 = unpacked_data.offset_active2
                self.asf_offset_active3 = unpacked_data.offset_active3
                self.asf_offset_active4 = unpacked_data.offset_active4
                self.asf_offset_active5 = unpacked_data.offset_active5
                self.asf_offset_active6 = unpacked_data.offset_active6
                self.asf_offset_active7 = unpacked_data.offset_active7
                self.asf_offset_active8 = unpacked_data.offset_active8
                self.asf_offset_active9 = unpacked_data.offset_active9
                self.asf_offset_active10 = unpacked_data.offset_active10
                self.asf_offset_active11 = unpacked_data.offset_active11

            elif _basic_unpack.command == 101:
                unpacked_data = self.unpack(process_message.HexapodStructure, data)

                assert unpacked_data.command == 101
                self.hexapod_mode = unpacked_data.mode
                self.hexapod_mode_lin = unpacked_data.mode_lin
                self.hexapod_anzahl_lin = unpacked_data.anzahl_lin
                self.hexapod_phase_lin = unpacked_data.phase_lin
                self.hexapod_p_xlin = unpacked_data.p_xlin
                self.hexapod_p_ylin = unpacked_data.p_ylin
                self.hexapod_p_zlin = unpacked_data.p_zlin
                self.hexapod_p_zlin = unpacked_data.p_zlin
                self.hexapod_v_cmd = unpacked_data.v_cmd
                self.hexapod_mode_rot = unpacked_data.mode_rot
                self.hexapod_anzahl_rot = unpacked_data.anzahl_rot
                self.hexapod_phase_rot = unpacked_data.phase_rot
                self.hexapod_p_xrot = unpacked_data.p_xrot
                self.hexapod_p_yrot = unpacked_data.p_yrot
                self.hexapod_p_zrot = unpacked_data.p_zrot
                self.hexapod_v_rot = unpacked_data.v_rot

            elif _basic_unpack.command == 102:
                unpacked_data = self.unpack(process_message.PolarStructure, data)

                assert unpacked_data.command == 102
                self.interlock_mode = unpacked_data.mode
                self.interlock_p_soll = unpacked_data.p_soll
                self.interlock_v_cmd = unpacked_data.v_cmd

            elif _basic_unpack.command == 106:
                self.unpacked_data = self.unpack(process_message.InterlockStructure, data)

                self.interlock_elevation = self.unpacked_data.elevation
                self.interlock_reserved = self.unpacked_data.reserved
                self.interlock_mode = self.unpacked_data.mode




@pytest.mark.usefixtures("mock_connection")
class TestUserMessagesReceivedCorrectly():

    def test_valid_elevation_commands(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = recv_msg(sock)
            mock_sr.get_message()

            value = float(data.rsplit(' ')[1])  # makes float of the number

            # Assertions we care about
            assert isinstance(mock_sr.interlock_elevation, float)
            assert msgs[0] == f"Interlock elevation set to {value} degrees"
            assert mock_sr.interlock_elevation == value
            assert mock_sr.interlock_reserved == 0.0
            assert mock_sr.interlock_mode == 2000

        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 8')
        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 80')
        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 90')
        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 9.9')
        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 26.8')
        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 56')
        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 20')


    def test_unvalid_elevation_commands_raise_value_err(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = recv_msg(sock)
            return msgs

        value_error = 'The elevation given was outside the limits. Elevation ' \
                      'must be between 8 degrees and 90 degrees inclusive.'

        error_message = helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 1')
        assert error_message[0] == value_error

        error_message = helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 7')
        assert error_message[0] == value_error

        error_message = helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 90.1')
        assert error_message[0] == value_error

        error_message = helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:SET 91')
        assert error_message[0] == value_error



    def test_can_add(self):
        four = 4
        assert four == 4

    def test_can_is_one(self):
        assert 1 == 1

    def test_can_send_to_mt(self):
        data = "fail"

        assert data == 'fail'

    #
    # def test_can_reach(self, mock_connection):
    #     sock, mock_sr, destination_address = mock_connection
    #     assert mock_sr
    #     real = mock_sr.unpacked_data
    #     assert real == 61
