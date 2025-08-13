#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

from drawing_bot_api import DrawingBot
from drawing_bot_api.shapes import *

# --- NEW: start the serial bridge (portable, no absolute paths) ---
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

# Create the bot
drawing_bot = DrawingBot(unit='mm', speed=200)


#################################
# Shape Functions
#################################

def heart():
    drawing_bot.add_shape(PartialCircle([0, 135], [-40, 110], 25, 1, big_angle=True))
    drawing_bot.add_shape(Line([-40, 110], [0, 75]))
    drawing_bot.add_shape(Line([0, 75], [40, 110]))
    drawing_bot.add_shape(PartialCircle([40, 110], [0, 135], 25, 1, big_angle=True))


def square(width=40, center=[0, 100]):
    side = width / 2
    drawing_bot.add_shape(Line([center[0] - side, center[1] + side], [center[0] + side, center[1] + side]))
    drawing_bot.add_shape(Line([center[0] + side, center[1] + side], [center[0] + side, center[1] - side]))
    drawing_bot.add_shape(Line([center[0] + side, center[1] - side], [center[0] - side, center[1] - side]))
    drawing_bot.add_shape(Line([center[0] - side, center[1] - side], [center[0] - side, center[1] + side]))


def triangle(size=50, center=[0, 100]):
    h = (size * (3 ** 0.5)) / 2  # height of equilateral triangle
    drawing_bot.add_shape(Line([center[0] - size / 2, center[1] - h / 3], [center[0] + size / 2, center[1] - h / 3]))
    drawing_bot.add_shape(Line([center[0] + size / 2, center[1] - h / 3], [center[0], center[1] + 2 * h / 3]))
    drawing_bot.add_shape(Line([center[0], center[1] + 2 * h / 3], [center[0] - size / 2, center[1] - h / 3]))


def star(size=40, center=[0, 110]):  # reduced from 50 to 40
    import math
    points = []
    for i in range(10):
        angle = math.radians(36 * i - 90)
        r = size if i % 2 == 0 else size / 2
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append([x, y])
    for i in range(len(points)):
        drawing_bot.add_shape(Line(points[i], points[(i+1) % len(points)]))


def line_example():
    drawing_bot.add_shape(Line([-30, 80], [40, 100]))


def circle():
    drawing_bot.add_shape(Circle([0, 110], 20))


#################################
# Letters for "Eram"
#################################

def letter_E(x=0, y=100, s=10):
    drawing_bot.add_shape(Line([x, y + s], [x, y - s]))
    drawing_bot.add_shape(Line([x, y + s], [x + s, y + s]))
    drawing_bot.add_shape(Line([x, y], [x + s * 0.8, y]))
    drawing_bot.add_shape(Line([x, y - s], [x + s, y - s]))


def letter_R(x=0, y=100, s=10):
    drawing_bot.add_shape(Line([x, y - s], [x, y + s]))
    drawing_bot.add_shape(PartialCircle([x, y + s], [x, y], s, -1, big_angle=False))
    drawing_bot.add_shape(Line([x, y], [x + s, y - s]))


def letter_A(x=0, y=100, s=10):
    drawing_bot.add_shape(Line([x - s / 2, y - s], [x, y + s]))
    drawing_bot.add_shape(Line([x, y + s], [x + s / 2, y - s]))
    drawing_bot.add_shape(Line([x - s / 4, y], [x + s / 4, y]))


def letter_M(x=0, y=100, s=10):
    drawing_bot.add_shape(Line([x, y - s], [x, y + s]))
    drawing_bot.add_shape(Line([x, y + s], [x + s / 2, y]))
    drawing_bot.add_shape(Line([x + s / 2, y], [x + s, y + s]))
    drawing_bot.add_shape(Line([x + s, y + s], [x + s, y - s]))


def write_eram():
    spacing = 25
    letter_E(x=-spacing * 1.5, y=100, s=10)
    letter_R(x=-spacing * 0.5, y=100, s=10)
    letter_A(x=spacing * 0.5, y=100, s=10)
    letter_M(x=spacing * 1.5, y=100, s=10)


#################################
# Main Menu (now supports word argument)
#################################

DISPATCH = {
    "line": line_example,
    "square": square,
    "triangle": triangle,
    "star": star,
    "heart": heart,
    "circle": circle,
    "eram": write_eram,  # optional word for the name
}

def main():
    # NEW: make sure the serial bridge is running
    ensure_serial_running()

    # If a word is passed (e.g. "star"), use it; otherwise show the old menu.
    if len(sys.argv) >= 2:
        choice_word = sys.argv[1].strip().lower()
        func = DISPATCH.get(choice_word)
        if not func:
            print(f"Unknown shape '{choice_word}'. Valid: {', '.join(DISPATCH.keys())}")
            return
        func()
    else:
        print("Was möchtest du zeichnen?")
        print("1: Kreis (Circle)")
        print("2: Herz (Heart)")
        print("3: Name 'Eram'")
        print("4: Linie (Line)")
        print("5: Quadrat (Square)")
        print("6: Dreieck (Triangle)")
        print("7: Stern (Star)")

        choice = input("Deine Wahl: ").strip()

        # (Keeping your current word-based checks; if you prefer numbers, say so.)
        if choice == 'circle':
            circle()
        elif choice == 'heart':
            heart()
        elif choice == "Eram":
            write_eram()
        elif choice == 'line':
            line_example()
        elif choice == 'square':
            square()
        elif choice == 'triangle':
            triangle()
        elif choice == 'star':
            star()
        else:
            print("Ungültige Eingabe.")
            return

    drawing_bot.plot()
    drawing_bot.execute(promting=True)


if __name__ == "__main__":
    main()
