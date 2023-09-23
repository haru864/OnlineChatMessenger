import chatroom
import asyncio
import json

room_title_to_chatrooms: dict[str, chatroom.ChatRoom] = {}
client_key_to_chatrooms: dict[str, chatroom.ChatRoom] = {}
active_username: set[str] = set()

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


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client_address = writer.get_extra_info("peername")
    print(f"Connected from {client_address}")
    username = None
    isActive = True

    while isActive:
        try:
            data = await asyncio.wait_for(reader.readline(), TIMEOUT_SECONDS)
            message_str = data.decode("utf-8")
            print(f"Received {message_str} from {client_address}")
            message_dict = json.loads(message_str)
            command = message_dict["command"]
            response_dict = {}

            if username is None:
                if command == "login":
                    username_candidate = message_dict["username"]
                    if (
                        len(username_candidate) == 0
                        or username_candidate in active_username
                    ):
                        response_dict["status"] = 1
                        response_dict[
                            "message"
                        ] = f"Username '{username_candidate}' is already used"
                    else:
                        username = username_candidate
                        active_username.add(username)
                        chatclient = chatroom.ChatClient(
                            client_address[0], client_address[1], username
                        )
                        print(f"User '{username}' login")
                        response_dict["status"] = 0
                        response_dict[
                            "message"
                        ] = f"Welcome to Online Chat Messenger, {username}!"
                else:
                    response_dict["status"] = 1
                    response_dict["message"] = "Please login first"
            elif command == "logout":
                active_username.remove(username)
                print(f"User '{username}' logout")
                response_dict["status"] = 0
                response_dict["message"] = f"Goodbye, {username}!"
                isActive = False
            else:
                response_dict["status"] = 1
                response_dict["message"] = "Your current request is invalid"

            response_str = json.dumps(response_dict)
            writer.write(response_str.encode("utf-8"))
            await writer.drain()

        except asyncio.TimeoutError:
            print(
                f"No data received in {TIMEOUT_SECONDS} seconds. Closing the connection."
            )
            writer.write(b"Timeout!")
            await writer.drain()

        except Exception as e:
            print("Error: " + str(e))
            writer.write(str(e).encode("utf-8"))
            await writer.drain()

    print("Closing current connection to", client_address)
    writer.close()
    await writer.wait_closed()


async def main():
    server_address = "0.0.0.0"
    server_port = 9001
    server = await asyncio.start_server(handle_client, server_address, server_port)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
