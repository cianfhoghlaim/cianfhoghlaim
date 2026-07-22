#!/usr/bin/env bun
// scripts/build_rename_maps.ts
// Build deterministic rename maps for the 4 packages + notebooks.
// Outputs YAML to stdout, keyed by package root.

interface PackageMaps {
  baml_src: Record<string, string>;
  dlt: Record<string, string>;
  orchestration: Record<string, string>;
  cocoindex: Record<string, string>;
  notebooks: Record<string, string>;
}

// 40 European nations (ISO 3 → snake_case full name)
const europeanNations: Record<string, string> = {
  alb: "albania",
  aut: "austria",
  bel: "belgium",
  bgr: "bulgaria",
  bih: "bosnia_and_herzegovina",
  che: "switzerland",
  cyp: "cyprus",
  cze: "czechia",
  deu: "germany",
  dnk: "denmark",
  esp: "spain",
  est: "estonia",
  fin: "finland",
  fra: "france",
  geo: "georgia",
  grc: "greece",
  hrv: "croatia",
  hun: "hungary",
  isl: "iceland",
  ita: "italy",
  lie: "liechtenstein",
  ltu: "lithuania",
  lux: "luxembourg",
  lva: "latvia",
  mda: "moldova",
  mkd: "north_macedonia",
  mlt: "malta",
  mne: "montenegro",
  nld: "netherlands",
  nor: "norway",
  pol: "poland",
  prt: "portugal",
  rou: "romania",
  srb: "serbia",
  svk: "slovakia",
  svn: "slovenia",
  swe: "sweden",
  tur: "turkey",
  ukr: "ukraine",
  xkx: "kosovo",
};

// 6 Commonwealth countries
const commonwealth: Record<string, string> = {
  aus: "australia",
  can: "canada",
  ind: "india",
  nga: "nigeria",
  nzl: "new_zealand",
  zaf: "south_africa",
};

// 13 Canadian provinces
const canadaProvinces: Record<string, string> = {
  ab: "alberta",
  bc: "british_columbia",
  mb: "manitoba",
  nb: "new_brunswick",
  nl: "newfoundland_and_labrador",
  ns: "nova_scotia",
  nt: "northwest_territories",
  nu: "nunavut",
  on: "ontario",
  pe: "prince_edward_island",
  qc: "quebec",
  sk: "saskatchewan",
  yt: "yukon",
};

// 8 British Isles jurisdictions (code → full)
const britishIsles: Record<string, string> = {
  en: "england",
  england: "england",
  ni: "northern_ireland",
  northern_ireland: "northern_ireland",
  sct: "scotland",
  scotland: "scotland",
  wls: "wales",
  wales: "wales",
  ireland: "ireland",
  iom: "isle_of_man",
  isle_of_man: "isle_of_man",
  jey: "jersey",
  jersey: "jersey",
  ggy: "guernsey",
  guernsey: "guernsey",
};

// 4 American nations
const americas: Record<string, string> = {
  bra: "brazil",
  mex: "mexico",
  us: "united_states",
  ven: "venezuela",
  us_us_ca: "united_states/california", // compound code hack
};

// Build the baml_src/ rename map (only valid subdirs)
const baml_src: Record<string, string> = {};
for (const [code, name] of Object.entries(europeanNations))
  baml_src[`baml_src/european_nations/${code}`] = `baml_src/european_nations/${name}`;
for (const [code, name] of Object.entries(commonwealth))
  baml_src[`baml_src/commonwealth/${code}`] = `baml_src/commonwealth/${name}`;
for (const [code, name] of Object.entries(canadaProvinces))
  baml_src[`baml_src/commonwealth/can/${code}`] =
    `baml_src/commonwealth/canada/provinces/${name}`;
for (const [code, name] of Object.entries(britishIsles))
  if (code !== "ireland")
    baml_src[`baml_src/education/${code}`] = `baml_src/british_isles/${name}`;
for (const [code, name] of Object.entries(americas)) {
  if (code === "us_us_ca") {
    baml_src[`baml_src/americas/${code}`] = `baml_src/american_nations/united_states`;
  } else {
    baml_src[`baml_src/americas/${code}`] = `baml_src/american_nations/${name}`;
  }
}
// Americas region rename
baml_src["baml_src/americas/_shared"] = "baml_src/american_nations/_shared";
baml_src["baml_src/americas/__init__.baml"] = "baml_src/american_nations/__init__.baml";
baml_src["baml_src/americas/__init__.py"] = "baml_src/american_nations/__init__.py";

// dlt/ rename map
const dlt: Record<string, string> = {};
for (const [code, name] of Object.entries(europeanNations))
  dlt[`dlt/european_nations/${code}`] = `dlt/european_nations/${name}`;
for (const [code, name] of Object.entries(commonwealth))
  dlt[`dlt/commonwealth/${code}`] = `dlt/commonwealth/${name}`;
for (const [code, name] of Object.entries(canadaProvinces))
  dlt[`dlt/commonwealth/can/${code}`] = `dlt/commonwealth/canada/provinces/${name}`;
for (const [code, name] of Object.entries(britishIsles))
  dlt[`dlt/british_isles/${code}`] = `dlt/british_isles/${name}`;
for (const [code, name] of Object.entries(americas))
  dlt[`dlt/americas/${code}`] = `dlt/american_nations/${name}`;

// orchestration/defs/1_ingestion/ rename map
const orchestration: Record<string, string> = {};
for (const [code, name] of Object.entries(europeanNations))
  orchestration[`orchestration/defs/1_ingestion/european_nations/${code}`] =
    `orchestration/defs/1_ingestion/european_nations/${name}`;
for (const [code, name] of Object.entries(commonwealth))
  orchestration[`orchestration/defs/1_ingestion/commonwealth/${code}`] =
    `orchestration/defs/1_ingestion/commonwealth/${name}`;
for (const [code, name] of Object.entries(canadaProvinces))
  orchestration[`orchestration/defs/1_ingestion/commonwealth/can/${code}`] =
    `orchestration/defs/1_ingestion/commonwealth/canada/provinces/${name}`;
for (const [code, name] of Object.entries(britishIsles))
  orchestration[`orchestration/defs/1_ingestion/british_isles/${code}`] =
    `orchestration/defs/1_ingestion/british_isles/${name}`;
for (const [code, name] of Object.entries(americas))
  orchestration[`orchestration/defs/1_ingestion/americas/${code}`] =
    `orchestration/defs/1_ingestion/american_nations/${name}`;

// cocoindex/ rename map (FLAT files + future subdirs)
// Per-jurisdiction education_embedding files
for (const [code, name] of Object.entries(europeanNations))
  dlt[`cocoindex/european_nations_${code}_education_embedding.py`] =
    `cocoindex/european_nations/${name}/education_embedding.py`;
// Cross-jurisdiction apps
dlt[`cocoindex/european_nations_law_embedding.py`] = "cocoindex/european_nations_cross/law_embedding.py";
dlt[`cocoindex/european_nations_medicine_embedding.py`] = "cocoindex/european_nations_cross/medicine_embedding.py";
dlt[`cocoindex/commonwealth_education_embedding.py`] = "cocoindex/commonwealth_cross/education_embedding.py";
// Per-jurisdiction commonwealth
for (const [code, name] of Object.entries(commonwealth))
  dlt[`cocoindex/commonwealth_${code}_education_embedding.py`] =
    `cocoindex/commonwealth/${name}/education_embedding.py`;

// Print as YAML
console.log("baml_src:");
for (const [k, v] of Object.entries(baml_src)) console.log(`  "${k}": "${v}"`);
console.log("\ndlt:");
for (const [k, v] of Object.entries(dlt)) console.log(`  "${k}": "${v}"`);
console.log("\norchestration:");
for (const [k, v] of Object.entries(orchestration)) console.log(`  "${k}": "${v}"`);

console.log("\n--- counts ---");
console.log("baml_src:", Object.keys(baml_src).length);
console.log("dlt:", Object.keys(dlt).length);
console.log("orchestration:", Object.keys(orchestration).length);