# # # Python code to demonstrate
# # # converting string to json
# # # using json.loads
# # import json
# #
# # # inititialising json object
# # ini_string = {'nikhil': (1, 3), 'akash': [5, [4, 5], ["str"]],
# #               'manjeet': "string", 'akshat': 15}
# # print(type(ini_string))
# # # printing initial json
# # ini_string = json.dumps(ini_string)
# # print("initial 1st dictionary", ini_string)
# # print("type of ini_object", type(ini_string))
# #
# # # converting string to json
# # final_dictionary = json.loads(ini_string)
# #
# # # printing final result
# # print("final dictionary", str(final_dictionary))
# # print("type of final_dictionary", type(final_dictionary))
# # print(final_dictionary['nikhil'])
# #
# #
# #
# # # humanData = json.loads(json.dumps({
# # #     'people': [
# # #         {
# # #             'Name': 'Ivan Sharankov',
# # #             'Age': 21,
# # #             'Height': 190,
# # #             'Weight': 78.5,
# # #             'Active': True,
# # #             'Balance': 100_000,
# # #         },
# # #         {
# # #             'Name': 'Alex Mechev',
# # #             'Age': 30,
# # #             'Height': 181,
# # #             'Weight': 70.5,
# # #             'Active': False,
# # #             'Balance': 1000
# # #         }
# # #     ]
# # # }, indent=2))
# #
# #!/usr/bin/env python
#
# import time
# import json
# import socket
# import struct
# import pickle
# from astropy.time import Time
#
# # SUBREF_ADDR = ***REMOVED***
# SUBREF_ADDR = '***REMOVED***'
# SUBREF_PORT = ***REMOVED***
#
#
#
# def main():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.connect((SUBREF_ADDR, SUBREF_PORT))
#     full_msg = b''
#     counter = 0
#     while 1:
#         print("in loop")
#         data = sock.recv(400000)
#         print("data received", len(data))
#         print(data)
#         # if counter == 0:
#         #     counter += 1
#         # else:
#         #
#         #     full_msg += bytearray(data)
#         #     # full_msg += data
#         #
#         #     if len(full_msg) >= 1760:
#         #         pickle.dump(full_msg, open("sept30pickled_data.p", "ab"))
#         #         print("pickled")
#
# if __name__ == "__main__":
#     main()


from ctypes import *

class Example(Structure):
    _fields_ = [
        ("index", c_int),
        ("counter", c_int),
        ]

def Pack(ctype_instance):
    buf = string_at(byref(ctype_instance), sizeof(ctype_instance))
    return buf

# def Unpack(ctype, buf):
#     cstring = create_string_buffer(buf)
#     ctype_instance = cast(pointer(cstring), POINTER(ctype)).contents
#     return ctype_instance

if __name__ == "__main__":
    e = Example(12, 13)
    buf = Pack(e)
    print(buf)
    # e2 = Unpack(Example, buf)
    # assert(e.index == e2.index)
    # assert(e.counter == e2.counter)
    # note: for some reason e == e2 is False..