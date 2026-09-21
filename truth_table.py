# ------------------------------------------------------------------
# Truth table generation (coloured with colorama)
# ------------------------------------------------------------------

from itertools import product

from colorama import Back, Fore, Style

from ast_nodes  import Node, to_text, variables
from transpiler import Evaluator

MAX_VARIABLES = 12   # 2**12 = 4096 rows, more than that is just a wall of text

def _paint(text: str, *styles: str) -> str:
    return "".join(styles) + text + Style.RESET_ALL

def truth_table(expr: Node, fn: Evaluator) -> str:
    names = variables(expr)
    if len(names) > MAX_VARIABLES:
        raise ValueError(f"Too many variables for a truth table ({len(names)} > {MAX_VARIABLES}).")

    header = names + [to_text(expr)]
    widths = [len(h) | 1 for h in header]

    head = [_paint(h.center(w), Style.BRIGHT, Fore.CYAN) for h, w in zip(names, widths)]
    head.append(_paint(header[-1].center(widths[-1]), Style.BRIGHT))

    lines = [" │ ".join(head), "─┼─".join("─" * w for w in widths)]

    for combo in product((False, True), repeat=len(names)):
        cells = [_paint(str(int(b)).center(w), Fore.CYAN) for b, w in zip(combo, widths)]

        result = fn(dict(zip(names, combo)))
        style  = (Back.GREEN, Fore.WHITE) if result else (Back.RED, Fore.WHITE)
        cells.append(_paint(str(int(result)).center(widths[-1]), *style, Style.BRIGHT))

        lines.append(" │ ".join(cells))
    return "\n".join(lines)

# ------------------------------------------------------------------
