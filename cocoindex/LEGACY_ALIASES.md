# LEGACY_ALIASES — cocoindex/

Per the
[`2026-07-17-pipeline-directory-consolidation-v1`](../../changes/2026-07-17-pipeline-directory-consolidation-v1/proposal.md)
openspec change. **All old flat-file paths remain importable via
deprecation shims for at least one release cycle.**

## Per-jurisdiction files (flat → subdirectory)

| Old | New |
|:--|:--|
| `cocoindex/european_nations_{alb,aut,bel,bgr,bih,che,cyp,cze,deu,dnk,esp,est,fin,fra,geo,grc,hrv,hun,isl,ita,lie,ltu,lux,lva,mda,mkd,mlt,mne,nld,nor,pol,prt,rou,srb,svk,svn,swe,tur,ukr,xkx}_education_embedding.py` | `cocoindex/european_nations/{albania,austria,belgium,bulgaria,bosnia_and_herzegovina,switzerland,cyprus,czechia,germany,denmark,spain,estonia,finland,france,georgia,greece,croatia,hungary,iceland,italy,liechtenstein,lithuania,luxembourg,latvia,moldova,north_macedonia,malta,montenegro,netherlands,norway,poland,portugal,romania,serbia,slovakia,slovenia,sweden,turkey,ukraine,kosovo}/education_embedding.py` |
| `cocoindex/commonwealth_{aus,can,ind,nga,nzl,zaf}_education_embedding.py` | `cocoindex/commonwealth/{australia,canada,india,nigeria,new_zealand,south_africa}/education_embedding.py` |
| `cocoindex/nigeria_education_embedding.py` | `cocoindex/commonwealth/nigeria/education_embedding.py` |
| `cocoindex/quebec_montreal_education_embedding.py` | `cocoindex/commonwealth/canada/provinces/quebec/montreal_education_embedding.py` |
| `cocoindex/canuint_embedding.py` | `cocoindex/british_isles/ireland/canuint_embedding.py` |
| `cocoindex/ireland_legal_embedding.py` | `cocoindex/british_isles/ireland/ireland_legal_embedding.py` |

## Cross-jurisdiction apps (flat → `_cross/`)

| Old | New |
|:--|:--|
| `cocoindex/european_nations_law_embedding.py` | `cocoindex/european_nations_cross/law_embedding.py` |
| `cocoindex/european_nations_medicine_embedding.py` | `cocoindex/european_nations_cross/medicine_embedding.py` |
| `cocoindex/european_nations_education_embedding.py` | `cocoindex/european_nations_cross/education_embedding.py` |
| `cocoindex/commonwealth_education_embedding.py` | `cocoindex/commonwealth_cross/education_embedding.py` |

## Cross-nation / purpose apps (flat → subject-specific subdir)

| Old | New |
|:--|:--|
| `cocoindex/mathematics_embedding.py` | `cocoindex/subjects/mathematics_embedding.py` |
| `cocoindex/chemistry_embedding.py` | `cocoindex/subjects/chemistry_embedding.py` |
| `cocoindex/english_embedding.py` | `cocoindex/subjects/english_embedding.py` |
| `cocoindex/geography_embedding.py` | `cocoindex/subjects/geography_embedding.py` |
| `cocoindex/computer_science_embedding.py` | `cocoindex/subjects/computer_science_embedding.py` |
| `cocoindex/history_embedding.py` | `cocoindex/subjects/history_embedding.py` |
| `cocoindex/applied_mathematics_embedding.py` | `cocoindex/subjects/applied_mathematics_embedding.py` |
| `cocoindex/cross_subject_competency_embedding.py` | `cocoindex/subjects/cross_subject_competency_embedding.py` |
| `cocoindex/gaeilge_embedding.py` | `cocoindex/celtic/gaeilge_embedding.py` |
| `cocoindex/celtic_curriculum_embedding.py` | `cocoindex/celtic/curriculum_embedding.py` |
| `cocoindex/celtic_multilingual.py` | `cocoindex/celtic/multilingual.py` |
| `cocoindex/ud_celtic_embedding.py` | `cocoindex/celtic/ud_celtic_embedding.py` |
| `cocoindex/gaois_embedding.py` | `cocoindex/celtic/gaois_embedding.py` |
| `cocoindex/mythology_embedding.py` | `cocoindex/celtic/mythology_embedding.py` |
| `cocoindex/artwork_embedding.py` | `cocoindex/media/artwork_embedding.py` |
| `cocoindex/cv_embedding.py` | `cocoindex/media/cv_embedding.py` |
| `cocoindex/apple_photos_chunks.py` | `cocoindex/media/apple_photos_chunks.py` |
| `cocoindex/apple_photos_geospatial.py` | `cocoindex/media/apple_photos_geospatial.py` |
| `cocoindex/apple_photos_metadata.py` | `cocoindex/media/apple_photos_metadata.py` |
| `cocoindex/ocr_aware_flow.py` | `cocoindex/media/ocr_aware_flow.py` |
| `cocoindex/heritage_embedding.py` | `cocoindex/portfolio/heritage_embedding.py` |
| `cocoindex/culture_heritage_embedding.py` | `cocoindex/portfolio/culture_heritage_embedding.py` |
| `cocoindex/multihop_search.py` | `cocoindex/knowledge_graph/multihop_search.py` |
| `cocoindex/terminology_linking.py` | `cocoindex/knowledge_graph/terminology_linking.py` |
| `cocoindex/youtube_kg_embedding.py` | `cocoindex/knowledge_graph/youtube_kg_embedding.py` |
| `cocoindex/file_graph.py` | `cocoindex/knowledge_graph/file_graph.py` |
| `cocoindex/leabharlann_flow.py` | `cocoindex/corpus/leabharlann_flow.py` |
| `cocoindex/leabharlann_embedding.py` | `cocoindex/corpus/leabharlann_embedding.py` |
| `cocoindex/root_pdfs_embedding.py` | `cocoindex/corpus/root_pdfs_embedding.py` |
| `cocoindex/local_documents_embedding.py` | `cocoindex/corpus/local_documents_embedding.py` |
| `cocoindex/government_circulars_embedding.py` | `cocoindex/corpus/government_circulars_embedding.py` |
| `cocoindex/university_embedding.py` | `cocoindex/corpus/university_embedding.py` |
| `cocoindex/duchas_embedding.py` | `cocoindex/corpus/duchas_embedding.py` |
| `cocoindex/unified_embedding.py` | `cocoindex/corpus/unified_embedding.py` |
| `cocoindex/eu_multilingual_alignment_embedding.py` | `cocoindex/european_union/eu_multilingual_alignment_embedding.py` |
| `cocoindex/european_union_official_embedding.py` | `cocoindex/european_union/official_embedding.py` |
| `cocoindex/americas_california_education_embedding.py` | `cocoindex/american_nations/united_states/california_education_embedding.py` |

## Infrastructure → infrastructure/

| Old | New |
|:--|:--|
| `cocoindex/codebase_indexing.py` | `cocoindex/infrastructure/codebase_indexing.py` |
| `cocoindex/api_indexing.py` | `cocoindex/infrastructure/api_indexing.py` |
| `cocoindex/config_indexing.py` | `cocoindex/infrastructure/config_indexing.py` |
| `cocoindex/filesystem_indexing.py` | `cocoindex/infrastructure/filesystem_indexing.py` |
| `cocoindex/storage_indexing.py` | `cocoindex/infrastructure/storage_indexing.py` |
| `cocoindex/agents_md.py` | `cocoindex/infrastructure/agents_md.py` |
| `cocoindex/agent_registry.py` | `cocoindex/infrastructure/agent_registry.py` |
| `cocoindex/upstream_api_surface.py` | `cocoindex/infrastructure/upstream_api_surface.py` |
| `cocoindex/upstream_blog_monitor.py` | `cocoindex/infrastructure/upstream_blog_monitor.py` |
| `cocoindex/arch_doc_cache.py` | `cocoindex/infrastructure/arch_doc_cache.py` |
| `cocoindex/cocoindex_v1_conformance.py` | `cocoindex/infrastructure/cocoindex_v1_conformance.py` |
| `cocoindex/academic_history_flow.py` | `cocoindex/infrastructure/academic_history_flow.py` |
| `cocoindex/docs_skills_consolidation.py` | `cocoindex/infrastructure/docs_skills_consolidation.py` |

## Shared utilities → `_shared/`

| Old | New |
|:--|:--|
| `cocoindex/_lifespan.py` | `cocoindex/_shared/_lifespan.py` |
| `cocoindex/languages.py` | `cocoindex/_shared/languages.py` |
| `cocoindex/reranker.py` | `cocoindex/_shared/reranker.py` |
| `cocoindex/caighdean_standardize.py` | `cocoindex/_shared/caighdean_standardize.py` |
| `cocoindex/repo_type_detector.py` | `cocoindex/_shared/repo_type_detector.py` |
| `cocoindex/repo_embedding.py` | `cocoindex/_shared/repo_embedding.py` |
| `cocoindex/cli.py` | `cocoindex/_shared/cli.py` |

## Irish law sub-tree

| Old | New |
|:--|:--|
| `cocoindex/ie_law_courts.py` | `cocoindex/british_isles/ireland/ie_law_courts.py` |
| `cocoindex/ie_law_court_rules.py` | `cocoindex/british_isles/ireland/ie_law_court_rules.py` |
| `cocoindex/ie_law_judgements.py` | `cocoindex/british_isles/ireland/ie_law_judgements.py` |
| `cocoindex/ie_law_legal_aid.py` | `cocoindex/british_isles/ireland/ie_law_legal_aid.py` |
| `cocoindex/ie_law_piab.py` | `cocoindex/british_isles/ireland/ie_law_piab.py` |