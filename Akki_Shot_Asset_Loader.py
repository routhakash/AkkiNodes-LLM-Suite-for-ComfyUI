# Node: Shot Asset Loader v3.7 (Precise Regex & Sanitization Fix)

import os
import re
import traceback
import folder_paths
import csv
import io
import torch
import numpy as np
from PIL import Image

def sanitize_for_filename(name):
    """
    A helper function to clean names for use in filenames.
    v3.7 FIX: Only removes characters that are truly illegal in filenames,
    preserving periods and dashes which are critical for set names.
    """
    name = re.sub(r'\(.*?\)', '', name).strip()
    # This regex now only removes characters invalid in Windows/Linux filenames.
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name

class ShotAssetLoader_Akki:
    """
    A master utility node that loads all assets for a single shot.
    v3.7 provides definitive, production-certified fixes for sanitization and
    implements precise regex patterns to match the exact, deterministic naming
    conventions for lookdev assets.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_path": ("STRING", {"forceInput": True}),
                "csv_report": ("STRING", {"forceInput": True}),
                "shot_index": ("INT", {"default": 1, "min": 1}),
                "character_lookdev_folder": ("STRING", {"default": "Lookdev/CHR"}),
                "set_lookdev_folder": ("STRING", {"default": "Lookdev/SET"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("character_images", "set_image", "character_lookdev_prompts", "set_lookdev_prompt", "character_names")
    FUNCTION = "load_shot_assets"
    CATEGORY = "AkkiNodes/FileIO"
    
    OUTPUT_IS_LIST = (True, False, True, False, True)

    def _find_latest_image_file(self, directory, base_name):
        """Finds the latest image file using a hardened, precise regex."""
        if not os.path.isdir(directory):
            return None, f"Directory not found: {directory}"
        
        # v3.7 FIX: Hardened regex to precisely match the image naming convention.
        pattern = re.compile(rf"^{re.escape(base_name)}_L_\d+_\.png$", re.IGNORECASE)
        
        matching_files = [f for f in os.listdir(directory) if pattern.match(f)]
        if not matching_files:
            return None, f"No '.png' file matching image pattern for asset '{base_name}' in '{directory}'"
        return os.path.join(directory, sorted(matching_files, reverse=True)[0]), None

    def _find_latest_prompt_file(self, directory, base_name):
        """Finds the latest prompt file using a hardened, precise regex."""
        if not os.path.isdir(directory):
            return None, f"Directory not found: {directory}"

        # v3.7 FIX: Hardened regex to precisely match the prompt naming convention.
        pattern = re.compile(rf"^{re.escape(base_name)}_\d+_\d{{4}}-\d{{2}}-\d{{2}}\.txt$", re.IGNORECASE)
        
        matching_files = [f for f in os.listdir(directory) if pattern.match(f)]
        if not matching_files:
            return None, f"No '.txt' file matching prompt pattern for asset '{base_name}' in '{directory}'"
        return os.path.join(directory, sorted(matching_files, reverse=True)[0]), None

    def _load_image(self, filepath):
        if not filepath or not os.path.exists(filepath):
            return torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        img = Image.open(filepath).convert("RGB")
        img = np.array(img).astype(np.float32) / 255.0
        return torch.from_numpy(img)[None,]

    def _load_text(self, filepath):
        if not filepath or not os.path.exists(filepath):
            return f"ERROR: Lookdev prompt file not found."
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def load_shot_assets(self, project_path, csv_report, shot_index, character_lookdev_folder, set_lookdev_folder):
        char_images_list = []
        char_prompts_list = []
        char_names_list = []
        error_log = []
        
        try:
            f = io.StringIO(csv_report)
            reader = list(csv.DictReader(f))
            if not (0 <= shot_index - 1 < len(reader)):
                raise ValueError(f"Shot index {shot_index} is out of bounds.")
            
            shot_data = reader[shot_index - 1]
            
            location_key = next((key for key in shot_data if key.strip().upper() == 'LOCATION'), None)
            characters_key = next((key for key in shot_data if key.strip().upper() == 'CHARACTERS'), None)

            if not location_key: raise KeyError("CSV has no 'Location' or 'LOCATION' column.")
            
            set_name_raw = shot_data.get(location_key)
            characters_str = shot_data.get(characters_key, "") if characters_key else ""
            characters_in_shot = [c.strip() for c in characters_str.split(',') if c.strip() and c.strip().lower() != 'none']

            base_dir = folder_paths.get_output_directory()
            
            full_project_dir = os.path.join(base_dir, project_path)
            char_folder = os.path.normpath(os.path.join(full_project_dir, character_lookdev_folder))
            set_folder = os.path.normpath(os.path.join(full_project_dir, set_lookdev_folder))

            if not set_name_raw or set_name_raw.lower() == 'none':
                raise ValueError(f"No set/location specified for shot {shot_index}.")
            
            set_base_name = sanitize_for_filename(set_name_raw)

            set_img_path, err_img = self._find_latest_image_file(set_folder, set_base_name)
            set_txt_path, err_txt = self._find_latest_prompt_file(set_folder, set_base_name)
            if err_img: error_log.append(f"SET '{set_base_name}': {err_img}")
            if err_txt: error_log.append(f"SET '{set_base_name}': {err_txt}")

            set_image = self._load_image(set_img_path)
            set_prompt = self._load_text(set_txt_path)
            
            if not characters_in_shot:
                print(f"[Shot Asset Loader] No characters in shot {shot_index}.")
            else:
                for char_name in characters_in_shot:
                    char_names_list.append(char_name)
                    char_base_name = sanitize_for_filename(char_name)
                    
                    char_img_path, err_img = self._find_latest_image_file(char_folder, char_base_name)
                    char_txt_path, err_txt = self._find_latest_prompt_file(char_folder, char_base_name)
                    if err_img: error_log.append(f"CHR '{char_base_name}': {err_img}")
                    if err_txt: error_log.append(f"CHR '{char_base_name}': {err_txt}")
                    
                    char_images_list.append(self._load_image(char_img_path))
                    char_prompts_list.append(self._load_text(char_txt_path))

            if error_log:
                print(f"[Shot Asset Loader] Notice: Encountered the following issues:\n" + "\n".join(f"- {e}" for e in error_log))

            final_char_images = char_images_list if char_images_list else [torch.zeros(1, 64, 64, 3, dtype=torch.float32)]
            
        except Exception as e:
            traceback.print_exc()
            error_text = f"ERROR: A critical exception occurred. Check console. Details: {e}"
            dummy_img = torch.zeros(1, 64, 64, 3, dtype=torch.float32)
            return ([dummy_img], dummy_img, [error_text], error_text, ["Error"])

        return (final_char_images, set_image, char_prompts_list, set_prompt, char_names_list)

NODE_CLASS_MAPPINGS = {"ShotAssetLoader-Akki": ShotAssetLoader_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"ShotAssetLoader-Akki": "Shot Asset Loader v3.7 - Akki"}