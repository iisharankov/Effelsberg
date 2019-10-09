#!/usr/bin/env python
import socket
import struct

mcast_group = '***REMOVED***'

#server_address = ('', 1600) # sdh information xml
#server_address = ('', 1601) # telescop information
# server_address = ('', 1602) # sdh json
#server_address = ('', ***REMOVED***)  READING

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind(server_address)
# group = socket.inet_aton(mcast_group)
# mreq = struct.pack('4sL', group, socket.INADDR_ANY)
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
# f = open('recstringSDH', 'w')
# rec=1
# while rec < 10:
#     data, address = sock.recvfrom(300000)
#     recvstring = str(data)
#     print(recvstring)
#     rec+=1
#     f.write(recvstring+'\n')
# f.close()

