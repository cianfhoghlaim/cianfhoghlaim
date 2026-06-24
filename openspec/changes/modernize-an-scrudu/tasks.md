# Tasks: modernize-an-scrudu

## 1. Add Pydantic schemas

- [x] Add `PTopicDistribution` (mirrors the canonical BAML class)
- [x] Add `PCircularReference`
- [x] Add `PMarkingSchemeSummary`
- [x] Add `PCircularExtraction` (the top-level result)

## 2. Update validation

- [x] Update `_validate_and_coerce` to use the Pydantic schema
      (accepts both the nested BAML shape and the flat legacy shape)
- [x] On Pydantic validation failure, fall back to the flat
      schema with defaults
- [x] Update the prompt template to request the nested BAML shape

## 3. Add pydantic to requirements

- [x] Add `pydantic>=2.5` to `spaces/an_scrudu/requirements.txt`

## 4. Spec deltas

- [x] 1 MODIFIED Requirement on `oideachais-pipeline`:
      "ExtractCircularMeta Pydantic mirror"
- [x] 1 MODIFIED Requirement on `spaces-cicd-pipeline`:
      "an_scrudu Pydantic schema validation"

## 5. Validate + commit + push + archive

- [x] `openspec validate modernize-an-scrudu --strict`
- [x] Commit with message
      `modernize-an-scrudu: Pydantic schemas + nested BAML shape + LiteLLM gateway`
- [x] Archive the openspec change
- [x] `git push`
