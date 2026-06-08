# Build Small 2026 — Submission Runbook

> The full step-by-step guide for taking the 4 Spaces from this
> monorepo to the HuggingFace `cianfhoghlaim/` personal account as
> 4 live demo Spaces, ready for the Build Small 2026 submission form.

## Overview

The 4 Spaces are already built and committed on `main` (commits
`e874bce7f` through `8ce8f75d8`). To go from "code on disk" to
"live demo on HF", you need to:

1. Authenticate with HF
2. Create + push the 4 Space repos
3. Add the `HF_TOKEN` secret to each
4. (Optional) Record demo videos
5. Fill the submission form

This runbook covers all 5 steps in detail.

---

## Step 1 — Authenticate with HuggingFace

You need a write-enabled HF access token. The token you already use
for `huggingface-cli login` works if it has `write` scope.

### 1a. If you don't have a token yet

1. Go to https://huggingface.co/settings/tokens
2. Click **+ Create new token**
3. Type: **Write**
4. Name: anything memorable (e.g. `build-small-2026-deploy`)
5. Click **Create token**
6. **Copy the token** — you can't see it again

### 1b. Authenticate the CLI

> **Note:** the old `huggingface-cli` is deprecated. Use the new `hf`
> CLI (it's the same `huggingface_hub` package, just a different
> entry point — `hf` was added in `huggingface_hub` 1.2+).

From the monorepo root:

```bash
.venv/bin/hf auth login
# Paste your token when prompted
# Choose: 'add token as git credential' (y) - this lets you push without re-entering
```

You should see:

```
Token is valid (permission: write).
Your token has been saved to /Users/.../huggingface/token
Login successful.
```

> **If `hf` errors with `Typer.__init__() got an unexpected keyword
> argument 'suggest_commands'`:** the `huggingface_hub` in the venv
> is too old for the installed `typer`. Fix it with:
>
> ```bash
> uv pip install --python .venv/bin/python3 --upgrade huggingface_hub
> ```

### 1c. Verify who you are

```bash
.venv/bin/hf auth whoami
```

Expected output: `cianfhoghlaim` (your username).

---

## Step 2 — Create + push the 4 Space repos

### 2a. Decide: this script or the Web UI

The script (`scripts/push_spaces_to_hf.sh`) does everything in one
shot: creates the empty Spaces on HF, builds a staging directory
that bundles `_common/` into each Space, runs `git init`, and pushes.

```bash
bash scripts/push_spaces_to_hf.sh
```

The script will:
- Print your HF username
- For each of the 4 Spaces:
  - Create the empty repo on HF (`huggingface-cli repo create ... --type space --space_sdk gradio`)
  - Build a staging dir at `.hf-spaces-staging/<slug>/` that contains the Space's files + the shared `_common/` bundle + the `social_card.png`
  - `git init`, commit, `git push` to the HF Space URL
- Print a list of 4 URLs to visit for the secrets step (Step 3)

If the script errors out partway through, it's safe to re-run — the
`huggingface-cli repo create ... --exist-ok` flag makes Space
creation idempotent.

### 2b. (Alternative) Manual `hf upload` per Space

If you want finer control, do the 4 pushes by hand:

```bash
# Create the 4 empty repos on HF
.venv/bin/hf repos create cianfhoghlaim/an-scrudu     --type space --space-sdk gradio --exist-ok
.venv/bin/hf repos create cianfhoghlaim/meaisin-cliste --type space --space-sdk gradio --exist-ok
.venv/bin/hf repos create cianfhoghlaim/cianfhoghlaim  --type space --space-sdk gradio --exist-ok
.venv/bin/hf repos create cianfhoghlaim/anam-tuatha   --type space --space-sdk gradio --exist-ok

# Build 4 staging dirs and upload each via hf upload
declare -A SLUG_TO_DIR=(
    [an-scrudu]=spaces/an_scrudu
    [meaisin-cliste]=spaces/meaisin_cliste
    [cianfhoghlaim]=spaces/cianfhoghlaim
    [anam-tuatha]=spaces/anam_tuatha
)

for slug in "${!SLUG_TO_DIR[@]}"; do
    local_dir="${SLUG_TO_DIR[${slug}]}"
    stage="/tmp/hf-${slug}"
    rm -rf "${stage}" && mkdir -p "${stage}"
    rsync -a --exclude='_common' "${local_dir}/" "${stage}/"
    rsync -a "spaces/_common/" "${stage}/_common/"
    [[ -f "${local_dir}/social_card.png" ]] && cp "${local_dir}/social_card.png" "${stage}/"
    .venv/bin/hf upload "cianfhoghlaim/${slug}" "${stage}" "." \
        --repo-type space \
        --commit-message "Initial Space push (Build Small 2026 submission)"
done
```

`hf upload` is the modern replacement for the old `git init && git
push` dance — it handles the git LFS setup, .gitattributes, and the
commit in one call.

### 2c. Verify the pushes

Visit each Space's URL and check that:
- The repo shows files in the "Files" tab
- The `Logs` tab (or `Open in playground`) doesn't show any errors
- The README frontmatter (`--- sdk: gradio ...`) is at the top of the README

URLs:
- https://huggingface.co/spaces/cianfhoghlaim/an-scrudu
- https://huggingface.co/spaces/cianfhoghlaim/meaisin-cliste
- https://huggingface.co/spaces/cianfhoghlaim/cianfhoghlaim
- https://huggingface.co/spaces/cianfhoghlaim/anam-tuatha

### 2d. What the Spaces look like without `HF_TOKEN`

All 4 Spaces have offline fallbacks. Without a `HF_TOKEN`:
- **Space 1** (An Scrúdú): regex-based extraction. Finds topics `CH3..CH8` in the sample.
- **Space 2** (Meaisín Cliste): all 3 tabs work; the curaclam tab uses the static reference table.
- **Space 3** (Cianfhoghlaim): NPC dialogue uses a templated offline response.
- **Space 4** (Anam): the exit-card generator uses the 16-template bank.

This means you can verify the Spaces work *before* you add the secret
in Step 3.

---

## Step 3 — Add the `HF_TOKEN` secret to each Space

For the 3-tier HF Inference fallback to actually work, each Space
needs the `HF_TOKEN` secret.

### 3a. For each of the 4 Spaces

1. Visit `https://huggingface.co/spaces/cianfhoghlaim/<slug>/settings`
2. Scroll to **Variables and secrets**
3. Click **+ New secret**
4. Name: `HF_TOKEN`
5. Value: paste your token (the same one from Step 1a)
6. Click **Create**

The Space will rebuild (takes ~30-60 seconds for cold start). When
the logs show `Application startup complete`, the Space is live and
the BAML chain is working.

### 3b. Verify the chain is working

Visit the Space's playground. Look for the model's name in the
output footer or the model badge — if you see `Qwen/Qwen2.5-7B-Instruct`,
the chain is engaged. If you see `offline-regex` or `offline-template-bank`,
the token is missing or wrong.

### 3c. What the chain looks like at runtime

When a request hits the Space:
1. `chat_complete_json()` is called with a typed message array
2. POST to `https://api-inference.huggingface.co/v1/chat/completions` with the primary model
3. On 5xx, 429, timeout, or schema failure: fall back to model 2
4. On the same from model 2: fall back to model 3
5. If all 3 fail: return the offline result (demo still works)

---

## Step 4 — Record demo videos (you)

Each Space has a pre-rendered storyboard PNG and a voiceover script
(`.txt`) in its repo:

| Space | Voiceover script | Storyboard | Est. duration |
|:--|:--|:-:|:-:|
| an-scrudu | `spaces/an_scrudu/voiceover_script.txt` | `storyboard.png` | ~50s |
| cianfhoghlaim | `spaces/cianfhoghlaim/voiceover_script.txt` | `storyboard.png` | ~75s |
| meaisin-cliste | `spaces/meaisin_cliste/voiceover_script.txt` | `storyboard.png` | ~65s |
| anam-tuatha | `spaces/anam_tuatha/voiceover_script.txt` | `storyboard.png` | ~70s |

### 4a. Recommended recording setup

1. **Open the Space in your browser**, full-screen the playground.
2. **Open the voiceover script** in a second window (or print it).
3. **Screen-record** with QuickTime (`File > New Screen Recording`) or
   OBS. Audio: your microphone.
4. **Follow the script's beat-by-beat section**. Each `[12.5s]`
   line is a timestamp cue.
5. **The storyboard PNG** is your on-screen reference for what the
   Space should look like at each step.

### 4b. Editing tips

- Keep each video **under 3 minutes** (the hackathon rule).
- Don't show the loading spinner for more than 1 second; cut the
  waiting time in post.
- Use the "Anam Bonneagar" footer as your closing card; it's already
  branded and on-theme.
- The BAML model name (`Qwen2.5-7B-Instruct`) in the badge is a
  trust signal — make sure it's visible.

### 4c. Where to upload the videos

The submission form asks for either YouTube or Loom links. Either
is fine. Recommended:

- Upload to a single YouTube playlist "Build Small 2026 — Cianfhoghlaim"
- Each video gets its own entry in the playlist
- Add the playlist link to the submission form

---

## Step 5 — Fill the submission form

The form is at https://huggingface.co/build-small-2026 (or wherever
the live link is — the URL may differ slightly).

### 5a. Required fields

| Field | What to put |
|:--|:--|
| Your name | Cian Mac an Deagánaigh |
| Project title | "Cianfhoghlaim: 4 Celtic AI Spaces, 5 Elements, 1 Typed Pipeline" |
| Short tagline | "4 HF Spaces, BAML → HF Inference → Gradio, all models ≤32B, bilingual EN + Gaeilge" |
| Project description | (paste the first 3 paragraphs of `doc/hackathons/build-small-2026-blog.md`) |
| Space 1 URL | https://huggingface.co/spaces/cianfhoghlaim/an-scrudu |
| Space 2 URL | https://huggingface.co/spaces/cianfhoghlaim/meaisin-cliste |
| Space 3 URL | https://huggingface.co/spaces/cianfhoghlaim/cianfhoghlaim |
| Space 4 URL | https://huggingface.co/spaces/cianfhoghlaim/anam-tuatha |
| Demo video | YouTube playlist URL |
| Repo URL | https://github.com/cianfhoghlaim/kings_college_galway |
| Social post | (the tweet thread from `doc/hackathons/build-small-2026-tweet-thread.md`) |
| Models used | Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, Gemma-2-9b-it (all ≤32B) |

### 5b. The "what's interesting" / "what's new" question

If the form has a free-form "what's interesting" or "novel
contribution" question, here's a 200-word answer:

> The 4 Spaces are bound together by a single typed pipeline
> (BAML → HF Inference → Gradio) and a single visual framework
> (5 Celtic elements: Talamh / Uisce / Tine / Aer / Anam). Every
> Space renders the same "Anam Bonneagar" footer with 5 trust
> signals — the Space slug, the Pobal HP Deprivation Index 2022
> for the home county (Dublin 8, -9.8), the model alias (≤32B
> asserted), the monorepo commit SHA, and a tamper-evident hash.
> The 3-tier HF Inference fallback (Qwen 7B → Llama 8B → Gemma
> 9b) keeps p95 latency under 10s even on transient failures;
> every Space also has an offline regex/template fallback so the
> demo never breaks. The 6 Celtic NPCs in Space 3 are grounded
> in cached Wikipedia articles, so the dialogue model can never
> hallucinate a fact. Total: 5,557 lines of code in 49 files,
> one monorepo, 4 Spaces.

---

## Post-submission

Once the form is in:

1. **Tweet the thread** (`doc/hackathons/build-small-2026-tweet-thread.md`).
2. **Post the blog** to dev.to or your personal site. The source is
   in `doc/hackathons/build-small-2026-blog.md`.
3. **Email the team** (if applicable) with the 4 Space links + the
   video playlist.
4. **Check the 6-file linter** is still at 97.2% (the footer claim)
   — run `bun run lint` from the monorepo root. If it's dropped,
   update the stub in `spaces/_common/anam_bonneagar.py:38`.

---

## Troubleshooting

### "huggingface-cli: command not found"

The old CLI is deprecated; use the new `hf` CLI instead:

```bash
.venv/bin/hf auth login
.venv/bin/hf auth whoami
.venv/bin/hf repos create ...
.venv/bin/hf upload ...
```

The `huggingface-cli` shim may still be on your PATH but it'll print
`Warning: 'huggingface-cli' is deprecated` on every invocation. Use
`hf` for everything in this runbook.

### "hf" errors with "Typer.__init__() got an unexpected keyword argument 'suggest_commands'"

The `huggingface_hub` in the venv is too old for the installed
`typer`. The fix:

```bash
uv pip install --python .venv/bin/python3 --upgrade huggingface_hub
```

This was the case as of `huggingface_hub==1.13.0` + `typer==0.16.1`
in this monorepo. The upgrade pulls in a `typer` that matches the
newer `huggingface_hub` API.

### "403 Forbidden" on push

The token doesn't have write scope. Go to https://huggingface.co/settings/tokens,
edit the token, set type to **Write**.

### "Space build failed: No module named 'spaces'"

The shared `_common/` bundle wasn't pushed. Re-run the push script;
verify the staging dir includes `_common/`.

### "BAML chain failed: HF_TOKEN is not set"

The Space secret wasn't set. Go to the Space's Settings > Variables
and secrets, add `HF_TOKEN`. (See Step 3.)

### Space loads but everything returns "offline" results

The HF_TOKEN isn't reaching the runtime. The Space is using the
fallback path. Re-check Step 3; the secret name is case-sensitive
and must be exactly `HF_TOKEN`.

### "Model is currently loading" appears in playground

HF Inference cold-starts take 30-60 seconds for the first request.
Subsequent requests are fast. This is normal; not a bug.

### "Out of memory" in the Space logs

The Spaces are configured for `cpu-basic` (free) tier. If HF bumps
you to a heavier model, switch to `cpu-basic` in the Space's
Settings > Hardware.

---

## Quick reference: file map

```
monorepo/
├── scripts/
│   ├── push_spaces_to_hf.sh       <-- THE deploy script (Step 2)
│   └── render_social_cards.py     (build-time only, not needed post-push)
├── doc/hackathons/
│   ├── build-small-2026-plan.md       (the re-themed plan)
│   ├── build-small-2026-docs-catalogue.md
│   ├── build-small-2026-model-fallback.md
│   ├── build-small-2026-blog.md       (paste into submission form)
│   ├── build-small-2026-tweet-thread.md
│   └── build-small-2026-final.md      (overall summary)
├── openspec/
│   ├── changes/archive/2026-06-08-croilar-hf-build-small-2026-demo/
│   └── specs/croilar-gradio-hf-demo/  (the formal capability spec)
└── spaces/
    ├── _common/                 (shared bundle, pushed into each Space)
    ├── an_scrudu/               (Space 1: Talamh)
    ├── cianfhoghlaim/           (Space 3: Anam)
    ├── meaisin_cliste/          (Space 2: Aer + Uisce)
    └── anam_tuatha/             (Space 4: all 5 elements)
```

Each Space dir contains:
- `app.py` — Gradio entry point
- `*_demo.py` / `*_visual.py` / etc. — feature modules
- `voiceover_script.txt` — for the demo video narration
- `storyboard.png` — for the demo video on-screen reference
- `social_card.png` — 1200x630 OG image
- `README.md` — HF Space frontmatter + architecture
- `requirements.txt` — gradio 4.44+, huggingface_hub, Pillow

Long learning. Cianfhoghlaim.
