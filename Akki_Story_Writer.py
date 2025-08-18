# Node: AI Story Writer v5.2 (Prompt Pathing Hotfix)

import re
import traceback
import os
from llama_cpp import Llama
from .shared_utils import get_wildcard_list, report_token_usage, extract_tagged_content

class StoryWriter_Akki:
    """
    AI Story Writer v5.2. This version incorporates a critical hotfix for the
    prompt file loading mechanism, removing the unnecessary subdirectory logic.
    It retains the v5.1 architecture for robust pathing and orthogonal inputs.
    """
    
    # --- v5.2: Simplified Prompt Directory Logic ---
    PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "_prompts", "story")

    @classmethod
    def _get_prompt_files(cls):
        """Dynamically lists .txt files from the node's designated prompt directory."""
        if not os.path.isdir(cls.PROMPTS_DIR):
            try:
                os.makedirs(cls.PROMPTS_DIR, exist_ok=True)
                placeholder_path = os.path.join(cls.PROMPTS_DIR, "placeholder.txt")
                if not os.path.exists(placeholder_path):
                     with open(placeholder_path, 'w', encoding='utf-8') as f:
                         f.write("Add your story prompt .txt files here.")
                return ["placeholder.txt"]
            except Exception as e:
                print(f"[StoryWriter-Akki v5.2] Error creating prompt directory {cls.PROMPTS_DIR}: {e}")
                return ["Error creating directory"]
        try:
            files = [f for f in os.listdir(cls.PROMPTS_DIR) if f.endswith('.txt')]
            return files if files else ["No .txt files found"]
        except Exception as e:
            print(f"[StoryWriter-Akki v5.2] Error scanning prompt directory {cls.PROMPTS_DIR}: {e}")
            return ["Error loading prompts"]

    def _read_prompt_file(self, filename):
        """Reads the content of a specific prompt file from the node's prompt directory."""
        filepath = os.path.join(self.PROMPTS_DIR, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    # --- v5.1: Platform-agnostic wildcard path helper ---
    WILDCARD_DIR = os.path.join(os.path.dirname(__file__), "wildcards")

    @classmethod
    def _get_wildcard_path(cls, filename):
        """Constructs a full, platform-agnostic path for a given wildcard file."""
        return os.path.join(cls.WILDCARD_DIR, filename)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "story_prompt_file": (cls._get_prompt_files(),), # v5.2: Simplified call
                "story_idea": ("STRING", {"multiline": True, "default": "A beagle called Chester discovers a lost ancient civilization."}),
                
                "protagonist_name": ("STRING", {"default": "Nora Lane"}),
                "protagonist_gender": (get_wildcard_list(cls._get_wildcard_path("character_gender.txt")),),
                "protagonist_identity": (get_wildcard_list(cls._get_wildcard_path("character_identity.txt")),),
                "protagonist_role": (get_wildcard_list(cls._get_wildcard_path("character_role.txt")),),
                "protagonist_age": (get_wildcard_list(cls._get_wildcard_path("character_age.txt")),),

                "antagonist_name": ("STRING", {"default": "Wayne Marshall"}),
                "antagonist_gender": (get_wildcard_list(cls._get_wildcard_path("character_gender.txt")),),
                "antagonist_identity": (get_wildcard_list(cls._get_wildcard_path("character_identity.txt")),),
                "antagonist_role": (get_wildcard_list(cls._get_wildcard_path("character_role.txt")),),
                "antagonist_age": (get_wildcard_list(cls._get_wildcard_path("character_age.txt")),),
                
                "period": (get_wildcard_list(cls._get_wildcard_path("periods.txt")),),
                "location": (get_wildcard_list(cls._get_wildcard_path("locations.txt")),),
                "core_conflict": (get_wildcard_list(cls._get_wildcard_path("conflicts.txt")),),
                "story_arc": (get_wildcard_list(cls._get_wildcard_path("story_arc.txt")),),
                "genre": (get_wildcard_list(cls._get_wildcard_path("genres.txt")),),
                "tone": (get_wildcard_list(cls._get_wildcard_path("tones.txt")),),
                "format": (get_wildcard_list(cls._get_wildcard_path("formats.txt")),),

                "word_count_limit": ("INT", {"default": 4000, "min": 0, "max": 16384, "step": 50}),
                "max_tokens": ("INT", {"default": 16384, "min": 64, "max": 16384}),
                "temperature": ("FLOAT", {"default": 0.75, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1234}),
                "keep_model_loaded": ("BOOLEAN", {"default": True}),
                "verbose": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("story_text", "full_llm_prompt", "story_idea_out", "protagonist_type_out", "protagonist_age_out", "antagonist_type_out", "antagonist_age_out", "period_out", "location_out", "core_conflict_out", "genre_out", "tone_out", "format_out", "protagonist_name_out", "antagonist_name_out")
    FUNCTION = "generate_story"
    CATEGORY = "AkkiNodes/LLM"

    def generate_story(self, llm_model, story_prompt_file, story_idea,
                         protagonist_name, protagonist_gender, protagonist_identity, protagonist_role, protagonist_age,
                         antagonist_name, antagonist_gender, antagonist_identity, antagonist_role, antagonist_age,
                         period, location, core_conflict, story_arc, genre, tone, format,
                         word_count_limit, max_tokens, temperature, top_p, top_k, seed,
                         keep_model_loaded, verbose):
        story_text = ""
        final_llm_prompt = ""
        
        try:
            if not hasattr(llm_model, 'create_completion'):
                raise ValueError("LLM Model not provided or is invalid.")

            def build_character_description(gender, identity, age, role, name):
                parts = []
                if gender and gender.lower() not in ['unspecified', 'it/its', 'they/them (as a singular pronoun)']:
                    parts.append(gender)
                if age:
                    parts.append(age)
                if identity and identity.lower() != 'human':
                    if not identity.lower().startswith(('a ', 'an ')):
                        parts.append(identity)
                    else:
                        parts = [gender, age, identity]
                if role:
                    parts.append(role)
                
                base_desc = " ".join(filter(None, parts))
                
                if name and name.strip():
                    base_desc += f" named {name.strip()}"
                
                return base_desc.strip()

            protagonist_desc = build_character_description(protagonist_gender, protagonist_identity, protagonist_age, protagonist_role, protagonist_name)
            antagonist_desc = build_character_description(antagonist_gender, antagonist_identity, antagonist_age, antagonist_role, antagonist_name)

            narrative_parameters_for_ai = f"""- **Protagonist:** {protagonist_desc}.
- **Antagonist:** {antagonist_desc}.
- **Setting:** Takes place in {location} during the {period}.
- **Plot:** The central conflict is '{core_conflict}'.
- **Narrative Arc:** The story follows a '{story_arc}' structure.
- **Style:** A {genre} story with a {tone} tone.
- **Format:** Written as a {format}."""
            
            if word_count_limit > 0:
                narrative_parameters_for_ai += f"\n- **Length:** The target length is approximately {word_count_limit} words."
            
            storytelling_meta_prompt = self._read_prompt_file(story_prompt_file) # v5.2: Simplified call

            final_llm_prompt = storytelling_meta_prompt.format(
                story_idea=story_idea.strip(),
                narrative_parameters=narrative_parameters_for_ai
            ).strip()

            if verbose:
                print(f"[StoryWriter-Akki v5.2] Full LLM prompt:\n{final_llm_prompt}")

            output = llm_model.create_completion(
                prompt=final_llm_prompt, max_tokens=max_tokens, temperature=temperature,
                top_p=top_p, top_k=top_k, seed=seed if seed > 0 else -1,
                stop=["</response>", "//---END_MAIN_OUTPUT--//"]
            )
            report_token_usage("StoryWriter-Akki", output)
            
            raw_text = output['choices'][0]['text'].strip()
            story_text = extract_tagged_content(raw_text, "main_output")
            
            if not keep_model_loaded:
                from .Akki_LLM_Loader import LLMLoader_Akki
                LLMLoader_Akki.clear_cache()
        
        except Exception as e:
            traceback.print_exc()
            story_text = f"ERROR: An exception occurred. Check console for details.\n\nDetails: {e}"

        protagonist_type_out = " ".join(filter(None, [protagonist_gender, protagonist_identity, protagonist_role]))
        antagonist_type_out = " ".join(filter(None, [antagonist_gender, antagonist_identity, antagonist_role]))

        return (story_text, final_llm_prompt, story_idea, 
                protagonist_type_out.strip(), protagonist_age, 
                antagonist_type_out.strip(), antagonist_age, 
                period, location, core_conflict, genre, tone, format, 
                protagonist_name, antagonist_name)

NODE_CLASS_MAPPINGS = {"StoryWriter-Akki": StoryWriter_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"StoryWriter-Akki": "AI Story Writer v5.2 - Akki"}