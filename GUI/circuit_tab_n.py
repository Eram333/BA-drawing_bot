# circuit_tab_n.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsRectItem,
    QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsLineItem
)
from PyQt6.QtGui import QBrush, QPixmap, QPainter, QDrag, QPen, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF, QMimeData


class CustomGraphicsView(QGraphicsView):
    def dragEnterEvent(self, event):
        if self.scene():
            self.scene().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if self.scene():
            self.scene().dragMoveEvent(event)

    def dropEvent(self, event):
        if self.scene():
            self.scene().dropEvent(event)


class DraggableLabel(QLabel):
    def __init__(self, image_path, name):
        super().__init__()
        self.name = name
        self.path = image_path
        self.setPixmap(QPixmap(image_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setToolTip(name)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"{self.name}|{self.path}")
            drag.setMimeData(mime)
            drag.setPixmap(self.pixmap())
            drag.setHotSpot(event.pos())
            drag.exec()

    def mouseMoveEvent(self, event):
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(f"{self.name}|{self.path}")
        drag.setMimeData(mime)
        drag.setPixmap(self.pixmap())
        drag.exec()


class CircuitScene(QGraphicsScene):
    def __init__(self, placeholder_data, background_image=None, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 800, 500)
        self.placeholders = []

        if background_image:
            self.setBackgroundBrush(QBrush(QPixmap(background_image).scaled(800, 500)))

        for label, pos, expected_name in placeholder_data:
            # === Create the shape ===
            if "Motor" in label:
                shape = QGraphicsEllipseItem(QRectF(0, 0, 70, 70))
            elif "ESP32" in label:
                shape = QGraphicsRectItem(QRectF(0, 0, 90, 50))
            else:
                shape = QGraphicsRectItem(QRectF(0, 0, 60, 60))

            shape.setBrush(QBrush(QColor(255, 255, 255, 200)))  # semi-transparent
            shape.setPen(QPen(QColor("black"), 2))
            shape.setPos(*pos)
            shape.setZValue(1)
            self.addItem(shape)

            # === Create the text label ===
            text = QGraphicsTextItem(label)
            text.setZValue(2)

            text_width = text.boundingRect().width()
            shape_width = shape.rect().width()
            x = pos[0] + (shape_width - text_width) / 2
            y = pos[1] + shape.rect().height() + 5  # 5 px below shape
            text.setPos(x, y)

            self.addItem(text)

            self.placeholders.append({
                "label": label,
                "rect": shape,
                "expected": expected_name,
                "content": None
            })

        self.draw_connections()

    def draw_connections(self):
        pen = QPen(Qt.GlobalColor.black, 2)

        def pt(x, y):
            return QPointF(x, y)

        connections = [
            (pt(135, 385), pt(135, 285)),  # Motor L -> Encoder L
            (pt(135, 285), pt(235, 285)),  # Encoder L -> SimpleFOC L
            (pt(235, 285), pt(235, 225)),  # up to FOC
            (pt(235, 225), pt(385, 225)),  # to ESP32

            (pt(635, 385), pt(635, 285)),  # Motor R -> Encoder R
            (pt(635, 285), pt(535, 285)),  # Encoder R -> FOC R
            (pt(535, 285), pt(535, 225)),  # up
            (pt(535, 225), pt(385, 225)),  # to ESP32
        ]

        for start, end in connections:
            line = QGraphicsLineItem(start.x(), start.y(), end.x(), end.y())
            line.setPen(pen)
            self.addItem(line)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def reset_scene(self):
        for placeholder in self.placeholders:
            # Remove image if present
            if placeholder["content"]:
                self.removeItem(placeholder["content"])
                placeholder["content"] = None

            # Reset placeholder color
            placeholder["rect"].setBrush(QBrush(QColor(255, 255, 255, 200)))

    def dropEvent(self, event):
        if not event.mimeData().hasText():
            return
        try:
            name, path = event.mimeData().text().split("|")
        except ValueError:
            return

        for placeholder in self.placeholders:
            rect = placeholder["rect"]
            expected = placeholder["expected"]

            scene_pos = self.views()[0].mapToScene(event.position().toPoint())
            if rect.contains(scene_pos - rect.pos()):
                pixmap = QPixmap(path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
                item = QGraphicsPixmapItem(pixmap)

                rect_width = rect.rect().width()
                rect_height = rect.rect().height()
                pixmap_width = pixmap.width()
                pixmap_height = pixmap.height()

                x = rect.pos().x() + (rect_width - pixmap_width) / 2
                y = rect.pos().y() + (rect_height - pixmap_height) / 2
                item.setPos(x, y)

                item.setZValue(3)
                self.addItem(item)
                placeholder["content"] = item

                if name == expected:
                    rect.setBrush(QBrush(QColor("lightgreen")))
                else:
                    rect.setBrush(QBrush(QColor("red")))
                return



from PyQt6.QtWidgets import QPushButton  # Add this import at the top

class CircuitTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        # === Left side: Palette + Reset ===
        palette_frame = QFrame()
        palette_layout = QVBoxLayout(palette_frame)

        components = [
            ("images/Esp32.jpg", "ESP32"),
            ("images/SimpleFoc_Mini_v1.0.jpg", "SimpleFOC Mini"),
            ("images/BLDC_gimbal_motor_gbm2804h.jpg", "BLDC Motor"),
            ("images/AS5600_Magnetic_Encod.jpg", "AS5600 Encoder"),
        ]

        for path, name in components:
            label = DraggableLabel(path, name)
            palette_layout.addWidget(label)

        # === Add Reset Button ===
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_scene)  # Connect the button
        palette_layout.addWidget(reset_button)

        # === Circuit area (center view) ===
        placeholder_data = [
            ("Motor Left", (100, 350), "BLDC Motor"),
            ("Encoder Left", (100, 250), "AS5600 Encoder"),
            ("SimpleFOC Mini L", (200, 250), "SimpleFOC Mini"),
            ("ESP32", (350, 200), "ESP32"),
            ("SimpleFOC Mini R", (500, 250), "SimpleFOC Mini"),
            ("Encoder Right", (600, 250), "AS5600 Encoder"),
            ("Motor Right", (600, 350), "BLDC Motor"),
        ]

        self.scene = CircuitScene(placeholder_data)
        self.view = CustomGraphicsView(self.scene)
        self.view.setAcceptDrops(True)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout.addWidget(palette_frame, 1)
        layout.addWidget(self.view, 3)

    def reset_scene(self):
        self.scene.reset_scene()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = QWidget()
    layout = QVBoxLayout(win)
    tabs = QTabWidget()
    tabs.addTab(CircuitTab(), "Schaltung")
    layout.addWidget(tabs)
    win.setWindowTitle("Drawing Bot GUI")
    win.resize(1000, 600)
    win.show()
    sys.exit(app.exec())
