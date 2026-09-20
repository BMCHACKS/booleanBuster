from enum import StrEnum, auto

class TokenType(StrEnum):
    # IDENTIFIER
    IDENTIFIER = auto(), # a-z,A-Z, 0-9, _ but not gate
    # GATES
    AND        = auto(), # AND gate  | (a.b)
    OR         = auto(), # OR gate   | (a + b)
    NOT        = auto(), # NOT gate  | a'
    NAND       = auto(), # NAND gate | (a . b)'
    NOR        = auto(), # NOR gate  | (a + b)'
    XOR        = auto(), # XOR gate  | (a'.b) + (a.b')
    XNOR       = auto(), # XNOR gate | (a.b) + (a'.b')
    # brackets
    L_BRACKET  = auto(), # (
    R_BRACKET  = auto()  # )
    # terminator
    TERMINATOR = auto() # ;
    EOF        = auto() # End of file
    #------------------------------------
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"
