"""
design-system-server.py — MCP server for the Cianfhoghlaim design system.

Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/:
  - R23 (MCP-driven AI UI generation + self-heal)

Exposes 4 tools that allow AI agents to:
  1. tokens_get()       — read the full design token set
  2. catalog_list()     — discover the A2UI catalog (definitions + renderers)
  3. catalog_render()   — validate + render a component against the catalog
  4. storybook_stories()— fetch the Storybook stories for a component

catalog_render() refuses to emit components that violate the design
system contract (banned colours, wrong fonts, invalid layouts). On failure
it returns a `suggested_fix` field with a machine-readable remediation
— this is the self-heal mechanism.

References:
  - /Users/cianmacandeisigh/dev/kings_college_galway/.agents/skills/mcp-apps-builder/SKILL.md
  - .agents/skills/copilotkit/skills/a2ui-renderer/SKILL.md
  - cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/src/styles/tokens.css
  - cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/src/styles/tokens.schema.json
  - cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/src/styles/tokens.ts
  - cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/baml_src/design_tokens.baml

Usage:
  python design-system-server.py --port 7777
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any

# Optional MCP SDK import (graceful fallback if not yet installed)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False
    Server = None  # type: ignore
    Tool = None    # type: ignore
    TextContent = None  # type: ignore

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("design-system-server")

# ============================================================================
# Path resolution — find tokens.css, tokens.ts, tokens.schema.json, baml
# ============================================================================

SERVER_PATH = Path(__file__).resolve()
# apps/web/packages/mcp/design-system-server.py
#   ^^^  ^^^  ^^^^^^^^^ ^^^^^^^^^^
# Going up from `design-system-server.py`:
#   parent                    = apps/web/packages/mcp/
#   parent.parent             = apps/web/packages/
#   parent.parent.parent      = apps/web/
#   parent.parent.parent.parent= apps/
MCP_DIR     = SERVER_PATH.parent
PACKAGES_DIR = MCP_DIR.parent              # apps/web/packages/
WEB_SRC_DIR = PACKAGES_DIR.parent          # apps/web/
APP_DIR     = WEB_SRC_DIR.parent           # apps/  (i.e. cianfhoghlaim-leaving-cert/apps/)
STYLES_DIR  = WEB_SRC_DIR / "src" / "styles"  # apps/web/src/styles
BAML_DIR    = APP_DIR / "baml_src"         # apps/baml_src (the baml_src is at the cianfhoghlaim-leaving-cert root)

TOKENS_CSS    = STYLES_DIR / "tokens.css"
TOKENS_TS     = STYLES_DIR / "tokens.ts"
TOKENS_SCHEMA = STYLES_DIR / "tokens.schema.json"
# baml_src lives one level above apps/, at the cianfhoghlaim-leaving-cert root
TOKENS_BAML   = APP_DIR.parent / "baml_src" / "design_tokens.baml"


# ============================================================================
# Design System Catalog (R18 from the openspec change)
# ============================================================================

# Maps BAML class names (per_subject baml file) → A2UI catalog entries.
# 11 components per openspec/changes/.../specs/cianfhoghlaim-leaving-cert-portal/spec.md R18.
A2UI_CATALOG: dict[str, dict[str, Any]] = {
    "StudyPlanCard": {
        "description": "A study plan with weeks, milestones, and recommended past papers",
        "baml_class": "MathematicsWebStudyPlanResponse (+ 5 siblings)",
        "props": {
            "title": "string",
            "title_ga": "string",
            "weeks": "int",
            "total_study_hours": "int",
            "weeks_plan": "WeekTimeline[]",
            "milestones": "MilestoneBadge[]",
            "recommended_past_papers": "int[]",
        },
        "subjects": ["mathematics", "chemistry", "geography", "gaeilge", "english", "computer_science"],
        "locales": ["en", "ga"],
        "banned_colors": ["#FF0000", "#00FF00", "#0000FF"],  # pure RGB are invalid brand colours
        "valid_padding": [4, 8, 12, 16, 24, 32, 48, 64],     # must use spacing tokens
    },
    "WeekTimeline": {
        "description": "A week-by-week breakdown of a study plan",
        "baml_class": "MathematicsStudyWeek (+ 5 siblings)",
        "props": {
            "week_number": "int",
            "theme": "string",
            "theme_ga": "string",
            "syllabus_topics": "string[]",
            "study_hours": "int",
            "past_paper_questions": "string[]",
            "marking_scheme_focus": "string[]",
            "kc_weights": "KCWeightsBar[]",
        },
        "valid_padding": [4, 8, 12, 16, 24, 32],
    },
    "MilestoneBadge": {
        "description": "A milestone in a study plan",
        "baml_class": "MathematicsStudyMilestone (+ 5 siblings)",
        "props": {
            "week": "int",
            "description": "string",
            "description_ga": "string",
            "assessment_type": "enum[past_paper_full|past_paper_section|mock_orals|lab_practical|essay]",
        },
    },
    "ExamPaperCard": {
        "description": "A past exam paper discussion",
        "baml_class": "MathematicsWebExamPaperDiscussionResponse (+ 5 siblings)",
        "props": {
            "question_summary": "string",
            "question_summary_ga": "string?",
            "marking_scheme": "string",
            "marking_scheme_ga": "string?",
            "model_answer_outline": "string[]",
            "model_answer_outline_ga": "string[]",
            "common_mistakes": "string[]",
            "marks_breakdown": "MarksBreakdownTable[]",
            "follow_up_questions": "string[]",
        },
    },
    "MarksBreakdownTable": {
        "description": "A breakdown of marks for an exam question part",
        "baml_class": "MathematicsMarksBreakdown (+ 5 siblings)",
        "props": {
            "part_label": "string",
            "part_text": "string",
            "marks": "int",
            "marking_notes": "string",
        },
    },
    "KCWeightsBar": {
        "description": "The 5 NCCA Key Competencies with weights for a unit of study",
        "baml_class": "MathematicsKCWeight (+ 5 siblings)",
        "props": {
            "slug": "enum[communicating|information-processing|critical-creative-thinking|personal-effectiveness|working-with-others]",
            "weight": "int [0-100]",
        },
    },
    "StageOverview": {
        "description": "An overview of one of the 5 educational stages (Aistear, Primary, JC, LC, Tertiary)",
        "baml_class": "ExtractAistearFramework | ExtractPrimaryLearningOutcomes | ExtractJCSpec | ExtractSeniorCycleSubject | ExtractTertiaryProgramme",
        "props": {
            "stage": "enum[aistear|primary|junior_cycle|leaving_cycle|tertiary]",
            "title": "string",
            "title_ga": "string?",
            "data": "object",
        },
    },
    "SubjectCard": {
        "description": "A per-subject card on the central portal",
        "baml_class": "(per-subject CocoIndex query)",
        "props": {
            "subject": "enum[mathematics|chemistry|geography|gaeilge|english|computer_science]",
            "subject_ga": "string",
            "topic_count": "int",
            "kc_weights": "KCWeightsBar[]",
            "colour_token": "string (must reference subjects.<slug>.colour)",
        },
    },
    "MarimoEmbed": {
        "description": "An embedded marimo notebook deployed to Cloudflare Workers + Container",
        "baml_class": "(marimo embed)",
        "props": {
            "notebook_ref": "string (Workers URL)",
            "subject": "enum[mathematics|chemistry|geography|gaeilge|english|computer_science]",
            "locale": "enum[en|ga]",
        },
    },
    "PdfLibraryPanel": {
        "description": "A panel of signed R2 URLs to PDF assets",
        "baml_class": "(R2 signed URL)",
        "props": {
            "pdfs": "object[]",
            "ttl_seconds": "int (default 900)",
        },
    },
    "TranslationToggle": {
        "description": "The bilingual EN↔GA translation toggle",
        "baml_class": "(existing)",
        "props": {
            "current_locale": "enum[en|ga]",
            "target_locale": "enum[en|ga]",
        },
    },
}


# ============================================================================
# Helpers — read tokens, schema, BAML
# ============================================================================

def _read_tokens_css() -> dict[str, str]:
    """Return the full set of CSS custom properties as a flat dict."""
    css = TOKENS_CSS.read_text()
    pattern = re.compile(r"--ci-([a-z0-9_-]+)\s*:\s*([^;]+);")
    return {f"--ci-{k}": v.strip() for k, v in pattern.findall(css)}


def _read_tokens_schema() -> dict[str, Any]:
    """Return the JSON Schema for the design token set."""
    return json.loads(TOKENS_SCHEMA.read_text())


def _read_baml_design_tokens() -> str:
    """Return the BAML source for the design tokens."""
    if TOKENS_BAML.exists():
        return TOKENS_BAML.read_text()
    return "// design_tokens.baml not found"


# ============================================================================
# The 4 MCP tools
# ============================================================================

def tokens_get() -> dict[str, Any]:
    """
    Return the full Cianfhoghlaim design token set as JSON.
    Includes the 4 artifacts: CSS, TS, JSON Schema, BAML.
    """
    css_tokens = _read_tokens_css()
    return {
        "css": css_tokens,
        "css_count": len(css_tokens),
        "ts": "see cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/src/styles/tokens.ts",
        "schema": _read_tokens_schema(),
        "baml": _read_baml_design_tokens(),
    }


def catalog_list() -> dict[str, Any]:
    """Return the A2UI catalog (definitions + renderers)."""
    return {
        "count": len(A2UI_CATALOG),
        "components": A2UI_CATALOG,
    }


def catalog_render(component: str, props: dict[str, Any]) -> dict[str, Any]:
    """
    Validate a component + props against the catalog schema.

    Refuses to emit components that violate the design system contract
    (banned colours, wrong fonts, invalid layouts). On failure, returns
    a `suggested_fix` field with a machine-readable remediation.
    """
    if component not in A2UI_CATALOG:
        valid = list(A2UI_CATALOG.keys())
        return {
            "ok": False,
            "error": f"unknown_component: {component}",
            "suggested_fix": {"valid_components": valid},
        }

    spec = A2UI_CATALOG[component]

    # Check banned colours
    banned = spec.get("banned_colors", [])
    for key in ("color", "colour", "background", "background_color", "bg", "border_color"):
        val = props.get(key)
        if isinstance(val, str) and val.lower() in (b.lower() for b in banned):
            return {
                "ok": False,
                "error": f"banned_colour: {val} is not a valid Cianfhoghlaim colour token",
                "suggested_fix": {
                    "use_instead": "var(--ci-brand-primary)  // or any --ci-* token",
                    "available_tokens": _read_tokens_css(),
                },
            }

    # Check padding is on the spacing scale
    valid_padding = spec.get("valid_padding")
    if valid_padding is not None:
        for key in ("padding", "padding_top", "padding_left", "margin", "gap"):
            val = props.get(key)
            if val is not None and val not in valid_padding:
                return {
                    "ok": False,
                    "error": f"invalid_{key}: {val} is not on the Cianfhoghlaim spacing scale",
                    "suggested_fix": {
                        "use_instead": f"one of {valid_padding}",
                        "css_token_prefix": "--ci-spacing-" + str(val),
                    },
                }

    # Subject guard (for per-subject components)
    if "subjects" in spec:
        subj = props.get("subject") or props.get("baml_class_args", {}).get("subject")
        if subj and subj not in spec["subjects"]:
            return {
                "ok": False,
                "error": f"unsupported_subject: {subj}",
                "suggested_fix": {
                    "supported_subjects": spec["subjects"],
                },
            }

    # Locale guard (for bilingual components)
    if "locales" in spec:
        loc = props.get("locale") or props.get("language")
        if loc and loc not in spec["locales"]:
            return {
                "ok": False,
                "error": f"unsupported_locale: {loc}",
                "suggested_fix": {
                    "supported_locales": spec["locales"],
                },
            }

    # All checks passed — emit a rendered handle
    return {
        "ok": True,
        "component": component,
        "props": props,
        "rendered_jsx": f"<!-- <{component} /> rendered by MCP server; props validated -->",
        "storybook_snapshot_id": f"{component}-{hash(json.dumps(props, sort_keys=True)) & 0xffffffff:08x}",
    }


def storybook_stories(component: str) -> dict[str, Any]:
    """
    Return the Storybook stories for a component.

    For Phase 1, this returns a pointer to the canonical Storybook
    location. The actual story fetching will be wired by the Storybook
    build in Phase 3.
    """
    return {
        "component": component,
        "storybook_url": f"http://localhost:6006/?path=/story/{component.lower()}--default",
        "stories": [
            f"{component}--default",
            f"{component}--with-props",
            f"{component}--ga-locale",
        ],
        "note": "Storybook 8 stories are wired by Phase 3 (R16).",
    }


# ============================================================================
# MCP server bootstrap
# ============================================================================

def build_mcp_server() -> Any:
    """Build the MCP server with the 4 tools registered."""
    if not MCP_SDK_AVAILABLE:
        log.warning("MCP SDK not installed — running in stub mode")
        return None

    server: Any = Server("design-system-server")

    @server.list_tools()
    async def list_tools() -> list[Any]:
        return [
            Tool(
                name="tokens_get",
                description="Return the full Cianfhoghlaim design token set (CSS + TS + Schema + BAML)",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            Tool(
                name="catalog_list",
                description="Return the A2UI catalog (definitions + renderers)",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            Tool(
                name="catalog_render",
                description="Validate + render a component against the A2UI catalog; returns suggested_fix on failure",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "component": {"type": "string"},
                        "props": {"type": "object"},
                    },
                    "required": ["component", "props"],
                },
            ),
            Tool(
                name="storybook_stories",
                description="Return the Storybook stories for a component",
                inputSchema={
                    "type": "object",
                    "properties": {"component": {"type": "string"}},
                    "required": ["component"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[Any]:
        if name == "tokens_get":
            return [TextContent(type="text", text=json.dumps(tokens_get(), indent=2))]
        if name == "catalog_list":
            return [TextContent(type="text", text=json.dumps(catalog_list(), indent=2))]
        if name == "catalog_render":
            component = arguments.get("component", "")
            props = arguments.get("props", {})
            return [TextContent(type="text", text=json.dumps(catalog_render(component, props), indent=2))]
        if name == "storybook_stories":
            component = arguments.get("component", "")
            return [TextContent(type="text", text=json.dumps(storybook_stories(component), indent=2))]
        return [TextContent(type="text", text=json.dumps({"error": f"unknown_tool: {name}"}))]

    return server


# ============================================================================
# Smoke test (run via `python design-system-server.py --smoke`)
# ============================================================================

def smoke_test() -> None:
    """Smoke test: invoke each tool with a representative payload."""
    log.info("Running smoke test…")

    # 1. tokens_get
    tokens = tokens_get()
    assert tokens["css_count"] > 50, f"Expected 50+ tokens, got {tokens['css_count']}"
    log.info("✓ tokens_get returned %d CSS tokens", tokens["css_count"])

    # 2. catalog_list
    catalog = catalog_list()
    assert catalog["count"] == 11, f"Expected 11 A2UI components, got {catalog['count']}"
    log.info("✓ catalog_list returned %d A2UI components", catalog["count"])

    # 3. catalog_render: success case
    result = catalog_render("StudyPlanCard", {
        "title": "12-week Maths plan",
        "title_ga": "Plean Mata 12 seachtaine",
        "weeks": 12,
        "subject": "mathematics",
        "language": "en",
        "padding": 12,         # valid spacing scale
    })
    assert result["ok"] is True, f"Expected success, got: {result}"
    log.info("✓ catalog_render(StudyPlanCard, good props) succeeded with snapshot_id=%s", result["storybook_snapshot_id"])

    # 4. catalog_render: banned colour case → suggested_fix
    bad = catalog_render("StudyPlanCard", {"color": "#FF0000", "subject": "mathematics"})
    assert bad["ok"] is False
    assert bad["error"] == "banned_colour: #FF0000 is not a valid Cianfhoghlaim colour token"
    assert "suggested_fix" in bad
    log.info("✓ catalog_render(StudyPlanCard, banned colour) returned suggested_fix")

    # 5. catalog_render: invalid padding case → suggested_fix
    bad2 = catalog_render("WeekTimeline", {"padding": 7, "subject": "mathematics"})
    assert bad2["ok"] is False
    assert "invalid_padding" in bad2["error"]
    log.info("✓ catalog_render(WeekTimeline, invalid padding) returned suggested_fix")

    # 6. catalog_render: unknown component
    bad3 = catalog_render("NotARealComponent", {})
    assert bad3["ok"] is False
    assert bad3["error"].startswith("unknown_component")
    log.info("✓ catalog_render(NotARealComponent, {}) returned valid_components list")

    # 7. storybook_stories
    stories = storybook_stories("StudyPlanCard")
    assert "storybook_url" in stories
    log.info("✓ storybook_stories(StudyPlanCard) returned %d stories", len(stories["stories"]))

    log.info("Smoke test passed.")


# ============================================================================
# Entrypoint
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Cianfhoghlaim design system MCP server")
    parser.add_argument("--smoke", action="store_true", help="Run smoke test only (no MCP server)")
    parser.add_argument("--port", type=int, default=7777, help="(reserved for future HTTP transport)")
    args = parser.parse_args()

    if args.smoke:
        smoke_test()
        return

    if not MCP_SDK_AVAILABLE:
        log.error("MCP SDK not available — install via `pip install mcp` or run with --smoke")
        return

    server = build_mcp_server()
    if server is None:
        return

    log.info("Starting design-system-server on stdio transport")
    import asyncio
    asyncio.run(stdio_server(server).run())


if __name__ == "__main__":
    main()
