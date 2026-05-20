"""Module for handling cross-platform application data storage directories."""

import os


def get_tasks_file_path(filename: str) -> str:
    """Resolves a cross-platform configuration file path based on the host operating system.

    Args:
        filename (str): The name of the file to resolve.

    Returns:
        str: The absolute path pointing to the file inside the system-sl data folder.
    """
    prog_name = 'system-sl'

    if os.name == 'nt':
        base_dir = os.environ.get('APPDATA', os.path.expanduser("~\\AppData\\Roaming"))
        config_dir = os.path.join(base_dir, prog_name)
    else:
        config_dir = os.path.join(os.path.expanduser("~"), ".config", prog_name)

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    return os.path.join(config_dir, filename)