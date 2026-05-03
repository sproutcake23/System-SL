from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Qt, QTimer
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

        self._setup_ui()
        self._apply_styles()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_task)
        self.timer.start(3600000)

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
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
        self.cat_label = QLabel("[ CATEGORY ]")
        self.cat_label.setObjectName("notifCategory")
        self.msg_label = QLabel("Loading task...")
        self.msg_label.setObjectName("notifMessage")

        for lbl in [self.cat_label, self.msg_label]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(lbl)

        self.dismiss_btn = QPushButton("DISMISS")
        self.dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dismiss_btn.clicked.connect(self.hide)

        self.container_layout.addWidget(self.header_frame)
        self.container_layout.addStretch()
        self.container_layout.addWidget(self.content_area)
        self.container_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.dismiss_btn)
        btn_layout.addStretch()
        self.container_layout.addLayout(btn_layout)

        self.main_layout.addWidget(self.container)

    def refresh_task(self):
        task_info = get_random_task()
        if task_info:
            category, title = task_info
            self.cat_label.setText(f"[ {category.upper()} ]")
            self.msg_label.setText(title)
            self.show_system_style()

    def show_system_style(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def keyPressEvent(self, event):
        self.hide()

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                font-family: 'Montserrat', sans-serif;
            }
            #systemWindow {
                background-color: rgba(5, 10, 20, 240);
                border: 1px solid rgba(0, 210, 255, 0.5);
                border-radius: 2px;
            }
            #header {
                border: 1px solid #00d2ff;
                margin: 40px 100px 0px 100px;
                max-height: 50px;
            }
            #headerText { color: white; font-size: 20px; letter-spacing: 4px; }
            #notifCategory { color: #00d2ff; font-weight: 700; font-size: 18px; }
            #notifMessage { font-size: 22px; color: #e0e0e0; }
            QPushButton {
                border: 1px solid #00d2ff;
                color: #00d2ff;
                padding: 8px 35px;
                font-weight: 700;
            }
            QPushButton:hover { background: rgba(0, 210, 255, 0.2); color: white; }
        """)
