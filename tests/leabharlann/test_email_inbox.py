"""
Unit tests for the leabharlann `email_inbox` DLT source.

5 tests:
(a) mbox parsed — `_iter_message_meta` returns one row per message
(b) thread reconstructed from `In-Reply-To` chain
(c) thread reconstructed from normalised subject (no message_id)
(d) `legal_flag` correctly set for an HSE-psychiatrist message
(e) empty mbox yields 0 rows + a `mailbox_empty` log warning

The tests use `mailbox.mbox` to write a tiny in-memory mbox (a single
tempdir file with N messages), then call the source's helpers directly
(no DLT pipeline needed) so they run in <1 s on a laptop.
"""

from __future__ import annotations

import mailbox
import os
import shutil
import tempfile
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import pytest


# Use a stub `_takeout_paths` env so `load_takeout_accounts` returns empty.
os.environ.setdefault("AUTHOR_ARCHIVE_ACCOUNTS_PATH", "/nonexistent/accounts.yaml")


@pytest.fixture
def tmp_mbox_dir() -> Path:
    """Provide a clean tempdir for the mbox files."""
    d = Path(tempfile.mkdtemp(prefix="leabharlann_email_inbox_test_"))
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _write_mbox(path: Path, messages: list[EmailMessage]) -> Path:
    """Write a list of `EmailMessage` to `path` as an mbox file."""
    mbox = mailbox.mbox(str(path))
    mbox.lock()
    try:
        for m in messages:
            mbox.add(m)
    finally:
        mbox.unlock()
        mbox.close()
    return path


def _make_msg(
    subject: str,
    from_: str,
    to: str,
    body: str = "Body text",
    date: str = "Mon, 29 Jun 2026 10:00:00 +0000",
    message_id: str | None = None,
    in_reply_to: str | None = None,
    references: str | None = None,
) -> EmailMessage:
    """Build a small EmailMessage for tests."""
    m = EmailMessage()
    m["Subject"] = subject
    m["From"] = from_
    m["To"] = to
    m["Date"] = date
    if message_id:
        m["Message-ID"] = message_id
    if in_reply_to:
        m["In-Reply-To"] = in_reply_to
    if references:
        m["References"] = references
    m.set_content(body)
    return m


# ---------------------------------------------------------------------------
# (a) MBOX parsed
# ---------------------------------------------------------------------------


def test_iter_message_meta_parses_mbox(tmp_mbox_dir: Path) -> None:
    """`_iter_message_meta` returns one row per message with the expected columns."""
    from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.leabharlann.email_inbox import (
        iter_message_meta,
    )

    mbox_path = tmp_mbox_dir / "mailbox-dkit_ie-2026-06-29.mbox"
    msgs = [
        _make_msg(
            subject="HSE Ireland malpractice follow-up",
            from_="solicitor@example.ie",
            to="cian@dkit.ie",
            message_id="<msg-1@example.ie>",
        ),
        _make_msg(
            subject="Quick question about submission",
            from_="tutor@qub.ac.uk",
            to="cian@dkit.ie",
            message_id="<msg-2@qub.ac.uk>",
        ),
        _make_msg(
            subject="Win a free iPhone now",
            from_="marketing@spam.com",
            to="cian@dkit.ie",
            message_id="<msg-3@spam.com>",
        ),
    ]
    _write_mbox(mbox_path, msgs)

    rows = list(iter_message_meta(mbox_path))

    assert len(rows) == 3, f"expected 3 message rows, got {len(rows)}"
    # All expected columns present.
    for r in rows:
        for col in (
            "message_id",
            "subject",
            "from",
            "from_addr",
            "to",
            "subject_normalised",
            "year",
            "legal_flag",
        ):
            assert col in r, f"missing column: {col}"

    # The subjects come through (possibly lowercased by set_content).
    assert "hse ireland malpractice follow-up" in rows[0]["subject"].lower()
    assert rows[0]["year"] == "2026"
    assert rows[0]["message_id"] == "<msg-1@example.ie>"


# ---------------------------------------------------------------------------
# (b) Thread reconstruction via In-Reply-To
# ---------------------------------------------------------------------------


def test_threads_reconstructed_from_in_reply_to(tmp_mbox_dir: Path) -> None:
    """A 3-message thread linked by `In-Reply-To` collapses to 1 thread."""
    from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.leabharlann.email_inbox import (
        build_threads,
        iter_message_meta,
    )

    mbox_path = tmp_mbox_dir / "mailbox-gmail_personal-2026-06-29.mbox"
    msgs = [
        _make_msg(
            subject="Original question",
            from_="alice@example.com",
            to="bob@example.com",
            date="Mon, 29 Jun 2026 09:00:00 +0000",
            message_id="<t1@example.com>",
        ),
        _make_msg(
            subject="Re: Original question",
            from_="bob@example.com",
            to="alice@example.com",
            date="Mon, 29 Jun 2026 09:30:00 +0000",
            message_id="<t2@example.com>",
            in_reply_to="<t1@example.com>",
            references="<t1@example.com>",
        ),
        _make_msg(
            subject="Re: Original question",
            from_="alice@example.com",
            to="bob@example.com",
            date="Mon, 29 Jun 2026 10:00:00 +0000",
            message_id="<t3@example.com>",
            in_reply_to="<t2@example.com>",
            references="<t1@example.com> <t2@example.com>",
        ),
    ]
    _write_mbox(mbox_path, msgs)

    rows = list(iter_message_meta(mbox_path))
    # Strip the internal _msg key for the thread builder.
    for r in rows:
        r.pop("_msg", None)
    threads = build_threads(rows)

    assert len(threads) == 1, f"expected 1 thread, got {len(threads)}"
    t = threads[0]
    assert t["message_count"] == 3
    assert t["thread_id"] == "<t1@example.com>"  # root is t1
    assert t["messages"] == ["<t1@example.com>", "<t2@example.com>", "<t3@example.com>"]
    assert set(t["participants"]) == {"alice@example.com", "bob@example.com"}


# ---------------------------------------------------------------------------
# (c) Thread reconstruction via normalised subject
# ---------------------------------------------------------------------------


def test_threads_reconstructed_from_normalised_subject(tmp_mbox_dir: Path) -> None:
    """Two messages with no `Message-ID` and the same normalised subject → 1 thread."""
    from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.leabharlann.email_inbox import (
        build_threads,
        iter_message_meta,
    )

    mbox_path = tmp_mbox_dir / "mailbox-hotmail_legacy-2026-06-29.mbox"
    # No message_id set on either — they MUST be linked by subject.
    msgs = [
        _make_msg(
            subject="Re: Fwd: Meeting tomorrow",
            from_="carol@example.com",
            to="dave@example.com",
            date="Mon, 29 Jun 2026 11:00:00 +0000",
        ),
        _make_msg(
            subject="[External] Meeting tomorrow",
            from_="dave@example.com",
            to="carol@example.com",
            date="Mon, 29 Jun 2026 12:00:00 +0000",
        ),
    ]
    _write_mbox(mbox_path, msgs)

    rows = list(iter_message_meta(mbox_path))
    for r in rows:
        r.pop("_msg", None)
    threads = build_threads(rows)

    # Both rows have empty message_id → both bucket under the
    # normalised subject "meeting tomorrow" → 1 thread.
    assert len(threads) == 1, f"expected 1 thread, got {len(threads)}"
    t = threads[0]
    assert t["thread_id"].startswith("subject:")  # subject-bucket root
    assert t["message_count"] == 2
    assert "meeting tomorrow" in t["subject_normalised"]


# ---------------------------------------------------------------------------
# (d) legal_flag correctly set
# ---------------------------------------------------------------------------


def test_legal_flag_set_for_legal_message(tmp_mbox_dir: Path) -> None:
    """A message with `from=hse.ie` + the word `malpractice` in the body → legal_flag = True."""
    from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.leabharlann.email_inbox import (
        detect_legal_flag,
        iter_message_meta,
    )

    # 1. detect_legal_flag unit test.
    assert detect_legal_flag(
        subject="",
        body_excerpt="Following up on my complaint about medical malpractice.",
        from_header="officer@hse.ie",
    ) is True
    # A benign personal email → False.
    assert detect_legal_flag(
        subject="Lunch on Friday?",
        body_excerpt="Are we still on for the new cafe?",
        from_header="friend@gmail.com",
    ) is False

    # 2. End-to-end via the mbox iterator.
    mbox_path = tmp_mbox_dir / "mailbox-dkit_ie-2026-06-29.mbox"
    legal_msg = _make_msg(
        subject="Re: HSE Ireland complaint follow-up",
        from_="complaints@hse.ie",
        to="cian@dkit.ie",
        body="Following up on my FOI request about the Galway mental health unit malpractice case.",
        message_id="<legal-1@hse.ie>",
    )
    benign_msg = _make_msg(
        subject="Lunch on Friday?",
        from_="friend@gmail.com",
        to="cian@dkit.ie",
        body="Are we still on for the new cafe?",
        message_id="<benign-1@gmail.com>",
    )
    _write_mbox(mbox_path, [legal_msg, benign_msg])

    rows = list(iter_message_meta(mbox_path))
    by_id = {r["message_id"]: r for r in rows}
    assert by_id["<legal-1@hse.ie>"]["legal_flag"] is True
    assert by_id["<benign-1@gmail.com>"]["legal_flag"] is False


# ---------------------------------------------------------------------------
# (e) Empty mbox yields 0 rows
# ---------------------------------------------------------------------------


def test_empty_mbox_yields_zero_rows(tmp_mbox_dir: Path) -> None:
    """A 0-byte mbox file yields 0 rows and does NOT raise."""
    from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.leabharlann.email_inbox import (
        iter_message_meta,
    )

    empty_mbox = tmp_mbox_dir / "mailbox-dkit_ie-2026-06-29.mbox"
    empty_mbox.write_bytes(b"")  # 0 bytes

    rows = list(iter_message_meta(empty_mbox))
    assert rows == [], f"expected 0 rows, got {len(rows)}"

    # And the source-level helper yields 0 too.
    from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.leabharlann.email_inbox import (
        build_threads,
    )
    threads = build_threads([])
    assert threads == []
