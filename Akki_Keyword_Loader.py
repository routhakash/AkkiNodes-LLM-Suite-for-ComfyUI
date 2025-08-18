# Node: Keyword Loader v1.0

import os
import re
import traceback
import folder_paths

class KeywordLoader_Akki:
    """
    A utility node that finds and loads the latest saved Keyword Bag file for a
    specific shot, designed to work within a looping production pipeline.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_path": ("STRING", {"forceInput": True}),
                "keyword_subfolder": ("STRING", {"default": "DATA"}),
                "shot_name": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("keyword_bag",)
    FUNCTION = "load_keyword_bag"
    CATEGORY = "AkkiNodes/FileIO"

    def load_keyword_bag(self, project_path, keyword_subfolder, shot_name):
        try:
            if not shot_name or shot_name.startswith("ERROR:"):
                return (f"ERROR: Invalid shot_name provided: {shot_name}",)

            # 1. Construct the full directory path from the project path
            base_dir = folder_paths.get_output_directory()
            full_project_dir = os.path.normpath(os.path.join(base_dir, project_path))
            data_dir = os.path.join(full_project_dir, keyword_subfolder)

            if not os.path.isdir(data_dir):
                return (f"ERROR: Keyword directory not found at: {data_dir}",)

            # 2. Create a regex pattern to find all versions of the file for this shot
            # Format: KEY_1A_0001_2025-07-21.txt
            pattern = re.compile(rf"^KEY_{re.escape(shot_name)}_\d+_\d{{4}}-\d{{2}}-\d{{2}}\.txt$")
            
            # 3. Find all matching files
            matching_files = [f for f in os.listdir(data_dir) if pattern.match(f)]

            if not matching_files:
                return (f"ERROR: No Keyword Bag file found for shot '{shot_name}' in {data_dir}",)
            
            # 4. Sort to find the latest file and load it
            # Reverse alphabetical sort works because the padding and date are at the end.
            latest_file = sorted(matching_files, reverse=True)[0]
            file_path = os.path.join(data_dir, latest_file)
            
            print(f"[Keyword Loader] Found latest file for Shot '{shot_name}': {latest_file}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                keyword_bag = f.read()

            return (keyword_bag,)

        except Exception as e:
            traceback.print_exc()
            return (f"ERROR: Failed to load Keyword Bag file. Check console. Details: {e}",)

NODE_CLASS_MAPPINGS = {"KeywordLoader-Akki": KeywordLoader_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"KeywordLoader-Akki": "Keyword Loader v1.0 - Akki"}