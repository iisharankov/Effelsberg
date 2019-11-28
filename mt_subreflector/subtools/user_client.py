import socket
import time

def recv_msg(sock):
    # Receive data from the server
    try:
        # received = sock.recv(***REMOVED***)
        # print("Received: {}".format(received.decode('utf-8')))
        messages = []
        while True:
            received = sock.recv(***REMOVED***)
            time.sleep(0.1)
            if received != b'\nend':
                messages.append(received.decode('utf-8'))
                print(f"Received: {received.decode('utf-8')}")
            else:
                break

    except socket.timeout:
        print("Socket timed out, Try again")

    else:
        return messages


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(4)

        # This block offers user to choose the IP/Port combo, and makes sure a
        # connection is made to the specified combo
        address, port = None, None
        while port is None:
            try:
                address = input("Specify the address (empty or zero for local): ")
                port = int(input("Specify port (default for SR_program: ***REMOVED***): "))
                assert port > ***REMOVED*** and port < 65535

                destination_address = (address, port)
                sock.sendto(str.encode("\n"), destination_address)
                initial_msg = recv_msg(sock)

            except AssertionError as E:
                port = None
                print("port should be between ***REMOVED*** and 65535, "
                      "lower values reserved (except 0)")
                print(E)

            except OSError as e:
                port = None
                print(f"OSError occured: {e}")

        while True:
            time.sleep(0.1)
            data = input("What to send: ")

            # Connect to server and send data
            sock.sendto(str.encode(data), destination_address)
            print("Sent:     {}".format(data))

            recv_msg(sock)

if __name__ == '__main__':
    main()

























