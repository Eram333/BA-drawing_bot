import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QScrollArea, QGridLayout
)
from PyQt6.QtGui import QPainter, QPixmap, QPolygon, QColor, QPainterPath, QIcon
from PyQt6.QtCore import Qt, QPoint


class ShapeButton(QPushButton):
    def __init__(self, shape_name):
        super().__init__()
        self.shape_name = shape_name
        self.setFixedSize(100, 100)
        self.setIconSize(self.size())
        self.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.setIcon(QIcon(self.draw_shape()))

    def draw_shape(self):
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(QColor("skyblue"))

        center = QPoint(50, 50)
        size = 30

        if self.shape_name == "line":
            painter.drawLine(20, 50, 80, 50)
        elif self.shape_name == "square":
            painter.drawRect(30, 30, 40, 40)
        elif self.shape_name == "triangle":
            points = [QPoint(50, 20), QPoint(30, 70), QPoint(70, 70)]
            painter.drawPolygon(QPolygon(points))
        elif self.shape_name == "star":
            points = [
                QPoint(50, 20), QPoint(60, 40), QPoint(80, 40),
                QPoint(65, 55), QPoint(70, 75), QPoint(50, 65),
                QPoint(30, 75), QPoint(35, 55), QPoint(20, 40),
                QPoint(40, 40)
            ]
            painter.drawPolygon(QPolygon(points))
        elif self.shape_name == "heart":
            path = QPainterPath()
            path.moveTo(50, 60)
            path.cubicTo(50, 20, 90, 20, 50, 60)
            path.cubicTo(10, 20, 50, 20, 50, 60)
            painter.drawPath(path)
        elif self.shape_name == "circle":
            painter.drawEllipse(center, size, size)

        painter.end()
        return pixmap

    def set_selected(self, selected):
        if selected:
            self.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        else:
            self.setStyleSheet("border: 1px solid gray; background-color: white;")


class ShapeSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shape Selector")
        self.setMinimumSize(600, 400)
        self.selected_button = None

        main_layout = QVBoxLayout(self)

        # Scrollable area
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Prompt inside scroll area
        prompt_label = QLabel("Please select a shape:")
        prompt_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        scroll_layout.addWidget(prompt_label)

        # Shape buttons inside scroll area
        shapes = ["line", "square", "triangle", "star", "heart", "circle"]
        grid = QGridLayout()

        self.shape_buttons = []

        for i, shape in enumerate(shapes):
            button = ShapeButton(shape)
            button.clicked.connect(lambda checked, b=button, s=shape: self.on_shape_selected(b, s))

            label = QLabel(shape.capitalize())
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            vbox = QVBoxLayout()
            vbox.addWidget(button)
            vbox.addWidget(label)

            container = QWidget()
            container.setLayout(vbox)
            grid.addWidget(container, i // 3, i % 3)

            self.shape_buttons.append(button)

        scroll_layout.addLayout(grid)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)

        main_layout.addWidget(scroll_area)

    def on_shape_selected(self, button, shape_name):
        print(f"Shape selected: {shape_name}")

        # Update button styles
        for b in self.shape_buttons:
            b.set_selected(b == button)

        # 🔧 Replace this with your robot drawing function
        # e.g., self.robot.draw_shape(shape_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShapeSelector()
    window.show()
    sys.exit(app.exec())

