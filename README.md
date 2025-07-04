<p align="center">
  <img src="https://github.com/user-attachments/assets/cde7c0c7-c60f-4829-80bd-17be62044ce6" alt="AkkiNodes Banner" width="1080"/>
</p>

# 🎭 AkkiNodes Suite: Your Personal AI Film Studio

<p align="center">
  <a href="https://github.com/YOUR_USERNAME/ComfyUI-AkkiNodes-Suite/stargazers"><img src="https://img.shields.io/github/stars/YOUR_USERNAME/ComfyUI-AkkiNodes-Suite?style=social" alt="Stars"></a>
  <a href="https://github.com/YOUR_USERNAME/ComfyUI-AkkiNodes-Suite/blob/main/LICENSE"><img src="https://img.shields.io/github/license/YOUR_USERNAME/ComfyUI-AkkiNodes-Suite?color=blue" alt="License"></a>
  <img src="https://img.shields.io/badge/Version-v15.1.0-blueviolet" alt="Version">
  <img src="https://img.shields.io/badge/ComfyUI-Compatible-brightgreen" alt="ComfyUI">
</p>

Welcome to the **AkkiNodes Suite**, an advanced collection of ComfyUI nodes designed to build a complete, end-to-end creative pipeline. This suite empowers you to go from a simple idea to a fully realized visual product—be it a short film, a cinematic, or a visual novel—all within your local ComfyUI environment.

---

## ✨ Core Philosophy: 100% Local, 100% Private

<div style="background-color: #1a2a38; padding: 15px; border-radius: 10px; border: 1px solid #3a5a78;">
  <h3 style="margin-top: 0; color: #58a6ff;">🌐 No Internet? No Problem.</h3>
  <p>This entire suite is built around one core principle: <strong>your creativity should never depend on a cloud service.</strong> All Large Language Model (LLM) processing happens directly on your own computer. This means:</p>
  <ul>
    <li>✅ <strong>Total Privacy:</strong> Your scripts, stories, and ideas stay on your machine.</li>
    <li>✅ <strong>No API Keys, No Fees:</strong> Run as many generations as you want, for free.</li>
    <li>✅ <strong>Offline Capable:</strong> Once set up, you can generate content without an internet connection.</li>
    <li>✅ <strong>Uncensored Creativity:</strong> You have full control over the models you use and the content you create.</li>
  </ul>
</div>

---

## 🚀 Workflow at a Glance

This diagram illustrates the core "Story to Screenplay" pipeline, where the output of one node seamlessly becomes the input for the next, creating a powerful chain of context.

![Current Workflow Screenshot](https://github.com/user-attachments/assets/7578a655-9535-49e4-aa9d-7931c582b5ad)

---

## ⚙️ Installation Guide

1.  **Clone or Download:**
    *   Clone this repository into your `ComfyUI/custom_nodes/` directory.
    *   Alternatively, download the ZIP, extract it, and place the `ComfyUI-AkkiNodes-Suite` folder inside `ComfyUI/custom_nodes/`.

2.  **Install Dependencies (Windows):**
    *   Navigate into the new `ComfyUI-AkkiNodes-Suite` folder.
    *   **Right-click `install.bat` and select "Run as administrator"**. This only needs to be done once to install the required `llama-cpp-python` library.

3.  **Download a GGUF Model:**
    *   This suite requires a GGUF-format Large Language Model. You can find thousands of compatible models on [Hugging Face](https://huggingface.co/models?search=gguf).
    *   Place your downloaded `.gguf` file into your `ComfyUI/models/llms/` directory.

4.  **Restart ComfyUI:**
    *   Completely close and restart your ComfyUI instance.

---

## 📖 Node Reference

### <div style="background-color: #2a3d4a; padding: 5px; border-radius: 5px;">🧠 LLM Core Nodes</div>

#### `LLM Loader v2.2 - Akki`
The starting point for all workflows. This node loads a GGUF model into memory and provides crucial feedback on its properties.

![LLM Loader Node](https://github.com/user-attachments/assets/be34d9c4-3f36-46dc-9862-a8ab9b9d9083)

---

### <div style="background-color: #4a2a3d; padding: 5px; border-radius: 5px;">📝 Narrative Generation Nodes</div>

#### `AI Story Writer v3.4 - Akki`
A specialized "Master Narrative Architect." It takes a simple concept and a rich set of parameters to generate a complete, well-structured story.

![AI Story Writer Node](https://github.com/user-attachments/assets/9169d170-b060-4090-968b-56ec78cfd970)

#### `Image Prompt Generator v1.0 - Akki`
A specialized node designed to engineer high-quality image generation prompts for models like Stable Diffusion.

![Image Prompt Generator Node]([SCREENSHOT of Image Prompt Generator v1.0 - Akki])

---

### <div style="background-color: #3d4a2a; padding: 5px; border-radius: 5px;">🎬 The AI ScriptCrafter Suite</div>

This is a professional, three-phase suite of nodes designed to develop a story idea into a fully-fledged screenplay.

#### `AI ScriptCrafter 01 (Foundation) v3.3 - Akki`
Analyzes the generated story to extract the core foundational elements of a screenplay: the logline, theme, and detailed character breakdowns.

![ScriptCrafter 01 Node](https://github.com/user-attachments/assets/2215466f-24f0-4d08-9e3d-48cd0a304d67)

#### `AI ScriptCrafter 02 (Beat Sheet) v3.0 - Akki`
Takes the foundational elements and builds the structural blueprint of the screenplay, following the classic "Save the Cat!" 15-beat structure.

![ScriptCrafter 02 Node](https://github.com/user-attachments/assets/9d307fb7-7ef5-4377-a838-3e3b3baf7b25)

#### `AI ScriptCrafter 03 (Screenplay) v5.1 - Akki`
The final phase. This node acts as an "AI Director," translating the beat sheet into a properly formatted screenplay with cinematic language.

![ScriptCrafter 03 Node](https://github.com/user-attachments/assets/4092c38e-7631-4db8-9242-41bfde9cefe0)

---

## 🗺️ Project Roadmap

This project is ambitious and growing. Here is the vision for the future.

### **Phase 1: Narrative Foundation**
- [x] ✅ Core LLM Loading & Execution
- [x] ✅ Advanced Story Generation Engine
- [x] ✅ Professional Screenplay Generation Suite

### **Phase 2: Visual Pre-Production**
- [ ] 🔲 **Character Sheet Node:** Generate detailed visual descriptions of characters for image models.
- [ ] 🔲 **Location Concept Node:** Generate detailed visual prompts for environments.
- [ ] 🔲 **Storyboard Node:** Automatically generate a sequence of image prompts based on the screenplay's action lines.

### **Phase 3: Automated Production**
- [ ] 🔲 **Image Generation Integration:** Chain storyboard prompts directly into K-Sampler or other image generation nodes.
- [ ] 🔲 **Animatic Creation:** Integrate with animation nodes (like AnimateDiff) to turn storyboards into simple animated sequences.

---

## 💻 Hardware & Software Tested

This suite has been developed and tested on the following configuration.

-   **OS:** Windows 11
-   **CPU:** 13th Gen Intel(R) Core(TM) i7-13700K @ 3.40 GHz
-   **GPU:** NVIDIA GeForce RTX 3060 (12GB VRAM)
-   **ComfyUI Version:** 0.3.43
-   **Python Version:** 3.12.0
-   **PyTorch Version:** 2.6.0+cu126

## 🐛 Known Bugs & Limitations

-   **GPU Offloading:** The pre-built library sometimes fails to offload all layers to the GPU on certain hardware/driver configurations, defaulting to CPU. This is an upstream issue we are actively monitoring.
-   **LLM Reliability:** The quality of the output is highly dependent on the model used. Smaller or less capable models may fail to follow complex instructions or generate perfect JSON. For best results, use models with at least 13B parameters.

## ❤️ Contributing

This is a community-focused project. Pull requests, feature suggestions, and bug reports are highly welcome. Please open an issue to discuss any major changes.

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
