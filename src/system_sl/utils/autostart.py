# import os
# import subprocess
# import sys

# SERVICE_NAME = "sl-notifer.service"
# SERVICE_PATH = os.path.expanduser(f"~/.config/systemd/user/{SERVICE_NAME}")


# class AutostartManager:
#     def is_enabled(self):
#         try:
#             result = subprocess.run(
#                 ["systemctl", "--user", "is-enabled", SERVICE_NAME],
#                 capture_output=True,
#                 text=True,
#             )
#             return result.stdout.strip() == "enabled"
#         except Exception:
#             return False

#     def toggle(self):
#         if self.is_enabled():
#             subprocess.run(
#                 ["systemctl", "--user", "disable", "--now", SERVICE_NAME],
#                 capture_output=True,
#             )
#             if os.path.exists(SERVICE_PATH):
#                 os.remove(SERVICE_PATH)
#             subprocess.run(
#                 ["systemctl", "--user", "daemon-reload"], capture_output=True
#             )
#             return False

#         else:
#             subprocess.run(
#                 ["systemctl", "--user", "unmask", SERVICE_NAME], capture_output=True
#             )

#             if getattr(sys, "frozen", False):
#                 exec_cmd = f"{os.path.abspath(sys.executable)} --bg"
#             else:
#                 exec_cmd = f"{sys.executable} {os.path.abspath(sys.argv[0])} --bg"

#             os.makedirs(os.path.dirname(SERVICE_PATH), exist_ok=True)
#             try:
#                 with open(SERVICE_PATH, "w") as f:
#                     f.write(
#                         "[Unit]\n"
#                         "Description=System-SL Autostart\n"
#                         "After=graphical-session.target\n\n"
#                         "[Service]\n"
#                         f"ExecStart={exec_cmd}\n"
#                         "Restart=always\n"
#                         "Environment=DISPLAY=:0\n"
#                         "Environment=WAYLAND_DISPLAY=wayland-0\n"
#                         "Environment=XDG_RUNTIME_DIR=/run/user/1000\n\n"
#                         "[Install]\n"
#                         "WantedBy=default.target"
#                     )

#                 subprocess.run(
#                     ["systemctl", "--user", "daemon-reload"], capture_output=True
#                 )

#                 result = subprocess.run(
#                     ["systemctl", "--user", "enable", "--now", SERVICE_NAME],
#                     capture_output=True,
#                     text=True,
#                 )

#                 if result.returncode != 0:
#                     print(f"\n[SYSTEMD ERROR]: {result.stderr.strip()}")
#                     return False

#                 return True

#             except Exception as e:
#                 print(f"\n[FILE ERROR]: Could not write service file: {e}")
#                 return False


import os
import platform
import sys
import subprocess

class CrossPlatformAutostart:
    def __init__(self, app_name="SL-Notifier"):
        self.app_name = app_name
        self.os_type = platform.system()
        
    def _get_exec_cmd(self) -> str:
        """Determines the correct command to execute this script/binary safely cross-platform."""
        if getattr(sys, "frozen", False):
            return f'"{os.path.abspath(sys.executable)}" --bg'
        

        script_path = os.path.abspath(sys.argv[0])
        if not script_path.endswith(".py"):
            return f"{script_path} --bg"
        
        python_exe = os.path.abspath(sys.executable)
        
        if platform.system() == "Windows":
            # Windows needs quotes around individual paths to handle folder paths containing spaces safely
            return f'"{python_exe}" "{script_path}" --bg'
        return f"{python_exe} {script_path} --bg"
    
    def is_enabled(self) -> bool:
        if self.os_type == "Windows":
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
                winreg.QueryValueEx(key, self.app_name)
                return True
            except FileNotFoundError:
                return False

        elif self.os_type == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            return os.path.exists(os.path.join(autostart_dir, f"{self.app_name.lower()}.desktop"))

        elif self.os_type == "Darwin":  # macOS
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.{self.app_name.lower()}.plist")
            return os.path.exists(plist_path)
            
        return False

    def enable(self) -> bool:
        exec_cmd = self._get_exec_cmd()

        if self.os_type == "Windows":
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                # For Windows, we wrap the command in quotes if it contains spaces
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, exec_cmd)
                return True
            except Exception as e:
                print(f"Windows Registry Error: {e}")
                return False

        elif self.os_type == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_path = os.path.join(autostart_dir, f"{self.app_name.lower()}.desktop")
            
            # 1. Resolve the true project root path
            base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
            while base_dir != "/" and not os.path.exists(os.path.join(base_dir, ".venv")):
                base_dir = os.path.dirname(base_dir)
            if base_dir == "/":
                base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

            # 2. Extract active system environment hooks (Fallback defaults if missing)
            current_display = os.environ.get("DISPLAY", ":0")
            current_dbus = os.environ.get("DBUS_SESSION_BUS_ADDRESS", "")

            # 3. Build a wrapper command that passes desktop display permissions to uv
            # We run it through /bin/sh to force inject the system display variables
            wrapped_exec = (
                f'/bin/sh -c "DISPLAY={current_display} '
                f'DBUS_SESSION_BUS_ADDRESS=\'{current_dbus}\' '
                f'{exec_cmd}"'
            )

            try:
                with open(desktop_path, "w") as f:
                    f.write(
                        "[Desktop Entry]\n"
                        "Type=Application\n"
                        f"Name={self.app_name}\n"
                        f"Exec={wrapped_exec}\n"  # ◄─── Passes display environment hooks cleanly
                        f"Path={base_dir}\n"
                        "Hidden=false\n"
                        "NoDisplay=false\n"
                        "X-GNOME-Autostart-enabled=true\n"
                    )
                return True
            except Exception as e:
                print(f"Linux Autostart Error: {e}")
                return False        
            except Exception as e:
                print(f"Linux Autostart Error: {e}")
                return False

        elif self.os_type == "Darwin":  # macOS
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.{self.app_name.lower()}.plist")
            # Break command into components for the plist array
            cmd_args = exec_cmd.split() 
            args_xml = "".join(f"<string>{arg}</string>" for arg in cmd_args)
            
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{self.app_name.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        {args_xml}
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
            try:
                os.makedirs(os.path.dirname(plist_path), exist_ok=True)
                with open(plist_path, "w") as f:
                    f.write(plist_content)
                # Load the agent immediately
                subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", plist_path], capture_output=True)
                return True
            except Exception as e:
                print(f"macOS LaunchAgent Error: {e}")
                return False

        return False

    def disable(self) -> bool:
        if self.os_type == "Windows":
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, self.app_name)
                return True
            except FileNotFoundError:
                return True  # Already disabled
            except Exception as e:
                print(f"Windows Registry Error: {e}")
                return False

        elif self.os_type == "Linux":
            desktop_path = os.path.expanduser(f"~/.config/autostart/{self.app_name.lower()}.desktop")
            if os.path.exists(desktop_path):
                os.remove(desktop_path)
            return True

        elif self.os_type == "Darwin":  # macOS
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.{self.app_name.lower()}.plist")
            if os.path.exists(plist_path):
                # Unload first
                subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", plist_path], capture_output=True)
                os.remove(plist_path)
            return True

        return False

    def toggle(self) -> bool:
        if self.is_enabled():
            self.disable()
            return False
        else:
            return self.enable()

# Example Usage:
if __name__ == "__main__":
    manager = CrossPlatformAutostart("SOLO_LEVELING")
    
    # Check status
    print(f"Autostart enabled: {manager.is_enabled()}")
    
    # Toggle it
    new_state = manager.toggle()
    print(f"Toggled! New autostart state: {new_state}")