# Node: LLM Loader v2.2

import torch
import folder_paths
from llama_cpp import Llama
import traceback

class LLMLoader_Akki:
    """
    Node to load a GGUF format LLM and prepare it for use.
    v2.2 updates the default context size for modern models.
    """
    _loaded_models = {}
    @classmethod
    def INPUT_TYPES(cls):
        models = []
        try: models.extend(folder_paths.get_filename_list("llms"))
        except: pass
        try:
            for model in folder_paths.get_filename_list("LLM"):
                if model not in models: models.append(model)
        except: pass
        if not models: models = ["No models found"]
            
        return { "required": {
                "gguf_name": (models,),
                "n_gpu_layers": ("INT", {"default": -1, "min": -1, "max": 1000}),
                "main_gpu": ("INT", {"default": 0, "min": 0, "max": 10}),
                # UPDATED: Default context size increased to 32k
                "n_ctx": ("INT", {"default": 32768, "min": 512, "max": 131072, "step": 1024}),
                "n_batch": ("INT", {"default": 512, "min": 32, "max": 8192, "step": 32}),
                "verbose": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("LLM_MODEL", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("llm_model", "model_name", "architecture", "quantization", "model_ctx_size", "offloaded_layers")
    FUNCTION = "load_llm_model"
    CATEGORY = "AkkiNodes/LLM"

    @classmethod
    def clear_cache(cls):
        cls._loaded_models = {}; import gc; gc.collect()
        if torch.cuda.is_available(): torch.cuda.empty_cache()
        print("[LLMLoader-Akki] Model cache cleared.")

    def load_llm_model(self, gguf_name, n_gpu_layers, main_gpu, n_ctx, n_batch, verbose):
        if gguf_name == "No models found": raise ValueError("No GGUF models found.")
        model_path = folder_paths.get_full_path("llms", gguf_name) or folder_paths.get_full_path("LLM", gguf_name)
        if not model_path: raise FileNotFoundError(f"Could not find model '{gguf_name}'.")
        cache_key = (model_path, n_gpu_layers, main_gpu, n_ctx, n_batch)
        if cache_key in self._loaded_models:
            llm = self._loaded_models[cache_key]
        else:
            try:
                llm = Llama(model_path=model_path, n_gpu_layers=n_gpu_layers, main_gpu=main_gpu, n_ctx=n_ctx, n_batch=n_batch, verbose=verbose)
                self._loaded_models[cache_key] = llm
            except Exception as e: traceback.print_exc(); raise e
        
        offloaded_layers_count = 0
        if hasattr(llm, 'model') and hasattr(llm.model, 'n_gpu_layers'): offloaded_layers_count = llm.model.n_gpu_layers
        print(f"[LLMLoader-Akki] >>> Offloaded {offloaded_layers_count} layers to GPU. <<<")
        
        metadata = llm.metadata or {}
        architecture = metadata.get('general.architecture', 'N/A')
        quantization = metadata.get('general.file_type_name', 'N/A').upper()
        model_ctx_size = str(metadata.get(f'{architecture}.context_length', 'N/A'))
        return (llm, gguf_name, architecture, quantization, model_ctx_size, str(offloaded_layers_count))

# --- Mappings for this file ---
NODE_CLASS_MAPPINGS = {"LLMLoader-Akki": LLMLoader_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"LLMLoader-Akki": "LLM Loader v2.2 - Akki"}