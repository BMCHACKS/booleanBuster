# ------------------------------------------------------------------
# Compare two or more expressions side by side (coloured with colorama)
#
# All expressions are evaluated over the UNION of their variables, so
# `A AND B` and `A AND (B OR C)` can be compared too (the first one just
# ignores C).
# ------------------------------------------------------------------

from itertools import product

from colorama   import Back, Fore, Style

from .ast_nodes    import Node, to_text, variables
from .transpiler   import compile_expression
from .truth_table  import MAX_VARIABLES

def _paint(text: str, *styles: str) -> str:
    # pad BEFORE colouring, otherwise the invisible ANSI codes break the alignment
    return "".join(styles) + text + Style.RESET_ALL

def compare_expressions(exprs: list[Node]) -> str:
    fns    = [compile_expression(e)[1] for e in exprs]
    labels = [f"E{i}" for i in range(1, len(exprs) + 1)]
    names  = list(dict.fromkeys(n for e in exprs for n in variables(e)))

    if len(names) > MAX_VARIABLES:
        raise ValueError(f"Too many variables to compare ({len(names)} > {MAX_VARIABLES}).")

    # ---- evaluate every row ---------------------------------------
    rows: list[tuple[tuple[bool, ...], list[bool]]] = []
    for combo in product((False, True), repeat=len(names)):
        env = dict(zip(names, combo))
        rows.append((combo, [fn(env) for fn in fns]))

    # ---- layout ---------------------------------------------------
    header  = names + labels + ["match"]
    # odd widths, so the 1-character 0/1 cells sit exactly in the middle of their column
    widths  = [len(h) | 1 for h in header]
    n_vars  = len(names)

    def fmt_header() -> str:
        return " | ".join(_paint(h.center(w), Style.BRIGHT) for h, w in zip(header, widths))

    lines = [
        *(f"{_paint(lbl, Style.BRIGHT)}: {to_text(e)}" for lbl, e in zip(labels, exprs)),
        "",
        fmt_header(),
        "-+-".join("-" * w for w in widths),
    ]

    differing = 0
    for combo, results in rows:
        cells = [str(int(b)).center(w) for b, w in zip(combo, widths)]

        for r, w in zip(results, widths[n_vars:]):
            cells.append(_paint(str(int(r)).center(w), Fore.GREEN if r else Fore.RED))

        if len(set(results)) == 1:
            cells.append(_paint("yes".center(widths[-1]), Fore.GREEN))
        else:
            differing += 1
            cells.append(_paint("NO!".center(widths[-1]), Back.RED, Fore.WHITE, Style.BRIGHT))

        lines.append(" | ".join(cells))

    # ---- verdict --------------------------------------------------
    lines.append("")
    if differing == 0:
        lines.append(_paint(f"All {len(exprs)} expressions are equivalent "
                            f"(same output in all {len(rows)} rows).", Fore.GREEN, Style.BRIGHT))
    else:
        lines.append(_paint(f"Not equivalent: outputs differ in {differing} of {len(rows)} rows.",
                            Fore.RED, Style.BRIGHT))
        if len(exprs) > 2:
            # expressions with identical output columns are equivalent to each other
            groups: dict[tuple[bool, ...], list[str]] = {}
            for i, label in enumerate(labels):
                groups.setdefault(tuple(r[i] for _, r in rows), []).append(label)
            shown = "  ".join("{" + ", ".join(g) + "}" for g in groups.values())
            lines.append(f"Equivalent groups: {shown}")

    return "\n".join(lines)

# ------------------------------------------------------------------
