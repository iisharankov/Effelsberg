import time
import json
import socket
import struct
MULTICAST = '***REMOVED***'
MULTIPORT = ***REMOVED***
MULTICAST_GROUP = '***REMOVED***'

# TODO: This can be implemented into SubreflectorProgram, but how do we need it?
#  kind of a waste have it all printed? Just the "last command" lines maybe?

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


while True:
    t = sdh_multicast()
    print(t)
    # loaded = json.dumps(t)
    # print(loaded)