# AkkiNodes Suite: Workflow Diagram (v77.0 - Production Certified)

This document outlines the standard data flow for the AkkiNodes Suite, which is organized into four distinct, modular production phases. Each phase produces a canonical data artifact (e.g., a screenplay, a CSV) that serves as the validated starting point for the next phase. This "Workflow Checkpointing" architecture allows for a flexible, iterative creative process.

---

### **Phase 1: Narrative Development**
*   **Goal:** To transform a simple idea into a complete, well-structured, and machine-readable screenplay.
*   **Flow:**
    1.  `Story Writer (v5.2)` generates a prose story using its robust "Orthogonal Input" architecture to ensure factual consistency.
    2.  `ScriptCrafter P1 (Bible) (v7.2)` analyzes the story to create the canonical **Character & World Bibles**.
    3.  `ScriptCrafter P2 (Beat Sheet)` creates a structural blueprint.
    4.  `ScriptCrafter P3 (Screenplay) (v16.8)` synthesizes all previous documents into a final, perfectly formatted screenplay using its "Creative Draft + Hybrid Heuristic Parser" architecture.
*   **Canonical Output Artifact:** A clean, industry-standard **Screenplay (`.txt`)**.

---

### **Phase 2: Pre-Production & Data Consolidation**
*   **Goal:** To translate the screenplay into a single, canonical, spreadsheet-like data file that governs the entire visual production.
*   **Flow:**
    1.  `AI Cinematographer (Pro) (v3.9)` reads the screenplay and uses its "Hybrid AI + Deterministic Resolver" architecture to generate a raw, detailed, and factually-aware shot-by-shot breakdown (`PreQC` file).
    2.  `AI QC Supervisor` ingests the raw breakdown and performs automated sanitization, removing "junk" assets (`PostQC` file).
    3.  `Pro Shot List Parser (v9.4)` ingests the clean breakdown and uses its "Context-Aware Two-Pass Transform" logic to produce the final, canonical production CSV.
*   **Canonical Output Artifact:** A definitive **Production Shot List (`.csv`)**.

---

### **Phase 3: Visual Development (Lookdev)**
*   **Goal:** To establish the final, approved "art direction" for every character and set in the production.
*   **Flow:**
    1.  `Asset Selector` reads the **Phase 2 CSV** to provide master lists of all required assets.
    2.  The user selects a specific character or set.
    3.  `AI Character Lookdev` or `AI Set Lookdev` is run. These nodes use their internal multi-stage pipelines to generate rich, detailed, story-specific prompts. A final "Python Enforcer" stage guarantees factual correctness.
*   **Canonical Output Artifacts:** A complete library of **Lookdev Prompts (`.txt`)** and their corresponding **Lookdev Images (`.png`)** for all characters and set variations.

---

### **Phase 4: Shot Production (Final Prompting)**
*   **Goal:** To combine the established art direction from Phase 3 with the specific action of a single shot to create the final, ready-to-render image prompt.
*   **Flow:**
    1.  `Shot Selector` reads the **Phase 2 CSV** to isolate all data for a single shot.
    2.  `Shot Asset Loader` reads the **Phase 3 Lookdev Assets** required for that specific shot.
    3.  `AI Scene Choreographer (Bible)` acts as the definitive engine for this phase. It ingests the CSV data and all relevant lookdev prompts, then uses its internal, multi-stage AI pipeline ("Director" and "Promptsmith" stages) to generate the final, bible-aware, and lookdev-consistent prompts for all shots in a scene.
*   **Canonical Output Artifact:** A final, ready-to-render **Shot Prompt (`.txt`)** for a single shot.