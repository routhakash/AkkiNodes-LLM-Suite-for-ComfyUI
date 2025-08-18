# Node: AI Cinematographer (Pro)
# Version: 3.9.0

import traceback
import re
from .shared_utils import report_token_usage

class AICinematographer_Akki:
    """
    The definitive director node. v3.9 represents the final, hardened
    architecture. It correctly delegates complex dialogue parsing to downstream
    nodes, introduces a "Factual Fidelity" protocol to prevent factual
    contradictions, and uses a deterministic Python helper to resolve
    unambiguous pronouns from the screenplay context.
    """
    DEFAULT_PROMPT_TEMPLATE = """<role>
You are an acclaimed, award-winning professional Cinematographer and Director. Your task is to translate the provided text of a single screenplay scene into a complete and actionable shot breakdown.
</role>
<block_format_mandate>
THIS IS YOUR MOST IMPORTANT INSTRUCTION. You MUST format your entire response as a series of self-contained shot blocks.
- Every shot block MUST begin with the exact line `//---SHOT_START---//`.
- Every shot block MUST end with the exact line `//---SHOT_END---//`.
- Inside each block, you will provide the data as a list of `KEY: Value` pairs, with each pair on its own line.
</block_format_mandate>
<auditory_event_protocol>
CRITICAL DATA RULE: A shot is a VISUAL instruction. If the screenplay text describes a VOICE OVER (V.O.), SOUND BRIDGE, or any other auditory event, you MUST create a compelling VISUAL shot to accompany it. The `SHOT_TYPE` field MUST contain a valid visual camera shot (e.g., WIDE SHOT, CLOSE UP). The `SHOT_TYPE` MUST NEVER be 'VOICE OVER', 'SOUND BRIDGE', 'FADE OUT', or any other non-visual term. The dialogue or sound cue itself should be placed in the appropriate `DIALOGUE` or `SFX` field.
</auditory_event_protocol>
<factual_fidelity_protocol>
CRITICAL DATA RULE: If the screenplay provides a specific factual detail about a character in an action line or parenthetical (e.g., an age like "(barely thirteen)" or "(50s)", a physical attribute like "(one-armed)", or a state like "(exhausted)"), you MUST faithfully reflect this canonical detail in the DESCRIPTION field of the most relevant shot where that detail is introduced or contextually important. Do not invent, alter, or omit these canonical facts.
</factual_fidelity_protocol>
<completeness_and_fidelity_mandate>
The screenplay is a checklist. You MUST generate a shot for EVERY piece of action, EVERY line of dialogue, and EVERY significant description. Do NOT summarize, consolidate, or omit any events from the source text.
</completeness_and_fidelity_mandate>
<character_naming_mandate>
CRITICAL DATA RULE: You MUST use character names *exactly* as they appear in the screenplay's action lines or dialogue blocks. DO NOT invent last names, first names, or alter the provided names in any way.
</character_naming_mandate>
<technical_realism_protocol>
Your choices must be technically plausible. A prime lens (e.g., "50mm Prime") has a FIXED focal length and CANNOT zoom. If you want to move the camera closer with a prime lens, you MUST describe the camera movement as a "Dolly In" or "Push-In."
</technical_realism_protocol>
<character_specific_asset_mandate>
For each character in the `CHARACTERS` list, you MUST provide a separate `PROPS (Character Name)` and `COSTUMES (Character Name)` field. These fields must contain a comma-separated list of keywords.
</character_specific_asset_mandate>
<output_format>
Inside each block, provide the following keys, each on its own line:
SHOT: [A single capital letter for the shot, e.g., A, B, C]
LOCATION: [The Full Location from the scene heading]
SET_DRESSING: [A comma-separated list of keywords for key background elements visible in THIS SHOT.]
SHOT_TYPE: [Select ONE from this specific list: WIDE SHOT, LONG SHOT, MEDIUM SHOT, MEDIUM CLOSE UP, CLOSE UP, EXTREME CLOSE UP, LOW ANGLE SHOT. Your choice MUST be logically consistent with the SHOT_FRAMING and DESCRIPTION.]
SHOT_FRAMING: [A literal, geometric description of the shot composition that is 100% consistent with the chosen SHOT_TYPE. No metaphors.]
Camera & Lens: [A specific, technically plausible choice.]
DESCRIPTION: [A concise, objective summary of the key action.]
Movement & Angle: [A specific, technically plausible choice.]
CHARACTERS: [A comma-separated list of keywords.]
PROPS (Character Name): [Keywords for Character 1's props.]
COSTUMES (Character Name): [Keywords for Character 1's costume.]
VFX: [A comma-separated list of keywords.]
Sound Design Cue: [Describe the overall auditory environment.]
SFX: [A comma-separated list of keywords.]
PERFORMANCE: [A brief, specific note for the actors.]
DIALOGUE: [The exact lines of dialogue spoken, including character name and parentheticals.]
Director's Rationale: [Justify your creative choices.]
</output_format>
<few_shot_example>
//---SHOT_START---//
SHOT: A
LOCATION: INT. SUMMIT OF MOUNT CINDER - DAY
SET_DRESSING: Vast cavern, Crystalline structures, Pulsing energy core, Rock floor
SHOT_TYPE: WIDE SHOT
SHOT_FRAMING: The camera reveals the entire cavern. It's immense, with cathedral-like rock formations.
Camera & Lens: ARRI Alexa 65 with a 28mm ARRI Prime DNA lens.
DESCRIPTION: Sia Volkov (15) and Kaelen (17) stand at the tunnel entrance, awestruck.
Movement & Angle: On a Technocrane, a slow, majestic crane-up and pull-back.
CHARACTERS: Sia Volkov, Kaelen
PROPS (Sia Volkov): None
COSTUMES (Sia Volkov): Practical travelling clothes, Dirt-stained boots
PROPS (Kaelen): Datapad
COSTUMES (Kaelen): Practical travelling clothes, Goggles
VFX: Ethereal glow, Pulsing light, Volumetric light shafts
Sound Design Cue: A sense of wonder. The low thrumming of the Core rises in volume.
SFX: Melodic hum, Low thrumming
PERFORMANCE: Jaws slack, eyes wide. A shared look of disbelief and triumph.
DIALOGUE: None.
Director's Rationale: This is the "reveal." The crane movement creates a sense of grandeur.
//---SHOT_END---//
</few_shot_example>
<final_instruction>
Now, perform this breakdown for the single scene text provided below. Follow all rules precisely.
</final_instruction>
<scene_to_break_down>
{current_scene_text}
</scene_to_break_down>
<response>
"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "screenplay": ("STRING", {"forceInput": True}),
                "temperature": ("FLOAT", {"default": 0.5, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1234}),
                "max_tokens": ("INT", {"default": 4096, "min": 1024, "max": 65536}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("shot_breakdown_report", "full_llm_prompt")
    FUNCTION = "generate_shot_list"
    CATEGORY = "AkkiNodes/Production"

    def _replace_shot_header(self, match, scene_num):
        shot_letter = match.group(1).upper()
        return f"SCENE: {scene_num}\nSHOT: {scene_num}{shot_letter}"

    def _get_characters_from_scene(self, scene_text):
        """Extracts unique, capitalized character names from scene text."""
        # This regex finds character dialogue headings (e.g., "BEN DUNCAN")
        heading_pattern = re.compile(r"^\s*([A-Z\s(V.O.)(CONT'D)]{2,})\s*$", re.MULTILINE)
        slugline_pattern = re.compile(r"^\s*(INT|EXT)\..*")
        
        canonical_names = set()
        for line in scene_text.splitlines():
            match = heading_pattern.match(line)
            if match and not slugline_pattern.match(line):
                name = re.sub(r'\s*\((V\.O\.|CONT\'D)\)\s*$', '', match.group(1).strip()).strip()
                canonical_names.add(name)
        return list(canonical_names)

    def _resolve_contextual_pronouns(self, breakdown_text, scene_text):
        """
        Deterministically resolves unambiguous pronouns in the CHARACTERS field
        using the context of the current scene.
        """
        scene_characters = self._get_characters_from_scene(scene_text)
        
        # Only proceed if the context is unambiguous (only one character in the scene)
        if len(scene_characters) != 1:
            return breakdown_text

        unambiguous_character = scene_characters[0]
        pronouns_to_check = {"he", "him", "his", "she", "her", "hers", "they", "them", "theirs"}

        corrected_blocks = []
        shot_blocks = breakdown_text.split('//---SHOT_START---//')
        for block in shot_blocks:
            if not block.strip(): continue
            
            rebuilt_block_lines = []
            was_corrected = False
            for line in block.splitlines():
                stripped_line = line.strip()
                if stripped_line.upper().startswith("CHARACTERS:"):
                    try:
                        key, value = stripped_line.split(":", 1)
                        value_clean = value.strip().lower()
                        if value_clean in pronouns_to_check:
                            rebuilt_block_lines.append(f"{key}: {unambiguous_character}")
                            was_corrected = True
                        else:
                            rebuilt_block_lines.append(line)
                    except ValueError:
                        rebuilt_block_lines.append(line)
                else:
                    rebuilt_block_lines.append(line)
            
            if was_corrected:
                print(f"    - Pronoun resolved in shot. Replaced with '{unambiguous_character}'")

            corrected_blocks.append("\n".join(rebuilt_block_lines))

        return "//---SHOT_START---//".join(corrected_blocks)


    def _normalize_character_names(self, breakdown_text, screenplay):
        # This function is being retained for now as per the lead programmer's analysis
        # of the AI QC Supervisor's dependency. It will be removed in a future refactor
        # of the entire pipeline.
        print("[AICinematographer-v3.9] Normalizing character names in breakdown (legacy pre-normalization for QC Supervisor)...")
        
        heading_pattern = re.compile(r"^\s*([A-Z\s(V.O.)(CONT'D)]{2,})\s*$", re.MULTILINE)
        slugline_pattern = re.compile(r"^\s*(INT|EXT)\..*")
        canonical_names = set()
        for line in screenplay.splitlines():
            match = heading_pattern.match(line)
            if match and not slugline_pattern.match(line):
                name = re.sub(r'\s*\((V\.O\.|CONT\'D)\)\s*$', '', match.group(1).strip()).strip()
                canonical_names.add(name)
        
        if not canonical_names:
            print("    - Warning: No canonical names found in screenplay. Skipping normalization.")
            return breakdown_text

        variation_map = {}
        for full_name in canonical_names:
            full_name_title = full_name.title()
            parts = full_name_title.split()
            if len(parts) > 0:
                variation_map[parts[0]] = full_name_title
                if len(parts) > 1:
                    variation_map[parts[-1]] = full_name_title

        if not variation_map: return breakdown_text
        
        corrected_lines = []
        for line in breakdown_text.splitlines():
            stripped_line = line.strip()
            
            if stripped_line.upper().startswith("CHARACTERS:"):
                key, values = stripped_line.split(":", 1)
                char_list = [c.strip() for c in values.split(',')]
                normalized_list = [variation_map.get(name, name) for name in char_list]
                corrected_lines.append(f"{key}: {', '.join(normalized_list)}")
                continue

            asset_match = re.match(r"(PROPS|COSTUMES)\s*\(([^)]+)\):(.*)", stripped_line, re.IGNORECASE)
            if asset_match:
                key_type = asset_match.group(1).upper()
                char_name = asset_match.group(2).strip()
                values = asset_match.group(3)
                normalized_char = variation_map.get(char_name, char_name)
                corrected_lines.append(f"{key_type} ({normalized_char}):{values}")
                continue

            corrected_lines.append(line)
        
        return "\n".join(corrected_lines)

    def generate_shot_list(self, llm_model, screenplay, temperature, top_p, top_k, seed, max_tokens):
        final_full_report = []
        full_llm_prompts_log = ""
        try:
            if not hasattr(llm_model, 'create_completion'):
                raise ValueError("LLM Model not provided or is invalid.")

            scene_anchor_pattern = re.compile(r"^\W*(?:\d+\.\s*)?(?:INT|EXT)\..*$", re.MULTILINE | re.IGNORECASE)
            anchors = list(scene_anchor_pattern.finditer(screenplay))
            if not anchors:
                raise ValueError("Could not split screenplay into scenes.")

            scenes = [screenplay[current.start():(anchors[i+1].start() if i + 1 < len(anchors) else len(screenplay))].strip() for i, current in enumerate(anchors)]
            
            print(f"[AICinematographer-Pro-v3.9] Found {len(scenes)} scenes to process.")

            for i, scene_text in enumerate(scenes):
                scene_num = i + 1
                print(f"[AICinematographer-Pro-v3.9] Processing Scene {scene_num}...")
                current_prompt = self.DEFAULT_PROMPT_TEMPLATE.format(current_scene_text=scene_text)
                full_llm_prompts_log += f"--- PROMPT FOR SCENE {scene_num} ---\n{current_prompt}\n\n"

                output = llm_model.create_completion(prompt=current_prompt, max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k, seed=seed if seed > 0 else -1, stop=["</response>"])
                report_token_usage(f"AICinematographer (Scene {scene_num})", output)
                creative_breakdown = output['choices'][0]['text'].strip()
                
                # --- Deterministic Python Processing Pipeline ---
                # Pass 1: Resolve unambiguous pronouns using scene context.
                pronoun_resolved_breakdown = self._resolve_contextual_pronouns(creative_breakdown, scene_text)

                # Pass 2: Legacy pre-normalization for AI QC Supervisor stability.
                normalized_breakdown = self._normalize_character_names(pronoun_resolved_breakdown, screenplay)

                if not normalized_breakdown.startswith("//---SHOT_START---//"):
                    normalized_breakdown = "//---SHOT_START---//" + normalized_breakdown
                shot_line_pattern = re.compile(r"SHOT:\s*([A-Z])", re.IGNORECASE)
                replacement_callback = lambda match: self._replace_shot_header(match, scene_num)
                corrected_breakdown = shot_line_pattern.sub(replacement_callback, normalized_breakdown)
                
                final_full_report.append(corrected_breakdown)

            shot_breakdown_report = "\n\n".join(final_full_report)
            print("[AICinematographer-Pro-v3.9] All scenes processed successfully.")

        except Exception as e:
            shot_breakdown_report = f"ERROR: An exception occurred. Check console.\n\nDetails: {e}"
            print(f"[AICinematographer-Pro-v3.9] Error:"); traceback.print_exc()

        return (shot_breakdown_report, full_llm_prompts_log)

NODE_CLASS_MAPPINGS = {"AICinematographer_Akki": AICinematographer_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AICinematographer_Akki": "AI Cinematographer (Pro) v3.9 - Akki"}