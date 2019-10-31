#!/usr/bin/env python
import socket
import datetime
import ctypes
import logging

TCP_IP = '***REMOVED***'
TCP_PORT = ***REMOVED***
BUFFER_SIZE = ***REMOVED***

# logging.basicConfig(filename='debug/subreflector_program_debug.log',
#                     filemode='w', level=logging.DEBUG,
#                     format='%(asctime)s - %(levelname)s - %(module)s '
#                            '- %(funcName)s- %(message)s',
#                     datefmt='%d-%b-%y %H:%M:%S')


class MTCommand:
    def __init__(self):
        # Initializes the socket to the Subreflector
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((TCP_IP, TCP_PORT))
        self.structure = None
        self.startflag = 0x1DFCCF1A
        self.endflag = 0xA1FCCFD1
        self.seconds = 10001

    def send_command(self, command):
        # Sends the given command though the socket to the Subreflector
        self.sock.send(command)

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
    '''
    Defined in page 6 and 7 in EFB_SPE documentation 
    '''

    def interlock_command_to_struct(self, command):

        # Correct class structure for given command
        class InterlockStructure(ctypes.Structure):
            _fields_ = [("start_flag", ctypes.c_uint32),
                        ("message_length", ctypes.c_int32),
                        ("command_serial_number", ctypes.c_int32),
                        ("command", ctypes.c_int32),
                        ("mode", ctypes.c_int16),
                        ("elevation", ctypes.c_double),
                        ("reserved", ctypes.c_double),
                        ("end_flag", ctypes.c_uint32)]

        size_of_struct = ctypes.sizeof(InterlockStructure())
        print(size_of_struct)  # To see the size in output, as it changes often
        cmd_il, mode, elevation, reserve = command
        self.seconds = 12345  # Temporary to have identical stamps to compare
        self.structure = InterlockStructure(
            self.startflag, size_of_struct, self.seconds, 
            cmd_il, mode, elevation, reserve, self.endflag)

    def asf_command_to_struct(self, command):
       
        # Correct class structure for given command
        class AsfStructure(ctypes.Structure):
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
        print(size_of_struct)  # To see the size in output, as it changes often

        cmd_as, mode, offset_dr_nr, offset_active, offset_value1, \
            offset_value2, offset_value3, offset_value4, offset_value5, \
            offset_value6, offset_value7, offset_value8, offset_value9, \
            offset_value10, offset_value11 = command

        self.seconds = 12345  # Temporary to have identical stamps to compare
        self.structure = AsfStructure(
            self.startflag,
            size_of_struct, self.seconds, cmd_as, mode, offset_dr_nr,
            offset_active, offset_value1, offset_value2, offset_value3,
            offset_value4, offset_value5, offset_value6, offset_value7,
            offset_value8, offset_value9, offset_value10, offset_value11,
            self.endflag)

    def hxpd_command_to_struct(self, command):

        # Correct class structure for given command
        class InterlockStructure(ctypes.Structure):
            _fields_ = [("start_flag", ctypes.c_uint32),
                        ("message_length", ctypes.c_int32),
                        ("command_serial_number", ctypes.c_int32),
                        ("command", ctypes.c_int32),  # INT32
                        ("fashion", ctypes.c_int16),  # INT16
                        ("mode_lin", ctypes.c_int16),
                        ("p_xlin", ctypes.c_double),
                        ("p_ylin", ctypes.c_double),
                        ("p_zlin", ctypes.c_double),
                        ("v_lin", ctypes.c_double),
                        ("mode_rot", ctypes.c_int16),
                        ("p_xrot", ctypes.c_double),
                        ("p_yrot", ctypes.c_double),
                        ("p_zrot", ctypes.c_double),
                        ("v_rot", ctypes.c_double),
                        ("elevation", ctypes.c_double),
                        ("reserved", ctypes.c_double),  # real64
                        ("end_flag", ctypes.c_uint32)]  # DWORD

        size_of_struct = ctypes.sizeof(InterlockStructure())
        print(size_of_struct)  # To see the size in output, as it changes often
        cmd_hxpd, fashion, mode_lin, p_xlin, p_ylin, p_zlin, v_lin, \
            mode_rot, p_xrot, p_yrot, p_zrot, v_rot = command
        self.seconds = 12345  # Temporary to have identical stamps to compare

        self.structure = InterlockStructure(
            self.startflag, size_of_struct, self.seconds, cmd_hxpd, fashion,
            mode_lin, p_xlin, p_ylin, p_zlin, v_lin,
            mode_rot, p_xrot, p_yrot, p_zrot, v_rot,
            self.endflag)

    def polar_command_to_struct(self, command):

        # Correct class structure for given command
        class InterlockStructure(ctypes.Structure):
            _fields_ = [("start_flag", ctypes.c_uint32),
                        ("message_length", ctypes.c_int32),
                        ("command_serial_number", ctypes.c_int32),
                        ("command", ctypes.c_int32),
                        ("mode", ctypes.c_int16),
                        ("p_soll", ctypes.c_double),
                        ("v_cmd", ctypes.c_double),
                        ("end_flag", ctypes.c_uint32)]

        size_of_struct = ctypes.sizeof(InterlockStructure())
        print(size_of_struct)  # To see the size in output, as it changes often
        cmd_polar, fashion, p_soll, v_cmd = command
        self.seconds = 12345  # Temporary to have identical stamps to compare
        self.structure = InterlockStructure(
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

        self.structure = None  # Sets back to None in case already set

        # Next lines are just to create a unique timestamp to differentiate msgs
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.seconds = (now - midnight).seconds  # a unique int of length five

        if type_of_command.lower() == "interlock":
            self.interlock_command_to_struct(command_msg)
        elif type_of_command.lower() == "asf":
            self.asf_command_to_struct(command_msg) 
        elif type_of_command.lower() == 'hxpd':
            self.hxpd_command_to_struct(command_msg) 
        elif type_of_command.lower() == 'polar':
            print("MUST MAKE METHOD AND CTYPES CLASS FOR THIS CASE")  # TODO
        else:
            print("Unknown command type")

        packaged_ctype_with_pack = self.pack(self.structure)
        print("packaged_ctype_with_pack")
        print(packaged_ctype_with_pack)

        test_bytes = b''
        self.send_command(test_bytes)

    # # # # # 4.2 Interlock command # # # # #
    def set_mt_elevation(self, elevation):
        cmd_il = 106  # 4
        mode = 2000  # 4
        reserve = 0.0  # 8
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
    def deactivate_asf(self):
        cmd_as = 100
        mode = 1
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0
        offset_value1 = 0
        offset_value2 = 0
        offset_value3 = 0
        offset_value4 = 0
        offset_value5 = 0
        offset_value6 = 0
        offset_value7 = 0
        offset_value8 = 0
        offset_value9 = 0
        offset_value10 = 0
        offset_value11 = 0

        data = (cmd_as, mode, offset_dr_nr, offset_active, offset_value1,
                offset_value2, offset_value3, offset_value4, offset_value5,
                offset_value6, offset_value7, offset_value8, offset_value9,
                offset_value10, offset_value11)

        self.encapsulate_command("asf", data)

    def rest_pos_asf(self):
        cmd_as = 100
        mode = 6
        offset_dr_nr = 1  # 1-96 apparently
        offset_active = 0
        offset_value1 = 0
        offset_value2 = 0
        offset_value3 = 0
        offset_value4 = 0
        offset_value5 = 0
        offset_value6 = 0
        offset_value7 = 0
        offset_value8 = 0
        offset_value9 = 0
        offset_value10 = 0
        offset_value11 = 0

        data = (cmd_as, mode, offset_dr_nr, offset_active, offset_value1,
                offset_value2, offset_value3, offset_value4, offset_value5,
                offset_value6, offset_value7, offset_value8, offset_value9,
                offset_value10, offset_value11)

        self.encapsulate_command("asf", data)

    # # # # # 4.5 Subreflector positioning instruction set # # # # #

    def activate_hxpd(self):
        cmd_hxpd = 101
        fashion = 2
        mode_lin = 0
        p_xlin, p_ylin, p_zlin, v_lin = 0, 0, 0, 0
        mode_rot = 0
        p_xrot, p_yrot, p_zrot, v_rot = 0, 0, 0, 0

        data = (cmd_hxpd, fashion,
                mode_lin, p_xlin, p_ylin, p_zlin, v_lin,
                mode_rot, p_xrot, p_yrot, p_zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def deactivate_hxpd(self):
        cmd_hxpd = 101
        fashion = 1
        mode_lin = 0
        p_xlin, p_ylin, p_zlin, v_lin = 0, 0, 0, 0
        mode_rot = 0
        p_xrot, p_yrot, p_zrot, v_rot = 0, 0, 0, 0

        data = (cmd_hxpd, fashion,
                mode_lin, p_xlin, p_ylin, p_zlin, v_lin,
                mode_rot, p_xrot, p_yrot, p_zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def stop_hxpd(self):
        cmd_hxpd = 101
        fashion = 7
        mode_lin = 0
        p_xlin, p_ylin, p_zlin, v_lin = 0, 0, 0, 0
        mode_rot = 0
        p_xrot, p_yrot, p_zrot, v_rot = 0, 0, 0, 0

        data = (cmd_hxpd, fashion,
                mode_lin, p_xlin, p_ylin, p_zlin, v_lin,
                mode_rot, p_xrot, p_yrot, p_zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def acknowledge_error_on_hxpd(self):
        cmd_hxpd = 101
        fashion = 15
        mode_lin = 0
        p_xlin, p_ylin, p_zlin, v_lin = 0, 0, 0, 0
        mode_rot = 0
        p_xrot, p_yrot, p_zrot, v_rot = 0, 0, 0, 0

        data = (cmd_hxpd, fashion,
                mode_lin, p_xlin, p_ylin, p_zlin, v_lin,
                mode_rot, p_xrot, p_yrot, p_zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def preset_abs_hxpd(self, p_xlin, p_ylin, p_zlin, v_lin,
                        p_xrot, p_yrot, p_zrot, v_rot):
        try:
            assert (p_xlin <= 230) and (p_xlin >= -230)
            assert (p_ylin <= 180) and (p_ylin >= -180)
            assert (p_zlin <= 50) and (p_zlin >= -200)
            assert (v_lin <= 10) and (v_lin >= 0.001)
            assert (p_xrot <= 1.01) and (p_xrot >= -1.01)
            assert (p_yrot <= 1.01) and (p_yrot >= -1.01)
            assert (p_zrot <= 1.01) and (p_zrot >= -1.01)
            assert (v_rot <= 0.1) and (v_rot >= 0.00001)
        except AssertionError as E:
            logging.exception("Paramater(s) out of range")
            print(f"Assertion Error: {E}")

        cmd_hxpd = 101
        fashion = 2
        mode_lin = 3
        mode_rot = 3

        data = (cmd_hxpd, fashion,
                mode_lin, p_xlin, p_ylin, p_zlin, v_lin,
                mode_rot, p_xrot, p_yrot, p_zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    def preset_rel_hxpd(self, p_xlin, p_ylin, p_zlin, v_lin,
                        p_xrot, p_yrot, p_zrot, v_rot):
        try:
            assert (p_xlin <= 230) and (p_xlin >= -230)
            assert (p_ylin <= 180) and (p_ylin >= -180)
            assert (p_zlin <= 50) and (p_zlin >= -200)
            assert (v_lin <= 10) and (v_lin >= 0.001)
            assert (p_xrot <= 1.01) and (p_xrot >= -1.01)
            assert (p_yrot <= 1.01) and (p_yrot >= -1.01)
            assert (p_zrot <= 1.01) and (p_zrot >= -1.01)
            assert (v_rot <= 0.1) and (v_rot >= 0.00001)
        except AssertionError as E:
            logging.exception("Paramater(s) out of range")
            print(f"Assertion Error: {E}")

        cmd_hxpd = 101
        fashion = 2
        mode_lin = 4
        mode_rot = 4

        data = (cmd_hxpd, fashion,
                mode_lin, p_xlin, p_ylin, p_zlin, v_lin,
                mode_rot, p_xrot, p_yrot, p_zrot, v_rot)

        self.encapsulate_command("hxpd", data)

    # # # # # Polarization Drive # # # # #
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

    def preset_abs_polar(self, p_soll, v_cmd):
        assert (p_soll <= 195) and (p_soll >= -195)
        assert (v_cmd <= 3) and (v_cmd >= 0.000_01)

        cmd_polar = 102
        fashion = 3

        data = (cmd_polar, fashion, p_soll, v_cmd)
        self.encapsulate_command("polar", data)

    def preset_rel_polar(self, p_soll, v_cmd):
        assert (p_soll <= 195) and (p_soll >= -195)
        assert (v_cmd <= 3) and (v_cmd >= 0.000_01)

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

        cmd_time = 107
        fashion = fashion_value
        time_offset = time_offset_mode
        reserve = 0.0
        data = (cmd_time, fashion, time_offset, reserve)
        self.encapsulate_command('unknown', data)

    def close(self):
        self.sock.close()

# Old way to pack/unpack to bytes that is commented out
# def convert_bytes_to_structure(st, byte):
#     # sizoef(st) == sizeof(byte)
#     ctypes.memmove(ctypes.addressof(st), byte, ctypes.sizeof(st))
#
# def convert_struct_to_bytes(st):
#     buffer = ctypes.create_string_buffer(ctypes.sizeof(st))
#     ctypes.memmove(buffer, ctypes.addressof(st), ctypes.sizeof(st))
#     return buffer.raw
