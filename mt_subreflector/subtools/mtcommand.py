#!/usr/bin/env python
import socket
import ctypes
import logging
import datetime

from . import config, process_message


class MTCommand:
    def __init__(self, is_test_server):
        # Initializes the socket to the Subreflector
        self.structure = None
        self.mt_command_status = None
        self.startflag = 0x1DFCCF1A
        self.endflag = 0xA1FCCFD1
        self.seconds = 10001  # initial value, overwritten by structure methods
        self.servertype = None
        self.get_server_address(is_test_server)

    def start_mtcommand(self):

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.connect(self.servertype)

        except ConnectionError:
            logging.exception("Error connecting to command port on SR")

    def get_server_address(self, test_server):
        """
        Swaps real SR address for local if instance of class is needed for tests
        :param flag: bool
            if flag set to true, the address for the test server is used instead
        :return: IP address and port for the respective subreflector
        """

        if test_server:
            msg = "Connected to local subreflector in MockSubreflector.py"
            logging.debug(msg)
            self.servertype = '', config.SR_WRITE_PORT

        else:
            msg = f"Connected to mt_subreflector. IP: {config.SR_IP} - " \
                  f"Port: {config.SR_WRITE_PORT}"
            logging.debug(msg)
            self.servertype = config.SR_IP, config.SR_WRITE_PORT

    def send_command(self, packaged_msg):
        """
        receives a bytes string that is a *structured, packed, and encoded* msg
        self.msg is set so it can be parsed in the UDPCommandParser class
        :param command: bytes string
        :return: N/A
        """
        # Sends the given command though the socket to the Subreflector
        try:
            logging.debug(f"Sending packaged_ctype to Subreflector at "
                          f"address: {self.servertype[0]}, "
                          f"port: {self.servertype[1]}.")

            self.sock.send(packaged_msg)
            self.mt_command_status = "sent successfully"
        except ConnectionError or BrokenPipeError as E:
            self.mt_command_status = f"There was a socket error: {E}"

    def interlock_command_to_struct(self, command):

        size_of_struct = ctypes.sizeof(process_message.InterlockStructure())

        cmd_il, mode, elevation, reserve = command
        self.structure = process_message.InterlockStructure(
            self.startflag, size_of_struct, self.seconds, 
            cmd_il, mode, elevation, reserve, self.endflag)

    def asf_command_to_struct(self, command):

        size_of_struct = ctypes.sizeof(process_message.AsfStructure())

        cmd_as, mode, offset_dr_nr, offset_active, offset_value1, \
            offset_value2, offset_value3, offset_value4, offset_value5, \
            offset_value6, offset_value7, offset_value8, offset_value9, \
            offset_value10, offset_value11 = command

        self.structure = process_message.AsfStructure(
            self.startflag,
            size_of_struct, self.seconds, cmd_as, mode, offset_dr_nr,
            offset_active, offset_value1, offset_value2, offset_value3,
            offset_value4, offset_value5, offset_value6, offset_value7,
            offset_value8, offset_value9, offset_value10, offset_value11,
            self.endflag)

    def hxpd_command_to_struct(self, command):

        size_of_struct = ctypes.sizeof(process_message.HexapodStructure())

        cmd_hxpd, fashion, mode_lin, anzahl_lin, phase_lin, \
            p_xlin, p_ylin, p_zlin, v_lin, mode_rot, anzahl_rot, phase_rot, \
            p_xrot, p_yrot, p_zrot, v_rot, = command

        self.structure = process_message.HexapodStructure(
            self.startflag, size_of_struct, self.seconds, cmd_hxpd, fashion,
            mode_lin, anzahl_lin, phase_lin, p_xlin, p_ylin, p_zlin, v_lin,
            mode_rot, anzahl_rot, phase_rot, p_xrot, p_yrot, p_zrot, v_rot,
            self.endflag)

    def polar_command_to_struct(self, command):

        size_of_struct = ctypes.sizeof(process_message.PolarStructure())

        cmd_polar, fashion, p_soll, v_cmd = command
        self.structure = process_message.PolarStructure(
            self.startflag, size_of_struct, self.seconds,
            cmd_polar, fashion, p_soll, v_cmd, self.endflag)

    @staticmethod
    def pack(ctype_instance):
        """
        Takes a ctype structure (created by a "..._to_struct" method, and
        packs it into a byte string so it can be sent via a socket
        :param ctype_instance: instance of a ctypes structure
        :return: byte string
        """
        buf = ctypes.string_at(ctypes.byref(ctype_instance),
                               ctypes.sizeof(ctype_instance))
        return buf

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

    def encapsulate_command(self, type_of_command, command_msg):
        """
        encapsulate_command takes in the parameter command_msg, and finds the
        method that has the correct ctypes structure to deal with a command of
        that length/type. It passes command_msg to that method to create an
        instance of the structure, saved in self.structure. This is what is
        then packed and sent through the socket.

        :param type_of_command: str indicating which ctype struct to use
        :param command_msg: Tuple (varying length)
        :return: None, but calls to send message to subreflector via socket
        """

        self.mt_command_status = None# In case already set. Note: exceptions below in methods
        # that set self.msg won't reach this so msg isn't lost
        self.structure = None

        # Creates a unique timestamp to differentiate messages
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.seconds = (now - midnight).seconds  # a unique int of length five

        # Parse the command to the correct method/structure
        if type_of_command.lower() == "interlock":
            self.interlock_command_to_struct(command_msg)
        elif type_of_command.lower() == "asf":
            self.asf_command_to_struct(command_msg) 
        elif type_of_command.lower() == 'hxpd':
            self.hxpd_command_to_struct(command_msg) 
        elif type_of_command.lower() == 'polar':
            self.polar_command_to_struct(command_msg)
            # print("MUST MAKE METHOD AND CTYPES CLASS FOR THIS CASE")  # TODO
        else:
            print("Unknown command type") # should be unreachable

        try:
            assert self.structure is not None # Should be changed from above code
            logging.debug("Packing structure to bytes")
            bytes_ctype = self.pack(self.structure)

        except AssertionError as E:
            logging.exception("Structure was not set by relevant"
                              " command_to_struct method, nothing to package")
            print(E)

        else:
            self.send_command(bytes_ctype)

    # # # # # 4.2 Interlock command # # # # #
    def set_mt_elevation(self, elevation):
        cmd_il = 106
        mode = 2000
        reserve = 0.0
        data = (cmd_il, mode, elevation, reserve)
        self.encapsulate_command("interlock", data)

    def activate_mt(self):
        cmd_il = 106
        mode = 2
        elevation = 0.0
        reserve = 0.0
        data = (cmd_il, mode, elevation, reserve)
        self.encapsulate_command("interlock", data)

    def deactivate_mt(self):
        cmd_il = 106
        mode = 1
        elevation = 0.0
        reserve = 0.0
        data = (cmd_il, mode, elevation, reserve)
        self.encapsulate_command("interlock", data)

    # # # # # 4.3 Active Surface command # # # # #


    def ignore_asf(self):
        cmd_as = 100
        mode = 0
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0
        data = (cmd_as, mode, offset_dr_nr, offset_active,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.encapsulate_command("asf", data)

    def deactivate_asf(self):
        cmd_as = 100
        mode = 1
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0
        data = (cmd_as, mode, offset_dr_nr, offset_active,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.encapsulate_command("asf", data)

    def rest_pos_asf(self):
        cmd_as = 100
        mode = 6
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0
        data = (cmd_as, mode, offset_dr_nr, offset_active,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.encapsulate_command("asf", data)

    def stop_asf(self):
        cmd_as = 100
        mode = 7
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0
        data = (cmd_as, mode, offset_dr_nr, offset_active,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.encapsulate_command("asf", data)

    def preset_pos_asf(self):
        cmd_as = 100
        mode = 23
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0

        data = (cmd_as, mode, offset_dr_nr, offset_active,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.encapsulate_command("asf", data)

    def acknowledge_error_on_asf(self):
        cmd_as = 100
        mode = 15
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0

        data = (cmd_as, mode, offset_dr_nr, offset_active,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.encapsulate_command("asf", data)

    def set_automatic_asf(self):
        cmd_as = 100
        mode = 42
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0
        data = (cmd_as, mode, offset_dr_nr, offset_active,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.encapsulate_command("asf", data)

    def set_offset_asf(self):
        cmd_as = 100
        mode = 44
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0
        data = (cmd_as, mode, offset_dr_nr, offset_active,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.encapsulate_command("asf", data)


    # # # # # 4.4 Subreflector positioning instruction set # # # # #
    def deactivate_hxpd(self):
        cmd_hxpd = 101
        fashion = 1
        mode_lin = 0
        xlin, ylin, zlin, v_lin = 0, 0, 0, 0
        mode_rot = 0
        xrot, yrot, zrot, v_rot = 0, 0, 0, 0
        anzahl_lin, phase_lin, anzahl_rot, phase_rot = 0, 0, 0, 0

        data = (cmd_hxpd, fashion,
                mode_lin, anzahl_lin, phase_lin, xlin, ylin, zlin, v_lin,
                mode_rot, anzahl_rot, phase_rot, xrot, yrot, zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def activate_hxpd(self):
        cmd_hxpd = 101
        fashion = 2
        mode_lin = 0
        xlin, ylin, zlin, v_lin = 0, 0, 0, 0
        mode_rot = 0
        xrot, yrot, zrot, v_rot = 0, 0, 0, 0
        anzahl_lin, phase_lin, anzahl_rot, phase_rot = 0, 0, 0, 0

        data = (cmd_hxpd, fashion,
                mode_lin, anzahl_lin, phase_lin, xlin, ylin, zlin, v_lin,
                mode_rot, anzahl_rot, phase_rot, xrot, yrot, zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def stop_hxpd(self):
        cmd_hxpd = 101
        fashion = 7
        mode_lin = 0
        xlin, ylin, zlin, v_lin = 0, 0, 0, 0
        mode_rot = 0
        xrot, yrot, zrot, v_rot = 0, 0, 0, 0
        anzahl_lin, phase_lin, anzahl_rot, phase_rot = 0, 0, 0, 0

        data = (cmd_hxpd, fashion,
                mode_lin, anzahl_lin, phase_lin, xlin, ylin, zlin, v_lin,
                mode_rot, anzahl_rot, phase_rot, xrot, yrot, zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def interlock_hxpd(self):
        cmd_hxpd = 101
        fashion = 14
        mode_lin = 0
        xlin, ylin, zlin, v_lin = 0, 0, 0, 0
        mode_rot = 0
        xrot, yrot, zrot, v_rot = 0, 0, 0, 0
        anzahl_lin, phase_lin, anzahl_rot, phase_rot = 0, 0, 0, 0

        data = (cmd_hxpd, fashion,
                mode_lin, anzahl_lin, phase_lin, xlin, ylin, zlin, v_lin,
                mode_rot, anzahl_rot, phase_rot, xrot, yrot, zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def acknowledge_error_on_hxpd(self):
        cmd_hxpd = 101
        fashion = 15
        mode_lin = 0
        xlin, ylin, zlin, v_lin = 0, 0, 0, 0
        mode_rot = 0
        xrot, yrot, zrot, v_rot = 0, 0, 0, 0
        anzahl_lin, phase_lin, anzahl_rot, phase_rot = 0, 0, 0, 0

        data = (cmd_hxpd, fashion,
                mode_lin, anzahl_lin, phase_lin, xlin, ylin, zlin, v_lin,
                mode_rot, anzahl_rot, phase_rot, xrot, yrot, zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def preset_abs_hxpd(self, xlin, ylin, zlin, vlin,
                            xrot, yrot, zrot, vrot):
        try:
            assert -225 <= xlin <= 225
            assert -175 <= ylin <= 175
            assert -195 <= zlin <= 45
            assert 0.001 <= vlin <= 10
            assert -0.95 <= xrot <= 0.95
            assert -0.95 <= yrot <= 0.95
            assert -0.95 <= zrot <= 0.95
            assert 0.000_01 <= vrot <= 0.1

        except AssertionError:
            logging.exception("Paramater(s) out of range")
            self.mt_command_status = f"Assertion error, parameters out of range. See manual"
        else:
            cmd_hxpd = 101
            fashion = 2
            mode_lin = 3
            mode_rot = 3
            anzahl_lin, phase_lin, anzahl_rot, phase_rot = 0, 0, 0, 0

            data = (cmd_hxpd, fashion,
                    mode_lin, anzahl_lin, phase_lin, xlin, ylin, zlin, vlin,
                    mode_rot, anzahl_rot, phase_rot, xrot, yrot, zrot, vrot)

            self.encapsulate_command("hxpd", data)


    # # # # # Polarization Drive # # # # #
    # TODO: Track_El needs to be added to polar, in docs. but what is it for ?
    def ignore_polar(self):
        cmd_polar = 102
        fashion = 0
        p_soll = 0
        v_cmd = 0
        data = (cmd_polar, fashion, p_soll, v_cmd)
        self.encapsulate_command("polar", data)

    def activate_polar(self):
        cmd_polar = 102
        fashion = 2
        p_soll = 0
        v_cmd = 0
        data = (cmd_polar, fashion, p_soll, v_cmd)
        self.encapsulate_command("polar", data)

    def deactivate_polar(self):
        cmd_polar = 102
        fashion = 1
        p_soll = 0
        v_cmd = 0
        data = (cmd_polar, fashion, p_soll, v_cmd)
        self.encapsulate_command("polar", data)

    def stop_polar(self):
        cmd_polar = 102
        fashion = 7
        p_soll = 0
        v_cmd = 0
        data = (cmd_polar, fashion, p_soll, v_cmd)
        self.encapsulate_command("polar", data)

    def acknowledge_error_on_polar(self):
        cmd_polar = 102
        fashion = 15
        p_soll = 0
        v_cmd = 0
        data = (cmd_polar, fashion, p_soll, v_cmd)
        self.encapsulate_command("polar", data)

    def preset_abs_polar(self, p_soll, v_cmd):
        try:
            assert 195 >= p_soll >= -195
            assert 3 >= v_cmd >= 0.000_01

        except AssertionError:
            logging.exception("parametrs for polar outside limits")

        else:
            cmd_polar = 102
            fashion = 3

            data = (cmd_polar, fashion, p_soll, v_cmd)
            self.encapsulate_command("polar", data)

    def preset_rel_polar(self, p_soll, v_cmd):
        # Todo do same as hexapod and only have absolute
        # Todo make check so relative
        try:
            assert 195 >= p_soll >= -195
            assert 3 >= v_cmd >= 0.000_01

        except AssertionError:
            logging.exception("parametrs for polar outside limits")

        else:
            cmd_polar = 102
            fashion = 4

            data = (cmd_polar, fashion, p_soll, v_cmd)
            self.encapsulate_command("polar", data)
    
    # # # # # Rest of the commands # # # # #
    """ 
    After discussions, the rest of the commands were decided to be left out.
    But they can easily be added here, and so long as you make a proper method
    to structure the command type following an example above like 
    interlock_command_to_struct, and add the new type as a elif line in 
    self.encapsulate_command section, any additions should be straight forward.
    """

    def irig_b_system(self, fashion_value, time_offset_mode=3):
        try:
            assert time_offset_mode == 3 or time_offset_mode == 4
        except Exception as E:
            print(E)
            self.mt_command_status = "Error, time_offset_mode should be 3 or 4"
        else:
            cmd_time = 107
            fashion = fashion_value
            time_offset = time_offset_mode
            reserve = 0.0
            data = (cmd_time, fashion, time_offset, reserve)
            self.encapsulate_command('unknown', data)

    #
    def close(self):
        self.sock.close()

if __name__ == '__main__':
    MTCommand().start_mtcommand()
