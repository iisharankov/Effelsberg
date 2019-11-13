import socket
import time

def recv_msg(sock):
    # Receive data from the server
    try:
        received = sock.recv(***REMOVED***)
        print("Received: {}".format(received.decode('utf-8')))
    except socket.timeout:
        print("Socket timed out, Try again")

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    address = input("Specify the address (empty for local): ")
    port = int(input("Specify port (***REMOVED*** is default for SR_program): "))
    destination_address = (address, port)
    sock.settimeout(4)

    sock.sendto(str.encode("\n"), destination_address)
    recv_msg(sock)

    while True:
        time.sleep(0.001)
        data = input("What to send: ")

        # Connect to server and send dataEFFELSBERG:MTSUBREFLECTOR:RESETCONNECTION
        sock.sendto(str.encode(data), destination_address)
        print("Sent:     {}".format(data))

        recv_msg(sock)



























