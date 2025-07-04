# Node: AI ScriptCrafter 01 (Foundation) v3.3

import re
import json
from llama_cpp import Llama
import traceback

class AIScriptCrafter01Foundation_Akki:
    """
    Phase 1: Generates foundational screenplay elements.
    v3.3 removes the editable prompt template from the UI for a cleaner, more focused workflow.
    """
    # The prompt template is now a class constant, no longer a user-facing input.
    DEFAULT_PROMPT_TEMPLATE = """<role>
You are ScriptCraft AI, an expert screenwriter and story analyst.
</role>
<task>
Analyze the provided story text and generate the foundational elements for a screenplay based on it.
Your entire output MUST be a single, valid JSON object and nothing else. Do not add any conversational text before or after the JSON block.
You MUST use the provided names for the protagonist and antagonist if they appear in the story.
</task>
<story_text_to_analyze>
{story_text}
</story_text_to_analyze>
<additional_context>
- The story's protagonist is a {protagonist_age} {protagonist_type} named {protagonist_name}.
- The antagonist is named {antagonist_name}.
- The story is a {tone} {genre}.
</additional_context>
<output_format>
Generate a JSON object with the following exact keys: "logline", "theme", and "characters".
The "characters" key must contain a list of JSON objects for the protagonist, antagonist, and any key supporting characters you identify from the text.
Each character object must have the keys: "name", "role", "goal", "motivation", "flaw", and "arc".
</output_format>
<response>
"""

    @classmethod
    def INPUT_TYPES(cls):
        # UPDATED: Removed 'prompt_template' from the inputs.
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "story_text": ("STRING", {"forceInput": True}),
                "protagonist_name": ("STRING", {"forceInput": True}),
                "antagonist_name": ("STRING", {"forceInput": True}),
                "protagonist_type": ("STRING", {"forceInput": True}),
                "protagonist_age": ("STRING", {"forceInput": True}),
                "genre": ("STRING", {"forceInput": True}),
                "tone": ("STRING", {"forceInput": True}),
                # Note: 'format' is no longer needed here as it's not in the new prompt template
                "temperature": ("FLOAT", {"default": 0.45, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1235}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("status_line", "theme", "character_breakdowns", "extracted_json_text", "full_analysis_text")
    FUNCTION = "generate_foundations"
    CATEGORY = "AkkiNodes/ScriptCraft"

    def generate_foundations(self, llm_model, story_text, protagonist_name, antagonist_name, protagonist_type, protagonist_age, genre, tone, temperature, top_p, top_k, seed):
        if not isinstance(llm_model, Llama): raise ValueError("LLM Model not provided.")
        
        # UPDATED: The function now uses the internal class constant for the prompt.
        prompt = self.DEFAULT_PROMPT_TEMPLATE.format(
            story_text=story_text,
            protagonist_name=protagonist_name,
            antagonist_name=antagonist_name,
            protagonist_age=protagonist_age,
            protagonist_type=protagonist_type,
            genre=genre,
            tone=tone,
        )
        
        print("[ScriptCraft-P1] Generating foundational analysis from story text...")
        output = llm_model.create_completion(prompt=prompt, max_tokens=2048, temperature=temperature, top_p=top_p, top_k=top_k, seed=seed if seed > 0 else -1, stop=["</response>"])
        raw_text = output['choices'][0]['text'].strip()
        
        status, theme, character_breakdowns, extracted_json = "ERROR: Unknown failure.", "", "", ""
        try:
            if not raw_text: raise ValueError("LLM returned an empty response.")
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if not json_match: raise ValueError("Could not find any JSON block in the response.")
            extracted_json = json_match.group(0)
            parsed_json = json.loads(extracted_json)

            logline = parsed_json.get('logline', 'Logline not found in JSON.')
            theme = parsed_json.get('theme', 'Theme not found in JSON.')
            characters = parsed_json.get('characters', [])
            
            breakdown_list = [f"Name: {c.get('name', 'N/A')} ({c.get('role', 'N/A')})\nGoal: {c.get('goal', 'N/A')}\nMotivation: {c.get('motivation', 'N/A')}\nFlaw: {c.get('flaw', 'N/A')}\nArc: {c.get('arc', 'N/A')}" for c in characters]
            character_breakdowns = "\n\n//===BREAK===//\n\n".join(breakdown_list)
            
            status = f"SUCCESS: {logline}"
        except Exception as e:
            status = f"ERROR: {e}"
            print(f"[ScriptCraft-P1] Error parsing LLM response: {e}")
            traceback.print_exc()

        return (status, theme, character_breakdowns, extracted_json, raw_text)

# --- Mappings for this file ---
NODE_CLASS_MAPPINGS = {"AIScriptCrafter01Foundation-Akki": AIScriptCrafter01Foundation_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AIScriptCrafter01Foundation-Akki": "AI ScriptCrafter 01 (Foundation) v3.3 - Akki"}