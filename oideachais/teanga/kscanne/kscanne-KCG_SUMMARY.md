# KCG_SUMMARY: kscanne — Irish NLP Tools Repository

## What It Is
kscanne is Kevin Scannell's comprehensive collection of Irish language NLP tools, datasets, and linguistic resources. It spans grammatical analysis, spell-checking, machine translation (Irish↔English, Manx, Scottish Gaelic), dependency parsing, part-of-speech tagging, named entity recognition, sentiment analysis, OCR correction, diacritic restoration, dialect classification, and language modeling — all specifically built for or adapted to the Irish language.

## Why This Matters for Kings' College Galway
This is the single most concentrated collection of Irish-language NLP infrastructure available in open source. For the **teanga** (language) curriculum platform, kscanne provides production-ready tools for automated Irish text processing — grammar checking for student writing, dialect-aware content classification, OCR correction for digitising historical Irish manuscripts, and machine translation for bilingual educational materials. The datasets (Irish Dependency Treebank, UD_Irish-IDT, spelling errors corpus) are directly usable for evaluating and improving Celtic language AI models in the classroom.

## Key Patterns Preserved
- `gbb/README.md` — Master index of 25+ Irish NLP tasks and datasets (Giorraíonn BERT Bóthar benchmark)
- `gbb/classification/*/README.md` — Dataset READMEs for native speaker, author, gender, topic, dialect, and sentiment classification
- `gbb/translation/*/README.md` — Irish↔English, Irish↔Manx, Irish↔Scottish Gaelic machine translation datasets
- `gbb/proofing/*/README.md` — Grammar checking, mutation prediction, OCR correction, standardisation, diacritic restoration
- `gbb/tagging/*/README.md` — NER, code-switching detection, POS tagging, lemmatization
- `gbb/syntax/*/README.md` — Dependency and constituency parsing, chunking
- `gbb/generation/*/README.md` — Language modeling, question answering, conversational agents
- `gramadoir/API.md` — An Gramadóir grammar checker API documentation
- `treocht/API.md` — Teanglann/Treocht API documentation
- `UD_Irish-IDT/CONTRIBUTING.md` — Universal Dependencies contribution guide
- `cadhan.com/README.md` — Cadhan Aonair Irish text resources
- `ogham/README.md` — Ogham script tools

## Source Files
Full source code was removed on 2026-06-06. The original repositories are available at GitHub (e.g., github.com/kscanne). This skeleton preserves only the documentation to show the architecture and scope of Irish NLP tools surveyed.

## What Was Removed
- Python/Perl/C++ source code for all NLP tools
- Training data and model checkpoints (GBB datasets)
- Crúbadán web crawl corpora
- Hunspell Irish spelling dictionaries
- Universal Dependencies treebank data files
- Language model binaries and tokenizers
- Build scripts and Makefiles
- Web application sources (treocht, gramadoir, cadhan.com)
