import subprocess
import sys
from pathlib import Path


def build_pyinstaller():
    """Build the PyInstaller binary."""
    project_root = Path(__file__).parent.parent.parent.parent
    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--name", "system-sl",
            "--windowed",
            "--noconsole",
            "--onefile",
            "--add-binary", "spellchecker/resources/en.json.gz:spellchecker/resources",
            "--add-data", "assets:assets",
            "--collect-all", "en_core_web_md",
            str(project_root / "src/system_sl/frontend/gui/main.py"),
        ],
        cwd=project_root,
        check=True,
    )
    return project_root


def build_appimage(project_root: Path):
    """Build AppImage for Linux."""
    print("Building AppImage...")
    subprocess.run(
        [sys.executable, "-m", "appimage", "build"],
        cwd=project_root,
        check=True,
    )
    print("AppImage built successfully!")


def build_msix(project_root: Path):
    """Build MSIX package for Windows."""
    if sys.platform != "win32":
        print("MSIX builds are only supported on Windows.")
        return

    print("Building MSIX package...")
    build_script = project_root / "packaging" / "windows" / "build_msix.ps1"
    if not build_script.exists():
        print(f"Build script not found: {build_script}")
        return

    subprocess.run(
        ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(build_script)],
        cwd=project_root,
        check=True,
    )
    print("MSIX package built successfully!")


def main():
    """Main build entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Build system-sl packages")
    parser.add_argument(
        "--format",
        choices=["binary", "appimage", "msix", "all"],
        default="binary",
        help="Package format to build (default: binary)"
    )
    args = parser.parse_args()

    project_root = build_pyinstaller()

    if args.format in ("appimage", "all"):
        if sys.platform == "linux":
            build_appimage(project_root)
        else:
            print("AppImage builds are only supported on Linux.")

    if args.format in ("msix", "all"):
        if sys.platform == "win32":
            build_msix(project_root)
        else:
            print("MSIX builds are only supported on Windows.")


if __name__ == "__main__":
    main()
