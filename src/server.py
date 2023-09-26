import traceback
import chat
import asyncio
import json

roomname_to_chatroom: dict[str, chat.ChatRoom] = {}
username_to_chatclient: dict[str, chat.ChatClient] = {}

BUFFER_SIZE: int = 256
TIMEOUT_SECONDS: float = 60.0


class UdpProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        print(f"(UDP) Received {data.decode()} from {addr}")


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client_address = writer.get_extra_info("peername")
    print(f"Connected from {client_address}")
    client: chat.ChatClient = None
    isActive = True

    while isActive:
        try:
            data = await asyncio.wait_for(reader.readline(), TIMEOUT_SECONDS)
            message_str = data.decode("utf-8")
            print(f"(TCP) Received {message_str} from {client_address}")
            message_dict = json.loads(message_str)
            command = message_dict["command"]
            response_dict = {}

            if client is None:
                if command == "login":
                    username_candidate = message_dict["username"]
                    if (
                        len(username_candidate) == 0
                        or username_candidate in username_to_chatclient
                    ):
                        response_dict["status"] = 1
                        response_dict[
                            "message"
                        ] = f"Username '{username_candidate}' is already used"
                    else:
                        client = chat.ChatClient(
                            client_address[0], client_address[1], username_candidate
                        )
                        username_to_chatclient[client.username] = client
                        print(f"User '{client.username}' login")
                        response_dict["status"] = 0
                        response_dict[
                            "message"
                        ] = f"Welcome to Online Chat Messenger, {client.username}!"
                else:
                    response_dict["status"] = 1
                    response_dict["message"] = "Please login first"

            elif command == "login":
                response_dict["status"] = 0
                response_dict["message"] = "You already log in"

            elif command == "logout":
                if client.chatroom:
                    current_chatroom = client.chatroom
                    roomname = current_chatroom.roomname
                    current_chatroom.leaveRoom(client)
                    if current_chatroom.isEmptyRoom():
                        del roomname_to_chatroom[roomname]
                        del current_chatroom
                del username_to_chatclient[client.username]
                print(f"[{client.username}] User '{client.username}' logout")
                response_dict["status"] = 0
                response_dict["message"] = f"Goodbye, {client.username}!"
                isActive = False

            elif command == "create":
                roomname = message_dict["roomname"]
                max_num_of_participants = message_dict["max_num_of_participants"]
                if roomname in roomname_to_chatroom:
                    response_dict["status"] = 1
                    response_dict["message"] = f"Chatroom '{roomname}' already exist"
                else:
                    (
                        transport,
                        protocol,
                    ) = await asyncio.get_running_loop().create_datagram_endpoint(
                        lambda: UdpProtocol(), local_addr=("0.0.0.0", 0)
                    )

                    new_chatroom = chat.ChatRoom(
                        transport,
                        roomname,
                        max_num_of_participants,
                        client,
                    )
                    roomname_to_chatroom[roomname] = new_chatroom
                    print(
                        f"Chatroom '{roomname}' is created, UDP on ({new_chatroom.getUdpAddress()}, {new_chatroom.getUdpPort()})"
                    )
                    response_dict["status"] = 0
                    response_dict["message"] = [
                        new_chatroom.getUdpAddress(),
                        new_chatroom.getUdpPort(),
                    ]

            elif command == "list":
                response_dict["status"] = 0
                if client.chatroom is None:
                    roomname_list = [
                        chatroom.roomname for chatroom in roomname_to_chatroom.values()
                    ]
                    response_dict["message"] = "chatrooms: " + str(roomname_list)
                else:
                    members = [
                        participant.username
                        for participant in client.chatroom.participants
                    ]
                    response_dict[
                        "message"
                    ] = f"members@{client.chatroom.roomname}: " + str(members)

            elif command == "join":
                roomname = message_dict["roomname"]
                if roomname not in roomname_to_chatroom:
                    response_dict["status"] = 0
                    response_dict["message"] = f"Chatroom '{roomname}' does not exist"
                else:
                    target_chat_room = roomname_to_chatroom[roomname]
                    target_chat_room.joinRoom(client)
                    print(
                        f"{client.username} join Chatroom '{target_chat_room.roomname}'"
                    )
                    response_dict["status"] = 0
                    response_dict["message"] = [
                        target_chat_room.getUdpAddress(),
                        target_chat_room.getUdpPort(),
                    ]

            elif command == "leave":
                if client.chatroom:
                    current_chatroom = client.chatroom
                    roomname = current_chatroom.roomname
                    current_chatroom.leaveRoom(client)
                    if current_chatroom.isEmptyRoom():
                        del roomname_to_chatroom[roomname]
                        del current_chatroom
                    response_dict["status"] = 0
                    response_dict["message"] = f"leave chatroom '{roomname}'"
                else:
                    response_dict["status"] = 0
                    response_dict["message"] = f"You're not belong to any chatroom"

            else:
                response_dict["status"] = 1
                response_dict["message"] = "Your current request is invalid"

            response_str = json.dumps(response_dict)
            print(f"response_str -> {response_str}")
            writer.write(response_str.encode("utf-8"))
            await writer.drain()

        except asyncio.TimeoutError:
            print(
                f"[{str(client)}] No data received in {TIMEOUT_SECONDS} seconds. Closing the connection."
            )
            writer.write(b'{"status":1, "message":"Timeout!"}')
            await writer.drain()
            break

        except Exception as e:
            print(f"[{str(client)}] Error: " + str(e))
            print(f"詳細なトレースバック情報:\n{traceback.format_exc()}")
            response_message = f'{{"status":1, "message":{str(e)}}}'
            writer.write(response_message.encode("utf-8"))
            await writer.drain()
            break

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
