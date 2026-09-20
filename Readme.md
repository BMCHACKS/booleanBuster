# booleanbuster

An interactive boolean-expression interpreter for the terminal. Type an expression, set the
values of its variables, print its truth table, or compare several expressions to see whether
they're equivalent.

## Usage

Start it with `booleanbuster` (or `python -m booleanbuster`), then type expressions ending in `;`
(the final `;` is added for you if you forget it):

```
> A AND NOT (B XOR C);
> -set vals A=1 B=0 C=1
> -show TT
> -cmp exp (A NOR B) NOR (A NOR B); A OR B;
```

### Language

Gates: `AND`, `OR`, `NOT`, `XOR`, `XNOR`, `NAND`, `NOR` (uppercase). Identifiers are letters,
digits and `_`. Use parentheses to group.

Precedence, highest first: `NOT`, then `AND`/`NAND`, then `XOR`/`XNOR`, then `OR`/`NOR`.
Gates of the same level chain left to right, so `A NAND B NAND C` means `(A NAND B) NAND C`.

### Commands

| Command | What it does |
|---|---|
| `-set vals` | prompt for the value of each variable (or inline: `-set vals A=1 B=0`) |
| `-show TT` | print the truth table |
| `-show exp` | print the current expression |
| `-show vals` | print the current values |
| `-show py` | print the Python the expression compiles to |
| `-cmp exp` | compare two or more expressions (prompts, or inline: `-cmp exp A NAND B; NOT (A AND B);`) |
| `-clear` | clear the screen |
| `-help`, `-quit` | help / exit |

## License

MIT, see [LICENSE](LICENSE).