import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget
)
from circuit_tab import CircuitTab
from rotation_matrixes import RotationMatrixWidget
from drawing_tab import ShapeSelector
from Mensch_Robo import MenschRoboTab


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Bot GUI")
        self.setGeometry(100, 100, 1000, 600)
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(CircuitTab(), "Schaltung")
        self.rotation_tab = RotationMatrixWidget()
        self.tabs.insertTab(2, self.rotation_tab, "Rotation matrix")
        self.tabs.addTab(ShapeSelector(), "Drawing Tab")
        self.tabs.addTab(QWidget(), "Settings")
        self.tabs.addTab(MenschRoboTab(), "Mensch(humain)")

        layout.addWidget(self.tabs)

        # 💅 Apply modern blue style sheet
        self.setStyleSheet("""
            QWidget {
                background-color: #e3f2fd;  /* Light blue background */
                font-family: "Segoe UI", sans-serif;
                font-size: 14px;
            }

            QTabWidget::pane {
                border: 1px solid #90caf9;
                background: #ffffff;
            }

            QTabBar::tab {
                background: #bbdefb;
                border: 1px solid #90caf9;
                padding: 8px 14px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background: #64b5f6;
                color: white;
            }

            QPushButton {
                background-color: #42a5f5;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #1e88e5;
            }

            QLabel {
                color: #0d47a1;
            }

            QGraphicsView {
                border: 1px solid #90caf9;
                background-color: #ffffff;
            }

            QFrame {
                border: none;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

