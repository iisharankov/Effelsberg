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


def main():

    logging.basicConfig(filename='debug/subreflector_program_debug.log', filemode='w', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(module)s '
                               '- %(funcName)s- %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')

    # This try block starts up two unique classes, which created threaded
    # instances, one calling a server to run in the background, the other
    # starting an instance in the subreflector_client.py module that receives
    # and processes the data collected from the SR (subreflector)
    try:
        logging.debug("Start Startup_Subreflector_Client instance")
        StartupSubreflectorClient().start_sr_client()

        logging.debug("Start InputCommands instance")
        InputCommands().start_udp_telnet()

    except Exception as E:
        logging.exception("An exception occured starting the threaded classes")
        raise E




# Communication class
class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This is the class that is instantiated in InputCommands as a non-daemon
    thread. This works on the functionality of socketserver, and the handel
    method listens to any incoming message on the IP/Port combo and passes it
    through to a different class which is responsible for parsing the message
    and forwarding it to mtcommand.py, which directly communicates to the
    subreflector
    """

    def setup(self):
        pass
        # print("Incoming message")

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

        # Message to return to client
        # print(f"Sending message: {msg}")

        logging.debug("Telnet: Setting up returnsocket")
        returnsocket = self.request[1]
        returnsocket.sendto(msg.encode(), self.client_address)
        logging.debug("Telnet: Message sent back to udp-telnet client")

    def finish(self):
        pass
        # print("End of message.")


class StartupSubreflectorClient:
    """
    Simple class that correctly starts up the subreflectorclient.py script
    in a thread so it can process data from the MT Subreflector in real time.
    This is set up as a non-deamon thread to work in the background, and to hang
    until closed manually. todo: ask/then implement way to close thread
    """

    def start_sr_client(self):
        """
        This method sets up a non-deamon thread to initiate the
        subreflector_client.py in the background. It calls the next method which
        is what actually instantiates SubreflectorClient
        """
        try:
            logging.debug(f"Creating Thread")
            thread = threading.Thread(target=self.run_sc_client, args=())
            thread.daemon = True  # Demonize thread
            logging.debug(f"Threading set to {thread.daemon}. Starting Thread")
            thread.start()
            logging.debug("Thread started successfully")
        except Exception as Er:
            print(Er)
            logging.exception("Exception starting Startup_Subreflector_Client")

    def run_sc_client(self):
        """
        creates instance of SubreflectorClient which starts listening to the
        subreflector.
         """
        subreflector_client_module.SubreflectorClient(use_test_server=True)


class InputCommands:
    """ todo: change name from udp-telnet to other server?
      Simple class that correctly starts listening to the udp-telnet server for
      any incomming messages. These messages are then accessed and received by
      MYUDPHandler which calls the necesarry class to parse the user input. This
       is set up as a non-deamon thread to work in the background, and to hang
      until closed manually. todo: ask/then implement way to close thread
      """
    def __init__(self):
        self.server = None  # This is just for pep-8 style
        logging.debug("Initialized")


    def start_udp_telnet(self):
        """
        This method sets up a non-deamon thread to initiate the
        ThreadingUDPserver in the background. It calls the next method which is
        what actually instantiates ThreadingUDPServer
        """
        try:
            logging.debug("Creating Thread")
            thread = threading.Thread(target=self.run_udp_telnet, args=())
            thread.daemon = False  # Do not demonize thread
            logging.debug(f"Threading set to {thread.daemon}. Starting thread")
            thread.start()
            logging.debug("Thread started successfully")
        except Exception as Er:
            print(Er)
            logging.exception("Exception starting telnet")

    def run_udp_telnet(self):
        """
        This is the thread that is started by the above method. This is the code
        that connects to the server to read the input data and parse it
        :return:
        """
        dest_address = (LOCAL_ADDRESS, UDPTELNET_PORT)
        logging.debug(f"ThreadingUDPServer accessing address:"
                      f" {dest_address[0]}, port: {dest_address[1]}")
        self.server = ThreadingUDPServer(dest_address, MyUDPHandler)

        # if True: # TODO: removes while loop. is fine?
        logging.debug(f"Setting server to run forever")
        t = threading.Thread(target=self.server.serve_forever)
        logging.debug(f"ThreadingUDPServer now running in a non-deamon "
                      f"thread ({threading.current_thread}) in background")
        t.start()


        # This commented out part was necessary since i put everything in a
        # while loop. Though it seems that was not needed.

        # # This next line is system critical so is in an enclosed try block
        # try:
        #     logging.debug("Joining thread")
        #     # t.join()  # CRITICAL or WILL CRASH (runtimeerror)
        # except Exception as E:
        #     logging.exception("Error joining thread. Memory"
        #                      " overflow would occur if continued. System "
        #                       " did abrupt exit to prevent possible crash")
        #     print(f"Exception when joining ThreadingUDPServer: {E}. Please"
        #           f" read debug logs. System forcefully exited. No Cleanup")
        #     time.sleep(.0001)
        #     os._exit(1) # This is a very abrupt stop (no cleanup is done),
        #     # but the alternative is reaching a thread limit if t.join fails

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
    
    def check_obsprefix(self):
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

        elif self.user_command.startswith('POLAR:'):
            self.polar_control()

        elif self.user_command.startswith('returnvariables'):
            self.return_variables_in_json()

        elif self.user_command.startswith('clearvariables'):
            self.clear_variables()

        # elif self.user_command in self.multicastdata:
        #     self.multicast_variable()

        else:
            string = f"{self.user_command} is not a valid input or not recognized"
            self.msg = string

    def interlock_control(self):
        # Splits user_command into command part, and if number, as 2nd val
        try:
            command, value = self.user_command[10:].strip().split(" ", 1)
        except ValueError:
            logging.exception("Number given couldn't be converted to a float")
        else:
            if command == "OFF":
                mtcommand_instance.deactivate_mt()
                self.msg = "Interlock deactivated"
            elif command == "ON":
                mtcommand_instance.activate_mt()
                self.msg = "Interlock activated"
            elif command == "SET":
                mtcommand_instance.set_mt_elevation(float(value))
                self.msg = f"Interlock elevation set to {value}"
            else:
                self.msg = 'message type not recognized. Correct types for ' \
                           'interlock are: "ON", "OFF", "SET"'

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
                numbers = [float(i) for i in values]  # change str to float
                assert len(numbers) == 8  # Make sure there's exactly 8 entries

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
                    mtcommand_instance.preset_abs_hxpd(numbers[0], numbers[1],
                                                       numbers[2], numbers[3],
                                                       numbers[4], numbers[5],
                                                       numbers[6], numbers[7])

                    self.msg = "Set absolute values for hexapod to \n" \
                               f" xlin: {numbers[0]}, ylin: {numbers[1]}," \
                               f" zlin: {numbers[2]}, v_lin: {numbers[3]} \n" \
                               f" xrot: {numbers[4]}, yrot: {numbers[5]}," \
                               f" zrot: {numbers[6]}, v_rot: {numbers[7]}"

                elif "SETREL" in self.user_command:
                    positions = multicast_instance.get_hexapod_positions()
                    new_xlin = positions[0] + numbers[0]
                    new_ylin = positions[1] + numbers[1]
                    new_zlin = positions[2] + numbers[2]
                    new_xrot = positions[4] + numbers[4]
                    new_yrot = positions[5] + numbers[5]
                    new_zrot = positions[6] + numbers[6]
                    mtcommand_instance.preset_abs_hxpd(new_xlin, new_ylin,
                                                       new_zlin, numbers[3],
                                                       new_xrot, new_yrot,
                                                       new_zrot, numbers[7])
                    self.msg = "adding relative values for hexapod to \n" \
                               f" xlin: {numbers[0]}, ylin: {numbers[1]}," \
                               f" zlin: {numbers[2]}, v_lin: {numbers[3]} \n" \
                               f" xrot: {numbers[4]}, yrot: {numbers[5]}," \
                               f" zrot: {numbers[6]}, v_rot: {numbers[7]}"

        elif "DEACTIVATE" in self.user_command:
            mtcommand_instance.deactivate_hxpd()
        elif "ACTIVATE" in self.user_command:
            mtcommand_instance.activate_hxpd()
        elif "STOP" in self.user_command:
            mtcommand_instance.stop_hxpd()
        elif "ERROR" in self.user_command:
            mtcommand_instance.acknowledge_error_on_hxpd()

        else:
            self.msg = 'message type not recognized. Correct types for ' \
                       'hexapod are: "GETABS", "SETABS", "SETREL", ' \
                       '"ACTIVATE", "DEACTIVATE", "STOP" "ERROR"'

    def polar_control(self):
        self.user_command = self.user_command[6:]

    def new_variable(self):
        self.user_command = self.user_command.replace('variable:', '')

        try:
            # telnet_msg is in form "variable=value" or "variable", so
            # check there is one or no "=" signs
            assert self.user_command.count("=") <= 1

        except AssertionError:
            string = "More than one equals sign in message. Don't assert."
            self.msg = string

        else:
            # If 1 =  sign, then we know something is being set
            if self.user_command.count("=") == 1:
                # Replace = with : to parse into temp JSON
                variable_name, value = self.user_command.split('=', 1)
                string = "no"
                self.msg = string

            # if no "=" sign, then user wants value of variable_name given
            else:
                assert self.user_command.count("=") == 0  # Should never fail
                self.return_variable()

    def return_variable(self):
        if self.user_command in dict_:

            string = f'The set value for {self.user_command} ' \
                     f'is {dict_[self.user_command]}'
            self.msg = string

        else:
            string = f"{self.user_command} was not found/was never set"
            self.msg = string

    def clear_variables(self):
        print('Clearing variables')
        dict_.clear()
        string = "All the variables were cleared"
        self.msg = string

    def return_variables_in_json(self):
        string = json.dumps(dict_)
        self.msg = string

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
        multicastdata_bytes, address = self.sock.recvfrom(***REMOVED****200)
        self.data =  json.loads(str(multicastdata_bytes.decode('utf-8')))

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
        # Deep copy to avoid any bugs
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
        self.data["status-data-interlock"]["simulation"] = "hell"
        self.data["status-data-interlock"]["override"] = "poop"

        list = ["status-data-interlock",
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
        for item in list:
            value = {k: self.data[item][k] for k, _ in
                     set(self.data[item].items()) - set(self.last_msg[item].items())}

            # value = {k: self.data[item] for k in set(self.data[item]) -
            #          set(self.last_msg[item])}
            # diff = set(self.last_msg[item].items()) - set(self.data[item].items())
            # print(diff)
            # value = diff
            if value:
                differences += (item, value)

        print(differences)

    def get_hexapod_positions(self):
        self.get_new_status()
        # local to prevent race condition
        lastmessage = self.last_msg
        hxpd_xlin = lastmessage["status-data-hexapod-drive"]\
            ["current_position_x_linear_[mm]"]
        hxpd_ylin = lastmessage["status-data-hexapod-drive"] \
            ["current_position_y_linear_[mm]"]
        hxpd_zlin = lastmessage["status-data-hexapod-drive"] \
            ["current_position_z_linear_[mm]"]
        hxpd_xrot = lastmessage["status-data-hexapod-drive"] \
            ["current_position_x_rotation_[deg]"]
        hxpd_yrot = lastmessage["status-data-hexapod-drive"] \
            ["current_position_y_rotation_[deg]"]
        hxpd_zrot = lastmessage["status-data-hexapod-drive"] \
            ["current_position_z_rotation_[deg]"]
        return (hxpd_xlin, hxpd_ylin, hxpd_zlin,
                hxpd_xrot, hxpd_yrot, hxpd_zrot)

    def print_mcast_data(self):
        self.get_new_status()
        self.find_diferences()

class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

# def sdh_multicast():  # This just is for the SDH port, not SRClient
#     # Currently this opens a multicast port just to get the multicastdata
#     # and then closes to save the resource. Can change to always open if needed
#     logging.debug("SDH_Multicast: sdh_multicast request made, opening sdh socket")
#     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
#
#         logging.debug("SDH_Multicast: sdh socket created, "
#                       "binding to server address")
#         server_address = ('', SDH_PORT)  # sdh json
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         sock.bind(server_address)
#         logging.debug("SDH_Multicast: Bound to server address, "
#                       "listening for message")
#
#         group = socket.inet_aton(MULTICAST_GROUP)
#         mreq = struct.pack('4sL', group, socket.INADDR_ANY)
#         sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
#         multicastdata_bytes, address = sock.recvfrom(300_000)
#
#         logging.debug("SDH_Multicast: Multicast data received, closing "
#                       "sdh socket and returning multicast data")
#         return str(multicastdata_bytes)


if __name__ == "__main__":
    # Constants
    UDPTELNET_PORT = ***REMOVED***
    SDH_PORT = 1602  # Port where sdh output can be reached
    SR_MULTI = ***REMOVED***  # Port where subreflector_client.py outputs JSON
    LOCAL_ADDRESS = '' # local IP
    MULTICAST_GROUP = '***REMOVED***'  # Multicast IP address
    dict_ = {}  # Temporary, will get to this fix later

    multicast_instance = MulticastReceiver()
    mtcommand_instance = mtcommand_module.MTCommand()

    main()

