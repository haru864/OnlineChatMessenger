from typing import Any
import socket
import sys
import os
import json

server_address: str = "127.0.0.1"
server_port: int = 9001
BUFFER_SIZE: int = 256


def getResponse(sock) -> tuple[str, Any]:
    response: bytes = sock.recv(BUFFER_SIZE)
    response_str: str = response.decode("utf-8")
    response_dict = json.loads(response_str)
    status = response_dict["status"]
    message = response_dict["message"]
    # print(f"response_dict -> {response_dict}")
    return (status, message)


def login(sock) -> str:
    print("login")
    while True:
        username: str = input("username > ")
        request_data: dict[str, str] = {}
        request_data["command"] = "login"
        request_data["username"] = username
        request_data_str: str = json.dumps(request_data) + "\n"
        sock.send(request_data_str.encode("utf-8"))
        status, message = getResponse(sock)
        print(message)
        if status == 0:
            return username


sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(30.0)
print("connecting to {}".format((server_address, server_port)))

while True:
    try:
        sock.connect((server_address, server_port))
        username = login(sock)
        current_room = None
        isActive = True

        while isActive:
            command: str = input(
                f"({username}@{current_room if current_room else ''}) >> "
            )
            request_data: dict[str, str] = {}
            request_data["command"] = command

            if command == "create":
                roomname: str = input("room name > ")
                max_num_of_participants: int = int(
                    input("Max number of participants > ")
                )
                current_room = roomname
                request_data["roomname"] = roomname
                request_data["max_num_of_participants"] = max_num_of_participants
            elif command == "join":
                roomname: str = input("room name > ")
                request_data["roomname"] = roomname
                current_room = roomname
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
            status, message = getResponse(sock)
            print(message)

            if command in ("create", "join"):
                if status == 1:
                    current_room = None
                else:
                    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    address_udp = message[0]
                    port_udp = message[1]
                    print(f"UDP -> {address_udp}, {port_udp}")
                    udp_socket.sendto(
                        f"Hello via UDP from {username}".encode(), (address_udp, port_udp)
                    )
                    udp_socket.close()

    except Exception as err:
        print(err)
        sys.exit(1)

    finally:
        print("Close socket")
        sock.close()
        sys.exit(0)
