#!/usr/bin/env python

import time
import json
import socket
import struct
import pickle
from astropy.time import Time

SUBREF_ADDR = "***REMOVED***"
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
                pickle.dump(full_msg, open("sept30pickled_data.p", "ab"))
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
        unpickled_obj = pickle.load(open("sept30pickled_data.p", "rb"))

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
            # print('power:', power)
            # print('polar:', polar)
            # print('heaxa:', hxpd)
            # print('focus:', focus)
            # print('asf:', asf)
            # print('bdkl:', bdkl)
            # print('temp:', temp)
            # t = Time(foctime[0], format="mjd")
            # print('foctime:', t.isot, foctime) #IRIG
            # print('last:', last)
            print(len(bdkl))
            print(bdkl)
            for idx, val in enumerate(bdkl):
                print(idx, val)

            humanData = {
                'status-data-interlock':
                    {
                        'active-control-unit': il[0],
                        'simulation': il[1],
                        'control-voltage-on': il[2],
                        'control-active': il[3],
                        'service-mode': il[4],
                        'override': il[5],
                        'feed-in-regeneration-module-on': il[6],
                        'infeed-regenerative-module-ready-warning': il[7],
                        'feed-in-feedback-module-temperature-warning': il[8],
                        'infeed-regenerative-module-error-timeout': il[9],
                        'fieldbus': il[10],
                        'interlock-cycle-monitoring': il[11],
                        'interlock-emergency-stop-(safety-device)': il[12],
                        'interlock-emergency-stop-chain': il[13],
                        'interlock-software': il[14],
                        'emergency-stop-button-(bit-coded)': il[15],
                        'communication-with-host-interrupted-(warning)': il[16],
                        'last-sent-mode-command': il[17],
                        'command-response-of-the-mode-command': il[18],
                        'last-sent-parameter-command': il[19],
                        'command-response-of-the-parameter-command': il[20],
                        'parameter-1-of-the-parameter-command': il[21],
                        'parameter-2-of-the-parameter-command': il[22],
                    },

                'power':
                    {
                        'unknown1': power[0],
                        'unknown2': power[1],
                        'unknown3': power[2],
                        'unknown4': power[3],
                        'unknown5': power[4],
                    },

                'status-data-polarization-drive':
                    {
                        'status-of-the-subsystem': polar[0],
                        'trajectory-status': polar[1],
                        'collective-status-error': polar[2],
                        'collective-status-warning': polar[3],
                        ###
                        'spindle1-software-emergency-stop': polar[4],
                        'spindle1-hardware-emergency-stop': polar[5],
                        'spindle1-emergency-stop-switch-up': polar[6],
                        'spindle1-emergency-limit-switch-down': polar[7],
                        'spindle1-group-error': polar[8],
                        'spindle1-brakes': polar[9],
                        'spindle1-power': polar[10],
                        'spindle1-servo-system': polar[11],
                        'spindle1-engine-timeout': polar[12],
                        'spindle1-speedometer': polar[13],
                        'spindle1-maximum-engine-speed-achieved': polar[14],
                        'spindle1-iquad_t;': polar[15],
                        'spindle1-position-encoder-hardware': polar[16],
                        'spindle1-position-encoder-step': polar[17],
                        'spindle1-position-outside-the-defined-area': polar[18],
                        'spindle1-maximum-position-deviation-reached': polar[19],
                        'spindle1-fieldbus': polar[20],
                        'spindle1-feed-back-module-servo': polar[21],
                        'spindle1-override': polar[22],
                        'spindle1-command-timeout': polar[23],
                        'spindle1-communication-error-with-host-computer': polar[24],
                        'spindle1-referencescoder-is-missing': polar[25],
                        'spindle1-referencescoder-error': polar[26],
                        'spindle1-speed-governor': polar[27],
                        'spindle1-maximum-speed-deviation-achieved': polar[28],
                        'spindle1-lock': polar[29],
                        'spindle1-external-error': polar[30],
                        ###
                        'spindle1-speed-mode': polar[31],
                        'spindle1_-override': polar[32],
                        'spindle1-stow-pin-in': polar[33],
                        'spindle1-parameter-error': polar[34],
                        'spindle1-power-heating': polar[35],
                        'spindle1-power-breaks': polar[36],
                        'spindle1-power-drives': polar[37],
                        'spindle1-power-external-24v': polar[38],
                        'spindle1-power-internal-24v': polar[39],
                        'spindle1-power-control': polar[40],
                        'spindle1_-position-encoder-hardware': polar[41],
                        'spindle1-engine-warning': polar[42],
                        'spindle1-mazimum-torque-achieved': polar[43],
                        'spindle1-degraded-fashion': polar[44],
                        'spindle1-security-device': polar[45],
                        'spindle1-ermaus': polar[46],
                        'spindle1-ermservo': polar[47],
                        'spindle1-emergency-limit-switch-up': polar[48],
                        'spindle1_-emergency-limit-switch-down': polar[49],
                        'spindle1-pre-limit-switch-up': polar[50],
                        'spindle1-pre-limit-switch-down': polar[51],
                        'spindle1-operating-limit-switch-up': polar[52],
                        'spindle1-operating-limit-switch-down': polar[53],
                        'spindle1-software-limit-switch-up': polar[54],
                        'spindle1-software-limit-switch-down': polar[55],
                        ###
                        'detailed-list-of-individual-warnings.-please-'
                        'refer-structure-5.11': polar[56],
                        'position-trajectory-[deg]': polar[56],
                        'current-actual-position-[deg]': polar[57],
                        'current-position-offset-[deg]': polar[58],
                        'current-position-deviation-[deg]': polar[59],
                        'current-web-speed-[deg-/-s]': polar[60],
                        'current-speed-[deg-/-s]': polar[61],
                        'current-speed-deviation-[deg-/-s': polar[62],
                        'current-acceleration-[deg-/-s²]': polar[63],
                        'display-of-the-selected-motors-(bit-coded)': polar[64],
                        ###
                        'engine1-current-position-[deg]': polar[65],
                        'engine1-current-speed-[deg-/-s]': polar[66],
                        'engine1-current-torque-[nm]': polar[67],
                        'engine1-current-engine-utilization-[%]': polar[68],
                        'engine1-initialization': polar[69],
                        'engine1-engine-ready': polar[70],
                        'engine1-engine-active': polar[71],
                        'engine1-speed-=-0': polar[72],
                        'engine1-speed-​​ok': polar[73],
                        'engine1-position-ok': polar[74],
                        'engine1-bus-error': polar[75],
                        'engine1-servo-error': polar[76],
                        'engine1-sensor-error': polar[77],
                        'engine1-reserve': polar[78],
                        'engine1-warning': polar[79],
                        'engine1-reserve-#2': polar[80],
                        'engine1-i²-t': polar[81],
                        'engine1-temperature-amplifier': polar[82],
                        'engine1-temperature-motor': polar[83],
                        'engine1-uic': polar[84],
                        'engine1-maximum-speed-achieved': polar[85],
                        'engine1-maximum-torque-achieved': polar[86],
                        ###
                        'engine2-current-position-[deg]': polar[87],
                        'engine2-current-speed-[deg-/-s]': polar[88],
                        'engine2-current-torque-[nm]': polar[89],
                        'engine2-current-engine-utilization-[%]': polar[90],
                        'engine2-initialization': polar[91],
                        'engine2-engine-ready': polar[92],
                        'engine2-engine-active': polar[93],
                        'engine2-speed-=-0': polar[94],
                        'engine2-speed-​​ok': polar[95],
                        'engine2-position-ok': polar[96],
                        'engine2-bus-error': polar[97],
                        'engine2-servo-error': polar[98],
                        'engine2-sensor-error': polar[99],
                        'engine2-reserve': polar[100],
                        'engine2-warning': polar[101],
                        'engine2-reserve-#2': polar[102],
                        'engine2-i²-t': polar[103],
                        'engine2-temperature-amplifier': polar[104],
                        'engine2-temperature-motor': polar[105],
                        'engine2-uic': polar[106],
                        'engine2-maximum-speed-achieved': polar[107],
                        'engine2-maximum-torque-achieved': polar[108],
                        ###
                        'last-sent-mode-command': polar[109],
                        'command-response-of-the-mode-command': polar[110],
                        'target-position-of-the-mode-command': polar[111],
                        'target-speed-of-the-mode-command': polar[112],
                        'last-sent-parameter-command': polar[113],
                        'command-response-of-the-parameter-command': polar[114],
                        'parameter-1-of-the-parameter-command': polar[115],
                        'parameter-2-of-the-parameter-command': polar[116],
                    },
                
                'status-data-hexapod-drive':
                    {
                        'status_of_the_subsystem_': hxpd[0],
                        'current_position_x_linear_[mm]': hxpd[1],
                        'current_position_y_linear_[mm]': hxpd[2],
                        'current_position_z_linear_[mm]': hxpd[3],
                        'current_position_x_rotation_[deg]': hxpd[4],
                        'current_position_y_rotation_[deg]': hxpd[5],
                        'current_position_z_rotation_[deg]': hxpd[6],
                        'collective_status_error': hxpd[7],
                        'collective_status_warning': hxpd[8],
                        #_warning_struct
                        'collective_message_warning_spindle': hxpd[9],
                        'collective_signal_pre-limit_switch_spindle_down': hxpd[10],
                        'group_message_pre-limit_switch_spindle_up': hxpd[11],
                        'group_message_maximum_speed': hxpd[12],
                        'inverse_transformation': hxpd[13],
                        'override_active': hxpd[14],
                        '3d_linear_position_preset_switch_down': hxpd[15],
                        '3d_linear_position_preset_switch_up': hxpd[16],
                        '3d_rotation_position_preset_switch_down': hxpd[17],
                        '3d_rotation_position_preset_switch_up': hxpd[18],
                        '3d_x_linear_position_operating_limit_switch_down': hxpd[19],
                        '3d_x_linear_position_limit_switch_up': hxpd[20],
                        '3d_y_linear_position_operating_limit_switch_down': hxpd[21],
                        '3d_y_linear_position_limit_switch_up': hxpd[22],
                        '3d_z_linear_position_operating_limit_switch_down': hxpd[23],
                        '3d_z_linear_position_limit_switch_up': hxpd[24],
                        '3d_x_rotation_position_operating_limit_switch_down': hxpd[25],
                        '3d_x_rotation_position_operating_limit_switch_up': hxpd[26],
                        '3d_y_rotation_position_operating_limit_switch_down': hxpd[27],
                        '3d_y_rotation_position_operating_limit_switch_up': hxpd[28],
                        '3d_z_rotation_position_operating_limit_switch_down': hxpd[29],
                        '3d_z_rotation_position_operating_limit_switch_up': hxpd[30],
                        #_end_warning_structure
                        'current_mode_of_linear_motion': hxpd[31],
                        'current_mode_of_rotation': hxpd[32],
                        'display_of_the_selected_motors_(bit-coded)': hxpd[33],
                        ####-start-of-spindles-####
                        'spindle1-current-position[mm/deg]': hxpd[34],
                        'spindle1-current-target-position[mm/deg]': hxpd[35],
                        'spindle1-current-position-offset[mm/deg]': hxpd[36],
                        'spindle1-current-speed[mm/s/deg/s]': hxpd[37],
                        'spindle1-current-target-speed[mm/s/deg/s]': hxpd[38],
                        'spindle1-current-web-speed[mm/s/deg/s]': hxpd[39],
                        'spindle1-position-deviation[mm/deg]': hxpd[40],
                        'spindle1-current-utilization-of-the-spindle[%]': hxpd[41],
                        'spindle1-spindle-active': hxpd[42],
                        'spindle1-brake-open': hxpd[43],
                        'spindle1-general-error': hxpd[44],
                        #-start-of-error-structure-(5.11-in-manual)
                        'spindle1-software-emergency-stop': hxpd[45],
                        'spindle1-hardware-emergency-stop': hxpd[46],
                        'spindle1-emergency-stop-switch-up': hxpd[47],
                        'spindle1-emergency-limit-switch-down': hxpd[48],
                        'spindle1-group-error': hxpd[49],
                        'spindle1-brakes': hxpd[50],
                        'spindle1-power': hxpd[51],
                        'spindle1-servo-system': hxpd[52],
                        'spindle1-engine-timeout': hxpd[53],
                        'spindle1-speedometer': hxpd[54],
                        'spindle1-maximum-engine-speed-achieved': hxpd[55],
                        'spindle1-iquad_t;': hxpd[56],
                        'spindle1-position-encoder-hardware': hxpd[57],
                        'spindle1-position-encoder-step': hxpd[58],
                        'spindle1-position-outside-the-defined-area': hxpd[59],
                        'spindle1-maximum-position-deviation-reached': hxpd[60],
                        'spindle1-fieldbus': hxpd[61],
                        'spindle1-feed-back-module-servo': hxpd[62],
                        'spindle1-override': hxpd[63],
                        'spindle1-command-timeout': hxpd[64],
                        'spindle1-communication-error-with-host-computer': hxpd[65],
                        'spindle1-referencescoder-is-missing': hxpd[66],
                        'spindle1-referencescoder-error': hxpd[67],
                        'spindle1-speed-governor': hxpd[68],
                        'spindle1-maximum-speed-deviation-achieved': hxpd[69],
                        'spindle1-lock': hxpd[70],
                        'spindle1-external-error': hxpd[71],
                        #  end-of-error-structure-(5.11-in-manual)
                        'spindle1-general-warning': hxpd[72],
                        #-start-of-warning-structure-(5.12-in-manual)
                        'spindle1-speed-mode': hxpd[73],
                        'spindle1_-override': hxpd[74],
                        'spindle1-stow-pin-in': hxpd[75],
                        'spindle1-parameter-error': hxpd[76],
                        'spindle1-power-heating': hxpd[77],
                        'spindle1-power-breaks': hxpd[78],
                        'spindle1-power-drives': hxpd[79],
                        'spindle1-power-external-24v': hxpd[80],
                        'spindle1-power-internal-24v': hxpd[81],
                        'spindle1-power-control': hxpd[82],
                        'spindle1_-position-encoder-hardware': hxpd[83],
                        'spindle1-engine-warning': hxpd[84],
                        'spindle1-mazimum-torque-achieved': hxpd[85],
                        'spindle1-degraded-fashion': hxpd[86],
                        'spindle1-security-device': hxpd[87],
                        'spindle1-ermaus': hxpd[88],
                        'spindle1-ermservo': hxpd[89],
                        'spindle1-emergency-limit-switch-up': hxpd[90],
                        'spindle1_-emergency-limit-switch-down': hxpd[91],
                        'spindle1-pre-limit-switch-up': hxpd[92],
                        'spindle1-pre-limit-switch-down': hxpd[93],
                        'spindle1-operating-limit-switch-up': hxpd[94],
                        'spindle1-operating-limit-switch-down': hxpd[95],
                        'spindle1-software-limit-switch-up': hxpd[96],
                        'spindle1-software-limit-switch-down': hxpd[97],
                        #-note: some-of-the-above-have-a-underscore-as-there-are
                        #-doubles-in-the-error-and-warning-stuct-with-the-same-name
                        ####
                        'spindle2-current-position[mm/deg]': hxpd[98],
                        'spindle2-current-target-position[mm/deg]': hxpd[99],
                        'spindle2-current-position-offset[mm/deg]': hxpd[100],
                        'spindle2-current-speed[mm/s/deg/s]': hxpd[101],
                        'spindle2-current-target-speed[mm/s/deg/s]': hxpd[102],
                        'spindle2-current-web-speed[mm/s/deg/s]': hxpd[103],
                        'spindle2-position-deviation[mm/deg]': hxpd[104],
                        'spindle2-current-utilization-of-the-spindle[%]': hxpd[105],
                        'spindle2-spindle-active': hxpd[106],
                        'spindle2-brake-open': hxpd[107],
                        'spindle2-general-error': hxpd[108],
                        'spindle2-software-emergency-stop': hxpd[109],
                        'spindle2-hardware-emergency-stop': hxpd[110],
                        'spindle2-emergency-stop-switch-up': hxpd[111],
                        'spindle2-emergency-limit-switch-down': hxpd[112],
                        'spindle2-group-error': hxpd[113],
                        'spindle2-brakes': hxpd[114],
                        'spindle2-power': hxpd[115],
                        'spindle2-servo-system': hxpd[116],
                        'spindle2-engine-timeout': hxpd[117],
                        'spindle2-speedometer': hxpd[118],
                        'spindle2-maximum-engine-speed-achieved': hxpd[119],
                        'spindle2-iquad_t;': hxpd[120],
                        'spindle2-position-encoder-hardware': hxpd[121],
                        'spindle2-position-encoder-step': hxpd[122],
                        'spindle2-position-outside-the-defined-area': hxpd[123],
                        'spindle2-maximum-position-deviation-reached': hxpd[124],
                        'spindle2-fieldbus': hxpd[125],
                        'spindle2-feed-back-module-servo': hxpd[126],
                        'spindle2-override': hxpd[127],
                        'spindle2-command-timeout': hxpd[128],
                        'spindle2-communication-error-with-host-computer': hxpd[129],
                        'spindle2-referencescoder-is-missing': hxpd[130],
                        'spindle2-referencescoder-error': hxpd[131],
                        'spindle2-speed-governor': hxpd[132],
                        'spindle2-maximum-speed-deviation-achieved': hxpd[133],
                        'spindle2-lock': hxpd[134],
                        'spindle2-external-error': hxpd[135],
                        'spindle2-general-warning': hxpd[136],
                        'spindle2-speed-mode': hxpd[137],
                        'spindle2_-override': hxpd[138],
                        'spindle2-stow-pin-in': hxpd[139],
                        'spindle2-parameter-error': hxpd[140],
                        'spindle2-power-heating': hxpd[141],
                        'spindle2-power-breaks': hxpd[142],
                        'spindle2-power-drives': hxpd[143],
                        'spindle2-power-external-24v': hxpd[144],
                        'spindle2-power-internal-24v': hxpd[145],
                        'spindle2-power-control': hxpd[146],
                        'spindle2_-position-encoder-hardware': hxpd[147],
                        'spindle2-engine-warning': hxpd[148],
                        'spindle2-mazimum-torque-achieved': hxpd[149],
                        'spindle2-degraded-fashion': hxpd[150],
                        'spindle2-security-device': hxpd[151],
                        'spindle2-ermaus': hxpd[152],
                        'spindle2-ermservo': hxpd[153],
                        'spindle2-emergency-limit-switch-up': hxpd[154],
                        'spindle2_-emergency-limit-switch-down': hxpd[155],
                        'spindle2-pre-limit-switch-up': hxpd[156],
                        'spindle2-pre-limit-switch-down': hxpd[157],
                        'spindle2-operating-limit-switch-up': hxpd[158],
                        'spindle2-operating-limit-switch-down': hxpd[159],
                        'spindle2-software-limit-switch-up': hxpd[160],
                        'spindle2-software-limit-switch-down': hxpd[161],
                        ####
                        'spindle3-current-position[mm/deg]': hxpd[162],
                        'spindle3-current-target-position[mm/deg]': hxpd[163],
                        'spindle3-current-position-offset[mm/deg]': hxpd[164],
                        'spindle3-current-speed[mm/s/deg/s]': hxpd[165],
                        'spindle3-current-target-speed[mm/s/deg/s]': hxpd[166],
                        'spindle3-current-web-speed[mm/s/deg/s]': hxpd[167],
                        'spindle3-position-deviation[mm/deg]': hxpd[168],
                        'spindle3-current-utilization-of-the-spindle[%]': hxpd[169],
                        'spindle3-spindle-active': hxpd[170],
                        'spindle3-brake-open': hxpd[171],
                        'spindle3-general-error': hxpd[172],
                        'spindle3-software-emergency-stop': hxpd[173],
                        'spindle3-hardware-emergency-stop': hxpd[174],
                        'spindle3-emergency-stop-switch-up': hxpd[175],
                        'spindle3-emergency-limit-switch-down': hxpd[176],
                        'spindle3-group-error': hxpd[177],
                        'spindle3-brakes': hxpd[178],
                        'spindle3-power': hxpd[179],
                        'spindle3-servo-system': hxpd[180],
                        'spindle3-engine-timeout': hxpd[181],
                        'spindle3-speedometer': hxpd[182],
                        'spindle3-maximum-engine-speed-achieved': hxpd[183],
                        'spindle3-iquad_t;': hxpd[184],
                        'spindle3-position-encoder-hardware': hxpd[185],
                        'spindle3-position-encoder-step': hxpd[186],
                        'spindle3-position-outside-the-defined-area': hxpd[187],
                        'spindle3-maximum-position-deviation-reached': hxpd[188],
                        'spindle3-fieldbus': hxpd[189],
                        'spindle3-feed-back-module-servo': hxpd[190],
                        'spindle3-override': hxpd[191],
                        'spindle3-command-timeout': hxpd[192],
                        'spindle3-communication-error-with-host-computer': hxpd[193],
                        'spindle3-referencescoder-is-missing': hxpd[194],
                        'spindle3-referencescoder-error': hxpd[195],
                        'spindle3-speed-governor': hxpd[196],
                        'spindle3-maximum-speed-deviation-achieved': hxpd[197],
                        'spindle3-lock': hxpd[198],
                        'spindle3-external-error': hxpd[199],
                        'spindle3-general-warning': hxpd[200],
                        'spindle3-speed-mode': hxpd[201],
                        'spindle3_-override': hxpd[202],
                        'spindle3-stow-pin-in': hxpd[203],
                        'spindle3-parameter-error': hxpd[204],
                        'spindle3-power-heating': hxpd[205],
                        'spindle3-power-breaks': hxpd[206],
                        'spindle3-power-drives': hxpd[207],
                        'spindle3-power-external-24v': hxpd[208],
                        'spindle3-power-internal-24v': hxpd[209],
                        'spindle3-power-control': hxpd[210],
                        'spindle3_-position-encoder-hardware': hxpd[211],
                        'spindle3-engine-warning': hxpd[212],
                        'spindle3-mazimum-torque-achieved': hxpd[213],
                        'spindle3-degraded-fashion': hxpd[214],
                        'spindle3-security-device': hxpd[215],
                        'spindle3-ermaus': hxpd[216],
                        'spindle3-ermservo': hxpd[217],
                        'spindle3-emergency-limit-switch-up': hxpd[218],
                        'spindle3_-emergency-limit-switch-down': hxpd[219],
                        'spindle3-pre-limit-switch-up': hxpd[220],
                        'spindle3-pre-limit-switch-down': hxpd[221],
                        'spindle3-operating-limit-switch-up': hxpd[222],
                        'spindle3-operating-limit-switch-down': hxpd[223],
                        'spindle3-software-limit-switch-up': hxpd[224],
                        'spindle3-software-limit-switch-down': hxpd[225],
                        ####
                        'spindle4-current-position[mm/deg]': hxpd[226],
                        'spindle4-current-target-position[mm/deg]': hxpd[227],
                        'spindle4-current-position-offset[mm/deg]': hxpd[228],
                        'spindle4-current-speed[mm/s/deg/s]': hxpd[229],
                        'spindle4-current-target-speed[mm/s/deg/s]': hxpd[230],
                        'spindle4-current-web-speed[mm/s/deg/s]': hxpd[231],
                        'spindle4-position-deviation[mm/deg]': hxpd[232],
                        'spindle4-current-utilization-of-the-spindle[%]': hxpd[233],
                        'spindle4-spindle-active': hxpd[234],
                        'spindle4-brake-open': hxpd[235],
                        'spindle4-general-error': hxpd[236],
                        'spindle4-software-emergency-stop': hxpd[237],
                        'spindle4-hardware-emergency-stop': hxpd[238],
                        'spindle4-emergency-stop-switch-up': hxpd[239],
                        'spindle4-emergency-limit-switch-down': hxpd[240],
                        'spindle4-group-error': hxpd[241],
                        'spindle4-brakes': hxpd[242],
                        'spindle4-power': hxpd[243],
                        'spindle4-servo-system': hxpd[244],
                        'spindle4-engine-timeout': hxpd[245],
                        'spindle4-speedometer': hxpd[246],
                        'spindle4-maximum-engine-speed-achieved': hxpd[247],
                        'spindle4-iquad_t;': hxpd[248],
                        'spindle4-position-encoder-hardware': hxpd[249],
                        'spindle4-position-encoder-step': hxpd[250],
                        'spindle4-position-outside-the-defined-area': hxpd[251],
                        'spindle4-maximum-position-deviation-reached': hxpd[252],
                        'spindle4-fieldbus': hxpd[253],
                        'spindle4-feed-back-module-servo': hxpd[254],
                        'spindle4-override': hxpd[255],
                        'spindle4-command-timeout': hxpd[256],
                        'spindle4-communication-error-with-host-computer': hxpd[257],
                        'spindle4-referencescoder-is-missing': hxpd[258],
                        'spindle4-referencescoder-error': hxpd[259],
                        'spindle4-speed-governor': hxpd[260],
                        'spindle4-maximum-speed-deviation-achieved': hxpd[261],
                        'spindle4-lock': hxpd[262],
                        'spindle4-external-error': hxpd[263],
                        'spindle4-general-warning': hxpd[264],
                        'spindle4-speed-mode': hxpd[265],
                        'spindle4_-override': hxpd[266],
                        'spindle4-stow-pin-in': hxpd[267],
                        'spindle4-parameter-error': hxpd[268],
                        'spindle4-power-heating': hxpd[269],
                        'spindle4-power-breaks': hxpd[270],
                        'spindle4-power-drives': hxpd[271],
                        'spindle4-power-external-24v': hxpd[272],
                        'spindle4-power-internal-24v': hxpd[273],
                        'spindle4-power-control': hxpd[274],
                        'spindle4_-position-encoder-hardware': hxpd[275],
                        'spindle4-engine-warning': hxpd[276],
                        'spindle4-mazimum-torque-achieved': hxpd[277],
                        'spindle4-degraded-fashion': hxpd[278],
                        'spindle4-security-device': hxpd[279],
                        'spindle4-ermaus': hxpd[280],
                        'spindle4-ermservo': hxpd[281],
                        'spindle4-emergency-limit-switch-up': hxpd[282],
                        'spindle4_-emergency-limit-switch-down': hxpd[283],
                        'spindle4-pre-limit-switch-up': hxpd[284],
                        'spindle4-pre-limit-switch-down': hxpd[285],
                        'spindle4-operating-limit-switch-up': hxpd[286],
                        'spindle4-operating-limit-switch-down': hxpd[287],
                        'spindle4-software-limit-switch-up': hxpd[288],
                        'spindle4-software-limit-switch-down': hxpd[289],
                        ####
                        'spindle5-current-position[mm/deg]': hxpd[290],
                        'spindle5-current-target-position[mm/deg]': hxpd[291],
                        'spindle5-current-position-offset[mm/deg]': hxpd[292],
                        'spindle5-current-speed[mm/s/deg/s]': hxpd[293],
                        'spindle5-current-target-speed[mm/s/deg/s]': hxpd[294],
                        'spindle5-current-web-speed[mm/s/deg/s]': hxpd[295],
                        'spindle5-position-deviation[mm/deg]': hxpd[296],
                        'spindle5-current-utilization-of-the-spindle[%]': hxpd[297],
                        'spindle5-spindle-active': hxpd[298],
                        'spindle5-brake-open': hxpd[299],
                        'spindle5-general-error': hxpd[300],
                        'spindle5-software-emergency-stop': hxpd[301],
                        'spindle5-hardware-emergency-stop': hxpd[302],
                        'spindle5-emergency-stop-switch-up': hxpd[303],
                        'spindle5-emergency-limit-switch-down': hxpd[304],
                        'spindle5-group-error': hxpd[305],
                        'spindle5-brakes': hxpd[306],
                        'spindle5-power': hxpd[307],
                        'spindle5-servo-system': hxpd[308],
                        'spindle5-engine-timeout': hxpd[309],
                        'spindle5-speedometer': hxpd[310],
                        'spindle5-maximum-engine-speed-achieved': hxpd[311],
                        'spindle5-iquad_t;': hxpd[312],
                        'spindle5-position-encoder-hardware': hxpd[313],
                        'spindle5-position-encoder-step': hxpd[314],
                        'spindle5-position-outside-the-defined-area': hxpd[315],
                        'spindle5-maximum-position-deviation-reached': hxpd[316],
                        'spindle5-fieldbus': hxpd[317],
                        'spindle5-feed-back-module-servo': hxpd[318],
                        'spindle5-override': hxpd[319],
                        'spindle5-command-timeout': hxpd[320],
                        'spindle5-communication-error-with-host-computer': hxpd[321],
                        'spindle5-referencescoder-is-missing': hxpd[322],
                        'spindle5-referencescoder-error': hxpd[323],
                        'spindle5-speed-governor': hxpd[324],
                        'spindle5-maximum-speed-deviation-achieved': hxpd[325],
                        'spindle5-lock': hxpd[326],
                        'spindle5-external-error': hxpd[327],
                        'spindle5-general-warning': hxpd[328],
                        'spindle5-speed-mode': hxpd[329],
                        'spindle5_-override': hxpd[330],
                        'spindle5-stow-pin-in': hxpd[331],
                        'spindle5-parameter-error': hxpd[332],
                        'spindle5-power-heating': hxpd[333],
                        'spindle5-power-breaks': hxpd[334],
                        'spindle5-power-drives': hxpd[335],
                        'spindle5-power-external-24v': hxpd[336],
                        'spindle5-power-internal-24v': hxpd[337],
                        'spindle5-power-control': hxpd[338],
                        'spindle5_-position-encoder-hardware': hxpd[339],
                        'spindle5-engine-warning': hxpd[340],
                        'spindle5-mazimum-torque-achieved': hxpd[341],
                        'spindle5-degraded-fashion': hxpd[342],
                        'spindle5-security-device': hxpd[343],
                        'spindle5-ermaus': hxpd[344],
                        'spindle5-ermservo': hxpd[345],
                        'spindle5-emergency-limit-switch-up': hxpd[346],
                        'spindle5_-emergency-limit-switch-down': hxpd[347],
                        'spindle5-pre-limit-switch-up': hxpd[348],
                        'spindle5-pre-limit-switch-down': hxpd[349],
                        'spindle5-operating-limit-switch-up': hxpd[350],
                        'spindle5-operating-limit-switch-down': hxpd[351],
                        'spindle5-software-limit-switch-up': hxpd[352],
                        'spindle5-software-limit-switch-down': hxpd[353],
                        ####
                        'spindle6-current-position[mm/deg]': hxpd[354],
                        'spindle6-current-target-position[mm/deg]': hxpd[355],
                        'spindle6-current-position-offset[mm/deg]': hxpd[356],
                        'spindle6-current-speed[mm/s/deg/s]': hxpd[357],
                        'spindle6-current-target-speed[mm/s/deg/s]': hxpd[358],
                        'spindle6-current-web-speed[mm/s/deg/s]': hxpd[359],
                        'spindle6-position-deviation[mm/deg]': hxpd[360],
                        'spindle6-current-utilization-of-the-spindle[%]': hxpd[361],
                        'spindle6-spindle-active': hxpd[362],
                        'spindle6-brake-open': hxpd[363],
                        'spindle6-general-error': hxpd[364],
                        'spindle6-software-emergency-stop': hxpd[365],
                        'spindle6-hardware-emergency-stop': hxpd[366],
                        'spindle6-emergency-stop-switch-up': hxpd[367],
                        'spindle6-emergency-limit-switch-down': hxpd[368],
                        'spindle6-group-error': hxpd[369],
                        'spindle6-brakes': hxpd[370],
                        'spindle6-power': hxpd[371],
                        'spindle6-servo-system': hxpd[372],
                        'spindle6-engine-timeout': hxpd[373],
                        'spindle6-speedometer': hxpd[374],
                        'spindle6-maximum-engine-speed-achieved': hxpd[375],
                        'spindle6-iquad_t;': hxpd[376],
                        'spindle6-position-encoder-hardware': hxpd[377],
                        'spindle6-position-encoder-step': hxpd[378],
                        'spindle6-position-outside-the-defined-area': hxpd[379],
                        'spindle6-maximum-position-deviation-reached': hxpd[380],
                        'spindle6-fieldbus': hxpd[381],
                        'spindle6-feed-back-module-servo': hxpd[382],
                        'spindle6-override': hxpd[383],
                        'spindle6-command-timeout': hxpd[384],
                        'spindle6-communication-error-with-host-computer': hxpd[385],
                        'spindle6-referencescoder-is-missing': hxpd[386],
                        'spindle6-referencescoder-error': hxpd[387],
                        'spindle6-speed-governor': hxpd[388],
                        'spindle6-maximum-speed-deviation-achieved': hxpd[389],
                        'spindle6-lock': hxpd[390],
                        'spindle6-external-error': hxpd[391],
                        'spindle6-general-warning': hxpd[392],
                        'spindle6-speed-mode': hxpd[393],
                        'spindle6_-override': hxpd[394],
                        'spindle6-stow-pin-in': hxpd[395],
                        'spindle6-parameter-error': hxpd[396],
                        'spindle6-power-heating': hxpd[397],
                        'spindle6-power-breaks': hxpd[398],
                        'spindle6-power-drives': hxpd[399],
                        'spindle6-power-external-24v': hxpd[400],
                        'spindle6-power-internal-24v': hxpd[401],
                        'spindle6-power-control': hxpd[402],
                        'spindle6_-position-encoder-hardware': hxpd[403],
                        'spindle6-engine-warning': hxpd[404],
                        'spindle6-mazimum-torque-achieved': hxpd[405],
                        'spindle6-degraded-fashion': hxpd[406],
                        'spindle6-security-device': hxpd[407],
                        'spindle6-ermaus': hxpd[408],
                        'spindle6-ermservo': hxpd[409],
                        'spindle6-emergency-limit-switch-up': hxpd[410],
                        'spindle6_-emergency-limit-switch-down': hxpd[411],
                        'spindle6-pre-limit-switch-up': hxpd[412],
                        'spindle6-pre-limit-switch-down': hxpd[413],
                        'spindle6-operating-limit-switch-up': hxpd[414],
                        'spindle6-operating-limit-switch-down': hxpd[415],
                        'spindle6-software-limit-switch-up': hxpd[416],
                        'spindle6-software-limit-switch-down': hxpd[417],
                        ####-end-of-spindles-####
                        'last_sent_mode_command_hexapod': hxpd[418],
                        'command_response_of_the_mode_command_hexapod': hxpd[419],
                        'last_sent_mode_command_linear': hxpd[420],
                        'command_response_of_the_mode_command_linear': hxpd[421],
                        'target_position_x_linear_[mm]': hxpd[422],
                        'nominal_position_y_linear_[mm]': hxpd[423],
                        'target_position_z_linear_[mm]': hxpd[424],
                        'target_speed_linear_[mm_/_s]': hxpd[425],
                        'last_sent_mode_command_rotation': hxpd[426],
                        'command_response_of_the_mode_command_rotation': hxpd[427],
                        'target_position_x_rotation_[deg]': hxpd[428],
                        'target_position_y_rotation_[deg]': hxpd[429],
                        'target_position_z_rotation_[deg]': hxpd[430],
                        'target_speed_linear_[deg_/_s]': hxpd[431],
                        'last_sent_parameter_command': hxpd[432],
                        'command_response_of_the_parameter_command': hxpd[433],
                        'parameter_1_of_the_parameter_command': hxpd[434],
                        'parameter_2_of_the_parameter_command': hxpd[435],
                        # There exists a way to loop the spindles, but honestly
                        # it's a bit too complicated to do it, and add it to a
                        # dict (they're unordered!). it could be done but would
                        # be too confusing for what it would save in lines. plus
                        # this is easily modifiable per spindle. it repeats,
                        # but it works
                    },
                
                'status-data-focus-change-drive':
                    {
                        'status-of-the-subsystem': focus[0],
                        'collective-status-warning': focus[1],
                        'collective-status-error': focus[2],
                        'primary-focus-position': focus[3],
                        'secondary-focus-position': focus[4],
                        'receiver-change-position': focus[5],
                        'display-of-the-selected-motors(bit-coded)': focus[6],
                        'current-target-position-[mm]': focus[7],
                        'current-position[mm]': focus[8],
                        'current-speed[mm/s]': focus[9],
                        ####-start-of-spindles-####
                        'spindle1-current-position[mm/deg]': focus[10],
                        'spindle1-current-target-position[mm/deg]': focus[11],
                        'spindle1-current-position-offset[mm/deg]': focus[12],
                        'spindle1-current-speed[mm/s/deg/s]': focus[13],
                        'spindle1-current-target-speed[mm/s/deg/s]': focus[14],
                        'spindle1-current-web-speed[mm/s/deg/s]': focus[15],
                        'spindle1-position-deviation[mm/deg]': focus[16],
                        'spindle1-current-utilization-of-the-spindle[%]': focus[17],
                        'spindle1-spindle-active': focus[18],
                        'spindle1-brake-open': focus[19],
                        'spindle1-general-error': focus[20],
                        # -start-of-error-structure-(5.11-in-manual)
                        'spindle1-software-emergency-stop': focus[21],
                        'spindle1-hardware-emergency-stop': focus[22],
                        'spindle1-emergency-stop-switch-up': focus[23],
                        'spindle1-emergency-limit-switch-down': focus[24],
                        'spindle1-group-error': focus[25],
                        'spindle1-brakes': focus[26],
                        'spindle1-power': focus[27],
                        'spindle1-servo-system': focus[28],
                        'spindle1-engine-timeout': focus[29],
                        'spindle1-speedometer': focus[30],
                        'spindle1-maximum-engine-speed-achieved': focus[31],
                        'spindle1-iquad_t;': focus[32],
                        'spindle1-position-encoder-hardware': focus[33],
                        'spindle1-position-encoder-step': focus[34],
                        'spindle1-position-outside-the-defined-area': focus[35],
                        'spindle1-maximum-position-deviation-reached': focus[36],
                        'spindle1-fieldbus': focus[37],
                        'spindle1-feed-back-module-servo': focus[38],
                        'spindle1-override': focus[39],
                        'spindle1-command-timeout': focus[40],
                        'spindle1-communication-error-with-host-computer': focus[
                            41],
                        'spindle1-referencescoder-is-missing': focus[42],
                        'spindle1-referencescoder-error': focus[43],
                        'spindle1-speed-governor': focus[44],
                        'spindle1-maximum-speed-deviation-achieved': focus[45],
                        'spindle1-lock': focus[46],
                        'spindle1-external-error': focus[47],
                        #  end-of-error-structure-(5.11-in-manual)
                        'spindle1-general-warning': focus[48],
                        # -start-of-warning-structure-(5.12-in-manual)
                        'spindle1-speed-mode': focus[49],
                        'spindle1_-override': focus[50],
                        'spindle1-stow-pin-in': focus[51],
                        'spindle1-parameter-error': focus[52],
                        'spindle1-power-heating': focus[53],
                        'spindle1-power-breaks': focus[54],
                        'spindle1-power-drives': focus[55],
                        'spindle1-power-external-24v': focus[56],
                        'spindle1-power-internal-24v': focus[57],
                        'spindle1-power-control': focus[58],
                        'spindle1_-position-encoder-hardware': focus[59],
                        'spindle1-engine-warning': focus[60],
                        'spindle1-mazimum-torque-achieved': focus[61],
                        'spindle1-degraded-fashion': focus[62],
                        'spindle1-security-device': focus[63],
                        'spindle1-ermaus': focus[64],
                        'spindle1-ermservo': focus[65],
                        'spindle1-emergency-limit-switch-up': focus[66],
                        'spindle1_-emergency-limit-switch-down': focus[67],
                        'spindle1-pre-limit-switch-up': focus[68],
                        'spindle1-pre-limit-switch-down': focus[69],
                        'spindle1-operating-limit-switch-up': focus[70],
                        'spindle1-operating-limit-switch-down': focus[71],
                        'spindle1-software-limit-switch-up': focus[72],
                        'spindle1-software-limit-switch-down': focus[73],
                        # -note: some-of-the-above-have-a-underscore-as-there-are
                        # -doubles-in-the-error-and-warning-stuct-with-the-same-name
                        ####
                        'spindle2-current-position[mm/deg]': focus[74],
                        'spindle2-current-target-position[mm/deg]': focus[75],
                        'spindle2-current-position-offset[mm/deg]': focus[76],
                        'spindle2-current-speed[mm/s/deg/s]': focus[77],
                        'spindle2-current-target-speed[mm/s/deg/s]': focus[78],
                        'spindle2-current-web-speed[mm/s/deg/s]': focus[79],
                        'spindle2-position-deviation[mm/deg]': focus[80],
                        'spindle2-current-utilization-of-the-spindle[%]': focus[
                            81],
                        'spindle2-spindle-active': focus[82],
                        'spindle2-brake-open': focus[83],
                        'spindle2-general-error': focus[84],
                        'spindle2-software-emergency-stop': focus[85],
                        'spindle2-hardware-emergency-stop': focus[86],
                        'spindle2-emergency-stop-switch-up': focus[87],
                        'spindle2-emergency-limit-switch-down': focus[88],
                        'spindle2-group-error': focus[89],
                        'spindle2-brakes': focus[90],
                        'spindle2-power': focus[91],
                        'spindle2-servo-system': focus[92],
                        'spindle2-engine-timeout': focus[93],
                        'spindle2-speedometer': focus[94],
                        'spindle2-maximum-engine-speed-achieved': focus[95],
                        'spindle2-iquad_t;': focus[96],
                        'spindle2-position-encoder-hardware': focus[97],
                        'spindle2-position-encoder-step': focus[98],
                        'spindle2-position-outside-the-defined-area': focus[99],
                        'spindle2-maximum-position-deviation-reached': focus[
                            100],
                        'spindle2-fieldbus': focus[101],
                        'spindle2-feed-back-module-servo': focus[102],
                        'spindle2-override': focus[103],
                        'spindle2-command-timeout': focus[104],
                        'spindle2-communication-error-with-host-computer': focus[
                            105],
                        'spindle2-referencescoder-is-missing': focus[106],
                        'spindle2-referencescoder-error': focus[107],
                        'spindle2-speed-governor': focus[108],
                        'spindle2-maximum-speed-deviation-achieved': focus[109],
                        'spindle2-lock': focus[110],
                        'spindle2-external-error': focus[111],
                        'spindle2-general-warning': focus[112],
                        'spindle2-speed-mode': focus[113],
                        'spindle2_-override': focus[114],
                        'spindle2-stow-pin-in': focus[115],
                        'spindle2-parameter-error': focus[116],
                        'spindle2-power-heating': focus[117],
                        'spindle2-power-breaks': focus[118],
                        'spindle2-power-drives': focus[119],
                        'spindle2-power-external-24v': focus[120],
                        'spindle2-power-internal-24v': focus[121],
                        'spindle2-power-control': focus[122],
                        'spindle2_-position-encoder-hardware': focus[123],
                        'spindle2-engine-warning': focus[124],
                        'spindle2-mazimum-torque-achieved': focus[125],
                        'spindle2-degraded-fashion': focus[126],
                        'spindle2-security-device': focus[127],
                        'spindle2-ermaus': focus[128],
                        'spindle2-ermservo': focus[129],
                        'spindle2-emergency-limit-switch-up': focus[130],
                        'spindle2_-emergency-limit-switch-down': focus[131],
                        'spindle2-pre-limit-switch-up': focus[132],
                        'spindle2-pre-limit-switch-down': focus[133],
                        'spindle2-operating-limit-switch-up': focus[134],
                        'spindle2-operating-limit-switch-down': focus[135],
                        'spindle2-software-limit-switch-up': focus[136],
                        'spindle2-software-limit-switch-down': focus[137],
                        'last-sent-mode-command': focus[138],
                        'command-response-of-the-mode-command': focus[139],
                        'target-position-of-the-mode-command': focus[140],
                        'target-speed-of-the-mode-command': focus[141],
                        'last-sent-parameter-command': focus[142],
                        'command-response-of-the-parameter-command': focus[143],
                        'parameter 1 of the parameter command': focus[144],
                        'parameter-2-of-the-parameter-command': focus[145],
                    },

                
                # 'engine':
                #     {
                #         'engine': polar[0],
                #         'engine': polar[1],
                #         'engine': polar[2],
                #         'engine': polar[3],
                #         'engine': polar[4],
                #         'engine': polar[5],
                #         'engine': polar[6],
                #         'engine': polar[7],
                #         'engine': polar[8],
                #         'engine': polar[9],
                #         'engine': polar[10],
                #         'engine': polar[11],
                #         'engine': polar[12],
                #         'engine': polar[13],
                #         'engine': polar[14],
                #         'engine': polar[15],
                #         'engine': polar[16],
                #         'engine': polar[17],
                #         'engine': polar[18],
                #         'engine': polar[19],
                #         'engine': polar[20],
                #         'engine': polar[21],
                #         'engine': polar[22],
                #         'engine': polar[23],
                #         'engine': polar[24],
                #         'engine': polar[25],
                #         'engine': polar[26],
                #         'engine': polar[27],
                #         'engine': polar[28],
                #         'engine': polar[29],
                #         'engine': polar[30],
                #         'engine': polar[31],
                #         'engine': polar[32],
                #         'engine': polar[33],
                #         'engine': polar[34],
                #         'engine': polar[35],
                #         'engine': polar[36],
                #         'engine': polar[37],
                #         'engine': polar[38],
                #         'engine': polar[39],
                #         'engine': polar[40],
                #         'engine': polar[41],
                #         'engine': polar[42],
                #         'engine': polar[43],
                #         'engine': polar[44],
                #         'engine': polar[45],
                #         'engine': polar[46],
                #         'engine': polar[47],
                #         'unknown1': polar[48],
                #         'unknown2': polar[49],
                #         'unknown3': polar[50],
                #         'unknown4': polar[51],
                #         'unknown5': polar[52],
                #         'unknown6': polar[53],
                #         'unknown7': polar[54],
                #         'unknown8': polar[55],
                #         'unknown9': polar[56],
                #         'unknown10': polar[57],
                #         'unknown11': polar[58],
                #         'unknown12': polar[59],
                #         'unknown13': polar[60],
                #         'unknown14': polar[61],
                #         'unknown15': polar[62],
                #         'unknown16': polar[63],
                #         'unknown17': polar[64],
                #         'unknown18': polar[65],
                #         'unknown19': polar[66],
                #         'unknown20': polar[67],
                #         'unknown21': polar[68],
                #         'unknown22': polar[69],
                #         'unknown23': polar[70],
                #         'unknown24': polar[71],
                #         'unknown25': polar[72],
                #         'unknown26': polar[73],
                #         'unknown27': polar[74],
                #         'unknown28': polar[75],
                #         'unknown29': polar[76],
                #         'unknown30': polar[77],
                #         'unknown31': polar[78],
                #         'unknown32': polar[79],
                #         'unknown33': polar[80],
                #         'unknown34': polar[81],
                #         'unknown35': polar[82],
                #         'unknown36': polar[83],
                #         'unknown37': polar[84],
                #         'unknown38': polar[85],
                #         'unknown39': polar[86],
                #         'unknown40': polar[87],
                #         'unknown41': polar[88],
                #         'unknown42': polar[89],
                #         'unknown43': polar[90],
                #         'unknown44': polar[91],
                #         'unknown45': polar[92],
                #         'unknown46': polar[93],
                #         'unknown47': polar[94],
                #         'unknown48': polar[95],
                #         'unknown49': polar[96],
                #         'unknown50': polar[97],
                #         'unknown51': polar[98],
                #         'unknown52': polar[99],
                #         'unknown53': polar[100],
                #         'unknown54': polar[101],
                #         'unknown55': polar[102],
                #         'unknown56': polar[102],
                #         'unknown57': polar[104],
                #         'unknown58': polar[105],
                #         'unknown59': polar[106],
                #         'unknown60': polar[107],
                #         'unknown61': polar[108],
                #         'unknown62': polar[109],
                #         'unknown63': polar[110],
                #         'unknown64': polar[111],
                #         'unknown65': polar[112],
                #         'unknown66': polar[113],
                #         'unknown67': polar[114],
                #         'unknown68': polar[115],
                #         'unknown69': polar[116],
                #     },
            }

            full_msg = b''

            # structurevaluenames = \
            #     [
            #         'current-position[mm/deg]',
            #         'current-target-position[mm/deg]',
            #         'current-position offset[mm/deg]',
            #         'current-speed[mm/s/deg/s]',
            #         'current-target speed[mm/s/deg/s]',
            #         'current-web speed[mm/s/deg/s]',
            #         'position-deviation[mm/deg]',
            #         'current-utilization-of-the-spindle[%]',
            #         'spindle-active',
            #         'brake-open',
            #         'general-error',
            #         # Start of error structure (5.11 in manual)
            #         'software-emergency-stop',
            #         'hardware-emergency-stop',
            #         'emergency-stop-switch-up',
            #         'emergency-limit-switch-down',
            #         'group-error',
            #         'brakes',
            #         'power',
            #         'servo-system',
            #         'engine-timeout',
            #         'speedometer',
            #         'maximum-engine-speed-achieved',
            #         'iquad_t;',
            #         'position-encoder-hardware',
            #         'position-encoder-step',
            #         'position-outside-the-defined-area',
            #         'maximum-position-deviation-reached',
            #         'fieldbus',
            #         'feed-back-module-servo',
            #         'override',
            #         'command-timeout',
            #         'communication-error-with-host-computer',
            #         'referencescoder-is-missing',
            #         'referencescoder-error',
            #         'speed-governor',
            #         'maximum-speed-deviation-achieved',
            #         'lock',
            #         'external-error',
            #         #  End of error structure (5.11 in manual)
            #         'general-warning',
            #         # Start of warning structure (5.12 in manual)
            #         'speed-mode',
            #         'override',
            #         'stow-pin-in',
            #         'parameter-error',
            #         'power-heating',
            #         'power-breaks',
            #         'power-drives',
            #         'power-external-24v',
            #         'power-internal-24v',
            #         'power-control',
            #         'position-encoder-hardware',
            #         'engine-warning',
            #         'mazimum-torque-achieved',
            #         'degraded-fashion',
            #         'security-device',
            #         'ermaus',
            #         'ermservo',
            #         'emergency-limit-switch-up',
            #         'emergency-limit-switch-down',
            #         'pre-limit-switch-up',
            #         'pre-limit-switch-down',
            #         'operating-limit-switch-up',
            #         'operating-limit-switch-down',
            #         'software-limit-switch-up',
            #         'software-limit-switch-down',
            #         # end of warning structure (5.12 in manual)
            #     ]
            #
            # spindle1 = {}
            # spindle2 = {}
            # spindle3 = {}
            # spindle4 = {}
            # spindle5 = {}
            # spindle6 = {}
            # ending = {}
            # spindles = [spindle1, spindle2, spindle3,
            #             spindle4, spindle5, spindle6]
            # # make 3 empty dicts for the 6 spindles
            # for spin in range(len(spindles)):  # spin between 0 and 5 inclusive
            #     for n in range(len(structurevaluenames)):  # 0 and 64 inclusive
            #
            #         # 13 entries are before the spindles, n+1 fixed startpoint
            #         # Spin * len(structurevaluenames) gives multiple of 64
            #         index = 33 + (n+1) + (spin*len(structurevaluenames))
            #
            #         # For each spindle, add entries that say spindle number,
            #         # take the structurevaluename, and the correct index of hxpd
            #         spindles[spin][f'spindle{spin+1}-n={index}-{structurevaluenames[n]}'] = hxpd[index]
            #
            # print(spindle1)
            #
            # spindle1x = json.dumps(spindle6, indent=2)
            # print(spindle1x)
            # # print(spindle2)
            # # print(spindle3)
            # # print(spindle4)
            # # print(spindle5)
            # # print(spindle6)
            #
            # # These need to be appended to the dict, but




            humandataa = json.dumps(humanData, indent=2)
            # print(humandataa)
            # print(humanData)
            # print(f"humanData is type: {type(humanData)}")
            # humanstring = json.loads(humanData)
            # print(f"humanstring is type: {type(humanstring)}")
            # backtodict = json.dumps(humanData)
            # print(f"backtodict maybe is type {type(humanData)}")

            # print(humanstring['Status data Interlock'])
            # print(humanstring['Status data Interlock'][0][0])
            # print(humanstring['Status data Interlock']['Active control unit'])
            # print(humanstring['Power'])
            # print("TEST")
            # j = json.dumps(header)
            # print(type(j), j)
            # s = json.loads(j)
            # print(type(s), s)

if __name__ == '__main__':
    mainn()
