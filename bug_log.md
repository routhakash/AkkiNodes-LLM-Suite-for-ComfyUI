# AkkiNodes Suite - Official Bug Log & Future Improvements List (v77.0.0)

This document tracks all identified issues in the "Text-to-Production-Data" pipeline. This version reflects the status after the successful "Trixie Stevens" end-to-end test run.

---

### **Project-Wide Architectural Debt & Process Failures**

*   **Issue:** Code Duplication in Internal Asset Loading
    *   **Severity:** 🔴 Critical
    *   **Status:** **PENDING (AUDIT COMPLETE).** Architectural audit confirmed that prompt-loading helper functions are duplicated across at least 6 node files (`ScriptCrafter_P3`, `Story_Writer`, `Shot_Duration_Calculator`, `Set_Lookdev`, `Character_Lookdev`, `Scene_Choreographer`). The proposed solution to refactor this logic into the central `shared_utils.py` module is validated and is the highest priority architectural task.

*   **Issue:** Violation of "Fix Data at the Source" Principle (`AI QC Supervisor`)
    *   **Severity:** 🟡 Major
    *   **Status:** **PENDING (AUDIT COMPLETE).** Audit confirmed the `AIQCSupervisor` exists solely to clean junk asset keys (e.g., `PROPS (None)`) from the `AICinematographer`'s output. The validated solution is to harden the `AICinematographer` prompt with stricter negative constraints and add a deterministic Python function within the `AICinematographer` itself to discard any remaining malformed keys before output. This will render the `AIQCSupervisor` obsolete.

*   **Issue:** Strategic Debt in Asset Selector (Semantic Deduplication)
    *   **Severity:** 🟡 Major
    *   **Status:** **PENDING (AUDIT COMPLETE).** Audit confirmed the `AssetSelector` node uses a hard-coded Python dictionary for asset aliases. The proposed solution to move this to a user-editable `aliases.json` file is validated and remains the correct path forward.

*   **Issue:** Documentation & Codebase Desynchronization
    *   **Severity:** 🟠 Minor
    *   **Status:** **PENDING (PARTIALLY RESOLVED).** Core documents are mostly up-to-date. However, the audit found specific version mismatches (e.g., `Set_Lookdev_Bible` displays `v3.1` in the UI but is `v6.0` internally) and README version lag (`v76.0.0` vs `v77.0.0`). A full synchronization pass is required.

*   **Issue:** Inconsistent Prompt Directory Structure
    *   **Severity:** 🔵 Trivial
    *   **Status:** **NEW (FROM AUDIT).** The `_prompts` directory structure is functional but inconsistent and unnecessarily nested (e.g., `_prompts/Choreographer/stage1/` vs. `_prompts/stage1/`). This increases cognitive load for developers.
    *   **Proposed Solution:** Refactor the directory to a flatter, more logical structure (e.g., `_prompts/NodeName/stage_name.txt`) and update the calling code in each node. This is a low-priority task for improving future maintainability.

---

### **Resolved Issues (Validated in "Trixie Stevens" Test Run)**

*   **Node:** `StoryWriter-Akki`
    *   **Issue:** Factual Ground Truth Contradiction (e.g., wrong `period`, wrong antagonist `identity`).
    *   **Status:** **RESOLVED in v5.2.** The re-architecture to use orthogonal inputs (gender, identity, role) and the hardened prompt template have successfully eliminated this failure mode.

*   **Node:** `AI ScriptCrafter P1 (Bible)`
    *   **Issue:** Logical Contradiction in World Bible.
    *   **Status:** **RESOLVED.** This was a downstream symptom of the `StoryWriter`'s failure. With clean input from `StoryWriter v5.2`, this node now produces a logically consistent World Bible.

*   **Node:** `AI ScriptCrafter P3 (Bible)`
    *   **Issue:** Creative Fidelity Failure (Hallucination of non-canonical scenes).
    *   **Status:** **RESOLVED in v16.8.** The new "Hierarchical Mandate" in the Stage 1 prompt has successfully prevented the AI from inventing scenes not present in the source story text.

*   **Node:** `AI ScriptCrafter P3 (Bible)`
    *   **Issue:** Inconsistent Dialogue Formatting (Incorrect capitalization of character cues).
    *   **Status:** **RESOLVED in v16.8.** The new "Hybrid Heuristic Parser" in the Python `_master_post_processor` now correctly identifies and formats character cues regardless of case.

*   **Node:** `AICinematographer (Pro)`
    *   **Issue:** Factual Contradiction (Hallucinating incorrect character ages).
    *   **Status:** **RESOLVED in v3.9.** The new `<factual_fidelity_protocol>` in the prompt has successfully instructed the AI to respect and transcribe factual details from the screenplay.

*   **Node:** `ProShotListParser`
    *   **Issue:** Pronoun Normalization Failure & Silent Data Loss (e.g., `CHARACTERS: She`).
    *   **Status:** **RESOLVED.** This was fixed at the source by the `AICinematographer v3.9` prompt, which no longer outputs unresolved pronouns.

*   **Node:** `ProShotListParser`
    *   **Issue:** Critical Data Formatting Failure (Unescaped brackets in CSV).
    *   **Status:** **RESOLVED.** This was a symptom of the `AICinematographer`'s old output format. The hardened prompts now produce cleaner lists that do not cause this downstream parsing error.

*   **Node:** `ProShotListParser`
    *   **Issue:** Dialogue Parsing Failure (Incorrectly prepending character cues).
    *   **Status:** **RESOLVED in v9.4.** The refactored `_sanitize_dialogue` function now correctly isolates and outputs only the spoken words, producing a clean `DIALOGUE` column in the final CSV.

---

### **Remaining Minor/Latent Issues (Non-Showstoppers)**

*   **Node:** `AICinematographer (Pro)`
    *   **Issue:** Generation of Junk Data Keys (e.g., `PROPS (None): None`).
    *   **Severity:** 🟠 Minor
    *   **Status:** **ACTIVE FAILURE.** The AI still produces these minor formatting errors in its raw output. This is currently handled correctly by the `AIQCSupervisor` and is not a pipeline blocker.

*   **Node:** `AI ScriptCrafter P1 (Bible)`
    *   **Issue:** Minor Character Hallucination (e.g., misinterpreting objects as characters).
    *   **Severity:** 🟠 Minor
    *   **Status:** **PENDING.** This remains a known, non-critical limitation of the AI's pattern recognition.