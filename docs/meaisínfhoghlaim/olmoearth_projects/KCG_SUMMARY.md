# OLMo Earth Projects — KCG Summary

## What It Is
Allen AI's repository of configuration files, model checkpoint references, and documentation for remote sensing models built on the OLMo Earth foundation model. Includes tools and tutorials for fine-tuning OLMo Earth on satellite imagery tasks: forest loss driver classification, mangrove mapping, ecosystem type mapping, land use classification, and live fuel moisture content mapping.

## Why This Matters for Kings' College Galway
Remote sensing and satellite imagery analysis maps to Irish geography and environmental studies in the curriculum. OLMo Earth's fine-tuning patterns for segmentation and classification demonstrate how to adapt large vision models to domain-specific tasks — directly transferable to adapting document vision models for historical Irish manuscript layout analysis. The geospatial data processing pipeline (rslearn + olmoearth_run) provides patterns for handling large-scale educational image datasets, such as digitised Leaving Certificate exam papers spanning decades. Fine-tuning foundation models for specialised domains is the core skill needed for Celtic language model adaptation.

## Key Patterns Preserved
- `README.md` — Project overview: available models, installation, tutorial links
- `docs/awf.md` — Land use / land cover mapping in Southern Kenya
- `docs/ecosystem_type_mapping.md` — Ecosystem type classification model
- `docs/forest_loss_driver.md` — Forest loss driver classification
- `docs/lfmc.md` — Live Fuel Moisture Content mapping
- `docs/mangrove.md` — Mangrove mapping model
- `docs/nandi.md` — Nandi region land cover mapping
- `docs/internal.md` — Allen AI internal infrastructure notes
- `docs/tutorials/FinetuneOlmoEarthSegmentation.md` — Fine-tuning OLMo Earth for segmentation tasks
- `olmoearth_projects/olmoearth_run/README.md` — OLMo Earth runner tooling
- `olmoearth_projects/utils/label_quality/README.md` — Label quality assessment utilities
- `olmoearth_run_data/mozambique_lulc/README.md` — Mozambique land use dataset
- `olmoearth_run_data/sample/README.md` — Sample data configuration
- `olmoearth_run_data/satlas_solar_farm/README.md` — Solar farm detection data

## Source Files
Full source removed (2026-06-06). Available at:
- GitHub: https://github.com/allenai/olmoearth_projects

## What Was Removed
Python source code, YAML/TOML configuration files, Jupyter notebooks, JSON data files, satellite image data (GeoTIFF, etc.), package dependencies (pyproject.toml, uv.lock), Dockerfiles, CI/CD configs, Git metadata.
