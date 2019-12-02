import time
import json
import ctypes
import socket
import pickle
import threading

from . import process_message, config


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
        # self.unpacked_data = 61  # TODO method does not replace this???
        self.do_run = True


    def shutdown(self):
        print('Receiver shutdown')
        print(f"The do_run value is {self.do_run}")
        templock = threading.Lock()


        with templock:
            self.do_run = False
        print(f"The do_run value is {self.do_run}")


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
            server_address = (config.LOCAL_IP, config.SR_WRITE_PORT)
            # sock.settimeout(3)
            sock.setblocking(False)
            # Sets the maximum buffersize of the socket to ***REMOVED***
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, config.BUFFER_SIZE)

            # SO_REUSEADDR tells kernel to use socket even if in TIME_WAIT state
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(server_address)

            sock.listen(2)


            while True:

                # listen for incoming connections (server mode)
                if not self.do_run:
                    print("BREAKING")
                    break
                try:
                    connection, client_address = sock.accept()
                except BlockingIOError:
                    pass
                else:
                    # intercept SR command to deconstruct
                    while True:
                        try:
                            data = connection.recv(config.BUFFER_SIZE)
                            if data:
                                self.find_structure_type(data)
                        except ConnectionError:
                            break

    def find_structure_type(self, data):
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
                self.unpacked_data = self.unpack(process_message.InterlockStructure, data)
                # print(unpacked_data.elevation)
                # print("jnvfkjvkjfvjsfvjJNJNEVJINVIEJNVIPJJRF")
                # print(unpacked_data)
                # self.dataa = unpacked_data
                # print(self.dataa.elevation)
                # print("jnvfkjvkjfvjsfvjJNJNEVJINVIEJNVIPJJRF")
                print(f"self.unpacked_data.elevation is {self.unpacked_data.elevation}")

                assert self.unpacked_data.command == 106
                print(f"self.unpacked_data is : {self.unpacked_data}")
                self.interlock_mode = self.unpacked_data.mode
                self.interlock_elevation = self.unpacked_data.elevation
                self.interlock_reserverd = self.unpacked_data.reserved

                # self.interlock_parser()

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

    # def interlock_parser(self):
    #     unpacked_data = self.unpacked_data





# Part that emulates port ***REMOVED*** and spits out data packets
def sender():
    # create TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        server_address = (config.LOCAL_IP, config.SR_READ_PORT)


        # Sets the maximum buffersize of the socket to ***REMOVED***
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, config.BUFFER_SIZE)

        # SO_REUSEADDR tells kernel to use socket even if in TIME_WAIT state
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)

        print('Mock subreflector started on %s' % server_address[0])
        sock.listen(2)


        while True:
            # listen for incoming connections (server mode)
            # with one connection a time

            connection, client_address = sock.accept()
            print("Connection from", client_address)

            # receive the data in small chunks and print it
            while True:

                data = connection.recv(config.BUFFER_SIZE)
                if data == b"\n":

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
    main()
