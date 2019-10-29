import socketserver
import threading
import logging
import socket
import struct
import time
import json
import os

from mt_subreflector import subreflector_program

class TestSubreflectorProgram:
    def test_game_server_starts_tcp_server(self):
        # Start game server in a background thread
        server = subreflector_program.main()
        server_thread = threading.Thread(target=server.start_listening)
        server_thread.start()

        # On my computer, 0.0000001 is the minimum sleep time or the
        # client might connect before server thread binds and listens
        # other computers will differ.
        time.sleep(0.00001)

        # This is our fake test client that is just going to attempt
        # a connect and disconnect
        fake_client = socket.socket()
        fake_client.settimeout(1)
        fake_client.connect(('***REMOVED***', 7777))
        fake_client.close()

        # Make sure server thread finishes
        server_thread.join()



# def run_fake_server(self):
#     # Run a server to listen for a connection and then close it
#     with socket.socket() as server_sock:
#         server_sock.bind(('***REMOVED***', 7777))
#         server_sock.listen(0)
#         server_sock.accept()
#         server_sock.close()