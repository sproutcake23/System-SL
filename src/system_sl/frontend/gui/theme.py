def generate_main_qss(colors: dict) -> str:
    return f"""
/* === Solo Leveling System theme === */
/*
   Inspired by The System's UI in the manhwa: deep navy/black background,
   sharp electric-cyan accents, no rounded corners, high-contrast text.
*/

QWidget {{
    background-color: {colors['bg']};
    color: {colors['text']};
    font-family: "Segoe UI", "Helvetica Neue", "DejaVu Sans", sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background-color: {colors['bg_dark']};
}}

QLabel {{
    background-color: transparent;
    color: {colors['text_light']};
}}

/* --- Buttons --- */
QPushButton {{
    background-color: {colors['accent_dim_08']};
    color: {colors['accent_light']};
    border: 1px solid {colors['accent_border']};
    border-radius: 0px;
    padding: 6px 14px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {colors['accent_dim_18']};
    color: #b6f1ff;
    border: 1px solid {colors['accent']};
}}

QPushButton:pressed {{
    background-color: {colors['accent_dim_30']};
    border: 1px solid {colors['accent_light']};
}}

QPushButton:disabled {{
    background-color: rgba(255, 255, 255, 0.02);
    color: #3d4d68;
    border: 1px solid #1a2638;
}}

/* --- Checkbox --- */
QCheckBox {{
    color: {colors['text_light']};
    spacing: 8px;
    background-color: transparent;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {colors['accent_border']};
    background-color: {colors['bg']};
}}

QCheckBox::indicator:hover {{
    border: 1px solid {colors['accent']};
}}

QCheckBox::indicator:checked {{
    background-color: {colors['accent']};
    border: 1px solid {colors['accent']};
}}

/* --- Text inputs --- */
QLineEdit, QDateEdit, QTextEdit, QComboBox, QSpinBox, QPlainTextEdit {{
    background-color: {colors['bg_light']};
    color: {colors['text']};
    border: 1px solid {colors['accent_border']};
    border-radius: 0px;
    padding: 4px 6px;
    selection-background-color: {colors['accent_border']};
    selection-color: #ffffff;
}}

QLineEdit:focus, QDateEdit:focus, QTextEdit:focus,
QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {{
    border: 1px solid {colors['accent']};
}}

QLineEdit:disabled, QDateEdit:disabled, QComboBox:disabled {{
    background-color: #0a0f1c;
    color: #3d4d68;
    border: 1px solid #16263a;
}}

/* --- List widget (task list) --- */
QListWidget {{
    background-color: {colors['bg_light']};
    color: {colors['text']};
    border: 1px solid {colors['accent_border']};
    border-radius: 0px;
    outline: 0;
}}

QListWidget::item {{
    padding: 6px 8px;
    border-bottom: 1px solid #142036;
}}

QListWidget::item:hover {{
    background-color: {colors['accent_dim_06']};
}}

QListWidget::item:selected {{
    background-color: {colors['accent_dim_18']};
    color: #b6f1ff;
    border-left: 2px solid {colors['accent']};
}}

/* --- Combo box popup --- */
QComboBox::drop-down {{
    border: none;
    width: 18px;
    background-color: transparent;
}}

QComboBox::down-arrow {{
    image: none;
    width: 6px;
    height: 6px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {colors['accent_light']};
    margin-right: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {colors['bg_light']};
    color: {colors['text']};
    border: 1px solid {colors['accent_border']};
    selection-background-color: {colors['accent_dim_22']};
    selection-color: #b6f1ff;
}}

/* --- Date edit / calendar popup --- */
QDateEdit::drop-down {{
    border: none;
    width: 18px;
}}

QCalendarWidget {{
    background-color: {colors['bg_light']};
}}

QCalendarWidget QWidget {{
    background-color: {colors['bg_light']};
    color: {colors['text']};
}}

QCalendarWidget QWidget#qt_calendar_navigationbar {{
    background-color: #0b1424;
}}

QCalendarWidget QToolButton {{
    color: #b6f1ff;
    background-color: transparent;
    border: 1px solid transparent;
    padding: 4px 8px;
}}

QCalendarWidget QToolButton:hover {{
    background-color: {colors['accent_dim_18']};
    border: 1px solid {colors['accent']};
}}

QCalendarWidget QSpinBox {{
    background-color: {colors['bg_light']};
    color: {colors['text']};
    border: 1px solid {colors['accent_border']};
}}

QCalendarWidget QAbstractItemView:enabled {{
    background-color: {colors['bg_light']};
    color: {colors['text']};
    selection-background-color: {colors['accent_dim_32']};
    selection-color: #ffffff;
}}

QCalendarWidget QAbstractItemView:disabled {{
    color: #324158;
}}

/* --- Scrollbars --- */
QScrollBar:vertical {{
    background-color: {colors['bg']};
    width: 10px;
    border: none;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {colors['accent_border']};
    min-height: 24px;
    border: none;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors['accent']};
}}

QScrollBar:horizontal {{
    background-color: {colors['bg']};
    height: 10px;
    border: none;
}}

QScrollBar::handle:horizontal {{
    background-color: {colors['accent_border']};
    min-width: 24px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {colors['accent']};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    width: 0;
    height: 0;
    background: none;
    border: none;
}}

QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}

/* --- Message boxes --- */
QMessageBox {{
    background-color: {colors['bg_dark']};
}}

QMessageBox QLabel {{
    color: {colors['text']};
    background-color: transparent;
}}

/* --- Menus / context menus --- */
QMenu {{
    background-color: {colors['bg_light']};
    color: {colors['text']};
    border: 1px solid {colors['accent_border']};
}}

QMenu::item {{
    padding: 4px 18px;
}}

QMenu::item:selected {{
    background-color: {colors['accent_dim_20']};
    color: #b6f1ff;
}}

/* --- Tooltips --- */
QToolTip {{
    background-color: {colors['bg_light']};
    color: #b6f1ff;
    border: 1px solid {colors['accent']};
    padding: 4px 6px;
}}
"""