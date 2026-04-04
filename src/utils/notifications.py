import sys

# import os
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QColor, QPalette
from core.tasks import get_random_task


class SystemNotification(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(800, 500)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.container = QFrame()
        self.container.setObjectName("systemWindow")
        self.container_layout = QVBoxLayout(self.container)

        self.header_frame = QFrame()
        self.header_frame.setObjectName("header")
        header_layout = QHBoxLayout(self.header_frame)

        self.header_text = QLabel("NOTIFICATION")
        self.header_text.setObjectName("headerText")
        header_layout.addStretch()
        header_layout.addWidget(self.header_text)
        header_layout.addStretch()

        self.content_area = QFrame()
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setSpacing(10)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.cat_label = QLabel("[ CATEGORY ]")
        self.cat_label.setObjectName("notifCategory")
        self.cat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.msg_label = QLabel("Loading task...")
        self.msg_label.setObjectName("notifMessage")
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.setWordWrap(True)

        content_layout.addWidget(self.cat_label)
        content_layout.addWidget(self.msg_label)

        self.button_area = QFrame()
        button_layout = QHBoxLayout(self.button_area)

        self.dismiss_btn = QPushButton("DISMISS")
        self.dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dismiss_btn.clicked.connect(self.hide)

        button_layout.addStretch()
        button_layout.addWidget(self.dismiss_btn)
        button_layout.addStretch()

        self.container_layout.addWidget(self.header_frame)
        self.container_layout.addStretch()
        self.container_layout.addWidget(self.content_area)
        self.container_layout.addStretch()
        self.container_layout.addWidget(self.button_area)

        self.main_layout.addWidget(self.container)

        self.setStyleSheet("""
            QWidget {
                        font-family: 'Montserrat', sans-serif;
                    }
            #systemWindow {
                background-color: rgba(5, 10, 20, 240);
                border: 1px solid rgba(0, 210, 255, 0.5);
                border-radius: 2px;
            }
            #header {
                border: 1px solid #00d2ff;
                margin-top: 40px;
                margin-left: 100px;
                margin-right: 100px;
                max-height: 50px;
            }
            #headerText {
                color: white;
                font-size: 20px;
                font-weight: 500;
                letter-spacing: 4px;
            }
            #notifCategory {
                color: #00d2ff;
                font-weight: 700;
                font-size: 18px;
                letter-spacing: 2px;
            }
            #notifMessage {
                font-size: 22px;
                font-weight: 400;
                color: #e0e0e0;
            }
            QPushButton {
                background: transparent;
                border: 1px solid #00d2ff;
                color: #00d2ff;
                padding: 8px 35px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(0, 210, 255, 0.2);
                color: white;
            }
        """)

    def refresh_task(self):
        """Fetches a random task and updates the UI labels"""
        task_info = get_random_task()
        if task_info:
            category, title = task_info
            self.cat_label.setText(f"[ {category.upper()} ]")
            self.msg_label.setText(title)
            self.show_system_style()

    def show_system_style(self):
        """Displays the window on top and restores from minimized state"""
        self.show()
        self.raise_()
        self.activateWindow()

    def keyPressEvent(self, event):
        """Allows dismissing the notification with any key"""
        self.hide()


def main():
    app = QApplication(sys.argv)

    notif = SystemNotification()
    timer = QTimer()
    timer.timeout.connect(notif.refresh_task)

    timer.start(3600000)

    notif.refresh_task()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
