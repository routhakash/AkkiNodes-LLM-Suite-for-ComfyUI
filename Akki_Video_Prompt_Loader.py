# Node: Video Prompt Loader v1.0

import os
import re
import traceback
import folder_paths

class VideoPromptLoader_Akki:
    """
    A utility node that finds and loads the latest saved Video Prompt file for a
    specific shot, designed to work within a looping video production pipeline.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_path": ("STRING", {"forceInput": True}),
                "video_prompt_subfolder": ("STRING", {"default": "DATA"}),
                "shot_name": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_prompt",)
    FUNCTION = "load_video_prompt"
    CATEGORY = "AkkiNodes/FileIO"

    def load_video_prompt(self, project_path, video_prompt_subfolder, shot_name):
        try:
            if not shot_name or shot_name.startswith("ERROR:"):
                return (f"ERROR: Invalid shot_name provided: {shot_name}",)

            # 1. Construct the full directory path from the project path
            base_dir = folder_paths.get_output_directory()
            full_project_dir = os.path.normpath(os.path.join(base_dir, project_path))
            data_dir = os.path.join(full_project_dir, video_prompt_subfolder)

            if not os.path.isdir(data_dir):
                return (f"ERROR: Video Prompt directory not found at: {data_dir}",)

            # 2. Create a regex pattern to find all versions of the file for this shot
            # Format: VPrompt_7B_0005_2025-07-24.txt
            pattern = re.compile(rf"^VPrompt_{re.escape(shot_name)}_\d+_\d{{4}}-\d{{2}}-\d{{2}}\.txt$")
            
            # 3. Find all matching files
            matching_files = [f for f in os.listdir(data_dir) if pattern.match(f)]

            if not matching_files:
                return (f"ERROR: No Video Prompt file found for shot '{shot_name}' in {data_dir}",)
            
            # 4. Sort to find the latest file and load it
            latest_file = sorted(matching_files, reverse=True)[0]
            file_path = os.path.join(data_dir, latest_file)
            
            print(f"[Video Prompt Loader] Found latest file for Shot '{shot_name}': {latest_file}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                video_prompt = f.read()

            return (video_prompt,)

        except Exception as e:
            traceback.print_exc()
            return (f"ERROR: Failed to load Video Prompt file. Check console. Details: {e}",)

NODE_CLASS_MAPPINGS = {"VideoPromptLoader-Akki": VideoPromptLoader_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"VideoPromptLoader-Akki": "Video Prompt Loader v1.0 - Akki"}