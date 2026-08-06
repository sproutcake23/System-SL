import os
import sys
from pathlib import Path
import subprocess

from dotenv import load_dotenv, set_key
from PySide6.QtCore import QSize, QTimer, QSettings, QFileSystemWatcher, Slot, QObject
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QFileDialog,
    QInputDialog,
)
from system_sl.frontend.gui.popup_windows import TasksWindow, OnboardingWindow
from system_sl.frontend.gui.chat_panel import ChatPanel
from system_sl.frontend.gui.theme import get_stylesheet
from system_sl.utils import (
    CrossPlatformAutostart,
    SystemNotification,
    get_tasks_file_path,
    get_wallpaper_path,
)
from system_sl.core import GoogleSyncEngine, CalendarProvider, TasksProvider
from system_sl.core.onboarding import PersonaStorageHandler
from system_sl.services import BackgroundServiceController
from system_sl.utils.audio_manager import (
    play_sound,
    set_sound_setting,
    DEFAULT_SOUNDS_DIR,
)
from system_sl.core.priority_engine_new import run_prioritization
from system_sl.utils.theme_gen import generate_dynamic_tokens
from system_sl.utils.autostart_migration import initialize_application_autostart
from system_sl.utils.auto_updater import (
    UpdateCheckThread,
    load_auto_update_preference,
    save_auto_update_preference,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setMinimumSize(QSize(700, 400))

        # --- NEW: Theme Settings Initialization ---
        self.settings = QSettings("system-sl", "AppConfig")
        self.last_wallpaper_path = None
        self.wallpaper_timer = QTimer(self)
        self.wallpaper_timer.timeout.connect(self.check_wallpaper_update)

        self.autostart = CrossPlatformAutostart()
        self.tasks_window = None
        self.update_thread = None

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

        # --- NEW: Dynamic Theme Checkbox ---
        self.theme_toggle = QCheckBox("Enable Dynamic Theming")
        is_dynamic = self.settings.value("dynamic_theming", False, type=bool)
        self.theme_toggle.setChecked(is_dynamic)
        self.theme_toggle.clicked.connect(self.on_theme_toggle_changed)

        left_layout.addWidget(task_button)
        left_layout.addWidget(google_button)
        left_layout.addWidget(sound_button)
        left_layout.addWidget(self.check_box)
        left_layout.addWidget(self.theme_toggle) # Added to the left panel UI

        self.auto_update_check = QCheckBox("Auto Update")
        self.auto_update_check.setChecked(load_auto_update_preference())
        self.auto_update_check.clicked.connect(self._toggle_auto_update)
        left_layout.addWidget(self.auto_update_check)

        # right box — chatbot panel (system / friend modes)
        self.chat_panel = ChatPanel(self)

        layout.addWidget(left_widget, stretch=1)
        layout.addWidget(self.chat_panel, stretch=3)

        # Start the background watcher if it was enabled during the last session
        if is_dynamic:
            self.start_dynamic_theming()

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
        except Exception as e:
            message_box.setWindowTitle("Error")
            message_box.setText(str(e))
            message_box.exec()

    def change_notification_sound(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Notification Sound",
            DEFAULT_SOUNDS_DIR,
            "Audio Files (*.wav *.mp3)",
        )
        if file_path:
            try:
                set_sound_setting(file_path)
                play_sound(file_path)
                QMessageBox.information(self, "Success", "Notification sound updated!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to set sound:\n{str(e)}")

    # --- NEW: Theme Manager Methods ---
    def on_theme_toggle_changed(self):
        is_checked = self.theme_toggle.isChecked()
        self.settings.setValue("dynamic_theming", is_checked)
        if is_checked:
            self.start_dynamic_theming()
        else:
            self.stop_dynamic_theming()

    def start_dynamic_theming(self):
        self.wallpaper_timer.start(5000) # Poll every 5 seconds
        self.check_wallpaper_update() # Instantly check when toggled on

    def stop_dynamic_theming(self):
        self.wallpaper_timer.stop()
        self.last_wallpaper_path = None
        QApplication.instance().setStyleSheet(get_stylesheet()) # Reset to fallback Theme

    def check_wallpaper_update(self):
        current_path = get_wallpaper_path()
        if current_path and current_path != self.last_wallpaper_path and "Error" not in current_path:
            self.last_wallpaper_path = current_path
            
            # Safely expand paths like ~/Pictures/wallpaper.jpg
            expanded_path = os.path.expanduser(current_path)
            
            # Generate new semantic tokens and inject them into the stylesheet
            new_tokens = generate_dynamic_tokens(expanded_path)
            QApplication.instance().setStyleSheet(get_stylesheet(new_tokens))

    def _toggle_auto_update(self):
        enabled = self.auto_update_check.isChecked()
        save_auto_update_preference(enabled)

    def _check_for_updates(self):
        if not load_auto_update_preference():
            return
        self.update_thread = UpdateCheckThread()
        self.update_thread.update_complete.connect(self._on_update_complete)
        self.update_thread.start()

    def _on_update_complete(self, success, message):
        if success:
            QMessageBox.information(self, "Auto Update", message)
        else:
            if "Updated to" not in message:
                QMessageBox.warning(self, "Auto Update", message)


# # ─── ADD THIS RELOADER CLASS AT THE TOP OF YOUR FILE ──────────────────
# class DevelopmentAutoReloader(QObject):
#     """Watches the source file and instantly swaps the process in RAM when you save."""
#     def __init__(self, app_instance: QApplication):
#         super().__init__()
#         self.app = app_instance
#         self.watcher = QFileSystemWatcher()
        
#         # Monitor the absolute path of this main.py file
#         self.script_path = os.path.abspath(sys.argv[0])
#         self.watcher.addPath(self.script_path)
#         self.watcher.fileChanged.connect(self.trigger_hot_reload)
#         print(f"[RELOADER] Monitoring file for live RAM updates: {self.script_path}")

#     @Slot(str)
#     def trigger_hot_reload(self, path: str):
#         print("\n[RELOADER] Change detected! Swapping process in RAM...")
        
#         # Cross-platform check for compiled executable deployment vs source development
#         if getattr(sys, "frozen", False):
#             # Deployed Mode: The executable spawns itself directly
#             subprocess.Popen([sys.executable] + sys.argv[1:])
#         else:
#             # Development Mode: Python spawns the live script file
#             subprocess.Popen([sys.executable, self.script_path] + sys.argv[1:])
        
#         # Kill this old instance out of memory instantly
#         self.app.quit()
#         os._exit(0)

def main():
    app = QApplication(sys.argv)
    
    # --- CHANGED: Inject the dynamic stylesheet on launch ---
    app.setStyleSheet(get_stylesheet())
    app.setQuitOnLastWindowClosed(False)
    initialize_application_autostart()

    # reload = DevelopmentAutoReloader(app)

    view = None
    controller = None
    
    if "--bg" in sys.argv:
        print("[INFO] Running in background notifier mode...")
        # --- NEW: Fetch live theme specifically for background notifications ---
        current_wall = get_wallpaper_path()
        if current_wall and "Error" not in current_wall:
            expanded_path = os.path.expanduser(current_wall)
            app.setStyleSheet(get_stylesheet(generate_dynamic_tokens(expanded_path)))

        view = SystemNotification()
        controller = BackgroundServiceController(view)
        controller.poll_and_render_task()

        sys.exit(app.exec())
    # Background notifier mode: the autostart systemd unit launches the app with
    # `--bg`. In this mode we run ONLY the hourly task notifier, never the main
    # menu. Opening the menu here would make the always-restarting service
    # reopen it every time it was closed.


    env_path = Path(get_tasks_file_path(".env"))
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        key, ok = QInputDialog.getText(
            None,
            "Missing API Key",
            "Paste GOOGLE_API_KEY:",
        )
        if not ok or not key.strip():
            QMessageBox.critical(
                None,
                "API Key Required",
                "No GOOGLE_API_KEY was provided. The app cannot continue.",
            )
        api_key = key.strip()
        os.environ["GOOGLE_API_KEY"] = api_key

        env_path.touch(exist_ok=True)
        set_key(str(env_path), "GOOGLE_API_KEY", api_key)

    try:
        storage = PersonaStorageHandler()
        if storage.is_first_time():
            onboarding = OnboardingWindow()
            main_window = None

            def _on_onboarding_done(result):
                nonlocal main_window
                main_window = MainWindow()
                main_window.show()
                main_window._check_for_updates()

            onboarding.onboarding_complete.connect(_on_onboarding_done)
            onboarding.show()
        else:
            main_window = MainWindow()
            main_window.show()
            main_window._check_for_updates()
            v = SystemNotification()
            control = BackgroundServiceController(v)
            control.poll_and_render_task()  

    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
