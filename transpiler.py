# ------------------------------------------------------------------
# AST -> Python source -> callable
#
# Identifiers are looked up as v["NAME"] in a dict instead of being emitted as
# Python variables, so names like `class`, `lambda` or `None` can't break the output.
# ------------------------------------------------------------------

from typing    import Callable

from ast_nodes import BinOp, Node, Not, Var

# {l} / {r} are the already-transpiled operands. Everything is parenthesised, so
# the generated code never depends on Python's own precedence rules.
_TEMPLATES = {
    "AND":  "({l} and {r})",
    "OR":   "({l} or {r})",
    "XOR":  "({l} != {r})",
    "XNOR": "({l} == {r})",
    "NAND": "(not ({l} and {r}))",
    "NOR":  "(not ({l} or {r}))",
}

Evaluator = Callable[[dict[str, bool]], bool]

def to_python(node: Node) -> str:
    """Python expression (in terms of a dict `v`) equivalent to the AST."""
    match node:
        case Var(name):
            return f"v[{name!r}]"
        case Not(operand):
            return f"(not {to_python(operand)})"
        case BinOp(op, left, right):
            return _TEMPLATES[op].format(l=to_python(left), r=to_python(right))
    raise TypeError(f"Unknown AST node: {node!r}")

def compile_expression(node: Node) -> tuple[str, Evaluator]:
    """Returns (python_source, function). Call the function with {name: bool}."""
    source = "lambda v: " + to_python(node)
    # no builtins needed: the generated code only uses and/or/not/==/!= and dict lookups
    return source, eval(source, {"__builtins__": {}})

# ------------------------------------------------------------------

if __name__ == "__main__":
    from parser    import Parser
    from tokenizer import Tokenizer
    tree = Parser(Tokenizer("A XOR NOT B;")).parse_program().statements[0]
    src, fn = compile_expression(tree)
    print(src)
    print(fn({"A": True, "B": True}))

# ------------------------------------------------------------------
