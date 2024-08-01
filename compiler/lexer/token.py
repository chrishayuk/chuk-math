# token.py
from typing import Any

class Token:
    def __init__(self, type, value, position):
        self.type = type
        self.value = value
        self.position = position

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and
                self.value == other.value and
                self.position == other.position)

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, position={self.position})"
