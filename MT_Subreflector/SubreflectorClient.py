#!/usr/bin/env python

import time
import json
import socket
import struct
import pickle
from astropy.time import Time

SUBREF_ADDR = ***REMOVED***
SUBREF_PORT = ***REMOVED***


def decode_struct(data):
    header = struct.unpack("=LiiH", data[:14])
    il = struct.unpack("=15BHB2H2H2f", data[14:48])
    power = struct.unpack("=5B", data[48:53])
    polar = struct.unpack("=2H2B27B25B8fH4f9BHBH6B4f9BHBH6B2H2f2H2f",
                          data[53:241])
    hxpd = struct.unpack("=H6f2b22b2iH8f3B27BB25B8f3B27BB25B8f3B27BB25B8f3B27BB"
                         "25B8f3B27BB25B8f3B27BB25B4H4f2H4f2H2f", data[241:885])
    focus = struct.unpack("=H5BH3f8f3B27BB25B8f3B27BB25B2H2f2H2f",
                          data[885:1106])
    asf = struct.unpack("=dI5B96B96h2H2H6Bh3f2H11h2H2f2H2f", data[1106:1489])
    bdkl = struct.unpack("=2BHHB10B10B2H2f2H2f", data[1489:1540])
    spkl = struct.unpack("=BH5BH2B27B2B3f2B27B2B3f2H2H2f", data[1540:1652])
    temp = struct.unpack("=10f10B", data[1652:1702])
    foctime = struct.unpack("=diH2B3d2H2f", data[1702:1754])
    last = struct.unpack("=2BI", data[1754:1760])

    return header, il, power, polar, hxpd, focus, \
           asf, bdkl, spkl, temp, foctime, last


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SUBREF_ADDR, SUBREF_PORT))
    sock.send(b"\n")
    print("1")
    full_msg = b''
    counter = 0
    while 1:
        print("in loop")
        data = sock.recv(1760)
        print("2")
        print("data received", len(data))
        if counter == 0:
            counter += 1
        else:

            full_msg += bytearray(data)
            # full_msg += data

            if len(full_msg) >= 1760:
                pickle.dump(full_msg, open("pickled_data.p", "ab"))
                print("pickled")
                # full_msg = b''
                time.sleep(2)
                # with open('dumpfile_bytes.txt', 'ab') as file:
                #     file.write(full_msg)
                #     print(full_msg)
                #     print("message written to file")

                break



def mainn():
    full_msg = b''
    flag = True

    if flag:
        unpickled_obj = pickle.load(open("pickled_data.p", "rb"))

        time.sleep(1)
        if True:
            print("Full length reached")

            # file1 = '/home/ivan/PycharmProjects/Effelsberg/MT_Subreflector/bytes.txt'
            # file2 = '/home/ivan/PycharmProjects/Effelsberg/MT_Subreflector/output.bin'
            # file3 = '/home/ivan/PycharmProjects/Effelsberg/MT_Subreflector/dumpfile_bytes.txt'
            #
            # with open(file1) as filename:
            #     msg = filename.read()
            #     print("The length of the message is: ", len(msg))
            #     print(type(msg))
            #     full_msg = bytes(msg, encoding='utf-16')
            # print(favorite_color)
            # print(len(favorite_color))
            # print(type(favorite_color))
            # string = favorite_color.decode()
            # print(len(string), string)
            # backtobytes =  string.encode() #bytes(string)
            # print(len(backtobytes))

            # print_data(unpickled_obj)

            header, il, power, polar, hxpd, focus, asf, bdkl, spkl, temp, \
            foctime, last = decode_struct(unpickled_obj)

            # print('header:', header)
            # print('il:', il)
            print('power:', power)
            # print('polar:', polar)
            # print('heaxa:', hxpd)
            # print('focus:', focus)
            # print('asf:', asf)
            # print('bdkl:', bdkl)
            # print('temp:', temp)
            # t = Time(foctime[0], format="mjd")
            # print('foctime:', t.isot, foctime)
            # print('last:', last)
            print(len(il))


            humanData = (json.dumps({
                'Status data Interlock':
                    {
                        'Active control unit': il[0],
                        'simulation': il[1],
                        'Control voltage on': il[2],
                        'Control active': il[3],
                        'service mode': il[4],
                        'override': il[5],
                        'Feed-in Regeneration Module On': il[6],
                        'Infeed-regenerative module Ready Warning': il[7],
                        'Feed-in feedback module Temperature warning': il[8],
                        'Infeed-regenerative module error timeout': il[9],
                        'fieldbus': il[10],
                        'Interlock cycle monitoring': il[11],
                        'Interlock emergency stop (safety device)': il[12],
                        'Interlock Emergency Stop Chain': il[13],
                        'Interlock software': il[14],
                        'Emergency stop button (bit-coded)': il[15],
                        'Communication with host interrupted (warning)': il[16],
                        'Last sent mode command': il[17],
                        'Command response of the mode command': il[18],
                        'Last sent parameter command': il[19],
                        'Command response of the parameter command': il[20],
                        'Parameter 1 of the parameter Command': il[21],
                        'Parameter 2 of the parameter Command': il[22],
            },
                'Power':
                    {
                        'unknown1': power[0],
                        'unknown2': power[1],
                        'unknown3': power[2],
                        'unknown4': power[3],
                        'unknown5': power[4],
                    }

            }, indent=2,))

            print(humanData)
            print(type(humanData))

            full_msg = b''
            humanstring = json.loads(humanData)
            print(type(humanstring))

            print(humanstring['Status data Interlock'])
            # print(humanstring['Status data Interlock'][0][0])
            print(humanstring['Status data Interlock']['Active control unit'])
            print(humanstring['Power'])
            # j = json.dumps(header)
            # print(type(j), j)
            # s = json.loads(j)
            # print(type(s), s)

if __name__ == '__main__':
    mainn()
