# __init__.py for AkkiNodes v13.2.0

# This file makes the 'AkkiNodes' folder a Python package and tells ComfyUI
# where to find the custom node definitions.

# It dynamically discovers and merges mappings from all separate node files.
# This makes the project more stable and easier to maintain.

import importlib
import os

# List of your node modules (the .py files)
node_files = [
    "Akki_LLM_Loader",
    "Akki_LLM_Executor",
    "Akki_LLM_Structured_Prompter",
    "Akki_Image_Prompt_Generator",
    "Akki_Story_Writer",
    "Akki_ScriptCrafter_P1",
    "Akki_ScriptCrafter_P2",
    "Akki_ScriptCrafter_P3",
]

# --- Master Dictionaries ---
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# --- Dynamic Import and Merging ---
for module_name in node_files:
    try:
        module = importlib.import_module(f".{module_name}", __name__)
        if hasattr(module, "NODE_CLASS_MAPPINGS"):
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
        if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
    except ImportError as e:
        print(f"[AkkiNodes] Error importing module {module_name}: {e}")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']