"""Marks `orchestration/defs/` as a regular (non-namespace) package.

Without this file, `orchestration/defs/` is an implicit PEP 420 namespace
package, which has no `__file__` — `orchestration/definitions.py`'s primary
`dg.load_defs(defs_root=Path(_defs_pkg.__file__).parent)` call then raises
`TypeError: argument should be a str or an os.PathLike object, not 'NoneType'`
inside `Path(None)`, and silently falls back to the 1.10-era `_defs_walker`.

Digit-prefixed layer directories (`2_materials/`, `3_model_lifecycle/`, ...)
are not valid Python identifiers on their own (`2_` parses as an incomplete
numeric literal) — that's a permanent tax of this 5-layer naming scheme, not
a bug, and `definitions.py`'s existing `importlib` workaround for it is kept
as-is.
"""
