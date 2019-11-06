# # import socketserver
# #
# #
# # class EchoRequestHandler(socketserver.BaseRequestHandler):
# #
# #     def handle(self):
# #         # Echo the back to the client
# #         data = self.request.recv(***REMOVED***)
# #         self.request.send(data)
# #         return
# #
# #
# # if __name__ == '__main__':
# #     import socket
# #     import threading
# #
# #     address = ('localhost', 0)  # let the kernel assign a port
# #     server = socketserver.TCPServer(address, EchoRequestHandler)
# #     ip, port = server.server_address  # what port was assigned?
# #     print("e")
# #     t = threading.Thread(target=server.serve_forever)
# #     print("43")
# #     t.setDaemon(True)  # don't hang on exit
# #     t.start()
# #
# #     # # Connect to the server
# #     # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #     # s.connect((ip, port))
# #     #
# #     # # Send the data
# #     # message = 'Hello, world'.encode()
# #     # print('Sending : {!r}'.format(message))
# #     # len_sent = s.send(message)
# #     #
# #     # # Receive a response
# #     # response = s.recv(len_sent)
# #     # print('Received: {!r}'.format(response))
# #     #
# #     # # Clean up
# #     # server.shutdown()
# #     # s.close()
# #     # server.socket.close()
#
#
# import threading
# import time
# import socketserver
# import socket
# import logging
#
# class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
#     pass
#
# # Communication class
# class MyUDPHandler(socketserver.BaseRequestHandler):
#
#     def handle(self):
#         # self.request is the UDP connected to the client
#         # takes message, decodes to string and - all whitespace (by rejoining)
#         telnet_msg = ''.join(self.request[0].decode('utf-8').lower().split())
#
#         # command = TelnetCommandParser(telnet_msg)
#         # msg = command.return_message()
#         msg = "yeS"
#
#         # Message to return to client
#         # print(f"Sending message: {msg}")
#
#         returnsocket = self.request[1]
#         returnsocket.sendto(msg.encode(), self.client_address)
#
#
# UDPTELNET_PORT = ***REMOVED***
# LOCAL_ADDRESS = '***REMOVED***'  # My personal IP atm
# dest_address = (LOCAL_ADDRESS, UDPTELNET_PORT)
#
# class ThreadingExample(object):
#     """ Threading example class
#     The run() method will be started and it will run in the background
#     until the application exits.
#     """
#
#     def __init__(self):
#         """ Constructor
#         :type interval: int
#         """
#         thread = threading.Thread(target=self.run, args=())
#         thread.daemon = False                            # Daemonize thread
#         thread.start()                                  # Start the execution
#
#     def run(self):
#         """ Method that runs forever """
#         self.server = ThreadingUDPServer(dest_address, MyUDPHandler)
#         while True:
#             # Do something
#             t = threading.Thread(target=self.server.serve_forever)
#             print("reached")
#             t.setDaemon(True)  # don't hang on exit
#             t.start()
#             t.join()
#             print("reace")
#
# example = ThreadingExample()
# time.sleep(3)
# print('Checkpoint')
# time.sleep(2)
# print('Bye')


import time
import os
import sys

# for i in range(10):
#     sys.stdout.write("%07d" % i)
#     # os.system('clear')
#     # print(i)
#     time.sleep(0.5)
for n in range(1, 11):

    if n != 10:
        print('\rI am on number {} of 10'.format(n), end='')
    else:
        print('\rI am on number {} of 10'.format(n))

    time.sleep(.5)