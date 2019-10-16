# load additional Python module
import socket
import json

# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# retrieve local hostname
local_hostname = socket.gethostname()

# get the according IP address
ip_address = socket.gethostbyname(local_hostname)

# output hostname, domain name and IP address
print("working on %s with %s" % (local_hostname, ip_address))

# bind the socket to the port 23456
server_address = ('***REMOVED***', ***REMOVED***)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

# listen for incoming connections (server mode) with one connection at a time
sock.listen(1)

while True:
    # wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()

    try:
        # show who connected to us
        print("connection from", client_address)
        msg = ""
        # receive the data in small chunks and print it
        while True:

            data = connection.recv(100_000)
            if data:
                # output received data
                # msg += str(data)
                #test
                print("Data")
                print(data)
            else:
                # print(msg)
                # no more data -- quit the loop
                print("no more data.")
                break
    finally:
        # Clean up the connection
        connection.close()