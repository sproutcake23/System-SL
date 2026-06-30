import os
import html

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from system_sl.chatbot import ChatSession, ChatConfigError
# --- NEW: Import Dynamic Theming Utilities ---
from system_sl.utils import get_wallpaper_path
from system_sl.utils.theme_gen import generate_dynamic_tokens, DEFAULT_TOKENS


class _ChatWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, session: ChatSession, user_msg: str):
        super().__init__()
        self.session = session
        self.user_msg = user_msg

    def run(self):
        try:
            reply = self.session.run_turn(self.user_msg)
        except Exception as e:
            self.failed.emit(f"{type(e).__name__}: {e}")
            return
        self.finished.emit(reply)


class ChatPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._sessions: dict[str, ChatSession] = {}
        self._thread: QThread | None = None
        self._worker: _ChatWorker | None = None

        root = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Channel:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("system")
        self.mode_combo.addItem("friend")
        header.addWidget(self.mode_combo)
        header.addStretch(1)
        root.addLayout(header)

        self.transcript = QTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setPlaceholderText(
            "[ awaiting Player input — channel: SYSTEM ]"
        )
        root.addWidget(self.transcript, stretch=1)

        input_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Speak, Player...")
        self.input_box.returnPressed.connect(self._on_send)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._on_send)
        input_row.addWidget(self.input_box, stretch=1)
        input_row.addWidget(self.send_button)
        root.addLayout(input_row)

    # ----- session lifecycle -----

    def _current_mode(self) -> str:
        return self.mode_combo.currentText()
    
    def _get_live_tokens(self) -> dict:
        """Fetches the live dynamic theme colors for the chat HTML."""
        try:
            path = get_wallpaper_path()
            if path and "Error" not in path:
                return generate_dynamic_tokens(os.path.expanduser(path))
        except Exception:
            pass
        return DEFAULT_TOKENS

    def _bot_label(self, tokens: dict) -> tuple[str, str]:
        if self._current_mode() == "system":
            # Map SYSTEM to the dynamic primary accent color
            return "SYSTEM", tokens.get("sys_color_primary", "#00d9ff")
        # Friend persona remains distinct purple
        return "FRIEND", "#c084fc"

    def _get_session(self, mode: str) -> ChatSession | None:
        if mode not in self._sessions:
            try:
                self._sessions[mode] = ChatSession(mode)  # type: ignore[arg-type]
            except ChatConfigError as e:
                self._append_alert(str(e))
                return None
            except Exception as e:
                self._append_alert(f"Could not open channel: {e}")
                return None
        return self._sessions[mode]

    # ----- transcript rendering -----

    def _append_html(self, html_line: str) -> None:
        self.transcript.append(html_line)

    def _format_line(self, label: str, label_color: str, body_color: str, text: str) -> str:
        safe = html.escape(text).replace("\n", "<br>")
        return (
            f'<span style="color:{label_color}; font-weight:bold">[{label}]</span> '
            f'<span style="color:{body_color}">{safe}</span>'
        )

    def _append_player(self, text: str) -> None:
        tokens = self._get_live_tokens()
        # Map Player to the secondary text color
        label_color = tokens.get("sys_color_text_secondary", "#9ab8e5")
        body_color = tokens.get("sys_color_text_main", "#d6e7ff")
        self._append_html(self._format_line("PLAYER", label_color, body_color, text))

    def _append_bot(self, text: str) -> None:
        tokens = self._get_live_tokens()
        label, label_color = self._bot_label(tokens)
        body_color = tokens.get("sys_color_text_main", "#d6e7ff")
        self._append_html(self._format_line(label, label_color, body_color, text))

    def _append_alert(self, text: str) -> None:
        safe = html.escape(text).replace("\n", "<br>")
        alert_color = "#ff6b8a" # Alerts stay explicitly red
        self._append_html(
            f'<span style="color:{alert_color}; font-weight:bold">[ALERT]</span> '
            f'<span style="color:{alert_color}">{safe}</span>'
        )

    # ----- input flow -----

    def _set_busy(self, busy: bool) -> None:
        self.send_button.setEnabled(not busy)
        self.input_box.setEnabled(not busy)
        self.mode_combo.setEnabled(not busy)

    def _on_send(self) -> None:
        if self._thread is not None:
            return
        text = self.input_box.text().strip()
        if not text:
            return

        mode = self._current_mode()
        session = self._get_session(mode)
        if session is None:
            return

        self.input_box.clear()
        self._append_player(text)
        self._set_busy(True)

        self._thread = QThread(self)
        self._worker = _ChatWorker(session, text)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_reply)
        self._worker.failed.connect(self._on_failure)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.start()

    def _on_reply(self, reply: str) -> None:
        self._append_bot(reply or "[empty reply]")

    def _on_failure(self, message: str) -> None:
        self._append_alert(message)

    def _cleanup_thread(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
        if self._thread is not None:
            self._thread.deleteLater()
            self._thread = None
        self._set_busy(False)
        self.input_box.setFocus()