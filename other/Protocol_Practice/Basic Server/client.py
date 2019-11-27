# load additional Python modules
import socket
import time
import json

# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# retrieve local hostname
local_hostname = socket.gethostname()

# get fully qualified hostname
local_fqdn = socket.getfqdn()

# get the according IP address
ip_address = socket.gethostbyname(local_hostname)
print(ip_address)
# bind the socket to the port 23456, and connect
server_address = ('***REMOVED***', ***REMOVED***)
sock.connect(server_address)
print(f"connecting to {local_hostname} ({local_fqdn}) with %{ip_address}")

# define example data to be sent to the server
temperature_data = ["1234567890", "22", "21", "26", "25", "19"]
for entry in temperature_data:
    print(f"data: {entry}")
    new_data = str("temperature: %s\n" % entry).encode("utf-8")
    sock.sendall(new_data)
    returnn = sock.recv(100000)
    #
    print(returnn)
    # wait for two seconds
    time.sleep(1)

# close connection
sock.close()