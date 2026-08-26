#!/usr/bin/env python3
"""
Deterministic generator for the Phase-0.2 ISO-3 -> snake_case sed
migration scripts of the openspec change
`2026-08-24-dlt-sources-to-multi-repo-scaffold-v1`.

Reads `dlt_sources/LEGACY_ALIASES.md` (relative to this script's parent)
and emits, into the same directory as this script:

  - migration_european_nations.sh           (40 pairs)
  - migration_commonwealth.sh               (6 pairs)
  - migration_commonwealth_canada_provinces.sh (13 pairs)
  - migration_commonwealth_nigeria_states.sh   (37 pairs)
  - migration_british_isles.sh              (7 pairs)
  - migration_americas.sh                   (4 case-A pairs; Capitalized country names)
  - migration_americas_case_b.sh            (9 case-B per-file rewrites; domain-first)
  - apply_all.sh                            (runner; invokes all 7 above in dependency order)

Idempotent + deterministic: identical input bytes yield identical
output bytes. Output ordering is fixed: pair ordering comes verbatim
from LEGACY_ALIASES.md (which is itself alphabetical / canonical).
No timestamps are written; LF line endings only.

Run:

    python3 _generator.py            # generate all 8 files
    python3 _generator.py --check    # exit 0 if files are up-to-date, 1 otherwise
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


HERE = Path(__file__).resolve().parent
LEGACY_ALIASES = HERE.parent.parent / "LEGACY_ALIASES.md"

CHANGE_ID = "2026-08-24-dlt-sources-to-multi-repo-scaffold-v1"

PKG = "dlt_sources"

WINDOWS_NEWLINE = re.compile(r"\r\n")

_BACKTICK_PATH = re.compile(r"`((?:dlt|dlt_sources)/[^`]+)`")


class Pair(NamedTuple):
    """One ISO-3 -> snake rename."""

    old_fs: str  # filesystem path of the old dir, e.g. "dlt_sources/european_nations/alb"
    new_fs: str  # filesystem path of the new dir, e.g. "dlt_sources/european_nations/albania"
    old_py: str  # python module path, e.g. "dlt_sources.european_nations.alb"
    new_py: str  # python module path, e.g. "dlt_sources.european_nations.albania"


class WaveSpec(NamedTuple):
    script_name: str
    title: str
    description: str
    legacy_lines: str  # "L97-L97" or "L121-L127" — human reference for header
    pairs: tuple[Pair, ...]


# ---------------------------------------------------------------------------
# LEGACY_ALIASES.md parser
# ---------------------------------------------------------------------------


def _strip_trailing_slash(s: str) -> str:
    return s[:-1] if s.endswith("/") else s


def _split_prefix_and_items(path: str) -> tuple[str, list[str]]:
    """
    Split a path like

        dlt/european_nations/{alb,aut,xkx}/          -> ("dlt/european_nations/", ["alb","aut","xkx"])
        dlt/british_isles/en/                        -> ("dlt/british_isles/",    ["en"])
        dlt/commonwealth/nigeria/states/nga_{...}/    -> ("dlt/commonwealth/nigeria/states/nga_",
                                                          ["abi","ada",...])

    Note: this only deals with PATH structure, not the dlt -> dlt_sources
    rename (caller is responsible).
    """
    s = _strip_trailing_slash(path)
    # find the LAST `{` that opens a `{a,b,c}` items group; the items end at
    # the corresponding `}` which must be the final char.
    if s.endswith("}"):
        last_open = s.rfind("{")
        if last_open != -1:
            inner = s[last_open + 1 : -1]
            prefix = s[:last_open]
            if not prefix.endswith("/"):
                prefix += "/"
            return prefix, inner.split(",")
    # no alternation: last segment is the entry
    idx = s.rfind("/")
    return s[: idx + 1], [s[idx + 1 :]]


def _unify_prefix_to_pkg(prefix: str) -> str:
    """
    Turn a dlt-prefixed filesystem path (as found in LEGACY_ALIASES.md) into
    a python-dot-notation package path.

        "dlt/european_nations/"   -> "dlt_sources.european_nations"
        "dlt_sources/european_nations/" -> "dlt_sources.european_nations"
    """
    return _dlt_swap(prefix).replace("/", ".").rstrip(".")


def _dlt_swap(path: str) -> str:
    """
    Replace the leading `dlt/` (from LEGACY_ALIASES.md) with `dlt_sources/`.

        "dlt/european_nations/alb"     -> "dlt_sources/european_nations/alb"
        "dlt_sources/european_nations/" -> "dlt_sources/european_nations/"
    """
    p = path.rstrip("/")
    if p.startswith("dlt/"):
        return "dlt_sources/" + p[len("dlt/") :]
    if p.startswith("dlt_sources/"):
        return p + "/" if path.endswith("/") else p
    raise ValueError(f"unexpected path prefix {path!r}")


def _parse_wave_table(
    lines: list[str], start_idx: int
) -> tuple[list[tuple[str, str]], int]:
    """
    Read rows of the wave table starting at `start_idx`. A row is any line
    of the form `| `dlt/...` | `dlt/...` |`. Returns (rows, end_idx) where
    end_idx is the line index AFTER the last row.

    Each row is `(old_path, new_path)` — both filesystem paths from the
    backticks.
    """
    rows: list[tuple[str, str]] = []
    j = start_idx
    while j < len(lines):
        line = lines[j].strip()
        if line.startswith("| `"):
            matches = _BACKTICK_PATH.findall(line)
            if len(matches) >= 2:
                rows.append((matches[0], matches[1]))
            j += 1
        elif line == "" or line.startswith("###") or line.startswith("---"):
            break
        else:
            j += 1
    return rows, j


def _py_join(py_pref_with_sep: str, seg: str) -> str:
    """
    Join a python-dot-prefix (which already carries the trailing separator)
    and a segment.

    - Most prefixes carry trailing `.` (e.g. `dlt_sources.european_nations.`):
      concat directly:  `dlt_sources.european_nations.` + `alb` = `...alb`.
    - The Nigeria-states prefix carries trailing `_` (e.g.
      `dlt_sources.commonwealth.nigeria.states.nga_`): concat directly too:
      `dlt_sources...states.nga_` + `abi` = `...states.nga_abi`.
    - The British Isles / European / Commonwealth / Americas prefixes all
      end in `.` for python-dot paths.
    """
    return py_pref_with_sep + seg


def _fs_join(fs_pref_with_sep: str, seg: str) -> str:
    """Same idea as `_py_join` but for slash-style filesystem paths."""
    return fs_pref_with_sep + seg


def _ensure_trailing(prefix: str, sep: str) -> str:
    """Make sure `prefix` ends with `sep`. If it already ends with `sep` or
    with `_` (the Nigeria-states convention), leave it alone; otherwise
    append `sep`."""
    if prefix.endswith(sep) or prefix.endswith("_"):
        return prefix
    return prefix + sep


def _pairs_from_rows(rows: list[tuple[str, str]]) -> list[Pair]:
    """
    Turn (old_path, new_path) rows into a list of `Pair` records.

    Two shapes are supported:

      A. Single-row alternation (e.g. European nations):
            1 row: (dlt/eur/{alb,...,xkx}/, dlt/eur/{albania,...,kosovo}/)
            -> N Pair records (one per item in the alternation).

      B. Multi-row per-entry (e.g. British Isles):
            N rows, one Pair per row.
    """
    if not rows:
        raise ValueError("no rows")

    old_pref, old_items = _split_prefix_and_items(rows[0][0])
    _, new_items = _split_prefix_and_items(rows[0][1])

    pairs: list[Pair] = []

    if len(old_items) > 1:
        # Shape A: single-row alternation
        if len(new_items) != len(old_items):
            raise ValueError(
                f"alternation shape mismatch: "
                f"{len(old_items)} old vs {len(new_items)} new"
            )
        new_pref = _split_prefix_and_items(rows[0][1])[0]
        old_py_pref = _ensure_trailing(_unify_prefix_to_pkg(old_pref), ".")
        new_py_pref = _ensure_trailing(_unify_prefix_to_pkg(new_pref), ".")
        old_fs_pref = _ensure_trailing(_dlt_swap(_strip_trailing_slash(old_pref)), "/")
        new_fs_pref = _ensure_trailing(_dlt_swap(_strip_trailing_slash(new_pref)), "/")
        for old_seg, new_seg in zip(old_items, new_items):
            pairs.append(
                Pair(
                    old_fs=_fs_join(old_fs_pref, old_seg),
                    new_fs=_fs_join(new_fs_pref, new_seg),
                    old_py=_py_join(old_py_pref, old_seg),
                    new_py=_py_join(new_py_pref, new_seg),
                )
            )
    else:
        # Shape B: multi-row per-entry.
        # Use the unified prefix (constant across all rows) for the join,
        # then iterate the per-row segment.
        bases = {_split_prefix_and_items(r[0])[0] for r in rows}
        if len(bases) > 1:
            raise ValueError(
                f"inconsistent OLD prefixes across rows: {bases!r}"
            )
        bases_new = {_split_prefix_and_items(r[1])[0] for r in rows}
        if len(bases_new) > 1:
            raise ValueError(
                f"inconsistent NEW prefixes across rows: {bases_new!r}"
            )
        base_old_pref_file = bases.pop()  # e.g. "dlt/british_isles/"
        base_new_pref_file = bases_new.pop()
        old_py_pref = _ensure_trailing(
            _unify_prefix_to_pkg(base_old_pref_file), "."
        )
        new_py_pref = _ensure_trailing(
            _unify_prefix_to_pkg(base_new_pref_file), "."
        )
        old_fs_pref = _ensure_trailing(
            _dlt_swap(_strip_trailing_slash(base_old_pref_file)), "/"
        )
        new_fs_pref = _ensure_trailing(
            _dlt_swap(_strip_trailing_slash(base_new_pref_file)), "/"
        )

        for old_path, new_path in rows:
            _, old_items_r = _split_prefix_and_items(old_path)
            _, new_items_r = _split_prefix_and_items(new_path)
            if len(old_items_r) != 1 or len(new_items_r) != 1:
                raise ValueError(
                    f"multi-row shape: row {old_path!r} has wrong item count"
                )
            pairs.append(
                Pair(
                    old_fs=_fs_join(old_fs_pref, old_items_r[0]),
                    new_fs=_fs_join(new_fs_pref, new_items_r[0]),
                    old_py=_py_join(old_py_pref, old_items_r[0]),
                    new_py=_py_join(new_py_pref, new_items_r[0]),
                )
            )

    return pairs


def _wave_block(
    text: str,
    pre_marker_re: re.Pattern[str],
    first_header_re: re.Pattern[str],
    script_name: str,
    title: str,
    description: str,
) -> WaveSpec:
    """
    Find the wave table under the header matched by `first_header_re` (which
    must come AFTER the `pre_marker_re` marker line) and return a WaveSpec.
    """
    lines = text.split("\n")
    # Find the Pre-Wave-1 marker
    pre_idx = None
    for i, line in enumerate(lines):
        if pre_marker_re.match(line):
            pre_idx = i
            break
    if pre_idx is None:
        raise RuntimeError("could not find Pre-Wave-1 marker")

    # Find the wave header
    hdr_idx = None
    for i in range(pre_idx + 1, len(lines)):
        if first_header_re.match(lines[i].strip()):
            hdr_idx = i
            break
    if hdr_idx is None:
        raise RuntimeError(f"could not find header matching {first_header_re.pattern}")

    # Find the first data row (| `dlt/...`|...)
    table_start = None
    for i in range(hdr_idx + 1, len(lines)):
        if lines[i].strip().startswith("| `dlt/"):
            table_start = i
            break
    if table_start is None:
        raise RuntimeError("could not find table start")

    rows, end_idx = _parse_wave_table(lines, table_start)
    pairs = _pairs_from_rows(rows)

    legacy_lines = f"L{table_start + 1}-L{end_idx}"
    return WaveSpec(
        script_name=script_name,
        title=title,
        description=description,
        legacy_lines=legacy_lines,
        pairs=tuple(pairs),
    )


PRE_MARKER_RE = re.compile(r"^## Pre-Wave-1 legacy aliases")
EUR_RE = re.compile(r"^### European nations\b")
CWL_RE = re.compile(r"^### Commonwealth\b")
CAN_RE = re.compile(r"^### Canada\b")
NGA_RE = re.compile(r"^### Nigeria\b")
BRI_RE = re.compile(r"^### British Isles\b")
AME_RE = re.compile(r"^### Americas\b")


def parse_legacy_aliases(text: str) -> list[WaveSpec]:
    text = WINDOWS_NEWLINE.sub("\n", text)
    waves = [
        _wave_block(
            text,
            PRE_MARKER_RE,
            EUR_RE,
            script_name="migration_european_nations.sh",
            title="European nations \u2014 ISO 3-letter -> full snake_case",
            description=(
                "39 country codes: alb -> albania, aut -> austria, bel -> belgium, "
                "bgr -> bulgaria, bih -> bosnia_and_herzegovina, che -> switzerland, "
                "cyp -> cyprus, cze -> czechia, deu -> germany, dnk -> denmark, "
                "esp -> spain, est -> estonia, fin -> finland, fra -> france, "
                "geo -> georgia, grc -> greece, hrv -> croatia, hun -> hungary, "
                "isl -> iceland, ita -> italy, lie -> liechtenstein, ltu -> lithuania, "
                "lux -> luxembourg, lva -> latvia, mda -> moldova, mkd -> north_macedonia, "
                "mlt -> malta, mne -> montenegro, nld -> netherlands, nor -> norway, "
                "pol -> poland, prt -> portugal, rou -> romania, srb -> serbia, "
                "svk -> slovakia, svn -> slovenia, swe -> sweden, tur -> turkey, "
                "ukr -> ukraine, xkx -> kosovo."
            ),
        ),
        _wave_block(
            text,
            PRE_MARKER_RE,
            CWL_RE,
            script_name="migration_commonwealth.sh",
            title="Commonwealth top-level \u2014 ISO 3-letter -> full snake_case",
            description=(
                "6 jurisdictions: aus -> australia, can -> canada, ind -> india, "
                "nga -> nigeria, nzl -> new_zealand, zaf -> south_africa."
            ),
        ),
        _wave_block(
            text,
            PRE_MARKER_RE,
            CAN_RE,
            script_name="migration_commonwealth_canada_provinces.sh",
            title="Canada \u2014 provinces under commonwealth/can/",
            description=(
                "13 provinces: ab -> alberta, bc -> british_columbia, mb -> manitoba, "
                "nb -> new_brunswick, nl -> newfoundland_and_labrador, ns -> nova_scotia, "
                "nt -> northwest_territories, nu -> nunavut, on -> ontario, "
                "pe -> prince_edward_island, qc -> quebec, sk -> saskatchewan, yt -> yukon."
            ),
        ),
        _wave_block(
            text,
            PRE_MARKER_RE,
            NGA_RE,
            script_name="migration_commonwealth_nigeria_states.sh",
            title="Nigeria \u2014 states under commonwealth/nigeria/states/nga_<3>/",
            description=(
                "36 states: nga_abi -> abia, nga_ada -> adamawa, nga_aki -> akwa_ibom, "
                "nga_ana -> anambra, nga_bau -> bauchi, nga_bay -> bayelsa, "
                "nga_ben -> benue, nga_bor -> borno, nga_crs -> cross_river, "
                "nga_del -> delta, nga_ebi -> ebonyi, nga_edo -> edo, nga_eki -> ekiti, "
                "nga_enu -> enugu, nga_fct -> federal_capital_territory, "
                "nga_gom -> gombe, nga_imo -> imo, nga_jig -> jigawa, nga_kad -> kaduna, "
                "nga_kan -> kano, nga_kat -> katsina, nga_keb -> kebbi, nga_kog -> kogi, "
                "nga_kwa -> kwara, nga_los -> lagos, nga_nas -> nasarawa, "
                "nga_ngr -> niger, nga_ogn -> ogun, nga_ond -> ondo, nga_osn -> osun, "
                "nga_oyo -> oyo, nga_plt -> plateau, nga_riv -> rivers, "
                "nga_sok -> sokoto, nga_tar -> taraba, nga_yob -> yobe, nga_zam -> zamfara."
            ),
        ),
        _wave_block(
            text,
            PRE_MARKER_RE,
            BRI_RE,
            script_name="migration_british_isles.sh",
            title="British Isles \u2014 collapse dual naming",
            description=(
                "7 jurisdictions: en -> england, ni -> northern_ireland, "
                "sct -> scotland, wls -> wales, iom -> isle_of_man, "
                "jey -> jersey, ggy -> guernsey."
            ),
        ),
        _wave_block(
            text,
            PRE_MARKER_RE,
            AME_RE,
            script_name="migration_americas.sh",
            title="Americas \u2014 americas/ -> american_nations/",
            description=(
                "4 nations: bra -> brazil, mex -> mexico, us -> united_states, "
                "ven -> venezuela. (After this wave `dlt_sources/americas/` is "
                "renamed to `dlt_sources/american_nations/`.)"
            ),
        ),
    ]
    return waves


# ---------------------------------------------------------------------------
# script emitters
# ---------------------------------------------------------------------------

SHEBANG = "#!/usr/bin/env bash\n"


# Wave 6 (Americas) constants. The 4 ISO-3 codes from LEGACY_ALIASES.md
# are lowercase (`bra`, `mex`, `us`, `ven`), but the actual broken imports
# in the tree use Capitalized country names (`Brazil`, `Mexico`,
# `united_states`, `Venezuela`). Per Subagent E's post-mortem
# (`stedding/sync-reports/legacy-import-fix-2026-08-24.md` §3.2) the
# lowercase patterns produced no matches. The Wave 6 migration script
# therefore uses the Capitalized names + an explicit `\.` anchor (NOT
# `\b`) so that only the segment boundary matches.
_AMERICAS_COUNTRY_MAP: dict[str, tuple[str, str]] = {
    # iso3_lower -> (capitalized, snake_case_lower)
    "bra": ("Brazil", "brazil"),
    "mex": ("Mexico", "mexico"),
    "us": ("United States", "united_states"),
    "ven": ("Venezuela", "venezuela"),
}


# Wave 6 case-B triples: 9 files under `dlt_sources/{law,education,medicine}/<country>/american_nations/__init__.py`
# whose broken imports follow the Wave-1 domain-first rule (drop the
# `<vertical>.` segment, use the package-level re-export). The rewrite
# target depends on the file's containing directory, so each entry is
# emitted as its own explicit apply_pair_b call (no `git mv` involved).
_AMERICAS_CASE_B_TRIPLES: tuple[tuple[str, str, str, str], ...] = (
    # (file_path, country_capitalized, vertical, domain)
    ("dlt_sources/law/brazil/american_nations/__init__.py", "Brazil", "law", "law"),
    ("dlt_sources/law/mexico/american_nations/__init__.py", "Mexico", "law", "law"),
    ("dlt_sources/law/venezuela/american_nations/__init__.py", "Venezuela", "law", "law"),
    (
        "dlt_sources/education/brazil/american_nations/__init__.py",
        "Brazil",
        "education",
        "education",
    ),
    (
        "dlt_sources/education/mexico/american_nations/__init__.py",
        "Mexico",
        "education",
        "education",
    ),
    (
        "dlt_sources/education/venezuela/american_nations/__init__.py",
        "Venezuela",
        "education",
        "education",
    ),
    (
        "dlt_sources/medicine/brazil/american_nations/__init__.py",
        "Brazil",
        "medicine",
        "medicine",
    ),
    (
        "dlt_sources/medicine/mexico/american_nations/__init__.py",
        "Mexico",
        "medicine",
        "medicine",
    ),
    (
        "dlt_sources/medicine/venezuela/american_nations/__init__.py",
        "Venezuela",
        "medicine",
        "medicine",
    ),
)


def _shell_escape_for_single_quote(s: str) -> str:
    """
    Escape a string for use inside a bash SINGLE-quoted string. Single-quoted
    bash strings cannot contain a literal `'`. They are escaped as `'\''`
    (close, escaped quote, reopen). Our paths contain no `'`, so this is a
    no-op, but we apply it for safety.
    """
    return s.replace("'", "'\\''")


HEADER_COMMON = r"""#
# {title}.
#
# Generated by `_generator.py` from `dlt_sources/LEGACY_ALIASES.md`
# (lines {legacy_lines}) for Phase 0.2 of the openspec change
# `{change_id}`.
#
# Usage:
#   bash {script_name}           # APPLY (default)
#   bash {script_name} --dry-run # print what would change; do NOT write
#
# Per the v2 plan constraint: target is macOS. Implementation uses
# `perl -i -pe` (NOT BSD `sed`) for the in-place edit. BSD `sed` on
# macOS silently drops `\b` word boundaries (see Subagent E post-mortem
# in `stedding/sync-reports/legacy-import-fix-2026-08-24.md` §3.1),
# which made the prior regex-only-with-`\b` migration emit no-ops on
# every pair. Perl honors `\b` correctly. Both perl-5 and GNU `sed`
# are fine on macOS via Homebrew; the script does NOT require any
# non-vendor binaries.
#
# What each pair does (driven by the `apply_pair` function below):
#   1. Print the BEFORE count via `git grep -l "<sed-from>" -- '*.py' | wc -l`.
#   2. `git mv <old-fs> <new-fs>` -- preserving git history (no content
#      touched). Only when `<old-fs>` exists; the script is a no-op if the
#      directory has already been moved (idempotent on a partial run).
#   3. Apply the import-path rewrite via
#      `perl -i -pe "s|<sed-from>|<sed-to>|g"` to every matching file.
#      The `\b` in `<sed-from>` is honored by perl (BSD sed drops it)
#      and ensures only the top-level segment matches (e.g.
#      `british_isles.en\b` matches `.en` and `.en.foo` but NOT `.england`).
#   4. Print the AFTER count (expect 0; non-zero means an import survived
#      and the script surfaces a manual-review warning).
#
# Idempotent on the import-rewrite side (re-running `perl -i -pe` against
# an already-migrated import path is a no-op because `<sed-from>` no
# longer matches). The `git mv` is fail-safe -- it errors if the
# destination already exists with the same content, so a partial re-run
# halts cleanly.

set -euo pipefail

DRY_RUN=0
if [[ "${{1:-}}" == "--dry-run" ]]; then
    DRY_RUN=1
    echo "[DRY RUN] No filesystem or git operations will be performed."
    echo "[DRY RUN] Every command below is prefixed with '[DRY RUN]'."
    echo
fi

# apply_pair <sed-from> <sed-to> <old-fs> <new-fs>
#
# - <sed-from> -- the SEARCH pattern for sed and git grep, with `\.` already
#   escaped and a trailing `\b` for word-boundary matching. Example:
#     "from dlt_sources\.european_nations\.alb\b"
# - <sed-to>   -- the REPLACEMENT pattern. Example:
#     "from dlt_sources.european_nations.albania"
# - <old-fs>   -- the OLD filesystem path (used for `git mv` + directory
#   existence check). Example:
#     "dlt_sources/european_nations/alb"
# - <new-fs>   -- the NEW filesystem path. Example:
#     "dlt_sources/european_nations/albania"
apply_pair() {{
    local sed_from="$1"
    local sed_to="$2"
    local old_fs="$3"
    local new_fs="$4"
    echo "[PAIR] ${{old_fs}} -> ${{new_fs}}"

    # `git grep -l` returns 1 when there are no matches. Combined with
    # `set -o pipefail` (enabled at the top of the script), the pipeline
    # would otherwise short-circuit the whole script on a pair that has
    # nothing to do (which is the common case on an already-migrated tree).
    # Use a `( ... || true )` subshell so the pipeline always succeeds; the
    # printed count is what matters. Restrict to `*.py` to skip the ~thousand
    # non-Python files that can never contain a Python `from ... import ...`.
    local before
    before=$( (git grep -l -- "${{sed_from}}" -- '*.py' 2>/dev/null || true) | wc -l | tr -d ' ')
    echo "  Before: ${{before}} import sites"

    if [[ "${{DRY_RUN}}" == "1" ]]; then
        if [[ -d "${{old_fs}}" ]]; then
            echo "  [DRY RUN] Would: git mv \"${{old_fs}}\" \"${{new_fs}}\""
        fi
        echo "  [DRY RUN] Would: perl -i -pe \"s|${{sed_from}}|${{sed_to}}|g\" <every matching *.py file>"
        local after
        after=$( (git grep -l -- "${{sed_from}}" -- '*.py' 2>/dev/null || true) | wc -l | tr -d ' ')
        echo "  After: ${{after}} import sites (expect 0)"
        return 0
    fi

    # --- APPLY path --------------------------------------------------------
    if [[ -d "${{old_fs}}" ]]; then
        git mv "${{old_fs}}" "${{new_fs}}"
    fi

    local matches
    matches=$(git grep -l -- "${{sed_from}}" -- '*.py' 2>/dev/null || true)
    if [[ -n "${{matches}}" ]]; then
        while IFS= read -r f; do
            perl -i -pe "s|${{sed_from}}|${{sed_to}}|g" "${{f}}"
        done <<<"${{matches}}"
    fi

    local after
    after=$( (git grep -l -- "${{sed_from}}" -- '*.py' 2>/dev/null || true) | wc -l | tr -d ' ')
    echo "  After: ${{after}} import sites (expect 0)"
    if [[ "${{after}}" != "0" ]]; then
        echo "  !! WARNING: ${{after}} import sites for ${{old_fs}} survived."
        echo "     Manual review required."
    fi
}}
"""


def _escape_for_sed(s: str) -> str:
    """
    Escape a Python module path so that it can be used as a sed SEARCH
    pattern. Dots become `\.`. Anything else (alnum, underscore, `from `,
    `\b`) is preserved.
    """
    return s.replace(".", r"\.")


def _shell_quote(s: str) -> str:
    """Single-quote a string for bash."""
    return "'" + s.replace("'", "'\\''") + "'"


def emit_migration_script(spec: WaveSpec) -> str:
    body = HEADER_COMMON.format(
        title=spec.title,
        script_name=spec.script_name,
        legacy_lines=spec.legacy_lines,
        change_id=CHANGE_ID,
    )

    body += "\n# ----------------------------------------------------------------------------\n"
    body += f"# Pair list ({len(spec.pairs)} pairs; deterministic, sourced from\n"
    body += f"# LEGACY_ALIASES.md {spec.legacy_lines})\n"
    body += "# ----------------------------------------------------------------------------\n\n"

    # Wave 6 (americas) special-case: the actual broken imports use
    # Capitalized country names (Brazil/Mexico/United States/Venezuela)
    # rather than the lowercase ISO-3 codes (bra/mex/us/ven) that
    # LEGACY_ALIASES.md encodes. The standard `\b`-anchored patterns
    # therefore do not match; we override the sed_from to use the
    # Capitalized name + an explicit `\.` anchor. See Subagent E post-mortem
    # `stedding/sync-reports/legacy-import-fix-2026-08-24.md` §3.2.
    is_americas_case_a = spec.script_name == "migration_americas.sh"

    for p in spec.pairs:
        if is_americas_case_a:
            iso3 = p.old_py.rsplit(".", 1)[-1]
            country_cap, country_lower = _AMERICAS_COUNTRY_MAP[iso3]
            sed_from = (
                f"from dlt_sources\\.americas\\.{country_cap}\\."
            )
            sed_to = (
                f"from dlt_sources.american_nations.{country_lower}."
            )
        else:
            sed_from = "from " + _escape_for_sed(p.old_py) + r"\b"
            sed_to = "from " + p.new_py
        body += "apply_pair "
        body += _shell_quote(sed_from) + " "
        body += _shell_quote(sed_to) + " "
        body += _shell_quote(p.old_fs) + " "
        body += _shell_quote(p.new_fs) + "\n"

    body += "\n# Done.\n"
    return SHEBANG + body


# Header template for the Wave 6 case-B sub-script. The case-B sub-script
# uses a different helper (`apply_pair_b`) because the rewrite target
# depends on the file path (per the Wave-1 domain-first rule, the
# destination uses the containing domain as the top-level segment).
# Otherwise the header is identical to HEADER_COMMON's structure.
HEADER_CASE_B = r"""#
# {title}.
#
# Generated by `_generator.py` for Phase 0.2 follow-up of the openspec
# change `{change_id}` (sub-change `2026-08-24-legacy-import-fix-v1`).
# Companion to `migration_americas.sh` (case-A). Together they cover the
# 15 truly-broken `from dlt_sources.americas.*` imports documented in
# `stedding/sync-reports/legacy-import-audit-2026-08-24.md` §1.6:
#   - case-A (6 files): `dlt_sources/american_nations/<country>/{{government,statistics}}/__init__.py`
#   - case-B (9 files): `dlt_sources/{{law,education,medicine}}/<country>/american_nations/__init__.py`
#
# Usage:
#   bash {script_name}           # APPLY (default)
#   bash {script_name} --dry-run # print what would change; do NOT write
#
# Uses `perl -i -pe` for the in-place edit (BSD sed lacks `\b` support).
# No `git mv` is needed for case-B: the destination files already exist
# at the canonical `dlt_sources/<domain>/<country>/american_nations/` path;
# only their `from ... import ...` statement needs updating.
#
# What `apply_pair_b` does:
#   1. Print the BEFORE count via `git grep -l "<sed-from>" -- '*.py' | wc -l`.
#   2. `perl -i -pe "s|<sed-from>|<sed-to>|g"` against the SPECIFIC file
#      (not a directory-wide rewrite -- the target depends on the file's
#      containing directory).
#   3. Print the AFTER count (expect 0).

set -euo pipefail

DRY_RUN=0
if [[ "${{1:-}}" == "--dry-run" ]]; then
    DRY_RUN=1
    echo "[DRY RUN] No filesystem or git operations will be performed."
    echo "[DRY RUN] Every command below is prefixed with '[DRY RUN]'."
    echo
fi

# apply_pair_b <sed-from> <sed-to> <file-path>
#
# Per-file variant of `apply_pair` (no `git mv`). Use when the rewrite
# target depends on the file path. See Subagent E post-mortem
# `stedding/sync-reports/legacy-import-fix-2026-08-24.md` §3.3 + the audit
# §1.6 for why case-B cannot use the standard regex-with-`\b` strategy.
apply_pair_b() {{
    local sed_from="$1"
    local sed_to="$2"
    local file_path="$3"
    echo "[PAIR-B] ${{file_path}}: ${{sed_from}} -> ${{sed_to}}"

    local before
    before=$( (git grep -l -- "${{sed_from}}" -- '*.py' 2>/dev/null || true) | wc -l | tr -d ' ')
    echo "  Before: ${{before}} import sites"

    if [[ "${{DRY_RUN}}" == "1" ]]; then
        echo "  [DRY RUN] Would: perl -i -pe \"s|${{sed_from}}|${{sed_to}}|g\" ${{file_path}}"
        local after
        after=$( (git grep -l -- "${{sed_from}}" -- '*.py' 2>/dev/null || true) | wc -l | tr -d ' ')
        echo "  After: ${{after}} import sites (expect 0)"
        return 0
    fi

    # --- APPLY path --------------------------------------------------------
    if [[ -f "${{file_path}}" ]]; then
        perl -i -pe "s|${{sed_from}}|${{sed_to}}|g" "${{file_path}}"
    else
        echo "  !! WARNING: file ${{file_path}} does not exist; skipping."
    fi

    local after
    after=$( (git grep -l -- "${{sed_from}}" -- '*.py' 2>/dev/null || true) | wc -l | tr -d ' ')
    echo "  After: ${{after}} import sites (expect 0)"
    if [[ "${{after}}" != "0" ]]; then
        echo "  !! WARNING: ${{after}} import sites for ${{file_path}} survived."
        echo "     Manual review required."
    fi
}}
"""


def emit_migration_americas_case_b() -> str:
    body = HEADER_CASE_B.format(
        title="Americas (case-B) — domain-first rewrite of 9 files",
        script_name="migration_americas_case_b.sh",
        change_id=CHANGE_ID,
    )

    body += "\n# ----------------------------------------------------------------------------\n"
    body += (
        f"# Pair list ({len(_AMERICAS_CASE_B_TRIPLES)} per-file rewrites; "
        "deterministic, sourced from\n"
        "# the Phase 0.2 audit §1.6 case-B + Subagent E post-mortem §3.3)\n"
    )
    body += "# ----------------------------------------------------------------------------\n\n"

    for file_path, country_cap, vertical, domain in _AMERICAS_CASE_B_TRIPLES:
        country_lower = country_cap.lower()
        # Match the exact broken statement (vertical followed by `[[:space:]]+import`).
        # `[[:space:]]+` is POSIX BRE/ERE-safe (no GNU extension) so the
        # macOS BSD `git grep` BEFORE-counting step works without surprises.
        # Perl substitution also handles `[[:space:]]+` the same way.
        sed_from = (
            f"from dlt_sources\\.americas\\.{country_cap}\\.{vertical}[[:space:]]+import"
        )
        sed_to = (
            f"from dlt_sources.{domain}.{country_lower}.american_nations import"
        )
        body += "apply_pair_b "
        body += _shell_quote(sed_from) + " "
        body += _shell_quote(sed_to) + " "
        body += _shell_quote(file_path) + "\n"

    body += "\n# Done.\n"
    return SHEBANG + body


APPLY_ALL_HEADER = r"""#
# apply_all.sh -- Phase 0.2 dependency-ordered runner for the 6 ISO-3 ->
# snake_case migration scripts of the openspec change `{change_id}`.
#
# Generated by `_generator.py`. Each migration script is itself idempotent;
# running this twice has the same effect as running it once.
#
# Pair counts (sourced from `dlt_sources/LEGACY_ALIASES.md`):
#   migration_commonwealth_nigeria_states.sh      : {nga} pairs (deepest path)
#   migration_commonwealth_canada_provinces.sh    : {can} pairs
#   migration_commonwealth.sh                     : {cwl} pairs
#   migration_european_nations.sh                 : {eur} pairs
#   migration_british_isles.sh                    : {bri} pairs
#   migration_americas.sh                         : {ame} pairs (case-A: 6 files)
#   migration_americas_case_b.sh                  : 9 pairs (case-B: 9 files)
#
# Ordering rule (sed-migration safety: most specific first):
#
#   1. `migration_commonwealth_nigeria_states.sh`
#      -- `commonwealth.nigeria.states.nga_<3>` is the deepest of the 6
#         path patterns.
#   2. `migration_commonwealth_canada_provinces.sh`
#      -- `commonwealth.can.<2>` must be rewritten to
#         `commonwealth.canada.provinces.<prov>` BEFORE the broader
#         `commonwealth.can -> commonwealth.canada` rename fires
#         (otherwise the province rewrite would land after the parent
#         collapse and miss).
#   3. `migration_commonwealth.sh`
#      -- canonical rename of all 6 jurisdictions
#         (aus/can/ind/nga/nzl/zaf). The `nga -> nigeria` rewrite happens
#         here, not in step 1; the step 1 sed pattern ends in `\b` which
#         won't collide.
#   4. `migration_european_nations.sh`
#      -- {eur} European ISO-3 codes. Independent of the commonwealth subtree.
#   5. `migration_british_isles.sh`
#      -- {bri} BI ISO-3 codes (en/ni/sct/wls/iom/jey/ggy). Independent.
#   6. `migration_americas_case_b.sh` (case-B, 9 files under
#      `{{law,education,medicine}}/<country>/american_nations/`)
#   7. `migration_americas.sh` (case-A, 6 files in `american_nations/` subtree)
#      -- case-B MUST run before case-A. The case-A sed pattern
#         `from dlt_sources\.americas\.<Country>\.` would otherwise rewrite
#         the case-B imports to the wrong target
#         (`from dlt_sources.american_nations.<country>.<vertical>` instead
#         of the domain-first `from dlt_sources.<domain>.<country>.american_nations`).
#         Case-B replaces the `<vertical>.` segment entirely so after case-B
#         the case-A pattern no longer matches the case-B files.
#
# Each of the 7 scripts is independent of the others and could be run alone;
# `apply_all.sh` just enforces the safe order when applying them all.
#
# Usage:
#   bash apply_all.sh           # APPLY in dependency order (default)
#   bash apply_all.sh --dry-run # print what would happen; do NOT write
#
# All scripts use `perl -i -pe` (NOT BSD `sed`) for the in-place edit.
#
# MUST be run from the REPO ROOT (cwd) so `git grep` / `git mv` resolve
# correctly. The script enforces no cwd check; out-of-tree runs will
# silently fail.

set -euo pipefail

DRY_RUN=0
if [[ "${{1:-}}" == "--dry-run" ]]; then
    DRY_RUN=1
    echo "[DRY RUN] No filesystem or git operations will be performed."
    echo
fi

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"

run() {{
    local script="$1"
    local path="${{SCRIPT_DIR}}/${{script}}"
    if [[ ! -f "${{path}}" ]]; then
        echo "!! ERROR: missing sibling script: ${{path}}" >&2
        exit 1
    fi
    if [[ "${{DRY_RUN}}" == "1" ]]; then
        echo "============================================================"
        echo "== [DRY RUN] ${{script}}"
        echo "============================================================"
        bash "${{path}}" --dry-run
    else
        echo "============================================================"
        echo "== APPLY ${{script}}"
        echo "============================================================"
        bash "${{path}}"
    fi
    echo
}}

# ----- 1. deepest path first -----
run "migration_commonwealth_nigeria_states.sh"
# ----- 2. provinces before the broader commonwealth rename -----
run "migration_commonwealth_canada_provinces.sh"
# ----- 3. commonwealth top-level -----
run "migration_commonwealth.sh"
# ----- 4. european_nations (independent subtree) -----
run "migration_european_nations.sh"
# ----- 5. british_isles (independent subtree) -----
run "migration_british_isles.sh"
# ----- 6. americas case-B FIRST (9 files in {{law,education,medicine}}/<country>/american_nations/) -----
# Must run before case-A because the case-A sed pattern
# `from dlt_sources\.americas\.<Country>\.` would otherwise rewrite
# the case-B imports to the wrong target
# (`from dlt_sources.american_nations.<country>.<vertical>` instead
# of the domain-first `from dlt_sources.<domain>.<country>.american_nations`).
# Case-B's perl replaces the `<vertical>.` segment entirely, so after
# case-B the case-A pattern no longer matches the case-B files.
run "migration_americas_case_b.sh"
# ----- 7. americas case-A (6 files in american_nations/<country>/{{government,statistics}}/__) -----
run "migration_americas.sh"

echo "============================================================"
echo "== ALL DONE"
echo "============================================================"
echo "Next: re-run 'mise run dlt:smoke-all' to verify the broken legacy imports are now resolvable."
echo "Then: open the sub-change 2026-08-24-legacy-import-fix-v1 per tasks.md task 2.5."
"""


def emit_apply_all(waves: list[WaveSpec]) -> str:
    by_name = {w.script_name: w for w in waves}
    eur = len(by_name["migration_european_nations.sh"].pairs)
    bri = len(by_name["migration_british_isles.sh"].pairs)
    cwl = len(by_name["migration_commonwealth.sh"].pairs)
    can = len(by_name["migration_commonwealth_canada_provinces.sh"].pairs)
    nga = len(by_name["migration_commonwealth_nigeria_states.sh"].pairs)
    ame = len(by_name["migration_americas.sh"].pairs)
    body = APPLY_ALL_HEADER.format(
        change_id=CHANGE_ID,
        eur=eur,
        bri=bri,
        cwl=cwl,
        can=can,
        nga=nga,
        ame=ame,
    )
    return SHEBANG + body


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 0 if up-to-date, 1 otherwise",
    )
    args = parser.parse_args(argv)

    text = LEGACY_ALIASES.read_text(encoding="utf-8")
    waves = parse_legacy_aliases(text)

    outputs: dict[str, str] = {}
    for spec in waves:
        outputs[spec.script_name] = emit_migration_script(spec)
    # Wave 6 case-B sub-script: 9 domain-first per-file rewrites. Lives
    # alongside the standard wave scripts; `apply_all.sh` runs it after
    # `migration_americas.sh` (case-A).
    outputs["migration_americas_case_b.sh"] = emit_migration_americas_case_b()
    outputs["apply_all.sh"] = emit_apply_all(waves)

    if args.check:
        ok = True
        for fname, expected in outputs.items():
            path = HERE / fname
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                ok = False
        return 0 if ok else 1

    for fname, content in outputs.items():
        path = HERE / fname
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
