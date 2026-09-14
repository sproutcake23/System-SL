import json
import os
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path

import requests
from PySide6.QtCore import QThread, Signal


GITHUB_REPO = "sproutcake23/System-SL"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def get_current_version() -> str:
    """Read the installed version from package metadata."""
    try:
        from importlib.metadata import version
        return version("system-sl")
    except Exception:
        return "0.0.0"


def get_latest_release_info() -> dict:
    """Fetch the latest release info from GitHub."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    resp = requests.get(GITHUB_API_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def parse_version(tag: str) -> tuple:
    """Parse a version tag like 'v0.2.0' into a comparable tuple (0, 2, 0)."""
    tag = tag.lstrip("v").strip()
    parts = tag.split(".")
    return tuple(int(p) for p in parts)


def should_update(current: str, latest: str) -> bool:
    """Return True if `latest` version is newer than `current`."""
    try:
        return parse_version(latest) > parse_version(current)
    except (ValueError, IndexError):
        return False


def get_platform_asset(assets: list) -> dict | None:
    """Pick the correct release asset for the current OS."""
    is_windows = os.name == "nt"
    for asset in assets:
        name = asset["name"].lower()
        if is_windows and name.endswith(".zip"):
            return asset
        if not is_windows and name.endswith(".tar.xz"):
            return asset
    return None


def download_asset(url: str, dest_dir: Path) -> Path:
    """Stream-download a release asset to dest_dir. Returns the file path."""
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    filename = url.split("/")[-1]
    dest_file = dest_dir / filename
    with open(dest_file, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return dest_file


def extract_binary(archive_path: Path, dest_dir: Path) -> Path:
    """Extract the system-sl binary from a tar.xz or zip archive."""
    binary_name = "system-sl.exe" if os.name == "nt" else "system-sl"

    if archive_path.suffix == ".xz" or archive_path.name.endswith(".tar.xz"):
        with tarfile.open(archive_path, "r:xz") as tar:
            tar.extractall(path=dest_dir)
    elif archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(dest_dir)
    else:
        raise ValueError(f"Unsupported archive format: {archive_path.name}")

    for f in dest_dir.rglob(binary_name):
        if f.is_file():
            return f

    raise FileNotFoundError(f"Binary '{binary_name}' not found inside {archive_path.name}")


def install_update(new_binary: Path) -> None:
    """Copy the new binary and update the desktop shortcut."""
    binary_name = "system-sl" if os.name != "nt" else "system-sl.exe"

    if os.name != "nt":
        install_dir = Path.home() / ".local" / "bin"
        shortcut_dir = Path.home() / ".local" / "share" / "applications"
    else:
        install_dir = Path(os.environ["APPDATA"]) / "system-sl"
        shortcut_dir = Path(os.environ["USERPROFILE"]) / "Desktop"

    install_dir.mkdir(parents=True, exist_ok=True)
    target_path = install_dir / binary_name

    shutil.copy2(new_binary, target_path)
    if os.name != "nt":
        os.chmod(target_path, 0o755)

    if os.name != "nt":
        shortcut_file = shortcut_dir / "system-sl.desktop"
        work_dir = target_path.parent
        content = [
            "[Desktop Entry]",
            "Type=Application",
            "Name=THE SYSTEM",
            f"Exec={target_path}",
            f"Path={work_dir}",
            "Terminal=false",
            "Icon=utilities-terminal",
            "Categories=Utility;",
            "Comment=Arise, Player.",
        ]
        with open(shortcut_file, "w") as f:
            f.write("\n".join(content))
        os.chmod(shortcut_file, 0o755)
    else:
        shortcut_file = shortcut_dir / "THE SYSTEM.lnk"
        import subprocess
        ps_script = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_file}")
        $Shortcut.TargetPath = "{target_path}"
        $Shortcut.WorkingDirectory = "{install_dir}"
        $Shortcut.Save()
        """
        subprocess.run(
            ["powershell.exe", "-Command", ps_script], capture_output=True, shell=True
        )


def load_auto_update_preference() -> bool:
    """Read the auto-update setting from settings.json."""
    try:
        from system_sl.utils.paths import get_tasks_file_path
        settings_path = Path(get_tasks_file_path("settings.json"))
        if settings_path.exists():
            with open(settings_path) as f:
                data = json.load(f)
            return data.get("auto_update", False)
    except Exception:
        pass
    return False


def save_auto_update_preference(enabled: bool) -> None:
    """Persist the auto-update setting to settings.json."""
    from system_sl.utils.paths import get_tasks_file_path
    settings_path = Path(get_tasks_file_path("settings.json"))
    data = {}
    if settings_path.exists():
        with open(settings_path) as f:
            data = json.load(f)
    data["auto_update"] = enabled
    with open(settings_path, "w") as f:
        json.dump(data, f, indent=2)


def _load_last_check_time() -> float:
    """Read the last update check timestamp from settings.json."""
    try:
        settings_path = Path(get_tasks_file_path("settings.json"))
        if settings_path.exists():
            with open(settings_path) as f:
                data = json.load(f)
            return data.get("last_update_check", 0)
    except Exception:
        pass
    return 0


def _save_last_check_time() -> None:
    """Persist the current time as the last update check timestamp."""
    import time as _time
    from system_sl.utils.paths import get_tasks_file_path
    settings_path = Path(get_tasks_file_path("settings.json"))
    data = {}
    if settings_path.exists():
        with open(settings_path) as f:
            data = json.load(f)
    data["last_update_check"] = _time.time()
    with open(settings_path, "w") as f:
        json.dump(data, f, indent=2)


class UpdateCheckThread(QThread):
    """Background thread that checks, downloads, and installs updates."""

    update_found = Signal(str, str)
    update_complete = Signal(bool, str)
    progress = Signal(int)

    def run(self):
        try:
            import time as _time

            # Throttle: skip if checked within 24 hours
            if _time.time() - _load_last_check_time() < 86400:
                return

            current = get_current_version()
            _save_last_check_time()
            release = get_latest_release_info()
            latest_tag = release.get("tag_name", "")
            assets = release.get("assets", [])

            if not should_update(current, latest_tag):
                return

            self.update_found.emit(latest_tag, release.get("html_url", ""))

            asset = get_platform_asset(assets)
            if not asset:
                self.update_complete.emit(False, "No compatible release asset found.")
                return

            download_url = asset["browser_download_url"]
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                self.progress.emit(25)
                archive = download_asset(download_url, tmp_path)
                self.progress.emit(50)
                binary = extract_binary(archive, tmp_path)
                self.progress.emit(75)
                install_update(binary)
                self.progress.emit(100)

            self.update_complete.emit(True, f"Updated to {latest_tag}. Please restart the app.")

        except requests.exceptions.HTTPError as e:
            # Rate limit hit — fail silently, no popup
            if e.response is not None and e.response.status_code == 403:
                return
            self.update_complete.emit(False, f"Update failed: {e}")
        except Exception as e:
            self.update_complete.emit(False, f"Update failed: {e}")
