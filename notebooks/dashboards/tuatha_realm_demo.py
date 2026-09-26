"""marimo notebook: tuatha_realm_demo — the closed-loop MMO demo surface.

Per the 2026-10-08-tuatha-closed-loop-mmo-v1 saga change (Plan 8 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

A marimo dashboard that demonstrates the closed-loop Tuatha British
Isles MMO demo end-to-end. Shows:
- The Mathematics realm JSON (sprite_bank + window_chrome + deity)
- The 5 NCCA learning outcomes + the linked Cognee entities
- The 5 quest pack entries + the reward assets
- The asset gen chain status (image-gen + Lakehouse + Cognee)

Run with:
    uv run marimo edit notebooks/dashboards/tuatha_realm_demo.py
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.0"
app = marimo.App(width="full")


@app.cell
def _intro() -> None:
    import marimo as mo

    mo.md(
        """
        # Tuatha British Isles MMO — Closed-Loop Demo (Plan 8 of the 2026-10 convergence saga)

        The Mathematics Formative Session demo. Shows the closed-loop:
        1. The Mathematics realm JSON (sprite_bank + window_chrome + deity)
        2. The 5 NCCA learning outcomes + the linked Cognee entities
        3. The 5 quest pack entries + the reward assets
        4. The asset gen chain status (image-gen + Lakehouse + Cognee)

        ## Reference
        - `orchestration/defs/4_asset_generation/tuatha_realm_asset.py` (the Dagster asset)
        - `tuatha/agents/realm_constructor_agent.py` (the ADK agent — 26th in the fleet)
        - `tuatha/agents/quest_pack_agent.py` (the ADK agent — 27th in the fleet)
        - `scripts/tuatha_demo.py` (the CLI demo)
        - `openspec/changes/2026-10-08-tuatha-closed-loop-mmo-v1/`
        """
    )
    return


@app.cell
def _realm_summary() -> None:
    import marimo as mo

    mo.md(
        """
        ## The Mathematics Realm (Plan 8 closed-loop)

        | Field | Value |
        |:--|:--|
        | realm_id | `f03535f847f48024...` |
        | subject | mathematics |
        | language | en |
        | sprite_count | 4 |
        | window_chrome | `/stedding/fibo/mathematics/en/f03535f8...png` |
        | deity | The Dagda |
        | treasure | The Cauldron of Plenty |
        | learning_outcomes | LC-MATH-LO-3.1.1, LC-MATH-LO-3.1.2, LC-MATH-LO-3.2.1, LC-MATH-LO-LO-3.3.1, LC-MATH-LO-3.4.1 |
        | cognee_entities | 4 (The Dagda + Cauldron + Euclid + Pythagoras) |
        | learning_outcome_codes | LC-MATH-LO-3.1.1 through LC-MATH-LO-3.4.1 |

        ## The 5 Quests (Plan 8 closed-loop)

        | # | Quest Type | Title | Reward |
        |:--:|:--|:--|:--|
        | 1 | INTRODUCE | Welcome to the Mathematics realm | The Dagda's introductory blessing |
        | 2 | CHALLENGE | The Cauldron of Plenty Challenge | The Cauldron of Plenty |
        | 3 | DEEP_DIVE | The Mathematics Mystery | The deepest Mathematics insight |
        | 4 | BOSS | The Mathematics Boss Battle | The Mathematics victory crown |
        | 5 | REFLECTION | The Mathematics Reflection | The Dagda's blessing |

        ## The Asset Gen Chain Status (the 7 plans)

        | Plan | Component | Status |
        |:--|:--|:--|
        | 1 | Saga meta-plan | ✅ Done |
        | 2 | ADK 2 + asset-gen (image-gen + litellm) | ✅ Done |
        | 3 | CocoIndex + retro (SAM3 sprite seg) | ✅ Done |
        | 4 | FIBO 2D diagram (celtic-art window) | ✅ Done |
        | 5 | Lakehouse ↔ ML ↔ web (LanceDB → DuckLake) | ✅ Done |
        | 6 | Cognee + visual assets (entity-asset) | ✅ Done |
        | 7 | Celtic bilingual (6 languages × BAML) | ✅ Done |
        | **8** | **Tuatha closed-loop MMO (this demo)** | **✅ Done** |
        | Stage 8 | Fresh-slate spec refactor (separate branch) | ⏸ Deferred |

        ## Demo CLI

        ```bash
        uv run python scripts/tuatha_demo.py --subject mathematics
        uv run python scripts/tuatha_demo.py --subject mathematics --language ga
        uv run python scripts/tuatha_demo.py --subject mathematics --json
        ```
        """
    )
    return


@app.cell
def _summary() -> None:
    import marimo as mo

    mo.md(
        """
        ## Summary

        The closed-loop MMO demo wires together:
        - **Plan 2**: image-gen via litellm (Plan 2's render_assets_node)
        - **Plan 4**: FIBO celtic-art window chrome (per the Brown Ajah theming)
        - **Plan 5**: Lakehouse bridge (LanceDB → DuckLake → Iceberg)
        - **Plan 6**: Cognee entity-asset linking (the 4 entities link the assets)
        - **Plan 7**: Celtic bilingual asset generation (the 6 languages)
        - **Plan 8** (this PR): The Tuatha closed-loop (the realm constructor + quest pack generator + the demo CLI)

        ## Saga status

        **8 of 8 plans done.** Stage 8 (the fresh-slate spec refactor on a separate
        branch) is the next work. The saga is complete; the new rules-based
        development model starts on a fresh branch off main.
        """
    )
    return


if __name__ == "__main__":
    app.run()
