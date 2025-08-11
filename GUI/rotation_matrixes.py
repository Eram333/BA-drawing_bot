import sys
import random
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QPushButton, QApplication, QLabel, QScrollArea, QFrame
)
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QTimer, QPointF


# -----------------------------
# Canvas that draws the triangle goal + 3 colored lines
# Each colored line is drawn centered at the fixed midpoint
# of its corresponding triangle edge (so shuffling only changes angle).
# -----------------------------
class TriangleCanvas(QWidget):
    def __init__(self, get_vectors_func, base_vectors, show_anchors=True):
        super().__init__()
        self.get_vectors = get_vectors_func    # returns current vectors (list of np.array([x, y]))
        self.base_vectors = base_vectors       # target triangle edge vectors (define fixed midpoints)
        self.setMinimumHeight(300)
        self.show_anchors = show_anchors

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fixed triangle corners (goal)
        anchors = [
            QPointF(self.width() / 2, 100),               # top
            QPointF(self.width() / 2 + 100, 250),         # right base
            QPointF(self.width() / 2 - 100, 250)          # left base
        ]

        # Dashed goal triangle
        pen_outline = QPen(QColor("lightgray"), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen_outline)
        painter.drawLine(anchors[0], anchors[1])
        painter.drawLine(anchors[1], anchors[2])
        painter.drawLine(anchors[2], anchors[0])

        # Optional corner dots
        if self.show_anchors:
            painter.setBrush(QColor("yellow"))
            for a in anchors:
                painter.drawEllipse(a, 5, 5)

        # Midpoints of the 3 goal edges (fixed centers for drawing)
        centers = [
            QPointF(anchors[i].x() + self.base_vectors[i][0] / 2.0,
                    anchors[i].y() + self.base_vectors[i][1] / 2.0)
            for i in range(3)
        ]

        # Draw the current lines centered at their midpoints
        colors = ['red', 'green', 'blue']
        vectors = self.get_vectors()
        for i, vec in enumerate(vectors):
            if not isinstance(vec, np.ndarray):
                continue
            cx, cy = centers[i].x(), centers[i].y()
            start = QPointF(cx - vec[0] / 2.0, cy - vec[1] / 2.0)
            end   = QPointF(cx + vec[0] / 2.0, cy + vec[1] / 2.0)
            painter.setPen(QPen(QColor(colors[i]), 3))
            painter.drawLine(start, end)


# -----------------------------
# Main widget with:
# - Single-line rotation demo (top)
# - Triangle challenge (bottom)
# -----------------------------
class RotationMatrixWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Target triangle edge vectors (from each corner to the next)
        # These define both the "correct" directions/lengths AND the fixed midpoints.
        self.solution_vectors = [
            np.array([-100.0, 150.0]),  # top corner edge (toward left base)
            np.array([-100.0, -150.0]), # right base edge (toward top)
            np.array([200.0, 0.0])      # left base edge (toward right base)
        ]
        # Edge lengths (for keeping length constant)
        self.edge_lengths = [float(np.linalg.norm(v)) for v in self.solution_vectors]

        # --- Single line rotation state ---
        self.original_vector = np.array([100.0, 0.0], dtype=np.float64)
        self.current_vector = self.original_vector.copy()
        self.target_vector = self.original_vector.copy()
        self.steps = 0
        self.step_vector = np.array([0.0, 0.0])
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_single_line_animation)
        self.single_matrix_inputs = [[QLineEdit() for _ in range(3)] for _ in range(3)]

        # --- Triangle lines state (start aligned with goal) ---
        self.triangle_vectors = [v.copy() for v in self.solution_vectors]              # base for applying new rotations
        self.current_triangle_vectors = [v.copy() for v in self.solution_vectors]      # what we draw
        self.target_triangle_vectors = [v.copy() for v in self.solution_vectors]       # animation target
        self.triangle_step_vectors = [np.array([0.0, 0.0]) for _ in range(3)]
        self.triangle_steps = 0
        self.triangle_timer = QTimer()
        self.triangle_timer.timeout.connect(self.update_triangle_animation)
        self.triangle_matrix_inputs = []  # 3 matrices, one per line

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # =========================
        # Single Line Rotation (demo)
        # =========================
        single_frame = QFrame()
        single_layout = QVBoxLayout(single_frame)
        single_layout.addWidget(QLabel("Single Line Rotation:"))

        self.single_canvas = QWidget()
        self.single_canvas.setMinimumHeight(200)
        self.single_canvas.paintEvent = self.paint_single_line
        single_layout.addWidget(self.single_canvas)

        grid = QGridLayout()
        for i in range(3):
            for j in range(3):
                box = self.single_matrix_inputs[i][j]
                box.setText("1.0" if i == j else "0.0")
                box.setFixedWidth(50)
                box.setAlignment(Qt.AlignmentFlag.AlignCenter)
                grid.addWidget(box, i, j)

        matrix_frame = QFrame()
        matrix_frame.setLayout(grid)
        matrix_frame.setFrameShape(QFrame.Shape.StyledPanel)

        apply_button = QPushButton("Apply Rotation")
        apply_button.clicked.connect(self.apply_single_matrix)

        single_layout.addWidget(QLabel("Enter 3×3 Rotation Matrix:"))
        single_layout.addWidget(matrix_frame)
        single_layout.addWidget(apply_button)
        content_layout.addWidget(single_frame)

        # =========================
        # Triangle Challenge
        # =========================
        triangle_frame = QFrame()
        triangle_layout = QVBoxLayout(triangle_frame)
        triangle_layout.addWidget(QLabel(
            "Triangle Challenge: Shuffle rotates each line around its midpoint.\n"
            "Use 3×3 rotation matrices to bring them back to match the dashed triangle."
        ))

        self.triangle_canvas = TriangleCanvas(
            get_vectors_func=lambda: self.current_triangle_vectors,
            base_vectors=self.solution_vectors,
            show_anchors=True
        )
        triangle_layout.addWidget(self.triangle_canvas)

        # Controls: Shuffle + Reset
        buttons_row = QHBoxLayout()
        shuffle_button = QPushButton("Shuffle (rotate around centers)")
        shuffle_button.clicked.connect(self.shuffle_triangle_midpoints)
        buttons_row.addWidget(shuffle_button)

        reset_button = QPushButton("Reset to triangle")
        reset_button.clicked.connect(self.reset_triangle)
        buttons_row.addWidget(reset_button)

        triangle_layout.addLayout(buttons_row)

        # Per-line rotation matrices
        for i in range(3):
            triangle_layout.addWidget(QLabel(f"Line {i + 1} Rotation Matrix:"))
            grid = QGridLayout()
            inputs = []
            for r in range(3):
                row = []
                for c in range(3):
                    le = QLineEdit()
                    le.setText("1.0" if r == c else "0.0")
                    le.setFixedWidth(50)
                    le.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    grid.addWidget(le, r, c)
                    row.append(le)
                inputs.append(row)
            self.triangle_matrix_inputs.append(inputs)

            button = QPushButton(f"Apply to Line {i + 1}")
            button.clicked.connect(lambda _, idx=i: self.apply_triangle_matrix(idx))
            triangle_layout.addLayout(grid)
            triangle_layout.addWidget(button)

        content_layout.addWidget(triangle_frame)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    # -----------------------------
    # Single Line Rotation (top demo)
    # -----------------------------
    def apply_single_matrix(self):
        try:
            M = np.array([[float(self.single_matrix_inputs[i][j].text())
                           for j in range(3)] for i in range(3)], dtype=float)
            unit = np.array([1.0, 0.0, 0.0], dtype=float)
            rotated = M @ unit
            v2 = rotated[:2]
            n = np.linalg.norm(v2)
            if np.isclose(n, 0.0):
                raise ValueError("Rotation resulted in a zero vector.")
            length = np.linalg.norm(self.original_vector)
            self.target_vector = (v2 / n) * length
            self.steps = 20
            self.step_vector = (self.target_vector - self.current_vector) / self.steps
            self.timer.start(20)
        except Exception as e:
            print(f"Unexpected error: {e}")

    def update_single_line_animation(self):
        if self.steps > 0:
            self.current_vector += self.step_vector
            self.steps -= 1
            self.single_canvas.update()
        else:
            self.timer.stop()

    def paint_single_line(self, event):
        painter = QPainter(self.single_canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.single_canvas.width() // 2, self.single_canvas.height() // 2
        painter.translate(w, h)
        painter.setPen(QPen(QColor("blue"), 4))
        half_vec = self.current_vector / 2.0
        start = QPointF(-half_vec[0],  half_vec[1])
        end   = QPointF( half_vec[0], -half_vec[1])
        painter.drawLine(start, end)

    # -----------------------------
    # Triangle Challenge: Apply matrix to a single line
    # -----------------------------
    def apply_triangle_matrix(self, idx: int):
        try:
            M = np.array([
                [float(self.triangle_matrix_inputs[idx][i][j].text()) for j in range(3)]
                for i in range(3)
            ], dtype=float)

            # Apply matrix to the current vector (students can iteratively correct)
            base_vec = self.current_triangle_vectors[idx].copy()
            v3 = np.array([base_vec[0], base_vec[1], 0.0], dtype=float)
            r3 = M @ v3
            r2 = r3[:2]
            n = np.linalg.norm(r2)
            if np.isclose(n, 0.0):
                raise ValueError("Rotation resulted in a zero vector.")

            # Keep the length equal to the goal edge length for this line
            fixed_len = self.edge_lengths[idx]
            rotated_fixed = (r2 / n) * fixed_len

            # Animate towards the new orientation
            self.target_triangle_vectors[idx] = rotated_fixed
            self.triangle_steps = 20
            diff = rotated_fixed - self.current_triangle_vectors[idx]
            self.triangle_step_vectors[idx] = diff / self.triangle_steps
            self.triangle_timer.start(20)
        except Exception as e:
            print(f"Matrix input error: {e}")

    def update_triangle_animation(self):
        if self.triangle_steps > 0:
            for i in range(3):
                self.current_triangle_vectors[i] += self.triangle_step_vectors[i]
            self.triangle_steps -= 1
            self.triangle_canvas.update()
        else:
            self.triangle_timer.stop()

    # -----------------------------
    # Shuffle: rotate each line around its midpoint (length unchanged)
    # -----------------------------
    def shuffle_triangle_midpoints(self):
        def random_rotation_2d(vec2):
            angle = np.radians(random.uniform(0, 360))
            c, s = np.cos(angle), np.sin(angle)
            R = np.array([[c, -s],
                          [s,  c]], dtype=float)
            return R @ vec2

        for i in range(3):
            v = self.current_triangle_vectors[i]
            v_rot = random_rotation_2d(v)

            # keep length exactly the same as before shuffle
            v_rot = v_rot / np.linalg.norm(v_rot) * np.linalg.norm(v)

            # set instantly (no animation for the shuffle)
            self.current_triangle_vectors[i] = v_rot
            self.target_triangle_vectors[i] = v_rot

        self.triangle_canvas.update()

    # -----------------------------
    # Reset to the perfect triangle
    # -----------------------------
    def reset_triangle(self):
        self.current_triangle_vectors = [v.copy() for v in self.solution_vectors]
        self.target_triangle_vectors = [v.copy() for v in self.solution_vectors]
        self.triangle_canvas.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RotationMatrixWidget()
    window.setWindowTitle("Rotation Matrix Playground")
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec())


