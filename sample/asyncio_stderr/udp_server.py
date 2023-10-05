import asyncio


class UDPEchoServerProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.clients = set()  # To keep track of clients

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print("UDP server received:", message)
        self.clients.add(addr)  # Add the client address to the set

        # This is the usual echo response
        self.transport.sendto(("Echoed: " + message).encode(), addr)

    async def send_periodic_messages(self):
        while True:
            for client in self.clients:
                self.transport.sendto("Hello from server!".encode(), client)
            await asyncio.sleep(5)  # Send every 5 seconds


async def udp_server():
    loop = asyncio.get_event_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        UDPEchoServerProtocol, local_addr=("127.0.0.1", 9999)
    )

    # Start the task for sending periodic messages
    asyncio.ensure_future(protocol.send_periodic_messages())

    try:
        await asyncio.sleep(3600)  # Keep the server running for a while
    finally:
        transport.close()


loop = asyncio.get_event_loop()
print("UDP Server started on 127.0.0.1:9999")
try:
    loop.run_until_complete(udp_server())
finally:
    loop.close()
