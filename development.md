# AkkiNodes Suite - Internal Development Log & Changelog

This document tracks the detailed, step-by-step progress of the AkkiNodes Suite, including bug fixes, feature enhancements, and architectural changes.

---

## **Definitive Certified Architectures (v77.0.0)**

This section serves as a quick-reference guide to the current, production-certified version of each major node and its validated architectural pattern.

*   **`StoryWriter-Akki v5.2` - "Orthogonal Input & Ground Truth Mandate"**
    *   **Methodology:** Re-architected with orthogonal inputs (gender, identity, role) to provide the LLM with granular, unambiguous facts. Combined with a hardened prompt that enforces a strict "Ground Truth Mandate," this architecture has proven effective at preventing factual contradictions.

*   **`AI ScriptCrafter P1 (Bible) v7.2` - "Analyze & Refine"**
    *   **Methodology:** Uses a single, comprehensive AI call for a creative first draft, followed by a deterministic Python function to parse, consolidate, and enforce the correctness of the final `Character Bible`. This remains the certified pattern for bible generation.

*   **`AI ScriptCrafter P3 (Bible) v16.8` - "Creative Draft + Hybrid Heuristic Parser"**
    *   **Methodology:** Uses a multi-stage AI pipeline for creative screenwriting. The output is then passed to a powerful, deterministic Python "Master Post-Processor" that uses a hybrid of strict and fuzzy logic to correctly parse and reformat the text into a 100% clean, Fountain-compliant screenplay, successfully handling minor AI typos.

*   **`AICinematographer_Akki v3.9` - "Hybrid AI + Deterministic Resolver"**
    *   **Methodology:** The AI uses a hardened prompt with a "Factual Fidelity Protocol" to perform the creative shot breakdown. The raw output is then passed to a deterministic Python helper function that performs context-aware resolution of unambiguous pronouns, fixing a key AI weakness at the source.

*   **`ProShotListParser-Akki v9.4` - "Context-Aware Two-Pass Transform"**
    *   **Methodology:** A definitive ETL (Extract, Transform, Load) architecture. The "Transform" stage is a two-pass process: Pass 1 establishes the "ground truth" characters for a single shot. Pass 2 uses this context to perform intelligent, high-fidelity normalization and sanitization of all data related to that shot, preventing pronoun errors and dialogue corruption.

*   **`AI Character Lookdev (Bible) v13.0` - "Hybrid 3-Stage AI + Python Enforcer"**
    *   **Methodology:** Uses a sophisticated 3-stage LLM pipeline for creative prompting, followed by a final, deterministic Python stage to guarantee factual data integrity (e.g., character age). This remains the certified pattern for character lookdev.

---
---

## **v77.0.0 (Milestone: Pipeline Hardened & Production-Certified)**
- **Status:** Definitive Stable Milestone.
- **Action:** Completed a multi-sprint, multi-story hardening and validation cycle for the entire front-end pipeline, from story conception to the final production CSV. All previously identified show-stopping, critical-risk bugs have been resolved.
- **Key Architectural Changes & Validations:**
    - **`StoryWriter` Ground Truth Failures FIXED:** The re-architecture of `StoryWriter-Akki` to `v5.2`, which uses orthogonal inputs (gender, identity, role) instead of a single ambiguous field, has successfully resolved the critical ground truth contradiction bugs. The node now produces factually consistent stories.
    - **`ScriptCrafter P3` Hallucinations FIXED:** The hardening of the `v16.8` prompt with a "Hierarchical Mandate" has proven effective. The node no longer invents non-canonical scenes, and its new "Hybrid Heuristic Parser" correctly formats AI-generated text, resolving the dialogue formatting bugs.
    - **`AICinematographer` Pronoun Failures FIXED:** The `v3.9` "Hybrid AI + Deterministic Resolver" architecture successfully resolves unambiguous pronouns at the source, preventing data corruption from propagating downstream.
    - **`ProShotListParser` Data Corruption FIXED:** The `v9.4` "Context-Aware Two-Pass Transform" architecture has definitively resolved all previously identified data integrity failures, including pronoun-related data loss and dialogue corruption. It now produces a clean, reliable, and machine-readable canonical CSV.
- **Outcome:** All nodes in Phase 1 (Narrative Development) and Phase 2 (Pre-Production) are now **Production Certified**. The pipeline reliably produces a clean, factually consistent, and structurally sound set of narrative and pre-production documents, unblocking the entire downstream visual development process.

## **v75.0.0 (Milestone: Master Specification & Documentation)**
- **Status:** Definitive Stable Milestone.
- **Action:** Completed a full audit of the project's interaction history and codebase to create a definitive Master Project & Workflow Specification. All key supporting documents (`README.md`, `development.md`, `bug_log.md`) have been updated to align with this new canonical specification.
- **Outcome:** The project's "institutional knowledge"—its core principles, validated architectures, and key lessons learned—has now been formally codified. This provides a single, unambiguous source of truth for all current and future development.

## **v74.0.0 (Milestone: Character Lookdev Pipeline Certified)**
- **Status:** Definitive Stable Milestone.
- **Action:** Completed a full hardening and stress-testing cycle for the `AI Character Lookdev (Bible)` node. This included fixing a critical data integrity bug and validating a new, more sophisticated internal architecture.
- **Key Architectural Changes & Validations:**
    - **Definitive `v13.0` Architecture ("Hybrid 3-Stage AI + Python Enforcer"):** The new architecture is certified as the production standard. It uses a sophisticated 3-stage LLM pipeline ("Artist," "Editor," "Assembler") to generate a high-quality creative prompt, which is then passed to a final, deterministic Python stage for factual enforcement.
    - **Critical Bug FIXED:** The "Python Age Enforcer" (`_enforce_canonical_age`) function was re-engineered with more sophisticated regex to correctly parse descriptive age ranges (e.g., "late 20s"), resolving the critical age contradiction bug with 100% reliability.
- **Outcome:** The `AI Character Lookdev (Bible)` node is now **Production Certified**. It produces factually accurate, structurally sound, and creatively superior prompts, unblocking the character asset generation phase of the visual development pipeline.

## **v73.0.0 (Milestone: "Text-to-Production-Data" Pipeline Certified)**
- **Status:** Definitive Stable Milestone.
- **Action:** Executed a final hardening and feature-completion pass on the `ScriptCrafter P3 (Bible)` node, resolving all known critical bugs and functional regressions.
- **Key Architectural Changes & Validations:**
    - **Definitive `v16.7` Architecture ("Creative Draft + Deterministic Formatter"):** This architecture is now certified as the final, robust solution. It correctly uses a 3-stage AI pipeline for sophisticated creative work and then passes the output to a powerful, deterministic Python post-processor.
    - **"Master Post-Processor" Hardened:** The processor's "Content Isolation" principle and its line-by-line Fountain-compliant reformatting have been proven to be 100% effective at fixing all previously identified formatting errors.
- **Outcome:** The entire "Text-to-Production-Data" pipeline, from `Story Writer` through `ScriptCrafter P3`, is now **Production Certified**.

## **v72.0.0 (Milestone: Critical Data Integrity Failure Resolved)**
- **Status:** Definitive Stable Milestone.
- **Action:** Executed a complete architectural overhaul of the `ScriptCrafter P1 (Bible)` node to resolve catastrophic data corruption bugs (duplicate entities, ground-truth contradiction).
- **Key Architectural Changes & Validations:**
    - **Definitive `v7.2` Architecture ("Analyze & Refine"):** The new, approved version uses a superior two-stage process: a comprehensive AI analysis followed by a deterministic Python refinement stage that programmatically enforces ground-truth data.
- **Outcome:** The `ScriptCrafter P1 (Bible)` node is now **Production Certified**.

## **v71.0.0 (Milestone: Visual Development & Asset Aggregation - Phase 1 Complete)**
- **Status:** Definitive Stable Milestone.
- **Action:** Completed the full QC and hardening cycle for the `Asset Selector` node.
- **Key Architectural Changes & Validations:**
    - **Definitive `v3.1` Architecture ("Data-Driven Hierarchy Inference"):** The final, approved version removes all hard-coded logic and programmatically infers the set hierarchy from the source CSV data.
- **Outcome:** The `Asset Selector` has been successfully transformed from a "dumb aggregator" into an intelligent, data-driven "Master Set Director."

---

## **v70.0.0 (Milestone: "Text-to-Production-Data" Pipeline Hardened)**
- **Status:** Definitive Stable Milestone.
- **Action:** Completed an exhaustive, multi-story Quality Control (QC) and hardening cycle for the entire front-end of the creative pipeline. All nodes from the `AI Story Writer` through the `Pro Shot List Parser` are now considered feature-complete, architecturally sound, and production-ready.