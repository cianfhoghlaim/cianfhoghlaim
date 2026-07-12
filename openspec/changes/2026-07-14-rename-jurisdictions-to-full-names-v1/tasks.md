# Tasks: 2026-07-14-rename-jurisdictions-to-full-names-v1

## 1. Create openspec change

- [ ] 1.1 Create `openspec/changes/2026-07-14-rename-jurisdictions-to-full-names-v1/`
- [ ] 1.2 Write `proposal.md` + `tasks.md` (this file)
- [ ] 1.3 Write the 3 spec deltas
- [ ] 1.4 `openspec validate 2026-07-14-rename-jurisdictions-to-full-names-v1 --strict` passes

## 2. Subagent dispatch

Dispatch 5 parallel data-platform subagents:

### Subagent 1 — EU nations (40 jurisdictions)

For each of the 40 jurisdictions below, rename every BAML class
+ function + Python class + docstring + Dagster defs.yaml metadata +
CocoIndex v1 App description + MotherDuck Dive description to use the
full country name:

- AUT (Austria) — Federal Republic of Austria
- BEL (Belgium) — Kingdom of Belgium — nl, fr, de
- BGR (Bulgaria) — Republic of Bulgaria
- CHE (Switzerland) — Swiss Confederation — de, fr, it, rm
- CYP (Cyprus) — Republic of Cyprus — el, tr
- CZE (Czechia) — Czech Republic
- DEU (Germany) — Federal Republic of Germany
- DNK (Denmark) — Kingdom of Denmark
- ESP (Spain) — Kingdom of Spain
- EST (Estonia) — Republic of Estonia
- FIN (Finland) — Republic of Finland — fi, sv
- FRA (France) — French Republic
- GRC (Greece) — Hellenic Republic
- HRV (Croatia) — Republic of Croatia
- HUN (Hungary) — Hungary
- IRL (Ireland) — Republic of Ireland
- ISL (Iceland) — Republic of Iceland
- ITA (Italy) — Italian Republic
- LIE (Liechtenstein) — Principality of Liechtenstein
- LTU (Lithuania) — Republic of Lithuania
- LUX (Luxembourg) — Grand Duchy of Luxembourg — lb, fr, de
- LVA (Latvia) — Republic of Latvia
- MLT (Malta) — Republic of Malta — mt, en
- NLD (Netherlands) — Kingdom of the Netherlands
- NOR (Norway) — Kingdom of Norway — nb, nn, se
- POL (Poland) — Republic of Poland
- PRT (Portugal) — Portuguese Republic
- ROU (Romania) — Romania
- SVK (Slovakia) — Slovak Republic
- SVN (Slovenia) — Republic of Slovenia
- SWE (Sweden) — Kingdom of Sweden
- UKR (Ukraine) — Ukraine (EU candidate)
- PLUS: LIE, plus the 8 BIEP nations (Scotland / England / Wales /
  Northern Ireland / Isle of Man / Jersey / Guernsey / Ireland — most
  already use full names; verify + light touch only).

BAML classes / functions to rename:
- `class DEUSubjectCurriculum` → `class GermanySubjectCurriculum`
- `class DEUStatute` → `class GermanyStatute`
- `class DEUHealthGuidance` → `class GermanyHealthGuidance`
- `function ExtractDEUSubjectCurriculum` → `function ExtractGermanySubjectCurriculum`
- ... (same pattern for all 40 jurisdictions)

### Subagent 2 — Canada (17 jurisdictions)

For each of the 17 Canadian jurisdictions, rename BAML + DLT +
Dagster + CocoIndex to use the full province name:

- AB (Alberta) — Province of Alberta
- BC (British Columbia) — Province of British Columbia
- MB (Manitoba) — Province of Manitoba
- NB (New Brunswick) — Province of New Brunswick
- NL (Newfoundland and Labrador) — Province of Newfoundland and Labrador
- NS (Nova Scotia) — Province of Nova Scotia
- NT (Northwest Territories) — Northwest Territories
- NU (Nunavut) — Territory of Nunavut
- ON (Ontario) — Province of Ontario
- PE (Prince Edward Island) — Province of Prince Edward Island
- QC (Quebec) — Province of Quebec
- SK (Saskatchewan) — Province of Saskatchewan
- YT (Yukon) — Yukon Territory

Plus the Quebec deep cluster (5 sources): MEES, CSSDM, EMSB, LBPSB,
McGill universities — rename classes to `QuebecMinistryOfEducation`,
`MontrealFrenchSchoolBoard` (CSSDM), `MontrealEnglishSchoolBoard`
(EMSB), `MontrealLesterBPearsonSchoolBoard` (LBPSB),
`MontrealUniversitiesCluster`.

### Subagent 3 — Nigeria (37 sub-units)

For each of the 36 states + 1 Federal Capital Territory, rename to
use the full state name:

- nga_abi → Abia State
- nga_ada → Adamawa State
- nga_aki → Akwa Ibom State
- nga_ana → Anambra State
- nga_bau → Bauchi State
- nga_bay → Bayelsa State
- nga_ben → Benue State
- nga_bor → Borno State
- nga_crs → Cross River State
- nga_del → Delta State
- nga_ebi → Ebonyi State
- nga_edo → Edo State
- nga_eki → Ekiti State
- nga_enu → Enugu State
- nga_fct → Federal Capital Territory (Abuja)
- nga_gom → Gombe State
- nga_imo → Imo State
- nga_jig → Jigawa State
- nga_kad → Kaduna State
- nga_kan → Kano State
- nga_kat → Katsina State
- nga_keb → Kebbi State
- nga_kog → Kogi State
- nga_kwa → Kwara State
- nga_los → Lagos State
- nga_nas → Nasarawa State
- nga_ngr → Niger State
- nga_ogn → Ogun State
- nga_ond → Ondo State
- nga_osn → Osun State
- nga_oyo → Oyo State
- nga_plt → Plateau State
- nga_riv → Rivers State
- nga_sok → Sokoto State
- nga_tar → Taraba State
- nga_yob → Yobe State
- nga_zam → Zamfara State

BAML classes become `LagosStateSubjectCurriculum`,
`KanoStateSubjectCurriculum`, etc.

### Subagent 4 — Americas (8 jurisdictions)

For each of the 8 Americas jurisdictions:

- us_us_ca → California (US state)
- bra → Federative Republic of Brazil
- mex → United Mexican States
- ven → Bolivarian Republic of Venezuela

Plus the 4 institutional Americas:
- OAS (Organization of American States)
- PAHO (Pan American Health Organization)
- IDB (Inter-American Development Bank)
- CELAC (Community of Latin American and Caribbean States)

BAML classes: `CaliforniaSubjectCurriculum`,
`BrazilSubjectCurriculum`, `MexicoSubjectCurriculum`,
`VenezuelaSubjectCurriculum`.

### Subagent 5 — Other Commonwealth (19 jurisdictions)

For each of the 19 Commonwealth nations:

- AUS (Australia) — Commonwealth of Australia — 6 states + 2 territories
- CAN (Canada — already done by #2; light touch only)
- NZL (New Zealand) — New Zealand
- IND (India) — Republic of India
- ZAF (South Africa) — Republic of South Africa

Australian states:
- nsw → New South Wales
- vic → Victoria
- qld → Queensland
- wa → Western Australia
- sa → South Australia
- tas → Tasmania
- act → Australian Capital Territory
- nt → Northern Territory

Indian states:
- in_mh → Maharashtra
- in_ka → Karnataka
- in_tn → Tamil Nadu
- in_up → Uttar Pradesh
- in_wb → West Bengal

South African provinces:
- za_gp → Gauteng
- za_wc → Western Cape
- za_kzn → KwaZulu-Natal
- za_ec → Eastern Cape

BAML classes: `AustraliaSubjectCurriculum`,
`NewSouthWalesSubjectCurriculum`, `MaharashtraSubjectCurriculum`,
`GautengSubjectCurriculum`, etc.

## 3. Spec deltas

- [ ] 3.1 MODIFIED delta on `cross-region-pipeline/spec.md`
  declaring the rename convention
- [ ] 3.2 MODIFIED delta on `british-isles-education-pipeline/spec.md`
  declaring the BIEP light-touch pass
- [ ] 3.3 MODIFIED delta on `oideachais-pipeline/spec.md` declaring
  the global rename convention

## 4. Validate

- [ ] 4.1 `openspec validate 2026-07-14-rename-jurisdictions-to-full-names-v1 --strict` passes
- [ ] 4.2 All 5 subagent deliverables complete + AST-parse cleanly
- [ ] 4.3 No file paths, source_id strings, partition values, or table
  names were changed (verify with `git grep` invariants)
- [ ] 4.4 `dg check yaml` passes
- [ ] 4.5 `mise run lint:skills` still passes (53/53)

## 5. Commit + push

- [ ] 5.1 Stage the 5 subagent deliverables + the openspec change
- [ ] 5.2 Single commit with message
  `refactor(jurisdictions): rename display strings to full country + state names (keep short IDs)`
- [ ] 5.3 `git push origin pick-4-biep-v1`
