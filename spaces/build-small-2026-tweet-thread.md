# Build Small 2026 — Twitter / X Thread

> 6 tweets for the @cianfhoghlaim Build Small 2026 submission. Each
> ends with a link or a Space slug. Co-post with the blog at
> doc/hackathons/build-small-2026-blog.md.

---

**1/6**  We shipped 4 @huggingface Spaces to the Build Small 2026
hackathon. 5 Celtic elements (Talamh / Uisce / Tine / Aer / Anam)
are the connective tissue that runs through every one. 1 typed
pipeline. All models ≤32B. #BuildSmall2026

**2/6**  Space 1: An Scrúdú. BAML extracts marking schemes from
Irish Leaving Cert past papers, returns a topic heatmap + PCLM-PDF.
Element: Talamh (Earth).
→ huggingface.co/spaces/cianfhoghlaim/an-scrudu

**3/6**  Space 2: Meaisín Cliste. 3 Celtic AI tools: 6-nation cognate
dictionary, school-density map (Pobal HP 2022, 26 counties), and
cross-nation curriculum compare. Elements: Aer + Uisce.
→ huggingface.co/spaces/cianfhoghlaim/meaisin-cliste

**4/6**  Space 3: Cianfhoghlaim. Hades-style dialogue with 6 Celtic
NPCs (Manannán, Rhiannon, Dian Cécht, Cian, Uí Liatháin, The Déisi)
on a navigable British Isles map. Each NPC grounded in a cached
Wikipedia article. Element: Anam.
→ huggingface.co/spaces/cianfhoghlaim/cianfhoghlaim

**5/6**  Space 4: Anam: Tuatha na nGaelscoil. The integration Space.
5 elements + 2 cross-cutting features = 7 panels. Bilingual EN/GA
classroom switcher. Soulbound token with 3 stages (Sétanta →
Cúchulainn → Ríastrad). Element: all 5.
→ huggingface.co/spaces/cianfhoghlaim/anam-tuatha

**6/6**  The model layer: 3-tier HF Inference fallback.
Qwen2.5-7B → Llama-3.1-8B → Gemma-2-9b, all ≤32B.
p95 dialogue latency: 3.2s. Cost per turn: $0.0002.
Every Space also has an offline regex/template fallback.
The full write-up: [link to blog]. #BuildSmall2026
