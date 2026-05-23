#!/bin/bash
set -e

echo "=== 1. Resetting Git History ==="
git reset --mixed origin/main

echo "=== 2. Updating .gitignore ==="
cat << 'IGNORE' >> .gitignore

# =============================================================================
# GITHUB FILE SIZE LIMIT EXCLUSIONS (>100MB)
# =============================================================================
# The following specific files are excluded because they exceed GitHub's 100MB 
# strict file size limit. We preserve the parent directories for dlt ingestion 
# and orchestration, but these massive CSV/JSON/pack files must remain local or 
# be synced via MotherDuck/Cloudflare R2 to prevent 'git push' timeouts.
stedding/site_scrape_samples/curriculumonline/www.curriculumonline.ie_getmedia_175e5aeb-a604-42c5-83eb-847ce8da7a2e_STUDENT_04_High_res.pdf.json
oideachais/data_platform/datasets/uk/ucas/eoc_provider_2023/*main scheme applications acceptances.csv
oideachais/data_platform/datasets/uk/ucas/eoc_2023/*acceptance route.csv
oideachais/data_platform/datasets/uk/dfe/key-stage-4-performance_2023-24/data/202324_subject_school_all_exam_entriesgrades_final.csv
oideachais/data_platform/datasets/uk/dfe/a-level-and-other-16-to-18-results_2023-24/data/all_inst_data.csv
hackathons/gsoc/beagle/docs.beagleboard.io/.git_disabled/objects/pack/*.pack
IGNORE

git add .gitignore
git commit -m "chore(git): ignore specific >100MB files to comply with GitHub limits. Chunking strategy: isolate git rules to unblock all subsequent pushes."
git push origin main

echo "=== 3. Pushing Application Restructure ==="
git add oideachais/web_app oideachais/data_platform university_of_galway/mata
git commit -m "feat(oideachais): restructure data_platform, web_app, and mata datasets. Chunking strategy: group core architecture and dataset skeleton changes."
git push origin main

echo "=== 4. Pushing Infrastructure & Secrets ==="
git add opencode.json oideachais/compose.yaml oideachais/sidecar.yaml infrastructure/infisical/scripts/init-vault.ts
git commit -m "chore(infra): harden secrets management with Locket/Infisical. Chunking strategy: isolate security, env var, and docker orchestration updates."
git push origin main

echo "=== 5. Pushing Documentation Updates ==="
git add README.md oideachais/README.md
git commit -m "docs: streamline root readme and enhance deployment instructions. Chunking strategy: align documentation strictly with the newly pushed architecture."
git push origin main

echo "=== 6. Pushing Remaining Files ==="
git add .
git commit -m "chore: integrate remaining dlt/dagster assets and configurations. Chunking strategy: final sweep of safe, <100MB files to finalize repository state."
git push origin main

echo "=== DONE ==="
