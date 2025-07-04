# Node: Image Prompt Generator v1.0

import re
from llama_cpp import Llama
from .Akki_LLM_Loader import LLMLoader_Akki

class ImagePromptGenerator_Akki:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "input_data": ("STRING", {"multiline": True, "default": "a woman on a boat"}),
                "persona": ("STRING", {"multiline": True, "default": "Act as a Image Generation prompt engineer for GenerativeAI based tools like Stable Diffusion and FLUX."}),
                "context": ("STRING", {"multiline": True, "default": "I am trying to make the prefecty optimized yet detailed prompts for the input prompts/ideas. Describe the prompt as if you are talking to a blind artist and art directing that artist."}),
                "rules_instructions": ("STRING", {"multiline": True, "default": "1. The token limit per prompt output should be limited to 150.\n2. The prompt should be in plain English without using any flourish.\n3. We should avoid using emotions or feelings to describe the prompt."}),
                "output_format": ("STRING", {"multiline": True, "default": "Provide the output as a single paragraph.The prompt should be formatted in the following format -\n1. The first line should describe the main idea.\n2. The second part should detail the subjects (including their appearance, action, motion etc.).\n3. The third part should describe the scene and the background.\n4. The 4th part should describe the technical cinematography details like closeup shot, dof, low angle shot etc.\n5. The last part should describe the style/mood/lighting/treatment."}),
                "max_tokens": ("INT", {"default": 150}),
                "temperature": ("FLOAT", {"default": 0.8, "step": 0.01}),
                "seed": ("INT", {"default": 0}),
                "keep_model_loaded": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "few_shot_examples": ("STRING", {"forceInput": True}),
                "negative_prompt": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("image_prompt", "full_llm_prompt")
    FUNCTION = "generate_image_prompt"
    CATEGORY = "AkkiNodes/LLM"

    def generate_image_prompt(self, llm_model, input_data, persona, context, rules_instructions, output_format, max_tokens, temperature, seed, keep_model_loaded, few_shot_examples=None, negative_prompt=None):
        if not isinstance(llm_model, Llama):
            raise ValueError("LLM Model not provided or is invalid.")
        
        prompt_parts = ["<instructions>"]
        if persona.strip(): prompt_parts.append(f"<persona>{persona.strip()}</persona>")
        if context.strip(): prompt_parts.append(f"<context>{context.strip()}</context>")
        if rules_instructions.strip(): prompt_parts.append(f"<rules>{rules_instructions.strip()}</rules>")
        if few_shot_examples and few_shot_examples.strip(): prompt_parts.append(f"<examples>{few_shot_examples.strip()}</examples>")
        if output_format.strip(): prompt_parts.append(f"<output_format>{output_format.strip()}</output_format>")
        if negative_prompt and negative_prompt.strip(): prompt_parts.append(f"<restrictions>{negative_prompt.strip()}</restrictions>")
        prompt_parts.append("</instructions>")
        prompt_parts.append(f"<input_idea>{input_data.strip()}</input_idea>")
        prompt_parts.append("<response>")
        final_llm_prompt = "\n\n".join(prompt_parts)

        output = llm_model.create_completion(prompt=final_llm_prompt, max_tokens=max_tokens, temperature=temperature, seed=seed if seed > 0 else -1, stop=["</response>"])
        raw_text = output['choices'][0]['text'].strip()
        
        # Clean the output
        clean_prompt = re.sub(r'<[^>]+>', '', raw_text).strip()
        clean_prompt = re.sub(r'\s{2,}', ' ', clean_prompt).replace('\n', ', ')
        
        if not keep_model_loaded:
            LLMLoader_Akki.clear_cache()
            
        return (clean_prompt, final_llm_prompt)

# --- Mappings for this file ---
NODE_CLASS_MAPPINGS = {"ImagePromptGenerator-Akki": ImagePromptGenerator_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"ImagePromptGenerator-Akki": "Image Prompt Generator v1.0 - Akki"}