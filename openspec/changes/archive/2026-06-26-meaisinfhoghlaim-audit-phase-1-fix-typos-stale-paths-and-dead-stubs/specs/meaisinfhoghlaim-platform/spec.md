## ADDED Requirements

### Requirement: No stale `sruth.oideachas` path references

The meaisínfhoghlaim quadrant MUST NOT contain any reference to
the non-existent package path `sruth.oideachas/` (Irish nominative
"education"). The canonical package name is `sruth/oideachais/`
(Irish genitive "of education"); `sruth/oideachas/` does not
exist. References include but are not limited to docstring
Usage-example code blocks, README examples, and tutorial-style
inline comments.

#### Scenario: A docstring Usage example references the non-existent path

- **GIVEN** a `.py` file under `sruth/meaisinfhoghlaim/` contains a
  docstring with `from sruth.oideachas.X import Y` in a
  Usage-example code block
- **WHEN** the file is committed
- **THEN** `grep -rn "sruth\.oideachas" sruth/meaisinfhoghlaim/`
  returns 0 hits
- **AND** the docstring's Usage example uses the canonical
  `sruth.oideachais.X` path

#### Scenario: A README or AGENTS.md example references the non-existent path

- **GIVEN** a `.md` file under `sruth/meaisinfhoghlaim/` contains
  the substring `sruth/oideachas` or `sruth.oideachas` (other than
  in an explanatory footnote documenting the typo was fixed)
- **WHEN** the file is committed
- **THEN** `grep -rn "sruth/oideachas\|sruth\.oideachas" sruth/meaisinfhoghlaim/*.md sruth/meaisinfhoghlaim/**/*.md`
  returns 0 hits outside an explicit typo-fix footnote

### Requirement: No dead stub modules in `meaisínfhoghlaim`

The meaisínfhoghlaim quadrant MUST NOT contain stand-alone module
files (`.py`) at any depth that have no Python importer anywhere
in the actual codebase (excluding `.venv/`, `__pycache__/`, and
3rd-party `.py` files inside installed packages). A "stub" is a
`.py` file that defines no production behaviour and is not
imported by any production code.

#### Scenario: A dead stub file is left behind after a prototype is abandoned

- **GIVEN** a `.py` file at e.g.
  `sruth/meaisinfhoghlaim/<sub>/<name>.py` is a tiny prototype
  (under 30 lines) that is NOT imported by any other file in
  `sruth/` (excluding `.venv/`, `__pycache__/`, installed
  3rd-party packages)
- **WHEN** the prototype is abandoned without an active consumer
- **THEN** the file is either deleted or wired into a real
  consumer within the same change that creates it
- **AND** `find sruth/meaisinfhoghlaim/ -name "*.py" -size -500c -not -path "*/__init__.py"`
  is reviewed each phase to ensure no new dead stubs were
  introduced

#### Scenario: An empty package directory remains after stubs are deleted

- **GIVEN** the only files in `sruth/meaisinfhoghlaim/<sub>/` are
  stubs that have been deleted
- **WHEN** the deletion is committed
- **THEN** the empty `<sub>/` directory is either removed (if not
  declared a Python package) or has an `__init__.py` (if it must
  remain as a package marker)
- **AND** `ls sruth/meaisinfhoghlaim/<sub>/` returns either empty
  output or contains only `__init__.py`

### Requirement: AGENTS.md BAML reference points to canonical path

`sruth/meaisinfhoghlaim/AGENTS.md` MUST reference the canonical
BAML schema home as `sruth/oideachais/baml_src/` (the actual
on-disk path). The future rename `baml_src → scéimre` was
explicitly deferred per the `lateralise-british-isles-domains`
decision and is documented in
`openspec/specs/meaisinfhoghlaim-platform/spec.md` (Known issues
#5) and `sruth/meaisinfhoghlaim/README.md`. AGENTS.md MUST NOT
forward-reference a non-existent path.

#### Scenario: AGENTS.md is updated after a deferred rename

- **GIVEN** AGENTS.md line ~77 contains
  `sruth/oideachais/scéimre/`
- **WHEN** the deferred rename has not yet been executed
- **THEN** AGENTS.md MUST instead reference
  `sruth/oideachais/baml_src/`
- **AND** the parenthetical explanation MUST note that the
  `baml_src → scéimre` rename is deferred per
  `lateralise-british-isles-domains`
- **AND** `grep -rn "sruth/oideachais/scéimre" sruth/meaisinfhoghlaim/*.md`
  returns 0 hits in the AGENTS.md file (it MAY still appear in
  `sruth/meaisinfhoghlaim/README.md` and the spec as a
  documentation note about the deferred decision)
