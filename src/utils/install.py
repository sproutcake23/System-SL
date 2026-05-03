import os
import sys
import shutil
import subprocess
from pathlib import Path


def install_the_system():
    script_dir = Path(__file__).parent.absolute()
    binary_name = "system-sl" if os.name != "nt" else "system-sl.exe"
    source_path = script_dir / binary_name

    if not source_path.exists():
        print(f"❌ Error: {binary_name} not found in {script_dir}!")
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
            "Terminal=true",
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
