import time
import json
import ctypes
import socket
import pickle
import threading

from . import process_message

# __all__ = ['start_mock_server']


SUBREF_ADDR = ***REMOVED***
SUBREF_READ_PORT = ***REMOVED***
SUBREF_WRITE_PORT = ***REMOVED***
buffer_size = ***REMOVED***

# TODO: ADD port ***REMOVED*** to receive commands, copy client.py methods to decode
# for a, b in zip(sample_msg, origional_way):
#     # assert np.isclose(a, b, 0.00001)
#     for x, y in zip(a, b):
#         assert abs(x-y) < 0.01

# takes the sample message in process_message and encodes it to send through
sample_msg = process_message.encode_struct(*process_message.sample_message)

# Seperates the message into 2, just like received by the real SR
first_msg = sample_msg[:***REMOVED***]
second_msg = sample_msg[***REMOVED***:]

def main():
    my_receiver = Receiver()
    start_mock_server(my_receiver)

def start_mock_server(my_receiver):
    t = threading.Thread(target=sender, args=(), name="***REMOVED*** Port")
    t.daemon = False
    t.start()

    t2 = threading.Thread(target=my_receiver.create_socket, args=(),
                          name="***REMOVED*** Port")
    t2.daemon = False
    t2.start()


class Receiver:

    def __init__(self):
        self.unpacked_data = 61
        self.elevation = None
        self.do_run = True

    def shutdown(self):
        print('Receiver shutdown')
        self.do_run = False

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
        # create TCP/IP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            server_address = (SUBREF_ADDR, SUBREF_WRITE_PORT)
            print('starting up on %s port %s' % server_address)

            # Sets the maximum buffersize of the socket to ***REMOVED***
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)

            # SO_REUSEADDR tells kernel to use socket even if in TIME_WAIT state
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(server_address)
            sock.listen(2)

            while True:
                time.sleep(1)
                # listen for incoming connections (server mode)
                connection, client_address = sock.accept()

                # intercept SR command to deconstruct
                while self.do_run:
                    # time.sleep()
                    data = connection.recv(buffer_size)
                    if data:
                        self.find_structure_type(data)

    def find_structure_type(self, data):
        self.unpacked_data = 50
        # This method unpacks the data message with a
        # BasicStructure class that can extract the command type

        try:
            _basic_unpack = self.unpack(process_message.BasicStructure, data)
            assert _basic_unpack.command in [100, 101, 102, 106]

        except AttributeError or AssertionError:
            pass
        else:

            if _basic_unpack.command == 100:
                unpacked_data = self.unpack(process_message.AsfStructure, data)
                self.asf_parser(unpacked_data)
            elif _basic_unpack.command == 101:
                unpacked_data = self.unpack(process_message.HexapodStructure, data)
                self.hexapod_parser(unpacked_data)
            elif _basic_unpack.command == 102:
                unpacked_data = self.unpack(process_message.PolarStructure, data)
                self.polar_parser(unpacked_data)
            elif _basic_unpack.command == 106:
                unpacked_data = self.unpack(process_message.InterlockStructure, data)
                print(unpacked_data.elevation)
                self.interlock_parser(unpacked_data)

    def asf_parser(self, unpacked_data):
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



    def hexapod_parser(self, unpacked_data):
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


    def polar_parser(self, unpacked_data):
        assert unpacked_data.command == 102
        self.interlock_mode = unpacked_data.mode
        self.interlock_p_soll = unpacked_data.p_soll
        self.interlock_v_cmd = unpacked_data.v_cmd

    def interlock_parser(self, unpacked_data):
        assert unpacked_data.command == 106
        self.interlock_mode = unpacked_data.mode
        self.interlock_elevation = unpacked_data.elevation
        self.interlock_reserverd = unpacked_data.reserved
        print("interlock_parser")
        print(f"{self.interlock_elevation}")



# Part that emulates port ***REMOVED*** and spits out data packets
def sender():
    # create TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        server_address = (SUBREF_ADDR, SUBREF_READ_PORT)
        print('starting up on %s port %s' % server_address)

        # Sets the maximum buffersize of the socket to ***REMOVED***
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)

        # SO_REUSEADDR tells kernel to use socket even if in TIME_WAIT state
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)
        sock.listen(2)

        while True:
            # listen for incoming connections (server mode)
            # with one connection a time
            print('waiting for a connection')
            connection, client_address = sock.accept()
            print("connection from", client_address)

            # receive the data in small chunks and print it
            while True:

                data = connection.recv(buffer_size)
                if data == b"\n":
                    print("Initialization request received")

                    while True:
                        time.sleep(0.05)
                        # Loop sending messages just like the real SR does
                        try:
                            connection.send(second_msg)
                            connection.send(first_msg)
                        except ConnectionError:
                            # If broken pipe, break for next connection
                            connection.close()  # Close connection as well
                            print("Connection broken, awaiting new connection")
                            break

                break




if __name__ == '__main__':
    start_mock_server()
