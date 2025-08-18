# --- START OF FILE Akki_Asset_Selector.py ---

# Node: Asset Selector v3.6 (Time-Only Variation) - Akki

import csv
import io
import traceback
import re
import json

class AssetSelector_Akki:
    """
    Parses a production CSV. v3.6 is the definitive "Time-Only Variation" version.
    It treats each unique location slugline as a single master set and only
    extracts the time-of-day as a variation, creating a simple and robust
    data structure for downstream nodes.
    """
    # --- CONFIGURATION (v3.6 - Hardened) ---
    COSTUME_ALIASES = {
        "practical travelling clothes": ["safari attire", "travel-worn clothing", "practical travelling clothes"],
        "sturdy boots": ["hiking boots", "sturdy boots"],
        "khaki shirt": ["khaki shirt", "khaki shorts", "cargo pants"]
    }
    PROP_ALIASES = {"writing tools": ["pen", "notebook"]}
    GLOBAL_NULL_EXACT = {"none", "n/a", "not specified"}
    GLOBAL_NULL_PREFIXES = ("no dialogue", "no performance", "n/a -", "no props", "none visible")
    GLOBAL_INVALID_KEYWORDS = {"hair", "eyes", "skin", "scar"}
    CATEGORICAL_EXCLUSIONS = {}
    INVALID_CHARS_PATTERN = re.compile(r'[\[\]\(\)\'"]')
    TIME_OF_DAY_SUFFIXES = {'DAY', 'NIGHT', 'DUSK', 'DAWN', 'CONTINUOUS', 'MOMENTS LATER', 'FLASHBACK', 'LATER'}

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"csv_report": ("STRING", {"forceInput": True}),"character_selector": ("INT", {"default": 1, "min": 1}),"set_selector": ("INT", {"default": 1, "min": 1}),}}
    
    RETURN_TYPES = ("STRING",)*6 + ("INT",)*2 + ("STRING",)*2 + ("STRING",) + ("STRING", "INT", "STRING", "STRING")
    RETURN_NAMES = ("master_character_list", "master_prop_list", "master_set_dressing_list", "master_costume_list", "master_vfx_list", "master_sfx_list","total_shots_count", "total_character_count", "selected_character_name", "selected_character_costumes", "debug_output","master_main_sets_list", "total_main_sets_count", "selected_main_set_name", "set_hierarchy_json",)
    FUNCTION = "select_assets"
    CATEGORY = "AkkiNodes/Production"
    
    def _format_master_list(self, asset_set):
        if not asset_set: return ""
        return ", ".join(sorted([item.capitalize() for item in asset_set]))

    def _compile_validation_regex(self, keywords):
        if not keywords: return None
        return re.compile(r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b', re.IGNORECASE)

    def _sanitize_asset_string(self, item):
        if not isinstance(item, str): return ""
        sanitized = self.INVALID_CHARS_PATTERN.sub('', item).strip()
        if sanitized.endswith('.'): sanitized = sanitized[:-1].strip()
        return sanitized

    def _is_asset_valid(self, item, category, validation_rules):
        sanitized_lower = item.lower()
        if not sanitized_lower: return False
        if sanitized_lower in validation_rules["null_exact"]: return False
        if sanitized_lower.startswith(validation_rules["null_prefixes"]): return False
        if validation_rules["global_regex"] and validation_rules["global_regex"].search(sanitized_lower): return False
        category_regex = validation_rules.get("category_regex_map", {}).get(category)
        if category_regex and category_regex.search(sanitized_lower): return False
        return True

    def _normalize_item(self, item): return item.lower().strip().rstrip('.')
    def _add_asset(self, asset_set, new_item):
        normalized_item = self._normalize_item(new_item)
        if normalized_item: asset_set.add(normalized_item)
    def _get_canonical_asset_name(self, item, alias_map):
        normalized_item = self._normalize_item(item)
        for canonical, aliases in alias_map.items():
            if normalized_item in aliases: return canonical
        return item
        
    # --- DEFINITIVE PARSER (v3.6 - Time-Only) ---
    def _parse_location_string(self, raw_location, validation_rules):
        location = self._sanitize_asset_string(raw_location)
        if not self._is_asset_valid(location, "LOCATION", validation_rules): return None
        
        # Extract and remove time of day from the end of the string first
        time_of_day = "UNKNOWN"
        base_name = location
        for suffix in self.TIME_OF_DAY_SUFFIXES:
            pattern = re.compile(r'\s*-\s*(' + re.escape(suffix) + r')\s*$', re.IGNORECASE)
            match = pattern.search(location)
            if match:
                time_of_day = match.group(1).upper()
                base_name = location[:match.start()].strip()
                break
        
        # Whatever remains is the base name. No sub-location is parsed.
        if not base_name: return None
        
        return {"base_name": base_name, "time_of_day": time_of_day}

    # --- DEFINITIVE CONSOLIDATOR (v3.6 - Time-Only) ---
    def _consolidate_sets(self, parsed_locations, all_rows, validation_rules):
        master_sets = {}
        for idx, loc_data in enumerate(parsed_locations):
            if loc_data is None: continue
            
            main_set_name = loc_data['base_name']
            if main_set_name not in master_sets:
                master_sets[main_set_name] = {"times_of_day": set(), "all_dressing": set(), "shot_indices": []}
            
            set_data = master_sets[main_set_name]
            set_data["times_of_day"].add(loc_data['time_of_day'])
            set_data["shot_indices"].append(idx)
            
            dressing_value = all_rows[idx].get('SET_DRESSING', '')
            if dressing_value:
                for item in dressing_value.split(','):
                    sanitized_item = self._sanitize_asset_string(item)
                    if self._is_asset_valid(sanitized_item, "SET_DRESSING", validation_rules):
                        set_data["all_dressing"].add(sanitized_item)
                        
        return master_sets

    def select_assets(self, csv_report, character_selector, set_selector):
        error_tuple = ("ERROR",)*6 + (0,0) + ("ERROR",)*2 + ("Check Console",) + ("ERROR", 0, "ERROR", "{}")
        if not csv_report or not csv_report.strip() or csv_report.startswith("ERROR:"): return error_tuple
        try:
            f = io.StringIO(csv_report)
            reader = csv.DictReader(f)
            all_rows = [row for row in reader if any(field and field.strip() for field in row.values())]
            if not all_rows: raise ValueError("CSV report contains no valid data.")
            
            validation_rules = { # ... (omitted for brevity)
                "null_exact": self.GLOBAL_NULL_EXACT, "null_prefixes": self.GLOBAL_NULL_PREFIXES,
                "global_regex": self._compile_validation_regex(self.GLOBAL_INVALID_KEYWORDS),
                "category_regex_map": {cat: self._compile_validation_regex(kw) for cat, kw in self.CATEGORICAL_EXCLUSIONS.items()}
            }
            
            master_assets = {"CHARACTERS": set(), "PROPS": set(), "COSTUMES": set(), "VFX": set(), "SFX": set()}
            # ... (Asset parsing for characters, etc. is unchanged and omitted for brevity)
            for row in all_rows:
                for key, value in row.items():
                    if not value: continue
                    category = key.strip().upper().split(' (')[0]
                    for item in value.split(','):
                        sanitized_item = self._sanitize_asset_string(item)
                        if not self._is_asset_valid(sanitized_item, category, validation_rules): continue
                        alias_map, target_set = None, None
                        if category == "PROPS": target_set, alias_map = master_assets["PROPS"], self.PROP_ALIASES
                        elif category == "COSTUMES": target_set, alias_map = master_assets["COSTUMES"], self.COSTUME_ALIASES
                        elif category in master_assets: target_set = master_assets[category]
                        else: continue
                        canonical_item = self._get_canonical_asset_name(sanitized_item, alias_map) if alias_map else sanitized_item
                        self._add_asset(target_set, canonical_item)
            
            location_header = next((k for k in all_rows[0].keys() if k.strip().upper() == 'LOCATION'), 'LOCATION')
            parsed_locations = [self._parse_location_string(row.get(location_header, ''), validation_rules) for row in all_rows]
            consolidated_sets = self._consolidate_sets(parsed_locations, all_rows, validation_rules)
            
            global_set_dressing = set()
            for data in consolidated_sets.values(): global_set_dressing.update(data['all_dressing'])
            
            # ... (Master list formatting is unchanged and omitted for brevity)
            master_prop_list = self._format_master_list(master_assets["PROPS"])
            master_costume_list = self._format_master_list(master_assets["COSTUMES"])
            master_set_dressing_list = self._format_master_list(global_set_dressing)
            master_character_list = self._format_master_list(master_assets["CHARACTERS"])
            master_vfx_list = self._format_master_list(master_assets["VFX"])
            master_sfx_list = self._format_master_list(master_assets["SFX"])
            
            total_shots_count = len(all_rows)
            total_characters_count = len(master_assets["CHARACTERS"])
            
            # ... (Character costume selection is unchanged and omitted for brevity)
            sorted_chars = sorted(list(master_assets["CHARACTERS"]))
            selected_char_name, selected_char_costumes = "N/A", "N/A"
            if sorted_chars:
                char_index = character_selector - 1
                if 0 <= char_index < len(sorted_chars):
                    selected_char_name = self._format_master_list({sorted_chars[char_index]})
                    costume_col_name = f"COSTUMES ({sorted_chars[char_index]})"
                    actual_costume_col = next((k for k in all_rows[0].keys() if k.strip().upper() == costume_col_name.upper()), None)
                    costumes_for_char = set()
                    if actual_costume_col:
                        for row in all_rows:
                            val = row.get(actual_costume_col)
                            if val:
                                for item in val.split(','):
                                    sanitized_item = self._sanitize_asset_string(item)
                                    if self._is_asset_valid(sanitized_item, "COSTUMES", validation_rules):
                                        canonical_item = self._get_canonical_asset_name(sanitized_item, self.COSTUME_ALIASES)
                                        self._add_asset(costumes_for_char, canonical_item)
                    selected_char_costumes = self._format_master_list(costumes_for_char) if costumes_for_char else "None"

            
            sorted_main_sets = sorted(consolidated_sets.keys())
            master_main_sets_list = ", ".join(sorted_main_sets)
            total_main_sets_count = len(sorted_main_sets)
            selected_main_set_name, set_hierarchy_json = "N/A", "{}" # Renamed for clarity
            if sorted_main_sets:
                set_index = set_selector - 1
                if 0 <= set_index < len(sorted_main_sets):
                    selected_main_set_name = sorted_main_sets[set_index]
                    set_data = consolidated_sets[selected_main_set_name]
                    
                    # --- DEFINITIVE JSON STRUCTURE (v3.6 - Time-Only) ---
                    json_output = {
                        "main_set": selected_main_set_name,
                        "times_of_day": sorted(list(set_data.get("times_of_day", set()))),
                        "all_dressing_items": sorted([item.capitalize() for item in set_data.get("all_dressing", set())]),
                        "shot_indices": sorted(set_data.get("shot_indices", []))
                    }
                    set_hierarchy_json = json.dumps(json_output, indent=2)

            debug_output = f"""--- Asset Selector v3.6 (Time-Only) DEBUG ---
- Total Shots: {total_shots_count}
- Total Unique Sets: {total_main_sets_count}
... (rest of debug output)
"""
            return (master_character_list, master_prop_list, master_set_dressing_list, master_costume_list, master_vfx_list, master_sfx_list,total_shots_count, total_characters_count,selected_char_name, selected_char_costumes, debug_output,master_main_sets_list, total_main_sets_count, selected_main_set_name, set_hierarchy_json)
        except Exception as e:
            traceback.print_exc()
            error_msg = f"ERROR: Could not process CSV. Check console. Details: {e}"
            return (error_msg,) + error_tuple[1:]

NODE_CLASS_MAPPINGS = {"AssetSelector-Akki": AssetSelector_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AssetSelector-Akki": "Asset Selector v3.6 (Prod) - Akki"}

# --- END OF FILE Akki_Asset_Selector.py ---