import socket
import time
import logging

from subtools import subreflector_start_server, mock_start_server, process_message, config

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)

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
            try:
                data = input("What to send: ")


                # Connect to server and send data
                sock.sendto(str.encode(data), destination_address)

                #TODO: Not the best implementation, TRY AGAIN
                newlist = []
                for i in range(2):
                    received_messages = process_message.recv_msg(sock, False)
                    print(received_messages)
                    sock.settimeout(0.5)
                    if not received_messages is None:
                        newlist = received_messages
                        # print(newlist)

                for i in newlist:
                    print(f"Received: {i}")

            except Exception as E:
                logging.exception("There was an exception")
            #
            # except TimeoutError:
            #     print("SOCKET TIMEOUT REACHED")
            #     logging.debug("SOCKET.TIMEOUT REACHED")
            #     process_message.recv_msg(sock, True)




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
            subreflector_start_server.main(False)

            break

        elif answer == 'mock' or answer == 'test':
            mock_start_server.main()
            subreflector_start_server.main(True)
            break

        else:
            print('Sorry, the input must be "test", "mock" or "real"')
            continue

if __name__ == '__main__':
    main()

























