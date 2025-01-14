from os import path
import os


def ensure_parent_folder_exists(filepath: str) -> None:
    view_dir = path.dirname(filepath)
    if not path.exists(view_dir):
        os.makedirs(view_dir)
