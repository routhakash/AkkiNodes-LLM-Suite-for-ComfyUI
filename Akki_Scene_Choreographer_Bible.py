# --- START OF FILE Akki_Scene_Choreographer_Bible.py ---

# Node: AI Scene Choreographer (Bible) v4.3 (Case-Insensitive)

import traceback
import csv
import io
import os
import re
import json
from .shared_utils import report_token_usage

# --- HELPER FUNCTIONS for Self-Contained Prompt Loading ---
NODE_DIR = os.path.dirname(__file__)
PROMPTS_ROOT_DIR = os.path.join(NODE_DIR, "_prompts", "Choreographer")

# ... (Helper functions are unchanged) ...
def get_prompt_files_from_stage_dir(stage_folder):
    stage_dir = os.path.join(PROMPTS_ROOT_DIR, stage_folder)
    if not os.path.isdir(stage_dir):
        print(f"[SceneChoreographer-v4.3] Creating prompt directory: {stage_dir}")
        os.makedirs(stage_dir, exist_ok=True)
        placeholder_path = os.path.join(stage_dir, "placeholder.txt")
        if not os.path.exists(placeholder_path):
             with open(placeholder_path, 'w', encoding='utf-8') as f: f.write(f"Add your {stage_folder} prompt .txt files here.")
        return ["placeholder.txt"]
    try:
        files = [f for f in os.listdir(stage_dir) if f.endswith('.txt')]
        return files if files else ["No .txt files found"]
    except Exception as e:
        print(f"[SceneChoreographer-v4.3] Error scanning prompt directory {stage_dir}: {e}")
        return ["Error loading prompts"]

def read_prompt_file(stage_folder, filename):
    filepath = os.path.join(PROMPTS_ROOT_DIR, stage_folder, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


class AISceneChoreographerBible_Akki:
    """
    v4.3 adds case-insensitive lookups for all assets, ensuring robust
    matching between lookdev files and CSV data, fixing the context bleed bug.
    """

    @classmethod
    def INPUT_TYPES(cls):
        # ... (INPUT_TYPES are unchanged from v4.2)
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "csv_report": ("STRING", {"forceInput": True}),
                "scene_number": ("INT", {"default": 1, "min": 1}),
                "set_names_STRING": ("STRING", {"forceInput": True}),
                "set_prompts_STRING": ("STRING", {"forceInput": True}),
                "character_names_STRING": ("STRING", {"forceInput": True}),
                "character_prompts_STRING": ("STRING", {"forceInput": True}),
                "prompt_director": (get_prompt_files_from_stage_dir("stage1"),),
                "prompt_promptsmith": (get_prompt_files_from_stage_dir("stage2"),),
                "temperature": ("FLOAT", {"default": 0.5, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1234}),
                "max_tokens": ("INT", {"default": 4096, "min": 256, "max": 16384}),
            }
        }


    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("shot_names_LIST", "final_shot_prompts_LIST", "scene_name", "choreography_text_DEBUG", "shot_count")
    FUNCTION = "choreograph_scene"
    CATEGORY = "AkkiNodes/Visuals/Production Line"
    
    OUTPUT_IS_LIST = (True, True, False, False, False)

    def choreograph_scene(self, llm_model, csv_report, scene_number, 
                          set_names_STRING, set_prompts_STRING, 
                          character_names_STRING, character_prompts_STRING,
                          prompt_director, prompt_promptsmith, **kwargs):
        
        full_llm_process_log = ""
        scene_location = "ERROR"
        error_tuple = ([], [], "ERROR", "Check console.", 0)
        
        try:
            if not hasattr(llm_model, 'create_completion'): raise ValueError("LLM Model invalid.")

            delimiter = "|||---|||"
            set_names_LIST = [name.strip() for name in set_names_STRING.split(delimiter) if name.strip()]
            set_prompts_LIST = [prompt.strip() for prompt in set_prompts_STRING.split(delimiter) if prompt.strip()]
            character_names_LIST = [name.strip() for name in character_names_STRING.split(delimiter) if name.strip()]
            character_prompts_LIST = [prompt.strip() for prompt in character_prompts_STRING.split(delimiter) if prompt.strip()]
            
            # --- SURGICAL CHANGE 1: Create dictionaries with lowercase keys ---
            set_lookdev_dict = {name.lower(): prompt for name, prompt in zip(set_names_LIST, set_prompts_LIST)}
            character_lookdev_dict = {name.lower(): prompt for name, prompt in zip(character_names_LIST, character_prompts_LIST)}

            f = io.StringIO(csv_report)
            scene_shots = [row for row in list(csv.DictReader(f)) if row.get('SCENE') == str(scene_number)]
            if not scene_shots:
                return ([], [], f"ERROR: No shots for Scene {scene_number}", "", 0)

            print(f"[SceneChoreographer-v4.3] Stage 1 (Director): Generating choreography for Scene {scene_number}...")

            scene_location = scene_shots[0].get('LOCATION', 'Unknown Location').strip()
            
            # --- SURGICAL CHANGE 2: Normalize names before lookup ---
            scene_location_lower = scene_location.lower()
            matched_set_name = ""
            best_match_len = 0
            # Keys are already lowercase from dict creation
            for name in set_lookdev_dict.keys():
                if scene_location_lower.startswith(name) and len(name) > best_match_len:
                    matched_set_name = name
                    best_match_len = len(name)
            
            set_lookdev_prompt = set_lookdev_dict.get(matched_set_name, f"No detailed lookdev found for set '{matched_set_name}'.")
            
            # We use the original-cased name for the XML tag for better readability in the prompt
            original_matched_set_name = next((s_name for s_name in set_names_LIST if s_name.lower() == matched_set_name), matched_set_name)
            lookdev_bible_context = f'<lookdev_for_set name="{original_matched_set_name}">\n{set_lookdev_prompt}\n</lookdev_for_set>\n'
            
            scene_characters = {c.strip() for shot in scene_shots for c in shot.get('CHARACTERS', '').split(',') if c.strip()}
            for char_name in sorted(list(scene_characters)):
                # Use the original-cased name for the XML tag
                char_lookdev_prompt = character_lookdev_dict.get(char_name.lower(), f"No detailed lookdev found for character '{char_name}'.")
                lookdev_bible_context += f'<lookdev_for_character name="{char_name}">\n{char_lookdev_prompt}\n</lookdev_for_character>\n'
            # --- END OF CHANGES ---

            shot_list_chunk = ""
            for s in scene_shots:
                shot_details = [f"  - {key}: {value}" for key, value in s.items() if value and value.lower() != 'none']
                shot_list_chunk += f"- Shot: {s['SHOT']}\n" + "\n".join(shot_details) + "\n"

            director_template = read_prompt_file("stage1", prompt_director)
            director_prompt = director_template.format(lookdev_bible_context=lookdev_bible_context, shot_list_chunk=shot_list_chunk)
            
            director_output = llm_model.create_completion(prompt=director_prompt, max_tokens=kwargs.get('max_tokens', 4096), temperature=kwargs.get('temperature', 0.5),
                                                        top_p=kwargs.get('top_p', 0.95), top_k=kwargs.get('top_k', 40),
                                                        seed=kwargs.get('seed', 1234) if kwargs.get('seed', 1234) > 0 else -1, stop=["</response>"])
            choreography_text = director_output['choices'][0]['text'].strip()

            choreography_dict = {}
            shot_blocks = choreography_text.split('//---SHOT_START---//')
            for block in shot_blocks:
                if not block.strip(): continue
                shot_id_match = re.search(r'\*\*Shot[\s:]*([\w\d.-]+)\*\*', block, re.IGNORECASE)
                if shot_id_match:
                    shot_id = shot_id_match.group(1).strip()
                    choreography_dict[shot_id] = block.replace('//---SHOT_END---//', '').strip()

            print(f"[SceneChoreographer-v4.3] Stage 2 (Promptsmith): Generating final prompts...")
            shot_names_LIST, final_shot_prompts_LIST = [], []
            promptsmith_template = read_prompt_file("stage2", prompt_promptsmith)

            for shot_data in scene_shots:
                shot_id = shot_data.get("SHOT", "").strip()
                if not shot_id: continue
                shot_names_LIST.append(shot_id)
                narrative_choreography = choreography_dict.get(shot_id, f"Choreography not found for shot {shot_id}.")
                promptsmith_prompt = promptsmith_template.format(lookdev_bible_context=lookdev_bible_context,
                                                               narrative_choreography=narrative_choreography,
                                                               structured_shot_data=json.dumps(shot_data, indent=2))
                promptsmith_output = llm_model.create_completion(prompt=promptsmith_prompt, max_tokens=1024, temperature=0.4,
                                                               top_p=kwargs.get('top_p', 0.95), top_k=kwargs.get('top_k', 40),
                                                               seed=kwargs.get('seed', 1234) if kwargs.get('seed', 1234) > 0 else -1, stop=["</response>"])
                final_prompt = promptsmith_output['choices'][0]['text'].strip()
                final_shot_prompts_LIST.append(final_prompt)
            
            return (shot_names_LIST, final_shot_prompts_LIST, scene_location, choreography_text, len(shot_names_LIST))

        except Exception as e:
            traceback.print_exc()
            return error_tuple

NODE_CLASS_MAPPINGS = {"AISceneChoreographerBible-Akki": AISceneChoreographerBible_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AISceneChoreographerBible-Akki": "AI Scene Choreographer (Bible) v4.3 - Akki"}

# --- END OF FILE Akki_Scene_Choreographer_Bible.py ---