# Phase 3: Pruning and Converging - Archival & Reinstatement Guide

## Overview

This document serves as the historical record and "undo/reinstatement map" for the **Phase 3 Pruning and Converging** operation. 

**Why was this done?** 
The repository's `.git` history had grown to 5.1GB due to trapped large files (comics, math PDFs, MP4s, heavy `node_modules`), which completely blocked pushing to remote Git servers. To successfully deploy "Core Version Zero" for the Gemini Live Agent Hackathon (which strictly focuses on English education pipelines for the UK and Ireland), we needed to aggressively prune the repository footprint.

**Important Note:** The removal of advanced features like `teanga/` (multilingualism), `lance/` (super-powerful indexing), and `web/` (frontend UI) was **not** a permanent deletion or an abandonment of these goals. They were temporarily filtered out to secure a stable MVP. This document provides the context for sub-agents to understand what was removed so it can be smoothly reinstated in subsequent phases.

---

## What Was Removed & Why

### 1. Research & Advanced Features (To Be Reinstated)
These directories were completely removed from the Git history but are integral to the ultimate vision of the platform. They will be reintroduced gradually:
*   **`education/research/teanga/`**: Contained advanced multilingual data (Breton, Old Irish, Scottish Gaelic) and Universal Dependencies. Removed to maintain the hackathon's English-language focus. Will be reinstated for the comprehensive Celtic education platform.
*   **`education/research/lance/`**: LanceDB and Ray integrations. Removed for MVP simplicity and to reduce dependencies.
*   **`education/research/web/`**: Contained heavily nested `node_modules` and raw UI designs/inspirations.
*   **`education/research/agents/` & `infrastructure/`**: Experimental multi-agent orchestration tools (agno, stagehand) and heavy infrastructure provisioning scripts. 

### 2. Large Media & Extraneous Blobs (Permanently Pruned)
These items were blocking the Git push due to massive file sizes and were permanently purged:
*   **Comics & Media:** `cian/favourite_comics/` containing numerous PNGs and 60MB+ PDFs.
*   **Math/University Notes:** `education/dlt_sources/filesystem/tertiary/` and various PDFs (e.g., DuckDB research, non-linear systems) exceeding 40MB.
*   **Video Files:** Untracked `.mp4` files buried in research folders.

---

## Technical Execution 

To achieve this without simply adding a standard commit (which wouldn't reduce the `.git` pack size), the following actions were executed:
1.  **Staged Pruning:** Physically deleted the directories.
2.  **Path Inversion (`git filter-repo`):** Rewrote the entire repository history to pretend the out-of-scope paths never existed, freeing up index space.
3.  **Blob Stripping (`git filter-repo --strip-blobs-bigger-than 40M`):** Searched the entire history and eliminated any orphaned blob larger than 40MB.
4.  **Garbage Collection (`git gc --prune=now --aggressive`):** Flushed the dangling references, successfully reducing the `.git/objects/pack` size from 5.1GB to ~4.6GB (and shrinking).

---

## Future Protocol: The Local Archive Rule

To prevent the `.git` folder from bloating again while allowing us to retain heavy files, experimental code, and future UI components locally, **we are instituting an automated Archive/Ignore rule.**

### Rule for AI Sub-Agents:
If you are generating heavy assets, pulling large datasets, or scaffolding temporary UI environments (`node_modules`), you MUST utilize a local archive directory that is ignored by Git.

1.  **Use the `_archive/` or `local_vault/` Directories:** 
    Any future research or reinstatements of heavy data should initially be placed in directories explicitly added to `.gitignore`.
2.  **Explicit `.gitignore` Additions:** 
    *   Ensure all `node_modules/` remain strictly ignored.
    *   Add `*.mp4`, `*.pdf` (if >10MB), and `*.db` to `.gitignore` to prevent accidental history bloat.
3.  **Reinstating Features:**
    When reinstating `teanga/` or `lance/`, do so selectively. Only commit the source code and configuration. Large datasets or binary models associated with them must remain in the `.gitignored` archive directories or utilize Git LFS (Large File Storage) if they strictly must be tracked.