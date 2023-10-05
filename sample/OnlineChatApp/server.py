import asyncio
from asyncio import transports
from typing import Dict


class TCPServer:
    clients: Dict[str, transports.Transport]

    def __init__(self):
        self.clients = {}

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        addr = writer.get_extra_info("peername")
        print(f"TCP client {addr} connected")
        self.clients[addr] = writer

        # UDPサーバーアドレスをクライアントに送信
        writer.write(b"Connect to UDP server at 127.0.0.1:9999\n")

        data = await reader.read(100)
        message = data.decode()
        print(f"Received {message} from {addr}")

        writer.close()
        await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, "127.0.0.1", 8888)
        await server.serve_forever()


class UDPServer(asyncio.DatagramProtocol):
    clients = set()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print(f"Received {data.decode()} from {addr}")
        self.clients.add(addr)

        # メッセージを全てのクライアントにブロードキャスト
        for client in self.clients:
            if client != addr:
                self.transport.sendto(data, client)

    async def start(self):
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: self, local_addr=("127.0.0.1", 9999)
        )
        while True:
            await asyncio.sleep(3600)  # just keep the server running


async def main():
    tcp_server = TCPServer()
    udp_server = UDPServer()

    await asyncio.gather(tcp_server.start(), udp_server.start())


if __name__ == "__main__":
    asyncio.run(main())
