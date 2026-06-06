# Comprehensive Analysis of curriculumonline.ie JSON Scrapes

## SUMMARY STATISTICS

**Total JSON Files: 300**

### By Language
- English (EN): 171 files
- Irish/Gaeilge (GA): 129 files

### By Curriculum Level
- Junior Cycle: 150 files (50%)
- Navigation/Landing Pages: ~20 files
- Early Childhood: 7 files
- Primary: 2 files
- Senior Cycle: 0 scraped content pages (landing pages only)

### By Content Type
- Navigation/Landing Pages: ~30 files
- Curriculum Specifications: ~40 files
- Assessment Guidelines: ~20 files
- Student Work Examples/CBAs: ~60 files
- Support Materials: ~20 files
- Miscellaneous Content: ~130 files

---

## A. URL PATTERN ANALYSIS

### Root Level Navigation
```
https://www.curriculumonline.ie/
https://www.curriculumonline.ie/ga-ie/           (Irish version)
https://www.curriculumonline.ie/about/
https://www.curriculumonline.ie/contact/
https://www.curriculumonline.ie/clipboard/
```

### Early Childhood (Aistear)
**Curriculum Levels: Birth-6 years**
```
/early-childhood/
/early-childhood/aistear-2024/
/early-childhood/aistear-2009/
/early-childhood/principles-and-themes/
/early-childhood/guidelines-for-good-practice/
/early-childhood/support-materials-for-early-childhood/
/early-childhood/support-videos-for-early-childhood/

Bilingual versions: /ga-ie/early-childhood/*
```

### Primary School
**Curriculum Levels: Ages 5-12**
```
/primary/
/primary/the-primary-curriculum-framework/
/primary/curriculum-areas/
/primary/curriculum-areas/updated-arts-education/
/primary/curriculum-areas/updated-language-curriculum/
/primary/curriculum-areas/mathematics/
/primary/curriculum-areas/updated-science-technology-engineering-and-mathematics-(stem)-education/
/primary/curriculum-areas/updated-social-and-environmental-education/
/primary/curriculum-areas/updated-wellbeing/

NOTE: Only 2 primary files scraped (landing pages)
```

### Junior Cycle
**Curriculum Level: Ages 12-15 (3 years)**

**Main Navigation:**
```
/junior-cycle/
/junior-cycle/curriculum/
/junior-cycle/assessment/
/junior-cycle/junior-cycle-subjects/
/junior-cycle/junior-cycle-is-changing/
/junior-cycle/key-skills/
/junior-cycle/short-courses/
/junior-cycle/level-1-learning-programmes-(l1lps)/
/junior-cycle/level-2-learning-programmes/
```

**Subject Landing Pages (16 subjects):**
```
/junior-cycle/junior-cycle-subjects/{subject}/
```

**Subject Content Structure (per subject):**
```
/junior-cycle/junior-cycle-subjects/{subject}/
  ├─ overview-course/
  ├─ rationale/
  ├─ rationale/aim/
  ├─ expectations-for-students/
  ├─ statements-of-learning/
  ├─ assessment-and-reporting/
  ├─ assessment-guidelines/
  ├─ examples-of-student-work/
  │   ├─ examples-of-cba-1-[type]/
  │   ├─ examples-of-cba-2-[type]/
  │   ├─ support-materials-for-cba-2/
  │   ├─ examples-of-classroom-based-assessment-1/
  │   └─ [topic-specific]/
  ├─ {subject}-and-key-skills/
  ├─ continuity-and-progression/
  └─ [subject-specific pages]

For Gaeilge (Irish):
  ├─ t1-l1/ (Taught Irish Level 1)
  ├─ t2-l2/ (Taught Irish Level 2)
  ├─ Each level with separate:
      ├─ assessment-guidelines-(t1-and-t2)/
      ├─ assessment-guidelines-(t1-t2)/
      ├─ assessment-task-(l1-and-l2)/
      ├─ samplai-de-shaothar-scolairi/
      ├─ literature/
      └─ literature-lists/
```

### Senior Cycle
**Curriculum Level: Ages 16-18 (2-3 years)**

**Navigation Structure (Landing Pages Only - No Content):**
```
/senior-cycle/
/senior-cycle/curriculum/
/senior-cycle/senior-cycle-subjects/
/senior-cycle/assessment/
/senior-cycle/transition-year/
/senior-cycle/lca/
/senior-cycle/sphe/
```

**Senior Cycle Subjects (60+ subjects listed in navigation but NOT scraped):**
- Academic Track: Accounting, Agricultural Science, Ancient Greek, Applied Mathematics, Arabic, Art, Biology, Business, Chemistry, Classical Studies, Climate Action and Sustainable Development, Computer Science, Construction Studies, Design and Communication Graphics, Drama/Film/Theatre Studies, Economics, Engineering, English, French, Gaeilge, Geography, German, Hebrew Studies, History, Home Economics, Italian, Japanese, Latin, Lithuanian, Mandarin Chinese, Mathematics, Music, Physics, Physics and Chemistry, Polish, Politics and Society, Portuguese, Religious Education, Russian, Spanish, Technology

- Leaving Certificate Applied Programme (LCAP/LCA) modules (30+ options)
- Transition Year
- SPHE (Social Personal and Health Education)
- Level 1 & 2 Learning Programmes

---

## B. SUBJECT COVERAGE - JUNIOR CYCLE INVENTORY

### Subjects with Complete Coverage (Both Languages)

#### 1. **Gaeilge (Irish) - T1-L1 & T2-L2**
- **Type:** Language subject (Primary focus of Irish education)
- **Levels:** 
  - T1-L1 (Taught Irish, Level 1)
  - T2-L2 (Taught Irish, Level 2)
- **Available Resources:**
  - Course overviews (EN & GA)
  - Assessment guidelines (EN & GA) - UPDATED Nov 2024
  - Assessment tasks (EN & GA)
  - Expectations for students (EN & GA)
  - Student work samples (EN & GA)
  - Support materials for CBA-2 (EN & GA)
  - Literature lists (EN & GA)
  - Statements of learning (EN & GA)
  - Rationale & aims (EN & GA)
  - Continuity & progression (EN & GA)
  - Introduction to specifications (EN & GA)
  - Key skills integration (EN & GA)
  - CEFR appendices (EN & GA)
- **Files Count:** 44 files (22 EN + 22 GA)
- **Language Available:** Both EN and GA

#### 2. **Business Studies**
- **Type:** Vocational subject
- **Available Resources:**
  - Overview & course planning (EN & GA)
  - Rationale & aims (EN & GA)
  - Assessment guidelines (EN & GA)
  - Assessment & reporting details (EN & GA)
  - Classroom-based assessments:
    - CBA-1: Business in Action (evidence & examples)
    - CBA-2: Presentation/TCA (evidence & examples)
  - Student work examples (EN & GA)
  - Support materials for CBA-2 (EN & GA)
  - Expectations for students (EN & GA)
  - Key skills integration (EN & GA)
  - Statements of learning (EN & GA)
- **Files Count:** 25 files (noted: GA versions updated through 2025)
- **Language Available:** Both EN and GA

#### 3. **English**
- **Type:** Language/Literature subject
- **Available Resources:**
  - Course overview & planning (EN only)
  - Assessment & reporting (EN only)
  - Assessment task (EN only)
  - Student work examples (EN only):
    - Oral communication (2nd year)
    - Collection of texts examples
  - Rationale & aims (EN only)
  - Expectations for students (EN only)
  - Statements of learning (EN only)
  - Key skills integration (EN only)
  - Pre-2014 English syllabus (legacy)
- **Files Count:** 18 files (EN only)
- **Language Available:** English only

#### 4. **Engineering**
- **Type:** STEM subject
- **Available Resources:**
  - Course overview (EN & GA)
  - Rationale & aims (EN & GA)
  - Assessment guidelines (EN & GA)
  - CBA-2 themes (EN only)
  - Student work examples (EN only)
  - Expectations for students (EN & GA)
  - Key skills integration (EN & GA)
  - Continuity & progression (EN & GA)
  - Statements of learning (EN & GA)
- **Files Count:** 13 files
- **Language Available:** Both EN and GA

#### 5. **Applied Technology**
- **Type:** STEM subject
- **Available Resources:**
  - Course overview (EN & GA)
  - Rationale & aims (EN & GA)
  - Assessment & reporting (EN & GA)
  - Student work examples (EN only)
  - Expectations for students (EN & GA)
  - Key skills integration (EN & GA)
  - Continuity & progression (EN & GA)
  - Statements of learning (EN & GA)
- **Files Count:** 12 files
- **Language Available:** Both EN and GA

#### 6. **Graphics**
- **Type:** Technology/Art subject
- **Available Resources:**
  - Course overview (EN & GA)
  - Rationale (EN & GA)
  - Assessment & reporting (EN & GA)
  - CBA-2 domains (EN only)
  - Student work examples (EN only)
  - Expectations for students (EN & GA)
  - Key skills integration (EN & GA)
  - Continuity & progression (EN & GA)
  - Statements of learning (EN only)
- **Files Count:** 11 files
- **Language Available:** Both EN and GA

#### 7. **Geography**
- **Type:** Social science subject
- **Available Resources:**
  - Course overview (EN & GA)
  - Rationale & aims (EN & GA)
  - Assessment & reporting (EN & GA)
  - Expectations for students (EN & GA)
  - Key skills integration (EN & GA)
  - Progression & continuity (EN & GA)
  - Statements of learning (EN & GA)
- **Files Count:** 11 files
- **Language Available:** Both EN and GA

#### 8. **Classics**
- **Type:** Language/History subject
- **Available Resources:**
  - Course overview (EN & GA)
  - Rationale & aims (EN & GA)
  - Assessment & reporting (EN & GA)
  - Student work examples (CBA-1 work)
  - Expectations for students (EN & GA)
  - Key skills (EN & GA)
  - Statements of learning (EN & GA)
- **Files Count:** 10 files
- **Language Available:** Both EN and GA

### Subjects with Limited Coverage

- **Mathematics:** 1 file (CBA-2 examples only)
- **History:** Not in current scrape set (listed in navigation)
- **Home Economics:** Not in current scrape set
- **Jewish Studies:** Not in current scrape set
- **Modern Foreign Languages (MFL):** Not in current scrape set
- **Music:** Not in current scrape set
- **Religious Education:** Not in current scrape set
- **Science:** Not in current scrape set
- **Visual Art:** Not in current scrape set
- **Wood Technology:** Not in current scrape set

### Senior Cycle Status
- **Navigation Pages:** Yes (all subject listings)
- **Content Pages:** NO - Not yet scraped
- **Subjects Available:** 60+ subjects documented in navigation but no detailed specifications scraped
- **Expected Content:** Syllabi specifications, assessment guidelines, PDFs via getmedia links

---

## C. CONTENT TYPE CLASSIFICATION

### 1. **Navigation/Landing Pages (30 files)**
- Root homepage
- Section homepages (Early Childhood, Primary, Junior Cycle, Senior Cycle)
- About pages (EN & GA)
- Contact pages (EN & GA)
- Assessment info pages (EN & GA)
- Literacy & numeracy pages (EN & GA)
- Language-specific landing pages

### 2. **Curriculum Specifications (40 files)**
- Course overviews
- Rationale documents
- Aim statements
- Expectations for students
- Statements of learning
- Key skills integration pages

### 3. **Assessment Materials (20 files)**
- Assessment guidelines
- Assessment and reporting frameworks
- Assessment task descriptions
- CEFR references (for language subjects)
- Reasonable accommodations documents

### 4. **Classroom-Based Assessment (CBA) Resources (60+ files)**
- Examples of CBA-1 work (with evidence)
- Examples of CBA-2 work (with evidence)
- Support materials for CBAs
- CBA themes documentation
- Topic-specific work samples
- Student work samples with annotations

### 5. **Support Materials (20 files)**
- Planning guidance
- Continuity & progression documents
- Pedagogical approaches
- Inclusion guidance
- Teaching strategies

### 6. **Miscellaneous (130 files)**
- Editor tips/widget documentation
- Sitemap data
- Redirects
- Legacy content (1999 Primary Curriculum)
- Clipboard functionality
- Login pages

---

## D. SITEMAP ANALYSIS

### Sitemap Stats
- **File:** curriculumonline.ie_sitemap.xml.json
- **Size:** ~272.5 KB (indicates ~1000+ URLs)
- **Format:** XML converted to JSON with raw markdown

### URL Frequency Distribution (from sitemap excerpt)
- **Bilingual pages:** Every page available in both EN and GA-IE
- **Update frequency:** 
  - Root: Weekly (1.0 priority)
  - Section pages: Weekly (0.5 priority)
  - Subject pages: Weekly (0.5 priority)
  - Content deep pages: Weekly (0.5 priority)

### Patterns Observed
- Last modified dates range from 2023-09 to 2025-11
- Recent updates:
  - Gaeilge assessment guidelines: Nov 2024
  - Gaeilge literature lists: Apr 2025
  - English oral examples: Nov 2025
  - Engineering content: May 2025

### Missing from Scraped Set
- Senior Cycle subject content (landing pages present, details missing)
- Some Junior Cycle subject details
- Primary curriculum details (2 files only)
- PDF getmedia links (referenced but not captured)

---

## E. DUBLIN CORE & METADATA

### Consistent Metadata Fields
```json
{
  "language": "en" or "ga",
  "ogTitle": "{Page Title} | Curriculum Online",
  "ogDescription": "{Brief description}",
  "og:url": "https://www.curriculumonline.ie:443/{path}/",
  "ogImage": "{Image URL}",
  "description": "{Meta description}",
  "title": "{Page Title}",
  "twitter:site": "NCCAie",
  "twitter:card": "summary",
  "viewport": "width=device-width, initial-scale=1.0",
  "sourceURL": "https://www.curriculumonline.ie/{path}/",
  "statusCode": 200,
  "contentType": "text/html; charset=utf-8",
  "scrapeId": "{UUID}",
  "cachedAt": "{ISO timestamp}",
  "creditsUsed": 1
}
```

### Dublin Core Elements
- **Title:** Available in og:title
- **Description:** In ogDescription
- **Language:** Explicit language tag (en/ga)
- **URL:** sourceURL field
- **Type:** og:type = "website"
- **Creator:** NCCA (National Council for Curriculum and Assessment)

### Notable Missing Metadata
- No explicit dc:creator
- No dc:date fields
- No dc:subject (taxonomy)
- No dc:relation (cross-references between resources)

---

## F. CONTENT STRUCTURE OBSERVATIONS

### Markdown Format
All files use extracted markdown from HTML with:
- Links preserved as markdown `[text](url)`
- Headings preserved (# ## ### levels)
- Lists preserved (- and numbered)
- Bold/italic markdown syntax
- Images embedded as markdown `![alt](url)`

### File Structure Pattern
```
{
  "markdown": "Full page content",
  "metadata": {
    "og*": "OpenGraph tags",
    "twitter:*": "Twitter Card tags",
    "language": "en/ga",
    "sourceURL": "Original URL",
    "scrapeId": "Unique ID",
    "statusCode": 200
  }
}
```

### Content Characteristics
- Heavy navigation menus duplicated on each page
- Consistent header/footer structure
- Navigation shows all curriculum sections
- Mobile menu variant included
- Footer with NCCA links

---

## G. LANGUAGE DETECTION

### File Naming Convention
- **English:** Filename without `ga-ie` prefix
  - Example: `www.curriculumonline.ie_junior-cycle_junior-cycle-subjects_mathematics_examples-of-student-work_cba-2_.json`
  
- **Irish/Gaeilge:** Filename with `ga-ie` prefix
  - Example: `www.curriculumonline.ie_ga-ie_junior-cycle_junior-cycle-subjects_gaeilge_..._.json`

### Metadata Language Field
- **EN:** `"language": "en"`
- **GA:** `"language": "ga"`

### Content Language
- **EN files:** English content in markdown
- **GA files:** Irish/Gaeilge content in markdown (utf-8 encoded with Irish diacritics)

### Bilingual Coverage
- Early Childhood: 7 EN + 7 GA = 14 total
- Primary: 2 EN + minimal GA
- Junior Cycle:
  - Navigation: 15 EN + 15 GA
  - Gaeilge subject: 22 EN + 22 GA (completely bilingual)
  - Other subjects: Varies (60-80% bilingual)
- Senior Cycle: Navigation only (EN & GA)

---

## H. EXTRACTION PATTERNS FOR CRAWL4AI

### Pattern 1: Section Navigation
```
Pattern: /^(https?:\/\/)?www\.curriculumonline\.ie\/(ga-ie\/)?[a-z-]+\/?$/
Examples:
  - /early-childhood/
  - /primary/
  - /junior-cycle/
  - /senior-cycle/
  - /ga-ie/early-childhood/
```

### Pattern 2: Subject Pages
```
Pattern: /junior-cycle\/junior-cycle-subjects\/[a-z-]+\/?$/
Match: Allows extraction of all 16+ subjects
Example: /junior-cycle/junior-cycle-subjects/gaeilge/
```

### Pattern 3: Subject Deep Content
```
Pattern: /junior-cycle\/junior-cycle-subjects\/[a-z-]+\/(?:t[1-2]-[l1-2]\/)?[a-z0-9\-()]+\/?$/
Match: Captures multi-level subject specifications
Example: /junior-cycle/junior-cycle-subjects/gaeilge/t1-l1/course-overview/
```

### Pattern 4: Assessment Resources
```
Pattern: /(assessment-guidelines|examples-of-student-work|assessment-and-reporting|assessment-task)\/?$/
Match: Finds all assessment materials
```

### Pattern 5: CBA Examples
```
Pattern: /(examples-of-cba-[12]|support-material|evidence-of-learning)/
Match: Targets Classroom-Based Assessment resources
```

### Pattern 6: Bilingual Variants
```
Pattern: /(^|\/)(ga-ie)?\/(.*)/
Match: Captures both EN and GA versions of same content
```

---

## I. GAPS IDENTIFIED

### High Priority Gaps

1. **Senior Cycle Content (0% coverage)**
   - 60+ subjects documented but NOT scraped
   - No specifications, no assessment guidelines
   - Only landing pages captured
   - Estimated 300-500 missing pages

2. **Primary School Content (1% coverage)**
   - Only 2 landing pages captured
   - No curriculum area specifications
   - No support materials
   - Missing Primary Curriculum Framework content
   - Estimated 50-100 missing pages

3. **Junior Cycle Missing Subjects**
   - Mathematics (1 file only - CBA-2)
   - History (0 files)
   - Home Economics (0 files)
   - Jewish Studies (0 files)
   - Modern Foreign Languages (0 files)
   - Music (0 files)
   - Religious Education (0 files)
   - Science (0 files)
   - Visual Art (0 files)
   - Wood Technology (0 files)
   - Junior Certificate School Programme (0 files)
   - Estimated 150+ missing pages

### Medium Priority Gaps

4. **Short Courses** (14 courses documented, 0 files)
   - Coding, Digital Media Literacy, CSPE, Philosophy, etc.
   - Full specifications missing

5. **Level 1 & 2 Learning Programmes**
   - Only navigation pages
   - Detailed guidelines missing
   - Purpose, assessment, glossaries missing

6. **Assessment Cross-Section**
   - Some subjects missing assessment guidelines entirely
   - Gaps in English language assessment
   - Incomplete student work samples

### Low Priority Gaps

7. **PDF Resources**
   - Referenced via getmedia links
   - Not captured as separate files
   - Example: Business Level Certificate guidelines (identified in filename)

8. **Media Content**
   - Support videos mentioned but not captured
   - Images referenced but not extracted

9. **Transition Year & LCA**
   - Navigation present
   - Content specifications missing
   - ~25 LCA modules not covered

---

## J. RECOMMENDATIONS FOR DATA EXTRACTION

### Phase 1: Complete Junior Cycle (Priority)
**Action:** Crawl missing 10 subjects + fill gaps in existing 6
**Pattern:** `/junior-cycle/junior-cycle-subjects/[a-z-]+/`
**Estimated Pages:** 150-200
**Expected Files:** ~75-100 JSON files
**Timeline:** 1-2 weeks

### Phase 2: Add Primary Curriculum (High Priority)
**Action:** Extract primary curriculum framework and all 6 curriculum areas
**Pattern:** `/primary/curriculum-areas/` and `/primary/primary-curriculum-toolkit/`
**Estimated Pages:** 50-80
**Expected Files:** ~25-40 JSON files
**Timeline:** 1 week

### Phase 3: Complete Senior Cycle (High Priority)
**Action:** Crawl all 60+ subject specifications
**Pattern:** `/senior-cycle/senior-cycle-subjects/[a-z-]+/`
**Additional:** Crawl LCA, Transition Year, Level 1-2 programmes
**Estimated Pages:** 300-500
**Expected Files:** ~150-250 JSON files
**Timeline:** 2-3 weeks

### Phase 4: Fill Assessment Gaps (Medium Priority)
**Action:** Reprocess all subjects for complete assessment materials
**Pattern:** `/(assessment|examples|cba|guidelines)/`
**Timeline:** 1 week (automated)

### Crawl4AI Configuration Template
```yaml
crawler:
  urls:
    - base: "https://www.curriculumonline.ie"
      paths:
        # Junior Cycle - all subjects
        - "/junior-cycle/junior-cycle-subjects/*/.*"
        - "/ga-ie/junior-cycle/junior-cycle-subjects/*/.*"
        
        # Primary - all curriculum areas
        - "/primary/curriculum-areas/.*"
        - "/ga-ie/primary/curriculum-areas/.*"
        
        # Senior Cycle - all subjects
        - "/senior-cycle/senior-cycle-subjects/*/.*"
        - "/ga-ie/senior-cycle/senior-cycle-subjects/*/.*"
        
        # Learning programmes
        - "/junior-cycle/level-[12]-learning-programmes/.*"
        - "/senior-cycle/level-[12]-learning-programmes/.*"
        
        # Short courses
        - "/junior-cycle/short-courses/.*"
        - "/ga-ie/junior-cycle/short-courses/.*"
        
        # LCA modules
        - "/senior-cycle/lca/.*"
        - "/ga-ie/senior-cycle/lca/.*"
  
  extract:
    - field: "markdown"
    - field: "metadata.language"
    - field: "metadata.sourceURL"
    - field: "metadata.title"
    - field: "metadata.ogDescription"
  
  delay: 2  # seconds between requests
  concurrent: 3
  timeout: 30
```

---

## K. SUMMARY TABLE: JUNIOR CYCLE COVERAGE

| Subject | Files | EN | GA | Course | Assessment | CBAs | Student Work | Key Skills | Complete |
|---------|-------|----|----|--------|------------|------|--------------|------------|----------|
| Gaeilge (T1-L1/T2-L2) | 44 | Y | Y | Y | Y | Y | Y | Y | Yes |
| Business Studies | 25 | Y | Y | Y | Y | Y | Y | Y | Yes |
| Engineering | 13 | Y | Y | Y | Y | - | Y | Y | 85% |
| Applied Technology | 12 | Y | Y | Y | Y | - | Y | Y | 85% |
| Graphics | 11 | Y | Y | Y | Y | - | Y | Y | 85% |
| Geography | 11 | Y | Y | Y | Y | - | - | Y | 75% |
| English | 18 | Y | - | Y | Y | - | Y | Y | 70% |
| Classics | 10 | Y | Y | Y | Y | - | Y | Y | 80% |
| Mathematics | 1 | Y | - | - | - | Y | - | - | 15% |
| History | - | - | - | - | - | - | - | - | 0% |
| Home Economics | - | - | - | - | - | - | - | - | 0% |
| Jewish Studies | - | - | - | - | - | - | - | - | 0% |
| MFL | - | - | - | - | - | - | - | - | 0% |
| Music | - | - | - | - | - | - | - | - | 0% |
| Religious Education | - | - | - | - | - | - | - | - | 0% |
| Science | - | - | - | - | - | - | - | - | 0% |
| Visual Art | - | - | - | - | - | - | - | - | 0% |
| Wood Technology | - | - | - | - | - | - | - | - | 0% |
| JCSP | - | - | - | - | - | - | - | - | 0% |

**Overall Junior Cycle Coverage: ~50% (8 of 16 subjects substantially complete)**

---

## L. DATA QUALITY NOTES

### Strengths
1. Consistent metadata structure across all files
2. Complete bilingual coverage where implemented
3. Up-to-date (recent modifications through Nov 2025)
4. HTML well-structured for markdown extraction
5. Clear URL patterns for pattern-based extraction

### Weaknesses
1. Heavy navigation markup in every file (boilerplate bloat)
2. No machine-readable taxonomy or subject classification
3. PDF references not captured
4. Missing media content (images, videos)
5. Incomplete coverage (50% of content not scraped)

### Data Normalization Needs
1. Extract markdown from HTML to remove navigation boilerplate
2. Parse URL to identify curriculum level, subject, content type
3. Add explicit content type field based on URL patterns
4. Create subject-level indices
5. Link related resources (EN<->GA, assessment guidelines<->examples)

---

