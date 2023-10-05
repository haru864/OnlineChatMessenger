import asyncio


class TCPServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print(f"Received message: {message}")


async def main():
    loop = asyncio.get_running_loop()
    await loop.create_server(TCPServerProtocol, "127.0.0.1", 8888)

    while True:
        await asyncio.sleep(3600)


asyncio.run(main())
