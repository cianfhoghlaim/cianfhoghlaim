# LEGACY_ALIASES — cocoindex/

Per the
[`2026-07-17-pipeline-directory-consolidation-v1`](../../changes/2026-07-17-pipeline-directory-consolidation-v1/proposal.md)
openspec change. **All old flat-file paths remain importable via
deprecation shims for at least one release cycle.**

## Per-jurisdiction files (flat → subdirectory)

| Old | New |
|:--|:--|
| `cocoindex/european_nations_{alb,aut,bel,bgr,bih,che,cyp,cze,deu,dnk,esp,est,fin,fra,geo,grc,hrv,hun,isl,ita,lie,ltu,lux,lva,mda,mkd,mlt,mne,nld,nor,pol,prt,rou,srb,svk,svn,swe,tur,ukr,xkx}_education_embedding.py` | `cocoindex_flows/european_nations/{albania,austria,belgium,bulgaria,bosnia_and_herzegovina,switzerland,cyprus,czechia,germany,denmark,spain,estonia,finland,france,georgia,greece,croatia,hungary,iceland,italy,liechtenstein,lithuania,luxembourg,latvia,moldova,north_macedonia,malta,montenegro,netherlands,norway,poland,portugal,romania,serbia,slovakia,slovenia,sweden,turkey,ukraine,kosovo}/education_embedding.py` |
| `cocoindex/commonwealth_{aus,can,ind,nga,nzl,zaf}_education_embedding.py` | `cocoindex_flows/commonwealth/{australia,canada,india,nigeria,new_zealand,south_africa}/education_embedding.py` |
| `cocoindex/nigeria_education_embedding.py` | `cocoindex_flows/commonwealth/nigeria/education_embedding.py` |
| `cocoindex/quebec_montreal_education_embedding.py` | `cocoindex_flows/commonwealth/canada/provinces/quebec/montreal_education_embedding.py` |
| `cocoindex/canuint_embedding.py` | `cocoindex_flows/british_isles/ireland/canuint_embedding.py` |
| `cocoindex/ireland_legal_embedding.py` | `cocoindex_flows/british_isles/ireland/ireland_legal_embedding.py` |

## Cross-jurisdiction apps (flat → `_cross/`)

| Old | New |
|:--|:--|
| `cocoindex/european_nations_law_embedding.py` | `cocoindex_flows/european_nations_cross/law_embedding.py` |
| `cocoindex/european_nations_medicine_embedding.py` | `cocoindex_flows/european_nations_cross/medicine_embedding.py` |
| `cocoindex/european_nations_education_embedding.py` | `cocoindex_flows/european_nations_cross/education_embedding.py` |
| `cocoindex/commonwealth_education_embedding.py` | `cocoindex_flows/commonwealth_cross/education_embedding.py` |

## Cross-nation / purpose apps (flat → subject-specific subdir)

| Old | New |
|:--|:--|
| `cocoindex/mathematics_embedding.py` | `cocoindex_flows/subjects/mathematics_embedding.py` |
| `cocoindex/chemistry_embedding.py` | `cocoindex_flows/subjects/chemistry_embedding.py` |
| `cocoindex/english_embedding.py` | `cocoindex_flows/subjects/english_embedding.py` |
| `cocoindex/geography_embedding.py` | `cocoindex_flows/subjects/geography_embedding.py` |
| `cocoindex/computer_science_embedding.py` | `cocoindex_flows/subjects/computer_science_embedding.py` |
| `cocoindex/history_embedding.py` | `cocoindex_flows/subjects/history_embedding.py` |
| `cocoindex/applied_mathematics_embedding.py` | `cocoindex_flows/subjects/applied_mathematics_embedding.py` |
| `cocoindex/cross_subject_competency_embedding.py` | `cocoindex_flows/subjects/cross_subject_competency_embedding.py` |
| `cocoindex/gaeilge_embedding.py` | `cocoindex_flows/celtic/gaeilge_embedding.py` |
| `cocoindex/celtic_curriculum_embedding.py` | `cocoindex_flows/celtic/curriculum_embedding.py` |
| `cocoindex/celtic_multilingual.py` | `cocoindex_flows/celtic/multilingual.py` |
| `cocoindex/ud_celtic_embedding.py` | `cocoindex_flows/celtic/ud_celtic_embedding.py` |
| `cocoindex/gaois_embedding.py` | `cocoindex_flows/celtic/gaois_embedding.py` |
| `cocoindex/mythology_embedding.py` | `cocoindex_flows/celtic/mythology_embedding.py` |
| `cocoindex/artwork_embedding.py` | `cocoindex_flows/media/artwork_embedding.py` |
| `cocoindex/cv_embedding.py` | `cocoindex_flows/media/cv_embedding.py` |
| `cocoindex/apple_photos_chunks.py` | `cocoindex_flows/media/apple_photos_chunks.py` |
| `cocoindex/apple_photos_geospatial.py` | `cocoindex_flows/media/apple_photos_geospatial.py` |
| `cocoindex/apple_photos_metadata.py` | `cocoindex_flows/media/apple_photos_metadata.py` |
| `cocoindex/ocr_aware_flow.py` | `cocoindex_flows/media/ocr_aware_flow.py` |
| `cocoindex/heritage_embedding.py` | `cocoindex_flows/portfolio/heritage_embedding.py` |
| `cocoindex/culture_heritage_embedding.py` | `cocoindex_flows/portfolio/culture_heritage_embedding.py` |
| `cocoindex/multihop_search.py` | `cocoindex_flows/knowledge_graph/multihop_search.py` |
| `cocoindex/terminology_linking.py` | `cocoindex_flows/knowledge_graph/terminology_linking.py` |
| `cocoindex/youtube_kg_embedding.py` | `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py` |
| `cocoindex/file_graph.py` | `cocoindex_flows/knowledge_graph/file_graph.py` |
| `cocoindex/leabharlann_flow.py` | `cocoindex_flows/corpus/leabharlann_flow.py` |
| `cocoindex/leabharlann_embedding.py` | `cocoindex_flows/corpus/leabharlann_embedding.py` |
| `cocoindex/root_pdfs_embedding.py` | `cocoindex_flows/corpus/root_pdfs_embedding.py` |
| `cocoindex/local_documents_embedding.py` | `cocoindex_flows/corpus/local_documents_embedding.py` |
| `cocoindex/government_circulars_embedding.py` | `cocoindex_flows/corpus/government_circulars_embedding.py` |
| `cocoindex/university_embedding.py` | `cocoindex_flows/corpus/university_embedding.py` |
| `cocoindex/duchas_embedding.py` | `cocoindex_flows/corpus/duchas_embedding.py` |
| `cocoindex/unified_embedding.py` | `cocoindex_flows/corpus/unified_embedding.py` |
| `cocoindex/eu_multilingual_alignment_embedding.py` | `cocoindex_flows/european_union/eu_multilingual_alignment_embedding.py` |
| `cocoindex/european_union_official_embedding.py` | `cocoindex_flows/european_union/official_embedding.py` |
| `cocoindex/americas_california_education_embedding.py` | `cocoindex_flows/american_nations/united_states/california_education_embedding.py` |

## Infrastructure → infrastructure/

| Old | New |
|:--|:--|
| `cocoindex/codebase_indexing.py` | `cocoindex_flows/infrastructure/codebase_indexing.py` |
| `cocoindex/api_indexing.py` | `cocoindex_flows/infrastructure/api_indexing.py` |
| `cocoindex/config_indexing.py` | `cocoindex_flows/infrastructure/config_indexing.py` |
| `cocoindex/filesystem_indexing.py` | `cocoindex_flows/infrastructure/filesystem_indexing.py` |
| `cocoindex/storage_indexing.py` | `cocoindex_flows/infrastructure/storage_indexing.py` |
| `cocoindex/agents_md.py` | `cocoindex_flows/infrastructure/agents_md.py` |
| `cocoindex/agent_registry.py` | `cocoindex_flows/infrastructure/agent_registry.py` |
| `cocoindex/upstream_api_surface.py` | `cocoindex_flows/infrastructure/upstream_api_surface.py` |
| `cocoindex/upstream_blog_monitor.py` | `cocoindex_flows/infrastructure/upstream_blog_monitor.py` |
| `cocoindex/arch_doc_cache.py` | `cocoindex_flows/infrastructure/arch_doc_cache.py` |
| `cocoindex/cocoindex_v1_conformance.py` | `cocoindex_flows/infrastructure/cocoindex_v1_conformance.py` |
| `cocoindex/academic_history_flow.py` | `cocoindex_flows/infrastructure/academic_history_flow.py` |
| `cocoindex/docs_skills_consolidation.py` | `cocoindex_flows/infrastructure/docs_skills_consolidation.py` |

## Shared utilities → `_shared/`

| Old | New |
|:--|:--|
| `cocoindex/_lifespan.py` | `cocoindex_flows/_shared/_lifespan.py` |
| `cocoindex/languages.py` | `cocoindex_flows/_shared/languages.py` |
| `cocoindex/reranker.py` | `cocoindex_flows/_shared/reranker.py` |
| `cocoindex/caighdean_standardize.py` | `cocoindex_flows/_shared/caighdean_standardize.py` |
| `cocoindex/repo_type_detector.py` | `cocoindex_flows/_shared/repo_type_detector.py` |
| `cocoindex/repo_embedding.py` | `cocoindex_flows/_shared/repo_embedding.py` |
| `cocoindex/cli.py` | `cocoindex_flows/_shared/cli.py` |

## Irish law sub-tree

| Old | New |
|:--|:--|
| `cocoindex/ie_law_courts.py` | `cocoindex_flows/british_isles/ireland/ie_law_courts.py` |
| `cocoindex/ie_law_court_rules.py` | `cocoindex_flows/british_isles/ireland/ie_law_court_rules.py` |
| `cocoindex/ie_law_judgements.py` | `cocoindex_flows/british_isles/ireland/ie_law_judgements.py` |
| `cocoindex/ie_law_legal_aid.py` | `cocoindex_flows/british_isles/ireland/ie_law_legal_aid.py` |
| `cocoindex/ie_law_piab.py` | `cocoindex_flows/british_isles/ireland/ie_law_piab.py` |