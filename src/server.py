from typing import Any
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


async def getRequest(reader: asyncio.StreamReader) -> dict[str:Any]:
    data = await asyncio.wait_for(reader.readline(), TIMEOUT_SECONDS)
    response_str = data.decode("utf-8")
    response_dict = json.loads(response_str)
    return response_dict


async def sendResponse(
    writer: asyncio.StreamWriter, response_dict: dict[str:Any]
) -> None:
    response_str = json.dumps(response_dict)
    writer.write(response_str.encode("utf-8"))
    await writer.drain()
    return None


def removeClientFromChatroom(client: chat.ChatClient) -> None:
    if client.chatroom:
        current_chatroom = client.chatroom
        roomname = current_chatroom.roomname
        current_chatroom.removeClientFromRoom(client)
        if current_chatroom.isEmptyRoom():
            del roomname_to_chatroom[roomname]
            del current_chatroom


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    client_address = writer.get_extra_info("peername")
    print(f"Connected from {client_address}")
    client: chat.ChatClient = None

    while not client:
        request_dict = await getRequest(reader)
        command = request_dict.get("command")
        username = request_dict.get("username")
        if command != "login":
            response = {
                "status": 1,
                "error_message": "Login first",
            }
        elif not username or len(username) == 0:
            response = {
                "status": 1,
                "error_message": "Username must be 1 character or more",
            }
        elif username in username_to_chatclient:
            response = {
                "status": 1,
                "error_message": f"Username '{username}' is already used",
            }
        else:
            client = chat.ChatClient(client_address[0], client_address[1], username)
            username_to_chatclient[client.username] = client
            print(f"User '{client.username}' login")
            response = {"status": 0}
        await sendResponse(writer, response)

    while True:
        try:
            request_dict = await getRequest(reader)
            print(f"request_dict -> {request_dict}")
            command = request_dict.get("command")
            response = {}

            if command == "logout":
                print(f"User '{client.username}' logout")
                response["status"] = 0
                await sendResponse(writer, response)
                break

            elif command == "leave":
                removeClientFromChatroom(client)
                if client.chatroom:
                    response["status"] = 0
                else:
                    response["status"] = 1
                    response["error_message"] = "You have not joined any chatroom"
                await sendResponse(writer, response)

            elif command == "create":
                roomname = request_dict["roomname"]
                max_num_of_participants = request_dict["max_num_of_participants"]
                if roomname in roomname_to_chatroom:
                    response["status"] = 1
                    response["error_message"] = f"Chatroom '{roomname}' already exist"
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
                    response["status"] = 0
                    response["udp_address"] = new_chatroom.getUdpAddress()
                    response["udp_port"] = new_chatroom.getUdpPort()
                await sendResponse(writer, response)

            elif command == "list":
                response["status"] = 0
                if client.chatroom is None:
                    roomname_list = [
                        chatroom.roomname for chatroom in roomname_to_chatroom.values()
                    ]
                    response["room_list"] = roomname_list
                else:
                    members = [
                        f"{participant.username}(host)"
                        if participant == client.chatroom.host
                        else participant.username
                        for participant in client.chatroom.participants
                    ]
                    response["member_list"] = members
                await sendResponse(writer, response)

            elif command == "join":
                roomname = request_dict["roomname"]
                if roomname not in roomname_to_chatroom:
                    response["status"] = 1
                    response["error_message"] = f"Chatroom '{roomname}' does not exist"
                else:
                    target_chat_room = roomname_to_chatroom[roomname]
                    target_chat_room.addClientToRoom(client)
                    print(
                        f"{client.username} join Chatroom '{target_chat_room.roomname}'"
                    )
                    response["status"] = 0
                    response["udp_address"] = target_chat_room.getUdpAddress()
                    response["udp_port"] = target_chat_room.getUdpPort()
                await sendResponse(writer, response)

            else:
                response["status"] = 1
                response["error_message"] = "Invalid request"
                await sendResponse(writer, response)

        except asyncio.TimeoutError:
            print(
                f"[{str(client)}] No data received in {TIMEOUT_SECONDS} seconds. Closing the connection."
            )
            await sendResponse(writer, {"status": 1, "error_message": "Timeout!"})
            break

        except Exception as e:
            print(f"[{str(client)}] Error: " + str(e))
            print(f"詳細なトレースバック情報:\n{traceback.format_exc()}")
            await sendResponse(writer, {"status": 1, "error_message": str(e)})
            break

    removeClientFromChatroom(client)
    del username_to_chatclient[client.username]
    print("Closing current connection to", client_address)
    writer.close()
    await writer.wait_closed()


async def main() -> None:
    server_address = "0.0.0.0"
    server_port = 9001
    server = await asyncio.start_server(handle_client, server_address, server_port)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
