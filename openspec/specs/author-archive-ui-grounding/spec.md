# author-archive-ui-grounding Specification

## Purpose
TBD - created by archiving change author-archive-v1. Update Purpose after archive.
## Requirements
### Requirement: UI type enum

The BAML `UiType` enum SHALL have 10 values: `SEARCH_BOX`, `FORM`,
`DASHBOARD`, `MAP`, `LOGIN_WALL`, `FILE_DOWNLOAD`, `CAROUSEL`,
`TIMELINE`, `OTHER`, `NONE`. The first 8 are interactive elements
that the user might want to script; `OTHER` is a catch-all; `NONE`
means no UI detected.

#### Scenario: A page with a search box

- **WHEN** the page has a text input labelled "Search"
- **THEN** `IdentifyUiPatterns` returns `ui_type = SEARCH_BOX`

#### Scenario: A plain article page

- **WHEN** the page has no interactive elements
- **THEN** `IdentifyUiPatterns` returns `ui_type = NONE` and
  `has_ui = False`

### Requirement: Per-page UI indicator

For every scraped page, the BAML `IdentifyUiPatterns` function SHALL
return 0-N `UiIndicator` records with: `has_ui` (bool), `ui_type`
(UiType), `element_label` (string?), `grounding_query` (string?),
`confidence` (float, 0.0-1.0).

#### Scenario: Single search box

- **WHEN** the page has exactly one interactive element
- **THEN** the function returns one `UiIndicator` with
  `has_ui = True` and the appropriate `ui_type`

#### Scenario: Multiple search boxes

- **WHEN** the page has two distinct search boxes
- **THEN** the function returns two `UiIndicator` records, one per
  element

### Requirement: Visual grounding bounding box

The BAML `VisualGroundingFromScreenshot` function SHALL return a
`GroundedElement` with: `label` (string), `bbox` (BoundingBox in 0-1
normalised coordinates), `action` (string: `click`|`type`|`select`|
`hover`|`drag`|`submit`), `selector` (string?), `confidence` (float,
0.0-1.0). If the element is not visible in the screenshot, the
function SHALL return `confidence=0` and `bbox=[0, 0, 0, 0]`.

#### Scenario: Element visible

- **WHEN** the screenshot shows a clear search box
- **THEN** the function returns `confidence > 0.7` and a non-zero
  `bbox`

#### Scenario: Element not visible

- **WHEN** the screenshot does not show the element
- **THEN** the function returns `confidence = 0` and `bbox = [0, 0, 0, 0]`

### Requirement: Storage shape

The `oideachais.official_media.ui_elements` LanceDB table MUST have
the following columns:

- `url` (string) — the page URL
- `ui_type` (UiType) — from the enum
- `element_label` (string)
- `grounding_query` (string)
- `bbox_x_min` (float, 0-1)
- `bbox_y_min` (float, 0-1)
- `bbox_x_max` (float, 0-1)
- `bbox_y_max` (float, 0-1)
- `action` (string)
- `selector` (string?)
- `confidence` (float)
- `backend_used` (string)
- `screenshot_path` (string) — path to the screenshot in the
  object store (S3 in prod, local fs in dev)
- `captured_at` (datetime)

#### Scenario: Persist a search box

- **WHEN** the BAML function returns a `BoundingBox(x_min=0.1, y_min=0.2, x_max=0.5, y_max=0.3)`
- **THEN** the asset inserts a row with `bbox_x_min=0.1`, `bbox_y_min=0.2`,
  `bbox_x_max=0.5`, `bbox_y_max=0.3`, `ui_type='SEARCH_BOX'`,
  `action='type'`, `confidence=0.92`

### Requirement: Free-fallback when no browser is available

The system MUST handle the case where no free browser backend is
running (CI without a Stagehand container). In that case the
`official_media_identify_uis` asset MUST skip the page, emit a
metadata counter for `screenshots_taken` and `uis_identified`, and
continue to the next source without raising. The asset MUST NOT
fail the whole asset run just because one backend is unavailable.

#### Scenario: CI without browser

- **WHEN** no free browser backend is registered
- **THEN** the asset skips every page
- **AND** emits `screenshots_taken = 0`, `uis_identified = 0`
- **AND** the asset run completes successfully

