"""Smoke tests for ``oideachais.api.routes.official_media``.

Asserts the 3 FastAPI endpoints:

  - GET  /api/official-media/candidates
  - GET  /api/official-media/{candidate_id}
  - POST /api/official-media/upload
"""
from __future__ import annotations

import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/official-media/candidates
# ---------------------------------------------------------------------------


def test_list_candidates_returns_allowlist(client: TestClient) -> None:
    """In offline mode, the candidates endpoint serves the curated
    allowlist as a fallback so the dashboard has something to render."""
    resp = client.get("/api/official-media/candidates")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 50  # the 4 allowlist YAMLs have ~73 entries
    # Every row has the expected shape
    for row in data:
        assert "ig_username" in row
        assert "category" in row
        assert "match_stage" in row


def test_list_candidates_filter_by_category(client: TestClient) -> None:
    resp = client.get("/api/official-media/candidates?category=university")
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["category"] == "university" for r in data)
    assert len(data) >= 5  # the universities allowlist has 12 entries


def test_list_candidates_limit(client: TestClient) -> None:
    resp = client.get("/api/official-media/candidates?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5


# ---------------------------------------------------------------------------
# GET /api/official-media/{candidate_id}
# ---------------------------------------------------------------------------


def test_get_resolved_source_for_gchq(client: TestClient) -> None:
    resp = client.get("/api/official-media/gchq@allowlist")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ig_username"] == "gchq"
    assert data["official_website"] == "https://www.gchq.gov.uk"
    assert data["resolver_notes"] == "override"


def test_get_resolved_source_404_for_unknown(client: TestClient) -> None:
    resp = client.get("/api/official-media/this_does_not_exist")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/official-media/upload
# ---------------------------------------------------------------------------


def test_upload_zip_accepts_valid_file(client: TestClient) -> None:
    """A minimal valid Instagram-export-like zip upload returns a
    job id and the upload path."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("connections/followers_and_following/following.json", '{"relationships_following":[]}')
    zip_buffer.seek(0)
    resp = client.post(
        "/api/official-media/upload",
        files={"file": ("instagram_export.zip", zip_buffer, "application/zip")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "upload_path" in data


def test_upload_rejects_non_zip(client: TestClient) -> None:
    """A non-zip file is rejected with a 400."""
    resp = client.post(
        "/api/official-media/upload",
        files={"file": ("export.txt", io.BytesIO(b"not a zip"), "text/plain")},
    )
    assert resp.status_code == 400
