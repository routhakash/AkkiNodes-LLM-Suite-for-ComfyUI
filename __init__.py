# __init__.py for AkkiNodes

import importlib
import os
import traceback

# --- ANSI Color Codes for Console Output ---
C_RED = '\033[91m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_END = '\033[0m'

print(f"{C_GREEN}--- Loading AkkiNodes Suite ---{C_END}")

node_files = [
    # LLM Core
    "Akki_LLM_Loader",
    "Akki_LLM_Loader_LMStudio",
    
    # Narrative Pipeline ("Narrative Bible" Architecture)
    "Akki_Story_Composer",
    "Akki_Story_Writer",
    "Akki_ScriptCrafter_P1_Bible",
    "Akki_ScriptCrafter_P2_Bible",
    "Akki_ScriptCrafter_P3_Bible",

    # Pre-Production Pipeline (Definitive)
    "Akki_AI_Cinematographer",
    "Akki_AI_QC_Supervisor",
    "Akki_Pro_Shot_List_Parser",
    "Akki_Asset_Selector",
    "Akki_Shot_Selector",
    "Akki_AI_Shot_Duration_Calculator",

    # Look Development Pipeline (Bible-Aware)
    "Akki_Lookdev_Loader",
    "Akki_Character_Lookdev_Bible",
    "Akki_Set_Lookdev_Bible",

    # Shot Production Pipeline (Consolidated)
    "Akki_Project_Director",
    "Akki_Shot_Asset_Loader",
    "Akki_Scene_Choreographer_Bible",
    
    # --- DEPRECATED NODES (Functionality absorbed into AISceneChoreographerBible) ---
    # "Akki_Dossier_Assembler_Sanitizer",
    # "Akki_Prompt_Weaver_Pro",
    
    # Video Production
    "Akki_Video_Prompt_Engineer",

    # File I/O
    "Akki_File_IO", 
    "Akki_Scene_Choreography_Loader",
    "Akki_Keyword_Loader",
    "Akki_Video_Prompt_Loader",
    "Akki_Generic_Image_Loader",
    "Akki_Generic_Image_Namer",
    "Akki_Generic_File_IO",
    # --- DEPRECATED LOADERS ---
    # "Akki_Dossier_Loader",
    # "Akki_Prompt_Loader",
]

# --- Master Dictionaries ---
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# --- Dynamic Import and Merging ---
for module_name in node_files:
    if module_name.startswith("#"): continue
    try:
        module = importlib.import_module(f".{module_name}", __name__)
        if hasattr(module, "NODE_CLASS_MAPPINGS"):
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
        if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
        print(f"  {C_GREEN}[+] Successfully loaded: {module_name}.py{C_END}")
    except ImportError as e:
        if "No module named" in str(e) and module_name in str(e):
             print(f"  {C_YELLOW}[-] Skipping retired node: {module_name}.py{C_END}")
        else:
            print(f"  {C_RED}[!] FAILED to load nodes from {module_name}.py{C_END}")
            print(f"  {C_YELLOW}[!] Error: {e}{C_END}")
            traceback.print_exc()
    except Exception as e:
        print(f"  {C_RED}[!] FAILED to load nodes from {module_name}.py{C_END}")
        print(f"  {C_YELLOW}[!] Error: {e}{C_END}")
        traceback.print_exc()

WEB_DIRECTORY = "js"
print(f"{C_GREEN}--- AkkiNodes Suite loading complete. Found {len(NODE_CLASS_MAPPINGS)} nodes. ---{C_END}")
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']