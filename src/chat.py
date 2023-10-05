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


class ChatRoom(asyncio.DatagramProtocol):
    def __init__(
        self,
        roomname: str,
        max_num_of_participants: int,
        host: ChatClient,
    ) -> None:
        if max_num_of_participants < 2:
            raise Exception("max_num_of_participants must be greater than one")
        super().__init__()
        self.roomname: str = roomname
        self.max_num_of_participants: int = max_num_of_participants
        self.host: ChatClient = host
        self.host.chatroom = self
        self.participants: list[ChatClient] = [host]
        self.participants_addr: set[tuple[str, int]] = set()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        request_str = data.decode("utf8")
        self.participants_addr.add(addr)
        print(f"(UDP) Received {request_str} from {addr}")
        for dest_addr in self.participants_addr:
            if dest_addr == addr:
                continue
            self.transport.sendto(data, dest_addr)

    def getUdpAddress(self) -> str:
        return self.transport.get_extra_info("sockname")[0]

    def getUdpPort(self) -> int:
        return self.transport.get_extra_info("sockname")[1]

    def addClientToRoom(self, participant: ChatClient) -> None:
        if self.isFullRoom():
            raise Exception(f"Chatroom '{self.roomname}' is full now")
        self.participants.append(participant)
        participant.chatroom = self
        return None

    def removeClientFromRoom(self, participant: ChatClient) -> None:
        if participant == self.host:
            self.host = self.participants[0] if len(self.participants) > 0 else None
        self.participants.remove(participant)
        participant.chatroom = None
        return None

    def isFullRoom(self) -> bool:
        return len(self.participants) == self.max_num_of_participants

    def isEmptyRoom(self) -> bool:
        return len(self.participants) == 0

    def __str__(self) -> str:
        return f"ChatRoom{{roomname:{self.roomname}, max_num_of_participants:{self.max_num_of_participants}, host:{self.host}}}"
