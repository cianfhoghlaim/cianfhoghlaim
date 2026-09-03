# LEGACY_ALIASES — orchestration/

Per the
[`2026-07-17-pipeline-directory-consolidation-v1`](../../changes/2026-07-17-pipeline-directory-consolidation-v1/proposal.md)
openspec change. **All old paths remain importable via deprecation
shims for at least one release cycle.**

## European nations — ISO 3-letter → full snake_case

40 jurisdictions, ISO-3 → full snake_case. See `baml_src/LEGACY_ALIASES.md`
for the canonical mapping; same applies here.

## Commonwealth

Same as `baml_src/LEGACY_ALIASES.md`:
- `aus → australia`, `can → canada`, `ind → india`, `nga → nigeria`,
  `nzl → new_zealand`, `zaf → south_africa`
- Canada provinces nest under `canada/provinces/{alberta,...}`
- Nigeria states nest under `nigeria/states/{abia,...}`

## British Isles — collapse dual naming

`en → england`, `ni → northern_ireland`, `sct → scotland`,
`wls → wales` (also: `iom → isle_of_man`, `jey → jersey`, `ggy → guernsey`).

## Americas

`americas/{bra,mex,us,ven}` → `american_nations/{brazil,mexico,united_states,venezuela}`.