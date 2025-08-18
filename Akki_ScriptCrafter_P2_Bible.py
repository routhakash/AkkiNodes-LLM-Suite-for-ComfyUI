# Node: AI ScriptCrafter 02 (Beat Sheet & Bible Passthrough) v4.0

import traceback
from .shared_utils import report_token_usage, extract_tagged_content

class AIScriptCrafter02BeatSheetBible_Akki:
    """
    Phase 2 (Enhanced): Generates a 15-point beat sheet, using the Narrative
    Bible for richer context, and passes the Bibles through for the next stage.
    """
    # PROMPT ENHANCED to accept the Narrative Bible for more context.
    DEFAULT_PROMPT_TEMPLATE = """<role>
You are ScriptCraft AI, an expert screenwriter specializing in narrative structure.
</role>
<task>
Analyze the provided story text and the detailed "Narrative Bible" context. Your task is to deconstruct this narrative into a 15-point "Save the Cat!" beat sheet. Your response MUST begin with `//---START_MAIN_OUTPUT--//` and end with `//---END_MAIN_OUTPUT--//`.
</task>

<narrative_bible_context>
--- WORLD BIBLE ---
{world_bible}
--- CHARACTER BIBLE ---
{character_bible}
</narrative_bible_context>

<story_text_to_analyze>
{story_text}
</story_text_to_analyze>

<output_format>
Your output MUST be a list of the following 15 beats, in order. For each beat, provide a 1-3 sentence description of the corresponding event from the analyzed story. Be concise and specific.

1.  **Opening Image:** A visual that represents the "before" snapshot of the protagonist and their world.
2.  **Theme Stated:** A line of dialogue or event that poses the central thematic question of the story.
3.  **Setup:** Introduce the protagonist, their world, their goals, and what's missing in their life.
4.  **Catalyst (Inciting Incident):** The event that disrupts the protagonist's world and sets the story in motion.
5.  **Debate:** A moment of hesitation where the protagonist questions whether to take on the challenge.
6.  **Break into Act 2:** The protagonist makes the decision to act and crosses the threshold into the "new world" of the story.
7.  **B Story:** Introduction of a subplot, often a relationship, that will help the protagonist learn the story's theme.
8.  **Fun and Games:** The protagonist explores the new world, experiencing either the highs of success or the lows of repeated failure. This is the "promise of the premise."
9.  **Midpoint:** A major event that raises the stakes, often where the "fun and games" end and the protagonist becomes proactive.
10. **Bad Guys Close In:** The antagonist's forces regroup and apply new, more powerful pressure on the protagonist.
11. **All Is Lost:** The lowest point for the protagonist. A major failure, often accompanied by the "whiff of death."
12. **Dark Night of the Soul:** The moment of reflection after the "All Is Lost" beat, where the protagonist realizes what they must do to succeed.
13. **Break into Act 3:** The protagonist, armed with their new knowledge, decides to confront the antagonist.
14. **Finale:** The final confrontation where the protagonist must apply the lessons learned from the B Story to resolve the A Story.
15. **Final Image:** An image that is the "after" snapshot, mirroring the Opening Image but showing how the protagonist and their world have changed.
</output_format>
<response>
//---START_MAIN_OUTPUT--//
"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "story_text": ("STRING", {"forceInput": True}),
                # NEW INPUTS
                "world_bible": ("STRING", {"forceInput": True}),
                "character_bible": ("STRING", {"forceInput": True}),
                "max_tokens": ("INT", {"default": 4096, "min": 256, "max": 16384}),
                "temperature": ("FLOAT", {"default": 0.7, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 1234}),
            }
        }
    
    # ADDED new passthrough outputs
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("beat_sheet", "world_bible_passthrough", "character_bible_passthrough")
    FUNCTION = "generate_beats"
    CATEGORY = "AkkiNodes/ScriptCraft"

    def generate_beats(self, llm_model, story_text, world_bible, character_bible, max_tokens, temperature, top_p, top_k, seed):
        beat_sheet = ""
        try:
            if not hasattr(llm_model, 'create_completion'): raise ValueError("LLM Model not provided.")
            
            prompt = self.DEFAULT_PROMPT_TEMPLATE.format(
                story_text=story_text,
                world_bible=world_bible,
                character_bible=character_bible
            )
            
            print("[ScriptCraft-P2-Bible] Generating beat sheet from story and bible...")
            output = llm_model.create_completion(
                prompt=prompt, max_tokens=max_tokens, temperature=temperature,
                top_p=top_p, top_k=top_k, seed=seed if seed > 0 else -1, stop=["</response>", "//---END_MAIN_OUTPUT--//"]
            )
            report_token_usage("ScriptCrafter-P2-Bible", output)
            raw_text = output['choices'][0]['text'].strip()
            beat_sheet = extract_tagged_content(raw_text, "main_output")
        except Exception as e:
            beat_sheet = f"ERROR: An exception occurred in ScriptCrafter P2. Check console for details.\n\nDetails: {e}"
            traceback.print_exc()

        # Pass the bibles through unchanged
        return (beat_sheet, world_bible, character_bible)

NODE_CLASS_MAPPINGS = {"AIScriptCrafter02BeatSheetBible-Akki": AIScriptCrafter02BeatSheetBible_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AIScriptCrafter02BeatSheetBible-Akki": "AI ScriptCrafter 02 (Bible) v4.0 - Akki"}