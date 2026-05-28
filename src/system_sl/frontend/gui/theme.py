SOLO_LEVELING_QSS = """
/* === Solo Leveling System theme === */
/*
   Inspired by The System's UI in the manhwa: deep navy/black background,
   sharp electric-cyan accents, no rounded corners, high-contrast text.
*/

QWidget {
    background-color: #0b0f1a;
    color: #d6e7ff;
    font-family: "Segoe UI", "Helvetica Neue", "DejaVu Sans", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #060912;
}

QLabel {
    background-color: transparent;
    color: #b3d4ff;
}

/* --- Buttons --- */
QPushButton {
    background-color: rgba(0, 217, 255, 0.08);
    color: #67e8ff;
    border: 1px solid #1f6f99;
    border-radius: 0px;
    padding: 6px 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: rgba(0, 217, 255, 0.18);
    color: #b6f1ff;
    border: 1px solid #00d9ff;
}

QPushButton:pressed {
    background-color: rgba(0, 217, 255, 0.30);
    border: 1px solid #67e8ff;
}

QPushButton:disabled {
    background-color: rgba(255, 255, 255, 0.02);
    color: #3d4d68;
    border: 1px solid #1a2638;
}

/* --- Checkbox --- */
QCheckBox {
    color: #b3d4ff;
    spacing: 8px;
    background-color: transparent;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #1f6f99;
    background-color: #0b0f1a;
}

QCheckBox::indicator:hover {
    border: 1px solid #00d9ff;
}

QCheckBox::indicator:checked {
    background-color: #00d9ff;
    border: 1px solid #00d9ff;
}

/* --- Text inputs --- */
QLineEdit, QDateEdit, QTextEdit, QComboBox, QSpinBox, QPlainTextEdit {
    background-color: #0e1626;
    color: #d6e7ff;
    border: 1px solid #1f6f99;
    border-radius: 0px;
    padding: 4px 6px;
    selection-background-color: #1f6f99;
    selection-color: #ffffff;
}

QLineEdit:focus, QDateEdit:focus, QTextEdit:focus,
QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {
    border: 1px solid #00d9ff;
}

QLineEdit:disabled, QDateEdit:disabled, QComboBox:disabled {
    background-color: #0a0f1c;
    color: #3d4d68;
    border: 1px solid #16263a;
}

/* --- List widget (task list) --- */
QListWidget {
    background-color: #0e1626;
    color: #d6e7ff;
    border: 1px solid #1f6f99;
    border-radius: 0px;
    outline: 0;
}

QListWidget::item {
    padding: 6px 8px;
    border-bottom: 1px solid #142036;
}

QListWidget::item:hover {
    background-color: rgba(0, 217, 255, 0.06);
}

QListWidget::item:selected {
    background-color: rgba(0, 217, 255, 0.18);
    color: #b6f1ff;
    border-left: 2px solid #00d9ff;
}

/* --- Combo box popup --- */
QComboBox::drop-down {
    border: none;
    width: 18px;
    background-color: transparent;
}

QComboBox::down-arrow {
    image: none;
    width: 6px;
    height: 6px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #67e8ff;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #0e1626;
    color: #d6e7ff;
    border: 1px solid #1f6f99;
    selection-background-color: rgba(0, 217, 255, 0.22);
    selection-color: #b6f1ff;
}

/* --- Date edit / calendar popup --- */
QDateEdit::drop-down {
    border: none;
    width: 18px;
}

QCalendarWidget {
    background-color: #0e1626;
}

QCalendarWidget QWidget {
    background-color: #0e1626;
    color: #d6e7ff;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #0b1424;
}

QCalendarWidget QToolButton {
    color: #b6f1ff;
    background-color: transparent;
    border: 1px solid transparent;
    padding: 4px 8px;
}

QCalendarWidget QToolButton:hover {
    background-color: rgba(0, 217, 255, 0.18);
    border: 1px solid #00d9ff;
}

QCalendarWidget QSpinBox {
    background-color: #0e1626;
    color: #d6e7ff;
    border: 1px solid #1f6f99;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: #0e1626;
    color: #d6e7ff;
    selection-background-color: rgba(0, 217, 255, 0.32);
    selection-color: #ffffff;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #324158;
}

/* --- Scrollbars --- */
QScrollBar:vertical {
    background-color: #0b0f1a;
    width: 10px;
    border: none;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #1f6f99;
    min-height: 24px;
    border: none;
}

QScrollBar::handle:vertical:hover {
    background-color: #00d9ff;
}

QScrollBar:horizontal {
    background-color: #0b0f1a;
    height: 10px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #1f6f99;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #00d9ff;
}

QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
    background: none;
    border: none;
}

QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}

/* --- Message boxes --- */
QMessageBox {
    background-color: #060912;
}

QMessageBox QLabel {
    color: #d6e7ff;
    background-color: transparent;
}

/* --- Menus / context menus --- */
QMenu {
    background-color: #0e1626;
    color: #d6e7ff;
    border: 1px solid #1f6f99;
}

QMenu::item {
    padding: 4px 18px;
}

QMenu::item:selected {
    background-color: rgba(0, 217, 255, 0.20);
    color: #b6f1ff;
}

/* --- Tooltips --- */
QToolTip {
    background-color: #0e1626;
    color: #b6f1ff;
    border: 1px solid #00d9ff;
    padding: 4px 6px;
}
"""
