import socket
import chatroom

room_title_to_chatrooms: dict[str, chatroom.ChatRoom] = {}
client_key_to_chatrooms: dict[str, chatroom.ChatRoom] = {}
BUFFER_SIZE: int = 256
TIMEOUT_SECONDS: float = 60.0


def createChatRoom(
    room_title: str, max_num_of_participants: int, host: chatroom.ChatClient
) -> None:
    if room_title in room_title_to_chatrooms:
        raise Exception(f"Chatroom '{room_title}' already exists")
    new_chatroom = chatroom.ChatRoom(
        title=room_title, max_num_of_participants=max_num_of_participants, host=host
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
        print("connection from", client_address)
        client_socket.settimeout(TIMEOUT_SECONDS)
        try:
            username = client_socket.recv(BUFFER_SIZE)
            client = chatroom.ChatClient(client_address[0], client_address[1], username)
            data_buffer: bytes = b""
            line: bytes = b""
            isActiveConnection = True
            while isActiveConnection:
                while True:
                    chunk = client_socket.recv(BUFFER_SIZE)
                    print("received data ->", chunk)
                    if chunk == b"":
                        isActiveConnection = False
                        break
                    data_buffer += chunk
                    if b"\n" in data_buffer:
                        line, data_buffer = data_buffer.split(b"\n", 1)
                        break
                words: list[str] = line.decode("utf-8").split(":")
                print(f"line -> {line}")
                print(f"data_buffer -> {data_buffer}")
                print(f"words -> {words}")
                if words[0] == "list":
                    titles: list[str] = list(room_title_to_chatrooms.keys())
                    client_socket.send(",".join(titles).encode("utf-8"))
                elif words[0] == "create":
                    title: str = words[1]
                    max_num_of_participants: str = words[2]
                    createChatRoom(title, int(max_num_of_participants), client)
                    client_socket.send(
                        f"New chatroom '{title}' was created".encode("utf-8")
                    )
                elif words[0] == "close":
                    break
                else:
                    pass
        except socket.timeout:
            print(
                f"No data received in {TIMEOUT_SECONDS} seconds. "
                f"Closing the connection."
            )
        except Exception as e:
            print("Error: " + str(e))
            client_socket.send(str(e).encode("utf-8"))
        finally:
            print("Closing current connection to", client_address)
            client_socket.close()


if __name__ == "__main__":
    main()
