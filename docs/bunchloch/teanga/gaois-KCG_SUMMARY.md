# KCG_SUMMARY: Gaois — Irish Language Digital Infrastructure (DCU)

## What It Is
Gaois is the research group at Fiontar & Scoil na Gaeilge, Dublin City University, responsible for building Ireland's core digital language infrastructure. This repository snapshot contains multiple interconnected projects: the National Terminology Database for Irish (téarma.ie), the Placenames Database of Ireland (logainm.ie), the Dúchas folklore API, Irish-language surname databases with grammatical inflection, a terminology management tool (Terminologue), multilingual technical documentation platform (Documental), and developer SDK components (QueryLogger, Localizer).

## Why This Matters for Kings' College Galway
Gaois represents the gold standard for Irish-language digital infrastructure — every project here is a live, government-funded service used by Irish speakers daily. For Kings' College Galway's **teanga** platform, these systems provide the foundational reference data and API patterns needed for any Celtic language curriculum tool: authoritative placenames for geography modules, the national terminology database for vocabulary and subject-specific Irish, grammatically-inflected surname data for teaching Irish grammar through personal identity, and a proven pattern for bilingual technical documentation (Irish/English) that the school's own platform should emulate.

## Key Patterns Preserved
- `Tearma/README.md` — Source code of téarma.ie, the National Terminology Database for Irish
- `Tearma/TearmaWeb/wwwroot/cabhair/*.md` — Bilingual (Irish/English) user help documentation for téarma.ie
- `Tearma/TearmaWeb/wwwroot/eolas/*.md` — Bilingual project background, corpus, committee, and data protection docs
- `terminologue/README.md` — Open-source terminology management tool (powers téarma.ie)
- `terminologue/docs/*.md` — Technical documentation for configuring, installing, and using Terminologue
- `terminologue/website/docs/info.*.md` — Multilingual (17 languages) about/intro pages
- `documental/README.md` — Multilingual technical documentation platform (Irish/English)
- `documental/docs/software/*/*.md` — Bilingual docs for Documental, GeoNames2Sql, Localizer, QueryLogger, Terminologue
- `DuchasAPI-docs/README.md` — Dúchas National Folklore Collection API (v0.5) with full endpoint reference
- `DuchasAPI-docs/DATADICT.md` — Dúchas data dictionary
- `DuchasAPI-docs/CHANGELOG.md`, `TODO.md` — Development history and roadmap
- `LogainmAPI-docs/README.md` — Placenames Database of Ireland API (v0.9) with full endpoint reference
- `LogainmAPI-docs/DATADICT.md`, `DECISIONS.md`, `CHANGELOG.md` — Data dictionary and design decisions
- `sloinnte/README.md` — Database of Irish-Language Surnames with XML format docs and grammatical inflection rules
- `IrishSurnameIndex/README.md` — Irish Folklore Commission surname collection (ODbL-licensed)
- `Gaois.QueryLogger/README.md` — .NET query logging library
- `Gaois.Localizer/README.md` — .NET localisation library
- `gaoisalign/README.md` — Text alignment tool
- `GeoNames2Sql/README.md`, `LICENSE.md` — GeoNames import tool
- `Nationalist/README.md` — Nationalist project
- `screenful/README.md` — UI component library

## Source Files
Full source code was removed on 2026-06-06. All projects are maintained by the Gaois research group at github.com/gaois. This skeleton preserves the bilingual documentation that describes the architecture, API design, and linguistic data models used across Ireland's national language infrastructure.

## What Was Removed
- .NET/C# application source code (TearmaWeb, Géonames2Sql, QueryLogger, Localizer)
- PHP source code (Terminologue, Documental)
- SQL database schemas and migration scripts
- XML data files (surname databases)
- Docker and deployment configurations
- JavaScript/CSS front-end assets
- Build scripts, MSBuild files, and NuGet configurations
- Test suites
- IIS/nginx web server configurations
