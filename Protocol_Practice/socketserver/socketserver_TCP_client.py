import socket
import sys

destination_address = ('localhost', 9999)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

flag = True
while flag:
    data = input("What do you want to send to the Server?")

    if data.lower() == "close":
        flag = False
        print("closing client")
        break

    # Connect to server and send data
    sock.sendto(str.encode(data + "\n"), destination_address)

    # Receive data from the server
    received = sock.recv(***REMOVED***)
    print("Sent:     {}".format(data))
    print("Received: {}".format(received.decode('utf-8')))

sock.close()
