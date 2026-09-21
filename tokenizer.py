# ------------------------------------------------------------------

# python imports
from dataclasses import dataclass
from enum        import StrEnum, auto
from typing      import Generator, Any
from string      import digits, ascii_letters

# custom imports
from keywords    import kw_dict
from token_types import TokenType

ascii_letters_underscore_digits = ascii_letters + "_" + digits

# ------------------------------------------------------------------

@dataclass
class Token:
    # each token requires two things, the TYPE of token and the value it holds
    type:  TokenType
    value: Any = None

    def __repr__(self) -> str:
        if self.value is not None:
            return f"{self.__class__.__name__}({self.type!r}, {self.value!r})"
        return f"{self.__class__.__name__}({self.type!r})"

# the actual Tokenizer
class Tokenizer:
    def __init__(self, code:str) -> None:
        self.code = code
        self.ptr  = 0

    def _peak(self) -> str:
        # since _peak is used AFTER incrementing self.ptr, we don't need to return self.code[self.ptr+1]
        if self.ptr < len(self.code):
            return self.code[self.ptr]
        return ''

    def next_token(self) -> Token:
    
        while self.ptr < len(self.code) and self.code[self.ptr] == " ":
            self.ptr += 1 
        
        if self.ptr == len(self.code): return Token(TokenType.EOF)
        
        char     = self.code[self.ptr]
        self.ptr += 1

        # depending on what char we get...

        # 1. check for single chars
        if char in ['(', ')', ';']: 
            # directly makes the token using Char's value :big_biran"
            return Token(kw_dict[char])
        # check for identifier & gates
        if char in ascii_letters_underscore_digits:
            startPtr = self.ptr - 1 # include the current char in our range

            while self.ptr < len(self.code) and self.code[self.ptr] in ascii_letters_underscore_digits:
                self.ptr += 1

            finalLit = self.code[startPtr:self.ptr]

            match finalLit:
                case 'AND'  : return Token(kw_dict[finalLit])
                case 'OR'   : return Token(kw_dict[finalLit])
                case 'NOT'  : return Token(kw_dict[finalLit])
                case 'NAND' : return Token(kw_dict[finalLit])
                case 'NOR'  : return Token(kw_dict[finalLit])
                case 'XOR'  : return Token(kw_dict[finalLit])
                case 'XNOR' : return Token(kw_dict[finalLit])

            return Token(TokenType.IDENTIFIER, finalLit)
        
        # if nothing is returned then...
        raise RuntimeError(f"[TOKENIZATION ERROR] Can't Tokenize {char!r}.") 

    def __iter__(self) -> Generator[Token, None, None]:
        while (token := self.next_token()).type != TokenType.EOF:
            yield token
        yield token # yield (return) the EOF token as well

# ------------------------------------------------------------------

if __name__ == "__main__":
    code = "B AND M AND C"
    tokenizer = Tokenizer(code)
    print(code)
    for tok in tokenizer:
        print(f"\t{tok.type}, {tok.value}")
