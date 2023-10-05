import asyncio


class TCPClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        loop = asyncio.get_running_loop()
        loop.create_task(self.send_from_stdin())

    async def send_from_stdin(self):
        while True:
            line = await loop.run_in_executor(None, input, "Enter message: ")
            self.transport.write(line.encode())


async def main():
    loop = asyncio.get_running_loop()
    await loop.create_connection(TCPClientProtocol, "127.0.0.1", 8888)

    while True:
        await asyncio.sleep(3600)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
