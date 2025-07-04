# Node: AI ScriptCrafter 03 (Screenplay) v5.1

from llama_cpp import Llama
import traceback
from .shared_utils import get_wildcard_list

class AIScriptCrafter03Screenplay_Akki:
    """
    Phase 3: Writes the screenplay from the beat sheet.
    v5.1 is a major overhaul to the core prompt, focusing on narrative fluidity, scene transitions, and concrete word count targets.
    """
    # The final, most advanced "AI Director" prompt template.
    DEFAULT_PROMPT_TEMPLATE = """<role>
You are ScriptCraft AI, an expert AI Film Director and Screenwriter. Your function is to translate a structural beat sheet into a complete, professional, and cinematic screenplay.
</role>

<core_directive>
Your primary task is to **interpret** each beat and **expand** it into one or more fully realized scenes.
**Crucially, you must ensure a fluid narrative flow.** Each scene should logically and smoothly transition into the next. Consider the pacing and momentum of the story as a whole. Do not just write isolated scenes; connect them to form a cohesive, cinematic sequence.
</core_directive>

<cinematic_language_mandate>
You MUST use the language of cinema to tell the story.
- **Camera Work:** Actively direct the camera. Use shot descriptions like `WIDE SHOT`, `CLOSE UP ON...`, `TRACKING SHOT`.
- **Dynamic Transitions:** Do not overuse `FADE IN:`. Use a variety of transitions like `CUT TO:`, `DISSOLVE TO:`, `SMASH CUT TO:`, or `MATCH CUT:` to control the rhythm.
- **Sound Design:** Describe critical sounds using `SOUND of...` to build atmosphere.
- **Action & Description:** Write what can be seen and heard. Be concise but evocative. Use sensory details.
</_cinematic_language_mandate>

<pacing_and_length_mandate>
The target length for this screenplay is approximately **{target_word_count} words**. You must pace the story and scene length to meet this target.
- **The Rule:** You will translate the provided {duration_minutes}-minute target runtime into a word count.
- **Act Structure Pacing:** For a {duration_minutes}-minute script, pace the acts accordingly: Act 1 (~25% of words), Act 2 (~50%), Act 3 (~25%).
- **Pacing Style:** The overall pacing should reflect a **{cinematic_style}**.
</pacing_and_length_mandate>

<formatting_rules>
Adhere strictly to American industry-standard screenplay format.
- **Scene Headings:** `INT. LOCATION - DAY` or `EXT. LOCATION - NIGHT`.
- **Character Names:** Centered, uppercase.
- **Dialogue:** Standard indented block.
- **Parentheticals:** `(wryly)`, used sparingly.
</formatting_rules>

<task>
Write the full screenplay. Translate the provided beat sheet, using the story context, into a complete cinematic script. Ensure the scenes flow together naturally. Start with "FADE IN:" and end with "FADE OUT.".
</task>

<story_context>
{story_text}
{character_breakdowns}
</story_context>

<beat_sheet_blueprint>
{beat_sheet}
</beat_sheet_blueprint>

<response>
FADE IN:
"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "story_text": ("STRING", {"forceInput": True}),
                "character_breakdowns": ("STRING", {"forceInput": True}),
                "beat_sheet": ("STRING", {"forceInput": True}),
                "duration_minutes": ("INT", {"default": 15, "min": 5, "max": 180, "step": 5}),
                "cinematic_style": (get_wildcard_list("cinematic_styles.txt"),),
                "max_tokens": ("INT", {"default": 16384, "min": 1024, "max": 16384}),
                "temperature": ("FLOAT", {"default": 0.8, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 0}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("screenplay", "full_llm_prompt")
    FUNCTION = "generate_script"
    CATEGORY = "AkkiNodes/ScriptCraft"

    def generate_script(self, llm_model, story_text, character_breakdowns, beat_sheet, duration_minutes, cinematic_style, max_tokens, temperature, top_p, top_k, seed):
        screenplay, final_llm_prompt = "", ""
        try:
            if not isinstance(llm_model, Llama): raise ValueError("LLM Model not provided.")
            
            # UPDATED: Calculate a concrete word count target. Average screenplay page has ~190 words.
            target_word_count = duration_minutes * 190

            final_llm_prompt = self.DEFAULT_PROMPT_TEMPLATE.format(
                duration_minutes=duration_minutes,
                target_word_count=target_word_count, # New parameter for the prompt
                cinematic_style=cinematic_style,
                story_text=story_text,
                character_breakdowns=character_breakdowns,
                beat_sheet=beat_sheet
            )
            
            print("[ScriptCraft-P3] Generating full screenplay with narrative flow logic...")
            output = llm_model.create_completion(
                prompt=final_llm_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                seed=seed if seed > 0 else -1,
                stop=["FADE OUT.", "</response>", "<role>", "<task>"]
            )
            screenplay = "FADE IN:\n\n" + output['choices'][0]['text'].strip() + "\n\nFADE OUT."
        except Exception as e:
            screenplay = f"ERROR: An exception occurred in ScriptCrafter P3. Check console for details.\n\nDetails: {e}"
            traceback.print_exc()

        return (screenplay, final_llm_prompt)

# --- Mappings for this file ---
NODE_CLASS_MAPPINGS = {"AIScriptCrafter03Screenplay-Akki": AIScriptCrafter03Screenplay_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AIScriptCrafter03Screenplay-Akki": "AI ScriptCrafter 03 (Screenplay) v5.1 - Akki"}