from typing import Any
import asyncio
import json


BUFFER_SIZE: int = 256
TIMEOUT_SECONDS: float = 60.0


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


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    client_address = writer.get_extra_info("peername")
    print(f"Connected from {client_address}")

    response_dict = await getRequest(reader)
    print(f"response_dict -> {response_dict}")
    sendResponse(writer, {"status": "hogehoge"})

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
