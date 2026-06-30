import os
import platform
import subprocess
import xml.etree.ElementTree as ET

def get_wallpaper_path():
    system_name = platform.system().lower()
    
    if system_name == "windows":
        # Windows: Use the built-in winreg module instead of PowerShell
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
                path, _ = winreg.QueryValueEx(key, "Wallpaper")
                return path.strip()
        except FileNotFoundError:
            return "Error: Wallpaper registry key not found."
        except Exception as e:
            return f"Error reading registry: {e}"
    elif system_name == "darwin":  # macOS support added
        try:
            script = 'tell application "System Events" to tell every desktop to get picture'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error running osascript: {e}"
        
    elif system_name == "linux":
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        
        if "gnome" in desktop or "unity" in desktop:
            try:
                # Check if system is using dark mode
                theme_req = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                    capture_output=True, text=True
                )
                uri_key = "picture-uri-dark" if "prefer-dark" in theme_req.stdout else "picture-uri"

                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.background", uri_key],
                    capture_output=True, text=True, check=True
                )
                path = result.stdout.strip()
                path = path.strip("'").replace("file://", "")
                return path if path else "No active GNOME wallpaper found."
            except FileNotFoundError:
                return "Error: gsettings not found."
            except subprocess.CalledProcessError as e:
                return f"Error running gsettings: {e}"
        
        elif "kde" in desktop:
            # KDE stores settings in a plain text config file. We can parse it directly.
            config_path = os.path.expanduser("~/.config/plasma-org.kde.plasma.desktop-appletsrc")
            if not os.path.exists(config_path):
                return "Error: KDE config file not found."
            
            try:
                with open(config_path, "r") as f:
                    for line in f:
                        if line.startswith("Image="):
                            path = line.strip().split("=", 1)[1]
                            return path.replace("file://", "")
            except Exception as e:
                return f"Error reading KDE config: {e}"
            return "No active KDE wallpaper found in config."
        
        elif "cosmic" in desktop:
            # COSMIC stores its background config in a readable file.
            config_path = os.path.expanduser("~/.config/cosmic/com.system76.CosmicBackground/v1/all")
            if not os.path.exists(config_path):
                return "Error: COSMIC config file not found."
            
            try:
                with open(config_path, "r") as f:
                    for line in f:
                        if "source: Path(" in line:
                            # Extract path between quotes: "image_path": "/path/to/image"
                            parts = line.split('"')
                            if len(parts) >= 2:
                                return parts[1]
            except Exception as e:
                return f"Error reading COSMIC config: {e}"
            return "No active COSMIC wallpaper found in config."
        
        elif "hyprland" in desktop:
            # 1. Process Table Check (For command-line setters like swaybg and wbg)
            try:
                for pid in os.listdir('/proc'):
                    if pid.isdigit():
                        try:
                            with open(f"/proc/{pid}/cmdline", "rb") as f:
                                cmd = f.read().split(b'\x00')
                                cmd = [c.decode('utf-8', 'ignore') for c in cmd if c]
                                if not cmd: continue
                                
                                # Check for swaybg
                                if 'swaybg' in cmd[0] or 'swaybg' in cmd:
                                    if '-i' in cmd:
                                        return cmd[cmd.index('-i') + 1]
                                
                                # Check for wbg (syntax: wbg /path/to/image)
                                if 'wbg' in cmd[0] or 'wbg' in cmd:
                                    if len(cmd) > 1:
                                        return cmd[1]
                        except (IOError, PermissionError):
                            continue
            except Exception as e:
                pass # Silently fail and try the next method

            # 2. Config File Check (For hyprpaper)
            hyprpaper_config = os.path.expanduser("~/.config/hypr/hyprpaper.conf")
            if os.path.exists(hyprpaper_config):
                try:
                    with open(hyprpaper_config, "r") as f:
                        # Read from the bottom up in case multiple monitors are set
                        for line in reversed(f.readlines()):
                            line = line.strip()
                            # hyprpaper syntax: wallpaper = monitor,/path/to/image.png
                            if line.startswith("wallpaper"):
                                parts = line.split(",")
                                if len(parts) > 1:
                                    return parts[1].strip()
                except Exception:
                    pass

            # 3. Socket / API Check (For swww)
            # swww uses a live daemon socket, so we can't parse a config file. 
            # We must query it securely without shell=True.
            try:
                # Runs `swww query` which outputs: eDP-1: image: /path/to/wallpaper.jpg
                result = subprocess.run(
                    ["swww", "query"], 
                    capture_output=True, text=True, check=True
                )
                if "image:" in result.stdout:
                    # Extract the path following "image:"
                    return result.stdout.split("image:")[1].strip().split("\n")[0].strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            return "No known Hyprland wallpaper daemon (swaybg, wbg, hyprpaper, swww) is actively running."
        
        elif "xfce" in desktop:
            # XFCE uses XML for its configuration. We can parse it cleanly with xml.etree
            config_path = os.path.expanduser("~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml")
            if not os.path.exists(config_path):
                return "Error: XFCE desktop XML not found."
            
            try:
                tree = ET.parse(config_path)
                root = tree.getroot()
                
                # We want the property where name="last-image"
                # <property name="last-image" type="string" value="/path/to/wall.jpg"/>
                for prop in root.iter('property'):
                    if prop.get('name') == 'last-image':
                        return prop.get('value', '')
            except ET.ParseError:
                return "Error parsing XFCE XML file."
            except Exception as e:
                return f"Error reading XFCE config: {e}"
            
            return "No XFCE wallpaper found."
        
        else:
            return f"Unsupported Desktop Environment: {desktop}"
    
    else:
        return f"Unsupported OS: {system_name}"
