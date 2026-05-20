import os
import subprocess
import sys

SERVICE_NAME = "sl-notifer.service"
SERVICE_PATH = os.path.expanduser(f"~/.config/systemd/user/{SERVICE_NAME}")


class AutostartManager:
    def is_enabled(self):
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-enabled", SERVICE_NAME],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() == "enabled"
        except Exception:
            return False

    def toggle(self):
        if self.is_enabled():
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

        else:
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
