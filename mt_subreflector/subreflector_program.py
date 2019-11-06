import os
import sys
import time
import json
import copy
import socket
import struct
import logging
import threading
import socketserver

import mt_subreflector.subreflector_client as subreflector_client_module
import mt_subreflector.mtcommand as mtcommand_module


def start_connections():
    # This try block starts up two unique classes, which created threaded
    # instances, one calling a server to run in the background, the other
    # starting an instance in the subreflector_client.py module that receives
    # and processes the data collected from the SR (subreflector)
    try:

        logging.debug("Start Startup_Subreflector_Client instance")
        srclient_instance.start_sr_client()

        logging.debug("Start UDP server instance")
        udpserver_instance.start_udp_server()

    except Exception as E:
        logging.exception("An exception occured starting the threaded classes")
        raise E


class StartupSubreflectorClient:
    """
    Simple class that correctly starts up the subreflectorclient.py script
    in a thread so it can process data from the MT Subreflector in real time.
    This is set up as a non-daemon thread to work in the background, and to hang
    until closed manually.
    """

    def __init__(self):
        self.thread = None
        self.stop_threads = False
        self.sr_instance = subreflector_client_module.SubreflectorClient(use_test_server=True)


    def start_sr_client(self):
        """
        This method sets up a non-daemon thread to initiate the
        subreflector_client.py in the background. It calls the next method which
        is what actually instantiates SubreflectorClient
        """

        try:
            logging.debug(f"Creating Thread")
            self.thread = threading.Thread(target=self.run_sr_client, args=(),
                                           name='sr_client_module')
            self.thread.daemon = True  # Demonize thread
            logging.debug(f"Threading set to {self.thread.daemon}. Starting Thread")
            self.thread.start()
            logging.debug("Thread started successfully")
            print(f"THREAD ID: {self.thread.ident}")

            # self.thread.join()
        except Exception as Er:
            print(Er)
            logging.exception("Exception starting Startup_Subreflector_Client")


    # @staticmethod
    def run_sr_client(self):
        """
        creates instance of SubreflectorClient which starts listening to the
        subreflector.
        """
        self.sr_instance.main()

    def close_sr_client(self):
        logging.debug("User initiated Subreflector connection reset")
        self.sr_instance.end_connection()

        time.sleep(2)
        logging.debug("Starting connection again")
        self.sr_instance.make_connection()


class UDPServer:
    """
      Simple class that starts listening to the udp-telnet server for
      any incomming messages. These messages are then accessed and received by
      MYUDPHandler which calls the necesarry class to parse the user input. This
       is set up as a non-daemon thread to work in the background, and to hang
      until closed manually.
      """

    def __init__(self):
        self.server = None  # This is just for pep-8 style
        logging.debug("Initialized")

    def start_udp_server(self):
        """
        This method sets up a non-daemon thread to initiate the
        ThreadingUDPserver in the background. This is the code
        that connects to the server to read the input data and parse it
        :return:
        """
        dest_address = (LOCAL_ADDRESS, UDPTELNET_PORT)
        logging.debug(f"ThreadingUDPServer accessing address:"
                      f" {dest_address[0]}, port: {dest_address[1]}")
        self.server = ThreadingUDPServer(dest_address, MyUDPHandler)

        logging.debug(f"Setting server to run forever")
        t = threading.Thread(target=self.server.serve_forever, name='UDPSERVER')

        t.daemon = False  # Do not demonize thread
        logging.debug(f"ThreadingUDPServer now running in a non-daemon "
                      f"thread ({threading.current_thread}) in background")
        t.start()

    # def stop_udp_telnet(self):
    #     if self.server:
    #         print("shutting down telnet")
    #         self.server.shutdown()
    #         self.server.server_close()
    #         self.server = None
    #     else:
    #         print("UDP-Telnet already shutdown")
    #
    # def return_telnet_status(self):
    #     if self.server:
    #         return True
    #     elif not self.server:
    #         return False
    #
    # def close_sr_program(self):
    #     doublecheck = ''.join(input("Do you want to close? ").lower().split())
    #     if doublecheck == 'yes':
    #         print("Closing Subreflector Program")
    #         if self.return_telnet_status():
    #             self.stop_udp_telnet()
    #         exit()
    #     elif doublecheck == 'no':
    #         self.user_input()
    #     else:
    #         print("Unrecognized command. Say 'yes' or 'no'")
    #         self.close_sr_program()


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
    def handle(self):

        logging.debug("Telnet: Message received from udp-telnet")
        # takes message, decodes to string and - all whitespace (by rejoining)
        telnet_msg = self.request[0].decode('utf-8')
        print(telnet_msg)
        # telnet_msg = ''.join(self.request[0].decode('utf-8').split())

        logging.debug("Telnet: Sending message to CommandModule")
        udp_parser_instnace = UDPCommandParser(telnet_msg)
        msg = udp_parser_instnace.return_message()
        logging.debug("Telnet: Message returned from CommandModule")

        logging.debug("Telnet: Setting up returnsocket")
        returnsocket = self.request[1]
        returnsocket.sendto(msg.encode(), self.client_address)
        logging.debug("Telnet: Message sent back to udp-telnet client")


class UDPCommandParser:
    """
    Instantiating this class takes a string and parses it to return the correct
    response to the user
    """

    def __init__(self, command_message):
        """
        :param command_message: str - message to parse
        """
        self.user_command = command_message
        self.msg = ''
        self.obsprefix = None
        self.commandprefix = None
        # self.multicastdata = sdh_multicast()
        self.check_obsprefix()

    # # # # # General parsing section # # # # #
    def check_obsprefix(self):

        print(threading.enumerate())
        # Checks to make sure the command starts with correct string
        if self.user_command.startswith("EFFELSBERG:"):
            self.obsprefix = 'EFFELSBERG:'
            self.user_command = self.user_command[11:]
            self.check_mtsubreflector_called()
        else:
            logging.info("Given command had the incorrect prefix "
                         "(was not 'EFFELSBERG:')")
            self.msg = "Command should start with 'EFFELSBERG:'"

    def check_mtsubreflector_called(self):
        if self.user_command.startswith("MTSUBREFLECTOR:"):
            self.obsprefix = 'MTSUBREFLECTOR:'
            self.user_command = self.user_command[15:]
            self.probe_command()

        else:
            logging.info("Given command had the incorrect prefix "
                         "(was not 'MTSUBREFLECTOR:')")
            self.msg = "Command should start with 'MTSUBREFLECTOR:'"
            
    def probe_command(self):

        # Checks what is in the string, and calls the correct method

        if self.user_command.startswith('INTERLOCK:'):
            self.interlock_control()
        elif self.user_command.startswith('HEXAPOD:'):
            self.hexapod_control()
        elif self.user_command.startswith('ASF:'):
            self.asf_control()
        elif self.user_command.startswith('POLAR:'):
            self.polar_control()
        elif "RESETCONNECTION" in self.user_command:
            self.reset_connections()

        else:
            string = f'{self.user_command} is not a valid input. The valid ' \
                     f'inputs are "INTERLOCK", "HEXAPOD", "ASF", "POLAR", and' \
                     f'"RESETCONNECTION'
            self.msg = string

    # # # # # Interlock parsing section # # # # #
    def interlock_control(self):
        # Splits user_command into command part, and if number, as 2nd val
        try:
            command, value = self.user_command[10:].strip().split(" ", 1)
            logging.debug(command)
            logging.debug(value)
        except ValueError:
            logging.exception("Number given couldn't be converted to a float")
        else:
            if command == "DEACTIVATE":
                mtcommand_instance.deactivate_mt()
                self.msg = "Interlock deactivated"
            elif command == "ACTIVATE":
                mtcommand_instance.activate_mt()
                self.msg = "Interlock activated"
            elif command == "SET":
                mtcommand_instance.set_mt_elevation(float(value))
                self.msg = f"Interlock elevation set to {value}"
            else:
                self.msg = 'message type not recognized. Correct types for ' \
                           'interlock are: "ACTIVATE", "DEACTIVATE", "SET"'

    # # # # # Hexapod parsing section # # # # #
    def hexapod_control(self):
        self.user_command = self.user_command[8:]

        if "GETABS" in self.user_command:
            positions = multicast_instance.get_hexapod_positions()
            message = f"\n hxpd_xlin: {positions[0]}," \
                      f"\n hxpd_ylin: {positions[1]}," \
                      f"\n hxpd_zlin: {positions[2]}," \
                      f"\n hxpd_xrot: {positions[3]}," \
                      f"\n hxpd_yrot: {positions[4]}," \
                      f"\n hxpd_zrot: {positions[5]}"
            self.msg = message

        elif "SETABS" in self.user_command or "SETREL" in self.user_command:
            try:
                # Remove "SETABS" from string and split into list at every space
                values = self.user_command[6:].strip().split(" ")
                new_val = [float(i) for i in values]  # change str to float
                assert len(new_val) == 8  # Make sure there's exactly 8 entries

            except AssertionError as E:
                print(E)
                logging.exception("Assertion error. Improper number in "
                                  "parameters or wrong type")

            except ValueError as E:
                msg = "Error converting entries to floats. Other " \
                      "characters may be present"
                logging.exception(msg)
                print(msg, E)

            else:
                if "SETABS" in self.user_command:
                    mtcommand_instance.preset_abs_hxpd(new_val[0], new_val[1],
                                                       new_val[2], new_val[3],
                                                       new_val[4], new_val[5],
                                                       new_val[6], new_val[7])

                    self.msg = "Set absolute values for hexapod to \n" \
                               f" xlin: {new_val[0]}, ylin: {new_val[1]}," \
                               f" zlin: {new_val[2]}, v_lin: {new_val[3]} \n" \
                               f" xrot: {new_val[4]}, yrot: {new_val[5]}," \
                               f" zrot: {new_val[6]}, v_rot: {new_val[7]}"

                elif "SETREL" in self.user_command:
                    positions = multicast_instance.get_hexapod_positions()
                    new_xlin = positions[0] + new_val[0]
                    new_ylin = positions[1] + new_val[1]
                    new_zlin = positions[2] + new_val[2]
                    new_xrot = positions[4] + new_val[4]
                    new_yrot = positions[5] + new_val[5]
                    new_zrot = positions[6] + new_val[6]
                    mtcommand_instance.preset_abs_hxpd(new_xlin, new_ylin,
                                                       new_zlin, new_val[3],
                                                       new_xrot, new_yrot,
                                                       new_zrot, new_val[7])
                    self.msg = "adding relative values for hexapod: \n" \
                               f" xlin: {new_val[0]}, ylin: {new_val[1]}," \
                               f" zlin: {new_val[2]}, v_lin: {new_val[3]} \n" \
                               f" xrot: {new_val[4]}, yrot: {new_val[5]}," \
                               f" zrot: {new_val[6]}, v_rot: {new_val[7]}"

        elif "DEACTIVATE" in self.user_command:
            mtcommand_instance.deactivate_hxpd()
        elif "ACTIVATE" in self.user_command:
            mtcommand_instance.activate_hxpd()
        elif "STOP" in self.user_command:
            mtcommand_instance.stop_hxpd()
        elif "INTERLOCK" in self.user_command():
            mtcommand_instance.interlock_hxpd()
        elif "ERROR" in self.user_command:
            mtcommand_instance.acknowledge_error_on_hxpd()

        else:
            self.msg = 'message type not recognized. Correct types for ' \
                       'hexapod are: "GETABS", "SETABS", "SETREL", ' \
                       '"ACTIVATE", "DEACTIVATE", "STOP", "INTERLOCK", "ERROR"'

    # # # # # Polar parsing section # # # # #

    def asf_control(self):
        self.user_command = self.user_command[4:]

        if "IGNORE" in self.user_command:
            mtcommand_instance.ignore_asf()
        elif "DEACTIVATE" in self.user_command:
            mtcommand_instance.deactivate_asf()
        elif "REST" in self.user_command:
            mtcommand_instance.rest_pos_asf()
        elif "ERROR" in self.user_command:
            mtcommand_instance.acknowledge_error_on_asf()
        elif "STOP" in self.user_command:
            mtcommand_instance.stop_asf()
        elif "PRESET" in self.user_command:
            mtcommand_instance.preset_pos_asf()
        elif "AUTO" in self.user_command:
            mtcommand_instance.set_automatic_asf()
        elif "OFFSET" in self.user_command:
            mtcommand_instance.set_offset_asf()
        else:
            self.msg = 'message type not recognized. Correct types for asf' \
                       'are: "IGNORE", "DEACTIVATE", "REST", "ERROR", "STOP",' \
                       '"PRESET", "AUTO", "OFFSET"'

    # # # # # Polar parsing section # # # # #
    def polar_control(self):
        self.user_command = self.user_command[6:]

        if "GETABS" in self.user_command:
            positions = multicast_instance.get_polar_position()
            message = f"\n P_soll[deg]: {positions[0]},"
            self.msg = message
        elif "DEACTIVATE" in self.user_command:
            mtcommand_instance.deactivate_polar()

        elif "ACTIVATE" in self.user_command:
            mtcommand_instance.activate_polar()

        elif "STOP" in self.user_command:
            mtcommand_instance.stop_polar()

        elif "ERROR" in self.user_command:
            mtcommand_instance.acknowledge_error_on_polar()

        elif "SETABS" in self.user_command:
            # TODO: Add test for right format from user on numbers. Very hacky currently
            self.user_command = self.user_command[6:]
            p_soll, v_cmd = self.user_command[10:].strip().split(" ", 1)
            logging.debug(p_soll)
            logging.debug(v_cmd)
            mtcommand_instance.preset_abs_polar(p_soll, v_cmd)

        elif "SETREL" in self.user_command:
            self.user_command = self.user_command[6:]
            p_soll, v_cmd = self.user_command[10:].strip().split(" ", 1)
            logging.debug(p_soll)
            logging.debug(v_cmd)
            mtcommand_instance.preset_rel_polar(p_soll, v_cmd)

        else:
            self.msg = 'message type not recognized. Correct types for polar' \
                       'are: "GETABS", "SETABS", "SETREL", ' \
                       '"ACTIVATE", "DEACTIVATE", "STOP", "ERROR"'

    # # # # # Reset Connections # # # # #
    def reset_connections(self):
        self.msg = "Resetting connections. Please wait 5 seconds"
        srclient_instance.close_sr_client()


    # def multicast_variable(self):
    #     # Finds the location of the variable in the multicast message
    #     loc = self.multicastdata.find(self.user_command)
    #     # takes a bit more on the right side than needed. This is trimmed next
    #     multicast_var = (self.multicastdata[loc:loc + 50])
    #
    #     # Format to remove everything after comma, and remove a quote
    #     multicast_var = multicast_var.replace('"', '').split(",", 1)[0]
    #     self.set_message(multicast_var)

    def return_message(self):
        return self.msg


class MulticastReceiver:
    """
    This class handles the receiving of the output data from the MT Subreflector
    It is sent to a multicast port by  the subreflector_client.py module, and
    picked up here (as well as anywhere else) for decoding. This is then used
    to read the output data of the subreflector, and see if the input comands
    gave the desired change, for example.
    """

    def __init__(self):
        self.sock = None  # set in __init__ for PEP-8 consistency
        self.data = None
        self.last_msg = None
        self.init_multicast()

    def init_multicast(self):
        # Todo Make this into a context manager class maybe?
        """" want to use a context manager here, but it's important to have a
        seperate method to recv data rather than create a socket every time, so
        sadly it was simpler to avoid a context manager, and risk not closing
        the socket (though, it shouldn't be closed while the program is running)
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('', SR_MULTI)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(server_address)

        group = socket.inet_aton(MULTICAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def recv_mcast_data(self):
        multicastdata_bytes, address = self.sock.recvfrom(***REMOVED*** * 200)
        self.data = json.loads(str(multicastdata_bytes.decode('utf-8')))

    def assert_static_data(self):
        # These should always be the same/True, only corruption or changes to
        # the fundamental structure of the message contents will change these.
        try:
            assert self.data["start-flag"] == 0x1DFCCF1A
            assert self.data["length-of-data-packet"] == 1760
            assert self.data["id=status-message(50)"] == 50
            assert self.data["end-flag"] == 0xA1FCCFD1
        except AssertionError as e:
            logging.exception("Assertion of static data failed. Critical "
                              "change must have been made to output string")
            print(f"Assertion of expected static data failed: {e}")

    def deepcopy_mcast_data(self):
        # Deep copy to avoid any issues with comparisons
        self.last_msg = copy.deepcopy(self.data)

    def get_new_status(self):
        try:
            self.recv_mcast_data()
            self.assert_static_data()
            self.deepcopy_mcast_data()
        except Exception as E:
            msg = "There was an exception receiving and processing a " \
                  "multicast message from the subreflector."
            logging.exception(msg)
            print(msg, E)

    def find_diferences(self):
        self.assert_static_data()
        self.data["status-data-interlock"]["simulation"] = "hello"
        self.data["status-data-interlock"]["override"] = "world"

        headers = ["status-data-interlock",
                   "status-data-polarization-drive",
                   "status-data-hexapod-drive",
                   "status-data-focus-change-drive",
                   "status-data-active-surface",
                   "status-data-bottom-flap",
                   "status-data-mirror-flap",
                   "status-data-temperature",
                   "status-data-irig-b-system",
                   ]

        differences = []
        for item in headers:
            value = {k: self.data[item][k] for k, _ in
                     set(self.data[item].items())
                     - set(self.last_msg[item].items())}

            # value = {k: self.data[item] for k in set(self.data[item]) -
            #          set(self.last_msg[item])}
            # diff = set(self.last_msg[item].items()) \
            #        - set(self.data[item].items())
            # print(diff)
            # value = diff
            if value:
                differences += (item, value)

        print(differences)

    def get_polar_position(self):
        self.get_new_status()
        # local to prevent race condition
        lastmessage = self.last_msg
        p_soll = lastmessage["status-data-polarization-drive"] \
            ["current-actual-position-[deg]"]
        return p_soll

    def get_hexapod_positions(self):
        self.get_new_status()
        # local to prevent race condition
        lastmessage = self.last_msg
        hxpd_header = "status-data-hexapod-drive"
        hxpd_xlin = lastmessage[hxpd_header]["current_position_x_linear_[mm]"]
        hxpd_ylin = lastmessage[hxpd_header]["current_position_y_linear_[mm]"]
        hxpd_zlin = lastmessage[hxpd_header]["current_position_z_linear_[mm]"]
        hxpd_xrot = lastmessage[hxpd_header]["current_position_x_rotation[deg]"]
        hxpd_yrot = lastmessage[hxpd_header]["current_position_y_rotation[deg]"]
        hxpd_zrot = lastmessage[hxpd_header]["current_position_z_rotation[deg]"]
        return (hxpd_xlin, hxpd_ylin, hxpd_zlin,
                hxpd_xrot, hxpd_yrot, hxpd_zrot)

    def print_mcast_data(self):
        self.get_new_status()
        self.find_diferences()


class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


if __name__ == "__main__":
    logging.basicConfig(filename='debug/subreflector_program_debug.log',
                        filemode='w', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(module)s '
                               '- %(funcName)s- %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')

    # Constants
    UDPTELNET_PORT = ***REMOVED***
    SDH_PORT = 1602  # Port where sdh output can be reached
    SR_MULTI = ***REMOVED***  # Port where subreflector_client.py outputs JSON
    LOCAL_ADDRESS = ''  # local IP
    MULTICAST_GROUP = '***REMOVED***'  # Multicast IP address
    dict_ = {}  # Temporary, will get to this fix later

    # Instanciate classes here so they're in global
    multicast_instance = MulticastReceiver()  # For recieving data from SR
    mtcommand_instance = mtcommand_module.MTCommand()  # Sending commands to SR
    srclient_instance = StartupSubreflectorClient()  # Module listens on port 8k
    udpserver_instance = UDPServer()  # Communication to user for commands

    start_connections()
