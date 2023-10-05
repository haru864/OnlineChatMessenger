import asyncio
import sys


class TCPEchoClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def send_message(self, message):
        self.transport.write(message.encode())

    def data_received(self, data):
        print("TCP server replied:", data.decode())


async def tcp_client(message, loop):
    transport, protocol = await loop.create_connection(
        TCPEchoClientProtocol, "127.0.0.1", 8888
    )
    protocol.send_message(message)
    transport.close()


async def udp_receive(loop):
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPClientProtocol(loop), local_addr=("127.0.0.1", 10000)
    )
    transport.sendto("Hello from client!".encode(), ("127.0.0.1", 9999))
    try:
        await asyncio.sleep(3600)
    finally:
        transport.close()


class UDPClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, loop):
        self.loop = loop

    def datagram_received(self, data, addr):
        message = data.decode()
        sys.stderr.write(f"UDP server says: {message}\n")


async def user_input():
    while True:
        message = input("Enter your message to TCP server: ")
        if message == "exit":
            break
        await tcp_client(message, asyncio.get_event_loop())


loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(udp_receive(loop))
    loop.run_until_complete(user_input())
finally:
    loop.close()
