# ------------------------------------------------------------------
# AST node definitions + helpers that work on the tree
# ------------------------------------------------------------------

from dataclasses import dataclass

# ------------------------------------------------------------------
# nodes
# ------------------------------------------------------------------

@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class Not:
    operand: "Node"

@dataclass(frozen=True)
class BinOp:
    op:    str          # "AND", "OR", "XOR", "XNOR", "NAND", "NOR"
    left:  "Node"
    right: "Node"

Node = Var | Not | BinOp

@dataclass
class Program:
    statements: list[Node]

# -- operator precedence (lowest -> highest).

BINARY_LEVELS: tuple[tuple[str, ...], ...] = (
    ("OR",  "NOR"),
    ("XOR", "XNOR"),
    ("AND", "NAND"),
)

_PREC = {op: i + 1 for i, level in enumerate(BINARY_LEVELS) for op in level}
_NOT_PREC  = len(BINARY_LEVELS) + 1
_ATOM_PREC = _NOT_PREC + 1

# ------------------------------------------------------------------
# mama mia helpers
# ------------------------------------------------------------------

def variables(node: Node) -> list[str]:
    """Identifiers used in the expression, in order of first appearance."""
    seen: dict[str, None] = {}

    def walk(n: Node) -> None:
        match n:
            case Var(name):        seen.setdefault(name)
            case Not(operand):     walk(operand)
            case BinOp(_, l, r):   walk(l); walk(r)

    walk(node)
    return list(seen)

def to_text(node: Node, min_prec: int = 0) -> str:
    """Expression back to source text, with only the parentheses that are needed."""
    match node:
        case Var(name):
            return name
        case Not(operand):
            text, prec = "NOT " + to_text(operand, _NOT_PREC), _NOT_PREC
        case BinOp(op, left, right):
            prec = _PREC[op]
            # REMEMBER: gates are left-associative: 
            # same-precedence child on the left needs
            # no parens, on the right it does
            text = f"{to_text(left, prec)} {op} {to_text(right, prec + 1)}"
    return f"({text})" if prec < min_prec else text

# ------------------------------------------------------------------
