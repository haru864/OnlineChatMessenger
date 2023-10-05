import json
import asyncio

tcp_server_address: str = "127.0.0.1"
tcp_server_port: int = 9001
BUFFER_SIZE: int = 256


class UDPClientProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport) -> None:
        self.transport = transport
        self.transport.sendto("Hello from UDP client".encode())

    def datagram_received(self, data, addr) -> None:
        print(f"Received UDP message from {addr}: {data.decode()}")


class TCPClientProtocol(asyncio.Protocol):
    def connection_made(self, transport) -> None:
        print("connecting to {}".format((tcp_server_address, tcp_server_port)))
        self.transport = transport
        loop = asyncio.get_running_loop()
        loop.create_task(self.send_from_stdin())

    def data_received(self, data) -> None:
        response_str = data.decode()
        response_dict = json.loads(response_str)
        print(f"response_dict -> {response_dict}", flush=True)

    async def send_from_stdin(self) -> None:
        while True:
            username = await loop.run_in_executor(
                None,
                input,
                "username >> ",
            )
            request_dict = {"command": "login", "usrename": username}
            response_str = json.dumps(request_dict) + "\n"
            print(f"response_str -> {response_str}")
            self.transport.write(response_str.encode())


async def main():
    loop = asyncio.get_running_loop()
    await loop.create_connection(TCPClientProtocol, tcp_server_address, tcp_server_port)
    while True:
        await asyncio.sleep(3600)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
