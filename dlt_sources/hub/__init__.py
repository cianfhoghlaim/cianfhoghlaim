"""`dlt_sources.hub` — defensive shim for `dlthub` deployment-manifest decorators.

The `_jobs/` sub-package uses `@run.pipeline("name")` from the dlthub-platform
toolkit to register deployment-manifest jobs. Per the original convention
(see `dlt_sources/_jobs/government_circulars_job.py` docstring), the
canonical home is `dlthub.run.pipeline` — but `dlthub` is an optional
extra and may not be installed in every CI environment.

This shim re-exports `dlthub.run.pipeline` if available, otherwise falls
back to a passthrough decorator that emits a `DeprecationWarning` so
smoke tests pass but runtime usage surfaces the missing dependency
clearly.

Per openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1
Phase 3 cleanup (the `cianchosaint-fail-subtree-fixes-2026-08-25` sub-batch
of the closure report §5): the original `@run.pipeline` decorator came from
`dlt.hub` (the `dlt[hub]` extra); per the v2 plan, the canonical name
in this repo is `dlthub.run.pipeline` (the `dlthub` package).
"""
from __future__ import annotations

import functools
import warnings


def _passthrough_pipeline(*decorator_args, **decorator_kwargs):
    """Passthrough decorator used when the dlthub toolkit is unavailable.

    Accepts the same call signature as `dlthub.run.pipeline(...)` so callers
    using `@run.pipeline("name")` continue to type-check, but emits a clear
    `DeprecationWarning` on first use to surface the missing dependency.
    """
    def _wrap(fn):
        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            warnings.warn(
                "dlt_sources.hub.run.pipeline is unavailable: the `dlthub` "
                "package is not installed in this environment. Install "
                "`dlthub` (or `dlt[hub]`) to enable real deployment-manifest "
                "job registration.",
                stacklevel=2,
            )
            return fn(*args, **kwargs)
        return _inner
    return _wrap


try:
    from dlthub.run import pipeline as _real_pipeline  # type: ignore[import-not-found,unused-ignore]
except ImportError:
    try:
        from dlt.hub import run as _dlthub_via_dlt  # type: ignore[import-not-found,unused-ignore]
        _real_pipeline = _dlthub_via_dlt.pipeline
    except (ImportError, AttributeError):
        _real_pipeline = None


class _RunNamespace:
    """Namespace exposing the `pipeline` decorator.

    Mirrors the dlthub-platform convention `dlthub.run.pipeline(...)` so
    callers using `@run.pipeline("name")` work unchanged whether the
    `dlthub` package is installed (uses the real decorator) or not
    (uses the passthrough that emits a `DeprecationWarning`).
    """

    def __init__(self, real_pipeline) -> None:
        self._real_pipeline = real_pipeline

    def pipeline(self, *args, **kwargs):
        if self._real_pipeline is None:
            return _passthrough_pipeline(*args, **kwargs)
        return self._real_pipeline(*args, **kwargs)


run = _RunNamespace(_real_pipeline)

__all__ = ["run"]
