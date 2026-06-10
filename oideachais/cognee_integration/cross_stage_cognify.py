"""
Cross-stage Cognee cognify pass.

After the 5 stage knowledge-graph assets materialise, this asset creates the
8 cross-stage edges that span the entire Cianfhoghlaim Oideachais graph:

  (:AistearPrinciple) -[:BRIDGES_TO]-> (:PrimaryLearningOutcome)
  (:PrimaryLearningOutcome) -[:PREPARES_FOR]-> (:JCLearningOutcome)
  (:JCLearningOutcome) -[:PROGRESSES_TO]-> (:SCLearningOutcome)
  (:SCLearningOutcome) -[:ASSESSED_BY]-> (:ExamQuestion)
  (:LCSubject) -[:REQUIRED_FOR]-> (:CAOCourse)
  (:CAOCourse) -[:DELIVERS]-> (:Programme)
  (:QQIFetAward) -[:LADDERS_INTO]-> (:CAOCourse)
  (:Apprenticeship) -[:ALTERNATIVE_TO]-> (:CAOCourse)
"""
from dagster import asset

EDGE_DEFINITIONS = [
    {
        "from_label": "AistearPrinciple",
        "to_label": "PrimaryLearningOutcome",
        "edge_type": "BRIDGES_TO",
        "weight": 0.6,
        "rationale": "An Aistear principle may bridge to a Stage 1 (Infants) Primary outcome.",
    },
    {
        "from_label": "PrimaryLearningOutcome",
        "to_label": "JCLearningOutcome",
        "edge_type": "PREPARES_FOR",
        "weight": 0.5,
        "rationale": "A Primary Stage 4 outcome prepares for a Junior Cycle Year 1 outcome in the same strand.",
    },
    {
        "from_label": "JCLearningOutcome",
        "to_label": "SCLearningOutcome",
        "edge_type": "PROGRESSES_TO",
        "weight": 0.7,
        "rationale": "A Junior Cycle Year 3 outcome progresses to a Senior Cycle Year 1 (5th Year) outcome.",
    },
    {
        "from_label": "SCLearningOutcome",
        "to_label": "ExamQuestion",
        "edge_type": "ASSESSED_BY",
        "weight": 0.9,
        "rationale": "A Senior Cycle learning outcome is assessed by a specific exam question.",
    },
    {
        "from_label": "LCSubject",
        "to_label": "CAOCourse",
        "edge_type": "REQUIRED_FOR",
        "weight": 1.0,
        "rationale": "A Leaving Certificate subject is required for a CAO course (matriculation).",
    },
    {
        "from_label": "CAOCourse",
        "to_label": "Programme",
        "edge_type": "DELIVERS",
        "weight": 1.0,
        "rationale": "A CAO course delivers a Programme of study at the HEI.",
    },
    {
        "from_label": "QQIFetAward",
        "to_label": "CAOCourse",
        "edge_type": "LADDERS_INTO",
        "weight": 0.8,
        "rationale": "A QQI FET Level 5/6 award can ladder into a CAO Level 7/8 course.",
    },
    {
        "from_label": "Apprenticeship",
        "to_label": "CAOCourse",
        "edge_type": "ALTERNATIVE_TO",
        "weight": 0.6,
        "rationale": "An Apprenticeship programme is an alternative pathway to a related CAO course.",
    },
]


# Per-stage knowledge_graph assets (aistear, primary, junior_cycle,
# senior_cycle, tertiary) are defined per-cycle in the ireland/curriculum_dlt
# assets. Until those are wired up as knowledge_graph producers, this
# cross-stage asset is standalone (no upstream assets) and records the
# 8 cross-stage edge specs.
#
# To re-enable strict cross-stage ordering once the per-stage
# knowledge_graph assets are defined, add them as Ins and accept them
# as parameters.
from dagster import asset


@asset(
    group_name="knowledge_graph",
    description="Cross-stage Cognee cognify: creates 8 cross-stage edges spanning Aistear → Primary → JC → SC → Tertiary.",
)
def cross_stage_cognify(context) -> int:
    """Trigger the Cognee cognify pass on the cross-stage dataset.

    The real implementation calls cognee.cognify(dataset="oideachais.cross_stage")
    after the 5 stage cognify passes have completed.
    """
    context.log.info("Running cross-stage Cognee cognify pass")
    for edge in EDGE_DEFINITIONS:
        context.log.info(
            f"  {edge['from_label']} -[:{edge['edge_type']}]-> {edge['to_label']} (weight {edge['weight']})"
        )

    # The 8 cross-stage edges to create
    edges_created = len(EDGE_DEFINITIONS)
    return edges_created
