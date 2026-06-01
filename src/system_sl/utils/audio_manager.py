import os
import sys

# 1. Force the environment to be quiet before Qt even loads
os.environ["AV_LOG_LEVEL"] = "quiet"
os.environ["QT_LOGGING_RULES"] = "*=false"

from PySide6.QtCore import QUrl, QEventLoop, QTimer, qInstallMessageHandler
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from system_sl.utils.json_client import load_data, save_data
from system_sl.utils.paths import get_tasks_file_path

# 2. Native Qt Silencer: Catches any remaining C-level logs and drops them
def _silent_qt_message_handler(mode, context, message):
    pass
qInstallMessageHandler(_silent_qt_message_handler)


SETTINGS_FILE = get_tasks_file_path("settings.json")
DEFAULT_SOUNDS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "sounds")
)
FALLBACK_SOUND = os.path.join(DEFAULT_SOUNDS_DIR, "default.wav")

_player = None
_audio_output = None

def _get_player():
    global _player, _audio_output
    if _player is None:
        _player = QMediaPlayer()
        _audio_output = QAudioOutput()
        _audio_output.setVolume(1.0)
        _player.setAudioOutput(_audio_output)
    return _player

def get_current_sound() -> str:
    data = load_data(SETTINGS_FILE)
    sound_path = data.get("notification_sound", FALLBACK_SOUND)
    return sound_path if os.path.exists(sound_path) else FALLBACK_SOUND

def play_sound(file_path: str):
    player = _get_player()
    player.setSource(QUrl.fromLocalFile(file_path))
    player.play()

def check_audio_duration(file_path: str) -> int:
    player = _get_player()
    player.setSource(QUrl.fromLocalFile(file_path))
    
    # Wait for the file to load so we can get the duration
    loop = QEventLoop()
    def on_status_changed(status):
        if status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.InvalidMedia):
            loop.quit()
            
    player.mediaStatusChanged.connect(on_status_changed)
    QTimer.singleShot(1500, loop.quit) 
    loop.exec()
    player.mediaStatusChanged.disconnect(on_status_changed)
    
    return player.duration()

def set_sound_setting(file_path: str):
    data = load_data(SETTINGS_FILE)
    data["notification_sound"] = os.path.abspath(file_path)
    save_data(SETTINGS_FILE, data)