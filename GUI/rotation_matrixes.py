import sys
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QPushButton, QApplication, QLabel, QFrame
)
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QLabel, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QTimer, QPointF
import numpy as np


class RotationLineWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.original_vector = np.array([100.0, 0.0], dtype=np.float64)
        self.current_vector = self.original_vector.copy()
        self.target_vector = self.original_vector.copy()

        self.steps = 0
        self.step_vector = np.array([0.0, 0.0])
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.setMinimumHeight(200)

    def set_new_direction(self, vector):
        self.target_vector = vector
        self.steps = 20
        self.step_vector = (self.target_vector - self.current_vector) / self.steps
        self.timer.start(20)

    def update_animation(self):
        if self.steps > 0:
            self.current_vector += self.step_vector
            self.steps -= 1
            self.update()
        else:
            self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width() // 2, self.height() // 2
        painter.translate(w, h)

        pen = QPen(QColor("blue"), 4)
        painter.setPen(pen)
        end_point = QPointF(self.current_vector[0], -self.current_vector[1])
        painter.drawLine(QPointF(0, 0), end_point)


 # secon task in the 3rd widget

# Shared Canvas for Triangle Challenge
class TriangleCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.vectors = [
            np.array([100.0, 0.0]),
            np.array([-50.0, 87.0]),
            np.array([-50.0, -87.0])
        ]
        self.current_vectors = self.vectors.copy()
        self.target_vectors = self.vectors.copy()
        self.step_vectors = [np.array([0.0, 0.0]) for _ in range(3)]
        self.steps = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_step)
        self.setMinimumHeight(200)

    def rotate_vector(self, idx, new_vec):
        self.target_vectors[idx] = new_vec
        self.steps = 20
        diff = new_vec - self.current_vectors[idx]
        self.step_vectors[idx] = diff / self.steps
        self.timer.start(20)

    def animate_step(self):
        if self.steps > 0:
            for i in range(3):
                self.current_vectors[i] += self.step_vectors[i]
            self.steps -= 1
            self.update()
        else:
            self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = QPointF(self.width() / 2, self.height() / 2)
        painter.translate(center)

        colors = ['red', 'green', 'blue']
        for i, vec in enumerate(self.current_vectors):
            pen = QPen(QColor(colors[i]), 3)
            painter.setPen(pen)
            painter.drawLine(QPointF(0, 0), QPointF(vec[0], -vec[1]))

    # Triangle Challenge UI


class TriangleChallengeFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        self.canvas = TriangleCanvas()
        layout.addWidget(QLabel("🧩 Triangle Challenge: Rotate all 3 lines to form a triangle"))
        layout.addWidget(self.canvas)

        self.matrix_widgets = []
        for i in range(3):
            group = self.create_matrix_group(i)
            layout.addLayout(group)

    def create_matrix_group(self, index):
        layout = QVBoxLayout()
        label = QLabel(f"Line {index + 1} Rotation Matrix:")
        layout.addWidget(label)

        grid = QGridLayout()
        inputs = []
        for i in range(3):
            row = []
            for j in range(3):
                le = QLineEdit()
                le.setText("1.0" if i == j else "0.0")
                le.setFixedWidth(50)
                le.setAlignment(Qt.AlignmentFlag.AlignCenter)
                grid.addWidget(le, i, j)
                row.append(le)
            inputs.append(row)

        self.matrix_widgets.append(inputs)

        button = QPushButton(f"Apply to Line {index + 1}")
        button.clicked.connect(lambda _, idx=index: self.apply_matrix(idx))

        layout.addLayout(grid)
        layout.addWidget(button)
        return layout

    def apply_matrix(self, idx):
        try:
            matrix = np.array([
                [float(self.matrix_widgets[idx][i][j].text()) for j in range(3)]
                for i in range(3)
            ])
            base_vector = self.canvas.vectors[idx].copy()
            base_vector3D = np.array([base_vector[0], base_vector[1], 0.0])
            rotated3D = matrix @ base_vector3D
            rotated2D = rotated3D[:2]
            self.canvas.rotate_vector(idx, rotated2D)
        except Exception as e:
            print(f"Matrix input error: {e}")

    # Final master widget with scroll area


class RotationMatrixWidget(QWidget):
    def __init__(self):
        super().__init__()
        outer_layout = QVBoxLayout(self)

        # === ONE LINE ROTATION ===
        from rotation_matrixes import RotationMatrixWidget as SingleLineWidget  # Avoid circular import if needed
        self.single_widget = SingleLineWidget()
        outer_layout.addWidget(self.single_widget)

        # === TRIANGLE CHALLENGE ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        triangle_frame = TriangleChallengeFrame()
        scroll.setWidget(triangle_frame)

        outer_layout.addWidget(scroll)


class RotationMatrixWidget(QWidget):
    def __init__(self):
        super().__init__()

        # === First Activity: One-Line Rotation ===
        self.canvas = RotationLineWidget()
        self.matrix_inputs = [[QLineEdit() for _ in range(3)] for _ in range(3)]

        # === Master Layout ===
        main_layout = QVBoxLayout(self)

        # Frame for the single-line rotation
        one_line_frame = QFrame()
        one_line_layout = QVBoxLayout(one_line_frame)
        one_line_layout.addWidget(self.canvas)

        grid = QGridLayout()
        for i in range(3):
            for j in range(3):
                box = self.matrix_inputs[i][j]
                box.setText("1.0" if i == j else "0.0")
                box.setFixedWidth(50)
                box.setAlignment(Qt.AlignmentFlag.AlignCenter)
                grid.addWidget(box, i, j)

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setLayout(grid)

        button = QPushButton("Apply Rotation")
        button.clicked.connect(self.apply_matrix)

        one_line_layout.addWidget(QLabel("Enter 3×3 Rotation Matrix:"))
        one_line_layout.addWidget(frame)
        one_line_layout.addWidget(button)

        main_layout.addWidget(one_line_frame)

        # === Second Activity: Triangle Challenge in Scroll Area ===
        from rotation_matrixes import TriangleChallengeFrame  # or move class above

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        triangle_frame = TriangleChallengeFrame()
        scroll_area.setWidget(triangle_frame)

        main_layout.addWidget(scroll_area)

    def apply_matrix(self):
        try:
            matrix = np.array([[float(self.matrix_inputs[i][j].text())
                                for j in range(3)] for i in range(3)])
            vector3 = np.array([self.canvas.original_vector[0],
                                self.canvas.original_vector[1], 0.0])
            rotated = matrix @ vector3
            new_vector = rotated[:2]  # ignore Z
            self.canvas.set_new_direction(new_vector)
        except Exception as e:
            print(f"Invalid input: {e}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RotationMatrixWidget()
    window.setWindowTitle("Rotation Matrix Playground")
    window.resize(400, 400)
    window.show()
    sys.exit(app.exec())
