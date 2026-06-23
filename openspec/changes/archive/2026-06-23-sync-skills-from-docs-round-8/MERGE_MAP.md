# Round 8 — docs/tuatha + docs/teanga → skills merge map

This file maps every `.md` (and 2 PDFs) under `docs/tuatha/` (excluding `08-mirrors/_summaries/` which are listed separately) and `docs/teanga/` to either the **4 new skills** (celtic-asset-generation, tuatha-mmo, irish-llm-on-device, upstream-mirrors) or one of the **existing skills** that need expansion, or marks it for deletion or as a clipping. The two PDFs (Bolmo / Molmo2 VLM tech reports) move to `celtic-asset-generation/references/papers/`. Near-duplicate pairs and the chosen canonical are listed at the end. The 12 files in `docs/tuatha/07-clippings/` and 9 teanga clipping-style files (those with `tags: clippings` front-matter) are all external articles → `references/clippings/`.

**Conventions used below**
- `KEEP-NEW: <new_skill>` — long-form reference inside a new skill, body source, or upstream-mirrors summary.
- `EXPAND: <existing_skill> [§section]` — content should be merged into an existing skill (often round-6/7 skills).
- `DELETE` — redundant with an existing skill, a link-list / research note with no KCG-specific content, or an external resource that already lives in its own skill (e.g. babylonjs, copilotkit).
- `CLIPPING: <new_skill>/references/clippings/<slug>.md` — an external article preserved verbatim in the clippings dir of the appropriate new skill.
- `2 PDFs`: 1765814974-bolmo.pdf (2.0 MB) and 1766008501-molmo2-tech-report.pdf (38.7 MB) → `celtic-asset-generation/references/papers/`.

## Per-file table (sorted by src path)

| src | topic (5 words max) | lines | dest | reason |
|---|---|---:|---|---|
| docs/teanga/1765814974-bolmo.pdf | Bolmo VLM tech report (2.0 MB) | – | KEEP-NEW: celtic-asset-generation/references/papers/bolmo.pdf | vision-language model paper, paired with molmo2 |
| docs/teanga/1766008501-molmo2-tech-report.pdf | Molmo2 VLM tech report (38.7 MB) | – | KEEP-NEW: celtic-asset-generation/references/papers/molmo2-tech-report.pdf | vision-language model paper, large |
| docs/teanga/AI Agents for Irish Language Resources.md | neuro-symbolic Gaeilge extraction | 435 | KEEP-NEW: celtic-asset-generation/references/neuro-symbolic-gaeilge-engine.md | Agno+GLM-4.6v+Cognee+BAML Irish HTR/KG blueprint |
| docs/teanga/AI Chemistry Education Image Generation.md | BAML+Fibo chem asset pipeline | 415 | KEEP-NEW: celtic-asset-generation/references/baml-fibo-chemistry.md | BAML chem syllabus → Fibo structured JSON prompts |
| docs/teanga/Agentic Translation Workflow Technologies.md | T5Gemma-2+ADK Irish translation | 279 | EXPAND: celtic-language-ai §Translation stack | agentic translation + English-pivoted CoT, complements celtic-language-ai translation section |
| docs/teanga/Agentic Web Scraping Pipeline.md | Agno+Browserbase+Z.AI scraping | 572 | EXPAND: kcg-leabharlann-pipeline §Ingestion layer | same neuro-symbolic Browserbase+BAML+Cognee flow, fuller source (merge with tuatha copy) |
| docs/teanga/Aligning Gaelic Script for QwenVL Finetuning.md | ColPali Gaelic manuscript alignment | 329 | KEEP-NEW: irish-llm-on-device/references/colpali-qwenvl-gaelic-alignment.md | weakly-supervised bounding-box via ColPali for Qwen2-VL fine-tuning |
| docs/teanga/Auto-Optimize Pydantic Models for Structured Information Extraction_ A Complete Guide to DSPydantic.md | DSPydantic Pydantic auto-optimise | 433 | DELETE | external HF blog; equivalent to baml skill content, redundant |
| docs/teanga/BAML Schemas for Irish Education.md | BAML+Graphiti NCCA education KG | 559 | KEEP-NEW: celtic-asset-generation/references/baml-irish-education-kg.md | BAML for NCCA / SEC / Dept-of-Ed tripartite knowledge graph |
| docs/teanga/BAML for Syllabus-Driven Data Extraction.md | BAML+Agno+Restate adaptive schemas | 416 | KEEP-NEW: celtic-asset-generation/references/baml-adaptive-syllabus.md | dynamic BAML TypeBuilder per-syllabus, Agno+Restate workflow |
| docs/teanga/BAML, DLT, and AI Workflow Integration.md | BAML+dlt+TanStack unified schema | 504 | EXPAND: baml §Polyglot code-gen | BAML as IDL across Python+TS, fits existing baml skill |
| docs/teanga/BritLLM.md | BritLLM project overview | 130 | EXPAND: celtic-language-ai §Celtic LLMs (BritLLM) | clipping about britllm/britllm-3b-v0.1 model |
| docs/teanga/British Isles Celtic Language Education Data.md | Celtic ed census fiscal 2024-25 | 305 | EXPAND: cross-domain-registry §8 nations | demographics + fiscal context, not a pattern |
| docs/teanga/British Isles Education Map.md | British Isles census 2021+TanStack | 483 | KEEP-NEW: celtic-asset-generation/references/british-isles-demographic-atlas.md | DuckDB+Convex+TanStack Hilbert-curved demographic viz (tuatha copy is redundant) |
| docs/teanga/Celtic Data Scraping and Integration Plan.md | Skyvern Celtic archive scrape | 415 | KEEP-NEW: celtic-asset-generation/references/skyvern-celtic-scrape.md | Skyvern+LLM agent for ncca/examinations/duchas scraping |
| docs/teanga/Celtic Language Data Aggregation & Analysis.md | Federated Linguistic Data Lakehouse | 343 | KEEP-NEW: celtic-asset-generation/references/federated-linguistic-data-lakehouse.md | non-Ireland Celtic corpora architecture, fuller source (merge with tuatha copy) |
| docs/teanga/Celtic Language Educational Data Scrape.md | Celtic-Bench education corpora | 335 | KEEP-NEW: celtic-asset-generation/references/celtic-bench-educational-corpora.md | pan-Celtic bilingual corpus via ncca/examinations/SQA |
| docs/teanga/Celtic Language OCR Resource Analysis.md | Qwen-VL+CLARIN-UK Celtic OCR | 334 | KEEP-NEW: irish-llm-on-device/references/qwen-vl-celtic-ocr.md | Qwen2-VL/Qwen3-VL fine-tuning on Celtic HTR (merge with tuatha copy) |
| docs/teanga/Chemistry Education Asset Generation.md | React+HF chem asset pipeline | 292 | KEEP-NEW: celtic-asset-generation/references/react-chemistry-assets.md | React three-fiber chemistry/asset pipeline for Irish LC |
| docs/teanga/Digital Resources for the Languages in Ireland and Britain.md | DR-LIB CLARIN-UK resources list | 199 | CLIPPING: celtic-asset-generation/references/clippings/dr-lib-resources.md | external CLARIN article, clipping |
| docs/teanga/Educational Game Dev Pipeline.md | DIAGE physics/chem engine | 457 | KEEP-NEW: tuatha-mmo/references/diage-educational-game-pipeline.md | DIAGE game-engine+Manim science viz (canonical, longer than tuatha copy) |
| docs/teanga/Enhancing English-Irish Translation with Diffusion Models.md | diffusion NMT Irish translation | 354 | KEEP-NEW: celtic-asset-generation/references/diffusion-irish-translation.md | NeoDiff+Block Diffusion for low-resource Irish |
| docs/teanga/Explore data with marimo _ dlt Docs.md | dlt+marimo+ibis notebook | 100 | CLIPPING: celtic-asset-generation/references/clippings/dlt-marimo-ibis.md | external dlt docs clipping, redundant with marimo skill |
| docs/teanga/Fine-tuning VLMs for iOS HTR.md | bilingual Irish HTR iOS MLX | 245 | KEEP-NEW: irish-llm-on-device/references/ios-bilingual-htr.md | ColPali+Qwen2-VL+MLX on-device HTR (merge with tuatha copy) |
| docs/teanga/Finetuning Qwen3-VL for Gaelic OCR.md | Qwen3-VL+Unsloth Gaelic OCR | 360 | KEEP-NEW: irish-llm-on-device/references/qwen3-vl-gaelic-finetuning.md | NaViT+MLflow+Ragas Qwen3-VL Gaelic fine-tuning |
| docs/teanga/Gaelic in the Digital Age_ Inside the ÈIST Project – Gaelic Algorithmic Research Group.md | ÈIST Gaelic Algorithmic Research | 78 | DELETE | short research note on ÈIST; covered by celtic-language-ai §ASR |
| docs/teanga/Game Dev Pipeline Research & Plan.md | Hades+BitCraft game pipeline | 328 | EXPAND: tuatha-platform §Dagster assets | Supergiant+SpacetimeDB game pipeline; redundant with tuatha copy |
| docs/teanga/Game Development Research & AI Integration.md | Anam MMO agentic engine | 221 | KEEP-NEW: tuatha-mmo/references/anam-mmo-engine-selection.md | agentic+CopilotKit+x402+KMP MMO architecture |
| docs/teanga/Geospatial Data Analysis and DuckDB.md | Hidden Heritages+Canúint+DuckDB | 376 | KEEP-NEW: celtic-asset-generation/references/hidden-heritages-duckdb.md | DCU Gaois spatial stack + DuckDB analytics |
| docs/teanga/Geospatial Data Visualization with Ibis.md | Ibis+DuckDB+GeoParquet education | 317 | KEEP-NEW: celtic-asset-generation/references/ibis-duckdb-education-geo.md | cloud-native geospatial EdTech stack |
| docs/teanga/Google ADK with LiteLLM _ liteLLM.md | Google ADK+LiteLLM tutorial | 317 | CLIPPING: celtic-asset-generation/references/clippings/google-adk-litellm.md | external LiteLLM docs clipping, covered by litellm+google-adk skills |
| docs/teanga/Graph Tech Integration and Recommendation.md | Cognee+CocoIndex+Graphiti+KGs | 439 | KEEP-NEW: celtic-asset-generation/references/cognee-cocoindex-graphiti-stack.md | FalkorDB vs Memgraph dual-engine architecture |
| docs/teanga/Handwriting Recognition and Dataset Creation.md | Dúchas scrape+Qwen-VL math HTR | 205 | KEEP-NEW: irish-llm-on-device/references/duchas-qwen-vl-htr.md | Dúchas+ColPali+Docling+DeepSeek-Math heritage HTR |
| docs/teanga/INDEX.md | teanga library index | 40 | DELETE | index, content moves to celtic-asset-generation SKILL |
| docs/teanga/Iceberg in the Browser.md | DuckDB Iceberg in browser | 98 | CLIPPING: celtic-asset-generation/references/clippings/iceberg-browser-duckdb.md | external duckdb.org blog; covered by motherduck+olake skills |
| docs/teanga/Integrating Olake, Lakekeeper, RisingWave.md | OLake+Lakekeeper+RisingWave lakehouse | 444 | KEEP-NEW: celtic-asset-generation/references/olake-lakekeeper-risingwave.md | second-gen open data lakehouse (canonical source for this stack) |
| docs/teanga/Integrating Rust, DuckDB, TanStack, CopilotKit.md | SpacetimeDB+DuckDB-WASM+TanStack MMO | 326 | EXPAND: tuatha-platform §Architecture | sovereign MMO state architecture; same as tuatha copy |
| docs/teanga/Interactive Map & AI Agents.md | Celtic OS PostHog Product OS | 356 | KEEP-NEW: tuatha-mmo/references/celtic-os-product-os.md | TanStack+Shadcn+Lonboard+Celtic OS window manager |
| docs/teanga/Irish Handwriting App Development.md | Irish HTR MLX+llama.cpp+Pencil | 291 | KEEP-NEW: irish-llm-on-device/references/irish-handwriting-mlx.md | MLX+Apple Pencil Irish HTR iPadOS (same as tuatha copy) |
| docs/teanga/Irish LLM for iPhone Development.md | Irish LLM iOS Unsloth GGUF | 420 | KEEP-NEW: irish-llm-on-device/references/irish-llm-ios-unsloth.md | Unsloth+Qomhrá+UCCIX iOS deployment (canonical, same as tuatha copy) |
| docs/teanga/Leaving Certificate Material App.md | TanStack Start LC prescribed texts | 328 | KEEP-NEW: celtic-asset-generation/references/leaving-cert-tanstack-app.md | LC prescribed material polymorphic TanStack schema |
| docs/teanga/Multimodal Irish Handwriting Generation Model.md | InkSpire+Qwen3 Gaelic handwriting gen | 273 | KEEP-NEW: celtic-asset-generation/references/inkspire-gaelic-handwriting-gen.md | InkSpire diffusion + MVTM Gaelic handwriting synthesis |
| docs/teanga/Neuro-Symbolic Translation Model Training.md | neuro-symbolic Gaeilge InkSpire | 253 | KEEP-NEW: celtic-asset-generation/references/neuro-symbolic-translation-engine.md | InkSpire Masked-CFM neuro-symbolic Gaeilge engine |
| docs/teanga/PlanetScale _ MotherDuck Docs.md | PlanetScale+MotherDuck pg_duckdb | 172 | CLIPPING: celtic-asset-generation/references/clippings/planetscale-motherduck.md | external MotherDuck docs clipping |
| docs/teanga/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray.md | Lance Namespace+Ray+production | 375 | CLIPPING: celtic-asset-generation/references/clippings/lance-namespace-ray.md | external LanceDB blog clipping, covered by lancedb skill |
| docs/teanga/README.md | teanga research papers README | 25 | DELETE | trivial index pointing to old paths |
| docs/teanga/Scraping Irish Audio Files.md | Teanglann+Canúint audio scrape | 345 | KEEP-NEW: irish-llm-on-device/references/teanglann-canuint-audio-scrape.md | Teanglann+Canúint dialectal ASR corpus extraction |
| docs/teanga/Using MotherDuck with PlanetScale — PlanetScale.md | PlanetScale+MotherDuck quickstart | 46 | CLIPPING: celtic-asset-generation/references/clippings/planetscale-motherduck-quickstart.md | external PlanetScale blog clipping |
| docs/teanga/british_isles_parallel_data_sources.md | British Isles parallel edu data | 286 | KEEP-NEW: celtic-asset-generation/references/british-isles-parallel-edu.md | UK+ROI parallel education data coverage map |
| docs/teanga/eu-irish-datasets.md | EU Irish datasets list | 1800 | EXPAND: oideachas-pipeline §EU sources | 1800-line EU+Irish dataset catalogue; covered but detailed enough to keep reference |
| docs/teanga/gaeilge.md | Gaeltacht areas PoC map | 183 | KEEP-NEW: celtic-asset-generation/references/gaeilge-gaeltacht-poc-map.md | Gaeltacht+LPA Tailte Éireann census data PoC |
| docs/teanga/geoai-Geospatial Workflow & Particle Effects(1).md | DuckDB+Lonboard+Marimo WebGPU | 340 | KEEP-NEW: celtic-asset-generation/references/cloud-native-geospatial-webgpu.md | cloud-native OLAP + WebGPU meteorological viz (same as tuatha copy) |
| docs/teanga/irish_bilingual_dataset_research.md | Gaois Irish bilingual dataset | 1173 | KEEP-NEW: celtic-asset-generation/references/gaois-irish-bilingual-dataset.md | 1173-line DCU Gaois dataset acquisition blueprint |
| docs/teanga/motherduck_mcp.md | MotherDuck MCP server | 457 | EXPAND: motherduck §MCP | MotherDuck's own MCP server docs, already covered by motherduck skill |
| docs/teanga/notebooklm_1.md | NotebookLM Celtic model notes | 42 | DELETE | research note from NotebookLM with no KCG-specific synthesis |
| docs/teanga/scottish_gaelic_huggingface_resources.md | Scottish Gaelic HF resource list | 427 | EXPAND: celtic-language-ai §Celtic LLMs (Gàidhlig) | comprehensive HF resource list for gd models |
| docs/teanga/useAgent Hook.md | useAgent hook docs | 512 | CLIPPING: tuatha-mmo/references/clippings/copilotkit-useagent-hook.md | external CopilotKit docs, covered by copilotkit skill |
| docs/teanga/utter-project_EuroLLM-22B-Instruct-2512 · Hugging Face.md | EuroLLM-22B model card | 137 | EXPAND: kcg-ml-models §Celtic LLMs | EuroLLM model card for Irish (canonical for this model) |
| docs/teanga/welsh-huggingface-resources.md | Welsh HF resource list | 624 | EXPAND: celtic-language-ai §Celtic LLMs (Welsh) | comprehensive HF resource list for cy models |
| docs/tuatha/00-nav/GRAPHICS_INDEX.md | graphics+game dev doc index | 246 | DELETE | doc index, content already in tuatha-mmo §references |
| docs/tuatha/00-nav/PIPELINES.md | tuatha data pipeline architecture | 478 | KEEP-NEW: tuatha-mmo/references/tuatha-pipelines.md | canonical tuatha pipeline diagram (DLT+CocoIndex+Dagster) |
| docs/tuatha/00-nav/Tuath API Reference.md | Tuath API reference | 810 | KEEP-NEW: tuatha-mmo/references/tuath-api-reference.md | full FastAPI+Axum API spec for tuatha backend |
| docs/tuatha/01-game-design/Asset Management for Full-Stack App.md | pixel-art RPG asset strategy | 354 | KEEP-NEW: celtic-asset-generation/references/asset-management-pixelart.md | LC subject asset strategy + UploadThing/Cloudinary |
| docs/tuatha/01-game-design/CELTIC_LANGUAGES.md | Celtic lang detection guide | 775 | KEEP-NEW: tuatha-mmo/references/celtic-languages-detection.md | langdetect+langcode+model gap mitigation for tuatha |
| docs/tuatha/01-game-design/Celtic Naming for the MMO.md | Celtic lexicography naming compendium | 593 | KEEP-NEW: tuatha-mmo/references/celtic-naming-lexicography.md | anam/tír/aran/gaelg/cymr/yern philology + Web3 conflicts |
| docs/tuatha/01-game-design/Educational Game Dev Pipeline.md | DIAGE physics/chem pipeline | 457 | KEEP-NEW: tuatha-mmo/references/diage-physics-chem-game-pipeline.md | KCG rename of teanga copy; same content |
| docs/tuatha/01-game-design/GAME_CLIENT.md | Babylon.js game client | 686 | KEEP-NEW: tuatha-mmo/references/babylonjs-game-client.md | TuathGame+SceneManager+SpacetimeDB Babylon 7 client |
| docs/tuatha/01-game-design/MMO Geospatial Data & Visual RAG.md | WebGPU MMO+Visual RAG | 348 | KEEP-NEW: tuatha-mmo/references/mmo-geospatial-visual-rag.md | DuckDB+MotherDuck+RisingWave+SpacetimeDB WebGPU MMO |
| docs/tuatha/01-game-design/educational-game-development.md | educational game dev guide | 687 | KEEP-NEW: tuatha-mmo/references/educational-game-development.md | full educational game dev pipeline, longer than DIAGE copy |
| docs/tuatha/01-game-design/engine-selection.md | Anam agentic+payment engine | 221 | KEEP-NEW: tuatha-mmo/references/anam-engine-selection.md | Anam MMO ecosystem CopilotKit+x402+KMP (same as teanga copy) |
| docs/tuatha/01-game-design/mythology-framework.md | pent-elemental Celtic cosmology | 385 | KEEP-NEW: tuatha-mmo/references/mythology-pent-elemental-cosmology.md | Spirit/Water/Fire/Earth/Air+Anam Cara MMO design |
| docs/tuatha/01-game-design/world-map.md | Celtic OS PostHog architecture | 356 | KEEP-NEW: tuatha-mmo/references/celtic-os-postmog-architecture.md | window-manager Product-OS for British Isles |
| docs/tuatha/02-agents/Agentic Education Platform Development.md | agentic academy CopilotKit+AgUI | 317 | KEEP-NEW: tuatha-mmo/references/agentic-education-platform.md | CopilotKit+AgUI+MCP+x402 academy architecture |
| docs/tuatha/02-agents/Tuath Agent System.md | Tuath multi-agent architecture | 1586 | KEEP-NEW: tuatha-mmo/references/tuath-agent-architecture.md | canonical Tuath agent system: tutor/myth/quest/research |
| docs/tuatha/03-data-pipelines/ADDING_DATA_SOURCES.md | DLT source onboarding | 830 | KEEP-NEW: tuatha-mmo/references/adding-dlt-data-sources.md | how-to add DLT source to tuatha pipeline |
| docs/tuatha/03-data-pipelines/Agentic Web Scraping Pipeline.md | neuro-symbolic Browserbase+BAML | 572 | EXPAND: kcg-leabharlann-pipeline §Ingestion layer | duplicate of teanga copy, point to celtic-asset-generation reference |
| docs/tuatha/03-data-pipelines/British Isles Education Map.md | British Isles demographic atlas | 483 | KEEP-NEW: celtic-asset-generation/references/british-isles-edu-map.md | same as teanga copy |
| docs/tuatha/03-data-pipelines/British Isles Game Dev Data Pipeline.md | OS MasterMap+GeoHive+LiDAR | 208 | KEEP-NEW: tuatha-mmo/references/british-isles-game-dev-pipeline.md | 2.5D game terrain from OS data + Met Office |
| docs/tuatha/03-data-pipelines/Building an Educational Agent's Knowledge Base.md | Agno+Dagster+dlt+BAML KB | 631 | KEEP-NEW: celtic-asset-generation/references/agent-knowledge-base.md | self-healing ontology + R2+Cloudflare+Cognee/Graphiti |
| docs/tuatha/03-data-pipelines/CRYPTEOLAS_INTEGRATION_GUIDE.md | crypteolas CopilotKit+AgentOS | 938 | KEEP-NEW: tuatha-mmo/references/crypteolas-copilotkit-integration.md | portfolio analysis+market monitoring+trade execution |
| docs/tuatha/03-data-pipelines/CRYPTO_INTEGRATION_SUMMARY.md | x402+MCPay+AP2+Web3 | 986 | KEEP-NEW: upstream-mirrors/references/crypteolas-crypto-integration.md | canonical x402 stack for crypteolas (combine with x402 mirror) |
| docs/tuatha/03-data-pipelines/Celtic Language Data Aggregation & Analysis.md | Celtic data lakehouse | 343 | KEEP-NEW: celtic-asset-generation/references/celtic-linguistic-lakehouse.md | same as teanga copy |
| docs/tuatha/03-data-pipelines/Crypteolas_ Federated Learning & Crypto Payments.md | crypteolas federated+SyftBox+x402 | 435 | KEEP-NEW: tuatha-mmo/references/crypteolas-fl-crypto.md | federated learning+crypto payments on iPhone (SyftBox+Flower+x402) |
| docs/tuatha/03-data-pipelines/Data Platform Technical Integration Plan.md | Dagster+DLT+CocoIndex+Feast | 2836 | KEEP-NEW: tuatha-mmo/references/data-platform-integration-plan.md | canonical 2836-line data platform plan (Crypto Analytics worked example) |
| docs/tuatha/03-data-pipelines/Integrating Rust, DuckDB, TanStack, CopilotKit.md | sovereign MMO state stack | 326 | KEEP-NEW: tuatha-mmo/references/sovereign-mmo-state-stack.md | same as teanga copy, mark as primary |
| docs/tuatha/03-data-pipelines/LLM Serving with MLflow & Langfuse.md | llama-swap+MLX+LiteLLM gateway | 381 | KEEP-NEW: upstream-mirrors/references/llm-serving-mlflow-langfuse.md | llama-swap+mlx-vlm+LiteLLM+Z.AI gateway (kcg-ml-models expansion source) |
| docs/tuatha/03-data-pipelines/Multimodal Video Knowledge Graph Pipeline.md | yt-dlp+WhisperX+GraphRAG | 482 | KEEP-NEW: celtic-asset-generation/references/multimodal-video-kg.md | yt-dlp+WhisperX+Qwen3-Omni video→KG pipeline |
| docs/tuatha/03-data-pipelines/TanStack DB Integration and Comparison.md | TanStack DB+DuckDB+RisingWave | 288 | KEEP-NEW: celtic-asset-generation/references/tanstack-db-integration.md | differential dataflow client-side DB |
| docs/tuatha/03-data-pipelines/dlt_crawl4ai_lancedb.md | dlt+crawl4ai+LanceDB crypto | 298 | KEEP-NEW: celtic-asset-generation/references/dlt-crawl4ai-lancedb-crypto.md | crypto sentiment fear-and-greed+dlt+crawl4ai+LanceDB |
| docs/tuatha/04-game-tech/Game Dev Pipeline Research & Plan.md | Hades+BitCraft+LangGraph | 328 | KEEP-NEW: tuatha-mmo/references/hades-bitcraft-pipeline.md | Supergiant+SpacetimeDB+agentic research pipeline |
| docs/tuatha/04-game-tech/Game Particle Effects Research(2).md | Anam meteorological particle sim | 298 | KEEP-NEW: tuatha-mmo/references/anam-meteorological-particles.md | Catmull-Rom+Bicubic+GRIB2+SpacetimeDB particle system |
| docs/tuatha/04-game-tech/Game Reverse Engineering Workflow Design.md | DIARE Z.AI+Agno reverse eng | 418 | KEEP-NEW: tuatha-mmo/references/diare-game-reverse-engineering.md | Ghidra+Frida+FFmpeg+UnityPy+Storybook agentic SRE |
| docs/tuatha/04-game-tech/Generative AI Art Workflow Integration.md | InvokeAI+MLX+shadcn asset gen | 249 | KEEP-NEW: celtic-asset-generation/references/invokeai-mlx-asset-workflow.md | agentic Bria→InvokeAI+MLX workflow for TanStack Start |
| docs/tuatha/04-game-tech/Geospatial Workflow & Particle Effects(1).md | DuckDB+Lonboard+WebGPU geo | 340 | KEEP-NEW: celtic-asset-generation/references/cloud-native-geospatial-webgpu-2.md | same as teanga copy, treat as primary |
| docs/tuatha/04-game-tech/Interactive AI Pipeline Development.md | Gradio+CopilotKit+AG-UI Fibo | 441 | KEEP-NEW: celtic-asset-generation/references/gradio-copilotkit-fibo.md | Gradio MCP server + CopilotKit AG-UI + Bria Fibo |
| docs/tuatha/04-game-tech/Rust Full-Stack Gaming Environment.md | Rust SpacetimeDB+Godot gdext | 554 | KEEP-NEW: tuatha-mmo/references/rust-fullstack-gaming.md | Rust workspace + SpacetimeDB+Godot GDExtension+Alloy |
| docs/tuatha/04-game-tech/SpacetimeDB Ogham Stone Game Integration.md | CISP+Megalithic+Ogham SpacetimeDB | 690 | KEEP-NEW: tuatha-mmo/references/spacetimedb-ogham-integration.md | CISP/Megalithic Portal Ogham ETL+Solana dNFT+Metaplex |
| docs/tuatha/04-game-tech/Spacetimedb Blockchain Integration Strategy.md | SpacetimeDB+Solana+Ethereum MMO | 325 | KEEP-NEW: tuatha-mmo/references/spacetimedb-blockchain-strategy.md | Token-2022+EIP-7702+SpacetimeDB+Metaplex Core |
| docs/tuatha/04-game-tech/reference/ADDING_ZONES.md | Babylon.js zone how-to | 516 | KEEP-NEW: tuatha-mmo/references/adding-babylonjs-zones.md | how-to add Celtic-language Babylon.js zones |
| docs/tuatha/04-game-tech/reference/DEPLOYMENT.md | tuatha Cloudflare deployment | 762 | KEEP-NEW: tuatha-mmo/references/tuatha-deployment-guide.md | Cloudflare Workers+R2+SpacetimeDB production deploy |
| docs/tuatha/04-game-tech/reference/FRONTEND.md | TanStack Start tuatha frontend | 736 | KEEP-NEW: tuatha-mmo/references/tuatha-tanstack-frontend.md | routes+components+SIWE+X402Paywall+TuathCopilot |
| docs/tuatha/04-game-tech/reference/PERFORMANCE_TUNING.md | embedding+game perf tuning | 883 | KEEP-NEW: tuatha-mmo/references/tuatha-performance-tuning.md | batch embedding 100×, HNSW, game client 60 FPS |
| docs/tuatha/04-game-tech/reference/guides/CROSS_PLATFORM_GUIDE.md | KMP+RN+Godot cross-platform | 781 | KEEP-NEW: tuatha-mmo/references/cross-platform-guide.md | KMP+Swift+React Native+Godot tuatha client |
| docs/tuatha/04-game-tech/reference/guides/GODOT_RUST_GUIDE.md | gdext Godot 4 Rust guide | 763 | KEEP-NEW: tuatha-mmo/references/gdext-godot-rust-guide.md | gdext setup+SpacetimeDB SDK integration |
| docs/tuatha/04-game-tech/reference/guides/PAYMENT_GUIDE.md | x402 tuatha payment guide | 811 | KEEP-NEW: upstream-mirrors/references/x402-payment-guide.md | x402 server/client/Axum middleware tuatha guide |
| docs/tuatha/04-game-tech/reference/guides/SPACETIMEDB_GUIDE.md | SpacetimeDB tuatha guide | 713 | KEEP-NEW: tuatha-mmo/references/spacetimedb-tuatha-guide.md | SpacetimeDB tables+reducers+TS SDK |
| docs/tuatha/04-game-tech/reference/guides/WGPU_GUIDE.md | wgpu Celtic-shaders guide | 699 | KEEP-NEW: upstream-mirrors/references/wgpu-tuatha-guide.md | wgpu+particle-system+Celtic-shaders tuatha setup |
| docs/tuatha/05-ios-ml/Federated AI Marketplace on iPhone.md | Crypteolas iOS federated+x402 | 297 | KEEP-NEW: tuatha-mmo/references/crypteolas-ios-marketplace.md | Apple MLX+x402+Flower+PySyft iOS marketplace |
| docs/tuatha/05-ios-ml/Irish Handwriting App Development.md | Irish HTR MLX+Pencil iOS | 291 | KEEP-NEW: irish-llm-on-device/references/irish-htr-mlx-pencil.md | same as teanga copy |
| docs/tuatha/05-ios-ml/Irish LLM for iPhone Development.md | Unsloth iOS Irish LLM | 420 | KEEP-NEW: irish-llm-on-device/references/irish-llm-unsloth-ios.md | same as teanga copy, mark as primary |
| docs/tuatha/05-ios-ml/apple_ml-fastvlm_ This repository contains the official implementation of _FastVLM_ Efficient Vision Encoding for Vision Language Models_ - CVPR 2025.md | FastVLM Apple CVPR 2025 | 122 | CLIPPING: irish-llm-on-device/references/clippings/fastvlm-apple-cvpr-2025.md | external Apple CVPR 2025 VLM, fits irish-llm-on-device context |
| docs/tuatha/05-ios-ml/celtic-ocr.md | bilingual HTR ColPali+Unsloth | 245 | KEEP-NEW: irish-llm-on-device/references/celtic-ocr-colpali-unsloth.md | bilingual iOS HTR (same as teanga/Fine-tuning-VLMs-for-iOS-HTR copy) |
| docs/tuatha/05-ios-ml/iOS App Development Ecosystem Strategy.md | KMP+Swift+Sandwich iOS+CopilotKit | 372 | KEEP-NEW: tuatha-mmo/references/ios-sandwich-architecture.md | Hybrid-Native Sandwich KMP+Swift+Rust+UniFFI |
| docs/tuatha/06-tokenomics/Learn-to-Earn Blockchain and AI.md | Cianfhoghlaim Scoilverse L2E | 349 | KEEP-NEW: tuatha-mmo/references/cianfhoghlaim-scoilverse-l2e.md | EBSI+Hypercerts+Solana+Mythology+Vargas learn-to-earn |
| docs/tuatha/06-tokenomics/Sign In With Ethereum (SIWE) _ Better Auth.md | Better Auth SIWE plugin | 433 | CLIPPING: upstream-mirrors/references/clippings/better-auth-siwe.md | external Better Auth SIWE docs, covered by better-auth skill |
| docs/tuatha/06-tokenomics/x402-payments.md | Celtic Knowledge Grid x402 | 348 | KEEP-NEW: upstream-mirrors/references/x402-celtic-knowledge-grid.md | x402+MCP+mcp-ui+Bria+Convex/BitCraft celtic grid |
| docs/tuatha/07-clippings/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md | AG-UI vs A2UI CopilotKit | 65 | CLIPPING: tuatha-mmo/references/clippings/copilotkit-ag-ui-a2ui.md | external CopilotKit clipping, covered by copilotkit skill |
| docs/tuatha/07-clippings/Comparing the Top 6 Agent-Native Rails for the Agentic Internet_ MCP, A2A, AP2, ACP, x402, and Kite.md | 6 agent-native rails comparison | 364 | CLIPPING: upstream-mirrors/references/clippings/agent-native-rails-compare.md | external marktechpost article on agent rails |
| docs/tuatha/07-clippings/GeoAI.md | GeoAI Python package | 150 | CLIPPING: celtic-asset-generation/references/clippings/opengeos-geoai.md | external opengeoai.org clipping, geospatial context |
| docs/tuatha/07-clippings/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md | AnyLanguageModel Apple SDK | 216 | CLIPPING: irish-llm-on-device/references/clippings/anylanguagemodel-apple.md | external HF blog, already in AnyLanguageModel mirror summary |
| docs/tuatha/07-clippings/Kotlin Multiplatform vs. React Native_ A cross-platform comparison _ Kotlin Multiplatform.md | KMP vs React Native | 107 | CLIPPING: tuatha-mmo/references/clippings/kmp-vs-react-native.md | external JetBrains article, KMP selection rationale |
| docs/tuatha/07-clippings/MCP-UI.md | MCP-UI protocol | 40 | CLIPPING: tuatha-mmo/references/clippings/mcp-ui.md | external mcpui.dev clipping, UI protocol |
| docs/tuatha/07-clippings/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md | wgpu v28 release notes | 393 | CLIPPING: upstream-mirrors/references/clippings/wgpu-v28-release.md | external wgpu release notes, covered by wgpu mirror |
| docs/tuatha/07-clippings/Swift Transformers Reaches 1.0 – and Looks to the Future.md | Swift Transformers 1.0 | 158 | CLIPPING: irish-llm-on-device/references/clippings/swift-transformers-1-0.md | external HF blog, iOS context |
| docs/tuatha/07-clippings/The Expulsion of the Déisi - Wikipedia.md | Déisi Wikipedia article | 110 | CLIPPING: tuatha-mmo/references/clippings/deisi-wikipedia.md | external Wikipedia, Irish mythology reference |
| docs/tuatha/07-clippings/Unsloth Model Catalog _ Unsloth Documentation.md | Unsloth model catalog | 344 | CLIPPING: irish-llm-on-device/references/clippings/unsloth-model-catalog.md | external Unsloth docs clipping, covered by unsloth skill |
| docs/tuatha/07-clippings/useAgent Hook.md | useAgent hook docs | 512 | CLIPPING: tuatha-mmo/references/clippings/copilotkit-useagent-hook-2.md | external CopilotKit useAgent docs (duplicates teanga copy) |
| docs/tuatha/ANALYSIS.md | Cianfhoghlaim project analysis | 351 | DELETE | high-level root summary, content already in tuatha-mmo body |
| docs/tuatha/INDEX.md | tuatha doc index | 170 | DELETE | doc index, superseded by new skills |
| docs/tuatha/README.md | Game Dev reference library | 167 | KEEP-NEW: tuatha-mmo | rewritten to point at the 4 new skills |
| docs/tuatha/08-mirrors/_summaries/repo-AnyLanguageModel.md | AnyLanguageModel KCG summary | 19 | KEEP-NEW: upstream-mirrors/references/anylanguagemodel.md | KCG-authored mirror summary, see 08-mirrors policy |
| docs/tuatha/08-mirrors/_summaries/repo-SpacetimeDB.md | SpacetimeDB KCG summary | 32 | KEEP-NEW: upstream-mirrors/references/spacetimedb.md | KCG-authored mirror summary |
| docs/tuatha/08-mirrors/_summaries/repo-agui_kotlin.md | agui_kotlin KCG summary | 29 | KEEP-NEW: upstream-mirrors/references/agui-kotlin.md | KCG-authored mirror summary |
| docs/tuatha/08-mirrors/_summaries/repo-hophacks-spacetimedb-workshop.md | hophacks SpacetimeDB summary | 22 | KEEP-NEW: upstream-mirrors/references/hophacks-spacetimedb-workshop.md | KCG-authored mirror summary |
| docs/tuatha/08-mirrors/_summaries/repo-ireland.md | ireland maps KCG summary | 16 | KEEP-NEW: upstream-mirrors/references/ireland-maps.md | KCG-authored mirror summary |
| docs/tuatha/08-mirrors/_summaries/repo-react-native-godot.md | react-native-godot KCG summary | 18 | KEEP-NEW: upstream-mirrors/references/react-native-godot.md | KCG-authored mirror summary |
| docs/tuatha/08-mirrors/_summaries/repo-react-native-reusables.md | react-native-reusables summary | 17 | KEEP-NEW: upstream-mirrors/references/react-native-reusables.md | KCG-authored mirror summary |
| docs/tuatha/08-mirrors/_summaries/repo-spacetimedb-cookbook.md | SpacetimeDB cookbook summary | 28 | KEEP-NEW: upstream-mirrors/references/spacetimedb-cookbook.md | KCG-authored mirror summary |
| docs/tuatha/08-mirrors/_summaries/repo-spacetimedb-typescript-sdk.md | spacetimedb TS SDK summary | 27 | KEEP-NEW: upstream-mirrors/references/spacetimedb-typescript-sdk.md | KCG-authored mirror summary |
| docs/tuatha/08-mirrors/_summaries/repo-wgpu.md | wgpu KCG summary | 34 | KEEP-NEW: upstream-mirrors/references/wgpu.md | KCG-authored mirror summary |
| docs/tuatha/08-mirrors/_summaries/repo-x402.md | x402 KCG summary | 22 | KEEP-NEW: upstream-mirrors/references/x402.md | KCG-authored mirror summary |

## New skill bodies & reference inventory

### `celtic-asset-generation` (new)
The Celtic asset generation / extraction / curriculum knowledge-graph skill. Body covers the canonical 5-stage pipeline (BAML extraction → CocoIndex v1 embedding → Cognee/FalkorDB cognify → Graphiti temporal memory → LanceDB vector) for bilingual curriculum and cultural-heritage content. References (37 files) include both the synthesis blueprints and external clippings. Most references are research-grade and should be summarized, not copied verbatim.

References:
- `references/baml-fibo-chemistry.md` — AI Chemistry Education Image Generation
- `references/baml-irish-education-kg.md` — BAML Schemas for Irish Education
- `references/baml-adaptive-syllabus.md` — BAML for Syllabus-Driven Data Extraction
- `references/british-isles-demographic-atlas.md` — British Isles Education Map (canonical)
- `references/british-isles-edu-map.md` — British Isles Education Map (tuatha copy, mark duplicate)
- `references/british-isles-parallel-edu.md` — british_isles_parallel_data_sources
- `references/celtic-linguistic-lakehouse.md` — Celtic Language Data Aggregation (Celtic-Bench + lakehouse)
- `references/celtic-bench-educational-corpora.md` — Celtic Language Educational Data Scrape
- `references/chemistry-react-assets.md` — Chemistry Education Asset Generation
- `references/cognee-cocoindex-graphiti-stack.md` — Graph Tech Integration and Recommendation
- `references/diffusion-irish-translation.md` — Enhancing English-Irish Translation with Diffusion Models
- `references/dlt-crawl4ai-lancedb-crypto.md` — dlt_crawl4ai_lancedb
- `references/federated-linguistic-data-lakehouse.md` — Celtic Data Scraping and Integration Plan
- `references/gaeilge-gaeltacht-poc-map.md` — gaeilge.md
- `references/gaois-irish-bilingual-dataset.md` — irish_bilingual_dataset_research
- `references/geoai-Geospatial Workflow & Particle Effects.md` — primary (tuatha copy)
- `references/hidden-heritages-duckdb.md` — Geospatial Data Analysis and DuckDB
- `references/ibis-duckdb-education-geo.md` — Geospatial Data Visualization with Ibis
- `references/invokeai-mlx-asset-workflow.md` — Generative AI Art Workflow Integration
- `references/inkspire-gaelic-handwriting-gen.md` — Multimodal Irish Handwriting Generation Model
- `references/leaving-cert-tanstack-app.md` — Leaving Certificate Material App
- `references/multimodal-video-kg.md` — Multimodal Video Knowledge Graph Pipeline
- `references/neuro-symbolic-gaeilge-engine.md` — AI Agents for Irish Language Resources
- `references/neuro-symbolic-translation-engine.md` — Neuro-Symbolic Translation Model Training
- `references/olake-lakekeeper-risingwave.md` — Integrating Olake, Lakekeeper, RisingWave
- `references/agent-knowledge-base.md` — Building an Educational Agent's Knowledge Base
- `references/skyvern-celtic-scrape.md` — Celtic Data Scraping and Integration Plan
- `references/asset-management-pixelart.md` — Asset Management for Full-Stack App
- `references/tanstack-db-integration.md` — TanStack DB Integration and Comparison
- `references/gradio-copilotkit-fibo.md` — Interactive AI Pipeline Development
- `references/webgpu-geospatial-particle.md` — Geospatial Workflow & Particle Effects (alt)
- `papers/bolmo.pdf` — Bolmo VLM tech report (2.0 MB)
- `papers/molmo2-tech-report.pdf` — Molmo2 VLM tech report (38.7 MB)
- `clippings/dr-lib-resources.md` — DR-LIB article
- `clippings/dlt-marimo-ibis.md` — dlt+marimo+ibis
- `clippings/planetscale-motherduck.md` — PlanetScale+MotherDuck
- `clippings/planetscale-motherduck-quickstart.md` — PlanetScale+MotherDuck quickstart
- `clippings/lance-namespace-ray.md` — Lance+Ray
- `clippings/iceberg-browser-duckdb.md` — Iceberg in Browser
- `clippings/opengeos-geoai.md` — GeoAI
- `clippings/google-adk-litellm.md` — Google ADK+LiteLLM

### `tuatha-mmo` (new)
The Celtic Educational MMO + Babylon.js client + SpacetimeDB server skill. Body covers architecture, agent system, deployment, payment, and gameplay. ~55 references; many are long (the Tuath Agent System doc alone is 1586 lines). The most important: Tuath Agent Architecture, Game Client, Data Platform Plan, the 4 game-tech guides (ADDING_ZONES, DEPLOYMENT, FRONTEND, PERFORMANCE_TUNING), the 5 reference guides (CROSS_PLATFORM, GODOT_RUST, PAYMENT, SPACETIMEDB, WGPU), and the iOS Sandwich architecture.

References (key):
- `references/tuath-api-reference.md` — Tuath API Reference
- `references/tuatha-pipelines.md` — PIPELINES
- `references/diage-physics-chem-game-pipeline.md` — Educational Game Dev Pipeline
- `references/diage-educational-game-pipeline.md` — Educational Game Dev Pipeline (alt)
- `references/anam-engine-selection.md` — engine-selection
- `references/anam-mmo-engine-selection.md` — Game Development Research & AI Integration
- `references/mythology-pent-elemental-cosmology.md` — mythology-framework
- `references/celtic-os-postmog-architecture.md` — world-map
- `references/celtic-os-product-os.md` — Interactive Map & AI Agents
- `references/celtic-languages-detection.md` — CELTIC_LANGUAGES
- `references/celtic-naming-lexicography.md` — Celtic Naming for the MMO
- `references/educational-game-development.md` — educational-game-development
- `references/babylonjs-game-client.md` — GAME_CLIENT
- `references/agentic-education-platform.md` — Agentic Education Platform Development
- `references/tuath-agent-architecture.md` — Tuath Agent System
- `references/adding-dlt-data-sources.md` — ADDING_DATA_SOURCES
- `references/data-platform-integration-plan.md` — Data Platform Technical Integration Plan
- `references/sovereign-mmo-state-stack.md` — Integrating Rust, DuckDB, TanStack, CopilotKit
- `references/crypteolas-copilotkit-integration.md` — CRYPTEOLAS_INTEGRATION_GUIDE
- `references/crypteolas-fl-crypto.md` — Crypteolas Federated Learning & Crypto
- `references/crypteolas-ios-marketplace.md` — Federated AI Marketplace on iPhone
- `references/cianfhoghlaim-scoilverse-l2e.md` — Learn-to-Earn Blockchain and AI
- `references/ios-sandwich-architecture.md` — iOS App Development Ecosystem Strategy
- `references/british-isles-game-dev-pipeline.md` — British Isles Game Dev Data Pipeline
- `references/hades-bitcraft-pipeline.md` — Game Dev Pipeline Research & Plan
- `references/anam-meteorological-particles.md` — Game Particle Effects Research(2)
- `references/diare-game-reverse-engineering.md` — Game Reverse Engineering Workflow Design
- `references/rust-fullstack-gaming.md` — Rust Full-Stack Gaming Environment
- `references/spacetimedb-ogham-integration.md` — SpacetimeDB Ogham Stone Game Integration
- `references/spacetimedb-blockchain-strategy.md` — Spacetimedb Blockchain Integration Strategy
- `references/mmo-geospatial-visual-rag.md` — MMO Geospatial Data & Visual RAG
- `references/spacetimedb-tuatha-guide.md` — SPACETIMEDB_GUIDE
- `references/adding-babylonjs-zones.md` — ADDING_ZONES
- `references/tuatha-deployment-guide.md` — DEPLOYMENT
- `references/tuatha-tanstack-frontend.md` — FRONTEND
- `references/tuatha-performance-tuning.md` — PERFORMANCE_TUNING
- `references/cross-platform-guide.md` — CROSS_PLATFORM_GUIDE
- `references/gdext-godot-rust-guide.md` — GODOT_RUST_GUIDE
- `references/mcp-ui.md` — MCP-UI clipping
- `clippings/copilotkit-ag-ui-a2ui.md` — AG-UI vs A2UI
- `clippings/copilotkit-useagent-hook.md` — useAgent hook (teanga copy)
- `clippings/copilotkit-useagent-hook-2.md` — useAgent hook (tuatha copy)
- `clippings/kmp-vs-react-native.md` — KMP vs RN
- `clippings/deisi-wikipedia.md` — Déisi Wikipedia

### `irish-llm-on-device` (new)
The Irish (Celtic) LLM on Apple Silicon + on-device OCR/HTR + fine-tuning skill. Body covers MLX+llama.cpp+AnyLanguageModel inference, Unsloth+GGUF quantisation, ColPali+weak-supervision for handwriting alignment, Qwen2-VL/Qwen3-VL fine-tuning, ASR/TTS corpus scraping. ~10 references.

References:
- `references/irish-llm-unsloth-ios.md` — Irish LLM for iPhone Development (canonical)
- `references/irish-llm-ios-unsloth.md` — Irish LLM for iPhone (alt)
- `references/irish-htr-mlx-pencil.md` — Irish Handwriting App Development
- `references/irish-handwriting-mlx.md` — Irish Handwriting (alt)
- `references/celtic-ocr-colpali-unsloth.md` — celtic-ocr (canonical, bilingual iOS HTR)
- `references/ios-bilingual-htr.md` — Fine-tuning VLMs for iOS HTR (alt)
- `references/qwen-vl-celtic-ocr.md` — Celtic Language OCR Resource Analysis
- `references/qwen3-vl-gaelic-finetuning.md` — Finetuning Qwen3-VL for Gaelic OCR
- `references/colpali-qwenvl-gaelic-alignment.md` — Aligning Gaelic Script for QwenVL Finetuning
- `references/duchas-qwen-vl-htr.md` — Handwriting Recognition and Dataset Creation
- `references/teanglann-canuint-audio-scrape.md` — Scraping Irish Audio Files
- `clippings/anylanguagemodel-apple.md` — AnyLanguageModel
- `clippings/fastvlm-apple-cvpr-2025.md` — FastVLM
- `clippings/swift-transformers-1-0.md` — Swift Transformers 1.0
- `clippings/unsloth-model-catalog.md` — Unsloth Model Catalog

### `upstream-mirrors` (new)
The 11-mirror KCG registry of upstream repos (SpacetimeDB, wgpu, x402, AnyLanguageModel, agui_kotlin, hophacks, ireland maps, react-native-godot, react-native-reusables, spacetimedb-cookbook, spacetimedb-typescript-sdk). Body is the KCG summary of each mirror. ~12 references including the 11 KCG-authored summaries + 3 paid-payment / agent-rails reference docs.

References:
- `references/spacetimedb.md` — repo-SpacetimeDB summary
- `references/wgpu.md` — repo-wgpu summary
- `references/x402.md` — repo-x402 summary
- `references/anylanguagemodel.md` — repo-AnyLanguageModel summary
- `references/agui-kotlin.md` — repo-agui_kotlin summary
- `references/hophacks-spacetimedb-workshop.md` — repo-hophacks summary
- `references/ireland-maps.md` — repo-ireland summary
- `references/react-native-godot.md` — repo-react-native-godot summary
- `references/react-native-reusables.md` — repo-react-native-reusables summary
- `references/spacetimedb-cookbook.md` — repo-spacetimedb-cookbook summary
- `references/spacetimedb-typescript-sdk.md` — repo-spacetimedb-typescript-sdk summary
- `references/crypteolas-crypto-integration.md` — CRYPTO_INTEGRATION_SUMMARY (x402 stack)
- `references/x402-payment-guide.md` — PAYMENT_GUIDE (tuatha)
- `references/x402-celtic-knowledge-grid.md` — x402-payments (tuatha)
- `references/llm-serving-mlflow-langfuse.md` — LLM Serving with MLflow & Langfuse
- `references/wgpu-tuatha-guide.md` — WGPU_GUIDE
- `clippings/agent-native-rails-compare.md` — 6 agent-native rails
- `clippings/wgpu-v28-release.md` — wgpu v28 release
- `clippings/better-auth-siwe.md` — Better Auth SIWE

## Per-existing-skill delta

| existing skill | source files (this round) | section to expand |
|---|---|---|
| `baml` | docs/teanga/BAML, DLT, and AI Workflow Integration.md | §Polyglot code-gen (BAML as IDL across Python+TS) |
| `better-auth` | (covered by SIWE clipping) | (no expansion; covered by upstream-mirrors clipping) |
| `celtic-language-ai` | docs/teanga/Agentic Translation Workflow Technologies.md, docs/teanga/BritLLM.md, docs/teanga/scottish_gaelic_huggingface_resources.md, docs/teanga/welsh-huggingface-resources.md, docs/teanga/utter-project_EuroLLM-22B-Instruct-2512 · Hugging Face.md | §Celtic LLMs (add BritLLM, EuroLLM, Qomhrá 2025), §Translation stack (add diffusion NMT, English-pivoted CoT) |
| `copilotkit` | (covered by useAgent + AG-UI/A2UI clippings) | (no expansion; already comprehensive) |
| `cross-domain-registry` | docs/teanga/British Isles Celtic Language Education Data.md | §8 nations (add 2024-25 census fiscal context) |
| `embedding-pipeline` | (covered by 100× batch rule) | (no expansion; PERF_TUNING duplicates) |
| `kcg-leabharlann-pipeline` | docs/tuatha/03-data-pipelines/Agentic Web Scraping Pipeline.md, docs/teanga/Agentic Web Scraping Pipeline.md | §Ingestion layer (Browserbase+Agno+GLM-4.6v+BAML+Cognee flow) |
| `kcg-ml-models` | docs/teanga/utter-project_EuroLLM-22B-Instruct-2512 · Hugging Face.md, docs/tuatha/03-data-pipelines/LLM Serving with MLflow & Langfuse.md | §Celtic LLMs (add EuroLLM 22B), §Inference backends (llama-swap+mlx-vlm+LiteLLM+Z.AI gateway) |
| `motherduck` | docs/teanga/motherduck_mcp.md | §MCP (MotherDuck's own MCP server) |
| `oideachas-pipeline` | docs/teanga/eu-irish-datasets.md | §EU sources (1800-line EU+Irish dataset catalogue) |
| `tuatha-platform` | docs/tuatha/03-data-pipelines/Integrating Rust, DuckDB, TanStack, CopilotKit.md, docs/teanga/Integrating Rust, DuckDB, TanStack, CopilotKit.md, docs/teanga/Game Dev Pipeline Research & Plan.md | §Architecture (sovereign game state), §Dagster assets (Hades+BitCraft agentic research) |
| `dagster`, `dlt`, `olake`, `risingwave`, `lancedb`, `falkordb`, `cognee`, `graphiti`, `cognee`, `huggingface`, `unsloth`, `peft`, `trl`, `tts`, `asr`, `babylonjs`, `tanstack-start`, `tanstack-db`, `cloudflare`, `firecrawl`, `crawl4ai`, `marimo`, `langfuse`, `mlflow`, `litellm`, `pydantic`, `pydantic-ai`, `agno`, `google-adk`, `pdf`, `document-intelligence`, `image-management`, `data-engineer`, `stack-ops`, `stagehand`, `effect-ts`, `hono`, `orpc`, `cognee`, `kcg-bunchloch`, `kcg-convergence`, `secrets-management` | — | (no expansion needed; round 8 only touches teanga+tuatha) |

## Dedup pairs (near-duplicate files)

| pair (a=tuatha, b=teanga unless marked) | chosen canonical | reason |
|---|---|---|
| `docs/tuatha/04-game-tech/Geospatial Workflow & Particle Effects(1).md` ≈ `docs/teanga/geoai-Geospatial Workflow & Particle Effects(1).md` | teanga copy (line 340) | same content, teanga is primary dir |
| `docs/tuatha/05-ios-ml/Irish Handwriting App Development.md` ≈ `docs/teanga/Irish Handwriting App Development.md` | both, canonical = teanga (291 lines) | identical content |
| `docs/tuatha/05-ios-ml/Irish LLM for iPhone Development.md` ≈ `docs/teanga/Irish LLM for iPhone Development.md` | both, canonical = teanga (420 lines) | identical content |
| `docs/tuatha/05-ios-ml/celtic-ocr.md` ≈ `docs/teanga/Fine-tuning VLMs for iOS HTR.md` | celtic-ocr (245) is shorter; Fine-tuning-VLMs-for-iOS-HTR (245) is teanga version | essentially identical, treat as one ref |
| `docs/tuatha/03-data-pipelines/Agentic Web Scraping Pipeline.md` ≈ `docs/teanga/Agentic Web Scraping Pipeline.md` | both 572 lines, identical | mark as merge with kcg-leabharlann-pipeline |
| `docs/tuatha/03-data-pipelines/British Isles Education Map.md` ≈ `docs/teanga/British Isles Education Map.md` | both 483 lines, identical | mark as merge to celtic-asset-generation |
| `docs/tuatha/03-data-pipelines/Celtic Language Data Aggregation & Analysis.md` ≈ `docs/teanga/Celtic Language Data Aggregation & Analysis.md` | both 343 lines, identical | mark as merge to celtic-asset-generation |
| `docs/tuatha/03-data-pipelines/Integrating Rust, DuckDB, TanStack, CopilotKit.md` ≈ `docs/teanga/Integrating Rust, DuckDB, TanStack, CopilotKit.md` | both 326 lines, identical | mark as merge to tuatha-platform |
| `docs/tuatha/01-game-design/Educational Game Dev Pipeline.md` ≈ `docs/teanga/Educational Game Dev Pipeline.md` | both 457 lines, identical | mark as merge to tuatha-mmo |
| `docs/tuatha/01-game-design/world-map.md` ≈ `docs/teanga/Interactive Map & AI Agents.md` | both 356 lines, identical | mark as merge to tuatha-mmo |
| `docs/tuatha/01-game-design/engine-selection.md` ≈ `docs/teanga/Game Development Research & AI Integration.md` | both 221 lines, identical | mark as merge to tuatha-mmo |
| `docs/tuatha/07-clippings/useAgent Hook.md` ≈ `docs/teanga/useAgent Hook.md` | both 512 lines, identical | teanga copy is primary, tuatha becomes a redirect note in celtic-asset-generation; or keep both as tuatha-mmo/reference/clipping (since CopilotKit doc belongs to MMO) |
| `docs/tuatha/04-game-tech/Game Particle Effects Research(2).md` vs teanga copy | teanga copy doesn't exist | (no dup) |
| `docs/tuatha/03-data-pipelines/CRYPTO_INTEGRATION_SUMMARY.md` (986) vs `docs/tuatha/03-data-pipelines/CRYPTEOLAS_INTEGRATION_GUIDE.md` (938) | partial overlap; both kept (CRYPTO for x402, CRYPTEOLAS for crypteolas CopilotKit) | different angle (x402 vs CopilotKit) |
| `docs/teanga/Multimodal Irish Handwriting Generation Model.md` (273) vs `docs/teanga/Neuro-Symbolic Translation Model Training.md` (253) | both kept, related but different (InkSpire-Gaelic-gen vs InkSpire-translation) | topic different |

## Counts

- **Files in scope**: 141 (57 teanga .md + 2 teanga PDFs + 71 tuatha .md + 11 tuatha mirror summaries)
- **KEEP-NEW (new skill bodies/references)**: 110
  - celtic-asset-generation: 31 references + 2 PDFs + 9 clippings
  - tuatha-mmo: 39 references + 5 clippings
  - irish-llm-on-device: 11 references + 4 clippings
  - upstream-mirrors: 11 mirror summaries + 5 reference docs + 3 clippings
- **EXPAND (existing skills)**: 11 (baml, celtic-language-ai, cross-domain-registry, kcg-leabharlann-pipeline, kcg-ml-models, motherduck, oideachas-pipeline, tuatha-platform, plus implicit dlt/dagster from data-platform integration)
- **DELETE**: 9 (tuatha: ANALYSIS, INDEX, GRAPHICS_INDEX; teanga: INDEX, README, notebooklm_1, Gaelic-in-Digital-Age, DSPydantic — note `docs/tuatha/README.md` is rewritten, not deleted)
- **CLIPPING (external articles)**: 21 (12 from docs/tuatha/07-clippings/ + 9 from docs/teanga/ with `tags: clippings` frontmatter)
- **Near-duplicate pairs**: 13 (4 teanga/tuatha same-content pairs + 9 within-teanga/tuatha pairs)
- **PDFs**: 2 (Bolmo 2.0 MB, Molmo2 38.7 MB)
- **New skill bodies**: 4 (celtic-asset-generation, tuatha-mmo, irish-llm-on-device, upstream-mirrors)
- **Existing skills expanded**: 8 (baml, celtic-language-ai, cross-domain-registry, kcg-leabharlann-pipeline, kcg-ml-models, motherduck, oideachas-pipeline, tuatha-platform)
