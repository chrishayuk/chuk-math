# token.py
from typing import Any

class Token:
    def __init__(self, type_: str, value: Any, position: int):
        # set the type, value and position
        self.type = type_
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, position={self.position})"


