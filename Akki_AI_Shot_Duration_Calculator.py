# Node: AI Shot Duration Calculator v1.6 (List Output Refactor)

import os
import traceback
import csv
import io
import re
from .shared_utils import report_token_usage

# --- CONSTANTS ---
NODE_DIR = os.path.dirname(__file__)
PROMPTS_ROOT_DIR = os.path.join(NODE_DIR, "_prompts", "Duration")

# --- HELPER FUNCTIONS ---
def get_prompt_files_from_dir():
    """Scans the node's prompts directory and returns a list of .txt files."""
    if not os.path.isdir(PROMPTS_ROOT_DIR):
        print(f"[AIShotDurationCalculator] Creating prompt directory: {PROMPTS_ROOT_DIR}")
        os.makedirs(PROMPTS_ROOT_DIR, exist_ok=True)
        placeholder_path = os.path.join(PROMPTS_ROOT_DIR, "placeholder_prompt.txt")
        if not os.path.exists(placeholder_path):
             with open(placeholder_path, 'w', encoding='utf-8') as f:
                f.write("Add your duration calculation prompt .txt files here.")
        return ["placeholder_prompt.txt"]
    try:
        files = [f for f in os.listdir(PROMPTS_ROOT_DIR) if f.endswith('.txt')]
        return sorted(files) if files else ["No .txt prompts found"]
    except Exception as e:
        print(f"[AIShotDurationCalculator] Error scanning prompt directory {PROMPTS_ROOT_DIR}: {e}")
        return ["Error loading prompts"]

def read_prompt_file(filename):
    """Reads the content of a specific prompt file."""
    filepath = os.path.join(PROMPTS_ROOT_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
# --- END HELPER FUNCTIONS ---


class AIShotDurationCalculator_Akki:
    """
    An AI agent that analyzes a production CSV to estimate shot durations.
    v1.6 refactors the output to provide synchronized lists of shot names and
    durations for downstream automation, replacing the CSV string output.
    """
    
    PRIMARY_KEYS = {
        'SHOT': ['SHOT'],
        'SHOT_FRAMING': ['SHOT_FRAMING', 'SHOT FRAMING'],
        'DESCRIPTION': ['DESCRIPTION'],
        'MOVEMENT_ANGLE': ['Movement & Angle', 'Movement/Angle'],
        'DIALOGUE': ['DIALOGUE'],
        'DIRECTOR_RATIONALE': ["Director's Rationale", "Director’s Rationale", "Director's Rationale"]
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "csv_report": ("STRING", {"forceInput": True}),
                "shot_index": ("INT", {"default": 1, "min": 1, "step": 1}),
                "prompt_selector": (get_prompt_files_from_dir(),),
                "temperature": ("FLOAT", {"default": 0.4, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1234}),
                "max_tokens": ("INT", {"default": 2048, "min": 64, "max": 8192}),
            }
        }

    # SURGICAL CHANGE v1.6: Refactored outputs to use lists
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("durations_text_report", "shot_names_LIST", "durations_LIST", "SEL_duration", "full_llm_process_log")
    FUNCTION = "calculate_durations"
    CATEGORY = "AkkiNodes/Production"
    
    OUTPUT_IS_LIST = (False, True, True, False, False)

    def _get_value_from_row(self, row, key_aliases):
        """A resilient, case-insensitive getter for CSV row data."""
        actual_key = next((k for k in row.keys() for alias in key_aliases if k.strip().lower() == alias.lower()), None)
        if actual_key and row[actual_key]:
            return row[actual_key].strip()
        return "N/A"

    def calculate_durations(self, llm_model, csv_report, shot_index, prompt_selector, temperature, top_p, top_k, seed, max_tokens):
        # Initialize outputs
        durations_text_report = "ERROR: Processing failed."
        shot_names_LIST = []
        durations_LIST = []
        sel_duration = "0"
        full_llm_process_log = ""
        
        try:
            # --- VALIDATION (Unchanged) ---
            if not csv_report or csv_report.strip().startswith("ERROR:"):
                raise ValueError("Invalid or empty CSV report provided.")
            if not hasattr(llm_model, 'create_completion'):
                raise ValueError("LLM Model not provided or is invalid.")

            prompt_template = read_prompt_file(prompt_selector)
            
            # --- DATA PREPARATION (Unchanged) ---
            csv_file = io.StringIO(csv_report)
            all_rows = list(csv.DictReader(csv_file))
            if not all_rows:
                raise ValueError("CSV report contains no data.")

            all_shot_data_blocks = []
            for row in all_rows:
                shot_id = self._get_value_from_row(row, self.PRIMARY_KEYS['SHOT'])
                if shot_id == "N/A": continue

                data_block = [f"--- DATA FOR SHOT: {shot_id} ---"]
                data_block.append(f"SHOT_FRAMING: {self._get_value_from_row(row, self.PRIMARY_KEYS['SHOT_FRAMING'])}")
                data_block.append(f"DESCRIPTION: {self._get_value_from_row(row, self.PRIMARY_KEYS['DESCRIPTION'])}")
                data_block.append(f"MOVEMENT_ANGLE: {self._get_value_from_row(row, self.PRIMARY_KEYS['MOVEMENT_ANGLE'])}")
                data_block.append(f"DIALOGUE: {self._get_value_from_row(row, self.PRIMARY_KEYS['DIALOGUE'])}")
                data_block.append(f"DIRECTOR_RATIONALE: {self._get_value_from_row(row, self.PRIMARY_KEYS['DIRECTOR_RATIONALE'])}")
                all_shot_data_blocks.append("\n".join(data_block))

            if not all_shot_data_blocks:
                raise ValueError("CSV was parsed, but no valid shots were found to process.")

            # --- LLM CALL (Unchanged) ---
            full_data_payload = "\n\n".join(all_shot_data_blocks)
            final_prompt = prompt_template.format(shot_data_blocks=full_data_payload)
            
            output = llm_model.create_completion(prompt=final_prompt, max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k, seed=seed if seed > 0 else -1)
            raw_ai_text = output['choices'][0]['text'].strip()
            full_llm_process_log = f"--- FULL PROMPT SENT TO LLM ---\n{final_prompt}\n\n--- RAW LLM RESPONSE ---\n{raw_ai_text}"

            # --- PARSING AND OUTPUT GENERATION (Refactored for Lists) ---
            sanitized_lines = [line.strip() for line in raw_ai_text.splitlines() if ':' in line and any(char.isdigit() for char in line)]
            
            parser_regex = re.compile(r"(\S+):\s*(\d+)")
            matches = []
            for line in sanitized_lines:
                match = parser_regex.search(line)
                if match:
                    matches.append(match.groups())

            if not matches:
                raise ValueError("AI response was received but could not be parsed into duration pairs.")

            # Unpack the list of tuples into two synchronized lists
            shot_names_LIST = [item[0] for item in matches]
            durations_LIST = [item[1] for item in matches]

            durations_text_report = "\n".join([f"{name}: {duration}s" for name, duration in zip(shot_names_LIST, durations_LIST)])

            # Logic for single selected duration
            target_index = shot_index - 1
            if 0 <= target_index < len(all_rows):
                target_shot_id = self._get_value_from_row(all_rows[target_index], self.PRIMARY_KEYS['SHOT'])
                try:
                    # Find the index of the shot_id in our new list to get the corresponding duration
                    found_index = shot_names_LIST.index(target_shot_id)
                    sel_duration = durations_LIST[found_index]
                except ValueError:
                    sel_duration = "0" # Shot from CSV not found in AI output
            else:
                sel_duration = "0" # Index out of bounds

        except Exception as e:
            traceback.print_exc()
            error_message = f"ERROR: {e}"
            durations_text_report = error_message
            full_llm_process_log += f"\n\n--- PROCESSING ERROR ---\n{traceback.format_exc()}"

        return (durations_text_report, shot_names_LIST, durations_LIST, sel_duration, full_llm_process_log)

# --- Node Mappings ---
NODE_CLASS_MAPPINGS = {
    "AIShotDurationCalculator-Akki": AIShotDurationCalculator_Akki
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "AIShotDurationCalculator-Akki": "AI Shot Duration Calculator - Akki"
}