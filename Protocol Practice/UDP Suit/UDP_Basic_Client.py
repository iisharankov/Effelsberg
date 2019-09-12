import socket
import time

# get the local IP address
localIP = socket.gethostbyname(socket.gethostname())
buffersize = ***REMOVED***

# Create a UDP socket on the client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Sends message to Server using the UDP socket
bytesToSend = str.encode("Hello UDP Server, I and a UDP Client")
UDPClientSocket.sendto(bytesToSend, (localIP, 12345))

# Waits for initialized response from Server, before going in while loop
msgFromServer = UDPClientSocket.recvfrom(buffersize)
msg = "Message from Server: {}".format(msgFromServer[0])
print(msg)

# While loop for user to continuously send messages to Server
while True:

    userReply = input("Please enter a message to send to the server: ")

    # If user inputs a message, it is sent to the Server
    if userReply:
        UDPClientSocket.sendto(str.encode(userReply), (localIP, 12345))

        # Checks if a return message was received from Server and decodes it
        serverResponse = UDPClientSocket.recvfrom(buffersize)
        NewMsgFromServer = serverResponse[0].decode('utf-8')

        # "No Reply" is used since IDK how to have the Server not send a message
        # back for certain messages without the Client hanging and waiting forever
        if NewMsgFromServer == "No Reply":
            pass  # If "no reply", then client knows to ignore waiting 4 a reply
        else:
            msg = "Message from Server: {}".format(NewMsgFromServer)
            print(msg)  # Otherwise the message is of importance and printed

    else:
        print("You did not enter any message")



