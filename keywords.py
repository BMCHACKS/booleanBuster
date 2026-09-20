from token_types import TokenType

kw_dict = {
    # IDENTIFIER
    # any : TokenType.IDENTIFIER,
    # gates
    "AND"  : TokenType.AND,
    "OR"   : TokenType.OR,
    "NOT"  : TokenType.NOT,
    "NOR"  : TokenType.NOR,
    "NAND" : TokenType.NAND,
    "XOR"  : TokenType.XOR,
    "XNOR" : TokenType.XNOR,
    # brackets
    "("    : TokenType.L_BRACKET,
    ")"    : TokenType.R_BRACKET,
    # terminator
    ";"    : TokenType.TERMINATOR,
    # ""   : TokenType.EOF,
}