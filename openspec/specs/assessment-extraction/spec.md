# Assessment Extraction Capability

## Purpose

`assessment-extraction` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


## Background
Extracting and structuring exam questions, marking schemes, and assessment criteria from SEC documents.

## Requirements

### Requirement: Question Extraction
The system SHALL extract exam questions with full structure preserved.

#### Scenario: Multi-Part Question
- **GIVEN** an exam paper with multi-part questions
- **WHEN** the paper is processed
- **THEN** all parts (a, b, c, i, ii, iii) are extracted with hierarchy

#### Scenario: Mathematical Content
- **GIVEN** a question containing LaTeX equations
- **WHEN** the content is extracted
- **THEN** equations are preserved in LaTeX format

### Requirement: Marking Scheme Extraction
The system SHALL extract marking schemes with point allocation.

#### Scenario: Scale 10C Marking
- **GIVEN** a Scale 10C marking scheme (10 marks total)
- **WHEN** the scheme is processed
- **THEN** all marking points with alternatives are extracted

#### Scenario: Penalty Rules
- **GIVEN** a marking scheme with penalty rules
- **WHEN** the scheme is processed
- **THEN** penalty conditions and deductions are captured

### Requirement: Question-Answer Alignment
The system SHALL align questions with their marking schemes.

#### Scenario: Part-Level Alignment
- **GIVEN** a question paper and marking scheme
- **WHEN** both are processed
- **THEN** each question part is linked to its marking criteria

### Requirement: Diagram and Table Extraction
The system SHALL extract visual content from exam papers.

#### Scenario: Graph Extraction
- **GIVEN** an exam question with a graph
- **WHEN** the paper is processed
- **THEN** the graph is captured with its reference

#### Scenario: Table Data
- **GIVEN** a question with tabular data
- **WHEN** the content is extracted
- **THEN** table structure is preserved

## BAML Schema Reference

```baml
class MarkingPoint {
  correct_answer: string
  marks_awarded: int
  valid_alternatives: string[]
  mandatory_keywords: string[]
}

class QuestionPartSchema {
  part_id: string
  total_marks: int
  marking_points: MarkingPoint[]
  penalties: PenaltyRule[]
}
```
