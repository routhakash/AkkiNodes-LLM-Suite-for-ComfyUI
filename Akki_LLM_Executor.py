from llama_cpp import Llama
from .Akki_LLM_Loader import LLMLoader_Akki

class LLMExecutor_Akki:
    @classmethod
    def INPUT_TYPES(cls): return {"required": {"llm_model": ("LLM_MODEL",), "prompt": ("STRING", {"multiline": True, "default": "Describe the universe."}), "max_tokens": ("INT", {"default": 256}), "temperature": ("FLOAT", {"default": 0.7}), "top_p": ("FLOAT", {"default": 0.95}), "top_k": ("INT", {"default": 40}), "seed": ("INT", {"default": 0}), "keep_model_loaded": ("BOOLEAN", {"default": True}),}}
    RETURN_TYPES, RETURN_NAMES, FUNCTION, CATEGORY = ("STRING",), ("text",), "execute_llm_prompt", "AkkiNodes/LLM"
    def execute_llm_prompt(self, llm_model, prompt, max_tokens, temperature, top_p, top_k, seed, keep_model_loaded):
        if not isinstance(llm_model, Llama): raise ValueError("LLM Model not provided or is invalid.")
        output = llm_model.create_completion(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k, seed=seed if seed > 0 else -1, stop=[])
        if not keep_model_loaded: LLMLoader_Akki.clear_cache()
        return (output['choices'][0]['text'].strip(),)

NODE_CLASS_MAPPINGS = {"LLMExecutor-Akki": LLMExecutor_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"LLMExecutor-Akki": "LLM Text Executor v1.0 - Akki"}