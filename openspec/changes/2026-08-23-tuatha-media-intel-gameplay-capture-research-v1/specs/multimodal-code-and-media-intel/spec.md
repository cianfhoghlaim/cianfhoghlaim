# Spec Delta: multimodal-code-and-media-intel

## ADDED Requirements

### Requirement: `MediaLocalEmbedding` App accepts typed `MediaDescriptor` records

The system SHALL extend the existing `MediaLocalEmbedding`
CocoIndex v1 App (defined in the `multimodal-code-and-media-intel`
spec) to accept typed `MediaDescriptor` records as the
upstream input, not just raw mp4/mkv/webm files.

The App SHALL:

- Read the `media_descriptors` LanceDB table (built by the
  `media-intel-corpus` spec) as the primary input
- Continue to accept raw media files (mp4/mkv/webm/mp3/wav/
  m4a/ogg) as a secondary input
- Use the BAML function
  `ExtractMediaDescriptorForEmbedding` (added in
  `baml_src/media/media_descriptor.baml`) to convert raw
  media into descriptors before embedding
- Mount 3 new LanceDB tables:
  `media_descriptors_embeddings` (the descriptor vectors),
  `media_descriptors_multimodal` (the descriptor +
  raw media pair), `media_descriptors_metadata` (the
  provenance + licence metadata)

#### Scenario: A raw mp4 is converted to a descriptor before embedding

- **GIVEN** a raw mp4 file is dropped into
  `stedding/ingest_queue/media/`
- **WHEN** the `MediaLocalEmbedding` App materialises
- **THEN** the `ExtractMediaDescriptorForEmbedding` BAML
  function runs with `medium = "moving_media"`,
  `vlm_primary = "qwen3-vl-8b"` (the
  `multimodal-code-and-media-intel` workhorse)
- **AND** the function emits a `MediaDescriptor` record
  with all 7 axes populated
- **AND** the record is written to the
  `media_descriptors` LanceDB table
- **AND** the embedding is stored in the
  `media_descriptors_embeddings` table

#### Scenario: A typed descriptor from a different source is embedded directly

- **GIVEN** a `MediaDescriptor` row already exists in the
  `media_descriptors` table (from a different source —
  e.g. the `retro_marvel_hickman_ff` DLT source)
- **WHEN** the `MediaLocalEmbedding` App materialises
- **THEN** the App SHALL embed the descriptor directly
  (no re-extraction)
- **AND** the embedding SHALL be tagged with the source
  provenance (`source: retro_marvel_hickman_ff`)
- **AND** the embedding SHALL preserve the
  `derivation_class` and `shippable` invariants
