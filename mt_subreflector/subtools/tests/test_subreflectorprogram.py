import threading
import logging
import pytest
import socket
import ctypes
import time

from subtools import mock_subreflector, process_message, config
from subtools import initialize_threaded_udp_server


@pytest.fixture(scope="module")
def mock_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(4)
    destination_address = ('', config.UDP_CLIENT_PORT)

    mock_sr = mock_subreflector.Receiver()
    mock_sr.create_socket()

    udp_client = initialize_threaded_udp_server(None)
    yield (sock, mock_sr, destination_address)

    print("\n")
    udp_client.shutdown()
    print('killed udp_client')

    mock_sr.shutdown()
    print('killed mock_sr')



@pytest.mark.usefixtures("mock_connection")
class TestUserMessagesReceivedCorrectly():

    def test_valid_elevation_commands(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            mock_sr.get_message()

            value = float(data.rsplit(' ')[1])  # makes float of the str number

            # Assertions we care about
            assert isinstance(mock_sr.interlock_elevation, float)
            assert msgs[0] == f"Interlock elevation set to {value} deg"
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

    def test_other_interlock_commands(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        def helper(data, answer):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            mock_sr.get_message()
            assert msgs[0] == answer

        answer = "Interlock activated"
        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:ACTIVATE', answer)

        answer = "Interlock deactivated"
        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:DEACTIVATE', answer)

    def test_interlock_input_is_questionmark(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        interlock_msg = 'Usable types for interlock are: "ACTIVATE", ' \
                        '"DEACTIVATE", "SET", "GET".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == interlock_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:?')

    def test_interlock_no_command_or_wrong_input(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        interlock_msg = 'Message type not recognized. Correct types for ' \
                        'interlock are: "ACTIVATE", "DEACTIVATE", "SET", "GET".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == interlock_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:')
        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK:wronginput')

    def test_invalid_elevation_commands_raise_value_err(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
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

    # # # # # # # # # # # #  Hexapod  tests # # # # # # # # # # # #


    # TODO: Test hexapod SETABS/SETREL (Need to finalize them first)
    
    def test_other_hexapod_commands(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        def helper(data, answer):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            mock_sr.get_message()
            assert msgs[0] == answer

        answer = "Hexapod activated"
        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:ACTIVATE', answer)

        answer = "Hexapod deactivated"
        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:DEACTIVATE', answer)

        answer = "Hexapod stopped"
        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:STOP', answer)

        answer = "Hexapod interlock"
        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:INTERLOCK', answer)

        answer = "Hexapod error acknowledged"
        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:ERROR', answer)


    def test_hexapod_input_is_questionmark(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        interlock_msg = 'Usable types for hexapod are: "GETABS", "SETABSLIN", '\
                        '"SETABSREL", "SETRELLIN", "SETRELROT", "ACTIVATE", ' \
                        '"DEACTIVATE", "STOP", "INTERLOCK", "ERROR".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == interlock_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:?')

    def test_hexapod_no_command_or_wrong_input(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        interlock_msg = 'Message type not recognized. Correct types for ' \
                        'hexapod are: "GETABS", "SETABSLIN", "SETABSREL", ' \
                        '"SETRELLIN", "SETRELROT", "ACTIVATE", "DEACTIVATE", ' \
                        '"STOP", "INTERLOCK", "ERROR".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == interlock_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:BADINPUT')
        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:activate')
        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:error')
        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD:stop')

    # # # # # # # # # # # #  Polar tests # # # # # # # # # # # #

    # TODO: Test polar SETABS/SETREL (Need to finalize them first)

    def test_other_polar_commands(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        def helper(data, answer):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            mock_sr.get_message()
            assert msgs[0] == answer

        answer = "Polar activate command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:ACTIVATE', answer)

        answer = "Polar deactivate command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:DEACTIVATE', answer)

        answer = "Polar stop command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:STOP', answer)

        answer = "Polar ignore command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:IGNORE', answer)

        answer = "Polar acknowledge error command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:ERROR', answer)

    def test_polar_input_is_questionmark(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        interlock_msg = 'Usable types for polar are: ' \
                        '"GETABS", "SETABS", "SETREL", "IGNORE", ' \
                        '"ACTIVATE", "DEACTIVATE", "STOP", "ERROR".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == interlock_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:?')

    def test_polar_no_command_or_wrong_input(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        interlock_msg = 'Message type not recognized. Correct types for polar' \
                        ' are: "GETABS", "SETABS", "SETREL", "IGNORE", ' \
                        '"ACTIVATE", "DEACTIVATE", "STOP", "ERROR".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == interlock_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:BADINPUT')
        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:activate')
        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:error')
        helper('EFFELSBERG:MTSUBREFLECTOR:POLAR:stop')

    # # # # # # # # # # # #  ASF tests # # # # # # # # # # # #

    # TODO: Test ASF SETABS/SETREL (Need to finalize them first)

    def test_other_asf_commands(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        def helper(data, answer):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            mock_sr.get_message()
            assert msgs[0] == answer

        answer = "ASF rest command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:REST', answer)

        answer = "ASF preset command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:PRESET', answer)

        answer = "ASF deactivate command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:DEACTIVATE', answer)

        answer = "ASF stop command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:STOP', answer)

        answer = "ASF ignore command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:IGNORE', answer)

        answer = "ASF acknowledge error command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:ERROR', answer)

        answer = "ASF auto command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:AUTO', answer)

        answer = "ASF offset command sent successfully"
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:OFFSET', answer)

    def test_asf_input_is_questionmark(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        interlock_msg = 'Usable types for asf are: "IGNORE", "DEACTIVATE", ' \
                        '"REST", "ERROR", "STOP", "PRESET", "AUTO", "OFFSET".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == interlock_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:?')

    def test_asf_no_command_or_wrong_input(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        interlock_msg = 'Message type not recognized. Correct types for asf ' \
                        'are: "IGNORE", "DEACTIVATE", "REST", "ERROR", ' \
                        '"STOP", "PRESET", "AUTO", "OFFSET".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == interlock_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:temp')
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:HELLOWORLD')
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:EROR')
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF:stop')

    # # # # # # # # # # # # General functionality tests # # # # # # # # # # # #
    def test_invalid_prefix_given_raise_value_err(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        error1 = 'Incorrect prefix (Command should start with "EFFELSBERG")'
        error2 = 'Incorrect prefix (Second entry of command ' \
                 'should be "MTSUBREFLECTOR")'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            return msgs

        error_message = helper('badprefix:MTSUBREFLECTOR:INTERLOCK:SET 15')
        assert error_message[0] == error1

        error_message = helper(':MTSUBREFLECTOR:INTERLOCK:SET 1')
        assert error_message[0] == error1

        error_message = helper(':MTSUBREFLECTOR:')
        assert error_message[0] == error1

        error_message = helper('EFELSBERG:MTSUBREFLECTOR:')
        assert error_message[0] == error1

        error_message = helper('EFFELSBERG:SUBREFLECTOR:INTERLOCK:SET 1')
        assert error_message[0] == error2

        error_message = helper('EFFELSBERG:SUBREFLECTOR:')
        assert error_message[0] == error2

        error_message = helper('EFFELSBERG:mtsubreflector:HEXAPOD:')
        assert error_message[0] == error2

        error_message = helper('EFFELSBERG::ASF')
        assert error_message[0] == error2


    def test_no_instrument_given_raise_err(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        no_command_msg = 'Command input must be given. The valid inputs are ' \
                         '"INTERLOCK", "HEXAPOD", "ASF", "POLAR", and "OTHER".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == no_command_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:')


    def test_instrument_input_is_questionmark(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        no_command_msg = 'Usable inputs are: "ACTIVATE", ' \
                         '"DEACTIVATE", "SET", "GET".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == no_command_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:?')

    def test_value_error_from_input(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        no_command_msg = 'Structure of message should be ' \
                         '"EFFELSBERG:MTSUBREFLECTOR:[command]:[subcommand]".'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == no_command_msg

        helper('')

    def test_wrong_instrument_given_raise_err(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)

            instrument = data.split(":")[2]
            no_command_msg = f'{instrument} is not a valid input. The valid ' \
                             f'inputs are "INTERLOCK", "HEXAPOD", "ASF", ' \
                             f'"POLAR", and "OTHER".'

            assert msgs[0] == no_command_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOOOCK:')
        helper('EFFELSBERG:MTSUBREFLECTOR:NOTANINSTRUMENT:')
        helper('EFFELSBERG:MTSUBREFLECTOR:MEOW:')


    def test_instrument_given_missing_colon_raise_err(self, mock_connection):
        sock, mock_sr, destination_address = mock_connection
        no_command_msg = 'No colon given after command entry. Add colon and ' \
                         'leave subcommand empty for possible options'

        def helper(data):
            sock.sendto(str.encode(data), destination_address)
            msgs = process_message.recv_msg(sock, print_msg=False)
            assert msgs[0] == no_command_msg

        helper('EFFELSBERG:MTSUBREFLECTOR:INTERLOCK')
        helper('EFFELSBERG:MTSUBREFLECTOR:ASF')
        helper('EFFELSBERG:MTSUBREFLECTOR:HEXAPOD')


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
