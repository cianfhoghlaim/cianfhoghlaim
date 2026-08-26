"""`dlt_sources.constants` — canonical home for dlt_sources-scoped constants.

Per the
`2026-08-24-dlt-sources-to-multi-repo-scaffold-v1` Phase 3 cleanup
(the `cianchosaint-fail-subtree-fixes-2026-08-25` sub-batch), this
package consolidates the 3 per-subtree phantom-imports
(`dlt_sources.constants.local_sources`,
`dlt_sources.constants.local_sources`) that were scattered across
`dlt_sources/local_archive/`, `dlt_sources/cultural_heritage/`, and
`dlt_sources/lexicographic/` after the Wave 1 restructure
(`2026-08-24-wave-1-dlt-sources-domain-restructure-v1`).

The 3 Phase 4 deferred FAILs (`cultural_heritage`, `lexicographic`,
and the `language/` circular import) are not fixed here — they
require the ciancheiltis split per the v2 plan §A bilingual
educational carve rule.

This package re-exports the canonical symbols from
`dlt_sources.raw_files` (where the scanner / leabharlann books
helpers already live per the v2 plan §A "UoG personal archive stays
in filesystem/" rule) and defines the 5 missing local-archive
constants inline.

New code SHOULD import from `dlt_sources.raw_files` directly where
the symbol already exists there.
"""
