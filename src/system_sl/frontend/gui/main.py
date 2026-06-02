import sys
import os
from PySide6.QtCore import QSize, QFileSystemWatcher
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout, \
    QMessageBox
from system_sl.frontend.gui.popup_windows import TasksWindow
from system_sl.frontend.gui.chat_panel import ChatPanel
from system_sl.frontend.gui.theme import generate_main_qss
from system_sl.utils.theme_manager import get_system_colors, THEME_FILE_PATH
from system_sl.utils import AutostartManager, SystemNotification
from system_sl.core import GoogleSyncEngine, CalendarProvider, TasksProvider
from system_sl.services import BackgroundServiceController

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
        
        # --- LIVE THEME WATCHER ---
        self.theme_watcher = QFileSystemWatcher()
        if os.path.exists(THEME_FILE_PATH):
            self.theme_watcher.addPath(THEME_FILE_PATH)
            
        self.theme_watcher.fileChanged.connect(self.reload_theme)

    # ---> THIS WAS THE MISSING FUNCTION <---
    def reload_theme(self):
        """Triggers instantly when the TOML file is modified."""
        colors = get_system_colors()
        new_qss = generate_main_qss(colors)
        QApplication.instance().setStyleSheet(new_qss)

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

def main():
    app = QApplication(sys.argv)

    # Background notifier mode: the autostart systemd unit launches the app with
    # `--bg`. In this mode we run ONLY the hourly task notifier, never the main
    # menu. Opening the menu here would make the always-restarting service
    # reopen it every time it was closed.
    if "--bg" in sys.argv:
        view = SystemNotification()
        colors = get_system_colors()
        view._apply_styles(colors)
        
        controller = BackgroundServiceController(view)
        controller.poll_and_render_task()
        sys.exit(app.exec())
        
    colors = get_system_colors()
    app.setStyleSheet(generate_main_qss(colors))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
     main()