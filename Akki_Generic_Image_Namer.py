# Node: Generic Image File Namer v1.0

import os
import re
from datetime import datetime
import folder_paths

class GenericImageNamer_Akki:
    """
    A utility node that constructs a ComfyUI-compatible filename prefix for saving
    shot-specific images. It combines project, shot, and prefix information into a
    standardized path.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_path": ("STRING", {"forceInput": True}),
                "image_subfolder": ("STRING", {"default": "Shots"}),
                "shot_name": ("STRING", {"forceInput": True}),
                "filename_prefix": ("STRING", {"default": "FinalRender"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename_prefix_out",)
    FUNCTION = "generate_name"
    CATEGORY = "AkkiNodes/FileIO"

    def generate_name(self, project_path, image_subfolder, shot_name, filename_prefix):
        try:
            if not shot_name or shot_name.startswith("ERROR:"):
                raise ValueError(f"Invalid shot_name provided: {shot_name}")
            if not filename_prefix:
                raise ValueError("Filename Prefix cannot be empty.")

            # 1. Construct the full directory path
            # The project_path from the Project Director is already relative to the 'output' folder
            full_directory_path = os.path.join(project_path, image_subfolder)

            # 2. Get the current date for versioning
            date_str = datetime.now().strftime("%Y-%m-%d")

            # 3. Sanitize shot_name to remove any characters invalid for filenames
            clean_shot_name = re.sub(r'[<>:"/\\|?*]', '_', shot_name).strip()

            # 4. Construct the filename prefix part
            # Example: FinalRender_1A_2025-07-24
            file_prefix_part = f"{filename_prefix}_{clean_shot_name}_{date_str}"

            # 5. Join the directory path and the filename prefix
            # Example: AKKILLM\Project01\Shots\FinalRender_1A_2025-07-24
            final_output_prefix = os.path.join(full_directory_path, file_prefix_part)
            
            print(f"[Generic Image Namer] Generated Prefix: {final_output_prefix}")

            return (final_output_prefix,)

        except Exception as e:
            print(f"ERROR in Generic Image Namer: {e}")
            return ("ERROR_CHECK_CONSOLE",)


NODE_CLASS_MAPPINGS = {"GenericImageNamer-Akki": GenericImageNamer_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"GenericImageNamer-Akki": "Generic Image File Namer v1.0 - Akki"}