"""cocoindex_flows.british_isles.uk — ciancheiltis umbrella CocoIndex App home.

Phase 1 of the ciancheiltis umbrella (Wales / en-cy). This package
houses the CocoIndex v1 App that embeds bilingual en-cy government
pages into the canonical LanceDB table
``lancedb://md:cianfhoghlaim/ciancheiltis/en_cy_chunks``.

Phase 2 of the ciancheiltis umbrella (Republic of Ireland / en-ga).
This package also houses the CocoIndex v1 App that embeds bilingual
en-ga government pages into the canonical LanceDB table
``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi_chunks``.

Phase 3 of the ciancheiltis umbrella (Northern Ireland / en-ga).
This package also houses the CocoIndex v1 App that embeds bilingual
en-ga government pages into the canonical LanceDB table
``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni_chunks``.

Phase 4 of the ciancheiltis umbrella (Scotland / en-gd). This package
also houses the CocoIndex v1 App that embeds bilingual en-gd
government pages into the canonical LanceDB table
``lancedb://md:cianfhoghlaim/ciancheiltis/en_gd_chunks``.

Phase 5 of the ciancheiltis umbrella (Isle of Man / en-gv). This
package also houses the CocoIndex v1 App that embeds bilingual
en-gv government pages into the canonical LanceDB table
``lancedb://md:cianfhoghlaim/ciancheiltis/en_gv_chunks``. Manx
(Gaelg) is in **revival status** — there is no statutory
bilingual publication duty and the Phase 5 strict-gate is
"capture what bilingual content exists and surface it faithfully".

Phase 6 of the ciancheiltis umbrella (EU level / en-ga). This
package also houses the CocoIndex v1 App that embeds bilingual
en-ga EU institutional pages into the canonical LanceDB table
``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu_chunks``. Irish
is an official + treaty language of the EU under Article 55 TEU +
Council Regulation No 1/1958; EU-level coverage is **partial** for
Irish — many EU documents exist only in English plus a "summary in
Irish" rather than a full Irish translation. The Phase 6 schema
MUST capture the ``language_availability`` ∈ ``{"full", "partial",
"summary_only"}`` as a first-class column (per the umbrella spec's
Phase 6 § first-class-column rule).

The R1-R4 conformance contract (per the
``oideachais-cocoindex-v1`` skill + the
``openspec/specs/ciancheiltis/spec.md`` R1-R4 section) is enforced by
``orchestration/components/layer3_model_lifecycle.py:_check_module_r1_to_r4``.
Every App in this sub-tree MUST:

- **R1** — import ``from ._lifespan import shared_lifespan`` (this file's sibling)
- **R2** — import the canonical ``ContextKey``s (``LANCE_DB``, ``EMBEDDER``,
  ``RESOLVED_FILE_REGISTRY``) from ``._lifespan``
- **R3** — declare ``coco.App(...)`` at module scope + wrap every flow as
  ``@coco.fn(memo=True, deps=[...])``
- **R4** — mount each LanceDB table via
  ``lancedb.mount_table_target(..., conformance_required=True)``

The shared embedder is ``BAAI/bge-m3`` (1024-d, multilingual — supports
CY/GA/GD/GV per the umbrella spec § R2; GV coverage is partial since
Manx is a smaller corpus).

Reference: ``openspec/changes/2026-09-06-ciancheiltis-v1/`` + the
Phase 5 extension at ``openspec/changes/2026-09-12-ciancheiltis-v2/``.
"""

# Phase 1 (Wales / en-cy) — re-export the CocoIndex v1 App symbol so
# downstream consumers can import it via
# ``cocoindex_flows.british_isles.uk.ciancheiltis_en_cy_embedding``.
from .ciancheiltis_en_cy_embedding import (
    EnCyChunk,
    en_cy_embedding,
    en_cy_embedding_flow,
)
from .ciancheiltis_en_cy_embedding import (
    flow as en_cy_flow,
)

# Phase 2 (Republic of Ireland / en-ga) — re-export the CocoIndex v1
# App symbol so downstream consumers can import it via
# ``cocoindex_flows.british_isles.uk.ciancheiltis_en_ga_roi_embedding``.
# Added by PR0.6 — the underlying
# ``ciancheiltis_en_ga_roi_embedding.py`` App is the Phase 2 mirror of
# the Phase 1 ``ciancheiltis_en_cy_embedding.py`` App, conforming to
# the same R1-R4 contract.
from .ciancheiltis_en_ga_roi_embedding import (
    EnGaRoiChunk,
    en_ga_roi_embedding,
    en_ga_roi_embedding_flow,
)
from .ciancheiltis_en_ga_roi_embedding import (
    flow as en_ga_roi_flow,
)

# Phase 3 (Northern Ireland / en-ga) — re-export the CocoIndex v1
# App symbol so downstream consumers can import it via
# ``cocoindex_flows.british_isles.uk.ciancheiltis_en_ga_ni_embedding``.
# Added by PR0.7 — the underlying
# ``ciancheiltis_en_ga_ni_embedding.py`` App is the Phase 3 mirror of
# the Phase 2 ``ciancheiltis_en_ga_roi_embedding.py`` App, conforming
# to the same R1-R4 contract. The Phase 3 canonical example is the
# *Identity and Language (Northern Ireland) Act 2022*
# (``https://www.legislation.gov.uk/uksi/2022/15/contents/made``).
from .ciancheiltis_en_ga_ni_embedding import (
    EnGaNiChunk,
    ciancheiltis_en_ga_ni_embedding,
    en_ga_ni_embedding_flow,
)
from .ciancheiltis_en_ga_ni_embedding import (
    flow as en_ga_ni_flow,
)

# Phase 4 (Scotland / en-gd) — re-export the CocoIndex v1 App symbol
# so downstream consumers can import it via
# ``cocoindex_flows.british_isles.uk.ciancheiltis_en_gd_embedding``.
# Added by PR0.8 — the underlying
# ``ciancheiltis_en_gd_embedding.py`` App is the Phase 4 mirror of
# the Phase 3 ``ciancheiltis_en_ga_ni_embedding.py`` App, conforming
# to the same R1-R4 contract. The Phase 4 canonical example is the
# *Gaelic Language (Scotland) Act 2005*
# (``https://www.legislation.gov.uk/asp/2005/7/contents``) and Bòrd
# na Gàidhlig under it
# (``https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/``).
from .ciancheiltis_en_gd_embedding import (
    EnGdChunk,
    ciancheiltis_en_gd_embedding,
    en_gd_embedding_flow,
)
from .ciancheiltis_en_gd_embedding import (
    flow as en_gd_flow,
)

# Phase 5 (Isle of Man / en-gv) — re-export the CocoIndex v1 App symbol
# so downstream consumers can import it via
# ``cocoindex_flows.british_isles.uk.ciancheiltis_en_gv_embedding``.
# Added by PR0.9 — the underlying
# ``ciancheiltis_en_gv_embedding.py`` App is the Phase 5 mirror of
# the Phase 4 ``ciancheiltis_en_gd_embedding.py`` App, conforming
# to the same R1-R4 contract. The Phase 5 canonical example is
# Culture Vannin under the Manx revival mandate
# (``https://www.culturevannin.im/learn-gaelg/``). Manx (Gaelg) is
# in **revival status** — there is no statutory bilingual
# publication duty and the Phase 5 strict-gate is "capture what
# bilingual content exists and surface it faithfully".
from .ciancheiltis_en_gv_embedding import (
    EnGvChunk,
    ciancheiltis_en_gv_embedding,
    en_gv_embedding_flow,
)
from .ciancheiltis_en_gv_embedding import (
    flow as en_gv_flow,
)

# Phase 6 (EU level / en-ga) — re-export the CocoIndex v1 App symbol
# so downstream consumers can import it via
# ``cocoindex_flows.british_isles.uk.ciancheiltis_en_ga_eu_embedding``.
# Added by PR0.10 — the underlying
# ``ciancheiltis_en_ga_eu_embedding.py`` App is the Phase 6 mirror of
# the Phase 5 ``ciancheiltis_en_gv_embedding.py`` App, conforming to
# the same R1-R4 contract (the canonical Phase 6 schema also adds a
# ``language_availability`` ∈ ``{"full", "partial", "summary_only"}``
# first-class column per the umbrella spec's Phase 6 §
# first-class-column rule). The Phase 6 canonical example is the
# Treaty on European Union, Irish-language edition
# (``https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E``).
from .ciancheiltis_en_ga_eu_embedding import (
    EnGaEuChunk,
    ciancheiltis_en_ga_eu_embedding,
    en_ga_eu_embedding_flow,
)
from .ciancheiltis_en_ga_eu_embedding import (
    flow as en_ga_eu_flow,
)

__all__ = [
    "EnCyChunk",
    "EnGaEuChunk",
    "EnGaNiChunk",
    "EnGaRoiChunk",
    "EnGdChunk",
    "EnGvChunk",
    "ciancheiltis_en_ga_eu_embedding",
    "ciancheiltis_en_ga_ni_embedding",
    "ciancheiltis_en_gd_embedding",
    "ciancheiltis_en_gv_embedding",
    "en_cy_embedding",
    "en_cy_embedding_flow",
    "en_cy_flow",
    "en_ga_eu_embedding_flow",
    "en_ga_eu_flow",
    "en_ga_ni_embedding_flow",
    "en_ga_ni_flow",
    "en_gd_embedding_flow",
    "en_gd_flow",
    "en_gv_embedding_flow",
    "en_gv_flow",
    "en_ga_roi_embedding",
    "en_ga_roi_embedding_flow",
    "en_ga_roi_flow",
]
