from enum import Enum

class ChatRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"