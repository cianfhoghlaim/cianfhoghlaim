# CEFR Learner Analytics Capability

## Purpose

`cefr-learner-analytics` is the analytics surface that maps each
learner's Celtic language progress (Irish, Scottish Gaelic, Welsh,
Cornish, Manx, Breton) to the Common European Framework of
Reference (CEFR) levels A1-C2 and emits dashboards for educators
+ parents + the learner themselves.

This capability is referenced by:
- `openspec/changes/2026-09-15-celtic-language-corpus-extension-v1`

## Requirements

### Requirement: CEFR level mapping

The capability SHALL emit one CEFR level per (learner, language)
pair based on the learner's assessment history.

### Requirement: 6 Celtic language coverage

The capability SHALL cover 6 Celtic languages: Irish (ga),
Scottish Gaelic (gd), Welsh (cy), Cornish (kw), Manx (gv), Breton
(br).

### Requirement: Learner dashboard

The capability SHALL expose a marimo dashboard that shows each
learner's CEFR level across all 6 languages + a recommended next
chamber per the Evidence Ladder.

### Requirement: Cognate detection

The capability SHALL emit cognate detection rows linking vocabulary
across the 6 Celtic languages so the learner can leverage known
vocabulary when learning a new Celtic language.
