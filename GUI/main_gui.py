# main_gui.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QFrame
)
from PyQt6.QtGui import QFont, QGuiApplication, QPalette, QColor, QIcon
from PyQt6.QtCore import Qt

from circuit_tab import CircuitTab
from Mensch_Robo import MenschRoboTab
from rotation_matrixes import RotationMatrixWidget
from drawing_tab import ShapeSelector


def get_stylesheet() -> str:
    return """
    QWidget {
        background-color: #f7f8fc;
        color: #0f172a;
        font-family: "Segoe UI", "Inter", "SF Pro Text", Arial, sans-serif;
        font-size: 13px;
    }

    /* ---------- Tab Bar Gradient Background ---------- */
    QTabBar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #2563eb, stop:1 #ec4899);
        border-top-left-radius: 14px;
        border-top-right-radius: 14px;
        padding: 6px;
    }
    QTabBar::tab {
        background: transparent;
        color: white;
        padding: 9px 16px;
        margin: 4px 6px;
        border-radius: 10px;
        font-weight: 600;
    }
    QTabBar::tab:hover {
        background: rgba(255,255,255,0.15); /* soft white overlay */
    }
    QTabBar::tab:selected {
        background: white;
        color: #111827;
    }

    /* ---------- Pane (tab content area) ---------- */
    QTabWidget::pane {
        border: 1px solid #e5e7eb;
        border-top: none;
        border-bottom-left-radius: 14px;
        border-bottom-right-radius: 14px;
        background: white;
    }

    /* ---------- Header Card stays same ---------- */
    #HeaderCard {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #2563eb, stop:1 #ec4899);
        border-radius: 16px;
        padding: 16px 20px;
        color: white;
    }
    #HeaderTitle {
        color: white;
        font-size: 20px;
        font-weight: 700;
    }
    #HeaderSubtitle {
        color: rgba(255,255,255,0.9);
        font-size: 12px;
        font-weight: 500;
    }

    /* Buttons, inputs, scrollbars ... (keep your old styles here) */
    """



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Bot GUI")
        self.setGeometry(100, 100, 1100, 700)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        # ---------- Header (gradient blue → pink) ----------
        header = QFrame()
        header.setObjectName("HeaderCard")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 16, 14)

        title = QLabel("Drawing Bot – Workshop Suite")
        title.setObjectName("HeaderTitle")

        subtitle = QLabel("Robotics • Rotation Matrices • Circuits • Drawing")
        subtitle.setObjectName("HeaderSubtitle")
        subtitle.setProperty("variant", "muted")

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        header_layout.addLayout(title_block)
        header_layout.addStretch(1)

        # You can add a small brand dot on the right if you like:
        brand_dot = QFrame()
        brand_dot.setFixedSize(14, 14)
        brand_dot.setStyleSheet("background: white; border-radius: 7px;")
        header_layout.addWidget(brand_dot, alignment=Qt.AlignmentFlag.AlignVCenter)

        # ---------- Tabs ----------
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)  # flatter modern tabs
        self.tabs.setMovable(True)

        # Add your existing tabs (unchanged)
        self.tabs.addTab(MenschRoboTab(), "Mensch (Human)")
        self.tabs.addTab(CircuitTab(), "Schaltung")
        self.rotation_tab = RotationMatrixWidget()
        self.tabs.insertTab(2, self.rotation_tab, "Rotation Matrix")
        self.tabs.addTab(ShapeSelector(), "Drawing Tab")
        self.tabs.addTab(QWidget(), "Settings")

        # ---------- Compose ----------
        root.addWidget(header)
        root.addWidget(self.tabs)


if __name__ == "__main__":
    # High-DPI friendly text rendering (optional)
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # Apply modern blue–pink stylesheet
    app.setStyleSheet(get_stylesheet())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())



