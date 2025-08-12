#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

from drawing_bot_api import DrawingBot
from drawing_bot_api.shapes import *  # Line, Circle, PartialCircle, etc.

# --- Launch the serial bridge so the bot can talk to the microcontroller ---
# This part calls the file: drawing_bot_api/serial_com.py
# That script handles the communication between Python and the robot's microcontroller
# Students do NOT need to change anything here.
_serial_proc = None

def ensure_serial_running():
    """Start drawing_bot_api/serial_com.py in the background (only if not running)."""
    global _serial_proc
    if _serial_proc and (_serial_proc.poll() is None):
        return  # Already running

    api_dir = Path(__file__).resolve().parent / "drawing_bot_api"
    serial_script = api_dir / "serial_com.py"

    if not serial_script.exists():
        print(f"[WARN] serial_com.py not found at: {serial_script}")
        return

    py = sys.executable  # current Python interpreter
    try:
        _serial_proc = subprocess.Popen(
            [py, serial_script.name],
            cwd=str(api_dir),                   # so "from config import *" works
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        print("[INFO] serial_com started in background.")
    except Exception as e:
        print(f"[ERROR] Could not start serial_com: {e}")


# --- Create the bot object ---
drawing_bot = DrawingBot(unit='mm', speed=200)


#################################
# Shape Functions (students fill in)
#################################

def heart():
    """
    TASK: Draw a heart shape using arcs and lines.
    Hints:
    - Use PartialCircle(start_point, end_point, radius, direction, big_angle=True) for the two lobes.
    - Use Line(start_point, end_point) for the "V" at the bottom.
    - Example points: [0, 135], [-40, 110], [40, 110], [0, 75]
    """
    pass


def square(width=40, center=[0, 100]):
    """
    TASK: Draw a square of given width centered at 'center'.
    Hints:
    - Calculate half side length: side = width / 2
    - Use four Line(...) commands to connect corners in order.
    """
    pass


def triangle(size=50, center=[0, 100]):
    """
    TASK: Draw an equilateral triangle centered at 'center'.
    Hints:
    - Height h = (size * (3 ** 0.5)) / 2
    - Start from the base, then draw the two slanted sides back to the start point.
    """
    pass


def star(size=40, center=[0, 110]):
    """
    TASK: Draw a 5-pointed star.
    Hints:
    - Loop from i = 0 to 9 to create 10 alternating points (outer and inner).
    - Outer radius = size, inner radius = size/2.
    - Angle = math.radians(36 * i - 90)
    - Connect each point to the next with Line.
    """
    pass


def line_example():
    """
    TASK: Draw a single straight line.
    Hints:
    - Choose two points [x1, y1] and [x2, y2] and use Line(start, end).
    - Example: [-30, 80] to [40, 100]
    """
    pass


def circle():
    """
    TASK: Draw a full circle.
    Hints:
    - Use Circle(center, radius)
    - Example: Circle([0, 110], 20)
    """
    pass


#################################
# Letters for "Eram" (bonus task)
#################################

def letter_E(x=0, y=100, s=10):
    """TASK: Draw letter E with 1 vertical line and 3 horizontal lines."""
    pass

def letter_R(x=0, y=100, s=10):
    """TASK: Draw letter R with 1 vertical line, a curved bowl (PartialCircle), and a diagonal leg."""
    pass

def letter_A(x=0, y=100, s=10):
    """TASK: Draw letter A with two legs and a crossbar."""
    pass

def letter_M(x=0, y=100, s=10):
    """TASK: Draw letter M with two verticals and two diagonals."""
    pass

def write_eram():
    """TASK: Call letter_E, letter_R, letter_A, letter_M in sequence with spacing."""
    pass


#################################
# Main Menu
#################################

DISPATCH = {
    "line": line_example,
    "square": square,
    "triangle": triangle,
    "star": star,
    "heart": heart,
    "circle": circle,
    "eram": write_eram,
}

def main():
    ensure_serial_running()

    if len(sys.argv) >= 2:
        choice_word = sys.argv[1].strip().lower()
        func = DISPATCH.get(choice_word)
        if not func:
            print(f"Unknown shape '{choice_word}'. Valid: {', '.join(DISPATCH.keys())}")
            return
        func()
    else:
        print("What do you want to draw?")
        print("circle, heart, eram, line, square, triangle, star")
        choice = input("Your choice: ").strip().lower()
        func = DISPATCH.get(choice)
        if func:
            func()
        else:
            print("Invalid input.")
            return

    drawing_bot.plot()
    drawing_bot.execute(promting=True)


if __name__ == "__main__":
    main()
