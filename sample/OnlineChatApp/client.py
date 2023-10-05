import asyncio
import socket


async def tcp_client():
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

    data = await reader.read(100)
    print(f"Received: {data.decode()}")

    writer.close()
    await writer.wait_closed()


async def udp_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        message = input("Enter message to broadcast (or 'exit' to quit): ")
        if message == "exit":
            break

        sock.sendto(message.encode(), ("127.0.0.1", 9999))
        data, addr = sock.recvfrom(1024)
        print(f"Received: {data.decode()} from {addr}")


if __name__ == "__main__":
    asyncio.run(tcp_client())
    asyncio.run(udp_client())
