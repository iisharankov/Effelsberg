import socket
import time

from subtools import subreflector_start_server, mock_start_server, process_message, config

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(4)

        # This block offers user to choose the IP/Port combo, and makes sure a
        # connection is made to the specified combo
        address, port = None, None
        while port is None:
            try:
                address = input("Specify the address (empty or zero for local): ")
                port = int(input("Specify port (see users_manual for defaults): "))
                assert port > 1024 and port < 65535

                destination_address = (address, port)

                if address in ['', '127.0.0.1']:
                    ask_user_between_test_and_real_server()


                sock.sendto(str.encode("\n"), destination_address)
                process_message.recv_msg(sock)


            except AssertionError as E:
                port = None
                print("port should be between 1024 and 65535, "
                      "lower values reserved (except 0)")
                print(E)

            except OSError as E:
                port = None
                print(f"OSError occured: {E}")

        while True:
            time.sleep(0.1)
            data = input("What to send: ")

            # Connect to server and send data
            sock.sendto(str.encode(data), destination_address)
            print("Sent:     {}".format(data))

            process_message.recv_msg(sock)


def ask_user_between_test_and_real_server():

    while True:
        answer = input(
            'Would you like to connect to the real MT subreflector (see users'
            'manual for IP) or start a local instance of a Mock Subreflector '
            'that mimics basic functionality (best for testing or when you '
            'are not connected to the real subreflector)? Type "real" for a '
            'real connection, and "mock" or "test" for the local subreflector ')

        answer = answer.lower().strip().replace(' ', '')

        if answer == "real":
            subreflector_start_server.main()
            # config.USE_TEST_SERVER = False  # Todo, make a way to change this var?
            break

        elif answer == 'mock' or answer == 'test':
            mock_start_server.main()
            subreflector_start_server.main()
            break

        else:
            print('Sorry, the input must be "test", "mock" or "real"')
            continue

if __name__ == '__main__':
    main()

























