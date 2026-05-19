import os
import subprocess
import sys


# --- Linux (systemd user unit) ---
SERVICE_NAME = "sl-notifer.service"
SERVICE_PATH = os.path.expanduser(f"~/.config/systemd/user/{SERVICE_NAME}")

# --- Windows (Startup folder .vbs) ---
STARTUP_FILENAME = "system-sl-autostart.vbs"


def _windows_startup_dir() -> str:
    appdata = os.environ.get("APPDATA") or os.path.expanduser(
        "~\\AppData\\Roaming"
    )
    return os.path.join(
        appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
    )


def _windows_startup_path() -> str:
    return os.path.join(_windows_startup_dir(), STARTUP_FILENAME)


def _bg_command_parts() -> tuple[str, list[str]]:
    """Return (executable, args) to launch System-SL in background mode."""
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.executable), ["--bg"]
    return sys.executable, [os.path.abspath(sys.argv[0]), "--bg"]


class AutostartManager:
    def __init__(self):
        self._is_windows = os.name == "nt"

    # --- Public interface ---

    def is_enabled(self) -> bool:
        if self._is_windows:
            return self._windows_is_enabled()
        return self._linux_is_enabled()

    def toggle(self) -> bool:
        if self._is_windows:
            return self._windows_toggle()
        return self._linux_toggle()

    # --- Linux (systemd --user) ---

    def _linux_is_enabled(self) -> bool:
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-enabled", SERVICE_NAME],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() == "enabled"
        except Exception:
            return False

    def _linux_toggle(self) -> bool:
        if self._linux_is_enabled():
            subprocess.run(
                ["systemctl", "--user", "disable", "--now", SERVICE_NAME],
                capture_output=True,
            )
            if os.path.exists(SERVICE_PATH):
                os.remove(SERVICE_PATH)
            subprocess.run(
                ["systemctl", "--user", "daemon-reload"], capture_output=True
            )
            return False

        subprocess.run(
            ["systemctl", "--user", "unmask", SERVICE_NAME], capture_output=True
        )

        if getattr(sys, "frozen", False):
            exec_cmd = f"{os.path.abspath(sys.executable)} --bg"
        else:
            exec_cmd = f"{sys.executable} {os.path.abspath(sys.argv[0])} --bg"

        os.makedirs(os.path.dirname(SERVICE_PATH), exist_ok=True)
        try:
            with open(SERVICE_PATH, "w") as f:
                f.write(
                    "[Unit]\n"
                    "Description=System-SL Autostart\n"
                    "After=graphical-session.target\n\n"
                    "[Service]\n"
                    f"ExecStart={exec_cmd}\n"
                    "Restart=always\n"
                    "Environment=DISPLAY=:0\n"
                    "Environment=WAYLAND_DISPLAY=wayland-0\n"
                    "Environment=XDG_RUNTIME_DIR=/run/user/1000\n\n"
                    "[Install]\n"
                    "WantedBy=default.target"
                )

            subprocess.run(
                ["systemctl", "--user", "daemon-reload"], capture_output=True
            )

            result = subprocess.run(
                ["systemctl", "--user", "enable", "--now", SERVICE_NAME],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"\n[SYSTEMD ERROR]: {result.stderr.strip()}")
                return False

            return True

        except Exception as e:
            print(f"\n[FILE ERROR]: Could not write service file: {e}")
            return False

    # --- Windows (Startup folder .vbs) ---

    def _windows_is_enabled(self) -> bool:
        return os.path.exists(_windows_startup_path())

    def _windows_toggle(self) -> bool:
        path = _windows_startup_path()

        if os.path.exists(path):
            try:
                os.remove(path)
                return False
            except OSError as e:
                print(f"\n[FILE ERROR]: Could not remove autostart .vbs: {e}")
                return True

        try:
            os.makedirs(_windows_startup_dir(), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(self._build_vbs_body())
            return True
        except OSError as e:
            print(f"\n[FILE ERROR]: Could not write autostart .vbs: {e}")
            return False

    def _build_vbs_body(self) -> str:
        """Build a VBS that launches System-SL hidden, in the background.

        WshShell.Run takes one command-line string. Each argument is
        wrapped in escaped double quotes (`""` is VBS's quote-escape) so
        paths containing spaces survive both the VBS string literal and
        Windows command-line parsing.
        """
        exe, args = _bg_command_parts()
        quoted = [f'""{exe}""'] + [f'""{a}""' for a in args]
        command_line = " ".join(quoted)
        return (
            'Set WshShell = CreateObject("WScript.Shell")\r\n'
            f'WshShell.Run "{command_line}", 0, False\r\n'
        )
