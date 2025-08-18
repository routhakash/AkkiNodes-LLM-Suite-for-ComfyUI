# Node: Scene Choreography Loader v2.1

import os
import re
import traceback
import folder_paths

class SceneChoreographyLoader_Akki:
    """
    A utility node that finds and loads the latest choreography file for a specific
    scene number, driven by the Project Director node.
    v2.1 refactors the input to use a direct project_path.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # UPDATED: Replaced the manual text input with a direct path input.
                "project_path": ("STRING", {"forceInput": True}),
                "choreography_subfolder": ("STRING", {"default": "DATA"}),
                "scene_number": ("INT", {"default": 1, "min": 1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("choreography_text",)
    FUNCTION = "load_choreography"
    CATEGORY = "AkkiNodes/FileIO"

    def load_choreography(self, project_path, choreography_subfolder, scene_number):
        try:
            # The project_path is now an absolute path relative to the output directory.
            base_dir = folder_paths.get_output_directory()
            full_project_dir = os.path.normpath(os.path.join(base_dir, project_path))
            data_dir = os.path.join(full_project_dir, choreography_subfolder)

            if not os.path.isdir(data_dir):
                return (f"ERROR: Choreography directory not found at: {data_dir}",)

            scene_num_padded = f"{scene_number:03d}"
            pattern = re.compile(rf"^CHO_{scene_num_padded}_\d+_\d{{4}}-\d{{2}}-\d{{2}}\.txt$")
            
            matching_files = [f for f in os.listdir(data_dir) if pattern.match(f)]

            if not matching_files:
                return (f"ERROR: No choreography file found for Scene {scene_number} in {data_dir}",)
            
            latest_file = sorted(matching_files, reverse=True)[0]
            file_path = os.path.join(data_dir, latest_file)
            
            print(f"[SceneChoreographyLoader] Found latest file for Scene {scene_number}: {latest_file}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                choreography_text = f.read()

            return (choreography_text,)

        except Exception as e:
            traceback.print_exc()
            return (f"ERROR: Failed to load choreography file. Check console. Details: {e}",)

NODE_CLASS_MAPPINGS = {"SceneChoreographyLoader-Akki": SceneChoreographyLoader_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"SceneChoreographyLoader-Akki": "Scene Choreography Loader v2.1 - Akki"}