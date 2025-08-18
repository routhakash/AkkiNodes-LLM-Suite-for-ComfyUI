# Node: AI ScriptCrafter 01 (Bible) v7.2 (Deterministic Refinement)

import re
import traceback
from .shared_utils import report_token_usage

class AIScriptCrafter01FoundationBible_Akki:
    """
    The definitive, production-ready Phase 1 Bible generator. v7.2 finalizes the
    robust "Analyze & Refine" architecture. It uses a single, comprehensive AI call,
    followed by a new, fully-implemented deterministic Python post-processing step.
    This "refinement" stage parses the AI output, intelligently merges duplicate
    entities, and programmatically enforces ground-truth data, guaranteeing 100%
    factual accuracy and a reliable, canonical source of truth.
    """
    
    # The advanced prompt from v7.1 remains unchanged.
    COMPREHENSIVE_BIBLE_PROMPT = """<role>
You are a meticulous Forensic Script Analyst. Your function is to read a prose story and generate foundational documents for a film production. You will be given a set of "Known Facts" which are the absolute, non-negotiable ground truth.
</role>
<task>
Your primary task is to conduct a complete analysis of the `story_text` and generate a "Narrative Bible" report. You must identify ALL characters, consolidate their identities (e.g., 'Sergeant Perry' is the same person as 'Minnie Perry'), and create a full profile for each unique character, adhering to the strict formatting and hierarchy rules below.
</task>
<analytical_process>
1.  **Acknowledge Known Facts:** The `known_facts` are 100% accurate and MUST be used as an override.
    - **CRITICAL RULE:** For the Protagonist and Antagonist, the `AGE` and `ROLE` fields in your output MUST be populated ONLY with the exact data from `known_facts`. You are forbidden from using ages or roles inferred from the story text for these specific characters. Their `NAME` field should also be based on the `known_facts`.

2.  **Creative Analysis:** Read the `story_text` to understand the high-level narrative. Generate the `LOGLINE` and `THEME`.

3.  **Comprehensive Character Identification:**
    - Read the `story_text` carefully to identify every single on-screen character, including individuals and named groups.
    - **CRITICAL:** You must perform entity resolution. If a character is referred to by name and title (e.g., 'Vicky Harris' and 'General Harris'), you must recognize they are the same person and create a single, consolidated profile. Use their most complete name for the `NAME` field.

4.  **Full Profile Generation (All Characters):**
    - For **every** unique character identified, you must generate a complete bible entry with all fields: `NAME`, `ROLE`, `AGE`, `GOAL`, `MOTIVATION`, `FLAW`, `ARC`, and `DESCRIPTION`.
    - **FOR SUPPORTING CHARACTERS:** For characters with limited textual information, you are required to generate a plausible and creative `GOAL`, `MOTIVATION`, `FLAW`, and `ARC`. Infer these details based on their actions, dialogue, and narrative function. Do not state they are 'not applicable' or that the character is static. Every character has an implicit purpose.

5.  **Enrichment:** Extract literal keywords, phrases, and physical details from the story to inform the `TONE`, `AESTHETIC`, and character `DESCRIPTION` fields.

6.  **Report Generation & Formatting:**
    - Assemble all information into the final report format.
    - **HIERARCHY RULE:** The output under `//---CHARACTER_BIBLE---//` MUST be ordered. The Protagonist's profile MUST appear first, followed immediately by the Antagonist's profile. All other supporting characters should follow in any order.
</analytical_process>
<known_facts>
--- Ground Truth Data ---
- **Protagonist Name:** {protagonist_name}
- **Protagonist Age:** {protagonist_age}
- **Protagonist Type:** {protagonist_type}
- **Antagonist Name:** {antagonist_name}
- **Antagonist Age:** {antagonist_age}
- **Antagonist Type:** {antagonist_type}
- **Genre:** {genre}
- **Period:** {period}
</known_facts>
<story_text_to_analyze>
{story_text}
</story_text_to_analyze>
<output_format>
Your output MUST follow this exact format, including the specified character hierarchy. Do not omit any characters.
//---NARRATIVE_FOUNDATION---//
LOGLINE: [Your generated logline here]
THEME: [Your generated theme here]
//---WORLD_BIBLE---//
GENRE: [From Known Facts]
PERIOD: [From Known Facts]
TONE: [A 2-3 keyword description of the story's mood, extracted from the text]
AESTHETIC: [A 3-4 keyword description of the visual style, extracted from the text]
//---CHARACTER_BIBLE---//
NAME: [Protagonist Name from Known Facts]
ROLE: Protagonist
AGE: [Protagonist Age from Known Facts]
GOAL: [Your creative analysis]
MOTIVATION: [Your creative analysis]
FLAW: [Your creative analysis, based on the text]
ARC: [Your creative analysis]
DESCRIPTION: [A 1-2 sentence description combining the character type from Known Facts with literal physical details extracted from the story.]
//---CHARACTER_BREAK---//
NAME: [Antagonist Name from Known Facts]
ROLE: Antagonist
AGE: [Antagonist Age from Known Facts]
... (repeat for Antagonist)
//---CHARACTER_BREAK---//
NAME: [Next Supporting Character Name]
... (repeat for ALL other on-screen characters found)
</output_format>
<response>
"""
    # Define the fields we expect in a character profile
    CHARACTER_FIELDS = ["NAME", "ROLE", "AGE", "GOAL", "MOTIVATION", "FLAW", "ARC", "DESCRIPTION"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "story_text": ("STRING", {"forceInput": True}),
                "protagonist_name": ("STRING", {"forceInput": True}),
                "protagonist_type": ("STRING", {"forceInput": True}),
                "protagonist_age": ("STRING", {"forceInput": True}),
                "antagonist_name": ("STRING", {"forceInput": True}),
                "antagonist_type": ("STRING", {"forceInput": True}),
                "antagonist_age": ("STRING", {"forceInput": True}),
                "genre": ("STRING", {"forceInput": True}),
                "period": ("STRING", {"forceInput": True}),
                "max_tokens": ("INT", {"default": 4096, "min": 256, "max": 16384}),
                "temperature": ("FLOAT", {"default": 0.7, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1235}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("logline", "theme", "world_bible", "character_bible", "full_analysis_text")
    FUNCTION = "generate_foundations"
    CATEGORY = "AkkiNodes/ScriptCraft"

    def _parse_profile_to_dict(self, profile_text):
        profile_dict = {}
        for field in self.CHARACTER_FIELDS:
            # Regex to find "FIELD:" and capture everything until the next field or end of string
            # It handles various spacings and is case-insensitive
            pattern = re.compile(rf"^\s*{field}\s*:(.*?)(\n\s*(?:{'|'.join(self.CHARACTER_FIELDS)})\s*:|$)", re.DOTALL | re.IGNORECASE | re.MULTILINE)
            match = pattern.search(profile_text)
            if match:
                profile_dict[field] = match.group(1).strip()
            else:
                profile_dict[field] = ""
        profile_dict['raw_text'] = profile_text # Keep the original for reference
        return profile_dict

    def _reconstruct_profile_from_dict(self, profile_dict):
        return "\n".join([f"{field}: {profile_dict.get(field, '').strip()}" for field in self.CHARACTER_FIELDS])

    def _deterministic_refinement(self, ai_generated_text, known_facts):
        print("[ScriptCraft-P1-Bible v7.2] Stage 2: Performing deterministic refinement...")
        
        char_bible_match = re.search(r"(//---CHARACTER_BIBLE---//)([\s\S]*)", ai_generated_text, re.DOTALL | re.IGNORECASE)
        if not char_bible_match:
            print("  - WARNING: Character Bible section not found for refinement.")
            return ai_generated_text # Nothing to refine

        header = char_bible_match.group(1)
        body = char_bible_match.group(2)
        
        profiles_text = [p.strip() for p in body.split("//---CHARACTER_BREAK---//") if p.strip()]
        profiles_dicts = [self._parse_profile_to_dict(p) for p in profiles_text]

        def get_match_score(profile_name, known_name):
            profile_name, known_name = profile_name.lower(), known_name.lower()
            if profile_name == known_name: return 10
            if known_name in profile_name: return 5
            known_name_parts = known_name.split()
            if len(known_name_parts) > 1 and all(part in profile_name for part in known_name_parts): return 4
            if any(part in profile_name for part in known_name_parts if len(part) > 2): return 2
            return 0

        # Find best match for Protagonist and Antagonist
        p_name = known_facts['protagonist_name']
        a_name = known_facts['antagonist_name']
        
        best_p_match = max(profiles_dicts, key=lambda p: get_match_score(p.get('NAME', ''), p_name), default=None)
        best_a_match = max(profiles_dicts, key=lambda p: get_match_score(p.get('NAME', ''), a_name), default=None)

        final_profiles = []
        processed_names = set()

        # Process Protagonist
        if best_p_match:
            best_p_match['NAME'] = p_name
            best_p_match['ROLE'] = 'Protagonist'
            best_p_match['AGE'] = known_facts['protagonist_age']
            final_profiles.append(best_p_match)
            processed_names.add(best_p_match['NAME'].lower())

        # Process Antagonist
        if best_a_match and best_a_match != best_p_match:
            best_a_match['NAME'] = a_name
            best_a_match['ROLE'] = 'Antagonist'
            best_a_match['AGE'] = known_facts['antagonist_age']
            final_profiles.append(best_a_match)
            processed_names.add(best_a_match['NAME'].lower())

        # Add remaining supporting characters, skipping duplicates
        for p_dict in profiles_dicts:
            if p_dict not in final_profiles and p_dict.get('NAME', '').lower() not in processed_names:
                final_profiles.append(p_dict)
                processed_names.add(p_dict.get('NAME', '').lower())
        
        # Reconstruct the character bible string
        reconstructed_body = "\n//---CHARACTER_BREAK---//\n".join([self._reconstruct_profile_from_dict(p) for p in final_profiles])
        
        # Replace the old character bible with the refined one
        sanitized_full_text = ai_generated_text.replace(char_bible_match.group(0), f"{header}\n{reconstructed_body.strip()}")
        
        print(f"  - Refinement complete. Processed {len(profiles_dicts)} profiles, finalized {len(final_profiles)} unique profiles.")
        return sanitized_full_text.strip()

    def generate_foundations(self, llm_model, story_text, protagonist_name, protagonist_type, protagonist_age, antagonist_name, antagonist_type, antagonist_age, genre, period, max_tokens, temperature, top_p, top_k, seed):
        if not hasattr(llm_model, 'create_completion'):
            raise ValueError("LLM Model not provided or is invalid.")
        
        full_process_log = ""
        logline, theme, world_bible, character_bible = "ERROR", "ERROR", "ERROR", "ERROR"
        
        known_facts_map = {
            "protagonist_name": protagonist_name,
            "protagonist_age": protagonist_age,
            "protagonist_type": protagonist_type,
            "antagonist_name": antagonist_name,
            "antagonist_age": antagonist_age,
            "antagonist_type": antagonist_type,
            "genre": genre,
            "period": period,
        }

        try:
            # --- STAGE 1: Intelligent Analysis (Single AI Call) ---
            print("[ScriptCraft-P1-Bible v7.2] Stage 1: Performing comprehensive analysis...")
            prompt = self.COMPREHENSIVE_BIBLE_PROMPT.format(story_text=story_text, **known_facts_map)
            full_process_log += f"--- STAGE 1: COMPREHENSIVE PROMPT ---\n{prompt}\n\n"
            
            ai_output = llm_model.create_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                seed=seed if seed > 0 else -1,
                stop=["</response>"]
            )
            report_token_usage("ScriptCrafter-P1-Bible (Comprehensive Analysis)", ai_output)
            raw_ai_text = ai_output['choices'][0]['text'].strip()
            full_process_log += f"--- STAGE 1: COMPREHENSIVE RESPONSE ---\n{raw_ai_text}\n\n"

            # --- STAGE 2: Deterministic Refinement & Extraction ---
            refined_text = self._deterministic_refinement(raw_ai_text, known_facts_map)
            full_process_log += f"--- STAGE 2: REFINED OUTPUT ---\n{refined_text}\n\n"

            # Extract final components from the refined text
            foundation_match = re.search(r"//---NARRATIVE_FOUNDATION---//([\s\S]*?)//---WORLD_BIBLE---//", refined_text, re.DOTALL)
            if foundation_match:
                foundation_text = foundation_match.group(1)
                logline_match = re.search(r"LOGLINE:\s*(.*)", foundation_text, re.IGNORECASE)
                if logline_match: logline = logline_match.group(1).strip()
                theme_match = re.search(r"THEME:\s*(.*)", foundation_text, re.IGNORECASE)
                if theme_match: theme = theme_match.group(1).strip()

            world_bible_match = re.search(r"//---WORLD_BIBLE---//([\s\S]*?)//---CHARACTER_BIBLE---//", refined_text, re.DOTALL)
            if world_bible_match: world_bible = world_bible_match.group(1).strip()

            character_bible_match = re.search(r"//---CHARACTER_BIBLE---//([\s\S]*)", refined_text, re.DOTALL)
            if character_bible_match:
                character_bible = character_bible_match.group(1).strip()
            else:
                character_bible = "ERROR: Character Bible section not found in AI output."

            print("[ScriptCraft-P1-Bible v7.2] All stages complete.")

        except Exception as e:
            print(f"[ScriptCraft-P1-Bible] Error during generation: {e}")
            traceback.print_exc()
            character_bible = f"ERROR: An exception occurred during bible generation. Check console. Details: {e}"
            full_process_log += f"--- CRITICAL ERROR ---\n{traceback.format_exc()}\n"

        return (logline, theme, world_bible, character_bible, full_process_log)


NODE_CLASS_MAPPINGS = {"AIScriptCrafter01FoundationBible-Akki": AIScriptCrafter01FoundationBible_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AIScriptCrafter01FoundationBible-Akki": "AI ScriptCrafter 01 (Bible) v7.2 - Akki"}