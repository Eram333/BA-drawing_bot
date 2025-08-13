#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

from drawing_bot_api import DrawingBot
from drawing_bot_api.shapes import Line, PartialCircle

# --- Start the serial bridge (portable, no absolute paths) ---
_serial_proc = None

def ensure_serial_running():
    """Launch drawing_bot_api/serial_com.py in the background if not already running."""
    global _serial_proc
    if _serial_proc and (_serial_proc.poll() is None):
        return  # already running in this process

    # serial_com.py lives inside the package folder next to this file
    api_dir = Path(__file__).resolve().parent / "drawing_bot_api"
    serial_script = api_dir / "serial_com.py"

    if not serial_script.exists():
        print(f"[WARN] serial_com.py not found at: {serial_script}")
        return

    py = sys.executable  # use the current interpreter / venv
    try:
        _serial_proc = subprocess.Popen(
            [py, serial_script.name],
            cwd=str(api_dir),                   # critical: so 'from config import *' works
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        print("[INFO] serial_com started in background.")
    except Exception as e:
        print(f"[ERROR] Could not start serial_com: {e}")

# --- Create the bot ---
drawing_bot = DrawingBot(unit='mm', speed=200)


#################################
# Letter Functions A–Z
# (x, y) = center of letter, s = half height
# width ≈ 1.2*s
#################################

def letter_A(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xL, yB], [x, yT]))
    drawing_bot.add_shape(Line([xR, yB], [x, yT]))
    drawing_bot.add_shape(Line([xL + 0.2*(xR-xL), yM], [xR - 0.2*(xR-xL), yM]))

def letter_B(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))              # stem
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))              # top
    drawing_bot.add_shape(Line([xR, yT], [xR, yM]))              # right upper
    drawing_bot.add_shape(Line([xR, yM], [xL, yM]))              # mid
    drawing_bot.add_shape(Line([xR, yM], [xR, yB]))              # right lower
    drawing_bot.add_shape(Line([xR, yB], [xL, yB]))              # bottom

def letter_C(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xR, yT], [xL, yT]))
    drawing_bot.add_shape(Line([xL, yT], [xL, yB]))
    drawing_bot.add_shape(Line([xL, yB], [xR, yB]))

def letter_D(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))              # stem
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([xR, yT], [xR, yB]))
    drawing_bot.add_shape(Line([xR, yB], [xL, yB]))

def letter_E(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([xL, yM], [xR - 0.2*(xR-xL), yM]))
    drawing_bot.add_shape(Line([xL, yB], [xR, yB]))

def letter_F(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([xL, yM], [xR - 0.2*(xR-xL), yM]))

def letter_G(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xR, yT], [xL, yT]))
    drawing_bot.add_shape(Line([xL, yT], [xL, yB]))
    drawing_bot.add_shape(Line([xL, yB], [xR, yB]))
    drawing_bot.add_shape(Line([xR, yB], [xR, yM]))
    drawing_bot.add_shape(Line([xR, yM], [xR - 0.4*(xR-xL), yM]))

def letter_H(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))
    drawing_bot.add_shape(Line([xR, yB], [xR, yT]))
    drawing_bot.add_shape(Line([xL, yM], [xR, yM]))

def letter_I(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([x,  yB], [x,  yT]))
    drawing_bot.add_shape(Line([xL, yB], [xR, yB]))

def letter_J(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([x,  yT], [x,  yB + 0.2*(yT-yB)]))
    drawing_bot.add_shape(Line([x,  yB + 0.2*(yT-yB)], [xL, yB]))

def letter_K(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))
    drawing_bot.add_shape(Line([xL, yM], [xR, yT]))
    drawing_bot.add_shape(Line([xL, yM], [xR, yB]))

def letter_L(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yT], [xL, yB]))
    drawing_bot.add_shape(Line([xL, yB], [xR, yB]))

def letter_M(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))
    drawing_bot.add_shape(Line([xR, yB], [xR, yT]))
    drawing_bot.add_shape(Line([xL, yT], [x,  yB + 0.4*(yT-yB)]))
    drawing_bot.add_shape(Line([xR, yT], [x,  yB + 0.4*(yT-yB)]))

def letter_N(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))
    drawing_bot.add_shape(Line([xR, yB], [xR, yT]))
    drawing_bot.add_shape(Line([xL, yB], [xR, yT]))

def letter_O(x=0, y=100, s=10):
    # Box O (robust on plotters)
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([xR, yT], [xR, yB]))
    drawing_bot.add_shape(Line([xR, yB], [xL, yB]))
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))

def letter_P(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([xR, yT], [xR, yM]))
    drawing_bot.add_shape(Line([xR, yM], [xL, yM]))

def letter_Q(x=0, y=100, s=10):
    # O with a tail
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([xR, yT], [xR, yB]))
    drawing_bot.add_shape(Line([xR, yB], [xL, yB]))
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))
    drawing_bot.add_shape(Line([x,  y],  [xR, yB]))  # tail

def letter_R(x=0, y=100, s=10):
    # Keep your earlier style with a small bowl using PartialCircle
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xL, yB], [xL, yT]))              # stem
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))              # top bar
    drawing_bot.add_shape(PartialCircle([xL, yT], [xL, yM], 0.9*s, -1, big_angle=False))  # bowl-ish arc
    drawing_bot.add_shape(Line([xL, yM], [xR, yB]))              # leg

def letter_S(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xR, yT], [xL, yT]))
    drawing_bot.add_shape(Line([xL, yT], [xL, yM]))
    drawing_bot.add_shape(Line([xL, yM], [xR, yM]))
    drawing_bot.add_shape(Line([xR, yM], [xR, yB]))
    drawing_bot.add_shape(Line([xR, yB], [xL, yB]))

def letter_T(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([x,  yT], [x,  yB]))

def letter_U(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yT], [xL, yB]))
    drawing_bot.add_shape(Line([xR, yT], [xR, yB]))
    drawing_bot.add_shape(Line([xL, yB], [xR, yB]))

def letter_V(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yT], [x,  yB]))
    drawing_bot.add_shape(Line([xR, yT], [x,  yB]))

def letter_W(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    x1 = xL + 0.25*(xR-xL)
    x2 = xR - 0.25*(xR-xL)
    drawing_bot.add_shape(Line([xL, yT], [x1, yB]))
    drawing_bot.add_shape(Line([x1, yB], [x,  yT - 0.2*(yT-yB)]))
    drawing_bot.add_shape(Line([x,  yT - 0.2*(yT-yB)], [x2, yB]))
    drawing_bot.add_shape(Line([x2, yB], [xR, yT]))

def letter_X(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yB], [xR, yT]))
    drawing_bot.add_shape(Line([xR, yB], [xL, yT]))

def letter_Y(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT, yM = y - s, y + s, y
    drawing_bot.add_shape(Line([xL, yT], [x,  yM]))
    drawing_bot.add_shape(Line([xR, yT], [x,  yM]))
    drawing_bot.add_shape(Line([x,  yM], [x,  yB]))

def letter_Z(x=0, y=100, s=10):
    xL, xR = x - 0.6*s, x + 0.6*s
    yB, yT = y - s, y + s
    drawing_bot.add_shape(Line([xL, yT], [xR, yT]))
    drawing_bot.add_shape(Line([xR, yT], [xL, yB]))
    drawing_bot.add_shape(Line([xL, yB], [xR, yB]))
#################################
# Helpers to write letters/words
#################################

LETTER_FUNCS = {
    'A': letter_A,
    # ... fill in all others: 'B': letter_B, 'C': letter_C, ...
    'R': letter_R,
}

def write_letter(char, x=0, y=100, s=10):
    func = LETTER_FUNCS.get(str(char).upper())
    if not func:
        print(f"[INFO] Letter '{char}' not implemented.")
        return
    func(x, y, s)

def write_word(word, start_x=0, y=100, s=10, spacing=None):
    spacing = spacing if spacing is not None else int(1.6 * s)
    x_pos = start_x
    for ch in str(word):
        if ch == ' ':
            x_pos += spacing
            continue
        func = LETTER_FUNCS.get(ch.upper())
        if func:
            func(x_pos, y, s)
        else:
            print(f"[INFO] Skipping unsupported char '{ch}'.")
        x_pos += spacing


#################################
# Main Menu
#################################

DISPATCH = {
    "letter": lambda: write_letter(input("Letter: ").strip(), x=0, y=100, s=10),
    "word": lambda: write_word(input("Word: ").strip(), start_x=-40, y=100, s=10),
}

def main():
    ensure_serial_running()

    if len(sys.argv) >= 2:
        choice_word = sys.argv[1].strip().lower()
        func = DISPATCH.get(choice_word)
        if not func:
            print(f"Unknown command '{choice_word}'. Valid: {', '.join(DISPATCH.keys())}")
            return
        func()
    else:
        print("Choose: letter | word")
        choice = input("Your choice: ").strip().lower()
        func = DISPATCH.get(choice)
        if func:
            func()
        else:
            print("Invalid choice.")
            return

    drawing_bot.plot()
    drawing_bot.execute(promting=True)


if __name__ == "__main__":
    main()
