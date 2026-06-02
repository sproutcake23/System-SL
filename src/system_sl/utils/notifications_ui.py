from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Qt
from system_sl.utils.audio_manager import play_sound, get_current_sound


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
        # DELETED: self._apply_styles() is removed from here

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

    def display_message(self, category: str, message: str) -> None:
        self.cat_label.setText(f"[ {category.upper()} ]")
        self.msg_label.setText(message)
        current_sound = get_current_sound()
        play_sound(current_sound)
        self.show_system_style()

    def show_system_style(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def keyPressEvent(self, event):
        self.hide()

    def _apply_styles(self, colors: dict):
        # Using f-strings to inject the dynamic theme variables
        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                font-family: 'Montserrat', sans-serif;
            }}
            #systemWindow {{
                background-color: {colors.get('bg', 'rgba(5, 10, 20, 240)')};
                border: 1px solid {colors.get('accent_border', '#00d2ff')};
                border-radius: 2px;
            }}
            #header {{
                border: 1px solid {colors.get('accent_border', '#00d2ff')};
                margin: 40px 100px 0px 100px;
                max-height: 50px;
            }}
            #headerText {{ 
                color: {colors.get('text_light', 'white')}; 
                font-size: 20px; 
                letter-spacing: 4px; 
            }}
            #notifCategory {{ 
                color: {colors.get('accent', '#00d2ff')}; 
                font-weight: 700; 
                font-size: 18px; 
            }}
            #notifMessage {{ 
                font-size: 22px; 
                color: {colors.get('text', '#e0e0e0')}; 
            }}
            QPushButton {{
                border: 1px solid {colors.get('accent_border', '#00d2ff')};
                color: {colors.get('accent_light', '#00d2ff')};
                background-color: {colors.get('accent_dim_08', 'transparent')};
                padding: 8px 35px;
                font-weight: 700;
            }}
            QPushButton:hover {{ 
                background-color: {colors.get('accent_dim_18', 'rgba(0, 210, 255, 0.2)')}; 
                color: white; 
                border: 1px solid {colors.get('accent', '#00d2ff')};
            }}
            QPushButton:pressed {{
                background-color: {colors.get('accent_dim_30', 'rgba(0, 210, 255, 0.3)')};
            }}
        """)