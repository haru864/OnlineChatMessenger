import asyncio


class TCPEchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print("TCP server received:", message)
        self.transport.write(("Received " + message).encode())


async def tcp_server(loop):
    server = await loop.create_server(TCPEchoServerProtocol, "127.0.0.1", 8888)
    await server.serve_forever()


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(tcp_server(loop))
finally:
    loop.close()
