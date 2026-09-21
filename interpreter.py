# ------------------------------------------------------------------
# The interactive front-end (REPL) (holy sigma)
#
#   A AND NOT B;        enter an expression (the final ';' is added if you forget it)
#   -set vals           prompt for the value of every identifier
#   -set vals A=1 B=0   or set them inline
#   -show TT            truth table
#   -show exp           the expression
#   -show vals          current values
#   -show py            the generated Python
#   -cmp exp            compare 2+ expressions (prompts, or: -cmp exp A AND B; NOT (A NAND B);)
#   -clear              clear the screen
#   -help / -quit
# ------------------------------------------------------------------
import colorama

from colorama     import Back, Fore, Style
from ast_nodes    import Node, to_text, variables
from compare      import compare_expressions
from parser       import ParseError, Parser
from tokenizer    import Tokenizer
from transpiler   import Evaluator, compile_expression
from truth_table  import truth_table

HELP = """\
  <expression>;        enter an expression, e.g.  A AND NOT (B XOR C);
  -set vals            prompt for the value of each identifier
  -set vals A=1 B=0    set values inline
  -show TT             print the truth table
  -show exp            print the current expression
  -show vals           print the current values
  -show py             print the generated Python
  -cmp exp             compare 2+ expressions (prompts, one per line, blank line to finish)
  -cmp exp <e1>; <e2>; compare expressions given inline, e.g.  -cmp exp A AND B; NOT (A NAND B);
  -clear               clear the screen
  -help                this message
  -quit                exit
Gates: AND OR NOT XOR XNOR NAND NOR (precedence: NOT > AND/NAND > XOR/XNOR > OR/NOR)"""

_BOOLS = {"0": False, "1": True, "f": False, "t": True, "false": False, "true": True}

def _parse_bool(text: str) -> bool | None:
    return _BOOLS.get(text.strip().lower())

class Session:
    def __init__(self) -> None:
        self.expr:   Node | None      = None
        self.source: str              = ""
        self.fn:     Evaluator | None = None
        self.values: dict[str, bool]  = {}

    # -- expressions -----------------------------------------------

    @staticmethod
    def _parse(code: str) -> list[Node]:
        if not code.rstrip().endswith(";"):
            code += ";"
        return Parser(Tokenizer(code)).parse_program().statements

    def run_expression(self, code: str) -> None:
        for stmt in self._parse(code):
            self.expr            = stmt
            self.source, self.fn = compile_expression(stmt)
            self._report()

    def _report(self) -> None:
        names   = variables(self.expr)
        missing = [n for n in names if n not in self.values]
        text    = to_text(self.expr)
        if missing:
            print(f"{text}\n  (no values for: {', '.join(missing)} - use -set vals)")
        else:
            print(f"{text} = {int(self.fn(self.values))}")

    # -- commands --------------------------------------------------

    def run_command(self, line: str) -> bool:
        """Returns False when the user wants to quit."""
        parts = line[1:].split(maxsplit=1)
        if not parts:
            print("Empty command. Try -help.")
            return True
        cmd  = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""      # raw text after the command
        args = rest.split()

        if   cmd in ("quit", "exit"): return False
        elif cmd == "help":           print(HELP)
        elif cmd == "set":            self._cmd_set(args)
        elif cmd == "show":           self._cmd_show(args)
        elif cmd == "cmp":            self._cmd_cmp(rest)
        elif cmd == "clear":          self._cmd_clear()
        else:                         print(f"Unknown command '-{cmd}'. Try -help.")
        return True

    def _cmd_set(self, args: list[str]) -> None:
        if not args or args[0].lower() != "vals":
            print("Usage: -set vals [NAME=0|1 ...]")
            return
        if self.expr is None:
            print("Enter an expression first.")
            return

        names = variables(self.expr)
        if args[1:]:
            self._set_inline(names, args[1:])
        else:
            self._set_interactive(names)
        self._report()

    def _set_inline(self, names: list[str], assignments: list[str]) -> None:
        for item in assignments:
            name, _, raw = item.partition("=")
            value = _parse_bool(raw)
            if name not in names or value is None:
                print(f"  ignored {item!r} (expected NAME=0|1 with NAME in {names})")
            else:
                self.values[name] = value

    def _set_interactive(self, names: list[str]) -> None:
        for name in names:
            current = self.values.get(name)
            hint    = f" [{int(current)}]" if current is not None else ""
            while True:
                raw = input(f"  {name}{hint} = ")
                if raw.strip() == "" and current is not None:
                    break                          # keep the old value
                value = _parse_bool(raw)
                if value is not None:
                    self.values[name] = value
                    break
                print("    enter 0/1 (or T/F)")

    def _cmd_show(self, args: list[str]) -> None:
        what = args[0].lower() if args else ""
        if what not in ("tt", "exp", "vals", "py"):
            print("Usage: -show TT | exp | vals | py")
            return
        if self.expr is None:
            print("Enter an expression first.")
            return

        if what == "tt":
            print(truth_table(self.expr, self.fn))
        elif what == "exp":
            print(to_text(self.expr))
        elif what == "py":
            print(self.source)
        else:
            print(", ".join(f"{n}={int(self.values[n])}" for n in variables(self.expr)
                            if n in self.values) or "(no values set)")

    def _cmd_cmp(self, rest: str) -> None:
        sub, _, code = rest.strip().partition(" ")
        if sub.lower() != "exp":
            print("Usage: -cmp exp [expression; expression; ...]")
            return

        code  = code.strip()
        exprs = self._parse(code) if code else self._collect_expressions()
        if exprs is None:
            return
        if len(exprs) < 2:
            print("Need at least 2 expressions to compare.")
            return
        print(compare_expressions(exprs))

    def _collect_expressions(self) -> list[Node] | None:
        """Prompt for expressions until a blank line. None = cancelled."""
        exprs: list[Node] = []
        print("  Enter one expression per line, blank line to finish.")
        while True:
            raw = input(f"  E{len(exprs) + 1} > ").strip()
            if not raw:
                if len(exprs) >= 2:
                    return exprs
                print("  Cancelled (need at least 2 expressions).")
                return None
            try:
                exprs.extend(self._parse(raw))
            except (ParseError, RuntimeError) as err:
                print(f"  {err}")

    @staticmethod
    def _cmd_clear() -> None:
        # ANSI clear screen + cursor home; colorama translates it on old Windows consoles
        print("\033[2J\033[H", end="")

def _print_fun():
    print(Fore.GREEN + "=====================================================================" + Style.RESET_ALL)
    print(Fore.GREEN + "###   ##   ##  #    ####  ##  #  #    ###  #  #  ### ##### #### ###  " + Style.RESET_ALL)
    print(Fore.GREEN + "#  # #  # #  # #    #    #  # ## #    #  # #  # #      #   #    #  # " + Style.RESET_ALL)
    print(Fore.GREEN + "###  #  # #  # #    ###  #### # ##    ###  #  #  ##    #   ###  ###  " + Style.RESET_ALL)
    print(Fore.GREEN + "#  # #  # #  # #    #    #  # #  #    #  # #  #    #   #   #    # #  " + Style.RESET_ALL)
    print(Fore.GREEN + "###   ##   ##  #### #### #  # #  #    ###   ##  ###    #   #### #  # " + Style.RESET_ALL)
    print(Fore.GREEN + "=====================================================================" + Style.RESET_ALL)
    print(Fore.GREEN + "                    Boolean Buster V1.0 - BY BMC                     " + Style.RESET_ALL)
    print(Fore.GREEN + "=====================================================================" + Style.RESET_ALL)

# ------------------------------------------------------------------

def _start() -> None:
    colorama.init()
    session = Session()
    _print_fun()
    print("Boolean expression interpreter. Type -help for commands.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        try:
            if line.startswith("-"):
                if not session.run_command(line):
                    break
            else:
                session.run_expression(line)
        except (ParseError, RuntimeError, ValueError) as err:   # RuntimeError = tokenizer errors
            print(err)
        except (EOFError, KeyboardInterrupt):                   # Ctrl-C / Ctrl-D inside a prompt
            print("\n(cancelled)")


# ------------------------------------------------------------------
