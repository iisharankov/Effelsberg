import time
import socket
status_message = b"Hello World"
MULTICAST = ''
MULTIPORT = 0


while True:
    time.sleep(1)
    multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    timee = str(time.time()).encode()
    multicast_sock.sendto(timee, (MULTICAST, MULTIPORT))
