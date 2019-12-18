import time
import sys
import json
import socket
import struct
from collections import defaultdict

from subtools.config import MULTICAST_IP, MULTICAST_PORT, BUFFER_SIZE

class GetterClass:

    def __init__(self):
        self.data = None
        self.init_multicast()

    def init_multicast(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_address = ('', MULTICAST_PORT)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(server_address)

            group = socket.inet_aton(MULTICAST_IP)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP,
                                 socket.IP_ADD_MEMBERSHIP, mreq)
        except ConnectionError or OSError as E:
            print(E)


    def recv_mcast_data(self):
        try:
            multicastdata_bytes, address = self.sock.recvfrom(BUFFER_SIZE * 50)
            self.data = json.loads(str(multicastdata_bytes.decode('utf-8')))
            # dumpped = json.dumps(self.data)
            # print(dumpped)
            return self.data

        except OSError or ConnectionError as E:
            print(E)


def sdh_multicast():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        server_address = ('', MULTICAST_PORT)  # sdh json
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)


        group = socket.inet_aton(MULTICAST_IP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        multicastdata_bytes, address = sock.recvfrom(300_000)

        return str(multicastdata_bytes.decode('utf-8'))

headers = [
    "status-data-interlock",
    "status-data-polarization-drive",
    "status-data-hexapod-drive",
    "status-data-focus-change-drive",
    "status-data-active-surface",
    "status-data-bottom-flap",
    "status-data-mirror-flap",
    "status-data-temperature",
    "status-data-irig-b-system",
]

masters = [defaultdict(list), defaultdict(list), defaultdict(list),
           defaultdict(list), defaultdict(list), defaultdict(list),
           defaultdict(list), defaultdict(list), defaultdict(list)]


sock_inst = GetterClass()
count = 0
while True:
    time.sleep(1)
    data = sock_inst.recv_mcast_data()
    print(json.dumps(data, indent=2))

    # for nesteddict, master in zip(headers, masters):
    #     # master = defaultdict(list)
    #     for k, v in data[nesteddict].items():
    #         master[k].append(v)
    #
    # if count%25 == 0:
    #     with open('getter_data.txt', 'w+') as file:
    #         print(count)
    #         # file.write(str(count) + "\n")
    #         for nesteddict, master in zip(headers, masters):
    #             # takes useful info (word after 2nd '-'), and pads to left side
    #             just_name = nesteddict.split('-')[2].ljust(15)
    #             file.write(just_name + str(master) + "\n")
    #
    #

