import socket
import sys

HOST, PORT = "localhost", 9999

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

flag = True
while flag:
    data = input("What do you want to send to the Server?")

    if data.lower() == "close":
        flag = False
        break

    # Connect to server and send data
    sock.sendall(str.encode(data + "\n"))

    # Receive data from the server
    received = sock.recv(***REMOVED***)
    print("Sent:     {}".format(data))
    print("Received: {}".format(received.decode('utf-8')))

sock.close()
