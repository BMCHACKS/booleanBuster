# ------------------------------------------------------------------
# Recursive-descent parser: tokens -> AST
#
# program     := statement* EOF
# statement   := or_exp ';'
# or_exp      := xor_exp  ((OR  | NOR)  xor_exp)*
# xor_exp     := and_exp  ((XOR | XNOR) and_exp)*
# and_exp     := unary_exp ((AND | NAND) unary_exp)*
# unary_exp   := NOT unary_exp | primary
# primary     := IDENTIFIER | '(' or_exp ')'
# ------------------------------------------------------------------

from typing      import Iterable

from ast_nodes   import BINARY_LEVELS, BinOp, Node, Not, Program, Var
from keywords    import kw_dict
from token_types import TokenType
from tokenizer   import Token

# resolve TokenTypes through kw_dict so this file doesn't depend on enum member names
LPAREN    = kw_dict['(']
RPAREN    = kw_dict[')']
SEMICOLON = kw_dict[';']
NOT       = kw_dict['NOT']

# TokenType -> gate name, and TokenType -> source text (for error messages)
GATE_NAME = {kw_dict[g]: g for g in ("AND", "OR", "NOT", "XOR", "XNOR", "NAND", "NOR")}
SYMBOL    = {tt: text for text, tt in kw_dict.items()}

class ParseError(Exception):
    pass

def _describe(tok: Token) -> str:
    if tok.type == TokenType.EOF:        return "end of input"
    if tok.type == TokenType.IDENTIFIER: return f"identifier {tok.value!r}"
    return repr(SYMBOL.get(tok.type, tok.type))

class Parser:
    def __init__(self, tokens: Iterable[Token]) -> None:
        # the Tokenizer always ends with an EOF token, so self.pos never runs off the end
        self.tokens = list(tokens)
        self.pos    = 0

    # -- token helpers ---------------------------------------------

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _expect(self, tt: TokenType, what: str) -> Token:
        tok = self._peek()
        if tok.type != tt:
            raise ParseError(f"[PARSE ERROR] Expected {what}, got {_describe(tok)}.")
        return self._advance()

    # -- grammar rules ---------------------------------------------

    def parse_program(self) -> Program:
        statements: list[Node] = []
        while self._peek().type != TokenType.EOF:
            statements.append(self._statement())
        return Program(statements)

    def _statement(self) -> Node:
        expr = self._binary(0)
        self._expect(SEMICOLON, "';' or a gate")
        return expr

    def _binary(self, level: int) -> Node:
        # one method handles all three binary precedence levels
        if level == len(BINARY_LEVELS):
            return self._unary()

        left = self._binary(level + 1)
        while GATE_NAME.get(self._peek().type) in BINARY_LEVELS[level]:
            op    = GATE_NAME[self._advance().type]
            right = self._binary(level + 1)
            left  = BinOp(op, left, right)
        return left

    def _unary(self) -> Node:
        if self._peek().type == NOT:
            self._advance()
            return Not(self._unary())
        return self._primary()

    def _primary(self) -> Node:
        tok = self._peek()
        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return Var(tok.value)
        if tok.type == LPAREN:
            self._advance()
            expr = self._binary(0)
            self._expect(RPAREN, "')'")
            return expr
        raise ParseError(f"[PARSE ERROR] Expected an identifier, 'NOT' or '(', got {_describe(tok)}.")

# ------------------------------------------------------------------

if __name__ == "__main__":
    from tokenizer import Tokenizer
    from ast_nodes import to_text
    for src in ("A AND NOT B OR C;", "A NAND (B XOR C) NOR D;"):
        prog = Parser(Tokenizer(src)).parse_program()
        print(src, "->", prog.statements[0])
        print("   ", to_text(prog.statements[0]))

# ------------------------------------------------------------------
