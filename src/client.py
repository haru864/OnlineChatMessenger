import socket
import sys
import os
import json

server_address: str = "127.0.0.1"
server_port: int = 9001
BUFFER_SIZE: int = 256


def getResponse(socket) -> str:
    response: bytes = sock.recv(BUFFER_SIZE)
    return response.decode("utf-8")


def login(sock) -> str:
    print("login")
    while True:
        username: str = input("username > ")
        request_data: dict[str, str] = {}
        request_data["command"] = "login"
        request_data["username"] = username
        request_data_str: str = json.dumps(request_data) + "\n"
        sock.send(request_data_str.encode("utf-8"))
        response: str = getResponse(sock)
        response_dict = json.loads(response)
        print(response_dict["message"])
        if response_dict["status"] == 0:
            return username


sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5.0)
print("connecting to {}".format((server_address, server_port)))

while True:
    try:
        sock.connect((server_address, server_port))
        username = login(sock)
        room = None
        isActive = True
        while isActive:
            command: str = input(f"({username}@{room}) >> ")
            request_data: dict[str, str] = {}
            request_data["command"] = command
            if command == "create":
                roomname: str = input("room name > ")
                max_num_of_participants: int = int(
                    input("Max number of participants > ")
                )
                request_data["roomname"] = roomname
                request_data["max_num_of_participants"] = max_num_of_participants
            elif command == "join":
                roomname: str = input("room name > ")
                request_data["roomname"] = roomname
            elif command == "list":
                pass
            elif command == "logout":
                isActive = False
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
            request_data_str: str = json.dumps(request_data) + "\n"
            sock.send(request_data_str.encode("utf-8"))
            response: str = getResponse(sock)
            response_dict = json.loads(response)
            print(response_dict["message"])
    except Exception as err:
        print(err)
        sys.exit(1)
    finally:
        print("Close socket")
        sock.close()
        sys.exit(0)
