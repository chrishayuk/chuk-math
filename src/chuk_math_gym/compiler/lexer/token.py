# token.py

from typing import Union


class Token:
    def __init__(self, type: str, value: Union[str, float, int], position: int):
        self.type = type
        self.value = value
        self.position = position

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return False
        return (
            self.type == other.type
            and self.value == other.value
            and self.position == other.position
        )

    def __repr__(self) -> str:
        return f"Token(type={self.type}, value={self.value}, position={self.position})"
