# #!/usr/bin/env python
#
# import socket
# # import MTCommand
#
#
# SUBREF_ADDR = "***REMOVED***"
# SUBREF_MONPORT = 9000
# SUBREF_COMPORT = ***REMOVED***
#
# #sockcom = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #sockcom.connect((SUBREF_ADDR,SUBREF_COMPORT))
#
# sockcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sockcon.connect((SUBREF_ADDR,SUBREF_COMPORT))
# sockcon.send(b"\n")
#
# while 1:
#     data = sockcon.recv(1760)
#     print(data)
#     print("data received",len(data))
#     if len(data)<1760 :
#         data = data + sockcon.recv(1760-len(data))
#         print("all data received",len(data))
#         break
#
# """
# take the output and look into the datastream
# FOR SERVER
# in translated file, buts be a description of the data stream
# should create out of this multicast
# read it out and create a multicast message as a json with all the  mjulddata
#
#
# """

