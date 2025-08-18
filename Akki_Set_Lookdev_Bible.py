# --- START OF FILE Akki_Set_Lookdev_Bible.py ---

# Node: AI Set Lookdev (Bible) v6.0 (Time-Only Variation)

import traceback
import re
import random
import json
import os
from .shared_utils import report_token_usage, extract_tagged_content, get_wildcard_list

# --- HELPER FUNCTIONS for Self-Contained Prompt Loading ---
NODE_DIR = os.path.dirname(__file__)
PROMPTS_ROOT_DIR = os.path.join(NODE_DIR, "_prompts", "LookdevSET")

def get_prompt_files_from_stage_dir(stage_folder):
    stage_dir = os.path.join(PROMPTS_ROOT_DIR, stage_folder)
    if not os.path.isdir(stage_dir):
        print(f"[SetLookdev-v6.0] Creating prompt directory: {stage_dir}")
        os.makedirs(stage_dir, exist_ok=True)
        placeholder_path = os.path.join(stage_dir, "placeholder.txt")
        if not os.path.exists(placeholder_path):
             with open(placeholder_path, 'w', encoding='utf-8') as f: f.write(f"Add your {stage_folder} prompt .txt files here.")
        return ["placeholder.txt"]
    try:
        files = [f for f in os.listdir(stage_dir) if f.endswith('.txt')]
        return files if files else ["No .txt files found"]
    except Exception as e:
        print(f"[SetLookdev-v6.0] Error scanning prompt directory {stage_dir}: {e}")
        return ["Error loading prompts"]

def read_prompt_file(stage_folder, filename):
    filepath = os.path.join(PROMPTS_ROOT_DIR, stage_folder, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def sanitize_filename(name):
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized

class AISetLookdevBible_Akki:
    """
    AI Set Lookdev (Bible) v6.0. The definitive "Time-Only Variation" engine.
    This node generates a master lookdev, then generates complete, rewritten
    prompts for all time-of-day variations provided by the Asset Selector's
    clean JSON output.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "world_bible": ("STRING", {"forceInput": True}),
                "screenplay": ("STRING", {"forceInput": True}),
                "set_hierarchy_json": ("STRING", {"forceInput": True}),
                "selected_main_set_name": ("STRING", {"forceInput": True}),
                "prompt_master_generator": (get_prompt_files_from_stage_dir("stage1"),),
                "prompt_variation_generator": (get_prompt_files_from_stage_dir("stage2"),),
                "debug_mode": (["Off", "Master Prose Only"],),
                "temperature": ("FLOAT", {"default": 0.70, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1234}),
                "max_tokens": ("INT", {"default": 2048, "min": 256, "max": 16384}),
            },
            "optional": {
                "architectural_style": (["Default", "Random"] + get_wildcard_list("set_architectural_styles.txt"),),
                "primary_material": (["Default", "Random"] + get_wildcard_list("set_materials_man_made.txt"),),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("master_lookdev_prose", "master_set_name", 
                    "variation_set_names_LIST", "variation_set_prompts_LIST", 
                    "full_llm_process_log", "variation_count")
    
    OUTPUT_IS_LIST = (False, False, True, True, False, False)

    FUNCTION = "generate_lookdev"
    CATEGORY = "AkkiNodes/Visuals"

    def _resolve_attribute(self, selection, wildcard_file):
        if selection is None or selection == "Default": return None
        if selection == "Random":
            options = get_wildcard_list(wildcard_file)
            return random.choice(options) if options and "Could not load" not in options[0] else None
        return selection

    def _extract_first_and_last_paragraphs(self, text):
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        if len(paragraphs) <= 1: return text
        first_paragraph = re.sub(r'^\d+\.\s*', '', paragraphs[0])
        last_paragraph = re.sub(r'^\d+\.\s*', '', paragraphs[-1])
        return f"{first_paragraph}\n\n{last_paragraph}"

    def _get_scene_context_by_time(self, screenplay, set_name, time_of_day):
        if not screenplay: return "No screenplay provided."
        
        # This regex now looks for the set name AND the time of day in the same heading
        pattern_str = f"(?=.*{re.escape(set_name)})(?=.*{re.escape(time_of_day)})"
        scene_pattern = re.compile(r'(\d+\.\s*(?:INT|EXT|I/E)\..*' + pattern_str + r'.*)', re.IGNORECASE)
        
        scenes = re.split(scene_pattern, screenplay)
        relevant_scenes_text = []
        for i in range(1, len(scenes), 2):
            heading = scenes[i]
            content = scenes[i+1].split('\n\n', 1)[0] # Heuristic to get content until next scene
            if re.search(r'\d+\.\s*(?:INT|EXT|I/E)\.', content):
                 content = content.split(re.search(r'\d+\.\s*(?:INT|EXT|I/E)\.', content).group(0))[0]
            relevant_scenes_text.append(f"--- Scene: {heading.strip()} ---\n{content.strip()}")

        return "\n\n".join(relevant_scenes_text) if relevant_scenes_text else f"No specific scene description found for time: {time_of_day}."

    def generate_lookdev(self, llm_model, world_bible, screenplay, set_hierarchy_json, selected_main_set_name,
                         prompt_master_generator, prompt_variation_generator, debug_mode, **kwargs):
        
        full_llm_process_log = ""
        variation_set_names_list, variation_set_prompts_list = [], []
        error_tuple = ("ERROR", "Error", [], [], "Check console for errors.", 0)
        
        try:
            if not hasattr(llm_model, 'create_completion'): raise ValueError("LLM Model invalid.")
            if not selected_main_set_name or "ERROR:" in selected_main_set_name: return error_tuple

            # --- PART 1: MASTER LOOKDEV GENERATION ---
            print(f"[SetLookdev-v6.0] Part 1: Generating Master Prose for '{selected_main_set_name}'...")
            
            json_data = json.loads(set_hierarchy_json)
            master_set_name = json_data.get("main_set", selected_main_set_name)
            all_dressing_items = ", ".join(json_data.get("all_dressing_items", ["None"]))
            
            # Get story context for the whole master set by not specifying a time
            master_story_context = self._get_scene_context_by_time(screenplay, master_set_name, "ALL_TIMES")

            attrs = { "Architectural Style": self._resolve_attribute(kwargs.get('architectural_style'), "set_architectural_styles.txt"),
                      "Primary Material": self._resolve_attribute(kwargs.get('primary_material'), "set_materials_man_made.txt")}
            creative_attributes_str = "\n".join([f"- {key}: {value}" for key, value in attrs.items() if value]) or "None specified."
            
            master_template = read_prompt_file("stage1", prompt_master_generator)
            master_prompt_str = master_template.format(set_name=master_set_name, deterministic_set_dressing=all_dressing_items,
                                                   story_context=master_story_context, world_bible=world_bible,
                                                   creative_attributes=creative_attributes_str)
            
            master_output = llm_model.create_completion(prompt=master_prompt_str, max_tokens=2048, temperature=0.6)
            raw_master_prose = master_output['choices'][0]['text'].strip()
            full_llm_process_log += f"--- MASTER PROSE (RAW) ---\n{raw_master_prose}\n\n"

            filtered_master_prose = self._extract_first_and_last_paragraphs(raw_master_prose)
            sanitized_master_name = sanitize_filename(master_set_name)
            if debug_mode == "Master Prose Only":
                return (filtered_master_prose, sanitized_master_name, [], [], full_llm_process_log, 0)

            # --- PART 2: TIME-OF-DAY VARIATION LOOP ---
            print(f"[SetLookdev-v6.0] Part 2: Generating Time-of-Day Variations...")
            variation_template = read_prompt_file("stage2", prompt_variation_generator)
            
            times_of_day = json_data.get("times_of_day", ["UNKNOWN"])
            
            for time_of_day in times_of_day:
                
                variation_target_name = f"{master_set_name} - {time_of_day}"
                print(f"  - Generating: {variation_target_name}")
                
                # Get the story context specific to this time of day
                specific_context = self._get_scene_context_by_time(screenplay, master_set_name, time_of_day)

                variation_prompt_str = variation_template.format(
                    master_prose_reference=filtered_master_prose,
                    variation_target_name=variation_target_name,
                    time_of_day=time_of_day,
                    specific_story_context=specific_context,
                    world_bible=world_bible
                )
                
                variation_output = llm_model.create_completion(prompt=variation_prompt_str, max_tokens=2048, temperature=0.7)
                final_variation_prompt = variation_output['choices'][0]['text'].strip()
                
                variation_set_names_list.append(variation_target_name)
                variation_set_prompts_list.append(final_variation_prompt)
                full_llm_process_log += f"--- VARIATION: {variation_target_name} ---\n{final_variation_prompt}\n\n"

            return (filtered_master_prose, sanitized_master_name, variation_set_names_list, variation_set_prompts_list, full_llm_process_log, len(variation_set_names_list))

        except Exception as e:
            print(f"[SetLookdev-v6.0] Error:"); traceback.print_exc()
            error_msg = f"ERROR: {e}"
            return (error_msg, "Error", [], [], str(e), 0)

# Using original names to ensure the node loads
NODE_CLASS_MAPPINGS = {"AISetLookdevBible-Akki": AISetLookdevBible_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AISetLookdevBible-Akki": "AI Set Lookdev (Bible) v6.0 - Akki"}

# --- END OF FILE Akki_Set_Lookdev_Bible.py ---