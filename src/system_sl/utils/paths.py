"""Module for handling cross-platform application data storage directories."""

import os
from pathlib import Path


def get_tasks_file_path(filename: str) -> str:
    """Resolves a cross-platform configuration file path based on the host operating system.

    Args:
        filename (str): The name of the file to resolve.

    Returns:
        str: The absolute path pointing to the file inside the system-sl data folder.
    """
    prog_name = 'system-sl'

    if os.name == "nt":
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        config_dir = base_dir / prog_name
    else:
        config_dir = Path.home() / ".config" / prog_name

    config_dir.mkdir(parents=True, exist_ok=True)
    return str(config_dir / filename)