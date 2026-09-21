'''
    ###   ##   ##  #    ####  ##  #  #    ###  #  #  ### ##### #### ### 
    #  # #  # #  # #    #    #  # ## #    #  # #  # #      #   #    #  #
    ###  #  # #  # #    ###  #### # ##    ###  #  #  ##    #   ###  ### 
    #  # #  # #  # #    #    #  # #  #    #  # #  #    #   #   #    # # 
    ###   ##   ##  #### #### #  # #  #    ###   ##  ###    #   #### #  #

    ^ is that even readable lol? 
    
    Inspired by Proteus, after I got tired of manually placing gates to verify outputs for expressions.
    - BMC | 20/09/2026
'''

import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path
 
REQUIREMENTS_FILE = Path(__file__).with_name("requirements.txt")   
REQUIRED_MODULES  = ("colorama",)                                  
 
def ensure_requirements() -> None:
    missing = [m for m in REQUIRED_MODULES if importlib.util.find_spec(m) is None]
    if not missing:
        return
 
    print(f"Missing required package(s): {', '.join(missing)}. Installing...")
    target = ["-r", str(REQUIREMENTS_FILE)] if REQUIREMENTS_FILE.exists() else missing
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *target])
    except (subprocess.CalledProcessError, FileNotFoundError):
        exe = Path(sys.executable).name
        print("\nCouldn't install the requirements automatically. Run this yourself, then start again:")
        print(f"    {exe} -m pip install {' '.join(target)}")
        print("(If pip says the environment is 'externally managed', create a virtual environment first:")
        print(f"    {exe} -m venv .venv  and activate it)")
        sys.exit(1)
 
    importlib.invalidate_caches() 
 
def main() -> None:
    ensure_requirements()
    from animation   import play_animation
    from interpreter import _start
    play_animation()
    _start()
 
if __name__ == "__main__":
    main()
