# GeoAI — KCG Summary

## What It Is
GeoAI is a Python package integrating AI with geospatial data analysis: satellite imagery classification, object detection, semantic segmentation (buildings, water bodies, solar panels), change detection, and interactive map visualization. Built on PyTorch, Transformers, and segmentation_models.pytorch, with QGIS plugin support and integration with Leafmap/MapLibre for interactive mapping. Includes 28 documentation pages and research on geospatial linguistics and Ibis integration.

## Why This Matters for Kings' College Galway
GeoAI's segmentation and classification patterns are directly applicable to Irish geography curriculum data — automated land cover analysis for Leaving Cert geography projects, historical map change detection for Celtic studies, and interactive map visualization for student-facing dashboards. The Ibis integration notes show how to bridge geospatial data with the oideachais Ibis analytics layer. The lightweight training patterns (fine-tuning on consumer hardware) align with the bunchloch MacBook M4 development environment.

## Key Patterns Preserved
34 .md files remain:
- `README.md` — Full GeoAI package overview with features, installation, and architecture
- `docs/*.md` (24 files) — Complete documentation: installation, segmentation, classification, change detection, model training (PyTorch, Detectron2, DINOv3, SAM, Moondream), map tools/widgets, QGIS plugin, GeoAgents, contributing, changelog
- `paper/paper.md` — JOSS paper on GeoAI
- `geospatial_book.md` — Geospatial data science reference
- `Geospatial Data Visualization with Ibis.md` — Ibis + geospatial integration
- `Geospatial Workflow & Particle Effects.md` — Advanced visualization patterns
- `geospatial-linguistics.md` — Linguistic geospatial analysis
- `qgis_plugin/README.md` — QGIS plugin overview
- `.github/ISSUE_TEMPLATE/` — Bug and feature request templates

## Source Files
Full source removed (2026-06-06). Available at https://github.com/opengeos/geoai

## What Was Removed
Python source (.py), Jupyter notebooks (.ipynb), YAML/TOML/JSON configs, SVG/PNG images, shell scripts, .gitignore, lock files, conda recipe, Docker files, QGIS plugin .xml
