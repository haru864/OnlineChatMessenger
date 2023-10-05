from typing import Any
import socket
import sys
import os
import json

tcp_server_address: str = "127.0.0.1"
tcp_server_port: int = 9001
TCP_BUFFER_SIZE: int = 256
UDP_BUFFER_SIZE: int = 1024

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(60.0)


def getResponse(request_data: dict) -> dict[str, Any]:
    request_data_str: str = json.dumps(request_data) + "\n"
    sock.send(request_data_str.encode("utf-8"))
    response: bytes = sock.recv(TCP_BUFFER_SIZE)
    response_str: str = response.decode("utf-8")
    response_dict = json.loads(response_str)
    return response_dict


def login() -> str:
    print("login")
    while True:
        username: str = input("username >> ")
        request_data: dict[str, str] = {}
        request_data["command"] = "login"
        request_data["username"] = username
        response_dict = getResponse(request_data)
        if response_dict["status"] == 0:
            print(f"Welcome to Online Chat Messenger, {username}!")
            return username
        print(response_dict["error_message"])


# TODO
def chatInRoom(udp_server_address: str, udp_server_port: int, roomname: str) -> None:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setblocking(False)
    print(f"Join chatroom '{roomname}'({udp_server_address}, {udp_server_port})")
    udp_socket.sendto(
        f"[admin@{current_room}]{username} join".encode(),
        (address_udp, port_udp),
    )
    while True:
        command: str = input(f"({username}@{roomname}) >> ")
        if command == "send":
            message: str = input("message:\n")
            udp_socket.sendto(message.encode(), (address_udp, port_udp))
        elif command == "receive":
            try:
                data, addr = udp_socket.recvfrom(UDP_BUFFER_SIZE)
                message: str = data.decode()
                print(message)
            except BlockingIOError:
                pass
        elif command == "leave":
            break
        else:
            print("available: send, receive, leave")
    udp_socket.close()


while True:
    try:
        sock.connect((tcp_server_address, tcp_server_port))
        print("connecting to {}".format((tcp_server_address, tcp_server_port)))

        username = login()
        current_room = None
        isActive = True

        while isActive:
            command: str = input(f"({username}) >> ")
            request_data: dict[str, str] = {}
            request_data["command"] = command

            if command == "create":
                roomname: str = input("room name >> ")
                max_num_of_participants: int = int(
                    input("Max number of participants >> ")
                )
                current_room = roomname
                request_data["roomname"] = roomname
                request_data["max_num_of_participants"] = max_num_of_participants
            elif command == "join":
                roomname: str = input("room name >> ")
                request_data["roomname"] = roomname
                current_room = roomname
            elif command == "list":
                pass
            elif command == "leave":
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

            response = getResponse(request_data)
            print(f"response -> {response}")

            if response["status"] == 1:
                error_message = response["error_message"]
                print(f"Error: {error_message}")

            if command in ("create", "join"):
                if response["status"] == 1:
                    current_room = None
                else:
                    address_udp = response["udp_address"]
                    port_udp = response["udp_port"]
                    chatInRoom(address_udp, port_udp, current_room)
                    getResponse({"command": "leave"})
            elif command == "leave":
                if response["status"] == 0:
                    print(f"leave from chatroom '{current_room}'")
                    current_room = None
            elif command == "list":
                print("chatroom list -> " + str(response.get("room_list")))

    except Exception as err:
        print(err)
        sys.exit(1)

    finally:
        print("Close socket")
        sock.close()
        sys.exit(0)
