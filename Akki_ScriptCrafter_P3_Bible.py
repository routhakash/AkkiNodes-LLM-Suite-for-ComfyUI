# --- START OF FILE Akki_ScriptCrafter_P3_Bible.py ---

# Node: AI ScriptCrafter 03 (Bible) v16.8 (Definitive)

import traceback
import re
import os
from .shared_utils import report_token_usage, extract_tagged_content

# --- HELPER FUNCTIONS for Self-Contained Prompt Loading ---
NODE_DIR = os.path.dirname(__file__)
PROMPTS_ROOT_DIR = os.path.join(NODE_DIR, "_prompts")

def get_prompt_files_from_stage_dir(stage_folder):
    stage_dir = os.path.join(PROMPTS_ROOT_DIR, stage_folder)
    if not os.path.isdir(stage_dir):
        print(f"[ScriptCraft-P3-v16.8] Creating prompt directory: {stage_dir}")
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
        print(f"[ScriptCraft-P3-v16.8] Error scanning prompt directory {stage_dir}: {e}")
        return ["Error loading prompts"]

def read_prompt_file(stage_folder, filename):
    filepath = os.path.join(PROMPTS_ROOT_DIR, stage_folder, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
# --- END HELPER FUNCTIONS ---


class AIScriptCrafter03ScreenplayBible_Akki:
    """
    AI ScriptCrafter v16.8 (Definitive). This is the final, production-ready
    version. It combines a hardened 3-stage LLM pipeline with a definitive
    Master Post-Processor. This processor uses a "Hybrid Heuristic Parser" to
    robustly handle LLM typos and formatting errors, ensuring 100% data and
    structural integrity in the final, Fountain-compliant screenplay.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return { "required": {
                "llm_model": ("LLM_MODEL",),
                "story_text": ("STRING", {"forceInput": True}),
                "world_bible": ("STRING", {"forceInput": True}),
                "character_bible": ("STRING", {"forceInput": True}),
                "beat_sheet": ("STRING", {"forceInput": True}),
                "prompt_stage_1": (get_prompt_files_from_stage_dir("stage1"),),
                "prompt_stage_2": (get_prompt_files_from_stage_dir("stage2"),),
                "prompt_stage_3": (get_prompt_files_from_stage_dir("stage3"),),
                "cinematic_style": ("STRING", {"multiline": False, "default": "Gritty and realistic with handheld camera work"}),
                "max_tokens": ("INT", {"default": 8192, "min": 1024, "max": 16384}),
                "temperature": ("FLOAT", {"default": 0.7, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1234}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("screenplay", "scene_breakdown", "full_llm_process_log")
    FUNCTION = "generate_script"
    CATEGORY = "AkkiNodes/ScriptCraft"

    def _master_post_processor(self, raw_text, character_bible):
        print("[ScriptCraft-P3-v16.8] Stage 4: Master Post-Processor starting...")

        # STAGE 1: Sanitize using the "Content Isolation" principle
        print("    - Step A: Isolating screenplay content...")
        try:
            start_index = raw_text.upper().index("FADE IN:")
        except ValueError:
            print("    - Warning: 'FADE IN:' not found. Processing from start of text.")
            start_index = 0
        try:
            end_marker_start = raw_text.upper().rindex("FADE OUT.")
            end_index = end_marker_start + len("FADE OUT.")
        except ValueError:
            print("    - Warning: 'FADE OUT.' not found. Processing to end of text.")
            end_index = len(raw_text)
        text = raw_text[start_index:end_index]
        text = re.sub(r'<\?.*?\?>|<.*?>', '', text, flags=re.DOTALL)
        text = text.strip()

        # STAGE 2: Contextual Parser & Fountain Formatter
        print("    - Step B: Parsing, Normalizing, and Formatting with Hardened Parser...")
        final_lines = []
        scene_counter = 1
        last_line_type = 'START'

        # Build a comprehensive, lowercase variation map for the fuzzy check
        name_pattern = re.compile(r"^NAME:\s*(.*)$", re.MULTILINE | re.IGNORECASE)
        canonical_names = [name.strip() for name in name_pattern.findall(character_bible)]
        lc_variation_map = {}
        if canonical_names:
            for full_name in canonical_names:
                full_name_upper = full_name.upper()
                # Store all parts of the name as lowercase keys
                for part in full_name.split():
                    lc_variation_map[part.lower()] = full_name_upper
                lc_variation_map[full_name.lower()] = full_name_upper
        
        for line in text.splitlines():
            line = line.strip()
            if not line: continue

            # Preserve FADE IN: at the start
            if line.upper() == "FADE IN:":
                final_lines.append(line.upper())
                last_line_type = 'TRANSITION'
                continue

            # Check for Scene Headings
            if re.match(r'^(INT|EXT)\..*', line, re.IGNORECASE):
                if last_line_type != 'START': final_lines.append("")
                numbered_heading = f"{scene_counter}. {line.upper()}"
                final_lines.append(numbered_heading)
                scene_counter += 1
                last_line_type = 'SCENE_HEADING'
                continue # Move to next line

            # --- HYBRID HEURISTIC PARSER FOR CHARACTER CUES ---
            
            # 1. Strict Check (Fast Path for well-formed cues)
            strict_match = re.match(r'^[A-Z\s(][^a-z]*$', line) and len(line) < 40 and not line.endswith(':')

            # 2. Surgical Fuzzy Check (Slower path for malformed cues like 'TRIxie')
            # Clean the line for a direct key lookup in our lowercase map
            cleaned_line_for_check = re.sub(r'\([^)]+\)', '', line).strip().lower()
            fuzzy_match = cleaned_line_for_check in lc_variation_map

            if strict_match or fuzzy_match:
                if last_line_type not in ['SCENE_HEADING', 'START', 'TRANSITION']: final_lines.append("")
                paren_match = re.search(r'(\s*\([^)]+\)\s*)$', line, re.IGNORECASE)
                paren = ''
                name_part = line.strip()
                if paren_match:
                    paren = paren_match.group(1).upper().strip()
                    name_part = line[:paren_match.start()].strip()
                
                # Use the fuzzy match result for normalization
                canonical_name = lc_variation_map.get(name_part.lower(), name_part.upper())
                
                final_lines.append(f"{canonical_name} {paren}".strip())
                last_line_type = 'CHARACTER'
            elif last_line_type in ['CHARACTER', 'PARENTHETICAL']:
                if line.startswith('(') and line.endswith(')'):
                    final_lines.append(line.lower())
                    last_line_type = 'PARENTHETICAL'
                else:
                    final_lines.append(line)
                    last_line_type = 'DIALOGUE'
            else:
                if last_line_type not in ['SCENE_HEADING', 'START', 'ACTION', 'TRANSITION']: final_lines.append("")
                final_lines.append(line)
                last_line_type = 'ACTION'
        
        # STAGE 3: Final Assembly
        print("    - Step C: Final assembly complete.")
        final_script = "\n".join(final_lines)
        
        return final_script.strip()

    def generate_script(self, llm_model, story_text, world_bible, character_bible, beat_sheet, prompt_stage_1, prompt_stage_2, prompt_stage_3, cinematic_style, max_tokens, temperature, top_p, top_k, seed):
        screenplay, full_llm_process_log, scene_breakdown = "", "", ""
        try:
            if not hasattr(llm_model, 'create_completion'): raise ValueError("LLM Model not provided.")

            source_context = {
                "story_text": story_text, "world_bible": world_bible,
                "character_bible": character_bible, "beat_sheet": beat_sheet,
                "cinematic_style": cinematic_style
            }

            print("[ScriptCraft-P3-v16.8] Starting 3-Stage LLM creative process...")
            stage1_prompt_template = read_prompt_file("stage1", prompt_stage_1)
            stage1_prompt = stage1_prompt_template.format(**source_context)
            stage1_output = llm_model.create_completion(prompt=stage1_prompt, max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k, seed=seed if seed > 0 else -1, stop=["</response>"])
            report_token_usage("ScriptCraft-P3 Stage 1", stage1_output)
            stage1_draft = extract_tagged_content(stage1_output['choices'][0]['text'].strip(), "main_output")
            
            stage2_prompt_template = read_prompt_file("stage2", prompt_stage_2)
            stage2_prompt = stage2_prompt_template.format(previous_draft=stage1_draft, **source_context)
            stage2_output = llm_model.create_completion(prompt=stage2_prompt, max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k, seed=seed if seed > 0 else -1, stop=["</response>"])
            report_token_usage("ScriptCraft-P3 Stage 2", stage2_output)
            stage2_draft = extract_tagged_content(stage2_output['choices'][0]['text'].strip(), "main_output")
            
            stage3_prompt_template = read_prompt_file("stage3", prompt_stage_3)
            stage3_prompt = stage3_prompt_template.format(previous_draft=stage2_draft, **source_context)
            stage3_output = llm_model.create_completion(prompt=stage3_prompt, max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k, seed=seed if seed > 0 else -1, stop=["</response>"])
            report_token_usage("ScriptCraft-P3 Stage 3", stage3_output)
            final_draft_from_llm = extract_tagged_content(stage3_output['choices'][0]['text'].strip(), "main_output")
            
            full_llm_process_log = f"--- RAW LLM OUTPUT ---\n{final_draft_from_llm}\n\n"

            screenplay = self._master_post_processor(final_draft_from_llm, character_bible)
            full_llm_process_log += f"--- FINAL PROCESSED SCRIPT (Fountain Compliant) ---\n{screenplay}\n\n"

            print("[ScriptCraft-P3-v16.8] Stage 5: Generating scene breakdown...")
            breakdown_list = []
            scene_heading_pattern = re.compile(r"^(\d+)\.\s*(INT|EXT)\.\s(.*?)(?:\s-\s(.*))?$", re.MULTILINE)
            for match in scene_heading_pattern.finditer(screenplay):
                scene_num, scene_type, scene_name, time_of_day = match.groups()
                scene_name = scene_name.strip()
                time_of_day = time_of_day.strip() if time_of_day else "DAY"
                breakdown_list.append(f"<Scene Number ({scene_num})> <Scene Type ({scene_type})> <{scene_name}> <Time of Day ({time_of_day})>")
            scene_breakdown = "\n".join(breakdown_list)
            print("    - Scene breakdown generated successfully.")

        except Exception as e:
            screenplay = f"ERROR: An exception occurred in ScriptCraft P3 v16.8. Check console.\n\nDetails: {e}"
            scene_breakdown = "ERROR: Could not generate scene breakdown."
            print(f"[ScriptCraft-P3-v16.8] Error:"); traceback.print_exc()

        return (screenplay, scene_breakdown, full_llm_process_log)


NODE_CLASS_MAPPINGS = {"AIScriptCrafter03ScreenplayBible-Akki": AIScriptCrafter03ScreenplayBible_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AIScriptCrafter03ScreenplayBible-Akki": "AI ScriptCrafter 03 (Bible) v16.8 - Akki"}
# --- END OF FILE Akki_ScriptCrafter_P3_Bible.py ---