from typing import Optional, List, Tuple, Dict

class Node:
    def __init__(self, type: str):
        self.type = type

class AntlrToken:
    pass  # Empty class as a placeholder for Antlr4TsToken

class TokenizeOptions:
    def __init__(self, range: bool = False, loc: bool = False):
        self.range = range
        self.loc = loc

class ParseOptions(TokenizeOptions):
    def __init__(self, tokens: bool = False, tolerant: bool = False, range: bool = False, loc: bool = False):
        super().__init__(range=range, loc=loc)
        self.tokens = tokens
        self.tolerant = tolerant

class Token:
    def __init__(self, type: str, value: Optional[str] = None, range: Optional[Tuple[int, int]] = None,
                 loc: Optional[Dict[str, Dict[str, int]]] = None):
        self.type = type
        self.value = value
        self.range = range
        self.loc = loc
