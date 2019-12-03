# load additional Python module
import socket
import json
import time

# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# retrieve local hostname
local_hostname = socket.gethostname()

# get the according IP address
ip_address = socket.gethostbyname(local_hostname)

# output hostname, domain name and IP address
print("working on %s with %s" % (local_hostname, ip_address))

# bind the socket to the port
server_address = ('', 0)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

# listen for incoming connections (server mode) with one connection at a time
sock.listen(1)
flag = True
short = 'o' * 736
long = "o" * ***REMOVED***
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
            if flag:
                connection.send(str.encode(short))
                time.sleep(1)
                connection.send(str.encode(long))
                time.sleep(1)
                connection.send(str.encode(short))
                time.sleep(1)
                connection.send(str.encode(long))
                time.sleep(1)



            # data = connection.recv(100_000)
            # # print(data)
            # if data:
            #     # output received data
            #     # msg += str(data)
            #     #test
            #     print(f"data: {data.decode()}")
            #     connection.send(("Got the data").encode('utf-8'))
            #     print("REACHED")
            # else:
            #     # print(msg)
            #     # no more data -- quit the loop
            #     print("no more data.")
            #     break
    except:
        # Clean up the connection
        # connection.close()
        pass