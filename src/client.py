import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = "127.0.0.1"
server_port = 9001

print("connecting to {}".format((server_address, server_port)))

try:
    sock.connect((server_address, server_port))
    sock.send(b"sample room:4:hogehoge")
    sock.send(b"sample room:join")
    sock.send(b"sample room:create:3")
except socket.error as err:
    print(err)
    sys.exit(1)
finally:
    print("closing socket")
    sock.close()
