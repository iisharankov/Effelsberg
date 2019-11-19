import time
import sys
import json
import socket
import struct
MULTICAST = ***REMOVED***
MULTIPORT = ***REMOVED***
MULTICAST_GROUP = ***REMOVED***

# TODO: Compare with multicast in python files, also:
# isharankov@be2:/opt/operatorguis/MCServer$ less MulticastDataServer.py



class GetterClass:

    def __init__(self):
        self.data = None
        self.init_multicast()

    def init_multicast(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_address = ('', MULTIPORT)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(server_address)

            group = socket.inet_aton(MULTICAST_GROUP)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP,
                                 socket.IP_ADD_MEMBERSHIP, mreq)
        except ConnectionError or OSError as E:
            print(E)


    def recv_mcast_data(self):
        try:
            multicastdata_bytes, address = self.sock.recvfrom(***REMOVED*** * 50)
            self.data = json.loads(str(multicastdata_bytes.decode('utf-8')))

            print('\n')
            print(self.data['status-data-irig-b-system'][
                      'current-time-as-modified-julian-day(mjd)'])
            print(self.data["status-data-active-surface"]["Elevation-angle[deg]"])
            # return self.data
        except OSError or ConnectionError as E:
            print(E)


def sdh_multicast():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        server_address = ('', MULTIPORT)  # sdh json
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)


        group = socket.inet_aton(MULTICAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        multicastdata_bytes, address = sock.recvfrom(300_000)

        return str(multicastdata_bytes.decode('utf-8'))

sock_inst = GetterClass()
while True:
    time.sleep(0.5)
    sock_inst.recv_mcast_data()
    # print(t['status-data-irig-b-system']['current-time-as-modified-julian-day(mjd)'])
    #
    # print(t["status-data-active-surface"]\
    #                             ["Elevation-angle[deg]"])
    # tt = t.decode('utf-8')
    # encoded_t = json.loads(tt)
    # # t = sdh_multicast()
    # print(encoded_t["status-data-active-surface"]\
    #                             ["Elevation-angle[deg]"])
    # loaded = json.loads(t)
    # print(type(loaded))
    # print(t)
    # print(loaded["status-data-irig-b-system"])