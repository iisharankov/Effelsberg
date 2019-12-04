import asyncio
import time


async def helpp():
    # print("er")
    while True:
        await asyncio.sleep(1)
        print(time.time())

class EchoServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        print('Send %r to %s' % (message, addr))
        self.transport.sendto(data + b' back!', addr)

loop = asyncio.get_event_loop()
print("Starting UDP server")
# One protocol instance will be created to serve all client requests
listen = loop.create_datagram_endpoint(
    EchoServerProtocol, local_addr=('', 0))
transport, protocol = loop.run_until_complete(listen)

try:
    # cors = asyncio.wait(helpp())
    # loop.run_until_complete(cors)

    # asyncio.run(helpp())
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()


