# Node: Generic File I/O v1.0

import os
import re
import traceback
from datetime import datetime
import folder_paths

class GenericFileSaver_Akki:
    """
    A generic utility node to save any text input to a file with a standardized,
    shot-specific, zero-padded naming convention, and includes a passthrough.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_path": ("STRING", {"forceInput": True}),
                "text": ("STRING", {"forceInput": True}),
                "file_subfolder": ("STRING", {"default": "DATA"}),
                "shot_name": ("STRING", {"forceInput": True}),
                "filename_prefix": ("STRING", {"default": "GenericOutput"}),
                "extension": (["txt", "csv", "md", "json", "log"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("saved_file_path", "text_passthrough")
    FUNCTION = "save_generic_file"
    CATEGORY = "AkkiNodes/FileIO"
    OUTPUT_NODE = True

    def save_generic_file(self, project_path, text, file_subfolder, shot_name, filename_prefix, extension):
        try:
            base_dir = folder_paths.get_output_directory()
            full_save_dir = os.path.normpath(os.path.join(base_dir, project_path, file_subfolder))
            os.makedirs(full_save_dir, exist_ok=True)

            # Sanitize shot_name for filename
            clean_shot_name = re.sub(r'[<>:"/\\|?*]', '_', shot_name).strip()
            
            # Pattern to find existing files for numbering
            # Format: <prefix>_<shot_name>_<date>_<padding>.ext
            date_str = datetime.now().strftime("%Y-%m-%d")
            base_filename_part = f"{filename_prefix}_{clean_shot_name}_{date_str}"
            pattern = re.compile(rf"^{re.escape(base_filename_part)}_(\d+)\.{extension}$")
            
            existing_numbers = []
            for f in os.listdir(full_save_dir):
                match = pattern.match(f)
                if match:
                    existing_numbers.append(int(match.group(1)))
            
            next_number = max(existing_numbers) + 1 if existing_numbers else 1
            
            # Construct final filename with 4-digit zero-padding
            final_file_name = f"{base_filename_part}_{next_number:04d}.{extension}"
            final_file_path = os.path.join(full_save_dir, final_file_name)

            with open(final_file_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            print(f"[Generic File Saver] Successfully saved file to: {final_file_path}")
            
            return (final_file_path, text)

        except Exception as e:
            traceback.print_exc()
            return (f"ERROR: Could not save file. Check console. Details: {e}", text)


class GenericFileLoader_Akki:
    """
    A generic utility node that finds and loads the latest version of any text file
    associated with a specific shot, identified by a user-defined prefix.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_path": ("STRING", {"forceInput": True}),
                "file_subfolder": ("STRING", {"default": "DATA"}),
                "shot_name": ("STRING", {"forceInput": True}),
                "filename_prefix": ("STRING", {"default": "GenericOutput"}),
                "extension": (["txt", "csv", "md", "json", "log"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_content",)
    FUNCTION = "load_generic_file"
    CATEGORY = "AkkiNodes/FileIO"

    def load_generic_file(self, project_path, file_subfolder, shot_name, filename_prefix, extension):
        try:
            base_dir = folder_paths.get_output_directory()
            full_search_dir = os.path.normpath(os.path.join(base_dir, project_path, file_subfolder))

            if not os.path.isdir(full_search_dir):
                raise FileNotFoundError(f"Directory not found at: {full_search_dir}")

            # Sanitize shot_name for searching
            clean_shot_name = re.sub(r'[<>:"/\\|?*]', '_', shot_name).strip()

            # Pattern to find all versions of the file
            # Format: <prefix>_<shot_name>_<date>_<padding>.ext
            pattern = re.compile(rf"^{re.escape(filename_prefix)}_{re.escape(clean_shot_name)}_.*\.{extension}$")

            matching_files = [f for f in os.listdir(full_search_dir) if pattern.match(f)]

            if not matching_files:
                raise FileNotFoundError(f"No file found for shot '{shot_name}' with prefix '{filename_prefix}' in {full_search_dir}")

            # Reverse sort will bring the latest file (by date, then by number) to the top
            latest_file = sorted(matching_files, reverse=True)[0]
            file_path = os.path.join(full_search_dir, latest_file)

            print(f"[Generic File Loader] Found latest file for Shot '{shot_name}': {latest_file}")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return (content,)

        except Exception as e:
            traceback.print_exc()
            return (f"ERROR: Could not load file. Check console. Details: {e}",)


NODE_CLASS_MAPPINGS = {
    "GenericFileSaver-Akki": GenericFileSaver_Akki,
    "GenericFileLoader-Akki": GenericFileLoader_Akki
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GenericFileSaver-Akki": "Generic File Saver v1.0 - Akki",
    "GenericFileLoader-Akki": "Generic File Loader v1.0 - Akki"
}