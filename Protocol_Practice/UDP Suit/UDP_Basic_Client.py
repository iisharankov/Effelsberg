import socket
import time

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    destination_address = ('', ***REMOVED***)
    sock.settimeout(2)

    while True:
        time.sleep(0.001)
        data = input("What to send: ")

        # Connect to server and send dataEFFELSBERG:MTSUBREFLECTOR:RESETCONNECTION
        sock.sendto(str.encode(data), destination_address)
        print("Sent:     {}".format(data))

        # Receive data from the server
        try:
            received = sock.recv(***REMOVED***)
            print("Received: {}".format(received.decode('utf-8')))
        except socket.timeout:
            print("Socket timed out, Try again")



























