import socket
import time
import json
humanData = {}
# get the local IP address
localIP = socket.gethostbyname(socket.gethostname())
buffersize = 8192
port = 12345

# Create a UDP socket on the client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Sends message to Server using the UDP socket
bytesToSend = str.encode("Hello UDP Server, I and a UDP Client")
UDPClientSocket.sendto(bytesToSend, (localIP, port))

# Waits for initialized response from Server, before going in while loop
msgFromServer = UDPClientSocket.recvfrom(buffersize)
msg = "Message from Server: {}".format(msgFromServer[0].decode())
print(msg)

# While loop for user to continuously send messages to Server
flag = True
while flag:

    userReply = input("Type 'Yes' to send JSON package, 'No' to send "
                      "another message, or 'Close' to close the socket ")

    # If user inputs a message, it is sent to the Server
    if userReply.lower() == 'yes':
        print('Sending JSON file to the server')
        userJSONMessage =  json.dumps(humanData)
        UDPClientSocket.sendto(str.encode(userJSONMessage), (localIP, 12345))
        # Checks if a return message was received from Server and decodes it
        # serverResponse = UDPClientSocket.recvfrom(buffersize)
        # NewMsgFromServer = serverResponse[0].decode('utf-8')



    elif userReply.lower() == 'no':
        newMessage = input("What would you like to say to the server? Enter "
                           "nothing to return back to resend JSON file")

        UDPClientSocket.sendto(str.encode(newMessage), (localIP, 12345))

        # Checks if a return message was received from Server and decodes it
        serverResponse = UDPClientSocket.recvfrom(buffersize)
        NewMsgFromServer = serverResponse[0].decode('utf-8')

        # "No Reply" is used since IDK how to have the Server not send a message
        # back for certain messages without the Client hanging and waiting forever
        if NewMsgFromServer == "No Reply":
            print("no server reply")
            pass  # If "no reply", then client knows to ignore waiting 4 a reply
        else:
            msg = "Message from Server: {}".format(NewMsgFromServer)
            print(msg)  # Otherwise the message is of importance and printed

    elif userReply.lower() == 'close':
        print("Closing connection to server")
        flag = False

UDPClientSocket.close()





