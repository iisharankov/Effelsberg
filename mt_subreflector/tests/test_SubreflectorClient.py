import socketserver
import threading
import logging
import pytest
import socket
import struct
import time
import json
import os
import asyncio


from mt_subreflector import subreflector_client
print("Erf")
class TestSubreflectorClient:
    pass
    # def test_dummy_tcp_server(self):
    #     start_client = SubreflectorClient.SubreflectorClient(True)
    #     with start_client as example_server:
    #         thread = threading.Thread(target=example_server.listen_for_traffic)
    #         thread.deamon = True
    #         thread.start()
    #         print("re")
    #         return example_server
    # #
    # def test_example(self):
    #     HOST = '***REMOVED***'
    #     PORT = ***REMOVED***
    #     data = ""
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.connect((HOST, PORT))
    #         s.send(b'\n')
    #         data = s.recv(***REMOVED***)
    #         # print(data)
    #     assert data
    #
    # def test_one(self):
    #     c = 1
    #     assert c == 1

    # async def echo_server(self, reader, writer):
    #     while True:
    #         data = await reader.read(100)  # Max number of bytes to read
    #         if not data:
    #             break
    #         writer.write(data)
    #         await writer.drain()  # Flow control, see later
    #     writer.close()
    #
    #     async def main(self, host, port):
    #         self.server = await asyncio.start_server(self.echo_server, host, port)
    #
    #     await self.server.serve_forever()
    #     asyncio.run(main('***REMOVED***', ***REMOVED***))



        # assert start_client.chosen_server == ('***REMOVED***', ***REMOVED***)

        # # Start game server in a background thread
        # server = SubreflectorClient.main()
        # server_thread = threading.Thread(target=server.start_listening)
        # server_thread.start()
        #
        # # On my computer, 0.0000001 is the minimum sleep time or the
        # # client might connect before server thread binds and listens
        # # other computers will differ.
        # time.sleep(0.00001)
        #
        # # This is our fake test client that is just going to attempt
        # # a connect and disconnect
        # fake_client = socket.socket()
        # fake_client.settimeout(1)
        # fake_client.connect(('***REMOVED***', 7777))
        # fake_client.close()
        #
        # # Make sure server thread finishes
        # server_thread.join()

class EchoProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.transport.write(data)

async def main(host, port):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(EchoProtocol, host, port)
    await server.serve_forever()
asyncio.run(main('***REMOVED***', ***REMOVED***))
