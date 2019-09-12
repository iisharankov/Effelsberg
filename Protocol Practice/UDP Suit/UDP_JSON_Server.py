import socket
import json

# get the according IP address
localIP = socket.gethostbyname(socket.gethostname())

# Sets the port and buffer size as constants for later use
bufferSize = 8192
port = 12345

# Create a datagram Socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, port))
print("UDP server up and is listening for a client to connect")


# Listen for incoming arguments
firstMsg = True
while True:
    # while True:
    # Receives and decodes the messaged given by the client
    message, address = UDPServerSocket.recvfrom(bufferSize)
    decodedmessage = (message.decode('utf-8'))

    try:
        jsonmessage = json.loads(decodedmessage)
        print("JSON message discovered!")
        isJSONMsg = True
        print(json.dumps(jsonmessage, indent=4))
        UDPServerSocket.close()
        break
    # If exception is made, it means whatever was recieved was not a JSON string
    except json.decoder.JSONDecodeError:
        isJSONMsg = False

        print("New message from client from "
              "port {}: {}".format(address[1], decodedmessage))

        # Checks if message received matches, if so, replies.

        if firstMsg:
            # Sends priliminary reply to the Client
            firstMsgcontents = str.encode("Hello UDP Client, I am a UDP Server")
            UDPServerSocket.sendto(firstMsgcontents, address)
            firstMsg = False  # sets to false to never send again during connection
        elif decodedmessage == "Hello World":
            print("Client said 'Hello World!'")
            returnmessage = str.encode("Hello back!")
            UDPServerSocket.sendto(returnmessage, address)

        elif len(decodedmessage) >= 8:
            print("Client message was long")
            returnmessage = str.encode("You wrote a lot")
            UDPServerSocket.sendto(returnmessage, address)

        elif len(decodedmessage) <= 8:
            print("Client message was short")
            returnmessage = str.encode("Is that all you can write?")
            UDPServerSocket.sendto(returnmessage, address)

        # If no message of importance recieved, No Reply sent (Client disposes it)
        else:
            returnmessage = str.encode("No Reply")
            UDPServerSocket.sendto(returnmessage, address)




