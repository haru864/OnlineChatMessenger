import asyncio


class ChatClient:
    def __init__(self, address: str, port: int, username: str) -> None:
        self.address: str = address
        self.port: int = port
        self.username: str = username
        self.chatroom: ChatRoom = None

    def generateKey(self) -> str:
        return self.address + ":" + str(self.port)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ChatClient):
            return False
        return self.generateKey() == __value.generateKey()

    def __str__(self) -> str:
        roomname = self.chatroom.roomname if self.chatroom is not None else ""
        return f"{self.username}({self.address}, {self.port})@{roomname}"


class ChatRoom:
    def __init__(
        self,
        udp_transport: asyncio.DatagramTransport,
        roomname: str,
        max_num_of_participants: int,
        host: ChatClient,
    ) -> None:
        self.udp_transport: asyncio.DatagramTransport = udp_transport
        self.roomname: str = roomname
        self.max_num_of_participants: int = max_num_of_participants
        self.host: ChatClient = host
        self.host.chatroom = self
        self.participants: list[ChatClient] = [host]

    def getUdpAddress(self) -> str:
        return self.udp_transport.get_extra_info("sockname")[0]

    def getUdpPort(self) -> int:
        return self.udp_transport.get_extra_info("sockname")[1]

    def closeUdpServer(self) -> None:
        self.udp_transport.close()
        return None

    def joinRoom(self, participant: ChatClient) -> None:
        self.participants.append(participant)
        participant.chatroom = self
        return None

    def leaveRoom(self, participant: ChatClient) -> None:
        if participant == self.host:
            self.host = self.participants[0] if len(self.participants) > 0 else None
        self.participants.remove(participant)
        participant.chatroom = None
        return None

    def isEmptyRoom(self) -> None:
        return len(self.participants) == 0

    def __str__(self) -> str:
        return f"ChatRoom{{roomname:{self.roomname}, max_num_of_participants:{self.max_num_of_participants}, host:{self.host}}}"
