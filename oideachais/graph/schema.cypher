// ============================================================================
// Memgraph Schema for Irish Curriculum Knowledge Graph
// ============================================================================
// This schema defines the temporal knowledge graph structure for:
// - Curriculum hierarchy (Subject -> Strand -> Unit -> Learning Outcome)
// - Document relationships (Curriculum docs, Exam papers, Insights)
// - Generated content (Questions, Vocabulary, Images)
// - Temporal versioning for tracking curriculum changes by year
// ============================================================================

// ============================================================================
// CONSTRAINTS (Ensure Data Integrity)
// ============================================================================

// Subject constraints
CREATE CONSTRAINT ON (s:Subject) ASSERT s.code IS UNIQUE;
CREATE CONSTRAINT ON (s:Subject) ASSERT EXISTS (s.code);
CREATE CONSTRAINT ON (s:Subject) ASSERT EXISTS (s.name_en);

// Strand constraints
CREATE CONSTRAINT ON (st:Strand) ASSERT st.id IS UNIQUE;
CREATE CONSTRAINT ON (st:Strand) ASSERT EXISTS (st.id);

// Strand Unit constraints
CREATE CONSTRAINT ON (su:StrandUnit) ASSERT su.id IS UNIQUE;
CREATE CONSTRAINT ON (su:StrandUnit) ASSERT EXISTS (su.id);

// Learning Outcome constraints
CREATE CONSTRAINT ON (lo:LearningOutcome) ASSERT lo.code IS UNIQUE;
CREATE CONSTRAINT ON (lo:LearningOutcome) ASSERT EXISTS (lo.code);

// Document constraints
CREATE CONSTRAINT ON (d:Document) ASSERT d.id IS UNIQUE;
CREATE CONSTRAINT ON (d:Document) ASSERT EXISTS (d.id);

// Question constraints
CREATE CONSTRAINT ON (q:Question) ASSERT q.id IS UNIQUE;
CREATE CONSTRAINT ON (q:Question) ASSERT EXISTS (q.id);

// Examiner Insight constraints
CREATE CONSTRAINT ON (ei:ExaminerInsight) ASSERT ei.id IS UNIQUE;

// Vocabulary Card constraints
CREATE CONSTRAINT ON (vc:VocabularyCard) ASSERT vc.id IS UNIQUE;

// Visual Asset constraints
CREATE CONSTRAINT ON (va:VisualAsset) ASSERT va.id IS UNIQUE;

// ============================================================================
// INDEXES (Query Performance)
// ============================================================================

// Subject indexes
CREATE INDEX ON :Subject(education_level);
CREATE INDEX ON :Subject(name_en);
CREATE INDEX ON :Subject(name_ga);

// Strand indexes
CREATE INDEX ON :Strand(name_en);
CREATE INDEX ON :Strand(subject_code);

// Learning Outcome indexes
CREATE INDEX ON :LearningOutcome(difficulty_level);
CREATE INDEX ON :LearningOutcome(curriculum_year);

// Document indexes
CREATE INDEX ON :Document(document_type);
CREATE INDEX ON :Document(education_level);
CREATE INDEX ON :Document(subject);
CREATE INDEX ON :Document(year);

// Question indexes
CREATE INDEX ON :Question(question_type);
CREATE INDEX ON :Question(difficulty);
CREATE INDEX ON :Question(education_level);
CREATE INDEX ON :Question(subject);

// Examiner Insight indexes
CREATE INDEX ON :ExaminerInsight(exam_year);
CREATE INDEX ON :ExaminerInsight(question_number);

// Temporal indexes for change tracking
CREATE INDEX ON :Subject(valid_from);
CREATE INDEX ON :LearningOutcome(valid_from);
CREATE INDEX ON :Document(created_at);

// ============================================================================
// NODE DEFINITIONS (with sample property types)
// ============================================================================

// Subject Node - Top level curriculum subject
// Properties:
//   code: string (e.g., "JC_IRISH", "LC_MATHS")
//   name_en: string
//   name_ga: string
//   education_level: string ("junior_cycle", "leaving_cert", "primary")
//   syllabus_url: string
//   valid_from: datetime
//   valid_to: datetime (null if current)

// Strand Node - Major curriculum strand
// Properties:
//   id: string (e.g., "JC_IRISH_STRAND_1")
//   subject_code: string (FK to Subject.code)
//   name_en: string
//   name_ga: string
//   description: string
//   sequence: integer

// StrandUnit Node - Sub-unit within a strand
// Properties:
//   id: string (e.g., "JC_IRISH_STRAND_1_UNIT_1")
//   strand_id: string (FK to Strand.id)
//   name_en: string
//   name_ga: string
//   description: string
//   sequence: integer

// LearningOutcome Node - Specific learning outcome
// Properties:
//   code: string (e.g., "JC_IRISH_LO_1.1")
//   strand_unit_id: string
//   description_en: string
//   description_ga: string
//   difficulty_level: string ("foundation", "ordinary", "higher")
//   curriculum_year: integer (year curriculum was introduced)
//   key_skills: list[string]
//   valid_from: datetime
//   valid_to: datetime

// Document Node - Curriculum document (PDF, specification)
// Properties:
//   id: string (UUID)
//   title: string
//   document_type: string ("specification", "exam_paper", "marking_scheme", "examiner_report")
//   education_level: string
//   subject: string
//   year: integer
//   source_url: string
//   pdf_storage_key: string
//   lancedb_table: string
//   chunk_count: integer
//   created_at: datetime

// Question Node - Generated or extracted question
// Properties:
//   id: string (UUID)
//   question_text_en: string
//   question_text_ga: string
//   question_type: string ("multiple_choice", "short_answer", "essay", "cloze")
//   difficulty: string ("easy", "medium", "hard")
//   education_level: string
//   subject: string
//   marking_scheme: string
//   max_marks: integer
//   generated_at: datetime
//   model_used: string

// ExaminerInsight Node - Insight from examiner report
// Properties:
//   id: string (UUID)
//   exam_year: integer
//   question_number: string
//   insight_type: string ("common_error", "best_practice", "tip")
//   content_en: string
//   content_ga: string
//   relevance_score: float

// VocabularyCard Node - Vocabulary learning card
// Properties:
//   id: string (UUID)
//   term_en: string
//   term_ga: string
//   definition_en: string
//   definition_ga: string
//   part_of_speech: string
//   example_sentence_en: string
//   example_sentence_ga: string
//   difficulty: string
//   created_at: datetime

// VisualAsset Node - Generated visual content
// Properties:
//   id: string (UUID)
//   visual_type: string ("diagram", "chart", "illustration", "concept_map")
//   title: string
//   description: string
//   storage_key: string
//   prompt_used: string
//   generated_at: datetime

// ============================================================================
// RELATIONSHIP DEFINITIONS (with temporal properties)
// ============================================================================

// Curriculum Hierarchy
// (:Subject)-[:HAS_STRAND {valid_from, valid_to, sequence}]->(:Strand)
// (:Strand)-[:HAS_UNIT {valid_from, valid_to, sequence}]->(:StrandUnit)
// (:StrandUnit)-[:HAS_OUTCOME {valid_from, valid_to, sequence}]->(:LearningOutcome)

// Document Relationships
// (:Document)-[:COVERS_SUBJECT {primary: boolean}]->(:Subject)
// (:Document)-[:ADDRESSES_OUTCOME {relevance_score, section}]->(:LearningOutcome)
// (:Document)-[:SUPERSEDES {effective_date}]->(:Document)

// Question Relationships
// (:Question)-[:TESTS_OUTCOME {alignment_score}]->(:LearningOutcome)
// (:Question)-[:DERIVED_FROM {extraction_method}]->(:Document)
// (:Question)-[:HAS_INSIGHT]->(:ExaminerInsight)

// Examiner Insight Relationships
// (:ExaminerInsight)-[:REPORTED_IN {exam_year}]->(:Document)
// (:ExaminerInsight)-[:RELATES_TO_OUTCOME]->(:LearningOutcome)

// Vocabulary Relationships
// (:VocabularyCard)-[:TEACHES_FOR]->(:LearningOutcome)
// (:VocabularyCard)-[:APPEARS_IN]->(:Document)

// Visual Asset Relationships
// (:VisualAsset)-[:ILLUSTRATES]->(:LearningOutcome)
// (:VisualAsset)-[:ACCOMPANIES]->(:Question)

// Cross-references
// (:LearningOutcome)-[:PREREQUISITE_OF]->(:LearningOutcome)
// (:LearningOutcome)-[:RELATED_TO {similarity_score}]->(:LearningOutcome)

// ============================================================================
// SAMPLE DATA CREATION PROCEDURES
// ============================================================================

// Create Subject with temporal tracking
// CALL create_subject('JC_IRISH', 'Irish', 'Gaeilge', 'junior_cycle', datetime())

// Track curriculum change
// CALL update_learning_outcome('JC_IRISH_LO_1.1', {description_en: 'Updated description'}, datetime())

// ============================================================================
// MAGE ALGORITHM HINTS
// ============================================================================

// PageRank for identifying important learning outcomes
// CALL pagerank.get() YIELD node, rank WHERE node:LearningOutcome RETURN node.code, rank ORDER BY rank DESC

// Community detection for clustering related topics
// CALL community_detection.louvain() YIELD node, community_id WHERE node:LearningOutcome RETURN community_id, collect(node.code)

// Shortest path for prerequisite chains
// MATCH p = shortestPath((lo1:LearningOutcome {code: 'JC_IRISH_LO_1.1'})-[:PREREQUISITE_OF*]-(lo2:LearningOutcome {code: 'JC_IRISH_LO_3.5'})) RETURN p

// Temporal queries for curriculum changes
// MATCH (lo:LearningOutcome) WHERE lo.valid_from >= datetime('2022-01-01') AND lo.valid_to IS NULL RETURN lo

// ============================================================================
// INITIALIZATION QUERIES
// ============================================================================

// Create root education level nodes
MERGE (jc:EducationLevel {code: 'junior_cycle', name_en: 'Junior Cycle', name_ga: 'An Teastas Sóisearach'})
MERGE (lc:EducationLevel {code: 'leaving_cert', name_en: 'Leaving Certificate', name_ga: 'An Ardteistiméireacht'})
MERGE (pr:EducationLevel {code: 'primary', name_en: 'Primary', name_ga: 'Bunscoil'});

// Create common difficulty levels
MERGE (f:DifficultyLevel {code: 'foundation', name_en: 'Foundation', name_ga: 'Bonnleibhéal'})
MERGE (o:DifficultyLevel {code: 'ordinary', name_en: 'Ordinary', name_ga: 'Gnáthleibhéal'})
MERGE (h:DifficultyLevel {code: 'higher', name_en: 'Higher', name_ga: 'Ardleibhéal'});

// Create document type taxonomy
MERGE (spec:DocumentType {code: 'specification', name: 'Curriculum Specification'})
MERGE (exam:DocumentType {code: 'exam_paper', name: 'Exam Paper'})
MERGE (mark:DocumentType {code: 'marking_scheme', name: 'Marking Scheme'})
MERGE (report:DocumentType {code: 'examiner_report', name: 'Examiner Report'})
MERGE (guide:DocumentType {code: 'teacher_guide', name: 'Teacher Guidelines'});
