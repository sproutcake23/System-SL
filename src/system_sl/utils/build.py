import subprocess
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).parent.parent.parent.parent
    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--name", "system-sl",
            "--windowed",
            "--onefile",
            "--add-binary", "spellchecker/resources/en.json.gz:spellchecker/resources",
            "--add-data", "assets:assets",
            str(project_root / "src/system_sl/frontend/gui/main.py"),
        ],
        cwd=project_root,
        check=True,
    )
