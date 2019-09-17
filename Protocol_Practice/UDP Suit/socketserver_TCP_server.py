import socketserver


class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.


    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def setup(self):
        print("Incoming message")

    def handle(self):
        # self.request is the UDP connected to the client
        self.data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        print(self.data.decode('utf-8'))
        # just send back the same data, but upper-cased
        socket.sendto(self.data.upper(), self.client_address)


    def finish(self):
        print("End of message.")


if __name__ == "__main__":
    destination_address = ('134.104.73.74', ***REMOVED***)
    # destination_address = ('localhost', 9999)

    # Create the server, binding to localhost on port 9999
    server = socketserver.UDPServer(destination_address, MyUDPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()