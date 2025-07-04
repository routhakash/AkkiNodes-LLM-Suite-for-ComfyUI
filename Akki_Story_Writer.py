# Node: AI Story Writer v3.4 (Stable)

import re
import traceback
from llama_cpp import Llama
from .shared_utils import get_wildcard_list
from .Akki_LLM_Loader import LLMLoader_Akki

class StoryWriter_Akki:
    """
    A specialized AI partner for generating compelling, well-structured stories.
    v3.4 updates the default max_tokens to 16k for longer story generation.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "story_idea": ("STRING", {"multiline": True, "default": "A beagle called Chester discovers a lost ancient civilization."}),
                "protagonist_name": ("STRING", {"default": "Sam"}),
                "antagonist_name": ("STRING", {"default": "Dean"}),
                "protagonist_type": (get_wildcard_list("protagonists.txt"),),
                "protagonist_age": (get_wildcard_list("ages.txt"),),
                "period": (get_wildcard_list("periods.txt"),),
                "location": (get_wildcard_list("locations.txt"),),
                "core_conflict": (get_wildcard_list("conflicts.txt"),),
                "genre": (get_wildcard_list("genres.txt"),),
                "tone": (get_wildcard_list("tones.txt"),),
                "format": (get_wildcard_list("formats.txt"),),
                "word_count_limit": ("INT", {"default": 200, "step": 50}),
                # UPDATED: Default max_tokens increased to 16k
                "max_tokens": ("INT", {"default": 16384, "min": 64, "max": 16384}),
                "temperature": ("FLOAT", {"default": 0.75, "step": 0.01}),
                "seed": ("INT", {"default": 1234}),
                "keep_model_loaded": ("BOOLEAN", {"default": True}),
                "verbose": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("story_text", "full_llm_prompt", "story_idea_out", "protagonist_type_out", "protagonist_age_out", "period_out", "location_out", "core_conflict_out", "genre_out", "tone_out", "format_out", "protagonist_name_out", "antagonist_name_out")
    FUNCTION = "generate_story"
    CATEGORY = "AkkiNodes/LLM"

    STORYTELLING_META_PROMPT = """<role>
You are a master narrative architect and storyteller. Your sole purpose is to take a user's core concept and forge it into a complete, compelling, and well-structured story.
</role>
<core_principles>
- **Show, Don't Tell:** This is your primary artistic principle. Prioritize demonstrating emotions, character traits, and plot points through action, dialogue, and sensory details.
- **Emotional Core:** Create a story that elicits an emotional response. Focus on character motivations, conflicts, and transformations. The protagonist must be different at the end than they were at the beginning.
- **Sensory Details:** Engage at least three of the five senses in every key scene to immerse the reader.
- **Pacing:** Use shorter, punchier sentences for action sequences and longer, more descriptive sentences for moments of reflection or world-building.
- **Purposeful Dialogue:** Ensure every line of dialogue either reveals character, advances the plot, or builds tension. Avoid idle chit-chat.
</core_principles>
<structure>
You will structure the narrative using a Three-Act Structure (Setup, Confrontation, Resolution) unless the user's requested format implies otherwise.
</structure>"""

    def generate_story(self, llm_model, story_idea, protagonist_name, antagonist_name, protagonist_type, protagonist_age, period, location, core_conflict, genre, tone, format, word_count_limit, max_tokens, temperature, seed, keep_model_loaded, verbose):
        story_text = ""
        final_llm_prompt = ""
        try:
            if not isinstance(llm_model, Llama): raise ValueError("LLM Model not provided or is invalid.")

            protagonist_desc = f"A {protagonist_age} {protagonist_type}"
            if protagonist_name.strip(): protagonist_desc += f" named {protagonist_name.strip()}"
            
            antagonist_desc = ""
            if antagonist_name.strip(): antagonist_desc = f"\n- **Antagonist:** The primary antagonist is named {antagonist_name.strip()}."

            narrative_parameters = f"""- **Protagonist:** {protagonist_desc}.{antagonist_desc}
- **Setting:** Takes place in {location} during the {period}.
- **Plot:** The central conflict is '{core_conflict}'.
- **Style:** A {genre} story with a {tone} tone.
- **Format:** Written as a {format}."""
            if word_count_limit > 0: narrative_parameters += f"\n- **Length:** The target length is approximately {word_count_limit} words."
            
            prompt_parts = [self.STORYTELLING_META_PROMPT.strip(), f"<task>\nYour task is to write a complete story based on the following central premise. You must adhere to all the specified parameters to shape the narrative.\n\n**Central Premise:**\n{story_idea.strip()}\n\n**Narrative Parameters:**\n{narrative_parameters}\n</task>", "<response>"]
            final_llm_prompt = "\n\n".join(prompt_parts)

            if verbose: print(f"[StoryWriter-Akki] Full LLM prompt:\n{final_llm_prompt}")

            output = llm_model.create_completion(prompt=final_llm_prompt, max_tokens=max_tokens, temperature=temperature, seed=seed if seed > 0 else -1, stop=["</response>", "<role>", "<task>"])
            story_text = output['choices'][0]['text'].strip()
            
            if not keep_model_loaded: LLMLoader_Akki.clear_cache()
        except Exception as e:
            traceback.print_exc()
            story_text = f"ERROR: An exception occurred. Check console for details.\n\nDetails: {e}"

        return (story_text, final_llm_prompt, story_idea, protagonist_type, protagonist_age, period, location, core_conflict, genre, tone, format, protagonist_name, antagonist_name)

# --- Mappings for this file ---
NODE_CLASS_MAPPINGS = {"StoryWriter-Akki": StoryWriter_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"StoryWriter-Akki": "AI Story Writer v3.4 - Akki"}