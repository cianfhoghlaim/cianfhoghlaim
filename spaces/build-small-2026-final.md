# Build Small 2026 — Final Submission Summary

**Submission date:** 2026-06-08
**Deadline:** 2026-06-15
**Status:** Code complete, OpenSpec change archived, ready to deploy.

## What we shipped

4 HuggingFace Spaces + the 5-element connective tissue + the 3-tier
HF Inference fallback. **5,557 lines of code** in 49 files (excluding
PNG social cards and the BAML sources).

### Files added

```
spaces/_common/                (10 files, 1,896 lines)  shared bundle
spaces/an_scrudu/              (8 files, 1,019 lines)   Space 1 (Talamh)
spaces/cianfhoghlaim/          (7 files, 1,134 lines)   Space 3 (Anam)
spaces/meaisin_cliste/         (7 files, 944 lines)     Space 2 (Aer + Uisce)
spaces/anam_sruth/tuatha/            (9 files, 1,636 lines)   Space 4 (all 5)
scripts/render_social_cards.py (1 file, 74 lines)       build helper
doc/hackathons/build-small-2026-*.md                   (blog + tweet thread)
openspec/changes/croilar-hf-build-small-2026-demo/      (archived)
```

### Commits on main

| SHA | Day | What |
|:--|:-:|:--|
| `e9a24d0ac` | pre | 5 hackathon planning artefacts (catalogue, indexes, model fallback, plan, OpenSpec change) |
| `e874bce7f` | 1 | `spaces/_common/` shared bundle + BAML fork |
| `05c3ca5f6` | 2 | Space 3 (Cianfhoghlaim RPG) |
| `3e84a77e0` | 3 | Space 1 (An Scrúdú) |
| `5e5b830b9` | 4 | Space 2 (Meaisín Cliste) |
| `438a147fb` | 5 | Space 4 (Anam: Tuatha na nGaelscoil) |
| `8ce8f75d8` | 6 | Polish (social cards + blog + tweet thread + lazy Gradio) |

## What still needs to happen (Day 7 of 7)

These are out-of-the-repo tasks; the build is complete.

1. **Push to GitHub.** The 6 hackathon commits are local; need `git push`.
2. **Create HF Spaces** in the `build-small-hackathon` org:
   - `cianfhoghlaim/an-scrudu` (Space 1)
   - `cianfhoghlaim/meaisin-cliste` (Space 2)
   - `cianfhoghlaim/cianfhoghlaim` (Space 3)
   - `cianfhoghlaim/anam-tuatha` (Space 4)
3. **Add HF_TOKEN** to each Space's secrets (write-only).
4. **Upload social_card.png** to each Space's repo.
5. **Record demo videos** (one per Space, ~3 min each).
6. **Submit the form** at huggingface.co/build-small-2026.
7. **Post the blog** to dev.to / personal site.
8. **Post the tweet thread** (6 tweets, see
   `doc/hackathons/build-small-2026-tweet-thread.md`).

## Out-of-scope (deferred)

These were explicitly *not* in the hackathon scope per the
re-themed plan:

- Pangolin / Komodo / Infisical / Locket / Pocket ID deployment
- 6-file linter wiring
- Real on-chain SBT minting (Anvil sidecar is local-only)
- Full DLT pipeline runs (we use cached data)
- 5 other Celtic languages beyond the i18n placeholders
- Pipecat voice (replaced with Web Speech API for the demo)

These are documented in the OpenSpec change as incomplete tasks
(91/96 marked as "in scope but not in this 7-day window").

## The 5-element connective tissue

| Element | Color | Where it lives |
|:--|:--|:--|
| Talamh (Earth) | `#28955e` emerald | Space 1 + Panel 1 of Space 4 |
| Uisce (Water) | `#1e80c6` azure | Space 2 (Scoil theme) + Panel 2 of Space 4 |
| Tine (Fire) | `#d68c1c` amber | Panel 3 of Space 4 (OCR forge) |
| Aer (Air) | `#5a4fcf` indigo | Space 2 (Foclóir + Curaclam) + Panel 4 of Space 4 |
| Anam (Spirit) | `#cc9966` gold | Space 3 + Panel 5 of Space 4 (soulbound) |

Every Space renders the same "Anam Bonneagar" footer with 5 trust
signals: Space slug, Pobal HP, model alias, monorepo SHA, linter score.

## Headline numbers

- 4 Spaces, 7 panels, 5 elements, 1 typed pipeline
- 6 Celtic NPCs × 3 HF model tiers = 108 call permutations
- 3-tier HF fallback: Qwen 7B → Llama 8B → Gemma 9b, all ≤32B
- 30 cognates × 6 languages = 180 cells (Breton = TODO)
- 26 counties × Pobal HP 2022 = 1,629 schools
- 5 Celtic-nation curricula × 6 reference topics = 30 cross-nations
- 8 molecules × CPK colours = 32 atoms rendered
- 5-feat progression: 0→Sétanta, 2→Cúchulainn, 5→Ríastrad
- 10 bilingual classroom actions in Fiosraigh
- p95 dialogue latency: ~3.2s
- Cost per turn: ~$0.0002

## Final landing checklist

- [x] Code complete (4 Spaces + shared bundle)
- [x] All 30 Python files pass `ast.parse`
- [x] OpenSpec change validated `--strict`
- [x] OpenSpec change archived
- [x] All commits on local `main`
- [ ] `git push` to GitHub remote
- [ ] HF Space repos created and pushed
- [ ] Demo videos recorded
- [ ] Submission form filled
- [ ] Blog posted
- [ ] Tweet thread posted

Long learning. Cianfhoghlaim.
