"""
Leabharlann Email Inbox DLT source (Phase 1: MBOX filesystem).

Scans `/srv/mailcow-exports/*.mbox` (populated by the Mailcow
`dovecot_imapsync_runner` ofelia job + the new `mailcow-export`
companion container) and yields 4 resources per partition:

1. `inbox_index`           — one row per message (header + body_excerpt)
2. `inbox_threads`         — one row per reconstructed thread
3. `inbox_attachments`     — one row per attachment metadata
4. `inbox_legal_threads`   — one row per thread where `legal_flag = true`

MBOX parsing uses Python's `mailbox` stdlib (single-pass iterator,
never loads the full file into memory). Thread reconstruction walks
the `In-Reply-To` + `References` chain, then falls back to a normalised
subject (strip `Re:`, `Fwd:`, `Fwd: Re:`, `[list-tag]`, `(External)`).

Partition keys:
- `account`    — `DynamicPartitionsDefinition` from
                 `author_archive_accounts.yaml` (4 accounts)
- `year`       — 4-digit string from the message `Date` header
- `legal_flag` — boolean from a first-500-char keyword scan +
                 sender-domain regex on the first 500 chars

GPG-at-rest is opt-in via the existing
`_takeout_paths.TakeoutAccountConfig.gpg_encrypt_paths` knob (we reuse
the same field, with prefixes `legal/`, `medical/`, `hsc/`, `nhs/`).

LBYL exception handling per the `dignified-python` skill: every `next()`
boundary catches `OSError` + `mailbox.Error` + `RuntimeError` so a
single bad message never crashes the source. Empty mbox files yield
0 rows and a `mailbox_empty` log warning.

Reference: openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/
"""

from __future__ import annotations
import dlt


import mailbox
import os
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from email import policy
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

from ._takeout_paths import (
    TakeoutAccountConfig,
    load_takeout_accounts,
)

logger = structlog.get_logger(__name__)


# Default path of the MBOX export directory. Overridden by the
# `LEABHARLANN_INBOX_MBOX_ROOT` env var.
DEFAULT_MBOX_ROOT = Path(
    os.environ.get(
        "LEABHARLANN_INBOX_MBOX_ROOT",
        "/srv/mailcow-exports",
    )
)


# Common attachments vs. body heuristic: anything in `Content-Disposition`
# with a `filename` parameter is an attachment. Inline images are also
# attachments but we ignore them (no OCR) for the e2e demo.
_ATTACHMENT_DISPOSITION_RE = re.compile(
    r"^\s*attachment\s*;", re.IGNORECASE
)

# Legal-flag keywords. We scan the first 500 chars of (subject + body)
# and the first 500 chars of the `from` header for any of these.
_LEGAL_KEYWORDS: tuple[str, ...] = (
    "legal",
    "tribunal",
    "discrimination",
    "dismissal",
    "harassment",
    "grievance",
    "wrc",
    "circuit court",
    "high court",
    "supreme court",
    "fraud",
    "negligence",
    "malpractice",
    "defamation",
    "solicitor",
    "barrister",
    "complaint to",
    "right of reply",
    "appeal",
    "tribunal",
)

# Sender-domain regex (case-insensitive): any of these on the first
# 500 chars of the `from` address flips `legal_flag` to true.
_LEGAL_SENDER_DOMAINS: tuple[str, ...] = (
    r"@courts\.ie",
    r"@lawsociety\.ie",
    r"@justice\.ie",
    r"@hse\.ie",          # HSE complaints touch legal channels
    r"@wrc\.ie",
    r"@circuitcourt\.ie",
    r"@barofireland\.ie",
    r"@intralex\.ie",
    r"@arthurcox\.ie",
    r"@mccannfitzgerald\.com",
    r"@aandlgoodbody\.com",
)

# Subject normalisation: strip these prefixes (case-insensitive) before
# grouping messages into threads. Order matters (longest prefix first).
_SUBJECT_PREFIXES_TO_STRIP: tuple[str, ...] = (
    r"fwd:\s*re:\s*",
    r"re:\s*fwd:\s*",
    r"fwd:\s*",
    r"re:\s*",
)

# Bracketed / parenthesised tag patterns to strip (e.g. `[External]`,
# `(Confidential)`, `[list-tag]`).
_SUBJECT_BRACKET_RE = re.compile(r"[\[\(][^\]\)]*[\]\)]")
_SUBJECT_WS_RE = re.compile(r"\s+")


# ============================================================================
# Helpers
# ============================================================================


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_decode_header(value: str | None) -> str:
    """Best-effort decode of a single header value. Returns "" on None."""
    if not value:
        return ""
    try:
        return str(value).strip()
    except (UnicodeDecodeError, AttributeError):
        return ""


def _extract_address(header: str | None) -> str:
    """Extract the email address (lowercased) from a From/To/Cc header.

    Handles both `"Name <addr@x>"` and bare `addr@x` shapes.
    """
    if not header:
        return ""
    text = _safe_decode_header(header)
    m = re.search(r"<([^>]+@[^>]+)>", text)
    if m:
        return m.group(1).strip().lower()
    m2 = re.search(r"([\w.+\-]+@[\w.\-]+\.[A-Za-z]{2,})", text)
    return m2.group(1).strip().lower() if m2 else ""


def _extract_sender_domain(from_header: str | None) -> str:
    """Extract the sender's email domain (after `@`). Returns "" on failure."""
    addr = _extract_address(from_header)
    if "@" in addr:
        return addr.rsplit("@", 1)[1].lower()
    return ""


def _normalise_subject(subject: str | None) -> str:
    """Strip `Re:` / `Fwd:` / `Fwd: Re:` / `[list-tag]` / `(External)` prefixes.

    Returns the lowercase, whitespace-collapsed remainder. Falls back to "".
    """
    if not subject:
        return ""
    s = _safe_decode_header(subject)
    # Strip bracketed / parenthesised tags first (e.g. `[External]`).
    s = _SUBJECT_BRACKET_RE.sub("", s)
    # Strip leading prefixes (longest first so `Fwd: Re:` beats `Re:`).
    for prefix in _SUBJECT_PREFIXES_TO_STRIP:
        s = re.sub(f"^{prefix}", "", s, flags=re.IGNORECASE)
    s = _SUBJECT_WS_RE.sub(" ", s).strip().lower()
    return s


def _parse_date_to_year(date_header: str | None) -> str:
    """Parse an RFC 2822 date header to a 4-digit year string.

    Returns "unknown" on failure (LBYL — never raise).
    """
    if not date_header:
        return "unknown"
    try:
        dt = parsedate_to_datetime(date_header)
    except (TypeError, ValueError):
        return "unknown"
    if dt is None:
        return "unknown"
    return str(dt.year)


def _parse_date_to_iso(date_header: str | None) -> str:
    """Parse an RFC 2822 date header to an ISO 8601 string. Returns "" on failure."""
    if not date_header:
        return ""
    try:
        dt = parsedate_to_datetime(date_header)
    except (TypeError, ValueError):
        return ""
    if dt is None:
        return ""
    try:
        return dt.isoformat()
    except (AttributeError, ValueError):
        return ""


def _detect_legal_flag(
    subject: str | None,
    body_excerpt: str,
    from_header: str | None,
) -> bool:
    """Heuristic `legal_flag` from the first 500 chars + sender domain.

    Returns True if any legal keyword appears in the first 500 chars of
    the combined subject + body, OR if the sender domain matches the
    legal-domain regex on the first 500 chars of the `from` address.
    """
    blob = f"{subject or ''} {body_excerpt or ''}"[:500].lower()
    if any(kw in blob for kw in _LEGAL_KEYWORDS):
        return True
    from_blob = (from_header or "")[:500].lower()
    for pattern in _LEGAL_SENDER_DOMAINS:
        if re.search(pattern, from_blob):
            return True
    return False


def _get_message_body(msg: Any) -> str:
    """Extract a plaintext body excerpt (first 2000 chars). Graceful on failure.

    Works with both `email.message.EmailMessage` (modern API) and
    `mailbox.mboxMessage` (the default mbox factory). On
    `mboxMessage`, `get_payload(decode=True)` may return a `str` directly.
    """
    try:
        is_multipart = getattr(msg, "is_multipart", None)
        is_multi = bool(is_multipart()) if callable(is_multipart) else False
        if is_multi:
            walk = getattr(msg, "walk", None)
            if not callable(walk):
                return ""
            for part in walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition") or "")
                if ctype == "text/plain" and not _ATTACHMENT_DISPOSITION_RE.match(disp):
                    payload = part.get_payload(decode=True) or b""
                    if isinstance(payload, str):
                        return payload[:2000]
                    try:
                        return payload.decode(
                            part.get_content_charset() or "utf-8", errors="replace"
                        )[:2000]
                    except (LookupError, UnicodeDecodeError, TypeError):
                        try:
                            return payload.decode("utf-8", errors="replace")[:2000]
                        except (AttributeError, TypeError):
                            return str(payload)[:2000]
            return ""
        payload = msg.get_payload(decode=True) or b""
        if isinstance(payload, str):
            return payload[:2000]
        if isinstance(payload, list):
            # multipart fallback — concat text parts.
            return "".join(
                p[:2000] for p in payload if isinstance(p, str)
            )[:2000]
        try:
            return payload.decode(
                msg.get_content_charset() or "utf-8", errors="replace"
            )[:2000]
        except (LookupError, UnicodeDecodeError, TypeError, AttributeError):
            try:
                return payload.decode("utf-8", errors="replace")[:2000]
            except (AttributeError, TypeError):
                return str(payload)[:2000]
    except (OSError, ValueError, AttributeError):
        return ""


def _iter_message_meta(
    mbox_path: Path,
) -> Iterator[dict[str, Any]]:
    """Stream-iterate a single mbox file, yielding one metadata row per message.

    LBYL: every `next()` boundary is wrapped so a corrupt mbox or a
    single bad message never crashes the source. Empty files yield 0
    rows + a `mailbox_empty` log warning.
    """
    if not mbox_path.exists():
        return
    try:
        mbox_size = mbox_path.stat().st_size
    except OSError as e:
        logger.warning("mbox_stat_failed", path=str(mbox_path), error=str(e))
        return
    if mbox_size == 0:
        logger.warning("mailbox_empty", path=str(mbox_path))
        return
    try:
        # Use the default `mboxMessage` factory — it has `.get()`,
        # `.get_payload()`, and works with the standard `mailbox.mbox()`
        # writer. We intentionally do NOT pass `factory=EmailMessage`
        # because in Python 3.13 that path silently returns empty
        # headers; the default `mboxMessage` is the only reliable
        # option for mbox files written by `mailbox.mbox()`.
        mbox = mailbox.mbox(str(mbox_path))
    except (mailbox.Error, OSError, FileNotFoundError) as e:
        logger.warning("mbox_open_failed", path=str(mbox_path), error=str(e))
        return
    try:
        idx = 0
        for key in mbox.iterkeys():
            try:
                msg = mbox[key]
            except (mailbox.Error, KeyError, OSError) as e:
                logger.warning(
                    "mbox_message_load_failed",
                    path=str(mbox_path),
                    key=str(key),
                    error=str(e),
                )
                continue
            subject = _safe_decode_header(msg.get("Subject"))
            from_header = _safe_decode_header(msg.get("From"))
            to_header = _safe_decode_header(msg.get("To"))
            cc_header = _safe_decode_header(msg.get("Cc"))
            body_excerpt = _get_message_body(msg)
            in_reply_to = _safe_decode_header(msg.get("In-Reply-To"))
            references = _safe_decode_header(msg.get("References"))
            message_id = _safe_decode_header(msg.get("Message-ID"))
            dkim_sig = _safe_decode_header(msg.get("DKIM-Signature"))
            arc_results = _safe_decode_header(msg.get("ARC-Authentication-Results"))
            date_header = _safe_decode_header(msg.get("Date"))
            yield {
                "_msg": msg,
                "_msg_index": idx,
                "message_id": message_id,
                "in_reply_to": in_reply_to,
                "references": references,
                "subject": subject,
                "subject_normalised": _normalise_subject(subject),
                "from": from_header,
                "from_addr": _extract_address(from_header),
                "sender_domain": _extract_sender_domain(from_header),
                "to": to_header,
                "cc": cc_header,
                "recipients": ", ".join(
                    filter(None, [to_header, cc_header])
                ),
                "date_iso": _parse_date_to_iso(date_header),
                "year": _parse_date_to_year(date_header),
                "dkim_signature": dkim_sig[:1000] if dkim_sig else "",
                "arc_authentication_results": arc_results[:1000] if arc_results else "",
                "body_excerpt": body_excerpt,
                "legal_flag": _detect_legal_flag(subject, body_excerpt, from_header),
                "mbox_file": str(mbox_path),
                "mbox_relative": str(mbox_path.name),
            }
            idx += 1
    finally:
        try:
            mbox.close()
        except (mailbox.Error, OSError):  # pragma: no cover — best-effort
            pass


def _classify_attachments(msg: Any) -> list[dict[str, Any]]:
    """Return one metadata row per attachment. Empty list if none.

    Works with both `EmailMessage` and `mboxMessage`. The latter does
    not implement `iter_attachments()`; we fall back to scanning the
    payload list for parts with a `Content-Disposition: attachment`
    header.
    """
    rows: list[dict[str, Any]] = []
    try:
        iter_attachments = getattr(msg, "iter_attachments", None)
        if callable(iter_attachments):
            for part in iter_attachments():
                filename = part.get_filename() or ""
                content_type = part.get_content_type() or "application/octet-stream"
                try:
                    payload = part.get_payload(decode=True) or b""
                    if isinstance(payload, str):
                        size = len(payload.encode("utf-8"))
                    else:
                        size = len(payload)
                except (OSError, ValueError, TypeError):
                    size = 0
                rows.append(
                    {
                        "filename": filename,
                        "content_type": content_type,
                        "size_bytes": size,
                    }
                )
            return rows
        # Fallback: scan the payload for sub-messages.
        payload = msg.get_payload() or []
        if not isinstance(payload, list):
            return rows
        for part in payload:
            try:
                disp = str(part.get("Content-Disposition") or "")
            except (AttributeError, TypeError):
                continue
            if "attachment" not in disp.lower():
                continue
            try:
                filename = part.get_filename() or ""
                content_type = part.get_content_type() or "application/octet-stream"
                try:
                    raw = part.get_payload(decode=True) or b""
                    if isinstance(raw, str):
                        size = len(raw.encode("utf-8"))
                    else:
                        size = len(raw)
                except (OSError, ValueError, TypeError):
                    size = 0
                rows.append(
                    {
                        "filename": filename,
                        "content_type": content_type,
                        "size_bytes": size,
                    }
                )
            except (OSError, ValueError, AttributeError):
                continue
    except (OSError, ValueError, AttributeError):
        return []
    return rows


# ============================================================================
# Thread reconstruction
# ============================================================================


def _build_threads(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Group messages into threads via `In-Reply-To` chain + normalised subject.

    Each thread row has the shape:
    ```
    {
      "thread_id":         str,   # message_id of the root, or hash
                                # of the normalised subject
      "subject":           str,   # first non-empty subject
      "subject_normalised":str,
      "subject_root":      str,   # original subject (with Re: stripped)
      "account":           str,
      "year":              str,
      "message_count":     int,
      "messages":          [str], # message_ids in chronological order
      "participants":      [str], # unique from_addr values
      "first_message_at":  str,   # date_iso of the first message
      "last_message_at":   str,
      "legal_flag":        bool,  # OR over all messages
    }
    ```
    """
    # 1. Index by message_id (used to follow In-Reply-To chains).
    by_id: dict[str, dict[str, Any]] = {
        r["message_id"]: r for r in rows if r["message_id"]
    }
    # 2. Index by In-Reply-To target.
    in_reply_to_index: dict[str, list[str]] = {}
    for r in rows:
        target = r["in_reply_to"]
        if target:
            in_reply_to_index.setdefault(target, []).append(r["message_id"])

    # 3. Walk every message to find its root (the message with no
    #    In-Reply-To, or whose chain bottoms out at a message not in
    #    this batch).
    def _find_root(msg_id: str, _seen: set[str] | None = None) -> str:
        _seen = _seen or set()
        if msg_id in _seen:
            return msg_id  # cycle — break
        _seen.add(msg_id)
        row = by_id.get(msg_id)
        if row is None:
            return msg_id
        target = row["in_reply_to"]
        if target and target in by_id:
            return _find_root(target, _seen)
        return msg_id

    root_of: dict[str, str] = {}
    for r in rows:
        if not r["message_id"]:
            # No message_id — fall through to subject-based grouping.
            continue
        root_of[r["message_id"]] = _find_root(r["message_id"])

    # 4. Subject-based fallback bucket (for messages without message_id
    #    or whose In-Reply-To chain was outside the mbox).
    subject_bucket: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        subj = r["subject_normalised"] or "(no-subject)"
        root = root_of.get(r["message_id"])
        if root is None:
            # No message_id or root not in `by_id` — bucket by subject.
            subject_bucket.setdefault(subj, []).append(r)

    # 5. Group messages by thread root (or subject bucket).
    threads_by_root: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        root = root_of.get(r["message_id"])
        if root is None:
            # Subject-bucketed — assigned below.
            continue
        threads_by_root.setdefault(root, []).append(r)
    for subj, bucket in subject_bucket.items():
        synth_root = f"subject:{subj}"
        threads_by_root[synth_root] = bucket

    # 6. Emit one thread row per group.
    out: list[dict[str, Any]] = []
    for root_id, msgs in threads_by_root.items():
        # Sort chronologically.
        msgs.sort(key=lambda r: r.get("date_iso") or "")
        first = msgs[0]
        last = msgs[-1]
        legal = any(m.get("legal_flag") for m in msgs)
        participants = sorted({m["from_addr"] for m in msgs if m["from_addr"]})
        # The "original" subject (first non-empty).
        original_subject = next(
            (m["subject"] for m in msgs if m["subject"]), "(no subject)"
        )
        out.append(
            {
                "thread_id": root_id,
                "subject": original_subject,
                "subject_normalised": first["subject_normalised"],
                "subject_root": _normalise_subject(original_subject),
                "account": first.get("_msg_index") and rows[0].get("year", "unknown") or "unknown",  # placeholder
                "year": first.get("year", "unknown"),
                "message_count": len(msgs),
                "messages": [m["message_id"] for m in msgs if m["message_id"]],
                "participants": participants,
                "first_message_at": first.get("date_iso", ""),
                "last_message_at": last.get("date_iso", ""),
                "legal_flag": legal,
            }
        )

    # The placeholder "account" above is filled in by `_build_thread_rows`
    # (which has the account context). We re-key here so it's stable.
    return out


def _build_thread_rows(
    account: TakeoutAccountConfig,
    year: str,
    mbox_path: Path,
) -> list[dict[str, Any]]:
    """Build thread rows for a single mbox file. Returns [] on failure."""
    msgs: list[dict[str, Any]] = []
    for m in _iter_message_meta(mbox_path):
        msgs.append(m)
    if not msgs:
        return []
    threads = _build_threads(msgs)
    for t in threads:
        t["account"] = account.account_label
        t["year"] = year
        t["mbox_file"] = str(mbox_path)
    return threads


# ============================================================================
# DLT source
# ============================================================================


@dlt.source(name="leabharlann_email_inbox")
def email_inbox_source(
    base_path: str | Path = DEFAULT_MBOX_ROOT,
    config_path: str | Path | None = None,
    account_label: str | None = None,
):
    """
    DLT source for the leabharlann email-inbox pipeline.

    Scans `<base_path>/mailbox-<account>-<YYYY-MM-DD>.mbox` and yields
    4 resources (`inbox_index`, `inbox_threads`, `inbox_attachments`,
    `inbox_legal_threads`) per account.

    Args:
        base_path: Directory containing the MBOX files. Default
            `/srv/mailcow-exports` (overridden by the
            `LEABHARLANN_INBOX_MBOX_ROOT` env var).
        config_path: Path to `author_archive_accounts.yaml`. Defaults
            to `AUTHOR_ARCHIVE_ACCOUNTS_PATH` or
            `./author_archive_accounts.yaml` at CWD.
        account_label: If set, only the named account is processed
            (Dagster partition key). If None, all configured accounts
            are processed.
    """
    base_path = Path(base_path)
    accounts = load_takeout_accounts(config_path=config_path)

    selected: list[TakeoutAccountConfig] = []
    if account_label is not None:
        for a in accounts:
            if a.account_label == account_label:
                selected = [a]
                break
        if not selected:
            logger.warning(
                "email_inbox_account_not_found",
                account_label=account_label,
            )
            return _empty_resources()
    else:
        selected = list(accounts)

    if not base_path.exists():
        logger.warning(
            "email_inbox_base_path_missing",
            path=str(base_path),
        )
        return _empty_resources()

    # Pre-build a list of (account, year, mbox_path) tuples so each
    # resource can iterate independently.
    work_items: list[tuple[TakeoutAccountConfig, str, Path]] = []
    for account in selected:
        for mbox_path in sorted(base_path.glob(f"mailbox-{account.account_label}-*.mbox")):
            year = _year_from_mbox_filename(mbox_path.name) or "unknown"
            work_items.append((account, year, mbox_path))

    @dlt.resource(
        name="inbox_index",
        write_disposition="merge",
        primary_key=["account", "mbox_file", "_msg_index"],
        columns={
            "account": {"partition": True},
            "year": {"partition": True},
            "legal_flag": {"partition": True},
        },
    )
    def inbox_index() -> Iterator[dict[str, Any]]:
        """One row per message (header + body excerpt)."""
        for account, year, mbox_path in work_items:
            try:
                for m in _iter_message_meta(mbox_path):
                    m["account"] = account.account_label
                    m["year"] = year
                    m["discovered_at"] = _now_iso()
                    m.pop("_msg", None)  # don't serialise the EmailMessage
                    yield m
            except (OSError, RuntimeError) as e:  # pragma: no cover
                logger.warning(
                    "inbox_index_resource_failed",
                    account=account.account_label,
                    mbox=str(mbox_path),
                    error=str(e),
                )

    @dlt.resource(
        name="inbox_threads",
        write_disposition="merge",
        primary_key=["account", "thread_id"],
        columns={
            "account": {"partition": True},
            "year": {"partition": True},
            "legal_flag": {"partition": True},
        },
    )
    def inbox_threads() -> Iterator[dict[str, Any]]:
        """One row per reconstructed thread (In-Reply-To + subject)."""
        for account, year, mbox_path in work_items:
            try:
                for t in _build_thread_rows(account, year, mbox_path):
                    t["discovered_at"] = _now_iso()
                    yield t
            except (OSError, RuntimeError) as e:  # pragma: no cover
                logger.warning(
                    "inbox_threads_resource_failed",
                    account=account.account_label,
                    mbox=str(mbox_path),
                    error=str(e),
                )

    @dlt.resource(
        name="inbox_attachments",
        write_disposition="merge",
        primary_key=["account", "mbox_file", "filename"],
        columns={
            "account": {"partition": True},
            "year": {"partition": True},
        },
    )
    def inbox_attachments() -> Iterator[dict[str, Any]]:
        """One row per attachment metadata."""
        for account, year, mbox_path in work_items:
            for m in _iter_message_meta(mbox_path):
                msg = m.get("_msg")
                if not isinstance(msg, EmailMessage):
                    continue
                for att in _classify_attachments(msg):
                    yield {
                        "account": account.account_label,
                        "year": year,
                        "mbox_file": str(mbox_path),
                        "message_id": m.get("message_id", ""),
                        "filename": att["filename"],
                        "content_type": att["content_type"],
                        "size_bytes": att["size_bytes"],
                        "discovered_at": _now_iso(),
                    }

    @dlt.resource(
        name="inbox_legal_threads",
        write_disposition="merge",
        primary_key=["account", "thread_id"],
        columns={
            "account": {"partition": True},
            "year": {"partition": True},
        },
    )
    def inbox_legal_threads() -> Iterator[dict[str, Any]]:
        """One row per thread where `legal_flag = true`."""
        for account, year, mbox_path in work_items:
            for t in _build_thread_rows(account, year, mbox_path):
                if t.get("legal_flag"):
                    t["discovered_at"] = _now_iso()
                    yield t

    return inbox_index, inbox_threads, inbox_attachments, inbox_legal_threads


def _empty_resources():
    """Return a set of no-op resources for the case where no accounts / mbox exist."""

    @dlt.resource(name="inbox_index", write_disposition="merge", primary_key=["account", "mbox_file", "_msg_index"])
    def _index():
        if False:
            yield {}

    @dlt.resource(name="inbox_threads", write_disposition="merge", primary_key=["account", "thread_id"])
    def _threads():
        if False:
            yield {}

    @dlt.resource(name="inbox_attachments", write_disposition="merge", primary_key=["account", "mbox_file", "filename"])
    def _attachments():
        if False:
            yield {}

    @dlt.resource(name="inbox_legal_threads", write_disposition="merge", primary_key=["account", "thread_id"])
    def _legal():
        if False:
            yield {}

    return _index, _threads, _attachments, _legal


def _year_from_mbox_filename(name: str) -> str | None:
    """Pull the 4-digit year out of `mailbox-<account>-<YYYY-MM-DD>.mbox`."""
    m = re.search(r"(\d{4})-\d{2}-\d{2}", name)
    return m.group(1) if m else None


# ============================================================================
# Pipeline convenience
# ============================================================================


def create_email_inbox_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "leabharlann_email_inbox",
):
    """Create a DLT pipeline for the email-inbox source."""
    import dlt_sources as _dlt

    return _dlt.pipeline(
        pipeline_name="leabharlann_email_inbox_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "DEFAULT_MBOX_ROOT",
    "email_inbox_source",
    "create_email_inbox_pipeline",
    # Helpers (exported for unit tests + the CocoIndex App)
    "normalise_subject",
    "detect_legal_flag",
    "iter_message_meta",
    "build_threads",
    "build_thread_rows",
    "year_from_mbox_filename",
]


# Re-export internal helpers under the public names used in the
# test suite + the CocoIndex App.
normalise_subject = _normalise_subject
detect_legal_flag = _detect_legal_flag
iter_message_meta = _iter_message_meta
build_threads = _build_threads
build_thread_rows = _build_thread_rows
year_from_mbox_filename = _year_from_mbox_filename
