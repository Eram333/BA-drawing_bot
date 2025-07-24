# mensch_robo_tab.py
import os
import random



from PyQt6.QtWidgets import (
    QWidget, QLabel, QListWidget, QListWidgetItem,
    QHBoxLayout, QVBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QFrame
)
from PyQt6.QtCore import (QSize,QBuffer, QByteArray, QIODevice)

from PyQt6.QtGui import QPixmap, QDrag,  QIcon, QImage, QCursor, QBrush
from PyQt6.QtCore import Qt, QMimeData, QByteArray

class DraggableList(QListWidget):
    def __init__(self, items, image_paths=None):
        super().__init__()
        self.setDragEnabled(True)

       


        if image_paths is not None:
            #  Linke Seite: Bauteile mit Bild + Name
            for i, item_text in enumerate(items):
                image_path = image_paths.get(item_text, None)
                
                pixmap = QPixmap(image_path) if image_path and os.path.exists(image_path) else QPixmap()
                if pixmap.isNull():
                    print(f"[WARNUNG] Bild ungültig oder fehlt: {image_path}")
                    pixmap = QPixmap(120, 120)
                    pixmap.fill(Qt.GlobalColor.gray)

                scaled = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)

                # Bild-Label
                img_label = QLabel()
                img_label.setPixmap(scaled)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Text-Label
                text_label = QLabel(item_text)
                text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                text_label.setStyleSheet("font-size: 13px; font-weight: bold;")

                # Gesamt-Widget
                widget = QWidget()
                vbox = QVBoxLayout(widget)
                vbox.addWidget(img_label)
                vbox.addWidget(text_label)
                vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
                vbox.setContentsMargins(5, 5, 5, 5)

                item = QListWidgetItem()
                item.setSizeHint(widget.sizeHint())

                self.addItem(item)
                self.setItemWidget(item, widget)

        else:
            #  Rechte Seite: Nur beschreibende Texte (ohne Bild)
            for item_text in items:
                text_label = QLabel(item_text)
                text_label.setWordWrap(True)
                text_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                text_label.setStyleSheet("""
                    font-size: 13px;
                    padding: 8px;
                    border: 1px solid #999;
                    border-radius: 6px;
                    background-color: black;
                """)

                # Dynamische Höhe
                font_metrics = text_label.fontMetrics()
                text_height = font_metrics.boundingRect(0, 0, 230, 0, Qt.TextFlag.TextWordWrap, item_text).height()

                # Verpacken in Widget
                widget = QWidget()
                vbox = QVBoxLayout(widget)
                vbox.addWidget(text_label)
                vbox.setContentsMargins(5, 5, 5, 5)

                item = QListWidgetItem()
                item.setSizeHint(QSize(230, text_height + 50))

                self.addItem(item)
                self.setItemWidget(item, widget)


        self.setStyleSheet("""
            QListWidget {
                background-color: transparent;
            }
        """)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return

        drag = QDrag(self)
        mime_data = QMimeData()

        widget = self.itemWidget(item)
        labels = widget.findChildren(QLabel)

        if len(labels) == 2:
            img_label = labels[0]
            text_label = labels[1]
        elif len(labels) == 1:
            img_label = None
            text_label = labels[0]
        else:
            print("[FEHLER] Kein gültiges Label-Widget gefunden.")
            return

        name = text_label.text()
        mime_data.setText(name)

        if img_label:
            pixmap = img_label.pixmap()
            if pixmap:
                byte_array = QByteArray()
                buffer = QBuffer(byte_array)
                buffer.open(QBuffer.OpenModeFlag.WriteOnly)
                pixmap.save(buffer, "PNG")
                mime_data.setImageData(byte_array.data())

        drag.setMimeData(mime_data)
        drag.exec()
     

        
class DropZoneLabel(QLabel):
    def __init__(self, zone_name=""):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFixedSize(120, 60)
        self.setStyleSheet("""
            background-color: #eee;
            border: 2px dashed #888;
            color: #333;
            font-weight: bold;
            padding: 5px;
        """)
        self.setText(zone_name)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.setText(event.mimeData().text())
        event.acceptProposedAction()


class ImageDropLabel(QLabel):
    def __init__(self, expected_text=None):
        super().__init__()
        self.expected_text = expected_text
        self.setAcceptDrops(True)
        self.setMinimumSize(120, 120)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: white; border: 2px dashed gray;")

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage() and event.mimeData().hasFormat("application/x-partname"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        part_name = event.mimeData().data("application/x-partname").data().decode()
        image = QPixmap()
        image.loadFromData(event.mimeData().imageData())
        self.setPixmap(image.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        self.setScaledContents(True)

        if part_name.strip().lower() == self.expected_text.strip().lower():
            self.setStyleSheet("background-color: lightgreen; border: 2px solid green;")
            print(f"[BILD OK] {part_name} korrekt platziert.")
        else:
            self.setStyleSheet("background-color: lightcoral; border: 2px solid red;")
            print(f"[BILD FALSCH] Erwartet: {self.expected_text}, bekommen: {part_name}")

        event.acceptProposedAction()

class ImageDropLabel(QLabel):
    def __init__(self, expected_name=""):
        super().__init__()
        self.expected_name = expected_name
        self.setAcceptDrops(True)
        self.setMinimumSize(120, 120)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            background-color: white;
            border: 2px dashed gray;
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage() and event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage() and event.mimeData().hasText():
            dragged_name = event.mimeData().text()
            pixmap = QPixmap()
            pixmap.loadFromData(event.mimeData().imageData())

            if dragged_name == self.expected_name:
                self.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                self.setStyleSheet("border: 2px solid green;")
            else:
                self.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                self.setStyleSheet("border: 2px solid red;")

            event.acceptProposedAction()


class TextDropLabel(QLabel):
    def __init__(self,expected_text =None):
        super().__init__()
        self.setAcceptDrops(True)
        self.expected_text = expected_text
        #self.expected_name = expected_name
        self.setMinimumSize(120, 120)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setStyleSheet("background-color: white; border: 2px dashed gray;")

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            dropped_text = event.mimeData().text().strip()
            print(f"[DROP] Erwartet: {self.expected_text} | Erhalten: {dropped_text}")

            beschreibung_zu_expected = {
            "Mikrocontroller zur zentralen Steuerung – wie das Gehirn.": "Kopf",
            "Sensor zur präzisen Winkelmessung – wie der Gelenksinn im Körper.": "Auge",
            "Motor für kontrollierte Bewegung – wie ein Muskel.": "Arm",
            "Motorregler für feine Bewegungen – wie das Rückenmark.": "Rumpf"
            }
            if dropped_text == self.expected_text:
                self.setStyleSheet("background-color: lightgreen; border: 2px solid green;")
                self.setText(dropped_text)
            else:
                self.setStyleSheet("background-color: red; border: 2px solid darkred;")
                self.setText(dropped_text)
            
            event.accept()

def get_expected_image_for(body_part):
    image_to_bodypart = {
        "ESP32 Mikrocontroller": "Kopf",
        "AS5600 Encoder": "Auge",
        "BLDC Gimbal Motor": "Arm",
        "SimpleFOC Mini": "Rumpf"
    }
    for image, target in image_to_bodypart.items():
        if target == body_part:
            return image
    return None


class RobotCanvas(QWidget):
    def __init__(self, image_path, part_names=None, part_descriptions=None, body_labels=None, part_image_paths=None):
        
        
        super().__init__()

        self.part_names = part_names or []
        self.part_descriptions = part_descriptions or []
        self.body_labels = body_labels or []
        self.part_image_paths = part_image_paths or []

        layout = QHBoxLayout(self)
    
       # Im Konstruktor der RobotCanvas
        #layout = QHBoxLayout(self)

        # Linke Drop-Zonen (für Bilder)
        self.left_drop_labels = []
        left_drop_zone_layout = QVBoxLayout()
        for part in self.body_labels:
            expected_name = get_expected_image_for(part)
            drop = ImageDropLabel(expected_name=expected_name)
            left_drop_zone_layout.addWidget(drop)
            self.left_drop_labels.append(drop)

        # Roboterbild (in der Mitte)
        center_layout = QVBoxLayout()
        robot_label = QLabel()
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            pixmap = QPixmap(300, 400)
            pixmap.fill(Qt.GlobalColor.gray)
        robot_label.setPixmap(pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio))
        robot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addStretch()
        center_layout.addWidget(robot_label)
        center_layout.addStretch()

        # Rechte Drop-Zonen (für Texte)
        self.right_drop_labels = []
        right_drop_zone_layout = QVBoxLayout()
        for desc in self.part_descriptions:
            drop = TextDropLabel(expected_text=desc)
            right_drop_zone_layout.addWidget(drop)
            self.right_drop_labels.append(drop)

        # Zusammenbau der drei Spalten
        layout.addLayout(left_drop_zone_layout)
        layout.addLayout(center_layout)
        layout.addLayout(right_drop_zone_layout)


class DropZone(QLabel):
    def __init__(self, title):
        super().__init__()
        self.setAcceptDrops(True)
        self.setText(f"{title}\n(Drop hier)")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(160, 80)
        self.setWordWrap(True)
        self.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px dashed #555;
                border-radius: 8px;
                padding: 6px;
                font-size: 12px;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text()
        self.setText(text)
        event.acceptProposedAction()



class MenschRoboTab(QWidget):
    def __init__(self):
        super().__init__()

        self.body_labels = ["Kopf", "Auge", "Arm", "Rumpf"]
        self.part_names = ["ESP32 Mikrocontroller", "AS5600 Encoder", "BLDC Gimbal Motor", "SimpleFOC Mini"]
        self.part_image_paths = {
            "AS5600 Encoder": "images/AS5600_Magnetic_Encod.jpg",
            "ESP32 Mikrocontroller": "images/Esp32.jpg",
            "BLDC Gimbal Motor": "images/BLDC_gimbal_motor_gbm2804h.jpg",
            "SimpleFOC Mini": "images/SimpleFoc_Mini_v1.0.jpg"
        }

        self.part_descriptions = [
            "Mikrocontroller zur zentralen Steuerung – wie das Gehirn.",
            "Sensor zur präzisen Winkelmessung – wie der Gelenksinn im Körper.",
            "Motor für kontrollierte Bewegung – wie ein Muskel.",
            "Motorregler für feine Bewegungen – wie das Rückenmark."
        ]

        

        #  RobotCanvas einmal korrekt initialisieren
        self.robot_canvas = RobotCanvas(
            image_path = "images/MaedchenRobo.png",
            part_names=self.part_names,
            part_descriptions=self.part_descriptions,
            body_labels=self.body_labels,
            part_image_paths=self.part_image_paths
        )
                   

        #  Bildpfad und Verfügbarkeit prüfen
        print("Bild existiert?", os.path.exists("images/MaedchenRobo.png"))
        #  GUI-Elemente initialisieren (einmal)

        random.shuffle(self.part_names)
        random.shuffle(self.part_descriptions)

        self.part_list = DraggableList(self.part_names, self.part_image_paths) 
        self.part_list.setFixedWidth(200)

        self.description_list = DraggableList(self.part_descriptions)
        self.description_list.setFixedWidth(230)
        self.description_list.setStyleSheet("background-color: cornflowerblue;")

        print("Beschreibungsliste wird hier gesetzt:", self.description_list.count(), "Einträge")

        #  Layout setzen: links – mitte – rechts
        layout = QHBoxLayout()
        layout.addWidget(self.part_list)
        layout.addWidget(self.robot_canvas)
        layout.addWidget(self.description_list)

        self.setLayout(layout)

