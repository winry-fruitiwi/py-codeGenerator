# an enumeration for token types
from enum import Enum


class TokenType(Enum):
    NOT_A_TOKEN = 0
    INT_CONST = 1
    STRING_CONST = 2
    KEYWORD = 3
    SYMBOL = 4
    IDENTIFIER = 5
