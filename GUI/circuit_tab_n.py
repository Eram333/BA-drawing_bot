import sys
from PyQt6.QtWidgets import (
    QApplication, QTabWidget
)
from PyQt6.QtCore import  QMimeData, QTimer
#from rotation_matrixes import RotationMatrixWidget
from drawing_tab import ShapeSelector




from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QGraphicsScene, QGraphicsView, QGraphicsEllipseItem,
    QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsLineItem
)
from PyQt6.QtGui import QBrush, QPixmap, QPainter, QDrag, QPen, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QRectF
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
        self.image_path = image_path
        self.name = name
        self.setPixmap(QPixmap(image_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.setToolTip(name)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"{self.name}|{self.image_path}")
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
        #self.setAcceptDrops(True)

        if background_image:
            self.setBackgroundBrush(QBrush(QPixmap(background_image).scaled(800, 500)))

        for label, pos, expected_name in placeholder_data:
            if "Motor" in label:
                shape = QGraphicsEllipseItem(QRectF(0, 0, 70, 70))
            elif "ESP32" in label:
                shape = QGraphicsRectItem(QRectF(0, 0, 90, 50))
            else:
                shape = QGraphicsRectItem(QRectF(0, 0, 60, 60))

            shape.setBrush(QBrush(QColor(255, 255, 255, 200)))  # Semi-transparent white
            shape.setPen(QPen(QColor("black"), 2))
            shape.setPos(*pos)
            shape.setZValue(1)
            self.addItem(shape)

            text = QGraphicsTextItem(label)
            text.setPos(pos[0], pos[1] + 72)
            text.setZValue(2)
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

        def pt(x, y): return QPointF(x, y)

        connections = [
            # Left Motor -> Encoder -> SimpleFOC L -> ESP32
            (pt(135, 385), pt(135, 285)),  # Motor L -> Encoder L
            (pt(135, 285), pt(235, 285)),  # Encoder L -> SimpleFOC L
            (pt(235, 285), pt(235, 225)),  # hoch zu FOC
            (pt(235, 225), pt(385, 225)),  # zu ESP32

            # Right Motor -> Encoder -> SimpleFOC R -> ESP32
            (pt(635, 385), pt(635, 285)),
            (pt(635, 285), pt(535, 285)),
            (pt(535, 285), pt(535, 225)),
            (pt(535, 225), pt(385, 225)),
        ]

        for start, end in connections:
            line = QGraphicsLineItem(start.x(), start.y(), end.x(), end.y())
            line.setPen(pen)
            self.addItem(line)


        def center(pos):
            return QPointF(pos[0] + 35, pos[1] + 35)

        def draw_path(points):
            for i in range(len(points) - 1):
                line = QGraphicsLineItem(points[i].x(), points[i].y(), points[i + 1].x(), points[i + 1].y())
                line.setPen(pen)
                self.addItem(line)

        def path(*pts):
            return [QPointF(x, y) for x, y in pts]

       
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

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
                # ➕ Bild platzieren
                pixmap = QPixmap(path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
                item = QGraphicsPixmapItem(pixmap)
                # Rechteckgröße und Bildgröße
                rect_width = rect.rect().width()
                rect_height = rect.rect().height()
                pixmap_width = pixmap.width()
                pixmap_height = pixmap.height()

                # Zentriere das Bild im Rechteck
                x = rect.pos().x() + (rect_width - pixmap_width) / 2
                y = rect.pos().y() + (rect_height - pixmap_height) / 2
                item.setPos(x, y)

                item.setZValue(3)
                self.addItem(item)
                placeholder["content"] = item

                # 🟩 oder 🟥 Farbe
                if name == expected:
                    rect.setBrush(QBrush(QColor("lightgreen")))
                else:
                    rect.setBrush(QBrush(QColor("red")))
                    placeholder["content"] = item
                return


class CircuitTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        palette_frame = QFrame()
        palette_layout = QVBoxLayout(palette_frame)

        components = [
           (r"C:\Users\narge\OneDrive\Dokumente\BA_Narges\Bilder\Esp32.jpg", "ESP32"),
            (r"C:\Users\narge\OneDrive\Dokumente\BA_Narges\Bilder\SimpleFoc_Mini_v1.0.jpg", "SimpleFOC Mini"),
            (r"C:\Users\narge\OneDrive\Dokumente\BA_Narges\Bilder\BLDC_gimbal_motor_gbm2804h.jpg", "BLDC Motor"),
            (r"C:\Users\narge\OneDrive\Dokumente\BA_Narges\Bilder\AS5600_Magnetic_Encod.jpg", "AS5600 Encoder"),
        ]

        for path, name in components:
            label = DraggableLabel(path, name)
            palette_layout.addWidget(label)

        placeholder_data = [
            ("Motor Left",        (100, 350), "BLDC Motor"),
            ("Encoder Left",      (100, 250), "AS5600 Encoder"),
            ("SimpleFOC Mini L",  (200, 250), "SimpleFOC Mini"),
            ("ESP32",             (350, 200), "ESP32"),
            ("SimpleFOC Mini R",  (500, 250), "SimpleFOC Mini"),
            ("Encoder Right",     (600, 250), "AS5600 Encoder"),
            ("Motor Right",       (600, 350), "BLDC Motor"),
]


        self.scene = CircuitScene(placeholder_data, background_image=r"")
        self.view = QGraphicsView(self.scene)
        self.view.setAcceptDrops(True)
        self.view = CustomGraphicsView(self.scene)
        self.view.setAcceptDrops(True)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout.addWidget(palette_frame, 1)
        layout.addWidget(self.view, 3)
