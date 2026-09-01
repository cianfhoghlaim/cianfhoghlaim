// =============================================================================
// Education Level Enums (split from curriculum_extraction.baml)
// Cross-stage education level enums shared across all NCCA stages.
// =============================================================================

// -----------------------------------------------------------------------------
// Relationship Types
// -----------------------------------------------------------------------------

enum RelationshipType {
  PREREQUISITE_FOR  @description("Source outcome must be learned before target")
  BUILDS_ON         @description("Target extends concepts from source")
  ASSESSES          @description("Outcome assesses a specific skill")
  RELATED_TO        @description("Outcomes share conceptual overlap")
  PART_OF           @description("Outcome is part of a larger competency")
  ENABLES           @description("Source outcome enables target")
  CONTRASTS_WITH    @description("Outcomes represent contrasting concepts")
}

// -----------------------------------------------------------------------------
// Difficulty Level
// -----------------------------------------------------------------------------

enum DifficultyLevel {
  FOUNDATION        @description("Basic foundational level")
  ORDINARY          @description("Standard ordinary level")
  HIGHER            @description("Advanced higher level")
  EXTENSION         @description("Extension or enrichment")
}

// -----------------------------------------------------------------------------
// Education Level (across cycles)
// -----------------------------------------------------------------------------

enum EducationLevel {
  PRIMARY           @description("Primary school (ages 4-12)")
  JUNIOR_CYCLE      @description("Junior Cycle (ages 12-15)")
  SENIOR_CYCLE      @description("Senior Cycle (ages 15-18)")
  TRANSITION_YEAR   @description("Transition Year (age 15-16)")
}

// -----------------------------------------------------------------------------
// Exam Level (Leaving Certificate)
// -----------------------------------------------------------------------------

enum ExamLevel {
  HIGHER           @description("Higher Level")
  ORDINARY         @description("Ordinary Level")
  FOUNDATION       @description("Foundation Level")
  COMMON           @description("Common Level")
}

// -----------------------------------------------------------------------------
// Question Type (Examination papers)
// -----------------------------------------------------------------------------

enum QuestionType {
  MULTIPLE_CHOICE  @description("MCQ questions")
  SHORT_ANSWER     @description("Brief written response")
  LONG_ANSWER      @description("Extended written response")
  CALCULATION      @description("Mathematical calculation")
  ESSAY            @description("Essay or extended writing")
  PRACTICAL        @description("Practical/coursework based")
  COMPREHENSION    @description("Reading comprehension")
  TRANSLATION      @description("Language translation")
  AURAL            @description("Listening comprehension")
  ORAL             @description("Speaking assessment")
}

// -----------------------------------------------------------------------------
// Leaving Certificate Subject (50+ subjects)
// -----------------------------------------------------------------------------

enum LeavingCertSubject {
  LC_MATHS                      @description("Mathematics")
  LC_APPLIED_MATHS              @description("Applied Mathematics")
  LC_ENGLISH                    @description("English")
  LC_GAEILGE                    @description("Gaeilge / Irish")
  LC_FRENCH                     @description("French")
  LC_GERMAN                     @description("German")
  LC_SPANISH                    @description("Spanish")
  LC_ITALIAN                    @description("Italian")
  LC_JAPANESE                   @description("Japanese")
  LC_RUSSIAN                    @description("Russian")
  LC_ARABIC                     @description("Arabic")
  LC_MANDARIN                   @description("Mandarin Chinese")
  LC_LATIN                      @description("Latin")
  LC_GREEK                      @description("Ancient Greek")
  LC_CLASSICAL_STUDIES          @description("Classical Studies")
  LC_HISTORY                    @description("History")
  LC_GEOGRAPHY                  @description("Geography")
  LC_PHYSICS                    @description("Physics")
  LC_CHEMISTRY                  @description("Chemistry")
  LC_BIOLOGY                    @description("Biology")
  LC_AGRICULTURAL_SCIENCE       @description("Agricultural Science")
  LC_BUSINESS                   @description("Business")
  LC_ACCOUNTING                 @description("Accounting")
  LC_ECONOMICS                  @description("Economics")
  LC_HOME_ECONOMICS_SOCIAL      @description("Home Economics — Social and Scientific")
  LC_ART                        @description("Art")
  LC_MUSIC                      @description("Music")
  LC_DCG                        @description("Design and Communication Graphics")
  LC_ENGINEERING                @description("Engineering")
  LC_TECHNOLOGY                 @description("Technology")
  LC_CONSTRUCTION_STUDIES       @description("Construction Studies")
  LC_PHYSICAL_EDUCATION         @description("Physical Education")
  LC_COMPUTER_SCIENCE           @description("Computer Science")
  LC_PHILOSOPHY                  @description("Philosophy")
  LC_POLITICS_AND_SOCIETY       @description("Politics and Society")
  LC_RELIGIOUS_EDUCATION        @description("Religious Education")
  LC_LINK_MODULES_LCVP          @description("Link Modules (LCVP)")
  LC_TRANSITION_YEAR            @description("Transition Year")
  LC_CAREERS_PORTFOLIO          @description("Careers Portfolio")
  LC_LCA_VOCATIONAL_PREP        @description("Leaving Certificate Applied — Vocational Preparation")
  LC_LCA_ENGLISH_COMM           @description("LCA — English and Communication")
  LC_LCA_GAEILGE_CUM            @description("LCA — Gaeilge Chumarsáideach")
  LC_LCA_MATHEMATICAL           @description("LCA — Mathematical Applications")
  LC_LCA_SOCIAL_EDUCATION       @description("LCA — Social Education")
  LC_LCA_HOTEL_CATERING         @description("LCA — Hotel, Catering and Tourism")
  LC_LCA_OFFICE_ADMIN           @description("LCA — Office Administration and Customer Care")
  LC_LCA_ICT                    @description("LCA — Information and Communication Technology")
  LC_LCA_ACTIVE_LEISURE         @description("LCA — Active Leisure Studies")
  LC_LCA_AGRICULTURE            @description("LCA — Agriculture/Horticulture")
  LC_LCA_CHILDCARE              @description("LCA — Childcare/Community Care")
  LC_LCA_CRAFT_DESIGN           @description("LCA — Craft and Design")
  LC_LCA_DANCE                  @description("LCA — Dance")
  LC_LCA_DRAMA                  @description("LCA — Drama")
  LC_LCA_ENGINEERING_LCA        @description("LCA — Engineering")
  LC_LCA_GRAPHICS_CONSTRUCTION  @description("LCA — Graphics and Construction Studies")
  LC_LCA_HAIR_BEAUTY            @description("LCA — Hair and Beauty")
  LC_LCA_LEISURE_RECREATION     @description("LCA — Leisure and Recreation")
  LC_LCA_MUSIC_LCA              @description("LCA — Music")
  LC_LCA_RELIGIOUS_ED           @description("LCA — Religious Education")
  LC_LCA_SCIENCE_LCA            @description("LCA — Science")
  LC_LCA_SIGN_LANGUAGE          @description("LCA — Sign Language")
  LC_LCA_TECHNOLOGY_LCA         @description("LCA — Technology")
  LC_LCA_VISUAL_ART             @description("LCA — Visual Art")
  LC_OTHER                      @description("Fallback for new subjects not yet catalogued")
}

// -----------------------------------------------------------------------------
// Specialism (Subject Family)
// -----------------------------------------------------------------------------

enum Specialism {
  SCIENCES
  LANGUAGES
  BUSINESS
  HUMANITIES
  PRACTICAL
  ARTS
  APPLIED
  INTERDISCIPLINARY
}

// -----------------------------------------------------------------------------
// Assessment Component Type
// -----------------------------------------------------------------------------

enum AssessmentComponentType {
  WRITTEN
  ORAL
  AURAL
  PRACTICAL
  COURSEWORK
  CBA
  PROJECT
  PORTFOLIO
}

// -----------------------------------------------------------------------------
// Rubric Style
// -----------------------------------------------------------------------------

enum RubricStyle {
  PCLM                            @description("Purpose / Coherence / Language / Mechanics — English")
  SRP                             @description("Significant Relevant Points — Geography, History")
  EQUATION_STEPS                  @description("Step-by-step equation solving — Mathematics, Physics")
  KEYWORD_MATCH_DIAGRAM            @description("Mandatory keyword + diagram labels — Biology, Science")
  COMPREHENSION_EXPRESSION        @description("Compréhension / expression — French, German, Spanish")
  SECTION_B_KEYWORD                @description("Section B keyword marks — Business, Accounting")
  DIAGRAM_SKETCH_STEPS            @description("Diagram / sketch + reasoning — Construction Studies, DCG")
  BALANCED_EQUATION_STATE_SYMBOLS @description("Balanced equations with state symbols — Chemistry")
  DEFINITION_UNIT_FORMULA          @description("Definition + unit + formula — Physics, Ag Science")
  RUBRIC_PCLM_IRISH                @description("Cumarsáid / Léamhthuiscint / Litríocht / Gramadach — Gaeilge")
  LINGUISTIC_PRINCIPLES            @description("Linguistic principles + examples — MFL, Classical languages")
}

// -----------------------------------------------------------------------------
// Document Category (PDF metadata)
// -----------------------------------------------------------------------------

enum DocumentCategory {
  SPECIFICATION           @description("Modern curriculum specifications")
  SYLLABUS                @description("Older curriculum syllabi")
  MEETING_MINUTES         @description("Curriculum development group meeting minutes")
  ASSESSMENT_GUIDELINES   @description("Guidelines for CBAs or final assessments")
  FRAMEWORK               @description("Overarching educational frameworks")
  CONSULTATION_DOCUMENT   @description("Drafts or feedback on proposed changes")
  EXAM_PAPER              @description("State examination papers")
  MARKING_SCHEME          @description("State examination marking schemes")
  EXAMINER_REPORT         @description("Chief examiner reports")
  OTHER                   @description("Other documents")
}

// -----------------------------------------------------------------------------
// Skill Category
// -----------------------------------------------------------------------------

enum SkillCategory {
  COGNITIVE         @description("Thinking, reasoning, problem-solving")
  LINGUISTIC        @description("Language, communication, literacy")
  MATHEMATICAL      @description("Numeracy, calculation, logic")
  CREATIVE          @description("Creativity, imagination, design")
  SOCIAL            @description("Collaboration, teamwork, empathy")
  PHYSICAL          @description("Motor skills, coordination")
  DIGITAL           @description("Technology, digital literacy")
  METACOGNITIVE     @description("Self-awareness, learning-to-learn")
}
