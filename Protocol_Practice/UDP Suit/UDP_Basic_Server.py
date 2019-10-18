import socket

# get the according IP address
localIP = socket.gethostbyname(socket.gethostname())

# Sets the port and buffer size as constants for later use
bufferSize = ***REMOVED***
port = 12345

# Create a datagram Socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, port))
print("UDP server up and is listening for a client to connect")

# Listen for incoming arguments
firstMsg = True
while True:

    # Receives and decodes the messaged given by the client
    message, address = UDPServerSocket.recvfrom(bufferSize)
    decodedmessage = message.decode('utf-8')

    print("New message from client from "
          "port {}: {}".format(address[1], decodedmessage))

    # Sends priliminary reply to the Client
    if firstMsg:
        firstMsgcontents = str.encode("Hello UDP Client, I am a UDP Server")
        UDPServerSocket.sendto(firstMsgcontents, address)
        firstMsg = False  # sets to false to never send again during connection

    # Checks if message received matches, if so, replies.
    elif decodedmessage == "Hello World":
        print("Client said 'Hello World!'")
        returnmessage = str.encode("Hello back!")

        # Replies with message
        UDPServerSocket.sendto(returnmessage, address)
    elif len(decodedmessage) <= 8:
        print("Client message was short")
        returnmessage = str.encode("Is that all you can bother to write?")

        UDPServerSocket.sendto(returnmessage, address)

    # If no message of importance recieved, No Reply sent (Client disposes it)
    else:
        returnmessage = str.encode("No Reply")
        UDPServerSocket.sendto(returnmessage, address)

