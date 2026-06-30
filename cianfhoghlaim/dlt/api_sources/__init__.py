"""REST API DLT sources for the Cianfhoghlaim platform.

These dlt sources consume REST APIs (GitHub, LinkedIn, ResearchGate, ...)
and produce structured records for downstream BAML extraction. Per the
v3 consolidation plan (consolidate-cianfhoghlaim-subdirs Phase A.6),
the 3 API-source modules are consolidated here from the legacy top-level
dirs (github/, linkedin/, researchgate/).

Modules:
- github — GitHub repos, languages, READMEs
- linkedin — LinkedIn profile extraction
- researchgate — ResearchGate profile + publications
"""
from .github import *
from .linkedin import *
from .researchgate import *
