#!/usr/bin/env python3
"""
Build AppImage for system-sl.

This script:
1. Builds a wheel with uv
2. Creates an AppDir structure
3. Installs the wheel into the AppDir
4. Copies assets and desktop file
5. Runs appimagetool to create the AppImage

Requirements:
- uv (for building wheel)
- appimagetool (for creating AppImage)
- Linux with FUSE support
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_cmd(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"🔧 Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=isinstance(cmd, str))
    if check and result.returncode != 0:
        print(f"❌ Command failed: {result.stderr}")
        sys.exit(result.returncode)
    if result.stdout:
        print(result.stdout)
    return result


def main():
    project_root = Path(__file__).parent.parent.parent
    version = "1.2.0"  # Should match pyproject.toml

    print("🚀 Building AppImage for system-sl...")

    # Step 1: Build wheel with uv
    print("\n📦 Building wheel with uv...")
    run_cmd(["uv", "build", "--wheel"], cwd=project_root)

    # Find the built wheel
    dist_dir = project_root / "dist"
    wheels = list(dist_dir.glob("system_sl-*.whl"))
    if not wheels:
        print("❌ No wheel found in dist/")
        sys.exit(1)
    wheel_path = wheels[0]
    print(f"✅ Found wheel: {wheel_path.name}")

    # Step 2: Create AppDir structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        appdir = tmpdir / "system-sl.AppDir"
        appdir.mkdir()

        usr_dir = appdir / "usr"
        usr_dir.mkdir()

        # Create standard directories
        (usr_dir / "bin").mkdir(parents=True, exist_ok=True)
        (usr_dir / "lib").mkdir(parents=True, exist_ok=True)
        (usr_dir / "share" / "applications").mkdir(parents=True, exist_ok=True)
        (usr_dir / "share" / "icons" / "hicolor" / "scalable" / "apps").mkdir(parents=True, exist_ok=True)
        (usr_dir / "share" / "system-sl").mkdir(parents=True, exist_ok=True)

        # Step 3: Install wheel into AppDir
        print("\n📥 Installing wheel into AppDir...")
        python_exe = shutil.which("python3") or shutil.which("python")
        run_cmd([
            python_exe, "-m", "pip", "install",
            "--prefix", str(usr_dir),
            "--no-deps",  # We'll install deps separately
            str(wheel_path)
        ])

        # Install dependencies
        print("\n📥 Installing dependencies...")
        run_cmd([
            python_exe, "-m", "pip", "install",
            "--prefix", str(usr_dir),
            "pyside6", "qtpy", "google-api-python-client",
            "google-auth-httplib2", "google-auth-oauthlib",
            "python-dotenv>=1.2.2", "langchain>=1.3.1",
            "langchain-core>=1.4.0", "langchain-google-genai>=4.2.3",
            "langsmith>=0.8.5", "numpy>=2.4.6", "openai>=2.38.0",
            "protobuf>=7.35.0", "spacy>=3.8.14",
            "en-core-web-md>=3.8.0", "click>=8.4.1",
            "pyspellchecker", "colorthief==0.2.1",
            "Pillow==12.3.0", "imagecodecs>=2025.3.30,<2026",
            "requests>=2.31.0"
        ])

        # Step 4: Copy assets
        print("\n📁 Copying assets...")
        assets_src = project_root / "src" / "system_sl" / "assets"
        assets_dst = usr_dir / "share" / "system-sl"

        # Copy sounds
        sounds_src = assets_src / "sounds"
        sounds_dst = assets_dst / "sounds"
        if sounds_src.exists():
            shutil.copytree(sounds_src, sounds_dst, dirs_exist_ok=True)
            print(f"✅ Copied sounds to {sounds_dst}")

        # Copy desktop file
        desktop_src = assets_src / "system-sl.desktop"
        desktop_dst = usr_dir / "share" / "applications" / "system-sl.desktop"
        if desktop_src.exists():
            shutil.copy2(desktop_src, desktop_dst)
            print(f"✅ Copied desktop file to {desktop_dst}")

        # Copy icon
        icon_src = assets_src / "system-sl.svg"
        icon_dst = usr_dir / "share" / "icons" / "hicolor" / "scalable" / "apps" / "system-sl.svg"
        if icon_src.exists():
            shutil.copy2(icon_src, icon_dst)
            print(f"✅ Copied icon to {icon_dst}")

        # Step 5: Create AppRun script
        print("\n📝 Creating AppRun script...")
        apprun = appdir / "AppRun"
        # Get Python version dynamically
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        apprun_content = f"""#!/bin/sh
# AppRun script for system-sl AppImage

# Set up environment
export PYTHONPATH="${{APPDIR}}/usr/lib/python{py_version}/site-packages:${{PYTHONPATH}}"
export PATH="${{APPDIR}}/usr/bin:${{PATH}}"
export LD_LIBRARY_PATH="${{APPDIR}}/usr/lib:${{LD_LIBRARY_PATH}}"

# Qt platform plugins
export QT_PLUGIN_PATH="${{APPDIR}}/usr/lib/python{py_version}/site-packages/PySide6/Qt/plugins:${{QT_PLUGIN_PATH}}"
export QML2_IMPORT_PATH="${{APPDIR}}/usr/lib/python{py_version}/site-packages/PySide6/Qt/qml:${{QML2_IMPORT_PATH}}"

# Ensure we can find the system-sl data
export SYSTEM_SL_DATA_DIR="${{APPDIR}}/usr/share/system-sl"

# Run the application
exec "${{APPDIR}}/usr/bin/system-sl" "$@"
"""
        apprun.write_text(apprun_content)
        apprun.chmod(0o755)

        # Step 6: Create desktop file in AppDir root (for appimagetool)
        shutil.copy2(desktop_dst, appdir / "system-sl.desktop")

        # Step 7: Copy icon to AppDir root
        shutil.copy2(icon_dst, appdir / "system-sl.svg")

        # Step 8: Download appimagetool if needed
        print("\n🔧 Checking for appimagetool...")
        appimagetool = shutil.which("appimagetool")
        if not appimagetool:
            print("📥 Downloading appimagetool...")
            appimagetool_path = Path(tmpdir) / "appimagetool"
            run_cmd([
                "wget", "-q", "-O", str(appimagetool_path),
                "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
            ])
            appimagetool_path.chmod(0o755)
            appimagetool = str(appimagetool_path)

        # Step 9: Build AppImage
        print("\n🏗️  Building AppImage...")
        output_name = f"system-sl-{version}-x86_64.AppImage"
        output_path = project_root / "dist" / output_name

        # Ensure dist directory exists
        (project_root / "dist").mkdir(exist_ok=True)

        # Run appimagetool
        env = os.environ.copy()
        env["VERSION"] = version
        run_cmd([appimagetool, str(appdir), str(output_path)], env=env)

        print(f"\n✅ AppImage created: {output_path}")
        print(f"📏 Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()