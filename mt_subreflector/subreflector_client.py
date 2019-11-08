#!/usr/bin/env python

import time
import json
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

    def main(self):
        self.activate_multicasting()
        self.make_connection()

    def activate_multicasting(self):
        # Sets up multicast socket for later use
        self.multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.multicast_sock.setsockopt(socket.IPPROTO_IP,
                                       socket.IP_MULTICAST_TTL, 1)

    def use_test_server(self, test_server):
        """
        Swaps real SR address for local if instance of class is needed for tests
        :param flag: bool
            if flag set to true, the address for the test server is used instead
        :return: IP address and port for the respective subreflector
        """

        if test_server:
            msg = "Connected to local subreflector in MockSubreflector.py"
            print(msg)
            logging.debug(msg)
            return LOCAL_ADDR, SR_PORT

        else:
            msg = f"Connected to mt_subreflector. IP: {SR_ADDR} - " \
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
        sock.send(b"\n")  # Initial message is needed to start stream
        count = 0
        while 1:
            time.sleep(1)
            try:

                # Due to the nature of TCP/IP connections, and the properties
                # of the subreflector, it is safer to receive two messages and
                # find a full one inside between the flags. Explained in docs
                data = sock.recv((1760*2))

            except socket.timeout:
                msg = f"Socket timed out after {sock.gettimeout()} seconds"
                logging.debug(msg)
                print(msg, " Trying again.")

            else:
                # Finds a start flag and cuts everything before it
                startindex = (data.find(b"\x1a\xcf\xfc\x1d"))
                data = data[startindex:]

                # Finds the first end flag afterwards and does the same
                endindex = (data.find(b"\xd1\xcf\xfc\xa1"))
                full_msg = data[:endindex + 4]  # +4 as endindex is start string

                if len(full_msg) != 1760:
                    msg = "The message didn't register the correct length, " \
                          "data may have been added/lost, changing the length."
                    logging.exception(msg)
                    raise ValueError(msg)

                # Expected length of the message
                elif len(full_msg) == 1760:

                    # Optional pickling of the message for storage
                    # pickle.dump(full_msg, open("Subreflector_Output_Nov-4.p", 'ab'))

                    # TODO: Next line just here for testing reasons
                    count += 1
                    print(f"\rmessage sent x{count}", end='')

                    status_message = self.package_msg(full_msg)
                    self.multicast_sock.sendto(status_message, MULTICAST)

            finally:
                with self.lock:
                     if self.connection_flag:
                        self.connection_flag = False  # resets the flag
                        logging.debug("Closing socket")
                        break

    def end_connection(self):
        with self.lock:
            self.connection_flag = True

        logging.debug("flag to close socket triggered")

    def package_msg(self, bytes_string):
        """
        Take given bytes string and parses it to be made into a JSON, then
        returns the encoded JSON string

        :param bytes_string: binary string
            input string from subreflector, recieved from socket
        :return: JSON string that is is encoded into binary for future socket
        """
        status_message = self.decompose_to_json(bytes_string)

        # Dumps JSON dict to string and encodes to bytes to send over socket
        status_string = json.dumps(status_message, indent=2).encode('utf-8')
        return status_string

    def decompose_to_json(self, bytes_string):
        """
        Receives a bytes string and decodes it with struct, then parses
        all the values into a JSON dict

        :param bytes_string: binary string
            input string from subreflector, received from socket
        :return: JSON dict
        """

        try:
            header, il, power, polar, hxpd, focus, asf, bdkl, spkl, temp, \
            foctime, last = self.decode_struct(bytes_string)
        except Exception as e:
            msg = f"There was an error deconstructing the message: {e}"
            logging.exception(msg)
            print(msg)
        else:
            status_message = {

                'start-flag': header[0],
                'length-of-data-packet': header[1],
                'number-of-the-command': header[2],
                'id=status-message(50)': header[3],

                'status-data-interlock':
                    {
                        'active-control-unit': il[0],
                        'simulation': il[1],
                        'control-voltage-on': il[2],
                        'control-active': il[3],
                        'service-mode': il[4],
                        'override': il[5],
                        'feed-in-regeneration-module-on': il[6],
                        'infeed-regenerative-module-ready-warning': il[7],
                        'feed-in-feedback-module-temperature-warning': il[8],
                        'infeed-regenerative-module-error-timeout': il[9],
                        'fieldbus': il[10],
                        'interlock-cycle-monitoring': il[11],
                        'interlock-emergency-stop-(safety-device)': il[12],
                        'interlock-emergency-stop-chain': il[13],
                        'interlock-software': il[14],
                        'emergency-stop-button-(bit-coded)': il[15],
                        'communication-with-host-interrupted-(warning)': il[16],
                        'last-sent-mode-command': il[17],
                        'command-response-of-the-mode-command': il[18],
                        'last-sent-parameter-command': il[19],
                        'command-response-of-the-parameter-command': il[20],
                        'parameter-1-of-the-parameter-command': il[21],
                        'parameter-2-of-the-parameter-command': il[22],
                    },

                # 'power':
                #     {
                #         'unknown1': power[0],
                #         'unknown2': power[1],
                #         'unknown3': power[2],
                #         'unknown4': power[3],
                #         'unknown5': power[4],
                #     },

                'status-data-polarization-drive':
                    {
                        'status-of-the-subsystem': polar[0],
                        'trajectory-status': polar[1],
                        'collective-status-error': polar[2],
                        'collective-status-warning': polar[3],
                        ###
                        'spindle1-software-emergency-stop': polar[4],
                        'spindle1-hardware-emergency-stop': polar[5],
                        'spindle1-emergency-stop-switch-up': polar[6],
                        'spindle1-emergency-limit-switch-down': polar[7],
                        'spindle1-group-error': polar[8],
                        'spindle1-brakes': polar[9],
                        'spindle1-power': polar[10],
                        'spindle1-servo-system': polar[11],
                        'spindle1-engine-timeout': polar[12],
                        'spindle1-speedometer': polar[13],
                        'spindle1-maximum-engine-speed-achieved': polar[14],
                        'spindle1-iquad_t;': polar[15],
                        'spindle1-position-encoder-hardware': polar[16],
                        'spindle1-position-encoder-step': polar[17],
                        'spindle1-position-outside-the-defined-area': polar[18],
                        'spindle1-maximum-position-deviation-reached': polar[19],
                        'spindle1-fieldbus': polar[20],
                        'spindle1-feed-back-module-servo': polar[21],
                        'spindle1-override': polar[22],
                        'spindle1-command-timeout': polar[23],
                        'spindle1-communication-error-with-host-computer': polar[24],
                        'spindle1-referencescoder-is-missing': polar[25],
                        'spindle1-referencescoder-error': polar[26],
                        'spindle1-speed-governor': polar[27],
                        'spindle1-maximum-speed-deviation-achieved': polar[28],
                        'spindle1-lock': polar[29],
                        'spindle1-external-error': polar[30],
                        ###
                        'spindle1-speed-mode': polar[31],
                        'spindle1_-override': polar[32],
                        'spindle1-stow-pin-in': polar[33],
                        'spindle1-parameter-error': polar[34],
                        'spindle1-power-heating': polar[35],
                        'spindle1-power-breaks': polar[36],
                        'spindle1-power-drives': polar[37],
                        'spindle1-power-external-24v': polar[38],
                        'spindle1-power-internal-24v': polar[39],
                        'spindle1-power-control': polar[40],
                        'spindle1_-position-encoder-hardware': polar[41],
                        'spindle1-engine-warning': polar[42],
                        'spindle1-mazimum-torque-achieved': polar[43],
                        'spindle1-degraded-fashion': polar[44],
                        'spindle1-security-device': polar[45],
                        'spindle1-ermaus': polar[46],
                        'spindle1-ermservo': polar[47],
                        'spindle1-emergency-limit-switch-up': polar[48],
                        'spindle1_-emergency-limit-switch-down': polar[49],
                        'spindle1-pre-limit-switch-up': polar[50],
                        'spindle1-pre-limit-switch-down': polar[51],
                        'spindle1-operating-limit-switch-up': polar[52],
                        'spindle1-operating-limit-switch-down': polar[53],
                        'spindle1-software-limit-switch-up': polar[54],
                        'spindle1-software-limit-switch-down': polar[55],
                        ###
                        'detailed-list-of-individual-warnings.-please-'
                        'refer-structure-5.11': polar[56],
                        'position-trajectory[deg]': polar[56],
                        'current-actual-position[deg]': polar[57],
                        'current-position-offset[deg]': polar[58],
                        'current-position-deviation[deg]': polar[59],
                        'current-web-speed[deg-/-s]': polar[60],
                        'current-speed[deg-/-s]': polar[61],
                        'current-speed-deviation[deg-/-s': polar[62],
                        'current-acceleration[deg-/-s²]': polar[63],
                        'display-of-the-selected-motors-(bit-coded)': polar[64],
                        ###
                        'engine1-current-position[deg]': polar[65],
                        'engine1-current-speed[deg-/-s]': polar[66],
                        'engine1-current-torque[nm]': polar[67],
                        'engine1-current-engine-utilization[%]': polar[68],
                        'engine1-initialization': polar[69],
                        'engine1-engine-ready': polar[70],
                        'engine1-engine-active': polar[71],
                        'engine1-speed-=-0': polar[72],
                        'engine1-speed-​​ok': polar[73],
                        'engine1-position-ok': polar[74],
                        'engine1-bus-error': polar[75],
                        'engine1-servo-error': polar[76],
                        'engine1-sensor-error': polar[77],
                        'engine1-reserve': polar[78],
                        'engine1-warning': polar[79],
                        'engine1-reserve-#2': polar[80],
                        'engine1-i²-t': polar[81],
                        'engine1-temperature-amplifier': polar[82],
                        'engine1-temperature-motor': polar[83],
                        'engine1-uic': polar[84],
                        'engine1-maximum-speed-achieved': polar[85],
                        'engine1-maximum-torque-achieved': polar[86],
                        ###
                        'engine2-current-position[deg]': polar[87],
                        'engine2-current-speed[deg-/-s]': polar[88],
                        'engine2-current-torque[nm]': polar[89],
                        'engine2-current-engine-utilization[%]': polar[90],
                        'engine2-initialization': polar[91],
                        'engine2-engine-ready': polar[92],
                        'engine2-engine-active': polar[93],
                        'engine2-speed-=-0': polar[94],
                        'engine2-speed-​​ok': polar[95],
                        'engine2-position-ok': polar[96],
                        'engine2-bus-error': polar[97],
                        'engine2-servo-error': polar[98],
                        'engine2-sensor-error': polar[99],
                        'engine2-reserve': polar[100],
                        'engine2-warning': polar[101],
                        'engine2-reserve-#2': polar[102],
                        'engine2-i²-t': polar[103],
                        'engine2-temperature-amplifier': polar[104],
                        'engine2-temperature-motor': polar[105],
                        'engine2-uic': polar[106],
                        'engine2-maximum-speed-achieved': polar[107],
                        'engine2-maximum-torque-achieved': polar[108],
                        ###
                        'last-sent-mode-command': polar[109],
                        'command-response-of-the-mode-command': polar[110],
                        'target-position-of-the-mode-command': polar[111],
                        'target-speed-of-the-mode-command': polar[112],
                        'last-sent-parameter-command': polar[113],
                        'command-response-of-the-parameter-command': polar[114],
                        'parameter-1-of-the-parameter-command': polar[115],
                        'parameter-2-of-the-parameter-command': polar[116],
                    },

                'status-data-hexapod-drive':
                    {
                        'status_of_the_subsystem_': hxpd[0],
                        'current_position_x_linear[mm]': hxpd[1],
                        'current_position_y_linear[mm]': hxpd[2],
                        'current_position_z_linear[mm]': hxpd[3],
                        'current_position_x_rotation[deg]': hxpd[4],
                        'current_position_y_rotation[deg]': hxpd[5],
                        'current_position_z_rotation[deg]': hxpd[6],
                        'collective_status_error': hxpd[7],
                        'collective_status_warning': hxpd[8],
                        # _warning_struct
                        'collective_message_warning_spindle': hxpd[9],
                        'collective_signal_pre-limit_switch_spindle_down': hxpd[10],
                        'group_message_pre-limit_switch_spindle_up': hxpd[11],
                        'group_message_maximum_speed': hxpd[12],
                        'inverse_transformation': hxpd[13],
                        'override_active': hxpd[14],
                        '3d_linear_position_preset_switch_down': hxpd[15],
                        '3d_linear_position_preset_switch_up': hxpd[16],
                        '3d_rotation_position_preset_switch_down': hxpd[17],
                        '3d_rotation_position_preset_switch_up': hxpd[18],
                        '3d_x_linear_position_operating_limit_switch_down': hxpd[19],
                        '3d_x_linear_position_limit_switch_up': hxpd[20],
                        '3d_y_linear_position_operating_limit_switch_down': hxpd[21],
                        '3d_y_linear_position_limit_switch_up': hxpd[22],
                        '3d_z_linear_position_operating_limit_switch_down': hxpd[23],
                        '3d_z_linear_position_limit_switch_up': hxpd[24],
                        '3d_x_rotation_position_operating_limit_switch_down': hxpd[25],
                        '3d_x_rotation_position_operating_limit_switch_up': hxpd[26],
                        '3d_y_rotation_position_operating_limit_switch_down': hxpd[27],
                        '3d_y_rotation_position_operating_limit_switch_up': hxpd[28],
                        '3d_z_rotation_position_operating_limit_switch_down': hxpd[29],
                        '3d_z_rotation_position_operating_limit_switch_up': hxpd[30],
                        # _end_warning_structure
                        'current_mode_of_linear_motion': hxpd[31],
                        'current_mode_of_rotation': hxpd[32],
                        'display_of_the_selected_motors_(bit-coded)': hxpd[33],
                        ####-start-of-spindles-####
                        'spindle1-current-position[mm/deg]': hxpd[34],
                        'spindle1-current-target-position[mm/deg]': hxpd[35],
                        'spindle1-current-position-offset[mm/deg]': hxpd[36],
                        'spindle1-current-speed[mm/s/deg/s]': hxpd[37],
                        'spindle1-current-target-speed[mm/s/deg/s]': hxpd[38],
                        'spindle1-current-web-speed[mm/s/deg/s]': hxpd[39],
                        'spindle1-position-deviation[mm/deg]': hxpd[40],
                        'spindle1-current-utilization-of-the-spindle[%]': hxpd[41],
                        'spindle1-spindle-active': hxpd[42],
                        'spindle1-brake-open': hxpd[43],
                        'spindle1-general-error': hxpd[44],
                        # -start-of-error-structure-(5.11-in-manual)
                        'spindle1-software-emergency-stop': hxpd[45],
                        'spindle1-hardware-emergency-stop': hxpd[46],
                        'spindle1-emergency-stop-switch-up': hxpd[47],
                        'spindle1-emergency-limit-switch-down': hxpd[48],
                        'spindle1-group-error': hxpd[49],
                        'spindle1-brakes': hxpd[50],
                        'spindle1-power': hxpd[51],
                        'spindle1-servo-system': hxpd[52],
                        'spindle1-engine-timeout': hxpd[53],
                        'spindle1-speedometer': hxpd[54],
                        'spindle1-maximum-engine-speed-achieved': hxpd[55],
                        'spindle1-iquad_t;': hxpd[56],
                        'spindle1-position-encoder-hardware': hxpd[57],
                        'spindle1-position-encoder-step': hxpd[58],
                        'spindle1-position-outside-the-defined-area': hxpd[59],
                        'spindle1-maximum-position-deviation-reached': hxpd[60],
                        'spindle1-fieldbus': hxpd[61],
                        'spindle1-feed-back-module-servo': hxpd[62],
                        'spindle1-override': hxpd[63],
                        'spindle1-command-timeout': hxpd[64],
                        'spindle1-communication-error-with-host-computer': hxpd[65],
                        'spindle1-referencescoder-is-missing': hxpd[66],
                        'spindle1-referencescoder-error': hxpd[67],
                        'spindle1-speed-governor': hxpd[68],
                        'spindle1-maximum-speed-deviation-achieved': hxpd[69],
                        'spindle1-lock': hxpd[70],
                        'spindle1-external-error': hxpd[71],
                        #  end-of-error-structure-(5.11-in-manual)
                        'spindle1-general-warning': hxpd[72],
                        # -start-of-warning-structure-(5.12-in-manual)
                        'spindle1-speed-mode': hxpd[73],
                        'spindle1_-override': hxpd[74],
                        'spindle1-stow-pin-in': hxpd[75],
                        'spindle1-parameter-error': hxpd[76],
                        'spindle1-power-heating': hxpd[77],
                        'spindle1-power-breaks': hxpd[78],
                        'spindle1-power-drives': hxpd[79],
                        'spindle1-power-external-24v': hxpd[80],
                        'spindle1-power-internal-24v': hxpd[81],
                        'spindle1-power-control': hxpd[82],
                        'spindle1_-position-encoder-hardware': hxpd[83],
                        'spindle1-engine-warning': hxpd[84],
                        'spindle1-mazimum-torque-achieved': hxpd[85],
                        'spindle1-degraded-fashion': hxpd[86],
                        'spindle1-security-device': hxpd[87],
                        'spindle1-ermaus': hxpd[88],
                        'spindle1-ermservo': hxpd[89],
                        'spindle1-emergency-limit-switch-up': hxpd[90],
                        'spindle1_-emergency-limit-switch-down': hxpd[91],
                        'spindle1-pre-limit-switch-up': hxpd[92],
                        'spindle1-pre-limit-switch-down': hxpd[93],
                        'spindle1-operating-limit-switch-up': hxpd[94],
                        'spindle1-operating-limit-switch-down': hxpd[95],
                        'spindle1-software-limit-switch-up': hxpd[96],
                        'spindle1-software-limit-switch-down': hxpd[97],
                        # -note: some-of-the-above-have-a-underscore-as-there-are
                        # -doubles-in-the-error-and-warning-stuct-with-the-same-name
                        ####
                        'spindle2-current-position[mm/deg]': hxpd[98],
                        'spindle2-current-target-position[mm/deg]': hxpd[99],
                        'spindle2-current-position-offset[mm/deg]': hxpd[100],
                        'spindle2-current-speed[mm/s/deg/s]': hxpd[101],
                        'spindle2-current-target-speed[mm/s/deg/s]': hxpd[102],
                        'spindle2-current-web-speed[mm/s/deg/s]': hxpd[103],
                        'spindle2-position-deviation[mm/deg]': hxpd[104],
                        'spindle2-current-utilization-of-the-spindle[%]': hxpd[105],
                        'spindle2-spindle-active': hxpd[106],
                        'spindle2-brake-open': hxpd[107],
                        'spindle2-general-error': hxpd[108],
                        'spindle2-software-emergency-stop': hxpd[109],
                        'spindle2-hardware-emergency-stop': hxpd[110],
                        'spindle2-emergency-stop-switch-up': hxpd[111],
                        'spindle2-emergency-limit-switch-down': hxpd[112],
                        'spindle2-group-error': hxpd[113],
                        'spindle2-brakes': hxpd[114],
                        'spindle2-power': hxpd[115],
                        'spindle2-servo-system': hxpd[116],
                        'spindle2-engine-timeout': hxpd[117],
                        'spindle2-speedometer': hxpd[118],
                        'spindle2-maximum-engine-speed-achieved': hxpd[119],
                        'spindle2-iquad_t;': hxpd[120],
                        'spindle2-position-encoder-hardware': hxpd[121],
                        'spindle2-position-encoder-step': hxpd[122],
                        'spindle2-position-outside-the-defined-area': hxpd[123],
                        'spindle2-maximum-position-deviation-reached': hxpd[124],
                        'spindle2-fieldbus': hxpd[125],
                        'spindle2-feed-back-module-servo': hxpd[126],
                        'spindle2-override': hxpd[127],
                        'spindle2-command-timeout': hxpd[128],
                        'spindle2-communication-error-with-host-computer': hxpd[129],
                        'spindle2-referencescoder-is-missing': hxpd[130],
                        'spindle2-referencescoder-error': hxpd[131],
                        'spindle2-speed-governor': hxpd[132],
                        'spindle2-maximum-speed-deviation-achieved': hxpd[133],
                        'spindle2-lock': hxpd[134],
                        'spindle2-external-error': hxpd[135],
                        'spindle2-general-warning': hxpd[136],
                        'spindle2-speed-mode': hxpd[137],
                        'spindle2_-override': hxpd[138],
                        'spindle2-stow-pin-in': hxpd[139],
                        'spindle2-parameter-error': hxpd[140],
                        'spindle2-power-heating': hxpd[141],
                        'spindle2-power-breaks': hxpd[142],
                        'spindle2-power-drives': hxpd[143],
                        'spindle2-power-external-24v': hxpd[144],
                        'spindle2-power-internal-24v': hxpd[145],
                        'spindle2-power-control': hxpd[146],
                        'spindle2_-position-encoder-hardware': hxpd[147],
                        'spindle2-engine-warning': hxpd[148],
                        'spindle2-mazimum-torque-achieved': hxpd[149],
                        'spindle2-degraded-fashion': hxpd[150],
                        'spindle2-security-device': hxpd[151],
                        'spindle2-ermaus': hxpd[152],
                        'spindle2-ermservo': hxpd[153],
                        'spindle2-emergency-limit-switch-up': hxpd[154],
                        'spindle2_-emergency-limit-switch-down': hxpd[155],
                        'spindle2-pre-limit-switch-up': hxpd[156],
                        'spindle2-pre-limit-switch-down': hxpd[157],
                        'spindle2-operating-limit-switch-up': hxpd[158],
                        'spindle2-operating-limit-switch-down': hxpd[159],
                        'spindle2-software-limit-switch-up': hxpd[160],
                        'spindle2-software-limit-switch-down': hxpd[161],
                        ####
                        'spindle3-current-position[mm/deg]': hxpd[162],
                        'spindle3-current-target-position[mm/deg]': hxpd[163],
                        'spindle3-current-position-offset[mm/deg]': hxpd[164],
                        'spindle3-current-speed[mm/s/deg/s]': hxpd[165],
                        'spindle3-current-target-speed[mm/s/deg/s]': hxpd[166],
                        'spindle3-current-web-speed[mm/s/deg/s]': hxpd[167],
                        'spindle3-position-deviation[mm/deg]': hxpd[168],
                        'spindle3-current-utilization-of-the-spindle[%]': hxpd[169],
                        'spindle3-spindle-active': hxpd[170],
                        'spindle3-brake-open': hxpd[171],
                        'spindle3-general-error': hxpd[172],
                        'spindle3-software-emergency-stop': hxpd[173],
                        'spindle3-hardware-emergency-stop': hxpd[174],
                        'spindle3-emergency-stop-switch-up': hxpd[175],
                        'spindle3-emergency-limit-switch-down': hxpd[176],
                        'spindle3-group-error': hxpd[177],
                        'spindle3-brakes': hxpd[178],
                        'spindle3-power': hxpd[179],
                        'spindle3-servo-system': hxpd[180],
                        'spindle3-engine-timeout': hxpd[181],
                        'spindle3-speedometer': hxpd[182],
                        'spindle3-maximum-engine-speed-achieved': hxpd[183],
                        'spindle3-iquad_t;': hxpd[184],
                        'spindle3-position-encoder-hardware': hxpd[185],
                        'spindle3-position-encoder-step': hxpd[186],
                        'spindle3-position-outside-the-defined-area': hxpd[187],
                        'spindle3-maximum-position-deviation-reached': hxpd[188],
                        'spindle3-fieldbus': hxpd[189],
                        'spindle3-feed-back-module-servo': hxpd[190],
                        'spindle3-override': hxpd[191],
                        'spindle3-command-timeout': hxpd[192],
                        'spindle3-communication-error-with-host-computer': hxpd[193],
                        'spindle3-referencescoder-is-missing': hxpd[194],
                        'spindle3-referencescoder-error': hxpd[195],
                        'spindle3-speed-governor': hxpd[196],
                        'spindle3-maximum-speed-deviation-achieved': hxpd[197],
                        'spindle3-lock': hxpd[198],
                        'spindle3-external-error': hxpd[199],
                        'spindle3-general-warning': hxpd[200],
                        'spindle3-speed-mode': hxpd[201],
                        'spindle3_-override': hxpd[202],
                        'spindle3-stow-pin-in': hxpd[203],
                        'spindle3-parameter-error': hxpd[204],
                        'spindle3-power-heating': hxpd[205],
                        'spindle3-power-breaks': hxpd[206],
                        'spindle3-power-drives': hxpd[207],
                        'spindle3-power-external-24v': hxpd[208],
                        'spindle3-power-internal-24v': hxpd[209],
                        'spindle3-power-control': hxpd[210],
                        'spindle3_-position-encoder-hardware': hxpd[211],
                        'spindle3-engine-warning': hxpd[212],
                        'spindle3-mazimum-torque-achieved': hxpd[213],
                        'spindle3-degraded-fashion': hxpd[214],
                        'spindle3-security-device': hxpd[215],
                        'spindle3-ermaus': hxpd[216],
                        'spindle3-ermservo': hxpd[217],
                        'spindle3-emergency-limit-switch-up': hxpd[218],
                        'spindle3_-emergency-limit-switch-down': hxpd[219],
                        'spindle3-pre-limit-switch-up': hxpd[220],
                        'spindle3-pre-limit-switch-down': hxpd[221],
                        'spindle3-operating-limit-switch-up': hxpd[222],
                        'spindle3-operating-limit-switch-down': hxpd[223],
                        'spindle3-software-limit-switch-up': hxpd[224],
                        'spindle3-software-limit-switch-down': hxpd[225],
                        ####
                        'spindle4-current-position[mm/deg]': hxpd[226],
                        'spindle4-current-target-position[mm/deg]': hxpd[227],
                        'spindle4-current-position-offset[mm/deg]': hxpd[228],
                        'spindle4-current-speed[mm/s/deg/s]': hxpd[229],
                        'spindle4-current-target-speed[mm/s/deg/s]': hxpd[230],
                        'spindle4-current-web-speed[mm/s/deg/s]': hxpd[231],
                        'spindle4-position-deviation[mm/deg]': hxpd[232],
                        'spindle4-current-utilization-of-the-spindle[%]': hxpd[233],
                        'spindle4-spindle-active': hxpd[234],
                        'spindle4-brake-open': hxpd[235],
                        'spindle4-general-error': hxpd[236],
                        'spindle4-software-emergency-stop': hxpd[237],
                        'spindle4-hardware-emergency-stop': hxpd[238],
                        'spindle4-emergency-stop-switch-up': hxpd[239],
                        'spindle4-emergency-limit-switch-down': hxpd[240],
                        'spindle4-group-error': hxpd[241],
                        'spindle4-brakes': hxpd[242],
                        'spindle4-power': hxpd[243],
                        'spindle4-servo-system': hxpd[244],
                        'spindle4-engine-timeout': hxpd[245],
                        'spindle4-speedometer': hxpd[246],
                        'spindle4-maximum-engine-speed-achieved': hxpd[247],
                        'spindle4-iquad_t;': hxpd[248],
                        'spindle4-position-encoder-hardware': hxpd[249],
                        'spindle4-position-encoder-step': hxpd[250],
                        'spindle4-position-outside-the-defined-area': hxpd[251],
                        'spindle4-maximum-position-deviation-reached': hxpd[252],
                        'spindle4-fieldbus': hxpd[253],
                        'spindle4-feed-back-module-servo': hxpd[254],
                        'spindle4-override': hxpd[255],
                        'spindle4-command-timeout': hxpd[256],
                        'spindle4-communication-error-with-host-computer': hxpd[257],
                        'spindle4-referencescoder-is-missing': hxpd[258],
                        'spindle4-referencescoder-error': hxpd[259],
                        'spindle4-speed-governor': hxpd[260],
                        'spindle4-maximum-speed-deviation-achieved': hxpd[261],
                        'spindle4-lock': hxpd[262],
                        'spindle4-external-error': hxpd[263],
                        'spindle4-general-warning': hxpd[264],
                        'spindle4-speed-mode': hxpd[265],
                        'spindle4_-override': hxpd[266],
                        'spindle4-stow-pin-in': hxpd[267],
                        'spindle4-parameter-error': hxpd[268],
                        'spindle4-power-heating': hxpd[269],
                        'spindle4-power-breaks': hxpd[270],
                        'spindle4-power-drives': hxpd[271],
                        'spindle4-power-external-24v': hxpd[272],
                        'spindle4-power-internal-24v': hxpd[273],
                        'spindle4-power-control': hxpd[274],
                        'spindle4_-position-encoder-hardware': hxpd[275],
                        'spindle4-engine-warning': hxpd[276],
                        'spindle4-mazimum-torque-achieved': hxpd[277],
                        'spindle4-degraded-fashion': hxpd[278],
                        'spindle4-security-device': hxpd[279],
                        'spindle4-ermaus': hxpd[280],
                        'spindle4-ermservo': hxpd[281],
                        'spindle4-emergency-limit-switch-up': hxpd[282],
                        'spindle4_-emergency-limit-switch-down': hxpd[283],
                        'spindle4-pre-limit-switch-up': hxpd[284],
                        'spindle4-pre-limit-switch-down': hxpd[285],
                        'spindle4-operating-limit-switch-up': hxpd[286],
                        'spindle4-operating-limit-switch-down': hxpd[287],
                        'spindle4-software-limit-switch-up': hxpd[288],
                        'spindle4-software-limit-switch-down': hxpd[289],
                        ####
                        'spindle5-current-position[mm/deg]': hxpd[290],
                        'spindle5-current-target-position[mm/deg]': hxpd[291],
                        'spindle5-current-position-offset[mm/deg]': hxpd[292],
                        'spindle5-current-speed[mm/s/deg/s]': hxpd[293],
                        'spindle5-current-target-speed[mm/s/deg/s]': hxpd[294],
                        'spindle5-current-web-speed[mm/s/deg/s]': hxpd[295],
                        'spindle5-position-deviation[mm/deg]': hxpd[296],
                        'spindle5-current-utilization-of-the-spindle[%]': hxpd[297],
                        'spindle5-spindle-active': hxpd[298],
                        'spindle5-brake-open': hxpd[299],
                        'spindle5-general-error': hxpd[300],
                        'spindle5-software-emergency-stop': hxpd[301],
                        'spindle5-hardware-emergency-stop': hxpd[302],
                        'spindle5-emergency-stop-switch-up': hxpd[303],
                        'spindle5-emergency-limit-switch-down': hxpd[304],
                        'spindle5-group-error': hxpd[305],
                        'spindle5-brakes': hxpd[306],
                        'spindle5-power': hxpd[307],
                        'spindle5-servo-system': hxpd[308],
                        'spindle5-engine-timeout': hxpd[309],
                        'spindle5-speedometer': hxpd[310],
                        'spindle5-maximum-engine-speed-achieved': hxpd[311],
                        'spindle5-iquad_t;': hxpd[312],
                        'spindle5-position-encoder-hardware': hxpd[313],
                        'spindle5-position-encoder-step': hxpd[314],
                        'spindle5-position-outside-the-defined-area': hxpd[315],
                        'spindle5-maximum-position-deviation-reached': hxpd[316],
                        'spindle5-fieldbus': hxpd[317],
                        'spindle5-feed-back-module-servo': hxpd[318],
                        'spindle5-override': hxpd[319],
                        'spindle5-command-timeout': hxpd[320],
                        'spindle5-communication-error-with-host-computer': hxpd[321],
                        'spindle5-referencescoder-is-missing': hxpd[322],
                        'spindle5-referencescoder-error': hxpd[323],
                        'spindle5-speed-governor': hxpd[324],
                        'spindle5-maximum-speed-deviation-achieved': hxpd[325],
                        'spindle5-lock': hxpd[326],
                        'spindle5-external-error': hxpd[327],
                        'spindle5-general-warning': hxpd[328],
                        'spindle5-speed-mode': hxpd[329],
                        'spindle5_-override': hxpd[330],
                        'spindle5-stow-pin-in': hxpd[331],
                        'spindle5-parameter-error': hxpd[332],
                        'spindle5-power-heating': hxpd[333],
                        'spindle5-power-breaks': hxpd[334],
                        'spindle5-power-drives': hxpd[335],
                        'spindle5-power-external-24v': hxpd[336],
                        'spindle5-power-internal-24v': hxpd[337],
                        'spindle5-power-control': hxpd[338],
                        'spindle5_-position-encoder-hardware': hxpd[339],
                        'spindle5-engine-warning': hxpd[340],
                        'spindle5-mazimum-torque-achieved': hxpd[341],
                        'spindle5-degraded-fashion': hxpd[342],
                        'spindle5-security-device': hxpd[343],
                        'spindle5-ermaus': hxpd[344],
                        'spindle5-ermservo': hxpd[345],
                        'spindle5-emergency-limit-switch-up': hxpd[346],
                        'spindle5_-emergency-limit-switch-down': hxpd[347],
                        'spindle5-pre-limit-switch-up': hxpd[348],
                        'spindle5-pre-limit-switch-down': hxpd[349],
                        'spindle5-operating-limit-switch-up': hxpd[350],
                        'spindle5-operating-limit-switch-down': hxpd[351],
                        'spindle5-software-limit-switch-up': hxpd[352],
                        'spindle5-software-limit-switch-down': hxpd[353],
                        ####
                        'spindle6-current-position[mm/deg]': hxpd[354],
                        'spindle6-current-target-position[mm/deg]': hxpd[355],
                        'spindle6-current-position-offset[mm/deg]': hxpd[356],
                        'spindle6-current-speed[mm/s/deg/s]': hxpd[357],
                        'spindle6-current-target-speed[mm/s/deg/s]': hxpd[358],
                        'spindle6-current-web-speed[mm/s/deg/s]': hxpd[359],
                        'spindle6-position-deviation[mm/deg]': hxpd[360],
                        'spindle6-current-utilization-of-the-spindle[%]': hxpd[361],
                        'spindle6-spindle-active': hxpd[362],
                        'spindle6-brake-open': hxpd[363],
                        'spindle6-general-error': hxpd[364],
                        'spindle6-software-emergency-stop': hxpd[365],
                        'spindle6-hardware-emergency-stop': hxpd[366],
                        'spindle6-emergency-stop-switch-up': hxpd[367],
                        'spindle6-emergency-limit-switch-down': hxpd[368],
                        'spindle6-group-error': hxpd[369],
                        'spindle6-brakes': hxpd[370],
                        'spindle6-power': hxpd[371],
                        'spindle6-servo-system': hxpd[372],
                        'spindle6-engine-timeout': hxpd[373],
                        'spindle6-speedometer': hxpd[374],
                        'spindle6-maximum-engine-speed-achieved': hxpd[375],
                        'spindle6-iquad_t;': hxpd[376],
                        'spindle6-position-encoder-hardware': hxpd[377],
                        'spindle6-position-encoder-step': hxpd[378],
                        'spindle6-position-outside-the-defined-area': hxpd[379],
                        'spindle6-maximum-position-deviation-reached': hxpd[380],
                        'spindle6-fieldbus': hxpd[381],
                        'spindle6-feed-back-module-servo': hxpd[382],
                        'spindle6-override': hxpd[383],
                        'spindle6-command-timeout': hxpd[384],
                        'spindle6-communication-error-with-host-computer': hxpd[385],
                        'spindle6-referencescoder-is-missing': hxpd[386],
                        'spindle6-referencescoder-error': hxpd[387],
                        'spindle6-speed-governor': hxpd[388],
                        'spindle6-maximum-speed-deviation-achieved': hxpd[389],
                        'spindle6-lock': hxpd[390],
                        'spindle6-external-error': hxpd[391],
                        'spindle6-general-warning': hxpd[392],
                        'spindle6-speed-mode': hxpd[393],
                        'spindle6_-override': hxpd[394],
                        'spindle6-stow-pin-in': hxpd[395],
                        'spindle6-parameter-error': hxpd[396],
                        'spindle6-power-heating': hxpd[397],
                        'spindle6-power-breaks': hxpd[398],
                        'spindle6-power-drives': hxpd[399],
                        'spindle6-power-external-24v': hxpd[400],
                        'spindle6-power-internal-24v': hxpd[401],
                        'spindle6-power-control': hxpd[402],
                        'spindle6_-position-encoder-hardware': hxpd[403],
                        'spindle6-engine-warning': hxpd[404],
                        'spindle6-mazimum-torque-achieved': hxpd[405],
                        'spindle6-degraded-fashion': hxpd[406],
                        'spindle6-security-device': hxpd[407],
                        'spindle6-ermaus': hxpd[408],
                        'spindle6-ermservo': hxpd[409],
                        'spindle6-emergency-limit-switch-up': hxpd[410],
                        'spindle6_-emergency-limit-switch-down': hxpd[411],
                        'spindle6-pre-limit-switch-up': hxpd[412],
                        'spindle6-pre-limit-switch-down': hxpd[413],
                        'spindle6-operating-limit-switch-up': hxpd[414],
                        'spindle6-operating-limit-switch-down': hxpd[415],
                        'spindle6-software-limit-switch-up': hxpd[416],
                        'spindle6-software-limit-switch-down': hxpd[417],
                        ####-end-of-spindles-####
                        'last_sent_mode_command_hexapod': hxpd[418],
                        'command_response_of_the_mode_command_hexapod': hxpd[419],
                        'last_sent_mode_command_linear': hxpd[420],
                        'command_response_of_the_mode_command_linear': hxpd[421],
                        'target_position_x_linear[mm]': hxpd[422],
                        'nominal_position_y_linear[mm]': hxpd[423],
                        'target_position_z_linear[mm]': hxpd[424],
                        'target_speed_linear[mm/s]': hxpd[425],
                        'last_sent_mode_command_rotation': hxpd[426],
                        'command_response_of_the_mode_command_rotation': hxpd[427],
                        'target_position_x_rotation[deg]': hxpd[428],
                        'target_position_y_rotation[deg]': hxpd[429],
                        'target_position_z_rotation[deg]': hxpd[430],
                        'target_speed_linear[deg/s]': hxpd[431],
                        'last_sent_parameter_command': hxpd[432],
                        'command_response_of_the_parameter_command': hxpd[433],
                        'parameter_1_of_the_parameter_command': hxpd[434],
                        'parameter_2_of_the_parameter_command': hxpd[435],
                        # There exists a way to loop the spindles, but honestly
                        # it's a bit too complicated to do it, and add it to a
                        # dict (they're unordered!). it could be done but would
                        # be too confusing for what it would save in lines. plus
                        # this is easily modifiable per spindle. it repeats,
                        # but it works
                    },

                'status-data-focus-change-drive':
                    {
                        'status-of-the-subsystem': focus[0],
                        'collective-status-warning': focus[1],
                        'collective-status-error': focus[2],
                        'primary-focus-position': focus[3],
                        'secondary-focus-position': focus[4],
                        'receiver-change-position': focus[5],
                        'display-of-the-selected-motors(bit-coded)': focus[6],
                        'current-target-position[mm]': focus[7],
                        'current-position[mm]': focus[8],
                        'current-speed[mm/s]': focus[9],
                        ####-start-of-spindles-####
                        'spindle1-current-position[mm/deg]': focus[10],
                        'spindle1-current-target-position[mm/deg]': focus[11],
                        'spindle1-current-position-offset[mm/deg]': focus[12],
                        'spindle1-current-speed[mm/s/deg/s]': focus[13],
                        'spindle1-current-target-speed[mm/s/deg/s]': focus[14],
                        'spindle1-current-web-speed[mm/s/deg/s]': focus[15],
                        'spindle1-position-deviation[mm/deg]': focus[16],
                        'spindle1-current-utilization-of-the-spindle[%]': focus[17],
                        'spindle1-spindle-active': focus[18],
                        'spindle1-brake-open': focus[19],
                        'spindle1-general-error': focus[20],
                        # -start-of-error-structure-(5.11-in-manual)
                        'spindle1-software-emergency-stop': focus[21],
                        'spindle1-hardware-emergency-stop': focus[22],
                        'spindle1-emergency-stop-switch-up': focus[23],
                        'spindle1-emergency-limit-switch-down': focus[24],
                        'spindle1-group-error': focus[25],
                        'spindle1-brakes': focus[26],
                        'spindle1-power': focus[27],
                        'spindle1-servo-system': focus[28],
                        'spindle1-engine-timeout': focus[29],
                        'spindle1-speedometer': focus[30],
                        'spindle1-maximum-engine-speed-achieved': focus[31],
                        'spindle1-iquad_t;': focus[32],
                        'spindle1-position-encoder-hardware': focus[33],
                        'spindle1-position-encoder-step': focus[34],
                        'spindle1-position-outside-the-defined-area': focus[35],
                        'spindle1-maximum-position-deviation-reached': focus[36],
                        'spindle1-fieldbus': focus[37],
                        'spindle1-feed-back-module-servo': focus[38],
                        'spindle1-override': focus[39],
                        'spindle1-command-timeout': focus[40],
                        'spindle1-communication-error-with-host-computer': focus[
                            41],
                        'spindle1-referencescoder-is-missing': focus[42],
                        'spindle1-referencescoder-error': focus[43],
                        'spindle1-speed-governor': focus[44],
                        'spindle1-maximum-speed-deviation-achieved': focus[45],
                        'spindle1-lock': focus[46],
                        'spindle1-external-error': focus[47],
                        #  end-of-error-structure-(5.11-in-manual)
                        'spindle1-general-warning': focus[48],
                        # -start-of-warning-structure-(5.12-in-manual)
                        'spindle1-speed-mode': focus[49],
                        'spindle1_-override': focus[50],
                        'spindle1-stow-pin-in': focus[51],
                        'spindle1-parameter-error': focus[52],
                        'spindle1-power-heating': focus[53],
                        'spindle1-power-breaks': focus[54],
                        'spindle1-power-drives': focus[55],
                        'spindle1-power-external-24v': focus[56],
                        'spindle1-power-internal-24v': focus[57],
                        'spindle1-power-control': focus[58],
                        'spindle1_-position-encoder-hardware': focus[59],
                        'spindle1-engine-warning': focus[60],
                        'spindle1-mazimum-torque-achieved': focus[61],
                        'spindle1-degraded-fashion': focus[62],
                        'spindle1-security-device': focus[63],
                        'spindle1-ermaus': focus[64],
                        'spindle1-ermservo': focus[65],
                        'spindle1-emergency-limit-switch-up': focus[66],
                        'spindle1_-emergency-limit-switch-down': focus[67],
                        'spindle1-pre-limit-switch-up': focus[68],
                        'spindle1-pre-limit-switch-down': focus[69],
                        'spindle1-operating-limit-switch-up': focus[70],
                        'spindle1-operating-limit-switch-down': focus[71],
                        'spindle1-software-limit-switch-up': focus[72],
                        'spindle1-software-limit-switch-down': focus[73],
                        # -note: some-of-the-above-have-a-underscore-as-there-are
                        # -doubles-in-the-error-and-warning-stuct-with-the-same-name
                        ####
                        'spindle2-current-position[mm/deg]': focus[74],
                        'spindle2-current-target-position[mm/deg]': focus[75],
                        'spindle2-current-position-offset[mm/deg]': focus[76],
                        'spindle2-current-speed[mm/s/deg/s]': focus[77],
                        'spindle2-current-target-speed[mm/s/deg/s]': focus[78],
                        'spindle2-current-web-speed[mm/s/deg/s]': focus[79],
                        'spindle2-position-deviation[mm/deg]': focus[80],
                        'spindle2-current-utilization-of-the-spindle[%]': focus[
                            81],
                        'spindle2-spindle-active': focus[82],
                        'spindle2-brake-open': focus[83],
                        'spindle2-general-error': focus[84],
                        'spindle2-software-emergency-stop': focus[85],
                        'spindle2-hardware-emergency-stop': focus[86],
                        'spindle2-emergency-stop-switch-up': focus[87],
                        'spindle2-emergency-limit-switch-down': focus[88],
                        'spindle2-group-error': focus[89],
                        'spindle2-brakes': focus[90],
                        'spindle2-power': focus[91],
                        'spindle2-servo-system': focus[92],
                        'spindle2-engine-timeout': focus[93],
                        'spindle2-speedometer': focus[94],
                        'spindle2-maximum-engine-speed-achieved': focus[95],
                        'spindle2-iquad_t;': focus[96],
                        'spindle2-position-encoder-hardware': focus[97],
                        'spindle2-position-encoder-step': focus[98],
                        'spindle2-position-outside-the-defined-area': focus[99],
                        'spindle2-maximum-position-deviation-reached': focus[
                            100],
                        'spindle2-fieldbus': focus[101],
                        'spindle2-feed-back-module-servo': focus[102],
                        'spindle2-override': focus[103],
                        'spindle2-command-timeout': focus[104],
                        'spindle2-communication-error-with-host-computer': focus[
                            105],
                        'spindle2-referencescoder-is-missing': focus[106],
                        'spindle2-referencescoder-error': focus[107],
                        'spindle2-speed-governor': focus[108],
                        'spindle2-maximum-speed-deviation-achieved': focus[109],
                        'spindle2-lock': focus[110],
                        'spindle2-external-error': focus[111],
                        'spindle2-general-warning': focus[112],
                        'spindle2-speed-mode': focus[113],
                        'spindle2_-override': focus[114],
                        'spindle2-stow-pin-in': focus[115],
                        'spindle2-parameter-error': focus[116],
                        'spindle2-power-heating': focus[117],
                        'spindle2-power-breaks': focus[118],
                        'spindle2-power-drives': focus[119],
                        'spindle2-power-external-24v': focus[120],
                        'spindle2-power-internal-24v': focus[121],
                        'spindle2-power-control': focus[122],
                        'spindle2_-position-encoder-hardware': focus[123],
                        'spindle2-engine-warning': focus[124],
                        'spindle2-mazimum-torque-achieved': focus[125],
                        'spindle2-degraded-fashion': focus[126],
                        'spindle2-security-device': focus[127],
                        'spindle2-ermaus': focus[128],
                        'spindle2-ermservo': focus[129],
                        'spindle2-emergency-limit-switch-up': focus[130],
                        'spindle2_-emergency-limit-switch-down': focus[131],
                        'spindle2-pre-limit-switch-up': focus[132],
                        'spindle2-pre-limit-switch-down': focus[133],
                        'spindle2-operating-limit-switch-up': focus[134],
                        'spindle2-operating-limit-switch-down': focus[135],
                        'spindle2-software-limit-switch-up': focus[136],
                        'spindle2-software-limit-switch-down': focus[137],
                        'last-sent-mode-command': focus[138],
                        'command-response-of-the-mode-command': focus[139],
                        'target-position-of-the-mode-command': focus[140],
                        'target-speed-of-the-mode-command': focus[141],
                        'last-sent-parameter-command': focus[142],
                        'command-response-of-the-parameter-command': focus[143],
                        'parameter 1 of the parameter command': focus[144],
                        'parameter-2-of-the-parameter-command': focus[145],
                    },

                'status-data-active-surface':
                    {
                        'Elevation-angle[deg]': asf[0],
                        'Status-of-the-subsystem': asf[1],
                        'Warning-File-offset-table-could-not-be-read': asf[2],
                        'Collective-status-warning': asf[3],
                        'Collective-status-error': asf[4],
                        'Emergency-stop-software-active': asf[5],
                        'Emergency-stop-hardware-active': asf[6],
                        'motor-status-motor1[bit-coded]': asf[7],
                        'motor-status-motor2[bit-coded]': asf[8],
                        'motor-status-motor3[bit-coded]': asf[9],
                        'motor-status-motor4[bit-coded]': asf[10],
                        'motor-status-motor5[bit-coded]': asf[11],
                        'motor-status-motor6[bit-coded]': asf[12],
                        'motor-status-motor7[bit-coded]': asf[13],
                        'motor-status-motor8[bit-coded]': asf[14],
                        'motor-status-motor9[bit-coded]': asf[15],
                        'motor-status-motor10[bit-coded]': asf[16],
                        'motor-status-motor11[bit-coded]': asf[17],
                        'motor-status-motor12[bit-coded]': asf[18],
                        'motor-status-motor13[bit-coded]': asf[19],
                        'motor-status-motor14[bit-coded]': asf[20],
                        'motor-status-motor15[bit-coded]': asf[21],
                        'motor-status-motor16[bit-coded]': asf[22],
                        'motor-status-motor17[bit-coded]': asf[23],
                        'motor-status-motor18[bit-coded]': asf[24],
                        'motor-status-motor19[bit-coded]': asf[25],
                        'motor-status-motor20[bit-coded]': asf[26],
                        'motor-status-motor21[bit-coded]': asf[27],
                        'motor-status-motor22[bit-coded]': asf[28],
                        'motor-status-motor23[bit-coded]': asf[29],
                        'motor-status-motor24[bit-coded]': asf[30],
                        'motor-status-motor25[bit-coded]': asf[31],
                        'motor-status-motor26[bit-coded]': asf[32],
                        'motor-status-motor27[bit-coded]': asf[33],
                        'motor-status-motor28[bit-coded]': asf[34],
                        'motor-status-motor29[bit-coded]': asf[35],
                        'motor-status-motor30[bit-coded]': asf[36],
                        'motor-status-motor31[bit-coded]': asf[37],
                        'motor-status-motor32[bit-coded]': asf[38],
                        'motor-status-motor33[bit-coded]': asf[39],
                        'motor-status-motor34[bit-coded]': asf[40],
                        'motor-status-motor35[bit-coded]': asf[41],
                        'motor-status-motor36[bit-coded]': asf[42],
                        'motor-status-motor37[bit-coded]': asf[43],
                        'motor-status-motor38[bit-coded]': asf[44],
                        'motor-status-motor39[bit-coded]': asf[45],
                        'motor-status-motor40[bit-coded]': asf[46],
                        'motor-status-motor41[bit-coded]': asf[47],
                        'motor-status-motor42[bit-coded]': asf[48],
                        'motor-status-motor43[bit-coded]': asf[49],
                        'motor-status-motor44[bit-coded]': asf[50],
                        'motor-status-motor45[bit-coded]': asf[51],
                        'motor-status-motor46[bit-coded]': asf[52],
                        'motor-status-motor47[bit-coded]': asf[53],
                        'motor-status-motor48[bit-coded]': asf[54],
                        'motor-status-motor49[bit-coded]': asf[55],
                        'motor-status-motor50[bit-coded]': asf[56],
                        'motor-status-motor51[bit-coded]': asf[57],
                        'motor-status-motor52[bit-coded]': asf[58],
                        'motor-status-motor53[bit-coded]': asf[59],
                        'motor-status-motor54[bit-coded]': asf[60],
                        'motor-status-motor55[bit-coded]': asf[61],
                        'motor-status-motor56[bit-coded]': asf[62],
                        'motor-status-motor57[bit-coded]': asf[63],
                        'motor-status-motor58[bit-coded]': asf[64],
                        'motor-status-motor59[bit-coded]': asf[65],
                        'motor-status-motor60[bit-coded]': asf[66],
                        'motor-status-motor61[bit-coded]': asf[67],
                        'motor-status-motor62[bit-coded]': asf[68],
                        'motor-status-motor63[bit-coded]': asf[69],
                        'motor-status-motor64[bit-coded]': asf[70],
                        'motor-status-motor65[bit-coded]': asf[71],
                        'motor-status-motor66[bit-coded]': asf[72],
                        'motor-status-motor67[bit-coded]': asf[73],
                        'motor-status-motor68[bit-coded]': asf[74],
                        'motor-status-motor69[bit-coded]': asf[75],
                        'motor-status-motor70[bit-coded]': asf[76],
                        'motor-status-motor71[bit-coded]': asf[77],
                        'motor-status-motor72[bit-coded]': asf[78],
                        'motor-status-motor73[bit-coded]': asf[79],
                        'motor-status-motor74[bit-coded]': asf[80],
                        'motor-status-motor75[bit-coded]': asf[81],
                        'motor-status-motor76[bit-coded]': asf[82],
                        'motor-status-motor77[bit-coded]': asf[83],
                        'motor-status-motor78[bit-coded]': asf[84],
                        'motor-status-motor79[bit-coded]': asf[85],
                        'motor-status-motor80[bit-coded]': asf[86],
                        'motor-status-motor81[bit-coded]': asf[87],
                        'motor-status-motor82[bit-coded]': asf[88],
                        'motor-status-motor83[bit-coded]': asf[89],
                        'motor-status-motor84[bit-coded]': asf[90],
                        'motor-status-motor85[bit-coded]': asf[91],
                        'motor-status-motor86[bit-coded]': asf[92],
                        'motor-status-motor87[bit-coded]': asf[93],
                        'motor-status-motor88[bit-coded]': asf[94],
                        'motor-status-motor89[bit-coded]': asf[95],
                        'motor-status-motor90[bit-coded]': asf[96],
                        'motor-status-motor91[bit-coded]': asf[97],
                        'motor-status-motor92[bit-coded]': asf[98],
                        'motor-status-motor93[bit-coded]': asf[99],
                        'motor-status-motor94[bit-coded]': asf[100],
                        'motor-status-motor95[bit-coded]': asf[101],
                        'motor-status-motor96[bit-coded]': asf[102],
                        'current-position-motor1[um]': asf[103],
                        'current-position-motor2[um]': asf[104],
                        'current-position-motor3[um]': asf[105],
                        'current-position-motor4[um]': asf[106],
                        'current-position-motor5[um]': asf[107],
                        'current-position-motor6[um]': asf[108],
                        'current-position-motor7[um]': asf[109],
                        'current-position-motor8[um]': asf[110],
                        'current-position-motor9[um]': asf[111],
                        'current-position-motor10[um]': asf[112],
                        'current-position-motor11[um]': asf[113],
                        'current-position-motor12[um]': asf[114],
                        'current-position-motor13[um]': asf[115],
                        'current-position-motor14[um]': asf[116],
                        'current-position-motor15[um]': asf[117],
                        'current-position-motor16[um]': asf[118],
                        'current-position-motor17[um]': asf[119],
                        'current-position-motor18[um]': asf[120],
                        'current-position-motor19[um]': asf[121],
                        'current-position-motor20[um]': asf[122],
                        'current-position-motor21[um]': asf[123],
                        'current-position-motor22[um]': asf[124],
                        'current-position-motor23[um]': asf[125],
                        'current-position-motor24[um]': asf[126],
                        'current-position-motor25[um]': asf[127],
                        'current-position-motor26[um]': asf[128],
                        'current-position-motor27[um]': asf[129],
                        'current-position-motor28[um]': asf[130],
                        'current-position-motor29[um]': asf[131],
                        'current-position-motor30[um]': asf[132],
                        'current-position-motor31[um]': asf[133],
                        'current-position-motor32[um]': asf[134],
                        'current-position-motor33[um]': asf[135],
                        'current-position-motor34[um]': asf[136],
                        'current-position-motor35[um]': asf[137],
                        'current-position-motor36[um]': asf[138],
                        'current-position-motor37[um]': asf[139],
                        'current-position-motor38[um]': asf[140],
                        'current-position-motor39[um]': asf[141],
                        'current-position-motor40[um]': asf[142],
                        'current-position-motor41[um]': asf[143],
                        'current-position-motor42[um]': asf[144],
                        'current-position-motor43[um]': asf[145],
                        'current-position-motor44[um]': asf[146],
                        'current-position-motor45[um]': asf[147],
                        'current-position-motor46[um]': asf[148],
                        'current-position-motor47[um]': asf[149],
                        'current-position-motor48[um]': asf[150],
                        'current-position-motor49[um]': asf[151],
                        'current-position-motor50[um]': asf[152],
                        'current-position-motor51[um]': asf[153],
                        'current-position-motor52[um]': asf[154],
                        'current-position-motor53[um]': asf[155],
                        'current-position-motor54[um]': asf[156],
                        'current-position-motor55[um]': asf[157],
                        'current-position-motor56[um]': asf[158],
                        'current-position-motor57[um]': asf[159],
                        'current-position-motor58[um]': asf[160],
                        'current-position-motor59[um]': asf[161],
                        'current-position-motor60[um]': asf[162],
                        'current-position-motor61[um]': asf[163],
                        'current-position-motor62[um]': asf[164],
                        'current-position-motor63[um]': asf[165],
                        'current-position-motor64[um]': asf[166],
                        'current-position-motor65[um]': asf[167],
                        'current-position-motor66[um]': asf[168],
                        'current-position-motor67[um]': asf[169],
                        'current-position-motor68[um]': asf[170],
                        'current-position-motor69[um]': asf[171],
                        'current-position-motor70[um]': asf[172],
                        'current-position-motor71[um]': asf[173],
                        'current-position-motor72[um]': asf[174],
                        'current-position-motor73[um]': asf[175],
                        'current-position-motor74[um]': asf[176],
                        'current-position-motor75[um]': asf[177],
                        'current-position-motor76[um]': asf[178],
                        'current-position-motor77[um]': asf[179],
                        'current-position-motor78[um]': asf[180],
                        'current-position-motor79[um]': asf[181],
                        'current-position-motor80[um]': asf[182],
                        'current-position-motor81[um]': asf[183],
                        'current-position-motor82[um]': asf[184],
                        'current-position-motor83[um]': asf[185],
                        'current-position-motor84[um]': asf[186],
                        'current-position-motor85[um]': asf[187],
                        'current-position-motor86[um]': asf[188],
                        'current-position-motor87[um]': asf[189],
                        'current-position-motor88[um]': asf[190],
                        'current-position-motor89[um]': asf[191],
                        'current-position-motor90[um]': asf[192],
                        'current-position-motor91[um]': asf[193],
                        'current-position-motor92[um]': asf[194],
                        'current-position-motor93[um]': asf[195],
                        'current-position-motor94[um]': asf[196],
                        'current-position-motor95[um]': asf[197],
                        'current-position-motor96[um]': asf[198],
                        'drive-number': asf[199],
                        'profibus-address': asf[200],
                        'status-word-1': asf[201],
                        'status-word-2': asf[202],
                        'bus-error': asf[203],
                        'servo-error': asf[204],
                        'warning': asf[205],
                        'drive-active': asf[206],
                        'position-reached': asf[207],
                        'drive-ready': asf[208],
                        'current-position-of-the-drive[um]': asf[209],
                        'current-speed-of-the-drive[um-/-s]': asf[210],
                        'current-torque-of-the-drive[m-x-nm]': asf[211],
                        'current-temperature-of-the-drive[celsius]': asf[212],
                        'error-number[bit-coded]': asf[213],
                        'warning-number[bit-coded]': asf[214],
                        'position-offset-at-elevation-unknown1': asf[215],
                        'position-offset-at-elevation-unknown2': asf[216],
                        'position-offset-at-elevation-unknown3': asf[217],
                        'position-offset-at-elevation-unknown4': asf[218],
                        'position-offset-at-elevation-unknown5': asf[219],
                        'position-offset-at-elevation-unknown6': asf[220],
                        'position-offset-at-elevation-unknown7': asf[221],
                        'position-offset-at-elevation-unknown8': asf[222],
                        'position-offset-at-elevation-unknown9': asf[223],
                        'position-offset-at-elevation-unknown10': asf[224],
                        'position-offset-at-elevation-unknown11': asf[225],
                        'last-sent-mode-command': asf[226],
                        'command-response-of-the-mode-command': asf[227],
                        'target-position-of-the-mode-command': asf[228],
                        'target-speed-of-the-mode-command': asf[229],
                        'last-sent-parameter-command': asf[230],
                        'command-response-of-the-parameter-command': asf[231],
                        'parameter-1-of-the-parameter-command': asf[232],
                        'parameter-2-of-the-parameter-command': asf[233],

                    },

                'status-data-bottom-flap':
                    {
                        'are-flaps-open': bdkl[0],
                        'are-flaps-closed': bdkl[1],
                        'display of the selected motors [bit-coded]': bdkl[2],
                        'subsystem status': bdkl[3],
                        'collective-status-error': bdkl[4],
                        'flap1-flap-open': bdkl[5],
                        'flap1-flap-closed': bdkl[6],
                        'flap1-general-error': bdkl[7],
                        'flap1-voltage-error': bdkl[8],
                        'flap1-engine-error': bdkl[9],
                        'flap1-external-interlock': bdkl[10],
                        'flap1-external error (focus changer in wrong position)': bdkl[
                            11],
                        'flap1-emergency stop': bdkl[12],
                        'flap1-time-out': bdkl[13],
                        'flap1-override': bdkl[14],
                        'flap2-flap-open': bdkl[15],
                        'flap2-flap-closed': bdkl[16],
                        'engine': bdkl[17],
                        'engine1': bdkl[18],  # TODO: index error with manual
                        'flap2-general-error': bdkl[19],
                        'flap2-voltage-error': bdkl[20],
                        'flap2-engine-error': bdkl[21],
                        'flap2-external-interlock': bdkl[22],
                        'flap2-external error (focus changer in wrong position)': bdkl[
                            23],
                        'flap2-emergency stop': bdkl[24],
                        'flap2-time-out': bdkl[25],
                        'flap2-override': bdkl[26],
                        'last sent mode command': bdkl[27],
                        'command response of the mode command': bdkl[28],
                        'last sent parameter command': bdkl[29],
                        'command response of the parameter command': bdkl[30],
                        'parameter-1-of-the-parameter-command': bdkl[31],
                        'parameter-2-of-the-parameter-command': bdkl[32],
                    },

                'status-data-mirror-flap':
                    {
                        'subsystem-status': spkl[0],
                        'status': spkl[1],
                        'fold-status': spkl[2],
                        'latch-status(locking-the-flaps)': spkl[3],
                        'collision': spkl[4],
                        'collective-status-error': spkl[5],
                        'collective-status-warning': spkl[6],
                        'display-of-the-selected-motors(bit-coded)': spkl[7],
                        # Start of first mirror flap
                        'mirror-flap1-status': spkl[8],
                        'mirror-flap1-drive-active': spkl[9],
                        'mirror-flap1-software-emergency-stop': spkl[10],
                        'mirror-flap1-hardware-emergency-stop': spkl[11],
                        'mirror-flap1-emergency-stop-switch-up': spkl[12],
                        'mirror-flap1-emergency-limit-switch-down': spkl[13],
                        'mirror-flap1-group-error': spkl[14],
                        'mirror-flap1-brakes': spkl[15],
                        'mirror-flap1-power': spkl[16],
                        'mirror-flap1-servo-system': spkl[17],
                        'mirror-flap1-engine-timeout': spkl[18],
                        'mirror-flap1-speedometer': spkl[19],
                        'mirror-flap1-maximum-engine-speed-achieved': spkl[20],
                        'mirror-flap1-iquad_t;': spkl[21],
                        'mirror-flap1-position-encoder-hardware': spkl[22],
                        'mirror-flap1-position-encoder-step': spkl[23],
                        'mirror-flap1-position-outside-the-defined-area': spkl[24],
                        'mirror-flap1-maximum-position-deviation-reached': spkl[25],
                        'mirror-flap1-fieldbus': spkl[26],
                        'mirror-flap1-feed-back-module-servo': spkl[27],
                        'mirror-flap1-override(error-struct)': spkl[28],
                        'mirror-flap1-command-timeout': spkl[29],
                        'mirror-flap1-communication-error-with-host-computer': spkl[30],
                        'mirror-flap1-referencescoder-is-missing': spkl[31],
                        'mirror-flap1-referencescoder-error': spkl[32],
                        'mirror-flap1-speed-governor': spkl[33],
                        'mirror-flap1-maximum-speed-deviation-achieved': spkl[34],
                        'mirror-flap1-lock': spkl[35],
                        'mirror-flap1-external-error': spkl[36],
                        'mirror-flap1-override': spkl[37],
                        'mirror-flap1-zero-speed': spkl[38],
                        'mirror-flap1-current-positoin[mm]': spkl[39],
                        'mirror-flap1-current-speed[mm/s]': spkl[40],
                        'mirror-flap1-current-itilization-of-the-spindle[%]': spkl[41],
                        # end of first mirror flap, start of second
                        'mirror-flap2-status': spkl[42],
                        'mirror-flap2-drive-active': spkl[43],
                        'mirror-flap2-software-emergency-stop': spkl[44],
                        'mirror-flap2-hardware-emergency-stop': spkl[45],
                        'mirror-flap2-emergency-stop-switch-up': spkl[46],
                        'mirror-flap2-emergency-limit-switch-down': spkl[47],
                        'mirror-flap2-group-error': spkl[48],
                        'mirror-flap2-brakes': spkl[49],
                        'mirror-flap2-power': spkl[50],
                        'mirror-flap2-servo-system': spkl[51],
                        'mirror-flap2-engine-timeout': spkl[52],
                        'mirror-flap2-speedometer': spkl[53],
                        'mirror-flap2-maximum-engine-speed-achieved': spkl[54],
                        'mirror-flap2-iquad_t;': spkl[55],
                        'mirror-flap2-position-encoder-hardware': spkl[56],
                        'mirror-flap2-position-encoder-step': spkl[57],
                        'mirror-flap2-position-outside-the-defined-area': spkl[58],
                        'mirror-flap2-maximum-position-deviation-reached': spkl[59],
                        'mirror-flap2-fieldbus': spkl[60],
                        'mirror-flap2-feed-back-module-servo': spkl[61],
                        'mirror-flap2-override(error-struct)': spkl[62],
                        'mirror-flap2-command-timeout': spkl[63],
                        'mirror-flap2-communication-error-with-host-computer': spkl[64],
                        'mirror-flap2-referencescoder-is-missing': spkl[65],
                        'mirror-flap2-referencescoder-error': spkl[66],
                        'mirror-flap2-speed-governor': spkl[67],
                        'mirror-flap2-maximum-speed-deviation-achieved': spkl[68],
                        'mirror-flap2-lock': spkl[69],
                        'mirror-flap2-external-error': spkl[70],
                        'mirror-flap2-override': spkl[71],
                        'mirror-flap2-zero-speed': spkl[72],
                        'mirror-flap2-current-positoin[mm]': spkl[73],
                        'mirror-flap2-current-speed[mm/s]': spkl[74],
                        'mirror-flap2-current-itilization-of-the-spindle[%]': spkl[75],
                        # end of second mirror flap
                        'last-sent-mode-command': spkl[76],
                        'command-response-pf-the-mode-command': spkl[77],
                        'last-sent-parameter-command': spkl[78],
                        'last-response-of-the-parameter-command': spkl[79],
                        'parameter1-of-the-parameter-command': spkl[80],
                        'parameter2-of-the-parameter-command': spkl[81],
                    },

                'status-data-temperature':
                    {
                        'actual-temperature-sensor-hexapod-spindle1': temp[0],
                        'actual-temperature-sensor-hexapod-spindle2': temp[1],
                        'actual-temperature-sensor-hexapod-spindle3': temp[2],
                        'actual-temperature-sensor-hexapod-spindle4': temp[3],
                        'actual-temperature-sensor-hexapod-spindle5': temp[4],
                        'actual-temperature-sensor-hexapod-spindle6': temp[5],
                        'actual-temperature-sensor-structure1': temp[6],
                        'actual-temperature-sensor-structure2': temp[7],
                        'actual-temperature-sensor-structure3': temp[8],
                        'actual-temperature-sensor-structure4': temp[9],
                        'error-sensor-hexapod-spindle1': temp[10],
                        'error-sensor-hexapod-spindle2': temp[11],
                        'error-sensor-hexapod-spindle3': temp[12],
                        'error-sensor-hexapod-spindle4': temp[13],
                        'error-sensor-hexapod-spindle5': temp[14],
                        'error-sensor-hexapod-spindle6': temp[15],
                        'error-seonsor-hexapod-structure1': temp[16],
                        'error-seonsor-hexapod-structure2': temp[17],
                        'error-seonsor-hexapod-structure3': temp[18],
                        'error-seonsor-hexapod-structure4': temp[19],
                    },

                'status-data-irig-b-system':
                    {
                        'current-time-as-modified-julian-day(mjd)': foctime[0],
                        'current-time-offset[s]': foctime[1],
                        'source-of-the-absoulute-time': foctime[2],
                        'source-of-the-irig-b-signal': foctime[3],
                        'status-of-communication-with-irig-b-system': foctime[4],
                        'curent-internal-acu-time-in-mjd': foctime[5],
                        'current-irig-b-time-in-mjd': foctime[6],
                        'time-currently-set-by-remote-host-in-mjd': foctime[7],
                        'last-sent-parameter-command': foctime[8],
                        'command-response-of-the-parameter-command': foctime[9],
                        'parameter1-of-the-parameter-command': foctime[10],
                        'parameter2-of-the-parameter-command': foctime[11],

                    },

                'end-flag': last[2]
                # TODO: last has 3 values, but maunal only shows one

            }

            return status_message

    @staticmethod
    def decode_struct(data):
        """
        Decodes, organizes, and returns a given bytes string to it's respective
        pieces.
        :param data: bytes string of len 1760.
        :return: tuple of tuples - Each with int/float entries
        """
        header = struct.unpack("=LiiH", data[:14])
        il = struct.unpack("=15BHB2H2H2f", data[14:48])
        power = struct.unpack("=5B", data[48:53])
        polar = struct.unpack("=2H2B27B25B8fH4f9BHBH6B4f9BHBH6B2H2f2H2f",
                              data[53:241])
        hxpd = struct.unpack("=H6f2b22b2iH8f3B27BB25B8f3B27BB25B8f3B27BB"
                             "25B8f3B27BB25B8f3B27BB25B8f3B27BB25B4H4f2H"
                             "4f2H2f", data[241:885])
        focus = struct.unpack("=H5BH3f8f3B27BB25B8f3B27BB25B2H2f2H2f",
                              data[885:1106])
        asf = struct.unpack("=dI5B96B96h2H2H6Bh3f2H11h2H2f2H2f",
                            data[1106:1489])
        bdkl = struct.unpack("=2BHHB10B10B2H2f2H2f", data[1489:1540])
        spkl = struct.unpack("=BH5BH2B27B2B3f2B27B2B3f2H2H2f",
                             data[1540:1652])
        temp = struct.unpack("=10f10B", data[1652:1702])
        foctime = struct.unpack("=diH2B3d2H2f", data[1702:1754])
        last = struct.unpack("=2BI", data[1754:1760])

        return header, il, power, polar, hxpd, focus, \
               asf, bdkl, spkl, temp, foctime, last

if __name__ == '__main__':
    logging.basicConfig(
        filename='debug/subreflector_client_debug.log', filemode='w',
        level=logging.DEBUG, format='%(asctime)s - %(levelname)s- %(message)s',
        datefmt='%d-%b-%y %H:%M:%S')

    SubreflectorClient(use_test_server=True).main()
