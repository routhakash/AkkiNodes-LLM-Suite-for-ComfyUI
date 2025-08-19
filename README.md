<p align="center">
  <img src="https://github.com/user-attachments/assets/cde7c0c7-c60f-4829-80bd-17be62044ce6" alt="AkkiNodes Banner" width="1080"/>
</p>

# 🎭 AkkiNodes LLM Suite: Your Personal AI Film Studio

<p align="center">
  <a href="https://github.com/routhakash/AkkiNodes-LLM-Suite-for-ComfyUI/stargazers"><img src="https://img.shields.io/github/stars/routhakash/AkkiNodes-LLM-Suite-for-ComfyUI?style=social" alt="Stars"></a>
  <a href="https://github.com/routhakash/AkkiNodes-LLM-Suite-for-ComfyUI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/routhakash/AkkiNodes-LLM-Suite-for-ComfyUI?color=blue" alt="License"></a>
  <img src="https://img.shields.io/badge/Version-v77.0.0-blueviolet" alt="Version">
  <img src="https://img.shields.io/badge/ComfyUI-Compatible-brightgreen" alt="ComfyUI">
</p>

Welcome to the **AkkiNodes Suite**, a professional, end-to-end creative pipeline for ComfyUI. This suite empowers you to go from a simple idea to a fully realized visual product—be it a short film, a cinematic, or a visual novel—all within your local ComfyUI environment.

---

## ✨ Core Philosophy: 100% Local, 100% Private

> ### 🌐 No Internet? No Problem.
> This entire suite is built around one core principle: **your creativity should never depend on a cloud service.** All Large Language Model (LLM) processing happens directly on your own computer. This means:
> - ✅ **Total Privacy:** Your scripts, stories, and ideas stay on your machine.
> - ✅ **No API Keys, No Fees:** Run as many generations as you want, for free.
> - ✅ **Offline Capable:** Once set up, you can generate content without an internet connection.
> - ✅ **Uncensored Creativity:** You have full control over the models you use and the content you create.

---

## ⚙️ Installation Guide

1.  **Clone or Download:**
    *   Clone this repository into your `ComfyUI/custom_nodes/` directory.
    *   Alternatively, download the ZIP, extract it, and place the `AkkiNodes-LLM-Suite-for-ComfyUI` folder inside `ComfyUI/custom_nodes/`.

2.  **Install Dependencies (Windows):**
    *   Navigate into the new `AkkiNodes-LLM-Suite-for-ComfyUI` folder.
    *   **Right-click `install.bat` and select "Run as administrator"**. This only needs to be done once.

3.  **Download a GGUF Model:**
    *   This suite requires a GGUF-format Large Language Model. You can find thousands of compatible models on [Hugging Face's GGUF Model Hub](https://huggingface.co/models?search=gguf).
    *   Place your downloaded `.gguf` file into your `ComfyUI/models/llms/` directory.

4.  **Restart ComfyUI:**
    *   Completely close and restart your ComfyUI instance.

---

## ▶️ Video Tutorial: Full Workflow Demo

[![Watch the tutorial on YouTube](https://img.youtube.com/vi/woMTMyN94CI/maxresdefault.jpg)](https://youtu.be/woMTMyN94CI)

**[Click here to watch the full "Script to Screen" workflow demonstration on YouTube.](https://youtu.be/woMTMyN94CI)**

---

## 🚀 Example Workflow File

You can download the complete ComfyUI workflow file demonstrated in the video tutorial directly from this repository. Drag and drop this file onto your ComfyUI canvas to load the entire workflow.

**[Download the Workflow JSON here](./WorkflowExample/Akki%20LLM%20Agents%20Suits%20WorkflowExample.json)**

---

## 📖 Node Reference (Core Production Suite v77.0.0)

### <div style="background-color: #2a3d4a; padding: 5px; border-radius: 5px;">Phase 1: Narrative Development</div>
*Goal: To transform a simple idea into a complete, well-structured, and machine-readable screenplay.*

#### `AI Story Writer (v5.2)`
The starting point of the entire pipeline. Takes a simple concept and creative parameters to generate a complete prose story.
*   **Architecture:** Uses an **"Orthogonal Input & Ground Truth Mandate"** to ensure factual consistency and prevent logical contradictions in the narrative.

#### `AI ScriptCrafter P1, P2, P3`
An automated "Writer's Room" that adapts the prose story into a professional screenplay.
*   **P1 (Bible) (v7.2):** Creates the canonical **Character Bible** and **World Bible**. Its **"Analyze & Refine"** architecture uses a deterministic Python process to guarantee data accuracy.
*   **P2 (Beat Sheet) (v4.0):** Creates a 15-point structural blueprint for the story.
*   **P3 (Screenplay) (v16.8):** Writes a creatively rich screenplay, then uses a **"Creative Draft + Hybrid Heuristic Parser"** to guarantee perfect, industry-standard formatting.

### <div style="background-color: #3d4a2a; padding: 5px; border-radius: 5px;">Phase 2: Pre-Production & Data Consolidation</div>
*Goal: To translate the screenplay into a single, canonical spreadsheet (CSV) that governs the visual production.*

#### `AI Cinematographer (Pro) (v3.9)`
Acts as the Director of Photography, reading the screenplay and creating a detailed, shot-by-shot breakdown.
*   **Architecture:** Its **"Hybrid AI + Deterministic Resolver"** pattern fixes common AI weaknesses (like pronoun ambiguity) at the source.

#### `AI QC Supervisor (v2.1)`
A data sanitization filter that cleans the raw output from the `Cinematographer`, removing "junk" data to prevent corruption of the production database.

#### `Pro Shot List Parser (v9.4)`
The definitive gatekeeper of clean data. Ingests the clean shot breakdown and produces the final, canonical **production CSV file**.
*   **Architecture:** Employs a **"Context-Aware Two-Pass Transform"** to perform high-fidelity data normalization, preventing data loss and dialogue corruption.

### <div style="background-color: #4a2a4a; padding: 5px; border-radius: 5px;">Phase 3: Visual Development (Lookdev)</div>
*Goal: To establish the final, approved "art direction" for every character and set.*

#### `Asset Selector (v3.6)`
The Production Manager. Reads the final CSV and provides master lists of all assets, allowing the user to select a specific character or set for look development.

#### `AI Character Lookdev (v13.0)` & `AI Set Lookdev (v6.0)`
The Art Department. These nodes generate rich, detailed, story-specific prompts for creating character model sheets and set designs.
*   **Architecture:** Use a **"Hybrid Multi-Stage AI + Python Enforcer"** pattern to guarantee factual details (like a character's age) are 100% correct in the final creative prompt.

### <div style="background-color: #4a3d2a; padding: 5px; border-radius: 5px;">Phase 4: Shot Production (Final Prompting)</div>
*Goal: To combine the art direction from Phase 3 with the action of a single shot to create a final, ready-to-render image prompt.*

#### `Shot Selector (v3.6)` & `Shot Asset Loader (v3.7)`
Utilities for isolating a single shot and fetching all of its required data and lookdev assets (images and prompts) from the canonical files produced in previous phases.

#### `AI Scene Choreographer (Bible) (v4.3)`
The creative engine for this phase. It performs a scene-wide creative pass, ingesting the CSV data and all relevant lookdev prompts to generate bible-aware, lookdev-consistent prompts for all shots in a scene.

### <div style="background-color: #444; padding: 5px; border-radius: 5px;">Utilities</div>

#### `LLM Loader` & `LLM Loader (LM Studio)`
The core nodes for loading your local GGUF language models or connecting to an LM Studio server.

#### `File I/O Nodes`
A comprehensive suite of utilities for project management, allowing for robust saving and loading of any text data (stories, bibles, CSVs, prompts, etc.) to keep your project organized.