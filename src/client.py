import socket
import sys
import os


def getResponse(socket) -> str:
    response: bytes = sock.recv(BUFFER_SIZE)
    return response.decode("utf-8")


def login(socket) -> None:
    username: str = input("username: ")
    sock.send(username.encode("utf-8"))


sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address: str = "127.0.0.1"
server_port: int = 9001
BUFFER_SIZE: int = 256

print("connecting to {}".format((server_address, server_port)))

while True:
    try:
        sock.connect((server_address, server_port))
        login(sock)
        while True:
            command: str = input(">> ")
            if command == "create":
                title: str = input("Title of chatroom > ")
                max_num_of_participants: int = int(
                    input("Max number of participants > ")
                )
                request_data: str = f"create:{title}:{max_num_of_participants}\n"
                sock.send(request_data.encode("utf-8"))
            elif command == "join":
                pass
            elif command == "list":
                sock.send("list\n".encode("utf-8"))
            elif command == "close":
                sock.send("close\n".encode("utf-8"))
                break
            elif command == "help":
                current_file_path: str = os.path.abspath(__file__)
                current_directory = os.path.dirname(current_file_path)
                manual_file_path = os.path.join(
                    current_directory, "../man", "manual.txt"
                )
                with open(manual_file_path, "r") as f:
                    manual: str = f.read()
                    print("\n" + manual + "\n")
            else:
                print("Invalid command. Type 'help' to find out how to operate.")
                continue
            response: str = getResponse(sock)
            print(response)
    except Exception as err:
        print(err)
        sys.exit(1)
    finally:
        print("Closing socket")
        sock.close()
        sys.exit(0)
