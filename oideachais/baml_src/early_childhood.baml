// oideachais/baml_src/early_childhood.baml
//
// BAML extraction for the Aistear (early childhood) framework.
// The Aistear framework is the Irish national curriculum framework
// for children from birth to 6 years, organised around 4 themes:
//
//   1. Well-being (Bheith go maith)
//   2. Identity and Belonging ( Féiniúlacht agus Cairdeas)
//   3. Communicating (Cumarsáid)
//   4. Exploring and Thinking (Iniúchadh agus Smaointeoireacht)
//
// Consumer: dlt_sources/ireland/aistear.py
// Dagster asset: dagster_defs/assets/ie/education/aistear_dlt_assets.py
//
// Reference: openspec/changes/wire-baml-with-known-consumers

class AistearPrinciple {
  name string @description("Short name of the principle (e.g. 'Children are capable and confident').")
  description string @description("One-paragraph explanation of the principle.")
  age_band string @description("Applicable age band: 'BIRTH_TO_3', '3_TO_4', '4_TO_5', '5_TO_6', or 'ALL'.")
}

class AistearLearningGoal {
  goal_id string @description("Stable ID, e.g. 'WB_1', 'IB_2', 'CO_3', 'ET_4'.")
  description string @description("The full text of the learning goal (often bilingual EN/GA).")
  theme string @description("One of: 'WELL_BEING', 'IDENTITY_BELONGING', 'COMMUNICATING', 'EXPLORING_THINKING'.")
  age_band string @description("Applicable age band: 'BIRTH_TO_3', '3_TO_4', '4_TO_5', '5_TO_6', or 'ALL'.")
}

class AistearFramework {
  themes string[] @description("The 4 Aistear themes in English: 'Well-being', 'Identity and Belonging', 'Communicating', 'Exploring and Thinking'.")
  principles AistearPrinciple[] @description("The 12 Aistear principles extracted from the document.")
  learning_goals AistearLearningGoal[] @description("All learning goals extracted (typically 40-60 per document).")
}

class AistearDocument {
  document_id string @description("Stable ID derived from filename (e.g. 'aistear_principles_2024').")
  title string @description("The English (or bilingual) title of the document.")
  framework AistearFramework
  extracted_at string @description("ISO-8601 UTC timestamp of the BAML extraction.")
}

function ExtractAistearFramework(pdf_text: string) -> AistearFramework {
  client LitellmClient
  prompt #"
    You are an Aistear (Irish early childhood curriculum) expert.

    Extract the 4 Aistear themes, 12 principles, and all learning goals
    from the following Aistear document text.

    The 4 Aistear themes are:
      1. Well-being (Bheith go maith)
      2. Identity and Belonging (Féiniúlacht agus Cairdeas)
      3. Communicating (Cumarsáid)
      4. Exploring and Thinking (Iniúchadh agus Smaointeoireacht)

    Aistear principles include (but are not limited to):
      - Children are capable and confident
      - Children are active learners
      - Children learn through relationships
      - Children learn through play
      - Children learn through meaningful experiences
      - Children's early years lay the foundation for later learning
      - Equality and diversity are rights
      - Parents and families are the primary educators
      - Quality early childhood experiences make a difference
      - Holistic development matters
      - The voice of the child matters
      - Play is a key context for learning

    For each learning goal, return:
      - goal_id: stable ID like 'WB_1', 'IB_2', 'CO_3', 'ET_4'
      - description: full text (often bilingual)
      - theme: one of the 4 themes
      - age_band: BIRTH_TO_3 / 3_TO_4 / 4_TO_5 / 5_TO_6 / ALL

    Document text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
