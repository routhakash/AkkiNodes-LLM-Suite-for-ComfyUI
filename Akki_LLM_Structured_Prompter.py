# Node: LLM Structured Prompter v1.0

from llama_cpp import Llama
from .Akki_LLM_Loader import LLMLoader_Akki

class LLMStructuredPrompter_Akki:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm_model": ("LLM_MODEL",),
                "persona": ("STRING", {"multiline": True, "default": ""}),
                "context": ("STRING", {"multiline": True, "default": ""}),
                "rules_instructions": ("STRING", {"multiline": True, "default": ""}),
                "input_data": ("STRING", {"multiline": True, "default": ""}),
                "task_question": ("STRING", {"multiline": True, "default": "Summarize."}),
                "few_shot_examples": ("STRING", {"multiline": True, "default": ""}),
                "output_format": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "max_tokens": ("INT", {"default": 256}),
                "temperature": ("FLOAT", {"default": 0.7, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                "top_k": ("INT", {"default": 40}),
                "seed": ("INT", {"default": 0}),
                "keep_model_loaded": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "structured_prompt")
    FUNCTION = "execute_structured_prompt"
    CATEGORY = "AkkiNodes/LLM"

    def execute_structured_prompt(self, llm_model, keep_model_loaded, **kwargs):
        final_prompt = self._build_prompt(**kwargs)
        if not isinstance(llm_model, Llama):
            raise ValueError("LLM Model not provided or is invalid.")
        
        # Remove non-generation kwargs before passing to the model
        kwargs.pop("llm_model", None)
        kwargs.pop("keep_model_loaded", None)
        
        output = llm_model.create_completion(
            prompt=final_prompt,
            **kwargs,
            seed=kwargs.get("seed", 0) or -1,
            stop=[]
        )
        
        if not keep_model_loaded:
            LLMLoader_Akki.clear_cache()
            
        return (output['choices'][0]['text'].strip(), final_prompt)

    def _build_prompt(self, **kwargs):
        parts = []
        # A defined order might be better than random iteration
        prompt_order = ['persona', 'context', 'rules_instructions', 'input_data', 'task_question', 'few_shot_examples', 'output_format', 'negative_prompt']
        for key in prompt_order:
            value = kwargs.get(key)
            if isinstance(value, str) and value.strip():
                 parts.append(f"### {key.replace('_', ' ').upper()} ###\n{value.strip()}")
        parts.append("### RESPONSE ###")
        return "\n\n".join(parts)

# --- Mappings for this file ---
NODE_CLASS_MAPPINGS = {"LLMStructuredPrompter-Akki": LLMStructuredPrompter_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"LLMStructuredPrompter-Akki": "LLM Structured Prompter v1.0 - Akki"}