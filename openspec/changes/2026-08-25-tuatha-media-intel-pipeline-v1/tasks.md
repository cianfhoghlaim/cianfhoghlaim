# Tasks: tuatha-media-intel-pipeline (v1)

## 1. BAML schema

- [ ] 1.1. Add `baml_src/tuatha_media_intel.baml` with 3 typed classes
      + 1 join class + 5 functions (see `tuatha_media_intel.baml`).
- [ ] 1.2. Run `baml-cli generate` to produce `baml_client/` (Python + TS).
- [ ] 1.3. Run `baml-cli test baml_src/tuatha_media_intel.baml` — verify
      the 3 test cases pass (`hades_athena_divine_strike`,
      `comic_absolute_superman_dust`, `gba_golden_sun_jupiter`).

## 2. CocoIndex v1 Apps

- [ ] 2.1. Add `cocoindex_flows/tuatha_media_intel/_shared/__init__.py`
      with the shared `LANCE_DB` + `EMBEDDER` + `S3_LANCE_URI`
      ContextKeys.
- [ ] 2.2. Add `cocoindex_flows/tuatha_media_intel/ingestors/hades_boons.py`
      with the `hades_boons_app` CocoIndex App.
- [ ] 2.3. Add `cocoindex_flows/tuatha_media_intel/ingestors/comic_particles.py`
      with the `comic_particles_app` CocoIndex App.
- [ ] 2.4. Add `cocoindex_flows/tuatha_media_intel/ingestors/gba_magic.py`
      with the `gba_magic_app` CocoIndex App.
- [ ] 2.5. Add `cocoindex_flows/tuatha_media_intel/ingestors/anam_particles.py`
      with the `anam_particles_app` (cross-source join).
- [ ] 2.6. Run `mise run upstream:conformance` and verify all 4 Apps pass
      the R1–R4 contract.

## 3. Swift capture daemon

- [ ] 3.1. Add `tuatha_media_intel/capture/tuatha-capture/Package.swift`
      (Swift Package Manager, macOS 15+).
- [ ] 3.2. Add `Sources/tuatha-capture/main.swift` — CLI entry point
      (doctor / daemon / list-windows / version).
- [ ] 3.3. Add `Sources/tuatha-capture/Doctor.swift` — permissions +
      HEVC encoder + sample frame check.
- [ ] 3.4. Add `Sources/tuatha-capture/Capture.swift` — SCStream
      per-window content filter + AVAssetWriter HEVC pipeline.
- [ ] 3.5. Add `Sources/tuatha-capture/Daemon.swift` — JSON-RPC server
      over AF_UNIX.
- [ ] 3.6. Add `tuatha_media_intel/capture/LaunchAgent/com.ci.tuatha.capture.plist`.
- [ ] 3.7. Verify `swift build -c release` succeeds.
- [ ] 3.8. Verify `tuatha-capture doctor` passes on M-series macOS 15+.

## 4. Python capture shims

- [ ] 4.1. Add `tuatha_media_intel/capture/python/pyproject.toml`.
- [ ] 4.2. Add `tuatha_capture/cli.py` (cyclopts subcommands: doctor /
      gba / comic).
- [ ] 4.3. Add `tuatha_capture/gba/__init__.py` (mgba-py + CLI fallback).
- [ ] 4.4. Add `tuatha_capture/comic/__init__.py` (CBZ panel extractor +
      k-means palette).
- [ ] 4.5. `uv run tuatha-capture-python doctor` passes on macOS.

## 5. Dagster assets

- [ ] 5.1. Add `orchestration/defs/2_materials/tuatha_media_intel.py`
      with 7 assets + 1 RAGAS asset_check.
- [ ] 5.2. Register the asset module in `orchestration/defs/__init__.py`.
- [ ] 5.3. Verify `dagster dev` loads the assets with no errors.

## 6. Docker Compose stack

- [ ] 6.1. Add `bonneagar/stacks/tuatha-media-intel/compose.yaml`
      (cocoindex-runner + baml-codegen + ragas-evaluator + mlflow-sidecar).
- [ ] 6.2. Add `sidecar.yaml` (Locket sidecar; Infisical refs only).
- [ ] 6.3. Add `secrets.env` (Infisical URIs only).
- [ ] 6.4. Add `pangolin.yaml` (6-label pattern + raw bucket).
- [ ] 6.5. Add `blueprint.yaml` (Komodo rollout).
- [ ] 6.6. Add `.env.example`.
- [ ] 6.7. `mise run cic:stack-doctor` passes for `tuatha-media-intel`.

## 7. Marimo dashboard

- [ ] 7.1. Add `notebooks/tuatha_anam_dashboard.py` (4-tab shell).
- [ ] 7.2. Add `notebooks/tuatha_anam/tabs/{sources,boons,particles,join}.py`.
- [ ] 7.3. Add `notebooks/tuatha_anam/helpers/__init__.py` (Lance
      federated query + ΔE + LAB helpers).
- [ ] 7.4. Verify `marimo edit notebooks/tuatha_anam_dashboard.py`
      opens and renders without errors.

## 8. Hermes Phase 2 stub

- [ ] 8.1. Add `agents/meaisinfhoghlaim/tuatha_capture_agent.py` with
      the 3 tool functions + the ADK `LlmAgent`.
- [ ] 8.2. Register `tuatha_capture_agent` in
      `agents/agent_registry.py:AGENT_REGISTRY`.
- [ ] 8.3. Verify `TUATHA_HERMES_ENABLED=false` (Phase 1 default) keeps
      the agent from invoking the screen.

## 9. DLT source manifests

- [ ] 9.1. Add `dlt_sources/tuatha_media_intel/hades/source.yaml`.
- [ ] 9.2. Add `dlt_sources/tuatha_media_intel/comic/source.yaml`.
- [ ] 9.3. Add `dlt_sources/tuatha_media_intel/gba/source.yaml`.
- [ ] 9.4. Verify every manifest carries `shippable: false` + `legal_notes`.

## 10. End-to-end smoke test

- [ ] 10.1. Start the Swift capture daemon.
- [ ] 10.2. Open Hades → let it capture 60 keyframes.
- [ ] 10.3. Verify `~/Library/Application Support/tuatha/captures/<run_id>/manifest.jsonl` exists.
- [ ] 10.4. Run `mise run cocoindex:update tuatha_hades_boons`.
- [ ] 10.5. Open `notebooks/tuatha_anam_dashboard.py` — verify the
        Boons tab shows the captured rows.
- [ ] 10.6. Verify the Langfuse trace shows the BAML extract span with
        a non-zero token cost.
- [ ] 10.7. Verify `dagster asset materialize anam_particles_v1` runs
        and the RAGAS check passes (threshold ≥ 0.85).
