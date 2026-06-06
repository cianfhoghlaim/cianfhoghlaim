# Curriculum Online (curriculumonline.ie) Data Collection

## Overview

This directory contains 300 JSON files extracted from the National Council for Curriculum and Assessment (NCCA) website [curriculumonline.ie](https://www.curriculumonline.ie), providing comprehensive documentation of Irish educational curricula across multiple educational levels.

## Collection Metadata

- **Source:** https://www.curriculumonline.ie
- **Scrape Date:** 2025-11-26
- **Total Files:** 300 JSON files
- **Total Size:** ~150-200 MB
- **Languages:** English (EN) and Irish/Gaeilge (GA)
- **Coverage:** ~50% of available content
- **Update Frequency:** Weekly (per sitemap)
- **Last Updates:** Through November 2025

## File Organization

```
/Users/cliste/dev/bonneagar/hackathon/data/flows/gaeilge/data/websites/curriculumonline.ie/
├── Documentation Files (in parent directory):
│   ├── CURRICULUMONLINE_ANALYSIS.md          (Main comprehensive analysis)
│   ├── FILE_INVENTORY.md                      (Detailed file listings)
│   └── README_CURRICULUMONLINE.md            (This file)
│
└── JSON Files (300 total):
    ├── Early Childhood (14 files)
    ├── Primary School (2 files)
    ├── Junior Cycle (150 files)
    │   ├── Gaeilge (44)
    │   ├── Business Studies (25)
    │   ├── Engineering (13)
    │   ├── Applied Technology (12)
    │   ├── Graphics (11)
    │   ├── Geography (11)
    │   ├── English (18)
    │   ├── Classics (10)
    │   └── Mathematics (1)
    ├── Navigation & Landing Pages (30 files)
    ├── Sitemap (1 file)
    └── Miscellaneous (104 files)
```

## Content Structure

### By Educational Level

#### 1. Early Childhood (Aistear Framework)
- **Age Range:** Birth to 6 years
- **Files:** 14 (EN & GA pairs)
- **Coverage:** Complete navigation and core materials
- **Resources:**
  - Aistear 2024 updated framework
  - Aistear 2009 (legacy)
  - Principles and Themes
  - Guidelines for Good Practice
  - Support materials and videos

#### 2. Primary School
- **Age Range:** 5-12 years
- **Files:** 2 (landing pages only)
- **Coverage:** Minimal (needs expansion)
- **Note:** Recently redeveloped (2025) - content not yet fully scraped

#### 3. Junior Cycle
- **Age Range:** 12-15 years (3 years)
- **Files:** 150 (50% of total scrape)
- **Coverage:** ~50% of subjects (8 of 16)
- **Complete Subjects:**
  - Gaeilge (Irish) - Both T1-L1 and T2-L2 with full documentation
  - Business Studies - Comprehensive with CBAs
  - Engineering, Applied Technology, Graphics, Geography, Classics (80-85% coverage)
  - English (EN only, 70% coverage)
- **Missing Subjects (0 coverage):**
  - History, Home Economics, Jewish Studies, Modern Foreign Languages, Music, Religious Education, Science, Visual Art, Wood Technology, Junior Certificate School Programme

#### 4. Senior Cycle
- **Age Range:** 16-18 years (2-3 years)
- **Files:** 0 content files (landing pages only)
- **Subjects Documented:** 60+ subjects in navigation
- **Status:** NOT YET SCRAPED
- **Coverage Includes:**
  - Academic subjects (40+)
  - Leaving Certificate Applied (LCA) modules (30+)
  - Transition Year
  - Leaving Certificate Vocational Programme (LCVP)
  - Special programmes

### By Language

- **English:** 171 files (57%)
- **Irish/Gaeilge:** 129 files (43%)
- **Bilingual Coverage:** 
  - Where implemented, every page has EN and GA versions
  - Gaeilge subject fully bilingual
  - Business Studies fully bilingual
  - Most other subjects 60-80% bilingual

## Data Format

### JSON Structure
```json
{
  "markdown": "Extracted page content in markdown format",
  "metadata": {
    "language": "en" | "ga",
    "sourceURL": "https://www.curriculumonline.ie/...",
    "title": "Page title",
    "ogTitle": "OpenGraph title",
    "ogDescription": "Short description",
    "ogImage": "Image URL",
    "statusCode": 200,
    "contentType": "text/html; charset=utf-8",
    "scrapeId": "UUID",
    "cacheState": "hit" | "miss",
    "cachedAt": "ISO-8601 timestamp"
  }
}
```

### Markdown Content
- Extracted from HTML
- Preserves structure (headings, lists, links)
- Images embedded as markdown
- Heavy navigation menus included (boilerplate)
- Suitable for text processing and NLP tasks

## Key Findings

### Strengths
1. **Consistent Structure:** All files follow standard JSON format
2. **Bilingual:** Complete English and Irish versions where implemented
3. **Well-Maintained:** Regular updates (last modified Nov 2025)
4. **Comprehensive Navigation:** All curriculum sections documented
5. **Assessment Focus:** Rich examples of student work and CBAs
6. **Clear Metadata:** OpenGraph and Twitter metadata present

### Weaknesses
1. **Incomplete Coverage:** Only 50% of content scraped
2. **Missing Subjects:** 10 of 16 Junior Cycle subjects not included
3. **Senior Cycle:** Completely missing (0 content files)
4. **Heavy Markup:** Navigation boilerplate duplicated on every page
5. **PDF References:** Links to PDFs not captured as files
6. **No Taxonomy:** No explicit subject classification in metadata

### Data Quality Issues
- URL-encoded spaces in some filenames (assessment%20task)
- Duplicate variants with UUID suffixes
- Large navigation sections on every page (~50% of content)
- No explicit content type field

## Use Cases

### Ideal For:
1. **Text Analysis:** Irish language curriculum documentation
2. **Bilingual Studies:** English-Irish paired content
3. **Education Research:** Assessment practices, learning outcomes
4. **Knowledge Extraction:** Curriculum specifications and frameworks
5. **LLM Training:** Educational content, structured curriculum data
6. **Search Indexing:** Complete educational resource database

### Recommended Preprocessing:
1. Remove navigation boilerplate (consistent menus)
2. Parse URL to extract curriculum level, subject, content type
3. Link EN and GA versions with shared metadata
4. Extract assessment examples as separate entities
5. Create subject-level indices
6. Add explicit content type field

## Notable Content

### High Value Files
- **Gaeilge Specifications:** Complete T1-L1 and T2-L2 with assessment guidelines (Nov 2024 update)
- **Business Studies:** Full documentation including CBA-1 (Business in Action) and CBA-2 (Presentation)
- **Engineering & Applied Technology:** Modern STEM curricula with practical assessment
- **Student Work Samples:** Real examples of CBA submissions with annotations

### Missing High Value Content
- **Senior Cycle Specifications:** All 60+ subjects (estimated 300-500 missing pages)
- **Primary Curriculum Framework:** Newly redeveloped (2025), not yet scraped
- **Short Courses:** 14 courses listed but content not captured
- **Learning Programmes:** Level 1 & 2 frameworks missing detailed content

## Extraction Recommendations

### Priority 1: Expand Junior Cycle
- Add 10 missing subjects (~150-200 pages)
- Complete assessment materials for all subjects
- Estimated effort: 1-2 weeks

### Priority 2: Add Primary School
- Extract all 6 curriculum areas
- Primary Curriculum Framework
- Support materials and toolkits
- Estimated effort: 1 week

### Priority 3: Add Senior Cycle
- All 60+ subject specifications
- LCA modules and frameworks
- Transition Year guidance
- Estimated effort: 2-3 weeks

### Total Expansion Potential
- Current: 300 files
- With missing content: ~700-1000 files
- Provides near-complete Irish curriculum documentation

## Crawl4AI Configuration

For expanding this collection, use patterns like:

```yaml
urls:
  - base: "https://www.curriculumonline.ie"
    paths:
      # Junior Cycle all subjects
      - "/junior-cycle/junior-cycle-subjects/[a-z-]+/.*"
      - "/ga-ie/junior-cycle/junior-cycle-subjects/[a-z-]+/.*"
      
      # Primary curriculum areas
      - "/primary/curriculum-areas/.*"
      - "/ga-ie/primary/curriculum-areas/.*"
      
      # Senior Cycle subjects
      - "/senior-cycle/senior-cycle-subjects/[a-z-]+/.*"
      - "/ga-ie/senior-cycle/senior-cycle-subjects/[a-z-]+/.*"
      
      # Learning programmes
      - "/junior-cycle/level-[12]-learning-programmes/.*"
      - "/senior-cycle/level-[12]-learning-programmes/.*"
      
      # Short courses
      - "/junior-cycle/short-courses/.*"
      - "/ga-ie/junior-cycle/short-courses/.*"
```

## Related Documentation

1. **CURRICULUMONLINE_ANALYSIS.md** - Comprehensive 700-line analysis including:
   - URL patterns and hierarchies
   - Subject coverage inventory
   - Content type classification
   - Metadata analysis
   - Language detection
   - Gaps and recommendations

2. **FILE_INVENTORY.md** - Detailed file listings with:
   - Complete file paths
   - Subject-by-subject breakdown
   - URL mappings
   - Data quality notes

## References

- **NCCA Website:** https://www.curriculumonline.ie
- **About NCCA:** https://ncca.ie/en/about-ncca/about-us/
- **Curriculum Framework:** https://ncca.ie/en/

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-02 | Initial analysis of 300 files |

## License & Attribution

- **Source:** National Council for Curriculum and Assessment (NCCA)
- **Attribution:** Curriculum Online (curriculumonline.ie)
- **Use:** Educational, research, non-commercial purposes
- **Access:** Publicly available content

---

**Last Updated:** 2025-12-02  
**Files Analyzed:** 300 JSON  
**Analysis Status:** Complete  
