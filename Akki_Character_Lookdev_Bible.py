# --- START OF FILE Akki_Character_Lookdev_Bible.py ---

# Node: AI Character Lookdev (Bible) v13.0 (Final LLM Editor Test)

import traceback
import re
import os
import csv
from .shared_utils import report_token_usage, extract_tagged_content, get_wildcard_list

# --- HELPER FUNCTIONS for Self-Contained Prompt Loading ---
NODE_DIR = os.path.dirname(__file__)
PROMPTS_ROOT_DIR = os.path.join(NODE_DIR, "_prompts", "LookdevCHR")

def get_prompt_files_from_stage_dir(stage_folder):
    stage_dir = os.path.join(PROMPTS_ROOT_DIR, stage_folder)
    if not os.path.isdir(stage_dir):
        print(f"[CharacterLookdev-v13.0] Creating prompt directory: {stage_dir}")
        os.makedirs(stage_dir, exist_ok=True)
        placeholder_path = os.path.join(stage_dir, "placeholder.txt")
        if not os.path.exists(placeholder_path):
             with open(placeholder_path, 'w', encoding='utf-8') as f:
                f.write(f"Add your {stage_folder} prompt .txt files here.")
        return ["placeholder.txt"]
    try:
        files = [f for f in os.listdir(stage_dir) if f.endswith('.txt')]
        return files if files else ["No .txt files found"]
    except Exception as e:
        print(f"[CharacterLookdev-v13.0] Error scanning prompt directory {stage_dir}: {e}")
        return ["Error loading prompts"]

def read_prompt_file(stage_folder, filename):
    filepath = os.path.join(PROMPTS_ROOT_DIR, stage_folder, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
# --- END HELPER FUNCTIONS ---


class AICharacterLookdevBible_Akki:
    """
    AI Character Lookdev (Bible) v13.0. TEST-ONLY build. This version
    tests a 3-stage LLM pipeline where Stage 1 is a "Creative Artist",
    Stage 2 is a "Ruthless Editor", and Stage 3 is a "Technical Assembler".
    This is the final test of a purely LLM-based filtering and assembly pipeline.
    """

    @classmethod
    def INPUT_TYPES(cls):
        def create_combo_with_default(wildcard_file):
            try:
                wildcard_path = os.path.join(NODE_DIR, "wildcards", wildcard_file)
                if os.path.exists(wildcard_path):
                    with open(wildcard_path, 'r', encoding='utf-8') as f:
                        return ["Default (From Bible)"] + [line.strip() for line in f if line.strip()]
                else: return ["Default (From Bible)"]
            except Exception: return ["Default (From Bible)"]

        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "world_bible": ("STRING", {"forceInput": True}),
                "character_bible": ("STRING", {"forceInput": True}),
                "story_or_script": ("STRING", {"forceInput": True}),
                "shot_list_csv": ("STRING", {"forceInput": True}),
                "selected_character_name": ("STRING", {"forceInput": True}),
                "prompt_stage_1_artist": (get_prompt_files_from_stage_dir("stage1"),),
                "prompt_stage_2_editor": (get_prompt_files_from_stage_dir("stage2"),),
                "prompt_stage_3_assembler": (get_prompt_files_from_stage_dir("stage3"),),
                "debug_mode": (["Off", "Stage 1 (Artist) Only", "Stages 1+2 (Artist+Editor)"],),
                "temperature": ("FLOAT", {"default": 0.70, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1234}),
                "max_tokens": ("INT", {"default": 2048, "min": 256, "max": 16384}),
            },
            "optional": {
                "ethnicity": (create_combo_with_default("human_ethnicities.txt"),),
                "age_range": (create_combo_with_default("character_age_ranges.txt"),),
                "body_type": (create_combo_with_default("human_body_types.txt"),),
                "hair_color": (create_combo_with_default("human_hair_colors.txt"),),
                "hair_style": (create_combo_with_default("human_hair_styles.txt"),),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("character_prompt", "character_name", "full_llm_process_log")
    FUNCTION = "generate_lookdev"
    CATEGORY = "AkkiNodes/Visuals"

    def _extract_character_data_from_bible(self, character_bible, character_name):
        try:
            character_blocks = re.split(r'\s*//---CHARACTER_BREAK---//\s*|\s*(?=\nNAME:)', character_bible, re.IGNORECASE)
            target_block = None
            safe_char_name = re.escape(character_name)
            name_pattern = re.compile(rf"^\s*NAME:\s*{safe_char_name}\s*$", re.IGNORECASE | re.MULTILINE)
            for block in character_blocks:
                if block and name_pattern.search(block):
                    target_block = block
                    break
            if not target_block: return (f"ERROR: No data block found for '{character_name}'.", None)
            desc_match = re.search(r"DESCRIPTION:\s*([\s\S]*)", target_block, re.IGNORECASE)
            age_match = re.search(r"^AGE:\s*(.*)$", target_block, re.IGNORECASE | re.MULTILINE)
            description = desc_match.group(1).strip() if desc_match else f"ERROR: No DESCRIPTION found for '{character_name}'."
            age = age_match.group(1).strip() if age_match else None
            return (description, age)
        except Exception as e:
            return (f"ERROR: Failed to parse Character Bible for '{character_name}'. Details: {e}", None)

    def _discover_context(self, character_name, story_or_script, shot_list_csv):
        discovered_items, safe_char_name = [], re.escape(character_name)
        if story_or_script:
            story_pattern = re.compile(rf'((?:[^\n]+\n?){{0,2}}[^\n]*{safe_char_name}[^\n]*(?:\n[^\n]+){{0,2}})', re.IGNORECASE)
            for match in story_pattern.finditer(story_or_script):
                discovered_items.append(f"From Story: {match.group(1).strip().replace(chr(10), ' ')}")
        if shot_list_csv:
            try:
                reader = csv.DictReader(shot_list_csv.splitlines())
                for row in reader:
                    char_field, desc_field = row.get("CHARACTERS", ""), row.get("DESCRIPTION", "")
                    if re.search(safe_char_name, char_field, re.IGNORECASE) or re.search(safe_char_name, desc_field, re.IGNORECASE):
                        discovered_items.append(f'From Shot List: {desc_field.strip()}')
            except Exception as e: discovered_items.append(f"Notice: Could not parse Shot List CSV. Details: {e}")
        if not discovered_items: return "No specific story context found for this character."
        return "\n".join(f"- {item}" for item in discovered_items)

    def _enforce_canonical_age(self, prompt_text, canonical_age_string):
        if not canonical_age_string: return prompt_text
        age_tag_content = None
        precise_match = re.search(r'\b(\d{1,3})\b', canonical_age_string)
        if precise_match: age_tag_content = precise_match.group(1)
        else:
            range_match = re.search(r'\b(early|mid|late)?\s*-?\s*(\d{2})s\b', canonical_age_string, re.IGNORECASE)
            if range_match:
                modifier, decade = range_match.groups()
                age_tag_content = f"{modifier or ''} {decade}s".replace('  ',' ').strip()
        if not age_tag_content: return prompt_text
        age_tag = f"({age_tag_content})"
        paragraphs = prompt_text.split('\n\n')
        if len(paragraphs) < 2: return prompt_text
        physical_desc = paragraphs[1]
        age_related_terms_pattern = r'\b(early|mid|late|twenties|thirties|forties|fifties|sixties|seventies|eighties|nineties|\d+s|' \
                                    r'young|youthful|old|elderly|mature|middle-aged|teen|teenage|adult|child|boy|girl)\b,?\s*'
        physical_desc = re.sub(age_related_terms_pattern, '', physical_desc, flags=re.IGNORECASE)
        physical_desc = re.sub(r'^\s*,\s*', '', physical_desc).strip()
        physical_desc = re.sub(r'\s{2,}', ' ', physical_desc)
        paragraphs[1] = f"{age_tag}, {physical_desc}"
        return "\n\n".join(paragraphs)

    def generate_lookdev(self, llm_model, world_bible, character_bible, story_or_script, shot_list_csv, selected_character_name,
                         prompt_stage_1_artist, prompt_stage_2_editor, prompt_stage_3_assembler,
                         debug_mode, **kwargs):
        full_llm_process_log = ""
        try:
            if not hasattr(llm_model, 'create_completion'): raise ValueError("LLM Model invalid.")
            if not selected_character_name or "ERROR:" in selected_character_name or "N/A" in selected_character_name:
                 return (f"Invalid character: {selected_character_name}", selected_character_name, "")
            
            # --- STAGE 0: PYTHON PRE-PROCESSING ---
            print(f"[CharacterLookdev-v13.0] Stage 0: Parsing & Discovering Context...")
            base_description, canonical_age = self._extract_character_data_from_bible(character_bible, selected_character_name)
            discovered_context = self._discover_context(selected_character_name, story_or_script, shot_list_csv)
            
            # --- STAGE 1: THE ARTIST (LLM) ---
            print(f"[CharacterLookdev-v13.0] Stage 1 (Artist): Generating creative concept...")
            stage1_template = read_prompt_file("stage1", prompt_stage_1_artist)
            stage1_prompt = stage1_template.format(
                character_name=selected_character_name, 
                base_description=base_description, 
                discovered_context=discovered_context
            )
            stage1_output = llm_model.create_completion(prompt=stage1_prompt, max_tokens=2048, temperature=0.7)
            creative_concept_doc = stage1_output['choices'][0]['text'].strip()
            full_llm_process_log += f"--- STAGE 1: ARTIST (Creative Concept) ---\n{creative_concept_doc}\n\n"
            if debug_mode == "Stage 1 (Artist) Only": return (creative_concept_doc, selected_character_name, full_llm_process_log)

            # --- STAGE 2: THE EDITOR (LLM) ---
            print(f"[CharacterLookdev-v13.0] Stage 2 (Editor): Filtering to character-only prose...")
            stage2_template = read_prompt_file("stage2", prompt_stage_2_editor)
            stage2_prompt = stage2_template.format(llm_concept_document=creative_concept_doc)
            stage2_output = llm_model.create_completion(prompt=stage2_prompt, max_tokens=2048, temperature=0.4)
            edited_prose = stage2_output['choices'][0]['text'].strip()
            full_llm_process_log += f"--- STAGE 2: EDITOR (Filtered Prose) ---\n{edited_prose}\n\n"
            if debug_mode == "Stages 1+2 (Artist+Editor)": return (edited_prose, selected_character_name, full_llm_process_log)

            # --- STAGE 3: THE ASSEMBLER (LLM) ---
            print(f"[CharacterLookdev-v13.0] Stage 3 (Assembler): Formatting final prompt...")
            stage3_template = read_prompt_file("stage3", prompt_stage_3_assembler)
            stage3_prompt = stage3_template.format(augmented_description=edited_prose) # Re-using `augmented_description` key
            stage3_output = llm_model.create_completion(prompt=stage3_prompt, max_tokens=2048, temperature=0.2)
            raw_creative_prompt = stage3_output['choices'][0]['text'].strip()
            full_llm_process_log += f"--- STAGE 3: ASSEMBLER (Raw Prompt) ---\n{raw_creative_prompt}\n\n"

            # --- STAGE 4: FINAL POLISH (Python) ---
            print(f"[CharacterLookdev-v13.0] Stage 4 (Python): Enforcing canonical age...")
            final_character_prompt = self._enforce_canonical_age(raw_creative_prompt, canonical_age)
            full_llm_process_log += f"--- STAGE 4: FINAL POLISH ---\n{final_character_prompt}\n\n"

        except Exception as e:
            final_character_prompt = f"ERROR: An exception occurred in v13.0. Check console.\n\nDetails: {e}"
            print(f"[CharacterLookdev-v13.0] Error:"); traceback.print_exc()

        return (final_character_prompt, selected_character_name, full_llm_process_log)


NODE_CLASS_MAPPINGS = {"AICharacterLookdevBible-Akki": AICharacterLookdevBible_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AICharacterLookdevBible-Akki": "AI Character Lookdev (Bible) v13.0 - Akki"}

# --- END OF FILE Akki_Character_Lookdev_Bible.py ---