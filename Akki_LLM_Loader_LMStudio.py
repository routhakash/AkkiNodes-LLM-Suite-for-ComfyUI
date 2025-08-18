# Node: LLM Loader (LM Studio) v1.0

from .shared_utils import LMStudioLlamaProxy

class LLMLoaderLMStudio_Akki:
    """
    This node connects to a running LM Studio server and creates a proxy object
    that can be used by other AkkiNodes executor nodes.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "server_address": ("STRING", {"default": "http://localhost:1234/v1"}),
            }
        }

    RETURN_TYPES = ("LLM_MODEL",)
    RETURN_NAMES = ("llm_model",)
    FUNCTION = "load_from_lm_studio"
    CATEGORY = "AkkiNodes/LLM"

    def load_from_lm_studio(self, server_address):
        print(f"[LMStudioLoader-Akki] Creating API proxy for server at: {server_address}")
        # The node's only job is to create and return our special proxy object.
        proxy_model = LMStudioLlamaProxy(base_url=server_address)
        return (proxy_model,)

# --- Mappings for this file ---
NODE_CLASS_MAPPINGS = {"LLMLoaderLMStudio-Akki": LLMLoaderLMStudio_Akki}
# **CRITICAL FIX**: Removed the extraneous single quote at the end of the line.
NODE_DISPLAY_NAME_MAPPINGS = {"LLMLoaderLMStudio-Akki": "LLM Loader (LM Studio) v1.0 - Akki"}