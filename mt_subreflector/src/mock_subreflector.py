import time
import ctypes
import socket
import pickle
import threading

SUBREF_ADDR = ***REMOVED***
SUBREF_READ_PORT = ***REMOVED***
SUBREF_WRITE_PORT = ***REMOVED***
buffer_size = ***REMOVED***

# TODO: ADD port ***REMOVED*** to receive commands, copy client.py methods to decode

# Opens and creates mirror samples of what the subreflector sends
# TODO: Local location, FIX before release
location = "/home/ivan/PycharmProjects/Effelsberg/mt_subreflector/data/" \
           "Pickled_Subreflector_Output.p"
with open(location, "rb") as pickle_instance:
    unpickled_obj = pickle.load(pickle_instance)
    first_msg = unpickled_obj[:***REMOVED***]
    second_msg = unpickled_obj[***REMOVED***:]


def main():
    t = threading.Thread(target=sender, args=(), name="***REMOVED*** Port")
    t.daemon = False
    t.start()

    t2 = threading.Thread(target=Receiver().create_socket, args=(), name="***REMOVED*** Port")
    t2.daemon = False
    t2.start()


class Receiver:

    def __init__(self):
        self.unpacked_data = 5

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
                while True:
                    time.sleep(1)
                    data = connection.recv(buffer_size)
                    if data:
                        self.find_structure_type(data)

    def find_structure_type(self, data):
        # This method unpacks the data message with a
        # BasicStructure class that can extract the command type

        try:
            _basic_unpack = self.unpack(BasicStructure, data)
            assert _basic_unpack.command in [100, 101, 102, 106]

        except AttributeError or AssertionError:
            pass
        else:
            if _basic_unpack.command == 100:
                self.unpacked_data = self.unpack(AsfStructure, data)
            elif _basic_unpack.command == 101:
                self.unpacked_data = self.unpack(HexapodStructure, data)
            elif _basic_unpack.command == 102:
                self.unpacked_data = self.unpack(PolarStructure, data)
            elif _basic_unpack.command == 106:
                self.unpacked_data = self.unpack(InterlockStructure, data)





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
                        time.sleep(0.01)
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


# # # # # # # # STRUCTURE CLASSES # # # # # # # #
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


class BasicStructure(ctypes.Structure):
    """
    BasicStructure is used to get the command value of the structure as it
    is the identifier that tells us what real Structure class to use. This
    structure only unpacks the first 4 values, the rest are lost.
    """
    _pack_ = 1
    _fields_ = [("start_flag", ctypes.c_uint32),
                ("message_length", ctypes.c_int32),
                ("command_serial_number", ctypes.c_int32),
                ("command", ctypes.c_int16)]


if __name__ == '__main__':
    main()
