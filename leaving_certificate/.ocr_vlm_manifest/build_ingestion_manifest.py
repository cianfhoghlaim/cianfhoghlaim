"""Build the OCR/VLM ingestion manifest for the 148 Ireland LC PDFs.

This is the canonical artifact that tracks which official PDFs
have been ingested into the BIEP pipeline. It's the metadata
manifest that the BAML extraction (curriculum_syllabus.baml,
exam_paper_layout.baml, marking_scheme.baml, syllabus_diagram.baml)
uses to know which PDFs to process.

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
change (Phase 3 - OCR/VLM 4-path ensemble processing).
"""

import json
import hashlib
from pathlib import Path
from datetime import UTC, datetime


def main() -> None:
    root = Path("leaving_certificate")
    subjects = [
        "mathematics", "applied_mathematics", "chemistry", "physics",
        "biology", "geography", "gaeilge", "english",
        "french", "history", "business", "accounting",
        "art", "music", "computer_science",
    ]

    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "per_change": "2026-08-13-web-monorepo-consolidation-and-agent-integration-v1",
        "phase_3": "OCR/VLM 4-path ensemble processing manifest",
        "pipeline_stages": [
            "Path 1: Docling-serve to text to BAML function (typed Pydantic row)",
            "Path 2: Docling-serve to Unstract workflow to JSON",
            "Path 3: qwen3-vl-8b page-level image to JSON",
            "Path 4: gemma-4-26B-A4B page-level image to JSON",
            "RAGAS consensus to canonical row to BIEP DuckLake table",
        ],
        "subjects": {},
    }

    for subject in subjects:
        subj_path = root / subject
        subject_data = {
            "subject": subject,
            "ncca_code": f"LC-{subject.upper().replace('_', '-')}-LO",
            "languages": ["en", "ga"],
            "level": ["hl", "ol"],
            "pdfs": [],
            "extraction_status": "pending",
            "ingested_at": None,
            "extracted_at": None,
            "ragas_consensus_score": None,
        }
        if subj_path.exists():
            for pdf_path in sorted(subj_path.rglob("*.pdf")):
                rel_path = pdf_path.relative_to(root)
                size_bytes = pdf_path.stat().st_size
                sha256 = hashlib.sha256()
                with open(pdf_path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha256.update(chunk)
                sha256_hash = sha256.hexdigest()
                subject_data["pdfs"].append(
                    {
                        "path": str(rel_path),
                        "size_bytes": size_bytes,
                        "sha256": sha256_hash,
                        "language": (
                            rel_path.parts[1]
                            if len(rel_path.parts) > 1
                            else "unknown"
                        ),
                    }
                )
        subject_data["pdf_count"] = len(subject_data["pdfs"])
        subject_data["total_size_bytes"] = sum(
            p["size_bytes"] for p in subject_data["pdfs"]
        )
        manifest["subjects"][subject] = subject_data

    manifest["total_subjects"] = len(manifest["subjects"])
    manifest["total_pdfs"] = sum(
        s["pdf_count"] for s in manifest["subjects"].values()
    )
    manifest["total_size_bytes"] = sum(
        s["total_size_bytes"] for s in manifest["subjects"].values()
    )

    out_dir = root / ".ocr_vlm_manifest"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ireland_lc_ingestion_manifest.json"
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Wrote {out_path}")
    print(f"Total subjects: {manifest['total_subjects']}")
    print(f"Total PDFs: {manifest['total_pdfs']}")
    print(f"Total size: {manifest['total_size_bytes'] / (1024 * 1024):.1f} MB")
    for subject, data in manifest["subjects"].items():
        print(f"  {subject:25s}: {data['pdf_count']:3d} PDFs, {data['total_size_bytes'] / 1024:.0f} KB")


if __name__ == "__main__":
    main()
