import chat
import asyncio
import json

roomname_to_chatroom: dict[str, chat.ChatRoom] = {}
username_to_chatclient: dict[str, chat.ChatRoom | None] = {}

BUFFER_SIZE: int = 256
TIMEOUT_SECONDS: float = 30.0


class UdpProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        print(f"Received {data.decode()} from {addr}")


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client_address = writer.get_extra_info("peername")
    print(f"Connected from {client_address}")
    client: chat.ChatClient = None
    isActive = True

    while isActive:
        try:
            data = await asyncio.wait_for(reader.readline(), TIMEOUT_SECONDS)
            message_str = data.decode("utf-8")
            print(f"[{str(client)}] Received {message_str} from {client_address}")
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

            # TODO：logout時にチャットルームから退出する
            elif command == "logout":
                current_chatroom = client.chatroom
                current_chatroom.leaveRoom(client)
                if current_chatroom.isEmpty():
                    del roomname_to_chatroom[current_chatroom.roomname]
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
                    address_udp = transport.get_extra_info("sockname")[0]
                    port_udp = transport.get_extra_info("sockname")[1]

                    new_chat_room = chat.ChatRoom(
                        address_udp,
                        port_udp,
                        roomname,
                        max_num_of_participants,
                        client,
                    )
                    roomname_to_chatroom[roomname] = new_chat_room
                    print(
                        f"Chatroom '{roomname}' is created, switch to UDP on ({address_udp}, {port_udp})"
                    )
                    response_dict["status"] = 0
                    response_dict["message"] = [address_udp, port_udp]

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
                    response_dict["status"] = 1
                    response_dict["message"] = f"Chatroom '{roomname}' does not exist"
                else:
                    target_chat_room = roomname_to_chatroom[roomname]
                    target_chat_room.joinRoom(client)
                    address_udp = target_chat_room.address
                    port_udp = target_chat_room.port
                    response_dict["status"] = 0
                    response_dict["message"] = [address_udp, port_udp]

            # TODO：チャットルーム退出ロジックを実装する
            elif command == "leave":
                pass

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
