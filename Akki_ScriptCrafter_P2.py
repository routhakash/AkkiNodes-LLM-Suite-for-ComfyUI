# Node: AI ScriptCrafter 02 (Beat Sheet) v3.0

from llama_cpp import Llama
import traceback

class AIScriptCrafter02BeatSheet_Akki:
    """
    Phase 2: Generates a 15-point beat sheet.
    v3.0 refactors the node to use the full story_text as its primary context for a more accurate blueprint.
    """
    DEFAULT_PROMPT_TEMPLATE = """<role>
You are ScriptCraft AI, an expert screenwriter specializing in narrative structure.
</role>
<task>
Analyze the provided story text and character breakdowns. Your task is to deconstruct this narrative into a 15-point "Save the Cat!" beat sheet.
</task>
<story_text_to_analyze>
{story_text}
</story_text_to_analyze>
<character_breakdowns>
{character_breakdowns}
</character_breakdowns>
<output_format>
Your output MUST be a list of the following 15 beats, in order. For each beat, provide a 1-3 sentence description of the corresponding event from the analyzed story. Be concise and specific.

1.  **Opening Image:**
2.  **Theme Stated:**
3.  **Setup:**
4.  **Catalyst (Inciting Incident):**
5.  **Debate:**
6.  **Break into Act 2:**
7.  **B Story:**
8.  **Fun and Games:**
9.  **Midpoint:**
10. **Bad Guys Close In:**
11. **All Is Lost:**
12. **Dark Night of the Soul:**
13. **Break into Act 3:**
14. **Finale:**
15. **Final Image:**
</output_format>
<response>
"""

    @classmethod
    def INPUT_TYPES(cls):
        # UPDATED: Inputs are now story_text and character_breakdowns
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "story_text": ("STRING", {"forceInput": True}),
                "character_breakdowns": ("STRING", {"forceInput": True}),
                "temperature": ("FLOAT", {"default": 0.5, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 0}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("beat_sheet",)
    FUNCTION = "generate_beats"
    CATEGORY = "AkkiNodes/ScriptCraft"

    def generate_beats(self, llm_model, story_text, character_breakdowns, temperature, top_p, top_k, seed):
        beat_sheet = ""
        try:
            if not isinstance(llm_model, Llama): raise ValueError("LLM Model not provided.")
            
            prompt = self.DEFAULT_PROMPT_TEMPLATE.format(
                story_text=story_text,
                character_breakdowns=character_breakdowns
            )
            
            print("[ScriptCraft-P2] Generating beat sheet from story text...")
            output = llm_model.create_completion(
                prompt=prompt,
                max_tokens=2048,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                seed=seed if seed > 0 else -1,
                stop=["</response>"]
            )
            beat_sheet = output['choices'][0]['text'].strip()
        except Exception as e:
            beat_sheet = f"ERROR: An exception occurred in ScriptCrafter P2. Check console for details.\n\nDetails: {e}"
            print(f"[ScriptCraft-P2] Error:")
            traceback.print_exc()

        return (beat_sheet,)

# --- Mappings for this file ---
NODE_CLASS_MAPPINGS = {"AIScriptCrafter02BeatSheet-Akki": AIScriptCrafter02BeatSheet_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AIScriptCrafter02BeatSheet-Akki": "AI ScriptCrafter 02 (Beat Sheet) v3.0 - Akki"}