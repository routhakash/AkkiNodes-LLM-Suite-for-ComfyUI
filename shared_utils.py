# shared_utils.py for AkkiNodes

import os
import re
import json
from openai import OpenAI

def get_wildcard_list(filename):
    try:
        file_path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines: return lines
    except Exception as e:
        print(f"[AkkiNodes] Warning: Could not read wildcard file {filename}. Error: {e}")
    return [f"Could not load {filename}"]

def report_token_usage(node_name, completion_output):
    try:
        usage = completion_output.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        print(f"[{node_name}] Token Usage: TOTAL: {total_tokens} (Input: {prompt_tokens} + Output: {completion_tokens})")
    except Exception as e:
        print(f"[{node_name}] Warning: Could not generate token report. Error: {e}")

def extract_tagged_content(text, tag="main_output"):
    start_tag = f"//---START_{tag.upper()}--//"
    end_tag = f"//---END_{tag.upper()}--//"
    start_index = text.find(start_tag)
    if start_index == -1: return text
    start_index += len(start_tag)
    end_index = text.find(end_tag, start_index)
    if end_index == -1: return text[start_index:].strip()
    return text[start_index:end_index].strip()

class LMStudioLlamaProxy:
    """
    Acts as a proxy to an LM Studio server.
    v1.3 provides a definitive fix for the 'stop' token issue by building the
    request payload manually for maximum robustness.
    """
    def __init__(self, base_url="http://localhost:1234/v1"):
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.model_name = "lm-studio"

    def create_completion(self, prompt, max_tokens=2048, temperature=0.7, top_p=0.95, top_k=40, stop=None, seed=0, **kwargs):
        
        # --- DEFINITIVE FIX: Manually construct the API payload ---
        # This ensures that all parameters are of the correct type and that
        # the 'stop' parameter is only included when it is a non-empty list.
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }

        # Only add the 'stop' key if the 'stop' list is valid and not empty.
        if stop and isinstance(stop, list) and len(stop) > 0:
            payload['stop'] = stop

        print("\n[LMStudioLlamaProxy] Preparing to send request to LM Studio Server...")
        print(f"[LMStudioLlamaProxy] API Payload being sent:\n{json.dumps(payload, indent=2)}\n")
        # --- END OF FIX ---

        try:
            # Use the manually constructed payload
            completion = self.client.chat.completions.create(**payload)
            
            response_text = completion.choices[0].message.content
            usage_data = completion.usage

            formatted_output = {
                "choices": [{"text": response_text}],
                "usage": {
                    "prompt_tokens": usage_data.prompt_tokens,
                    "completion_tokens": usage_data.completion_tokens,
                    "total_tokens": usage_data.total_tokens,
                }
            }
            return formatted_output
        except Exception as e:
            print(f"[LMStudioLlamaProxy] API call failed: {e}")
            return {
                "choices": [{"text": f"ERROR: API call to LM Studio failed. Is the server running? Details: {e}"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }