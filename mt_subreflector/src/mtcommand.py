#!/usr/bin/env python
import socket
import ctypes
import logging
import datetime

SR_ADDR = '***REMOVED***'
SR_PORT = ***REMOVED***
BUFFER_SIZE = ***REMOVED***


class MTCommand:
    def __init__(self, use_test_server):
        # Initializes the socket to the Subreflector
        self.structure = None
        self.msg = None
        self.startflag = 0x1DFCCF1A
        self.endflag = 0xA1FCCFD1
        self.seconds = 10001  # initial value, overwritten by structure methods
        self.servertype = use_test_server

    def setup_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect(self.use_test_server(self.servertype))
        except ConnectionError:
            logging.exception("Error connecting to command port on SR")

    def use_test_server(self, test_server):
        """
        Swaps real SR address for local if instance of class is needed for tests
        :param flag: bool
            if flag set to true, the address for the test server is used instead
        :return: IP address and port for the respective subreflector
        """
        # TODO Fails to connect as port ***REMOVED*** not active on mock_subreflector.py
        if test_server:
            msg = "Connected to local subreflector in MockSubreflector.py"
            logging.debug(msg)
            return '', SR_PORT

        else:
            msg = f"Connected to mt_subreflector. IP: {SR_ADDR} - " \
                  f"Port: {SR_PORT}"
            logging.debug(msg)
            return SR_ADDR, SR_PORT

    def send_command(self, command):
        # Sends the given command though the socket to the Subreflector
        try:
            logging.debug(f"Sending packaged_ctype to Subreflector at "
                          f"address: {self.sock.getsockname()[0]}, "
                          f"port: {self.sock.getsockname()[1]}.")
            self.sock.send(command)
        except ConnectionError or BrokenPipeError as E:
            self.msg = f"There was a socket error: {E}"

        # else:
        #     print(self.unpack())


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

    def interlock_command_to_struct(self, command):

        # Correct class structure for given command
        class InterlockStructure(ctypes.Structure):
            _pack_ = 1
            _fields_ = [("start_flag", ctypes.c_uint32),
                        ("message_length", ctypes.c_int32),
                        ("command_serial_number", ctypes.c_int32),
                        ("command", ctypes.c_int16),
                        ("mode", ctypes.c_int16),
                        ("elevation", ctypes.c_double),
                        ("reserved", ctypes.c_double),
                        ("end_flag", ctypes.c_uint32)]

        size_of_struct = ctypes.sizeof(InterlockStructure())

        cmd_il, mode, elevation, reserve = command
        # self.seconds = 12345  # Temporary to have identical stamps to compare
        self.structure = InterlockStructure(
            self.startflag, size_of_struct, self.seconds, 
            cmd_il, mode, elevation, reserve, self.endflag)

    def asf_command_to_struct(self, command):
       
        # Correct class structure for given command
        class AsfStructure(ctypes.Structure):
            _pack_ = 1
            _fields_ = [("start_flag", ctypes.c_uint32),
                        ("message_length", ctypes.c_int32),
                        ("command_serial_number", ctypes.c_int32),
                        ("command", ctypes.c_int16),
                        ("mode", ctypes.c_int16),
                        ("offset_dr_nr", ctypes.c_int16),
                        ("offset_active", ctypes.c_uint16),
                        ("offset_value1", ctypes.c_int16),
                        ("offset_value2", ctypes.c_int16),
                        ("offset_value3", ctypes.c_int16),
                        ("offset_value4", ctypes.c_int16),
                        ("offset_value5", ctypes.c_int16),
                        ("offset_value6", ctypes.c_int16),
                        ("offset_value7", ctypes.c_int16),
                        ("offset_value8", ctypes.c_int16),
                        ("offset_value9", ctypes.c_int16),
                        ("offset_value10", ctypes.c_int16),
                        ("offset_value11", ctypes.c_int16),
                        ("end_flag", ctypes.c_uint32)]

        size_of_struct = ctypes.sizeof(AsfStructure())

        cmd_as, mode, offset_dr_nr, offset_active, offset_value1, \
            offset_value2, offset_value3, offset_value4, offset_value5, \
            offset_value6, offset_value7, offset_value8, offset_value9, \
            offset_value10, offset_value11 = command

        # self.seconds = 12345  # Temporary to have identical stamps to compare
        self.structure = AsfStructure(
            self.startflag,
            size_of_struct, self.seconds, cmd_as, mode, offset_dr_nr,
            offset_active, offset_value1, offset_value2, offset_value3,
            offset_value4, offset_value5, offset_value6, offset_value7,
            offset_value8, offset_value9, offset_value10, offset_value11,
            self.endflag)

    def hxpd_command_to_struct(self, command):

        # Correct class structure for given command
        class HexapodStructure(ctypes.Structure):
            _pack_ = 1
            _fields_ = [("start_flag", ctypes.c_uint32),
                        ("message_length", ctypes.c_int32),
                        ("command_serial_number", ctypes.c_int32),
                        ("command", ctypes.c_int16),
                        ("fashion", ctypes.c_int16),
                        ("mode_lin", ctypes.c_int16),
                        ("anzahl_lin", ctypes.c_uint16),
                        ("phase_lin", ctypes.c_double),
                        ("p_xlin", ctypes.c_double),
                        ("p_ylin", ctypes.c_double),
                        ("p_zlin", ctypes.c_double),
                        ("v_lin", ctypes.c_double),
                        ("mode_rot", ctypes.c_int16),
                        ("anzahl_rot", ctypes.c_uint16),
                        ("phase_rot", ctypes.c_double),
                        ("p_xrot", ctypes.c_double),
                        ("p_yrot", ctypes.c_double),
                        ("p_zrot", ctypes.c_double),
                        ("v_rot", ctypes.c_double),
                        ("end_flag", ctypes.c_uint32)]  # DWORD

        size_of_struct = ctypes.sizeof(HexapodStructure())

        cmd_hxpd, fashion, mode_lin, anzahl_lin, phase_lin, \
            p_xlin, p_ylin, p_zlin, v_lin, mode_rot, anzahl_rot, phase_rot, \
            p_xrot, p_yrot, p_zrot, v_rot, = command

        self.structure = HexapodStructure(
            self.startflag, size_of_struct, self.seconds, cmd_hxpd, fashion,
            mode_lin, anzahl_lin, phase_lin, p_xlin, p_ylin, p_zlin, v_lin,
            mode_rot, anzahl_rot, phase_rot, p_xrot, p_yrot, p_zrot, v_rot,
            self.endflag)

    def polar_command_to_struct(self, command):

        # Correct class structure for given command
        class PolarStructure(ctypes.Structure):
            _pack_ = 1
            _fields_ = [("start_flag", ctypes.c_uint32),
                        ("message_length", ctypes.c_int32),
                        ("command_serial_number", ctypes.c_int32),
                        ("command", ctypes.c_int16),
                        ("mode", ctypes.c_int16),
                        ("p_soll", ctypes.c_double),
                        ("v_cmd", ctypes.c_double),
                        ("end_flag", ctypes.c_uint32)]

        size_of_struct = ctypes.sizeof(PolarStructure())

        cmd_polar, fashion, p_soll, v_cmd = command
        # self.seconds = 12345  # Temporary to have identical stamps to compare
        self.structure = PolarStructure(
            self.startflag, size_of_struct, self.seconds,
            cmd_polar, fashion, p_soll, v_cmd, self.endflag)

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

        self.structure = None  # In case already set

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
            packaged_ctype = self.pack(self.structure)
            print('\n', packaged_ctype)
        except AssertionError as E:
            logging.exception("Structure was not set by relevant"
                              " command_to_struct method, nothing to package")
            print(E)
        else:
            self.send_command(packaged_ctype)

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

    def preset_abs_lin_hxpd(self, xlin, ylin, zlin, v_lin):
        try:
            assert -225 <= xlin <= 225
            assert -175 <= ylin <= 175
            assert -195 <= zlin <= 45
            assert 0.001 <= v_lin <= 10

        except AssertionError as E:
            logging.exception("Paramater(s) out of range")
            print(f"Assertion Error: {E}")
        else:
            cmd_hxpd = 101
            fashion = 2
            mode_lin = 3
            mode_rot = 0
            anzahl_lin, phase_lin, anzahl_rot, phase_rot = 0, 0, 0, 0

            data = (cmd_hxpd, fashion,
                    mode_lin, anzahl_lin, phase_lin, xlin, ylin, zlin, v_lin,
                    mode_rot, anzahl_rot, phase_rot, 0, 0, 0, 0)

            self.encapsulate_command("hxpd", data)

    def preset_abs_rot_hxpd(self, xrot, yrot, zrot, v_rot):
        try:
            assert -0.95 <= xrot <= 0.95
            assert -0.95 <= yrot <= 0.95
            assert -0.95 <= zrot <= 0.95
            assert 0.000_01 <= v_rot <= 0.1


        except AssertionError as E:
            logging.exception("Paramater(s) out of range")
            print(f"Assertion Error: {E}")
        else:
            cmd_hxpd = 101
            fashion = 2
            mode_lin = 0
            mode_rot = 3
            anzahl_lin, phase_lin, anzahl_rot, phase_rot = 0, 0, 0, 0

            data = (cmd_hxpd, fashion,
                    mode_lin, anzahl_lin, phase_lin, 0, 0, 0, 0,
                    mode_rot, anzahl_rot, phase_rot, xrot, yrot, zrot,
                    v_rot)

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
            fashion = 4

            data = (cmd_polar, fashion, p_soll, v_cmd)
            self.encapsulate_command("polar", data)

    def preset_rel_polar(self, p_soll, v_cmd):
        # Todo do same as hexapod and only have absolute
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
    
    # # # # # # # # # # # # # # # #
    def irig_b_system(self, fashion_value, time_offset_mode=3):
        try:
            assert time_offset_mode == 3 or time_offset_mode == 4
        except Exception as E:
            print(E)
            print("Error, time_offset_mode (second entry) should be 3 or 4")
        else:
            cmd_time = 107
            fashion = fashion_value
            time_offset = time_offset_mode
            reserve = 0.0
            data = (cmd_time, fashion, time_offset, reserve)
            self.encapsulate_command('unknown', data)

    def close(self):
        self.sock.close()
