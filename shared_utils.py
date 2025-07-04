# shared_utils.py for AkkiNodes

import os

def get_wildcard_list(filename):
    """
    Reads a .txt file from the current node's directory and returns a list of its lines.
    """
    try:
        # __file__ is the path to the current python file.
        file_path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    return lines
    except Exception as e:
        print(f"[AkkiNodes] Warning: Could not read wildcard file {filename}. Error: {e}")
    
    return [f"Could not load {filename}"]