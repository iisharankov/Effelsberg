#!/usr/bin/env python
import socket
import datetime
import struct

TCP_IP = '***REMOVED***'
TCP_PORT = ***REMOVED***
BUFFER_SIZE = ***REMOVED***


class MTCommand:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))

    def send_command(self,command):
        self.sock.send(command)
    '''
    So he wants this to be rewritten and cleaned up
    may not be correct!
    now, midnight, seconds is used to make a unique identifier
    start and end flags are explained in the code
    make sure the length of dataLen is correct. 
    make an __init__ and clean up this class
    cmd_il stands for command interlock and the mode is the command for
    the elevation angle, 1, 2, or 2000. Make all three
    Defined in page 6 and 7 in EFB_SPE documentation 
    
    '''
    def encapsulate_command(self, command):
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds = (now - midnight).seconds # len of 5 - no milliseconds
        startflag = 0x1DFCCF1A
        endflag = 0xA1FCCFD1

        # Todo: this should unpack no matter length, not just 4 long
        cmd_il, mode, elevation, reserve = command

        # starflag_len = 4
        # dataLen_len = 4
        # seconds_len = 4
        # cmd_il_len = 4
        # mode_len = 2
        # elevation_len = 8
        # reserve_len = 8
        # endflag_len = 4

        # dataLen = starflag_len + dataLen_len + seconds_len + \
        #           cmd_il_len + mode_len + elevation_len + \
        #           reserve_len + endflag_len
        dataLen = 48
        # Flags are long long (len 8), but dataLen and seconds are long (len 4)?
        s = struct.pack("LiiihddL", startflag, dataLen, seconds,
                        cmd_il, mode, elevation, reserve, endflag)
        print(s.__sizeof__())
        self.send_command(s)

    def set_mt_elevation(self, elevation):
        cmd_il = 106  # 4
        mode = 2000  # 4
        reserve = 0.0  # 8
        data = (cmd_il, mode, elevation, reserve)
        self.encapsulate_command(data)

    def activate_mt(self):
        cmd_il = 106
        mode = 2
        elevation = 0.0
        reserve = 0.0
        # s = struct.pack("Iidd", cmd_il, mode, elevation, reserve)
        data = (cmd_il, mode, elevation, reserve)
        self.encapsulate_command(data)

    def deactivate_mt(self):
        cmd_il = 106
        mode = 1
        elevation = 0.0
        reserve = 0.0
        # s =  struct.pack("Iidd", cmd_il,  mode, elevation, reserve)
        data = (cmd_il, mode, elevation, reserve)
        self.encapsulate_command(data)

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
        self.encapsulate_command(data)

    def close(self):
        self.sock.close()
