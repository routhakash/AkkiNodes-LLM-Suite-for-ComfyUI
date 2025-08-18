# Node: Akki File I/O v7.0 (Consolidated)

import os
import re
import folder_paths
from datetime import datetime
from server import PromptServer
import aiohttp.web

# --- NODE 1: Save Text File ---
class SaveTextFile_Akki:
    """
    Saves text to a file and includes a passthrough for the original text.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "directory": ("STRING", {"default": "AKKILLM/Project01"}),
                "filename_prefix": ("STRING", {"default": "output"}),
                "extension": (["txt", "csv", "md", "json"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("saved_file_path", "text_passthrough")
    FUNCTION = "save_text_file"
    CATEGORY = "AkkiNodes/FileIO"
    OUTPUT_NODE = True

    def save_text_file(self, text, directory, filename_prefix, extension):
        base_dir = folder_paths.get_output_directory()
        full_output_dir = os.path.normpath(os.path.join(base_dir, directory))
        os.makedirs(full_output_dir, exist_ok=True)

        try:
            pattern_str = f"^{re.escape(filename_prefix)}_(\\d+)_.*\\.{extension}$"
            pattern = re.compile(pattern_str)
            existing_numbers = [int(match.group(1)) for f in os.listdir(full_output_dir) if (match := pattern.match(f))]
            next_number = max(existing_numbers) + 1 if existing_numbers else 1
        except Exception as e:
            print(f"[Save Text - Akki] Warning: Could not parse existing files. Using fallback. Error: {e}")
            next_number = int(datetime.now().timestamp())

        date_str = datetime.now().strftime("%Y-%m-%d")
        final_file_name = f"{filename_prefix}_{next_number:04d}_{date_str}.{extension}"
        final_file_path = os.path.join(full_output_dir, final_file_name)

        try:
            with open(final_file_path, "w", encoding="utf-8") as f: f.write(text)
        except Exception as e:
            return (f"ERROR: Could not save file. Check console. Details: {e}", "")
        return (final_file_path, text)


# --- NODE 2: Load Text File (Simple) ---
class LoadTextFileSimple_Akki:
    """
    Loads a text file by providing a direct path relative to the ComfyUI output directory.
    This is the simple, stable, direct-path loader.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {
                    "multiline": True,
                    "default": "AKKILLM/Project01/filename.txt"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_content",)
    FUNCTION = "execute"
    CATEGORY = "AkkiNodes/FileIO"

    def execute(self, file_path):
        if not file_path or not file_path.strip():
            return ("",)

        base_dir = folder_paths.get_output_directory()
        full_path = os.path.normpath(os.path.join(base_dir, file_path))

        if not os.path.exists(full_path):
            return (f"ERROR: File not found at the specified path: {full_path}",)
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return (f.read(),)
        except Exception as e:
            return (f"ERROR: Could not read file. Details: {e}",)


# --- NODE 3: Load Text File (Advanced) ---
class LoadTextFileAdvanced_Akki:
    """
    An advanced file loader with a dynamic UI controlled by the accompanying JS file.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": "AKKILLM/Project01"}),
                "extension_filter": (["txt", "csv", "md", "json", "log"],),
            },
            "optional": { "file": ([],) }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_content",)
    FUNCTION = "execute"
    CATEGORY = "AkkiNodes/FileIO"

    def execute(self, directory, extension_filter, file=None):
        if not file or file in ["No files found", "Directory not found"]:
            return ("",)

        base_dir = folder_paths.get_output_directory()
        full_dir_path = os.path.normpath(os.path.join(base_dir, directory))
        full_file_path = os.path.join(full_dir_path, file)
        
        if not os.path.exists(full_file_path):
            return (f"ERROR: File does not exist at '{full_file_path}'",)
            
        try:
            with open(full_file_path, 'r', encoding='utf-8') as f:
                return (f.read(),)
        except Exception as e:
            return (f"ERROR: Could not read file. Details: {e}",)


# --- API Endpoint for the Advanced Loader ---
@PromptServer.instance.routes.get("/akkinodes/get_project_files")
async def get_project_files(request):
    directory = request.query.get("directory")
    ext = request.query.get("ext", "txt")
    if not directory: return aiohttp.web.json_response([])
    try:
        base_dir = folder_paths.get_output_directory()
        search_path = os.path.normpath(os.path.join(base_dir, directory))
        if not os.path.isdir(search_path): return aiohttp.web.json_response([])
        found_files = []
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith(f".{ext}"):
                    relative_path = os.path.relpath(os.path.join(root, file), search_path)
                    found_files.append(relative_path.replace('\\', '/'))
        return aiohttp.web.json_response(sorted(found_files))
    except Exception: return aiohttp.web.json_response([])


# --- Master Mappings for All Nodes in This File ---
NODE_CLASS_MAPPINGS = {
    "SaveTextFile-Akki": SaveTextFile_Akki,
    "LoadTextFileSimple-Akki": LoadTextFileSimple_Akki,
    "LoadTextFileAdvanced-Akki": LoadTextFileAdvanced_Akki
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveTextFile-Akki": "Save Text File v7.0 - Akki",
    "LoadTextFileSimple-Akki": "Load Text File (Simple) v7.0 - Akki",
    "LoadTextFileAdvanced-Akki": "Load Text File (Advanced) v7.0 - Akki"
}