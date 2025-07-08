# main_gui.py

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget
from circuit_tab import CircuitTab
from rotation_matrixes import RotationMatrixWidget
from drawing_tab import ShapeSelector

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Bot GUI")
        self.setGeometry(100, 100, 1000, 600)
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), "Mensch(humain)")
        self.tabs.addTab(CircuitTab(), "Schaltung")
        self.rotation_tab = RotationMatrixWidget()
        self.tabs.insertTab(2, self.rotation_tab, "Rotation matrix")
        self.tabs.addTab(ShapeSelector(), "Drawing Tab")
        self.tabs.addTab(QWidget(), "Settings")

        layout.addWidget(self.tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
