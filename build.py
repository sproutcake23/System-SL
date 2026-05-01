import PyInstaller.__main__
import os


def run_build():
    entry_point = os.path.join("src", "cli", "main.py")

    PyInstaller.__main__.run(
        [
            entry_point,
            "--name=system-sl",
            "--onefile",
            "--console",
            "--noconfirm",
            "--clean",
            "--paths=src",
        ]
    )


if __name__ == "__main__":
    run_build()
