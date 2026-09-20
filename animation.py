# BMC animation - I'm somwhat of an Animator myself B)

import time
import colorama

from colorama import Fore, Style

# block ref
GLYPHS = {
    "B": ["█▀▀▀▄", "█▀▀▀▄", "█▄▄▄▀"],
    "M": ["█▄ ▄█", "█ ▀ █", "█   █"],
    "C": ["▄▀▀▀▄", "█    ", "▀▄▄▄▀"],
    " ": ["     ", "     ", "     "],
}

FRAMES = [
    'B\nMC',   
    'BC\nM',    
    'BC\n M',   
    ' C\nBM',   
    'C\nBM',    
    'CM\nB',    
    'CM\n B',   
    ' M\nCB',   
    'M\nCB',    
    'MB\nC',    
    'MB\n C',   
    ' B\nMC',    
]

def render(frame: str) -> str:
    rows = []
    for line in frame.split("\n"):
        line = line.ljust(2)                      
        for i in range(3):
            rows.append(" ".join(GLYPHS[ch][i] for ch in line))
    return "\n".join(rows)

def play_animation(loops: int = 1, delay: float = .2) -> None:
    colorama.just_fix_windows_console()

    frames = [render(f) for f in FRAMES]
    height = frames[0].count("\n") + 1

    i = 0
    # clr = [Fore.RED, Fore.LIGHTRED_EX, Fore.GREEN, Fore.LIGHTGREEN_EX, Fore.BLUE, Fore.LIGHTBLUE_EX, Fore.YELLOW, Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.LIGHTMAGENTA_EX]
    clr = [Fore.GREEN, Fore.LIGHTGREEN_EX]
    for _ in range(loops):
        for frame in frames:
            print(clr[i] + frame + Style.RESET_ALL)
            print(f"\033[{height}A", end="") # cursor fix
            time.sleep(delay)
            i = (i+1) % len(clr)

    print("\033[J", end="") # erase

# ------------------------------------------------------------------

if __name__ == "__main__":
    import colorama
    colorama.init()
    play_animation()

# ------------------------------------------------------------------