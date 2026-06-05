import os
import subprocess
import sys
import shutil
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


def migrate_credentials():
    """
    Scans for credentials.json in common locations (Installer folder & Downloads)
    and moves it to the persistent system data directory.
    """
    # 1. Define Potential Sources
    script_dir = Path(__file__).parent.absolute()
    downloads_dir = Path.home() / "Downloads"

    potential_sources = [
        script_dir / "credentials.json",  # Current folder
        downloads_dir / "credentials.json",  # System Downloads folder
    ]

    # 2. Define Destination
    try:
        from system_sl.core.tasks import get_tasks_file_path

        target_path = Path(get_tasks_file_path("credentials.json"))
    except ImportError:
        print("⚠️  Warning: Could not import core.tasks. Migration skipped.")
        return

    # 3. Search and Move
    found_source = None
    for src in potential_sources:
        if src.exists():
            found_source = src
            break

    if found_source:
        print(f"Found Google credentials at: {found_source}")
        print(f"Migrating to: {target_path.parent}...")
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(found_source, target_path)
            print("✅ Credentials migrated successfully.")
        except Exception as e:
            print(f"❌ Error migrating credentials: {e}")
    else:
        print(
            "ℹ️  credentials.json not found in Downloads or current folder. Skipping migration."
        )


def install_sounds(source_sounds_dir: Path):
    """
    Takes the exact folder path where the sounds are currently located,
    and copies them to the system config folder.
    """
    if not source_sounds_dir.exists():
        print(f"ℹ️  No sounds found at {source_sounds_dir}. Skipping.")
        return

    # Try to use your existing path logic
    try:
        from system_sl.core.tasks import get_tasks_file_path

        target_sounds_dir = Path(get_tasks_file_path("sounds"))
    except ImportError:
        # Failsafe just in case the import breaks during install
        target_sounds_dir = Path.home() / ".config" / "system-sl" / "sounds"

    print(f"🎵 Installing notification sounds to {target_sounds_dir}...")

    try:
        target_sounds_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for audio_file in source_sounds_dir.glob("*"):
            if audio_file.is_file():
                shutil.copy2(audio_file, target_sounds_dir)
                count += 1
        print(f"✅ {count} sound(s) installed successfully.")
    except Exception as e:
        print(f"❌ Error installing sounds: {e}")


def install_the_system():
    project_root = Path(__file__).parent.parent.parent.parent.absolute()
    binary_name = "system-sl" if os.name != "nt" else "system-sl.exe"

    source_path = project_root / "dist" / binary_name
    sounds_folder = project_root / "assets" / "sounds"

    if not source_path.exists():
        print(f"❌ Error: {binary_name} not found in {source_path.parent}!")
        print("Did you remember to run PyInstaller first?")
        return

    if os.name != "nt":
        install_dir = Path.home() / ".local" / "bin"
        shortcut_dir = Path.home() / ".local" / "share" / "applications"
    else:
        install_dir = Path(os.environ["APPDATA"]) / "system-sl"
        shortcut_dir = Path(os.environ["USERPROFILE"]) / "Desktop"

    install_dir.mkdir(parents=True, exist_ok=True)
    target_path = install_dir / binary_name

    print(f"🚚 Moving binary to {target_path}...")
    shutil.copy2(source_path, target_path)

    if os.name != "nt":
        os.chmod(target_path, 0o755)

    migrate_credentials()
    install_sounds(sounds_folder)

    print("⚔️  Forging the shortcut...")

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

    print("\n✅ INSTALLATION COMPLETE")
    print("You can now delete the original folder. 'THE SYSTEM' shortcut is installed")


if __name__ == "__main__":
    install_the_system()
