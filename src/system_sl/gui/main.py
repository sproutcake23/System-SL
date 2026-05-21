import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout, \
    QMessageBox
from system_sl.gui.popup_windows import TasksWindow
from system_sl.gui.chat_panel import ChatPanel
from system_sl.gui.theme import SOLO_LEVELING_QSS
from system_sl.utils.autostart import AutostartManager
from system_sl.core import GoogleSyncEngine, CalendarProvider, TasksProvider

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setMinimumSize(QSize(700,400))

        self.autostart = AutostartManager()
        self.tasks_window = None

        main_container = QWidget()
        self.setCentralWidget(main_container)
        layout = QHBoxLayout(main_container)

        # left box
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        task_button = QPushButton("Tasks")
        task_button.clicked.connect(self.open_tasks_window)

        google_button = QPushButton("Google")
        google_button.clicked.connect(self.sync_calendar)

        self.check_box = QCheckBox("Notification AutoStart")
        initial_state = self.autostart.is_enabled()
        self.check_box.setChecked(initial_state)
        self.check_box.clicked.connect(self.notification_autostart)

        left_layout.addWidget(task_button)
        left_layout.addWidget(google_button)
        left_layout.addWidget(self.check_box)

        # right box — chatbot panel (system / friend modes)
        self.chat_panel = ChatPanel(self)

        layout.addWidget(left_widget,stretch=1)
        layout.addWidget(self.chat_panel,stretch=3)

    def open_tasks_window(self):
        if self.tasks_window is None:
            self.tasks_window = TasksWindow()
        self.tasks_window.show()

    def notification_autostart(self):
        self.autostart.toggle()
        message_box = QMessageBox()
        message_box.setWindowTitle("Auto Start")
        if self.check_box.isChecked():
            message_box.setText("Enabled AutoStart")
        else:
            message_box.setText("Disabled AutoStart")
        message_box.exec()

    def sync_calendar(self):
        message_box = QMessageBox()
        try:
            engine = GoogleSyncEngine()
            engine.execute_sync(CalendarProvider(engine.client))
            engine.execute_sync(TasksProvider(engine.client))
            # sync_calendar_events()
            # sync_google_tasks()
        except Exception as e:
            message_box.setWindowTitle("Error")
            message_box.setText(str(e))
            message_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(SOLO_LEVELING_QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
