# Knowledge Graph Capability

## Overview

Building and querying curriculum knowledge graphs for prerequisite chains, topic relationships, and learning path generation.

## Requirements

### Requirement: Prerequisite Mapping
The system SHALL model prerequisite relationships between curriculum topics.

#### Scenario: Direct Prerequisite
- **GIVEN** Topic A requires understanding of Topic B
- **WHEN** the relationship is stored
- **THEN** a `:PREREQUISITE` edge connects them

#### Scenario: Transitive Prerequisites
- **GIVEN** a topic with multiple levels of prerequisites
- **WHEN** queried for all prerequisites
- **THEN** the complete prerequisite chain is returned

### Requirement: Strand-Topic Hierarchy
The system SHALL model the curriculum hierarchy in the graph.

#### Scenario: Mathematics Hierarchy
- **GIVEN** the Mathematics curriculum structure
- **WHEN** stored in the graph
- **THEN** Subject → Strand → Topic → Learning Outcome hierarchy is preserved

### Requirement: Assessment Linkage
The system SHALL link learning outcomes to assessment items.

#### Scenario: Question-Outcome Mapping
- **GIVEN** an exam question
- **WHEN** linked to the graph
- **THEN** it connects to the learning outcomes it assesses

#### Scenario: Marking Scheme Coverage
- **GIVEN** a topic
- **WHEN** queried for assessment coverage
- **THEN** all related exam questions and their marks are returned

### Requirement: Learning Path Generation
The system SHALL generate optimal learning paths.

#### Scenario: Prerequisite-Ordered Path
- **GIVEN** a target learning outcome
- **WHEN** a learning path is requested
- **THEN** topics are ordered respecting prerequisites

#### Scenario: Gap Analysis
- **GIVEN** a student's mastery state
- **WHEN** compared to target outcome
- **THEN** missing prerequisites are identified

## Graph Schema

```cypher
// Core nodes
(:Subject {name: "Mathematics"})
(:Strand {name: "Algebra", subject: "Mathematics"})
(:Topic {name: "Quadratic Equations", strand: "Algebra"})
(:LearningOutcome {code: "LC-MA-2.1", description: "..."})
(:Question {year: 2023, paper: 1, number: 3})

// Core relationships
(:Topic)-[:PREREQUISITE]->(:Topic)
(:Topic)-[:PART_OF]->(:Strand)
(:Strand)-[:PART_OF]->(:Subject)
(:LearningOutcome)-[:BELONGS_TO]->(:Topic)
(:Question)-[:ASSESSES]->(:LearningOutcome)
```

## Bi-Temporal Model

```cypher
// Syllabus versioning with validity periods
(:Topic {name: "Matrices"}) -[:PART_OF {
  valid_at: "1990-01-01",
  invalid_at: "2015-01-01"
}]-> (:Curriculum {name: "Leaving Cert"})

// Student mastery tracking
(:Student) -[:HAS_MASTERY {
  valid_at: "2024-03-15",
  confidence: 0.85,
  decay_rate: 0.02
}]-> (:Topic)
```

## Query Examples

```cypher
// Find all prerequisites for a topic
MATCH (t:Topic {name: "Complex Numbers"})<-[:PREREQUISITE*]-(prereq)
RETURN prereq.name ORDER BY length(path)

// Topics assessed in 2023 Higher Level
MATCH (q:Question {year: 2023, level: "Higher"})
      -[:ASSESSES]->(:LearningOutcome)
      -[:BELONGS_TO]->(t:Topic)
RETURN DISTINCT t.name

// Learning path to target
MATCH path = (target:Topic {name: "Differential Equations"})
              <-[:PREREQUISITE*]-(start:Topic)
WHERE NOT (start)<-[:PREREQUISITE]-()
RETURN path ORDER BY length(path)
```
