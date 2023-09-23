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
    def __init__(
        self, title: str, max_num_of_participants: int, host: ChatClient
    ) -> None:
        self.title = title
        self.max_num_of_participants = max_num_of_participants
        self.host = host

    def __str__(self) -> str:
        return (
            f"ChatRoom{{title:{self.title}, "
            f"max_num_of_participants:{self.max_num_of_participants}, "
            f"host:{self.host}}}"
        )
