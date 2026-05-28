"""Module for raw JSON serialization and deserialization file operations."""

import os
import json


def load_data(filepath: str) -> dict:
    """Reads and parses raw dictionary contents from a specified target JSON file.

    Args:
        filepath (str): The absolute path of the file to load.

    Returns:
        dict: The parsed data dictionary from the JSON file. Returns an empty dictionary if loading fails or file is empty.
    """
    if not os.path.exists(filepath):
        print(f"File {os.path.basename(filepath)} not found. Creating it.")
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("{}")
            return {}
        except Exception as e:
            print(f"Could not create file {filepath}: {e}")
            return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = f.read().strip()

            if not data:
                return {}

            return json.loads(data)
    except Exception as e:
        print(f"Error loading data {e}")
        return {}


def save_data(filepath: str, data: dict) -> None:
    """Serializes and saves a dictionary structure directly into a target JSON file.

    Args:
        filepath (str): The destination path where the data should be saved.
        data (dict): The data dictionary to serialize and write.

    Returns:
        None
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Could not save data to the file {filepath}: {e}")