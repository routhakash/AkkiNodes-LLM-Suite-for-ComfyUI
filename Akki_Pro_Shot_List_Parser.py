# Node: Pro Shot List Parser v9.4 (Definitive)

import re
import traceback
import csv
import io
import json

class ProShotListParser_Akki:
    """
    The definitive, intelligent parser. v9.4 represents the final synthesis,
    combining a robust ETL architecture with a context-aware, two-pass transform
    process. This ensures pronouns are resolved, not deleted, guaranteeing the
    highest level of data integrity and reliability.
    """
    KEY_ALIASES = {
        "SET_TYPE": "SHOT_TYPE",
        "CAMERA": "Camera & Lens",
        "SHOT TYPE": "SHOT_TYPE",
        "MOVEMENT/ANGLE": "Movement & Angle"
    }
    
    CHARACTER_DENYLIST = {"he", "she", "it", "they", "them", "him", "her"}

    @classmethod
    def INPUT_TYPES(cls):
        return { "required": {
                "shot_breakdown_report": ("STRING", {"forceInput": True}),
                "character_bible": ("STRING", {"forceInput": True}),
                "shot_index_for_debug": ("INT", {"default": 0, "min": 0, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "full_report_csv", "shot_details_for_dossier", "cinematography_notes", 
        "sound_design_notes", "performance_notes", "master_character_list", "master_prop_list",
        "debug_log"
    )
    FUNCTION = "parse_pro_report"
    CATEGORY = "AkkiNodes/Production"

    # --- INDEPENDENT, PURE HELPER FUNCTIONS ---

    def _get_canonical_names(self, character_bible):
        name_pattern = re.compile(r"^NAME:\s*(.*)$", re.MULTILINE | re.IGNORECASE)
        return [name.strip() for name in name_pattern.findall(character_bible)]

    def _levenshtein_distance(self, s1, s2):
        if len(s1) > len(s2): s1, s2 = s2, s1
        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            new_distances = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2: new_distances.append(distances[i1])
                else: new_distances.append(1 + min((distances[i1], distances[i1 + 1], new_distances[-1])))
            distances = new_distances
        return distances[-1]

    def _find_best_match(self, variation, canonical_names):
        if not variation or not canonical_names: return variation
        var_lower = variation.lower()
        for name in canonical_names:
            if var_lower == name.lower(): return name
        possible_matches = [name for name in canonical_names if name.lower().startswith(var_lower)]
        if len(possible_matches) == 1: return possible_matches[0]
        scores = {name: self._levenshtein_distance(var_lower, name.lower()) for name in canonical_names}
        best_match = min(scores, key=scores.get)
        if scores[best_match] <= 3:
            return best_match
        else:
            return variation

    def _normalize_character_name(self, name_variation, canonical_names):
        if not name_variation: return ""
        end_of_name_index = -1
        markers = ['(', 'V.O.', 'CONT\'D', 'O.S.']
        found_indices = [name_variation.find(m) for m in markers if name_variation.find(m) != -1]
        if found_indices:
            end_of_name_index = min(found_indices)
        cleaned_variation = name_variation[:end_of_name_index].strip() if end_of_name_index != -1 else name_variation.strip()
        return self._find_best_match(cleaned_variation, canonical_names)

    # [NEW] v9.4 - Context-aware entity resolver.
    def _resolve_entity(self, name_variation, canonical_names, ground_truth_characters):
        """Resolves pronouns using shot context, otherwise normalizes."""
        # Step 1: Check if the variation is a pronoun.
        if name_variation.lower() in self.CHARACTER_DENYLIST:
            # Step 2: If it is, resolve only if the context is unambiguous (only 1 character in the shot).
            if len(ground_truth_characters) == 1:
                return ground_truth_characters[0]
            else:
                # Cannot resolve ambiguously, so return original to surface the upstream error.
                return name_variation
        
        # Step 3: If not a pronoun, use the standard normalization process.
        return self._normalize_character_name(name_variation, canonical_names)

    def _sanitize_dialogue(self, text, canonical_names):
        if not text or text.strip().lower() in ("none", "none.", "n/a"): return "None"
        text = text.replace('\n', ' ').strip()
        speaker_candidate, action, dialogue_text, final_speaker = None, None, text, None

        if ':' in text:
            speaker_candidate, rest = text.split(':', 1)
            dialogue_text = rest.strip()
        
        action_match = re.match(r"^\((.*?)\)\s*(.*)", dialogue_text, re.DOTALL)
        if action_match:
            action, dialogue_text = action_match.groups()

        if speaker_candidate:
            normalized_speaker = self._normalize_character_name(speaker_candidate, canonical_names)
            if normalized_speaker in canonical_names:
                final_speaker = normalized_speaker
            else:
                final_speaker = speaker_candidate.strip()
        else:
            for name in canonical_names:
                variations = [name]
                if ' ' in name: variations.append(name.split(' ')[0])
                for var in sorted(variations, key=len, reverse=True):
                    if text.upper().startswith(var.upper()):
                        final_speaker = name
                        rest_of_line = text[len(var):].strip()
                        action_match = re.match(r"^\((.*?)\)\s*(.*)", rest_of_line, re.DOTALL)
                        if action_match: action, dialogue_text = action_match.groups()
                        else: action, dialogue_text = None, rest_of_line
                        break
                if final_speaker: break
        
        parts = []
        if final_speaker: parts.append(f"{final_speaker}:")
        if action: parts.append(f"({action.strip()})")
        if dialogue_text: parts.append(dialogue_text.strip())
        if not parts and text: return text
        return " ".join(parts) if parts else "None"

    # --- ETL STAGE 1: EXTRACT ---
    def _extract_raw_data(self, raw_text):
        shot_blocks = re.findall(r"//---SHOT_START---//([\s\S]*?)(?://---SHOT_END---//|$)", raw_text)
        unique_blocks, seen_blocks = [], set()
        for block in shot_blocks:
            compare_key = re.sub(r'\s+', ' ', block).strip()
            if compare_key and compare_key not in seen_blocks:
                seen_blocks.add(compare_key)
                unique_blocks.append(block)
        all_shots_data = []
        for block_text in unique_blocks:
            shot_tuples = []
            current_key, value_lines = None, []
            for line in block_text.strip().split('\n'):
                line = line.strip()
                if not line: continue
                key_match = re.match(r'^([^:]+?):\s*(.*)', line)
                if key_match:
                    if current_key:
                        shot_tuples.append((current_key, " ".join(value_lines)))
                    current_key = key_match.group(1).strip()
                    value_lines = [key_match.group(2).strip()] if key_match.group(2).strip() else []
                elif current_key:
                    value_lines.append(line)
            if current_key:
                shot_tuples.append((current_key, " ".join(value_lines)))
            if shot_tuples:
                all_shots_data.append(shot_tuples)
        return all_shots_data

    # --- ETL STAGE 2: TRANSFORM ---
    def _transform_and_sanitize_data(self, all_shots_tuples, canonical_names, debug_log_lines, is_debug_mode):
        transformed_shots = []
        for shot_tuples in all_shots_tuples:
            shot_id_tuple = next((item for item in shot_tuples if item[0] == 'SHOT'), ('SHOT', 'N/A'))
            if is_debug_mode:
                debug_log_lines.append(f"\n--- NORMALIZING SHOT: {shot_id_tuple[1]} ---")

            merged_shot = {}
            for key, value in shot_tuples:
                corrected_key = self.KEY_ALIASES.get(key.upper(), key)
                if is_debug_mode and key.upper() in self.KEY_ALIASES:
                    debug_log_lines.append(f"  - SCHEMA CORRECTION: Remapped key '{key}' to '{corrected_key}'")
                if corrected_key in merged_shot and merged_shot[corrected_key] and value:
                     merged_shot[corrected_key] += f"\n{value}"
                else:
                    merged_shot[corrected_key] = value

            # [RE-ARCHITECTED] v9.4 - Two-Pass Transformation
            # Pass 1: Establish Ground Truth for the shot.
            ground_truth_characters = []
            if "CHARACTERS" in merged_shot:
                char_val = merged_shot["CHARACTERS"]
                if char_val and char_val.lower().strip() not in ('none', 'n/a'):
                    raw_names = [v.strip() for v in char_val.split(',') if v.strip()]
                    # Filter out junk BEFORE normalization to establish a clean ground truth.
                    valid_raw_names = [name for name in raw_names if name.lower() not in self.CHARACTER_DENYLIST]
                    ground_truth_characters = [self._normalize_character_name(v, canonical_names) for v in valid_raw_names]

            # Pass 2: Resolve, Normalize, and Sanitize all fields using the ground truth context.
            final_shot = {}
            for key, value in merged_shot.items():
                if key.upper() == "CHARACTERS":
                    final_shot[key] = ", ".join(ground_truth_characters) if ground_truth_characters else "None"
                elif key.upper() == "DIALOGUE":
                    final_shot[key] = self._sanitize_dialogue(value, canonical_names)
                elif re.match(r"^(PROPS|COSTUMES)\s*\((.*)\)$", key, re.IGNORECASE):
                    key_type, char_name_var = re.match(r"^(PROPS|COSTUMES)\s*\((.*)\)$", key, re.IGNORECASE).groups()
                    # Use the context-aware resolver here
                    resolved_name = self._resolve_entity(char_name_var, canonical_names, ground_truth_characters)
                    normalized_key = f"{key_type.upper()} ({resolved_name})"
                    if is_debug_mode and key != normalized_key:
                        debug_log_lines.append(f"  - CONTEXT-AWARE MATCH: Corrected key '{key}' to '{normalized_key}'")
                    if normalized_key in final_shot and final_shot[normalized_key] and value:
                        final_shot[normalized_key] += f", {value}"
                    else:
                        final_shot[normalized_key] = value
                else:
                    final_shot[key] = value
            
            transformed_shots.append(final_shot)
        return transformed_shots

    def parse_pro_report(self, shot_breakdown_report, character_bible, shot_index_for_debug):
        debug_log_lines = []
        if not shot_breakdown_report or not shot_breakdown_report.strip() or shot_breakdown_report.startswith("ERROR:"):
            return ("ERROR: Invalid or empty shot breakdown report provided.",) * 8
        try:
            is_debug_mode = shot_index_for_debug > 0
            canonical_names = self._get_canonical_names(character_bible)
            
            raw_parsed_tuples = self._extract_raw_data(shot_breakdown_report)
            if not raw_parsed_tuples: raise ValueError("Parsing yielded no shot data.")
            
            shots_to_process = [raw_parsed_tuples[shot_index_for_debug - 1]] if is_debug_mode and shot_index_for_debug <= len(raw_parsed_tuples) else raw_parsed_tuples
            if is_debug_mode:
                debug_log_lines.append(f"--- DEBUGGING SINGLE SHOT: INDEX {shot_index_for_debug} of {len(raw_parsed_tuples)} ---")
                raw_log_data = [[list(t) for t in shot] for shot in shots_to_process]
                debug_log_lines.append(f"\n--- [1] RAW PARSED DATA (PRE-TRANSFORM) ---\n{json.dumps(raw_log_data, indent=2)}")

            all_parsed_shots = self._transform_and_sanitize_data(shots_to_process, canonical_names, debug_log_lines, is_debug_mode)

            if is_debug_mode:
                debug_log_lines.append(f"\n--- [2] FINAL NORMALIZED DICTIONARY ---\n{json.dumps(all_parsed_shots, indent=2)}")
                return ("",) * 7 + ("\n".join(debug_log_lines),)
            
            master_assets = {"CHARACTERS": set(), "PROPS": set()}
            for shot in all_parsed_shots:
                if shot.get("CHARACTERS") and shot["CHARACTERS"] != "None": master_assets["CHARACTERS"].update([name.strip() for name in shot["CHARACTERS"].split(',') if name.strip()])
                for key, value in shot.items():
                    if key.startswith("PROPS (") and value: master_assets["PROPS"].update([p.strip() for p in value.split(',') if p.strip()])
            
            dossier_details_list, cinematography_notes_list, sound_design_notes_list, performance_notes_list = [], [], [], []
            for i, shot in enumerate(all_parsed_shots):
                shot_id = shot.get('SHOT', shot.get('SCENE', f"Unnumbered Shot {i+1}"))
                dossier_details_list.append(f"**Scene:** {shot.get('SCENE', 'N/A')}\n**Shot:** {shot.get('SHOT', 'N/A')}\n**Description:** {shot.get('DESCRIPTION', 'N/A')}\n**Characters:** {shot.get('CHARACTERS', 'N/A')}\n**VFX:** {shot.get('VFX', 'N/A')}")
                cinematography_notes_list.append(f"//--- SHOT {shot_id} ---\n**SHOT_FRAMING:** {shot.get('SHOT_FRAMING', 'N/A')}\n**Camera & Lens:** {shot.get('Camera & Lens', 'N/A')}\n**Movement & Angle:** {shot.get('Movement & Angle', 'N/A')}")
                sound_design_notes_list.append(f"//--- SHOT {shot_id} ---\n**Sound Design Cue:** {shot.get('Sound Design Cue', 'N/A')}\n**SFX:** {shot.get('SFX', 'N/A')}")
                performance_notes_list.append(f"//--- SHOT {shot_id} ---\n**PERFORMANCE:** {shot.get('PERFORMANCE', 'N/A')}\n**DIALOGUE:** {shot.get('DIALOGUE', 'N/A')}")
            
            header_set = set()
            for shot in all_parsed_shots: header_set.update(shot.keys())
            preferred_order = ["SCENE", "LOCATION", "SHOT", "SHOT_TYPE", "SHOT_FRAMING", "Camera & Lens", "DESCRIPTION", "Movement & Angle", "CHARACTERS", "VFX", "Sound Design Cue", "SFX", "PERFORMANCE", "DIALOGUE", "Director's Rationale"]
            static_headers = [h for h in preferred_order if h in header_set]
            dynamic_headers = sorted([h for h in header_set if h not in static_headers])
            final_header = static_headers + dynamic_headers
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=final_header, quoting=csv.QUOTE_ALL, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_parsed_shots)
            full_report_csv = output.getvalue()

            shot_details_for_dossier = "\n\n//---SHOT_BREAK---//\n\n".join(dossier_details_list)
            cinematography_notes = "\n\n".join(cinematography_notes_list)
            sound_design_notes = "\n\n".join(sound_design_notes_list)
            performance_notes = "\n\n".join(performance_notes_list)
            master_character_list = ", ".join(sorted(list(master_assets["CHARACTERS"])))
            master_prop_list = ", ".join(sorted(list(master_assets["PROPS"])))
            final_debug_log = "Debug mode off. Set shot_index > 0 to enable."
        except Exception as e:
            traceback.print_exc()
            error_msg = f"Failed to parse pro report. Check console. Details: {e}"
            return (f"ERROR: {error_msg}",) * 7 + (f"ERROR: {e}\n{traceback.format_exc()}",)

        return (full_report_csv, shot_details_for_dossier, cinematography_notes, sound_design_notes, performance_notes, master_character_list, master_prop_list, final_debug_log)

NODE_CLASS_MAPPINGS = {"ProShotListParser-Akki": ProShotListParser_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"ProShotListParser-Akki": "Pro Shot List Parser v9.4 (Definitive)"}