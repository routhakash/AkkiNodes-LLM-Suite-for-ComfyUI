# --- START OF FILE Akki_Shot_Selector.py ---

# Node: Shot Selector v3.6 (Definitive)

import csv
import io
import traceback
import re
import json
from collections import defaultdict

class ShotSelector_Akki:
    """
    Parses a CSV shot report. v3.6 is the definitive "Data Provider" version.
    It provides a clear, prefixed distinction between shot-specific (SEL_) and
    global outputs. It is fully backwards-compatible in functionality, provides
    an enriched JSON, and represents empty fields with clean, blank values.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "csv_report": ("STRING", {"forceInput": True}),
                "shot_index": ("INT", {"default": 1, "min": 1, "step": 1}),
            }
        }
    
    # --- DEFINITIVE v3.6 OUTPUT SIGNATURE: Prefixed, Reordered, and Backwards-Compatible ---
    RETURN_TYPES = ("STRING", "INT", "STRING", "INT", "STRING", "STRING", "STRING",   # Selected Outputs
                    "INT", "INT", "INT", "INT", "INT", "INT", "INT")                  # Global Outputs
    RETURN_NAMES = ("SEL_shot_details", "SEL_character_count", "SEL_shot_name", "SEL_scene_number", "SEL_scene_name", "SEL_shot_number_in_scene", "SEL_shot_data_JSON",
                    "total_shot_count", "total_character_count", "total_scene_count", 
                    "scene_start_indices", "scene_shot_counts", "unique_set_indices", "total_shot_count_list")
    FUNCTION = "select_shot"
    CATEGORY = "AkkiNodes/Production"
    
    OUTPUT_IS_LIST = (False, False, False, False, False, False, False,   # Selected Outputs
                      False, False, False, True, True, True, True)       # Global Outputs

    def select_shot(self, csv_report, shot_index):
        # Define the error tuple to perfectly match the final return signature
        error_tuple = ("ERROR: Invalid CSV", 0, "ERROR", 0, "ERROR", "0", "{}",
                       0, 0, 0, [], [], [], [])
        
        try:
            f = io.StringIO(csv_report)
            all_shots = list(csv.DictReader(f))
            if not all_shots:
                raise ValueError("CSV report is empty or invalid.")

            # --- SINGLE SOURCE OF TRUTH PIPELINE ---
            # 1. Calculate all global and looping stats ONCE
            total_shot_count = len(all_shots)
            master_character_set = set()
            scene_start_indices = []
            scene_shot_counts = []
            unique_set_indices = []
            scene_counts = defaultdict(int)
            last_scene_id = None
            seen_locations = set()

            for i, row in enumerate(all_shots):
                char_str = row.get('CHARACTERS', '')
                if char_str and char_str.lower().strip() not in ['none', 'n/a']:
                    for char_name in char_str.split(','):
                        cleaned_name = re.sub(r'\(.*?\)', '', char_name).strip()
                        if cleaned_name: master_character_set.add(cleaned_name)
                current_scene_id = row.get('SCENE')
                if current_scene_id:
                    scene_counts[current_scene_id] += 1
                    if current_scene_id != last_scene_id:
                        scene_start_indices.append(i + 1)
                        last_scene_id = current_scene_id
                location = row.get('LOCATION')
                if location and location not in seen_locations:
                    seen_locations.add(location)
                    unique_set_indices.append(i + 1)

            total_character_count = len(master_character_set)
            ordered_unique_scenes = sorted(scene_counts.keys(), key=lambda x: int(x))
            total_scene_count = len(ordered_unique_scenes)
            scene_shot_counts = [scene_counts[scene_id] for scene_id in ordered_unique_scenes]
            total_shot_count_list = list(range(1, total_shot_count + 1))

            # --- Select and Process the Target Shot ---
            target_index = shot_index - 1

            if 0 <= target_index < total_shot_count:
                # 2. Get the raw data for the selected shot
                raw_shot_data = all_shots[target_index]
                
                # 3. Create the enriched data packet (The Single Source of Truth)
                enriched_data = dict(raw_shot_data)
                props_set, costumes_set = set(), set()
                def _clean_and_parse_list(value_string):
                    if not value_string or value_string.lower().strip() in ['none', 'n/a']: return []
                    return [item.strip() for item in value_string.split(',') if item.strip()]
                
                for key, value in raw_shot_data.items():
                    key_upper = key.strip().upper()
                    if key_upper.startswith("PROPS"):
                        props_set.update(_clean_and_parse_list(value))
                    elif key_upper.startswith("COSTUMES"):
                        costumes_set.update(_clean_and_parse_list(value))
                
                enriched_data['CHARACTERS_LIST'] = _clean_and_parse_list(raw_shot_data.get("CHARACTERS", ""))
                enriched_data['PROPS_AGGREGATED_LIST'] = sorted(list(props_set))
                enriched_data['COSTUMES_AGGREGATED_LIST'] = sorted(list(costumes_set))
                
                # 4. Generate the final outputs by deriving them from the processed data
                
                # --- v2.12 Legacy Outputs (Derived & Hardened) ---
                details = []
                preferred_key_order = ["SCENE", "SHOT", "SHOT_TYPE", "LOCATION", "DESCRIPTION", "CHARACTERS", "DIALOGUE", "PERFORMANCE", "SET_DRESSING", "PROPS", "COSTUMES", "VFX", "SFX"]
                processed_keys = set()
                for key in preferred_key_order:
                    actual_key = next((k for k in raw_shot_data.keys() if k.strip().upper() == key), None)
                    if actual_key:
                        value = raw_shot_data.get(actual_key, "").strip()
                        # CRITICAL FIX: Use '' for blank, not "None"
                        details.append(f"**{actual_key}:** {value if value else ''}")
                        processed_keys.add(actual_key)
                for key, value in raw_shot_data.items():
                    if key not in processed_keys:
                        value_str = str(value).strip()
                        details.append(f"**{key}:** {value_str if value_str else ''}")
                SEL_shot_details = "\n".join(details)
                
                SEL_character_count = len(enriched_data['CHARACTERS_LIST'])
                SEL_shot_name = raw_shot_data.get("SHOT", "N/A").strip()
                SEL_scene_number = int(raw_shot_data.get("SCENE", 0))
                SEL_scene_name = raw_shot_data.get("LOCATION", "N/A").strip()
                
                count = 0
                current_scene_str = str(SEL_scene_number)
                for i in range(target_index + 1):
                    if all_shots[i].get("SCENE") == current_scene_str: count += 1
                SEL_shot_number_in_scene = str(count)
                
                SEL_shot_data_JSON = json.dumps(enriched_data, indent=2)

                return (SEL_shot_details, SEL_character_count, SEL_shot_name, SEL_scene_number, SEL_scene_name, SEL_shot_number_in_scene, SEL_shot_data_JSON,
                        total_shot_count, total_character_count, total_scene_count, 
                        scene_start_indices, scene_shot_counts, unique_set_indices, total_shot_count_list)
            else:
                error_msg_details = f"ERROR: Shot index {shot_index} is out of bounds (1-{total_shot_count})."
                return (error_msg_details, 0, "ERROR", 0, "ERROR", "0", "{}",
                        total_shot_count, total_character_count, total_scene_count, 
                        scene_start_indices, scene_shot_counts, unique_set_indices, total_shot_count_list)

        except Exception as e:
            traceback.print_exc()
            return error_tuple

# --- Mappings for this file ---
NODE_CLASS_MAPPINGS = {"ShotSelector-Akki": ShotSelector_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"ShotSelector-Akki": "Shot Selector v3.6 (DP) - Akki"}

# --- END OF FILE Akki_Shot_Selector.py ---