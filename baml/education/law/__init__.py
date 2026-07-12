"""cianfhoghlaim.baml.education.law — Pick-8 Ireland/law BAML extraction registry.

5 BAML files + 1 shared enums file for the 5 operational-law sources
in the Pick-8 Ireland/law quadrant:

- shared_legal_enums.baml  — CourtLevel, LegalAidCategory,
                             LegalAidEligibilityOutcome
- piab.baml                — PIABPage, ExtractPIABPage
- courts.baml              — CourtForm, CourtFee, ExtractCourtForm,
                             ExtractCourtFee
- judgements.baml          — Judgement, ExtractJudgement
- court_rules.baml         — CourtRule, ExtractCourtRule
- legal_aid.baml           — LegalAidPage, LegalAidForm,
                             ExtractLegalAidPage, ExtractLegalAidForm

Re-uses the canonical cross-file types from
`baml/processing/legal_case_profile.baml`
(CaseCategory, Jurisdiction, TimelineEvent, StatuteReference).

Generation: `cd cianfhoghlaim && uv run baml-cli generate`

Reference: openspec/changes/archive/2026-07-07-finalize-v4-landing/
           absorbed/2026-07-06-ireland-legal-pipeline/proposal.md
"""
from __future__ import annotations
