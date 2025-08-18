# Node: AI QC Supervisor v2.1

import traceback
import re
from .shared_utils import report_token_usage, extract_tagged_content

class AIQCSupervisor_Akki:
    """
    This node acts as an automated AI Quality Control Supervisor. v2.1 provides
    the definitive hardening for the "Single Pass Sanitizer" architecture.
    The AI prompt is refined with a clearer cognitive model to prevent over-
    aggressive cleaning, and the Python rebuilder is hardened to deterministically
    reject and discard malformed junk keys like `PROPS (None)`.
    """

    # --- DEFINITIVE FIX v2.1: Refined prompt with a context-free cognitive model ---
    DEFAULT_PROMPT_TEMPLATE = """<role>
You are a meticulous, hyper-vigilant Data Sanitizer for a film production pipeline. Your only task is to analyze the provided asset lists from a single film shot and rewrite them to be clean and accurate.
</role>

<definitions>
- **VALID ASSETS:** Tangible, physical, production-relevant items. This includes props, costumes, and set dressing (e.g., "Textbook", "Collar with ID tag", "Campus buildings").
- **INVALID ASSETS:** Any item that is not a valid asset. This includes:
    - People or Animals: "Emma", "Students", "Chester"
    - Body Parts: "Emma's face", "Chester's nose", "Emma's hand"
    - Biological Features: "Fur coat", "Dog fur", "skin"
    - Abstract Concepts or Actions: "a flicker of apprehension", "disapproving expression", "showing pain"
</definitions>

<cognitive_model>
For each item in the input lists, you will perform a single, context-independent check: "Is this a tangible, physical object that could be built or acquired for a film set?"
- If YES, you MUST include the item in your rewritten clean list.
- If NO (it is a person, body part, emotion, action, or biological feature), you MUST discard it.
This check is absolute. Do not try to infer context. For example, if "Textbook" appears in a `SET_DRESSING` list, you must still identify it as a valid asset and include it in your `CLEANED_SET_DRESSING` output. Your only job is to sanitize, not to re-categorize.
</cognitive_model>

<output_format>
Your entire response MUST use the following format. Provide the full, clean list for each category. If a cleaned list is empty, output `None`.

//---START_QC_REPORT--//
CLEANED_PROPS: [comma-separated list of valid props]
CLEANED_COSTUMES: [comma-separated list of valid costumes]
CLEANED_SET_DRESSING: [comma-separated list of valid set dressing items]
//---END_QC_REPORT--//
</output_format>

<asset_lists_to_sanitize>
{asset_lists_text}
</asset_lists_to_sanitize>

<response>
"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "shot_breakdown_report": ("STRING", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("clean_shot_breakdown_report", "full_llm_process_log")
    FUNCTION = "supervise_and_correct"
    CATEGORY = "AkkiNodes/Production"

    def supervise_and_correct(self, llm_model, shot_breakdown_report):
        clean_blocks, full_llm_process_log = [], ""
        try:
            if not hasattr(llm_model, 'create_completion'):
                raise ValueError("LLM Model not provided or is invalid.")
            
            shot_blocks = [block for block in shot_breakdown_report.split('//---SHOT_START---//') if block.strip()]

            for i, block in enumerate(shot_blocks):
                original_shot_block = block.replace('//---SHOT_END---//', '').strip()
                print(f"  - Sanitizing shot block {i+1}/{len(shot_blocks)}...")

                # --- STAGE 1 (Python Extractor) ---
                raw_asset_lists = []
                asset_lines_to_replace = set()
                for line in original_shot_block.splitlines():
                    line_lower = line.strip().lower()
                    if line_lower.startswith("props (") or line_lower.startswith("costumes (") or line_lower.startswith("set_dressing:"):
                        raw_asset_lists.append(line.strip())
                        asset_lines_to_replace.add(line.strip())
                asset_lists_text = "\n".join(raw_asset_lists)

                # --- STAGE 2 (AI Sanitizer) ---
                final_llm_prompt = self.DEFAULT_PROMPT_TEMPLATE.format(asset_lists_text=asset_lists_text)
                full_llm_process_log += f"--- PROMPT FOR BLOCK {i+1} ---\n{final_llm_prompt}\n\n"
                
                output = llm_model.create_completion(prompt=final_llm_prompt, max_tokens=1024, temperature=0.1, stop=["</response>"])
                report_token_usage(f"AIQCSupervisor (Block {i+1})", output)
                qc_report_text = extract_tagged_content(output['choices'][0]['text'].strip(), "qc_report")
                full_llm_process_log += f"--- QC REPORT FOR BLOCK {i+1} ---\n{qc_report_text}\n\n"
                
                clean_lists = {}
                for line in qc_report_text.splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        clean_lists[key.strip()] = value.strip()

                # --- STAGE 3 (Python Rebuilder) ---
                rebuilt_block_lines = []
                for line in original_shot_block.splitlines():
                    if line.strip() not in asset_lines_to_replace:
                        rebuilt_block_lines.append(line)
                
                original_props = self._extract_assets_by_char(original_shot_block, "PROPS")
                original_costumes = self._extract_assets_by_char(original_shot_block, "COSTUMES")
                
                clean_props_items = [item.strip() for item in clean_lists.get("CLEANED_PROPS", "").split(',') if item.strip() and item.strip().lower() != 'none']
                clean_costumes_items = [item.strip() for item in clean_lists.get("CLEANED_COSTUMES", "").split(',') if item.strip() and item.strip().lower() != 'none']
                clean_sd_items = [item.strip() for item in clean_lists.get("CLEANED_SET_DRESSING", "").split(',') if item.strip() and item.strip().lower() != 'none']

                for char, items in original_props:
                    # --- DEFINITIVE FIX v2.1: Deterministic check for junk keys ---
                    if char.lower() == 'none':
                        print(f"    - Discarded malformed PROPS key: PROPS ({char})")
                        continue # Skip and discard this junk entry entirely
                    
                    retained_items = sorted([item for item in items if item in clean_props_items])
                    if retained_items:
                        rebuilt_block_lines.append(f"PROPS ({char}): {', '.join(retained_items)}")

                for char, items in original_costumes:
                    # --- DEFINITIVE FIX v2.1: Deterministic check for junk keys ---
                    if char.lower() == 'none':
                        print(f"    - Discarded malformed COSTUMES key: COSTUMES ({char})")
                        continue # Skip and discard this junk entry entirely
                        
                    retained_items = sorted([item for item in items if item in clean_costumes_items])
                    if retained_items:
                        rebuilt_block_lines.append(f"COSTUMES ({char}): {', '.join(retained_items)}")
                
                if clean_sd_items:
                    rebuilt_block_lines.append(f"SET_DRESSING: {', '.join(sorted(clean_sd_items))}")

                clean_blocks.append("\n".join(rebuilt_block_lines))
            
            final_report = "//---SHOT_START---//\n" + "\n//---SHOT_END---//\n\n//---SHOT_START---//\n".join(clean_blocks) + "\n//---SHOT_END---//"
            print("[AIQCSupervisor-v2.1] All shot blocks sanitized and reassembled successfully.")

        except Exception as e:
            final_report = f"ERROR: An exception occurred. Check console.\n\nDetails: {e}"
            print(f"[AIQCSupervisor-v2.1] Error:"); traceback.print_exc()
            
        return (final_report, full_llm_process_log)

    def _extract_assets_by_char(self, block_text, asset_type):
        pattern = re.compile(rf"^{asset_type.upper()}\s*\((.*?)\):\s*(.*)", re.IGNORECASE | re.MULTILINE)
        return [(match.group(1).strip(), [item.strip() for item in match.group(2).split(',')]) for match in pattern.finditer(block_text)]

# --- Mappings ---
NODE_CLASS_MAPPINGS = {"AIQCSupervisor-Akki": AIQCSupervisor_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"AIQCSupervisor-Akki": "AI QC Supervisor v2.1 - Akki"}