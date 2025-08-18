# Node: AI Video Prompt Engineer (Pro) v2.4

import traceback
import re
from .shared_utils import report_token_usage, get_wildcard_list

class AIVideoPromptEngineerPro_Akki:
    """
    The definitive AI agent for video prompting. v2.4 evolves the node into a
    3-stage process, adding a final "AI Editor" stage to condense the verbose
    output into a tight, motion-focused, and highly effective video prompt.
    """
    
    # STAGE 1: Action Analyst (UNCHANGED)
    STAGE_1_PROMPT = """<role>
You are a script analyst. Your only job is to read the `ACTION/CAMERA` section of a film shot dossier and identify the single most important subject and the primary physical action they are performing.
</role>
<core_directive>
- Be concise. Output a single, simple sentence describing the core movement.
- Ignore static details, camera angles, setting descriptions, and internal emotional states.
- Focus ONLY on the physical movement.
</core_directive>
<example>[INPUT]
A medium shot establishing Sia Volkov's movement across a chasm... She pulls herself across with determined effort...
[YOUR OUTPUT]
A young woman uses a grappling hook to swing across a chasm.
</example>
<dossier_action_section>{action_camera_data}</dossier_action_section>
<response>
"""

    # STAGE 2: Virtual DOP (UNCHANGED)
    STAGE_2_PROMPT = """<role>
You are an award-winning Director of Photography and AI Prompt Engineer. Your task is to transform a simple "Core Action" and supporting documents into a rich, detailed, and technically precise multi-paragraph "micro-scene" for a video generation model.
</role>
<synthesis_protocol>
1.  **Describe a Complete Event:** The prompt must describe a short sequence of actions with a clear beginning, middle, and end.
2.  **Invent Subtle Environmental Motion:** You MUST add creative, secondary environmental details that enhance realism (e.g., `gusts of wind kicking up sand`, `rain splashing off shoulders`).
3.  **Use Explicit Camera Language:** You MUST include professional cinematography terms (`dolly-in`, `wide-angle lens`, `shallow depth of field`, `low-angle shot`).
4.  **Prioritize Motion:** Focus on describing movement and transformation.
</synthesis_protocol>
<negative_mandate>CRITICAL RULE: Do NOT include generic quality keywords like 'photorealistic', 'masterpiece', '8k', etc. Your entire focus is on the cinematic and technical description of the shot.</negative_mandate>
<few_shot_example>[Core Action]
A young woman uses a grappling hook to swing across a chasm.
[Master Dossier]
--- ACTION/CAMERA ---
A medium shot establishing Sia Volkov's movement across a chasm... Kaelen... watches nervously...
[YOUR IDEAL OUTPUT]
A cinematic medium shot, subtly shaky handheld shot of a lean agile young woman named Sia Volkov who strains against a makeshift grappling hook as she pulls herself across a vast chasm. Gusts of wind whipping strands of hair across her face. She pulls herself across with determined effort, her layered clothing fluttering in gusts of wind.

Kaelen a boy positioned below hunches over a diagnostic tool. His brow furrowed with worry as he watches her progress. He moves subtly with anxious motion.

Gusts of wind stirring dust devils and shimmering heat haze in the background. The shot emphasizes the gritty junkyard aesthetic.

The camera performs a slow dolly-in focusing on the girl's focused and determined expression as she finishes her climb in the end. Lighting is motivated by the ambient glow of residual energy fields and bioluminescent fungi, creating pockets of cool illumination amidst the general grime and rust; this contrasts with Kaelen's worried expression below. A shallow depth of field isolates Sia as she pulls herself across, utilizing a prime lens (likely in the 50mm range) to maintain focus on her determined effort while blurring the chaotic background details of the Crimson Heap, heightening the feeling of precariousness and isolation within this technological graveyard.
</few_shot_example>
<core_action>{core_action}</core_action>
<master_dossier>{master_dossier}</master_dossier>
<shot_breakdown>{shot_details}</shot_breakdown>
<directorial_notes>- Camera Movement: {camera_movement}
- Motion Speed: {motion_speed}</directorial_notes>
<response>
"""

    # STAGE 3: The AI Editor (NEW)
    STAGE_3_PROMPT = """<role>
You are an expert AI Prompt Editor. Your task is to take a verbose, descriptive "micro-scene" and condense it into a tight, efficient, and powerful video prompt, preserving its structure and core meaning.
</role>

<optimization_protocol>
1.  **Remove Dialogue:** You MUST remove any and all lines of dialogue or spoken words.
2.  **Remove Redundant Static Details:** You MUST remove static environmental descriptions that do not contribute to the sense of motion. The input image will provide the static details; your job is to describe the *action*. Focus on keywords that imply motion (e.g., keep `gusts of wind stirring dust`, remove `the container has patched metal plating`).
3.  **Preserve Structure:** You MUST maintain the original multi-paragraph structure (one paragraph for each character, one for environment, one for cinematography).
4.  **Preserve Motion & Cinematography:** You MUST preserve all descriptions of character action, environmental motion (like wind, rain, sparks), and explicit camera language.
</optimization_protocol>

<example_before_editing>
A cinematic medium shot, subtly shaky handheld shot of a lean agile young woman named Sia Volkov who strains against a makeshift grappling hook as she pulls herself across a vast chasm. Gusts of wind whipping strands of hair across her face. She pulls herself across with determined effort, her layered clothing fluttering in gusts of wind. She says, "I'm almost there!"

Kaelen a boy positioned below hunches over a diagnostic tool. His brow furrowed with worry as he watches her progress. He moves subtly with anxious motion.

Gusts of wind stirring dust devils and shimmering heat haze in the background. The junkyard is full of rusted durasteel and tangled cables. The shot emphasizes the gritty junkyard aesthetic.

The camera performs a slow dolly-in focusing on the girl's focused and determined expression. Lighting is motivated by the ambient glow of residual energy fields. A shallow depth of field isolates Sia, utilizing a prime lens (likely 50mm).
</example_before_editing>

<example_after_editing>
A cinematic medium shot, subtly shaky handheld, of a lean agile young woman, Sia Volkov, straining against a makeshift grappling hook, pulling herself across a vast chasm. Gusts of wind whip her hair and clothing.

Kaelen, positioned below, hunches over a diagnostic tool with a worried expression, moving with subtle anxious motion.

Gusts of wind stir dust devils and shimmering heat haze in the background.

The camera performs a slow dolly-in, focusing on the girl's determined expression. Lighting from ambient energy fields creates cool illumination. A shallow depth of field with a 50mm prime lens isolates Sia.
</example_after_editing>

<verbose_prompt_to_edit>
{verbose_prompt}
</verbose_prompt_to_edit>

<response>
"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "master_dossier": ("STRING", {"forceInput": True}),
                "shot_details": ("STRING", {"forceInput": True}),
                "camera_movement": (["Default (from prompt)", "Random"] + get_wildcard_list("video_camera_movements.txt"),),
                "motion_speed": (["Default (from prompt)", "Random"] + get_wildcard_list("video_motion_speeds.txt"),),
                "temperature": ("FLOAT", {"default": 0.8, "step": 0.01}),
                "seed": ("INT", {"default": 1234}),
                "max_tokens": ("INT", {"default": 1024, "min": 256, "max": 4096}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_prompt", "full_llm_process_log")
    FUNCTION = "generate_prompt"
    CATEGORY = "AkkiNodes/Video"

    def _extract_action_from_dossier(self, dossier_text):
        match = re.search(r"--- ACTION/CAMERA ---\n([\s\S]*?)(\n--- SET LOOKDEV ---|\n--- CHARACTERS ---|$)", dossier_text)
        return match.group(1).strip() if match else dossier_text

    def generate_prompt(self, llm_model, master_dossier, shot_details, camera_movement, motion_speed, **kwargs):
        video_prompt, full_llm_process_log = "", ""
        try:
            if not hasattr(llm_model, 'create_completion'): raise ValueError("LLM Model invalid.")
            if not master_dossier or "ERROR:" in master_dossier: return (f"Invalid Master Dossier: {master_dossier}", "")
            if not shot_details or "ERROR:" in shot_details: return (f"Invalid Shot Details: {shot_details}", "")

            action_camera_data = self._extract_action_from_dossier(master_dossier)

            # --- STAGE 1: Action Analyst ---
            stage1_prompt = self.STAGE_1_PROMPT.format(action_camera_data=action_camera_data)
            stage1_output = llm_model.create_completion(prompt=stage1_prompt, max_tokens=256, temperature=0.2)
            core_action = stage1_output['choices'][0]['text'].strip()
            full_llm_process_log += f"--- STAGE 1: ANALYST RESPONSE ---\n{core_action}\n\n"

            # --- STAGE 2: Virtual DOP ---
            stage2_prompt = self.STAGE_2_PROMPT.format(
                core_action=core_action, master_dossier=master_dossier, shot_details=shot_details,
                camera_movement=camera_movement, motion_speed=motion_speed
            )
            stage2_output = llm_model.create_completion(prompt=stage2_prompt, max_tokens=kwargs.get('max_tokens', 1024),
                                                        temperature=kwargs.get('temperature', 0.8),
                                                        seed=kwargs.get('seed', 1234) if kwargs.get('seed', 1234) > 0 else -1,
                                                        stop=["</response>"])
            verbose_prompt = stage2_output['choices'][0]['text'].strip()
            full_llm_process_log += f"--- STAGE 2: V-DOP RESPONSE (VERBOSE) ---\n{verbose_prompt}\n\n"

            # --- STAGE 3: AI Editor ---
            print("[VideoPromptEngineer-Pro v2.4] Stage 3: Condensing verbose prompt...")
            stage3_prompt = self.STAGE_3_PROMPT.format(verbose_prompt=verbose_prompt)
            stage3_output = llm_model.create_completion(prompt=stage3_prompt, max_tokens=kwargs.get('max_tokens', 1024),
                                                        temperature=0.4, # Lower temp for precise editing
                                                        seed=kwargs.get('seed', 1234) if kwargs.get('seed', 1234) > 0 else -1,
                                                        stop=["</response>"])
            report_token_usage("VideoPromptEngineer-Pro (Editor)", stage3_output)
            video_prompt = stage3_output['choices'][0]['text'].strip()
            full_llm_process_log += f"--- STAGE 3: EDITOR RESPONSE (FINAL) ---\n{video_prompt}"

        except Exception as e:
            traceback.print_exc()
            video_prompt = f"ERROR: An exception occurred. Check console. Details: {e}"

        return (video_prompt, full_llm_process_log)

NODE_CLASS_MAPPINGS = {"AIVideoPromptEngineerPro-Akki": AIVideoPromptEngineerPro_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AIVideoPromptEngineerPro-Akki": "AI Video Prompt Engineer (Pro) v2.4 - Akki"}