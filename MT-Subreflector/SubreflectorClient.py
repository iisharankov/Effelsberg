#!/usr/bin/env python

import time
import socket
import struct
from astropy.time import Time

SUBREF_ADDR = "***REMOVED***"
SUBREF_PORT = ***REMOVED***

def decodeStruct(data):

    header = struct.unpack("=LiiH", data[:14])
    il = struct.unpack("=15BHB2H2H2f", data[14:48])
    power = struct.unpack("=5B", data[48:53])
    polar = struct.unpack("=2H2B27B25B8fH4f9BHBH6B4f9BHBH6B2H2f2H2f", data[53:241])
    hxpd = struct.unpack("=H6f2b22b2iH8f3B27BB25B8f3B27BB25B8f3B27BB25B8f3B27BB"
                         "25B8f3B27BB25B8f3B27BB25B4H4f2H4f2H2f", data[241:885])
    focus = struct.unpack("=H5BH3f8f3B27BB25B8f3B27BB25B2H2f2H2f", data[885:1106])
    asf = struct.unpack("=dI5B96B96h2H2H6Bh3f2H11h2H2f2H2f", data[1106:1489])
    bdKl = struct.unpack("=2BHHB10B10B2H2f2H2f", data[1489:1540])
    spKl = struct.unpack("=BH5BH2B27B2B3f2B27B2B3f2H2H2f", data[1540:1652])
    temp = struct.unpack("=10f10B", data[1652:1702])
    foctime = struct.unpack("=diH2B3d2H2f", data[1702:1754])
    last = struct.unpack("=2BI", data[1754:1760])

    return header, il, power, polar, hxpd, focus, \
           asf, bdKl, spKl, temp, foctime, last


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SUBREF_ADDR,SUBREF_PORT))
sock.send(b"\n")
full_msg = b''
flag = False

while 1:
    data = sock.recv(1760)
    print("data received", len(data))
    if flag:

        full_msg += bytearray(data)
        print(len(full_msg))

        if len(full_msg) == 1760:
            print("REACHED")
            print(full_msg)
            header, il, power, polar, hxpd, focus, asf, bdKl, spKl, temp, \
            foctime, last = decodeStruct(full_msg)
            # print('header:',header)

            print('il:', il)
            print('power:', power)
            print('polar:', polar)
            print('heaxa:', hxpd)
            print('focus:', focus)
            print('asf:', asf)
            print('bdKl:', bdKl)
            print('temp:', temp)
            t=Time(foctime[0], format="mjd")
            print('foctime:', t.isot, foctime)
            print('last:',last)
            full_msg = b''
    else:
        flag =True

        # print("REACHED END!")
        # sock.close()

    # except Exception as err:
    #     print("Error occured: ", err)

