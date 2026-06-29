# Per-Stack Documentation

Every stack in `bonneagar/stacks/` has a corresponding .md
doc at this directory. The contract is enforced by
`scripts/stack-doctor.sh` (the CI gate fails if a stack is
missing its doc).

The 4-section template for each doc:

1. **Purpose for the Cianfhoghlaim project** — what this
   stack does for the platform
2. **Why it stays in komodo/pangolin/infisical GitOps** —
   the operational requirement
3. **Cross-references** — to the ops dir, to the code, to
   the IaC entry, to the Pangolin domain
4. **Tags** — the IaC tags

## The 5-group model (88 stacks)

### infrastructure (4 stacks)

- [`backrest`](./backrest.md)
- [`infisical`](./infisical.md)
- [`komodo`](./komodo.md)
- [`pangolin`](./pangolin.md)

### data-engineering (9 stacks)

- [`cognee`](./cognee.md)
- [`dagster`](./dagster.md)
- [`falkordb`](./falkordb.md)
- [`graphiti`](./graphiti.md)
- [`lakehouse`](./lakehouse.md)
- [`langfuse`](./langfuse.md)
- [`litellm`](./litellm.md)
- [`llama-swap`](./llama-swap.md)
- [`marimo`](./marimo.md)

### agent-platform (6 stacks)

- [`agent-os`](./agent-os.md)
- [`lmnr`](./lmnr.md)
- [`memgraph`](./memgraph.md)
- [`mlx-omni`](./mlx-omni.md)
- [`openchamber`](./openchamber.md)
- [`openclaw`](./openclaw.md)

### language-model (4 stacks)

- [`logfire`](./logfire.md)
- [`mlflow`](./mlflow.md)
- [`motherduck`](./motherduck.md)
- [`nimtable`](./nimtable.md)

### ci (1 stacks)

- [`ci/hf-watchdog`](./ci_hf-watchdog.md)

### personal-utility (62 stacks)

- [`Kapowarr`](./Kapowarr.md)
- [`LetterFeed`](./LetterFeed.md)
- [`actual`](./actual.md)
- [`audiobookshelf`](./audiobookshelf.md)
- [`beszel`](./beszel.md)
- [`browser`](./browser.md)
- [`bytebase`](./bytebase.md)
- [`cal-diy`](./cal-diy.md)
- [`changedetection`](./changedetection.md)
- [`coder`](./coder.md)
- [`convex`](./convex.md)
- [`crawl4ai`](./crawl4ai.md)
- [`croilar`](./croilar.md)
- [`docling-serve`](./docling-serve.md)
- [`dots-ocr`](./dots-ocr.md)
- [`dozzle`](./dozzle.md)
- [`dragonfly`](./dragonfly.md)
- [`enclosed`](./enclosed.md)
- [`forgejo`](./forgejo.md)
- [`forgejo-runner`](./forgejo-runner.md)
- [`frontend`](./frontend.md)
- [`garage`](./garage.md)
- [`glance`](./glance.md)
- [`gluetun`](./gluetun.md)
- [`headplane`](./headplane.md)
- [`headscale`](./headscale.md)
- [`it-tools`](./it-tools.md)
- [`karakeep`](./karakeep.md)
- [`lakefs`](./lakefs.md)
- [`lakehouse-oci`](./lakehouse-oci.md)
- [`lakekeeper`](./lakekeeper.md)
- [`lancedb`](./lancedb.md)
- [`linkwarden`](./linkwarden.md)
- [`mailcow-dockerized`](./mailcow-dockerized.md)
- [`meaisinfoghlaim`](./meaisinfoghlaim.md)
- [`n8n`](./n8n.md)
- [`oideachais`](./oideachais.md)
- [`olake`](./olake.md)
- [`olmocr`](./olmocr.md)
- [`paddleocr`](./paddleocr.md)
- [`paperless-ngx`](./paperless-ngx.md)
- [`pastemax`](./pastemax.md)
- [`pinchflat`](./pinchflat.md)
- [`pipecat`](./pipecat.md)
- [`planetscale`](./planetscale.md)
- [`pocket-id`](./pocket-id.md)
- [`pulumi`](./pulumi.md)
- [`pydantic-gateway`](./pydantic-gateway.md)
- [`qdrant`](./qdrant.md)
- [`risingwave`](./risingwave.md)
- [`romm`](./romm.md)
- [`rybbit`](./rybbit.md)
- [`searxng`](./searxng.md)
- [`skyvern`](./skyvern.md)
- [`stirling-pdf`](./stirling-pdf.md)
- [`technitium`](./technitium.md)
- [`tools`](./tools.md)
- [`tuatha`](./tuatha.md)
- [`unstract`](./unstract.md)
- [`vaultwarden`](./vaultwarden.md)
- [`vikunja`](./vikunja.md)
- [`windmill`](./windmill.md)

## Adding a new stack

When you add a new stack to `bonneagar/stacks/<name>/`, you
MUST also create the corresponding doc at
`cianfhoghlaim/docs/stacks/<name>.md` using the 4-section
template. The CI gate will fail your PR if the doc is
missing.
