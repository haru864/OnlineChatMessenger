class ChatClient:
    def __init__(self, address: str, port: int, username: str) -> None:
        self.address = address
        self.port = port
        self.username = username

    def generateKey(self) -> str:
        return self.address + ":" + str(self.port)

    def __str__(self) -> str:
        return f"ChatRoom{{address:{self.address}, port:{self.port}, name:{self.username}}}"


class ChatRoom:
    def __init__(self, roomname: str, max_num_of_participants: int, host: str) -> None:
        self.roomname = roomname
        self.max_num_of_participants = max_num_of_participants
        self.host = host

    def __str__(self) -> str:
        return f"ChatRoom{{title:{self.title}, max_num_of_participants:{self.max_num_of_participants}, host:{self.host}}}"
