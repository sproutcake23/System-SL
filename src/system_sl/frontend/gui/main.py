import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout, \
    QMessageBox,QFileDialog
from system_sl.frontend.gui.popup_windows import TasksWindow, OnboardingWindow
from system_sl.core.onboarding import PersonaStorageHandler
from system_sl.frontend.gui.chat_panel import ChatPanel
from system_sl.frontend.gui.theme import SOLO_LEVELING_QSS
from system_sl.utils import AutostartManager, SystemNotification
from system_sl.core import GoogleSyncEngine, CalendarProvider, TasksProvider
from system_sl.services import BackgroundServiceController
from system_sl.utils.audio_manager import play_sound, set_sound_setting, DEFAULT_SOUNDS_DIR


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

        sound_button = QPushButton("Set Notification Sound")
        sound_button.clicked.connect(self.change_notification_sound)

        self.check_box = QCheckBox("Notification AutoStart")
        initial_state = self.autostart.is_enabled()
        self.check_box.setChecked(initial_state)
        self.check_box.clicked.connect(self.notification_autostart)

        left_layout.addWidget(task_button)
        left_layout.addWidget(google_button)
        left_layout.addWidget(sound_button)
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
        message_box = QMessageBox(self)
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

    def change_notification_sound(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Notification Sound",
            DEFAULT_SOUNDS_DIR,
            "Audio Files (*.wav *.mp3)"
        )
        if file_path:
            try:
                set_sound_setting(file_path)
                play_sound(file_path)
                QMessageBox.information(self, "Success", "Notification sound updated!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to set sound:\n{str(e)}")


def main():
    app = QApplication(sys.argv)

    # Background notifier mode: the autostart systemd unit launches the app with
    # `--bg`. In this mode we run ONLY the hourly task notifier, never the main
    # menu. Opening the menu here would make the always-restarting service
    # reopen it every time it was closed.
    if "--bg" in sys.argv:
        view = SystemNotification()
        controller = BackgroundServiceController(view)
        controller.poll_and_render_task()
        sys.exit(app.exec())

    app.setStyleSheet(SOLO_LEVELING_QSS)

    try:
        storage = PersonaStorageHandler()
        if storage.is_first_time():
            onboarding = OnboardingWindow()
            main_window = None

            def _on_onboarding_done(result):
                nonlocal main_window
                main_window = MainWindow()
                main_window.show()

            onboarding.onboarding_complete.connect(_on_onboarding_done)
            onboarding.show()
        else:
            main_window = MainWindow()
            main_window.show()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

    sys.exit(app.exec())

if __name__ == "__main__":
     main()
