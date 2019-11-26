import time
import json
import copy
import socket
import struct
import logging
import threading
import socketserver

from . import mtcommand, subreflector_client

# Constants
UDPTELNET_PORT = ***REMOVED***
SDH_PORT = 1602  # Port where sdh output can be reached
SR_MULTI = ***REMOVED***  # Port where subreflector_client.py outputs JSON
LOCAL_ADDRESS = ''  # local IP

MULTICAST = ('***REMOVED***', ***REMOVED***)


__all__ = ['start_server']

class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    """
          Simple class that starts listening to the udp-telnet server for
          any incoming messages. These messages are then accessed and received
          by MYUDPHandler which calls the necessarily class to parse the user
          input. This is set up as a non-daemon thread to work in the
          background, and to hang until closed manually.
          """

    def __init__(self, sr_client, is_test_server, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sr_client = sr_client
        self.udp_parser_client = UDPCommandParser(self.sr_client,
                                                  is_test_server)
        logging.debug("Initialized ThreadingUDPServer")
        self.helll = "hello"
        # self.start_sr_client()


def start_udp_server(sr_client, is_test_server):
    """
    This function sets up a non-daemon thread to initiate the
    ThreadingUDPserver in the background. This is the code
    that connects to the server to read the input data and parse it
    :return:
    """
    dest_address = (LOCAL_ADDRESS, UDPTELNET_PORT)
    logging.debug(f"ThreadingUDPServer accessing address:"
                  f" {dest_address[0]}, port: {dest_address[1]}")
    server = ThreadingUDPServer(sr_client, is_test_server,
                                dest_address, MyUDPHandler, )

    logging.debug(f"Setting server to run forever")
    t = threading.Thread(target=server.serve_forever, name='UDPSERVER')
    t.daemon = False  # Do not demonize thread
    logging.debug(f"ThreadingUDPServer now running in a non-daemon "
                  f"thread ({threading.current_thread}) in background")
    t.start()


def start_connections(is_test_server):
    """
    Start connections does just that, it connects to two servers. One is in
    subreflector_client.py which directly connects to the output of the
    subreflector, which listens for the status message which gets multicast by
    that module. The second is start_udp_server, which starts a server listening
    to any input commands on the computer address and on PORT ***REMOVED***. Any input
    is passed through the handle method in the MyUDPHandler class, which deals
    with the command it was given via a parse class. start_udp_server is given
    the instance of the sr_client to be able to control/reset the connection.
    :return: N/a
    """
    try:

        # makes sure parameter is bool or int (bool is subclass of int)
        assert isinstance(is_test_server, int)
        # def start_sr_client(self):
        logging.debug("Start Startup_Subreflector_Client instance")
        sr_client = StartupSubreflectorClient(is_test_server)
        sr_client.start_sr_client()

        # sr_client = subreflector_client.SubreflectorClient(is_test_server)
        # sr_client.main()EFFELSBERG:MTSUBREFLECTOR:OTHER:RESETCONNECTION

        logging.debug("Start UDP server instance")
        start_udp_server(sr_client, is_test_server)

    except AssertionError:
        logging.debug("Start connections parameter must be bool, was other")

    except Exception as E:
        logging.exception("An exception occurred starting the threaded classes")
        raise E


# def close_sr_client(sr_client):
#     logging.debug("User initiated Subreflector connection reset")
#     logging.debug(f"{threading.enumerate()}")
#
#     endsocketthread = threading.Thread(target=sr_client.end_connection)
#     endsocketthread.start()
#     endsocketthread.join()
#
#     logging.debug(f"{threading.enumerate()}")
#
#     #
#     time.sleep(2)
#     logging.debug("Starting connection again")
#     sr_client.make_connection()


class StartupSubreflectorClient:
    """
    Simple class that correctly starts up the subreflectorclient.py script
    in a thread so it can process data from the MT Subreflector in real time.
    This is set up as a non-daemon thread to work in the background, and to hang
    until closed manually.
    """

    def __init__(self, is_test_server):
        self.thread = None
        self.stop_threads = False
        self.srclient = subreflector_client.SubreflectorClient(is_test_server)

    def start_sr_client(self):
        """
        This method sets up a non-daemon thread to initiate the
        subreflector_client.py in the background. It calls the next method which
        is what actually instantiates SubreflectorClient
        """

        try:
            logging.debug(f"Creating Thread")
            self.thread = threading.Thread(
                target=self.run_sr_client, args=(), name='sr_client_module')

            self.thread.daemon = False  # Demonize thread
            logging.debug(f"Threading set to {self.thread.daemon}.")
            time.sleep(0.5)
            self.thread.start()
            logging.debug(f"Thread started successfully with "
                          f"thread ID: {self.thread.ident}")
            # self.close_sr_client()
        except Exception as Er:
            print(Er)
            logging.exception("Exception starting Startup_Subreflector_Client")

    def run_sr_client(self):
        """
        creates instance of SubreflectorClient which starts listening to the
        subreflector.
        """
        self.srclient.main()

    def close_sr_client(self):
        logging.debug("User initiated Subreflector connection reset")
        logging.debug(f"{threading.enumerate()}")
        self.thread.join()
        # endsocketthread = threading.Thread(target=)
        # endsocketthread.start()
        # endsocketthread.join()
        self.srclient.end_connection()
        logging.debug(f"{threading.enumerate()}")

        #
        # time.sleep(2)
        logging.debug("Starting connection again")
        self.srclient.make_connection()


# Communication class
class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This is the class that is instantiated in UDPServer as a thread.
    This works on the functionality of socketserver, and the handle
    method listens to any incoming message on the IP/Port combo and passes it
    through to a different class which is responsible for parsing the message
    and forwarding it to mtcommand.py, which directly communicates to the
    subreflector
    """

    def setup(self):
        self.msg = []

    def handle(self):
        logging.debug("#" * 50)
        logging.debug("Telnet: Message received from udp-telnet")
        # takes message, decodes to string and - all whitespace (by rejoining)
        telnet_msg = self.request[0].decode('utf-8')
        # print(telnet_msg)
        # telnet_msg = ''.join(self.request[0].decode('utf-8').split())

        self.server.udp_parser_client.probe_command(telnet_msg)
        self.msg = self.server.udp_parser_client.return_message()
        self.msg.append('\nend')
        ###############################
        # print(self.server.helll)

        logging.debug("Telnet: Setting up returnsocket")
        returnsocket = self.request[1]
        logging.debug(f"All messages are: {self.msg}")

        for each_msg in self.msg:
            returnsocket.sendto(each_msg.encode(), self.client_address)

        logging.debug("#" * 50)


class UDPCommandParser:
    """
    Instantiating this class takes a string and parses it to return the correct
    response to the user
    TODO: Complete doc string
    """

    def __init__(self, sr_client, is_test_server):
        """
        :param sr_client: object
            instance of the StartupSubreflectorClient class
        """
        # Proper PEP-8 form has these defined here
        self.msg = []  # Message given back to user
        self.obsprefix = None  # prefix found while parsing user command
        self.commandprefix = None  # prefix found while parsing user command

        # These are instances that are used within methods
        self.mcast_receiver = MulticastReceiver()  # For recieving data from SR
        # self.mcast_receiver = threading.Thread(
        #     target=MulticastReceiver, args=(), name="Mcast Receiver")
        # self.mcast_receiver.daemon = False
        # self.mcast_receiver.start()
        # self.mcast_receiver.join()

        # Sending commands to SR
        self.mtcommand_client = mtcommand.MTCommand(is_test_server)
        self.mtcommand_client.setup_connection()
        self.sr_client = sr_client

    # # # # # General parsing section # # # # #
    def probe_command(self, usr_input):
        self.msg = []
        self.obsprefix = None
        self.commandprefix = None
        logging.debug("Parser values reset")

        try:

            telescope, subref, command, \
                *subcommand = usr_input.strip().split(":")

            logging.debug(f"User gave values {telescope}:{subref}:"
                          f"{command}:{subcommand}")

            # Replace is done here individually instead of above as sometimes
            # subcommand will have numbers separated by spaces from user
            telescope = telescope.replace(" ", '')
            subref = subref.replace(" ", '')
            command = command.replace(" ", '')

        except ValueError:
            msg = 'Structure of message should be ' \
                  '"EFFELSBERG:MTSUBREFLECTOR:[command]:[subcommand]".'

            self.msg.append(msg)
        else:

            if telescope != "EFFELSBERG":
                logging.info('Input did not start with "EFFELSBERG"')
                self.msg.append(
                    'Incorrect prefix (Command should start with "EFFELSBERG")')

            elif subref != "MTSUBREFLECTOR":
                logging.info('Subreference was not "MTSUBREFLECTOR"')
                self.msg.append(
                    'Incorrect prefix (Second entry of command should be '
                    '"MTSUBREFLECTOR")')

            elif not command:
                logging.debug("User gave no command var input")
                string = f'Command input must be given. The valid inputs are ' \
                         f'"INTERLOCK", "HEXAPOD", "ASF", "POLAR", and ' \
                         f'"OTHER".'
                self.msg.append(string)

            elif not subcommand:
                msg = "No colon given after command entry. Add colon and " \
                      "leave subcommand empty for possible options"
                self.msg.append(msg)
                logging.debug(msg)

            # Calls respective method for the given command var
            elif command == 'INTERLOCK':
                self.interlock_control(subcommand[0])
            elif command == 'HEXAPOD':
                self.hexapod_control(subcommand[0])
            elif command == 'ASF':
                self.asf_control(subcommand[0])
            elif command == 'POLAR':
                self.polar_control(subcommand[0])
            elif command == "OTHER":
                self.other_controls(subcommand[0])
            elif command == "?":
                self.msg.append('Usable types for interlock are: "ACTIVATE", '
                                '"DEACTIVATE", "SET", "GET".')
            else:
                logging.debug("User gave unrecognized command input")
                string = f'{command} is not a valid input. The valid inputs' \
                         f' are "INTERLOCK", "HEXAPOD", "ASF", "POLAR", and ' \
                         f'"OTHER".'
                self.msg.append(string)

    # # # # # Interlock parsing section # # # # #
    def interlock_control(self, subcommand):

        if "DEACTIVATE" in subcommand:
            logging.debug("interlock deactivate command given")
            self.mtcommand_client.deactivate_mt()
            self.msg.append("Interlock deactivated")

        elif "ACTIVATE" in subcommand:
            logging.debug("interlock activate command given")
            self.mtcommand_client.activate_mt()
            self.msg.append("Interlock activated")

        elif "SET" in subcommand:

            try:
                just_command, str_value = subcommand.strip().split(" ", 1)
                logging.debug(
                    f"Command given: {just_command}. Value given: {str_value}")
                value = int(str_value)
                assert 8 <= value <= 90

            except AssertionError:
                logging.exception("User gave elevation outside of range")
                self.msg.append(
                    "The elevation given was outside the limits. Elevation "
                    "must be between 8 degrees and 90 degrees inclusive.")

            except ValueError:
                logging.exception("Number given couldn't be converted to float")
                self.msg.append("Number given after 'SET' couldn't be "
                                "converted to a float or none provided")

            else:
                logging.debug("interlock set elevation command given")
                self.mtcommand_client.set_mt_elevation(float(value))
                self.msg.append(f"Interlock elevation set to {value} degrees")

        elif "GET" in subcommand:
            logging.debug("Interlock get elevation command given")
            elevation = self.mcast_receiver.get_elevation()

            msg = f"\n Interlock elevation: {elevation}"
            self.msg.append(msg)

        elif "?" in subcommand:
            self.msg.append('Usable types for interlock are: "ACTIVATE", '
                            '"DEACTIVATE", "SET", "GET".')

        else:
            logging.debug("User command fit no interlock option")
            self.msg.append('message type not recognized. Correct types for '
                            'interlock are: "ACTIVATE", "DEACTIVATE", '
                            '"SET", "GET".')

    # # # # # Hexapod parsing section # # # # #
    def hexapod_control(self, subcommand):

        # Long message that is near identical except variation of type
        def helper_msg(commandtype):
            """
            :param commandtype: str
                val: 'absolute' or 'relative
            :return: str
            """
            assert commandtype == 'absolute' or commandtype == 'relative'

            return \
                f"One or more of the {commandtype} values given go over the  " \
                f"permitted limits. Please input smaller {commandtype} " \
                f"values, or use \"GETABS\" to read out current positions. " \
                f"Read Users Manual for more information. Limits are: \n" \
                " x_lin: between -225 and 225 \n" \
                " y_lin: between -175 and 175 \n" \
                " z_lin: between -195 and 45 \n" \
                " x_rot, y_rot, z_r: between -0.95 and 0.95"

        if "GETABS" in subcommand:
            logging.debug("Hexapod get absolute position command given")
            positions = self.mcast_receiver.get_hexapod_positions()
            msg = f"\n hxpd_xlin: {positions[0]}," \
                  f"\n hxpd_ylin: {positions[1]}," \
                  f"\n hxpd_zlin: {positions[2]}," \
                  f"\n hxpd_xrot: {positions[3]}," \
                  f"\n hxpd_yrot: {positions[4]}," \
                  f"\n hxpd_zrot: {positions[5]}"
            self.msg.append(msg)

        elif subcommand[:9] in ["SETABSLIN", "SETRELLIN",
                                "SETABSROT", "SETRELROT"]:
            try:
                if ',' in subcommand:
                    self.msg.append("Do not put commas between numbers")

                values = subcommand[9:].strip().replace(',', '').split(" ")
                new_val = [float(i) for i in values]  # change str to float
                logging.debug(f'new_vals are: {new_val}')

                assert len(new_val) == 4  # Make sure there's exactly 4 entries

            except AssertionError:
                msg = "Assertion error. Improper number in parameters or " \
                      "wrong type. SETABS/SETREL takes 4 entries"
                self.msg.append(msg)
                logging.exception(msg)

            except ValueError as E:
                msg = f"Error converting entries to floats. Other " \
                      f"characters may be present. Error: {E}"
                logging.exception(msg)
                self.msg.append(msg)

            else:
                if "SETABSLIN" in subcommand:
                    logging.debug("Hexapod set linear absolute command given")

                    try:
                        assert -225 <= new_val[0] <= 225
                        assert -175 <= new_val[1] <= 175
                        assert -195 <= new_val[2] <= 45
                        assert .001 <= new_val[3] <= 10

                    except AssertionError:
                        self.msg.append(helper_msg('absolute'))
                        logging.exception("Absolute inputs go over saftey "
                                          "limits set on Hexapod. Aborted")

                    else:
                        self.mtcommand_client.preset_abs_lin_hxpd(
                            new_val[0], new_val[1], new_val[2], new_val[3])
                        msg = f"Set absolute values for linear drives on " \
                              f"hexapod to \n" \
                              f" xlin: {new_val[0]}, ylin: {new_val[1]}," \
                              f" zlin: {new_val[2]}, v_lin: {new_val[3]}"
                        self.msg.append(msg)

                elif "SETABSROT" in subcommand:
                    logging.debug("Hexapod set absolute rotational"
                                  " command given")

                    try:
                        assert -0.95 <= new_val[0] <= 0.95
                        assert -0.95 <= new_val[1] <= 0.95
                        assert -0.95 <= new_val[2] <= 0.95
                        assert 0.001 <= new_val[3] <= 0.10

                    except AssertionError:
                        self.msg.append(helper_msg('absolute'))
                        logging.exception("Absolute inputs go over saftey "
                                          "limits set on Hexapod. Aborted")

                    else:
                        self.mtcommand_client.preset_abs_rot_hxpd(
                            new_val[0], new_val[1], new_val[2], new_val[3])
                        msg = f"Set absolute values for rotational drives on " \
                              f"hexapod to \n" \
                              f" xrot: {new_val[0]}, yrot: {new_val[1]}," \
                              f" zrot: {new_val[2]}, v_rot: {new_val[3]}"
                        self.msg.append(msg)
                        logging.debug("Msg appended")

                elif "SETRELLIN" in subcommand:
                    logging.debug("Hexapod set relative linear command given")
                    cur_vals = self.mcast_receiver.get_hexapod_positions()
                    new_xlin = cur_vals[0] + new_val[0]
                    new_ylin = cur_vals[1] + new_val[1]
                    new_zlin = cur_vals[2] + new_val[2]
                    velocity = new_val[3]

                    try:
                        assert -225 <= new_xlin <= 225
                        assert -175 <= new_ylin <= 175
                        assert -195 <= new_zlin <= 45
                        assert .001 <= velocity <= 10

                    except AssertionError:
                        self.msg.append(helper_msg('relative'))
                        logging.exception("Relative inputs given go over saftey"
                                          " limits set on Hexapod. Aborted")
                    else:
                        self.mtcommand_client.preset_abs_lin_hxpd(
                            new_xlin, new_ylin, new_zlin, velocity)

                        self.msg.append(
                            "added relative values for linear drives on "
                            "hexapod. Moving to values: \n"
                            f" xlin: {new_xlin}, ylin: {new_ylin},"
                            f" zlin: {new_zlin}, v_lin: {velocity}")

                elif "SETRELROT" in subcommand:
                    logging.debug("Hexapod set relative rotational "
                                  "command given")
                    positions = self.mcast_receiver.get_hexapod_positions()
                    new_xrot = positions[3] + new_val[0]
                    new_yrot = positions[4] + new_val[1]
                    new_zrot = positions[5] + new_val[2]
                    velocity = new_val[3]

                    try:
                        assert -0.95 <= new_xrot <= 0.95
                        assert -0.95 <= new_yrot <= 0.95
                        assert -0.95 <= new_zrot <= 0.95
                        assert 0.001 <= velocity <= 0.10

                    except AssertionError:
                        self.msg.append(helper_msg('relative'))
                        logging.exception("Relative inputs given go over saftey"
                                          " limits set on Hexapod. Aborted")
                    else:
                        self.mtcommand_client.preset_abs_rot_hxpd(
                            new_xrot, new_yrot, new_zrot, velocity)

                        self.msg.append(
                            "added relative values for rotational drive on "
                            "hexapod. Moving to values: \n"
                            f" xrot: {new_xrot}, yrot: {new_yrot},"
                            f" zrot: {new_zrot}, v_rot: {velocity}")
                else:
                    # Safety, but should be unreachable
                    self.msg.append(
                        'Subcommand not recognized. Possible entries are: '
                        '"SETABSLIN", "SETABSROT", "SETRELLIN", or "SETRELROT"')

        elif "DEACTIVATE" in subcommand:
            logging.debug("Hexapod deactivation command given")
            self.mtcommand_client.deactivate_hxpd()
        elif "ACTIVATE" in subcommand:
            logging.debug("Hexapod activation command given")
            self.mtcommand_client.activate_hxpd()
        elif "STOP" in subcommand:
            logging.debug("Hexapod stop command given")
            self.mtcommand_client.stop_hxpd()
        elif "INTERLOCK" in subcommand:
            logging.debug("Hexapod interlock command given")
            self.mtcommand_client.interlock_hxpd()
        elif "ERROR" in subcommand:
            logging.debug("Hexapod acknowledge error command given")
            self.mtcommand_client.acknowledge_error_on_hxpd()
        elif "?" in subcommand:
            self.msg.append(
                'Usable types for hexapod are: '
                '"GETABS", "SETABSLIN", "SETABSREL", "SETRELLIN", "SETRELROT",'
                '"ACTIVATE", "DEACTIVATE", "STOP", "INTERLOCK", "ERROR".')

        else:
            logging.debug("User command fit no hexapod option")
            self.msg.append(
                'message type not recognized. Correct types for hexapod are: '
                '"GETABS", "SETABSLIN", "SETABSREL", "SETRELLIN", "SETRELROT",'
                '"ACTIVATE", "DEACTIVATE", "STOP", "INTERLOCK", "ERROR".')

    # # # # # Polar parsing section # # # # #

    def asf_control(self, subcommand):

        if "IGNORE" in subcommand:
            logging.debug("ASF ignore command given")
            self.mtcommand_client.ignore_asf()
        elif "DEACTIVATE" in subcommand:
            logging.debug("ASF deactivate command given")
            self.mtcommand_client.deactivate_asf()
        elif "REST" in subcommand:
            logging.debug("ASF reset command given")
            self.mtcommand_client.rest_pos_asf()
        elif "ERROR" in subcommand:
            logging.debug("ASF acknowledge error command given")
            self.mtcommand_client.acknowledge_error_on_asf()
        elif "STOP" in subcommand:
            logging.debug("ASF stop command given")
            self.mtcommand_client.stop_asf()
        elif "PRESET" in subcommand:
            logging.debug("ASF preset position command given")
            self.mtcommand_client.preset_pos_asf()
        elif "AUTO" in subcommand:
            logging.debug("ASF set automatic mode command given")
            self.mtcommand_client.set_automatic_asf()
        elif "OFFSET" in subcommand:
            logging.debug("ASF set offset command given")
            self.mtcommand_client.set_offset_asf()
        elif "?" in subcommand:
            self.msg.append(
                'Usable types for asf are: "IGNORE", "DEACTIVATE", '
                '"REST", "ERROR", "STOP", "PRESET", "AUTO", "OFFSET".')
        else:
            logging.debug("User command fit no ASF option")
            self.msg.append(
                'message type not recognized. Correct types for asf'
                'are: "IGNORE", "DEACTIVATE", "REST", "ERROR", "STOP",'
                '"PRESET", "AUTO", "OFFSET".')

    # # # # # Polar parsing section # # # # #
    def polar_control(self, subcommand):

        if "GETABS" in subcommand:
            logging.debug("Polar get absolute positions command given")
            positions = self.mcast_receiver.get_polar_position()
            msg = f"\n P_soll[deg]: {positions[0]},"
            self.msg.append(msg)

        elif "IGNORE" in subcommand:
            logging.debug("Polar ignore command given")
            self.mtcommand_client.ignore_polar()

        elif "DEACTIVATE" in subcommand:
            logging.debug("Polar deactivate command given")
            self.mtcommand_client.deactivate_polar()

        elif "ACTIVATE" in subcommand:
            logging.debug("Polar activate command given")
            self.mtcommand_client.activate_polar()

        elif "STOP" in subcommand:
            logging.debug("Polar stop command given")
            self.mtcommand_client.stop_polar()

        elif "ERROR" in subcommand:
            logging.debug("Polar acknowledge error command given")
            self.mtcommand_client.acknowledge_error_on_polar()

        elif "SETABS" in subcommand:  # TODO add logging here
            # TODO: Add test for right format from user on numbers.
            #   Very hacky currently
            p_soll, v_cmd = subcommand[10:].strip().split(" ", 1)
            logging.debug(p_soll)
            logging.debug(v_cmd)
            self.mtcommand_client.preset_abs_polar(p_soll, v_cmd)

        elif "SETREL" in subcommand:  # TODO add logging here
            p_soll, v_cmd = subcommand[10:].strip().split(" ", 1)
            logging.debug(p_soll)
            logging.debug(v_cmd)
            self.mtcommand_client.preset_rel_polar(p_soll, v_cmd)

        elif "?" in subcommand:
            self.msg.append(
                'Usable types for polar are: "GETABS", "SETABS", "SETREL", '
                '"IGNORE", "ACTIVATE", "DEACTIVATE", "STOP", "ERROR".')

        else:
            logging.debug("User command fit no polar option")
            self.msg.append(
                'message type not recognized. Correct types for polar are: '
                '"GETABS", "SETABS", "SETREL", "IGNORE", "ACTIVATE", '
                '"DEACTIVATE", "STOP", "ERROR".')

    # # # # # Other Controls # # # # #
    def other_controls(self, subcommand):

        if "RESETCONNECTION" in subcommand:
            logging.debug("Other command given to reset connection to server")
            self.reset_connections()  # TODO Fix this threading nuance

        elif "?" in subcommand:
            self.msg.append('Usable types for other are: "RESETCONNECTION".')

        else:
            logging.debug("User command fit no other option")
            self.msg.append(
                'message type not recognized. Correct types for other'
                'are: "RESETCONNECTION".')

    # # # # # Reset Connections # # # # #
    def reset_connections(self):
        logging.debug("User initiated connection reset to server")
        self.sr_client.close_sr_client()
        # close_sr_client(self.sr_client)
        self.msg.append("Connection reset successfully")

        #
        # if srclient.srclient.sock.fileno() == -1:
        #     logging.debug("Connection severed")
        # else:
        #     logging.error("Socket closed but fileno did not return -1")
        #
        # # srclient.srclient.make_connection()
        #
        # # srclient.thread.join()
        # logging.debug("Connection reestablished")

    def return_message(self):
        return self.msg


# TODO This class is not functioning yet after restructure. FIX!
class MulticastReceiver:
    """
    This class handles the receiving of the output data from the MT Subreflector
    It is sent to a multicast port by  the subreflector_client.py module, and
    picked up here (as well as anywhere else) for decoding. This is then used
    to read the output data of the subreflector, and see if the input comands
    gave the desired change, for example.
    """

    def __init__(self):
        logging.debug("Initializing MulticastReciever")
        self.sock = None  # set in __init__ for PEP-8 consistency
        self.data = None
        self.thread = None
        self.mcast_data = None
        self.init_multicast()

    def init_multicast(self):
        """" want to use a context manager here, but it's important to have a
        seperate method to recv data rather than create a socket every time, so
        sadly it was simpler to avoid a context manager, and risk not closing
        the socket (though, it shouldn't be closed while the program is running)
        """
        logging.debug("Setting up the multicast receiver")
        try:

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(MULTICAST)

            group = socket.inet_aton(MULTICAST[0])
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP,
                                 socket.IP_ADD_MEMBERSHIP, mreq)

        except ConnectionError or OSError:
            logging.exception("There was an exception setting "
                              "up the multicast receiver")

    def start_mcast_receiver_thread(self):

        try:
            logging.debug(f"Creating Thread")
            self.thread = threading.Thread(
                target=self.get_new_status, args=(), name='update_mcast')

            self.thread.daemon = False  # Demonize thread
            logging.debug(f"Threading set to {self.thread.daemon}.")
            self.thread.start()

        except Exception as Er:
            print(Er)
            logging.exception("Exception starting Startup_Subreflector_Client")


    def recv_mcast_data(self):
        try:
            logging.debug("Recieved new multicast packet")

            multicastdata_bytes, address = self.sock.recvfrom(***REMOVED*** * 50)
            multicastdata_bytes, address = self.sock.recvfrom(***REMOVED*** * 50)
            multicastdata_bytes, address = self.sock.recvfrom(***REMOVED*** * 50)
            multicastdata_bytes, address = self.sock.recvfrom(***REMOVED*** * 50)
            multicastdata_bytes, address = self.sock.recvfrom(***REMOVED*** * 50)

            self.data = json.loads(str(multicastdata_bytes.decode('utf-8')))

            print(self.data["status-data-active-surface"]["Elevation-angle[deg]"])

        except OSError or ConnectionError as E:
            logging.exception(f"Error occurred receiving multicast data: {E}")

    def assert_static_data(self):
        # These should always be the same/True, only corruption or changes to
        # the fundamental structure of the message contents will change these.
        try:
            assert self.data["start-flag"] == 0x1DFCCF1A
            assert self.data["length-of-data-packet"] == 1760
            assert self.data["id=status-message(50)"] == 50
            assert self.data["end-flag"] == 0xA1FCCFD1
        except AssertionError as E:
            logging.exception("Assertion of static data failed. Critical "
                              "change must have been found in output string")
            print(f"Assertion of expected static data failed: {E}")

    def deepcopy_mcast_data(self):
        # Deep copy to avoid any issues with memory linkage
        logging.debug("New message deep copied to instance variable")
        self.mcast_data = copy.deepcopy(self.data)
        logging.debug(
            f'Interlock elv self.last: {self.mcast_data["status-data-active-surface"]["Elevation-angle[deg]"]}')

    def get_new_status(self):
        try:
            logging.debug("getting_new_mcast")
            self.recv_mcast_data()
            self.assert_static_data()
            self.deepcopy_mcast_data()

        except Exception as E:
            msg = "There was an exception receiving and processing a " \
                  "multicast message from the subreflector."
            logging.exception(msg)
            print(msg, E)

    # def find_diferences(self):
    #     self.assert_static_data()
    #     self.data["status-data-interlock"]["simulation"] = "hello"
    #     self.data["status-data-interlock"]["override"] = "world"
    #
    #     headers = ["status-data-interlock",
    #                "status-data-polarization-drive",
    #                "status-data-hexapod-drive",
    #                "status-data-focus-change-drive",
    #                "status-data-active-surface",
    #                "status-data-bottom-flap",
    #                "status-data-mirror-flap",
    #                "status-data-temperature",
    #                "status-data-irig-b-system"]
    #
    #     differences = []
    #
    #     # Runs through all the subfields in the dict and find value differences
    #     for item in headers:
    #         value = {k: self.data[item][k] for k, _ in
    #                  set(self.data[item].items())
    #                  - set(self.last_msg[item].items())}
    #
    #         if value:
    #             # If value is different, append to differences
    #             differences += (item, value)
    #
    #     print(differences)

    def get_elevation(self):
        self.get_new_status()
        mcast_data = self.mcast_data  # local to prevent race condition

        elevation = mcast_data["status-data-active-surface"] \
            ["Elevation-angle[deg]"]
        return elevation

    def get_polar_position(self):
        self.get_new_status()
        mcast_data = self.mcast_data  # local to prevent race condition

        p_soll = mcast_data["status-data-polarization-drive"] \
            ["current-actual-position[deg]"]

        return p_soll

    def get_hexapod_positions(self):
        self.get_new_status()
        mcast_data = self.mcast_data  # local to prevent race condition

        hxpd_header = "status-data-hexapod-drive"
        hxpd_xlin = mcast_data[hxpd_header]["current_position_x_linear[mm]"]
        hxpd_ylin = mcast_data[hxpd_header]["current_position_y_linear[mm]"]
        hxpd_zlin = mcast_data[hxpd_header]["current_position_z_linear[mm]"]
        hxpd_xrot = mcast_data[hxpd_header]["current_position_x_rotation[deg]"]
        hxpd_yrot = mcast_data[hxpd_header]["current_position_y_rotation[deg]"]
        hxpd_zrot = mcast_data[hxpd_header]["current_position_z_rotation[deg]"]
        return (hxpd_xlin, hxpd_ylin, hxpd_zlin,
                hxpd_xrot, hxpd_yrot, hxpd_zrot)


    def check_hexapod_activated(self):
        self.get_new_status()
        mcast_data = self.mcast_data  # local to prevent race condition
        hxpd_header = "status-data-hexapod-drive"
        flag = True

        try:
            assert mcast_data[hxpd_header]["status_of_the_subsystem_"] == 1
            for i in range(5):
                break_open = f"spindle{i + 1}-brake-open"
                assert mcast_data[hxpd_header][break_open] == 1

                spin_active = f"spindle{i + 1}-spindle-active"
                assert mcast_data[hxpd_header][spin_active] == 1
        except AssertionError:
            flag = False

        return flag

    def check_hexapod_is_stationary(self):
        self.get_new_status()
        mcast_data = self.mcast_data  # local to prevent race condition
        hxpd_header = "status-data-hexapod-drive"
        flag_for_linear, flag_for_rotation = True, True

        stationary_linear = ["target_position_x_linear[mm]",
                             "target_position_y_linear[mm]",
                             "target_position_z_linear[mm]",
                             "target_speed_linear[mm/s]",
                             ]

        stationary_rotation = ["target_position_x_rotation[deg]",
                               "target_position_y_rotation[deg]",
                               "target_position_z_rotation[deg]",
                               "target_speed_rotation[deg/s]"]
        try:
            for i in stationary_linear:
                assert mcast_data[hxpd_header][i] == 0
        except AssertionError:
            flag_for_linear = False

        try:
            for i in stationary_rotation:
                assert mcast_data[hxpd_header][i] == 0
        except AssertionError:
            flag_for_rotation = False

        return flag_for_linear, flag_for_rotation


def start_server(use_test_server):
    logging.basicConfig(filename='subreflector_program_debug.log',
                        filemode='w', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(thread)d - '
                               '%(module)s - %(funcName)s- %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')

    start_connections(use_test_server)
