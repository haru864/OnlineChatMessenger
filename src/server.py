import socket
import chatroom

room_title_to_chatrooms: dict[str, chatroom.ChatRoom] = {}
client_key_to_chatrooms: dict[str, chatroom.ChatRoom] = {}
MAX_NUM_OF_PARTICIPANTS: int = 3
BUFFER_SIZE: int = 256
TIMEOUT_SECONDS: float = 10.0


def createChatRoom(room_title: str) -> None:
    if room_title in room_title_to_chatrooms:
        raise Exception(f"Chatroom '{room_title}' already exists")
    new_chatroom = chatroom.ChatRoom(
        title=room_title, max_num_of_participants=MAX_NUM_OF_PARTICIPANTS
    )
    room_title_to_chatrooms[room_title] = new_chatroom
    print(f"Chatroom '{room_title}' was created")
    return None


def joinChatRoom(client: chatroom.ChatClient, room_title: str) -> None:
    client_key: str = client.generateKey()
    if client_key in client_key_to_chatrooms:
        chat_room: chatroom.ChatRoom = client_key_to_chatrooms[client_key]
        raise Exception(
            f"Client '{client}' have already been in chat room '{chat_room}'"
        )
    client_key_to_chatrooms[client_key] = room_title_to_chatrooms[room_title]
    print(f"'{client}' joined chatroom '{room_title}'")
    return None


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = "127.0.0.1"
    server_port = 9001

    print("Starting up on {} port {}".format(server_address, server_port))

    sock.bind((server_address, server_port))
    sock.listen(1)

    while True:
        client_socket, client_address = sock.accept()
        client_socket.settimeout(TIMEOUT_SECONDS)
        try:
            print("connection from ", client_address)
            data: bytes = client_socket.recv(BUFFER_SIZE)
            print("received data -> ", data)
            whole_data_string: str = ""
            while data is not None and data != b"":
                whole_data_string += data.decode("utf-8")
                data = client_socket.recv(BUFFER_SIZE)
                print("received data -> ", data)
            print("received data -> ", whole_data_string)
            print("receive all data from ", client_address)
        except socket.timeout:
            print(
                f"No data received in {TIMEOUT_SECONDS} seconds. "
                f"Closing the connection."
            )
        except Exception as e:
            print("Error: " + str(e))
        finally:
            print("Closing current connection to ", client_address)
            client_socket.close()


if __name__ == "__main__":
    main()
