# Node: Generic Image Shot Loader v1.0

import os
import re
import traceback
import folder_paths
import torch
import numpy as np
from PIL import Image

class GenericImageLoader_Akki:
    """
    A generic utility node that finds and loads the latest version of any image
    associated with a specific shot, identified by a user-defined prefix.
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

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "load_generic_image"
    CATEGORY = "AkkiNodes/FileIO"

    def _load_image(self, filepath):
        """Loads an image file into a torch tensor."""
        if not filepath or not os.path.exists(filepath):
            print(f"[Generic Image Loader] Warning: Image file not found at path: {filepath}")
            # Return a blank tensor if the image doesn't exist
            return torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        
        img = Image.open(filepath)
        img = img.convert("RGB")
        img = np.array(img).astype(np.float32) / 255.0
        img = torch.from_numpy(img)[None,]
        return img

    def load_generic_image(self, project_path, image_subfolder, shot_name, filename_prefix):
        try:
            if not shot_name or shot_name.startswith("ERROR:"):
                raise ValueError(f"Invalid shot_name provided: {shot_name}")
            if not filename_prefix:
                raise ValueError("Filename Prefix cannot be empty.")

            # 1. Construct the full directory path from the project path
            base_dir = folder_paths.get_output_directory()
            full_project_dir = os.path.normpath(os.path.join(base_dir, project_path))
            data_dir = os.path.join(full_project_dir, image_subfolder)

            if not os.path.isdir(data_dir):
                raise FileNotFoundError(f"Image directory not found at: {data_dir}")

            # 2. Create a regex pattern to find all versions of the file
            # Format: <prefix>_<ShotName>_<date>_<padding>.png
            # Example: SFRough_1A_2025-07-24_00001_.png
            pattern = re.compile(rf"^{re.escape(filename_prefix)}_{re.escape(shot_name)}_\d{{4}}-\d{{2}}-\d{{2}}_\d+.*?\.png$")
            
            # 3. Find all matching files
            matching_files = [f for f in os.listdir(data_dir) if pattern.match(f)]

            if not matching_files:
                raise FileNotFoundError(f"No image file found for shot '{shot_name}' with prefix '{filename_prefix}' in {data_dir}")
            
            # 4. Sort to find the latest file and load it
            # Reverse alphabetical sort works because the date and padding number ensure sequential naming.
            latest_file = sorted(matching_files, reverse=True)[0]
            file_path = os.path.join(data_dir, latest_file)
            
            print(f"[Generic Image Loader] Found latest file for Shot '{shot_name}': {latest_file}")
            
            image = self._load_image(file_path)

            return (image,)

        except Exception as e:
            traceback.print_exc()
            print(f"ERROR: {e}")
            # Return a blank image on any error to prevent workflow from crashing
            return (torch.zeros(1, 64, 64, 3, dtype=torch.float32),)

NODE_CLASS_MAPPINGS = {"GenericImageLoader-Akki": GenericImageLoader_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"GenericImageLoader-Akki": "Generic Image Shot Loader v1.0 - Akki"}