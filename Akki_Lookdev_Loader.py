# --- START OF FILE Akki_Lookdev_Loader.py ---

# Node: Lookdev Bible Loader v3.6 (Robust Search & Disambiguation)

import os
import re
import traceback
import folder_paths
from collections import defaultdict

class LookdevBibleLoader_Akki:
    """
    A definitive node to scan a project's lookdev directories and load assets.
    v3.6 provides a critical logic fix to the single asset selector, implementing
    a robust, multi-tiered search with logical tie-breakers to correctly
    handle ambiguous partial matches and better reflect user intent.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_path": ("STRING", {"forceInput": True}),
                "character_subfolder": ("STRING", {"default": "Lookdev/CHR"}),
                "set_subfolder": ("STRING", {"default": "Lookdev/SET"}),
            },
            "optional": {
                "selected_name": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("set_names_LIST", "set_prompts_LIST", "character_names_LIST", "character_prompts_LIST", 
                    "set_names_STRING", "set_prompts_STRING", "character_names_STRING", "character_prompts_STRING",
                    "selected_name_out", "selected_prompt_out")
    FUNCTION = "load_lookdev_bible"
    CATEGORY = "AkkiNodes/FileIO"
    
    OUTPUT_IS_LIST = (True, True, True, True, False, False, False, False, False, False)

    def _find_and_load_latest_bible(self, directory_path):
        if not os.path.isdir(directory_path):
            print(f"[Lookdev Loader] Warning: Directory not found: {directory_path}")
            return [], []
        names_list, prompts_list = [], []
        try:
            file_groups = defaultdict(list)
            pattern = re.compile(r"(.+?)_\d+.*\.txt$", re.IGNORECASE)
            for filename in os.listdir(directory_path):
                if filename.endswith(".txt"):
                    match = pattern.match(filename)
                    if match:
                        file_groups[match.group(1).strip().lower()].append(filename)
            
            for base_name_norm in sorted(file_groups.keys()):
                latest_file = sorted(file_groups[base_name_norm], reverse=True)[0]
                latest_file_path = os.path.join(directory_path, latest_file)
                with open(latest_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                original_name = pattern.match(latest_file).group(1).strip()
                names_list.append(original_name)
                prompts_list.append(content)
        except Exception as e:
            traceback.print_exc()
            return [f"ERROR: Failed to load files from {directory_path}"], [str(e)]
        return names_list, prompts_list

    # REVISED FUNCTION v3.6: Implements robust, multi-tiered search
    def _find_and_load_single_asset(self, search_dirs, target_name):
        if not target_name or not target_name.strip():
            return "N/A", "No name provided."

        target_name_norm = target_name.strip().lower()
        
        # 1. Scan and categorize all available assets
        all_assets = []
        for directory in search_dirs:
            if not os.path.isdir(directory): continue
            for filename in os.listdir(directory):
                if filename.endswith(".txt"):
                    base_name_match = re.match(r"(.+?)_\d+.*\.txt$", filename, re.IGNORECASE)
                    if base_name_match:
                        asset_name = base_name_match.group(1).strip()
                        all_assets.append({'name': asset_name, 'path': os.path.join(directory, filename)})
        
        # 2. Multi-tiered search logic
        exact_matches = [asset for asset in all_assets if asset['name'].lower() == target_name_norm]
        starts_with_matches = [asset for asset in all_assets if asset['name'].lower().startswith(target_name_norm)]
        contains_matches = [asset for asset in all_assets if target_name_norm in asset['name'].lower()]

        best_match_pool = []
        if exact_matches:
            best_match_pool = exact_matches
        elif starts_with_matches:
            best_match_pool = starts_with_matches
        elif contains_matches:
            best_match_pool = contains_matches
        else:
            return target_name, f"ERROR: No lookdev file found matching '{target_name}'."

        # 3. Logical Tie-Breaker: Find the latest version of the most specific match (shortest name)
        best_match_pool.sort(key=lambda x: (len(x['name']), x['path']), reverse=False)
        best_asset_name = best_match_pool[0]['name']
        
        # Find the absolute latest version of that specific asset
        final_candidates = [asset for asset in best_match_pool if asset['name'].lower() == best_asset_name.lower()]
        final_candidates.sort(key=lambda x: x['path'], reverse=True)
        best_match = final_candidates[0]

        # 4. On-Demand Loading
        try:
            with open(best_match['path'], 'r', encoding='utf-8') as f:
                content = f.read()
            return best_match['name'], content
        except Exception as e:
            traceback.print_exc()
            return best_match['name'], f"ERROR: Could not read file. Details: {e}"

    def load_lookdev_bible(self, project_path, character_subfolder, set_subfolder, selected_name=None):
        base_dir = folder_paths.get_output_directory()
        full_project_dir = os.path.normpath(os.path.join(base_dir, project_path))
        char_dir_path = os.path.normpath(os.path.join(full_project_dir, character_subfolder))
        set_dir_path = os.path.normpath(os.path.join(full_project_dir, set_subfolder))

        set_names, set_prompts = self._find_and_load_latest_bible(set_dir_path)
        character_names, character_prompts = self._find_and_load_latest_bible(char_dir_path)

        delimiter = "|||---|||"
        set_names_str = delimiter.join(set_names if set_names and "ERROR" not in set_names[0] else [])
        set_prompts_str = delimiter.join(set_prompts if set_prompts and "ERROR" not in set_prompts[0] else [])
        character_names_str = delimiter.join(character_names if character_names and "ERROR" not in character_names[0] else [])
        character_prompts_str = delimiter.join(character_prompts if character_prompts and "ERROR" not in character_prompts[0] else [])
        
        selected_name_out, selected_prompt_out = self._find_and_load_single_asset(
            [char_dir_path, set_dir_path], selected_name
        )

        return (set_names, set_prompts, character_names, character_prompts, 
                set_names_str, set_prompts_str, character_names_str, character_prompts_str,
                selected_name_out, selected_prompt_out)

NODE_CLASS_MAPPINGS = {"LookdevBibleLoader-Akki": LookdevBibleLoader_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"LookdevBibleLoader-Akki": "Lookdev Bible Loader v3.6 - Akki"}

# --- END OF FILE Akki_Lookdev_Loader.py ---