<!--
Document: GDSN TSV Transformer README
Version: v0.1.0
Status: Draft implementation guide
Date: 2026-07-24
-->

# GDSN TSV Transformer

**Version:** v0.1.0

This document explains how to use the local Python transformer that converts
the GDSN UML JSON dump into TSV artefacts accepted by
`uml2semantics-python`.

The implementation follows:

- `artefacts/GDSN-TSV-Mapping-v0.1.0.md`
- the GDSN JSON dump in `artefacts/GDSN_Current_v3.1.35`
- the `uml2semantics-python` TSV specification:
  https://github.com/chris-day/uml2semantics-python/wiki/TSV-Specification

## 1. Purpose

The transformer generates two TSV modules:

1. **GDSN model TSVs** using the `gdsn:` namespace.
2. **GPC taxonomy TSVs** using the `gpc:` namespace.

The generated TSVs can then be passed to `uml2semantics-python` to produce OWL
or RDF serialisations.

## 2. Repository Layout

Important files and directories:

| Path | Purpose |
|---|---|
| `src/gdsn_tsv_transformer/` | Python package source |
| `pyproject.toml` | Package metadata and executable entry point |
| `requirements.txt` | Maintained package list |
| `venv/` | Local virtual environment, ignored by Git |
| `artefacts/GDSN_Current_v3.1.35/` | Source GDSN JSON dump |
| `artefacts/GDSN-TSV-Mapping-v0.1.0.md` | Mapping specification |
| `build/gdsn-tsv/gdsn/` | Generated GDSN TSVs |
| `build/gdsn-tsv/gpc/` | Generated GPC TSVs |

## 3. Environment Setup

Use the local virtual environment for all Python work.

If `venv/` already exists:

```bash
venv/bin/python --version
```

If it needs to be recreated:

```bash
python3 -m venv venv
```

Install the local transformer package into the virtual environment:

```bash
venv/bin/python -m pip install -e .
```

The package has no third-party runtime dependencies at v0.1.0.

## 4. Generate TSV Artefacts

Run the full transform from the repository root:

```bash
venv/bin/gdsn-json-to-tsv --output-dir build/gdsn-tsv
```

Equivalent module form:

```bash
venv/bin/python -m gdsn_tsv_transformer --output-dir build/gdsn-tsv
```

To generate only the GDSN module and skip the separate GPC module:

```bash
venv/bin/gdsn-json-to-tsv \
  --input-dir artefacts/GDSN_Current_v3.1.35 \
  --output-dir build/gdsn-tsv \
  --skip-gpc
```

## 5. Generated GDSN TSVs

The GDSN output directory is:

```text
build/gdsn-tsv/gdsn/
```

It contains:

- `Classes.tsv`
- `Attributes.tsv`
- `Datatypes.tsv`
- `Enumerations.tsv`
- `EnumerationNamedValues.tsv`
- `AnnotationProperties.tsv`
- `Annotations.tsv`
- `diagnostics.tsv`

The generated model uses stable source-ID based CURIEs:

- classes and datatypes: `gdsn:c{id}`
- attributes: `gdsn:a{id}`
- code values: `gdsn:cv{id}`
- association properties: `gdsn:assoc_{sourceClassId}_{destinationClassId}_{index}`
- synthetic AVP container: `gdsn:GDSNAVP`
- synthetic extended attribute container: `gdsn:GDSNExtendedAttribute`

## 6. Generated GPC TSVs

The GPC output directory is:

```text
build/gdsn-tsv/gpc/
```

It contains the same TSV file set, but only the relevant files are populated.
The GPC hierarchy is represented as a separate ontology module using `gpc:`
CURIEs, with hierarchy encoded through class parent relationships.

## 7. Diagnostics

Each module includes:

```text
diagnostics.tsv
```

For GDSN, diagnostics capture conversion warnings such as:

- malformed multiplicities left blank in `Attributes.tsv`
- limits that could not be safely converted to datatype facets
- missing code-list class records
- type-3 details preserved outside datatype facets

Malformed multiplicities are not guessed. The transformer leaves
`MinMultiplicity` and `MaxMultiplicity` blank, preserves the original value as
`gdsn:originalMultiplicity`, and emits `gdsn:conversionWarning`.

## 8. Build the GDSN Ontology

After generating TSVs, run `uml2semantics-python` against the GDSN module.

If `uml2semantics` is available on `PATH`:

```bash
uml2semantics \
  --classes build/gdsn-tsv/gdsn/Classes.tsv \
  --attributes build/gdsn-tsv/gdsn/Attributes.tsv \
  --datatypes build/gdsn-tsv/gdsn/Datatypes.tsv \
  --enumerations build/gdsn-tsv/gdsn/Enumerations.tsv \
  --enum-values build/gdsn-tsv/gdsn/EnumerationNamedValues.tsv \
  --annotation-properties build/gdsn-tsv/gdsn/AnnotationProperties.tsv \
  --annotations build/gdsn-tsv/gdsn/Annotations.tsv \
  --output build/gdsn.ttl \
  --ontology-iri gdsn:Ontology \
  --prefixes "gdsn:gdsn:,gpc:gpc:,iso3166:iso3166:,xsd:http://www.w3.org/2001/XMLSchema#,dct:http://purl.org/dc/terms#,owl:http://www.w3.org/2002/07/owl#" \
  --format turtle \
  --profile generic
```

If using a local checkout of `uml2semantics-python`, replace `uml2semantics`
with that environment's executable, for example:

```bash
/var/software/gitrepos/uml2semantics-python/.venv/bin/uml2semantics \
  --classes build/gdsn-tsv/gdsn/Classes.tsv \
  --attributes build/gdsn-tsv/gdsn/Attributes.tsv \
  --datatypes build/gdsn-tsv/gdsn/Datatypes.tsv \
  --enumerations build/gdsn-tsv/gdsn/Enumerations.tsv \
  --enum-values build/gdsn-tsv/gdsn/EnumerationNamedValues.tsv \
  --annotation-properties build/gdsn-tsv/gdsn/AnnotationProperties.tsv \
  --annotations build/gdsn-tsv/gdsn/Annotations.tsv \
  --output build/gdsn.ttl \
  --ontology-iri gdsn:Ontology \
  --prefixes "gdsn:gdsn:,gpc:gpc:,iso3166:iso3166:,xsd:http://www.w3.org/2001/XMLSchema#,dct:http://purl.org/dc/terms#,owl:http://www.w3.org/2002/07/owl#" \
  --format turtle \
  --profile generic
```

## 9. Build the GPC Ontology

Run `uml2semantics-python` against the separate GPC module:

```bash
uml2semantics \
  --classes build/gdsn-tsv/gpc/Classes.tsv \
  --attributes build/gdsn-tsv/gpc/Attributes.tsv \
  --datatypes build/gdsn-tsv/gpc/Datatypes.tsv \
  --enumerations build/gdsn-tsv/gpc/Enumerations.tsv \
  --enum-values build/gdsn-tsv/gpc/EnumerationNamedValues.tsv \
  --annotation-properties build/gdsn-tsv/gpc/AnnotationProperties.tsv \
  --annotations build/gdsn-tsv/gpc/Annotations.tsv \
  --output build/gpc.ttl \
  --ontology-iri gpc:Ontology \
  --prefixes "gpc:gpc:,gdsn:gdsn:,xsd:http://www.w3.org/2001/XMLSchema#,dct:http://purl.org/dc/terms#" \
  --format turtle \
  --profile generic
```

The GPC module currently has empty attributes, datatypes, enumerations, and
named values TSVs. They are still passed explicitly so the command remains
stable if those files are populated later.

## 10. Validation Checks

Basic transformer checks:

```bash
venv/bin/python -m compileall -q src
venv/bin/python -m unittest tests.test_holon
venv/bin/gdsn-json-to-tsv --output-dir build/gdsn-tsv
```

Inspect generated row counts:

```bash
venv/bin/python - <<'PY'
import csv
from pathlib import Path

for base in [Path("build/gdsn-tsv/gdsn"), Path("build/gdsn-tsv/gpc")]:
    print(base)
    for path in sorted(base.glob("*.tsv")):
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            next(reader, [])
            print(path.name, sum(1 for _ in reader))
PY
```

## 11. Generate SHACL Holon Shapes

The package also installs a SHACL generator executable:

```bash
venv/bin/gs1-gsdn-holon --help
```

The repository also includes a standalone wrapper that prefers the local
virtual environment and can be run directly:

```bash
./gs1-gsdn-holon --help
```

Generate a GPC Brick SHACL shape from a Brick code:

```bash
./gs1-gsdn-holon 10000030 \
  --gpc build/gpc.ttl \
  --output build/shacl/gpc-brick-10000030.shacl.ttl \
  --write-tests \
  --report-json build/shacl/gpc-brick-10000030.report.json
```

Example for Brick `10000043`, Sugar/Sugar Substitutes Shelf Stable:

```bash
./gs1-gsdn-holon 10000043 \
  --gpc build/gpc.ttl \
  --output build/shacl/gpc-brick-10000043.shacl.ttl \
  --write-tests \
  --report-json build/shacl/gpc-brick-10000043.report.json
```

Generate a Brick shape and include the optional GDSN cross-category
`TradeItemGDSNShape`:

```bash
./gs1-gsdn-holon 10001198 \
  --gpc build/gpc.ttl \
  --gdsn build/gdsn.ttl \
  --include-gdsn \
  --output build/shacl/gpc-brick-10001198-with-gdsn.shacl.ttl \
  --write-tests \
  --report-json build/shacl/gpc-brick-10001198-with-gdsn.report.json
```

Example for Brick `10000043` with the optional GDSN cross-category shape:

```bash
./gs1-gsdn-holon 10000043 \
  --gpc build/gpc.ttl \
  --gdsn build/gdsn.ttl \
  --include-gdsn \
  --output build/shacl/gpc-brick-10000043-with-gdsn.shacl.ttl
```

For GTIN input, the ontology alone is not enough to resolve product
classification. Supply either a resolved Brick code:

```bash
./gs1-gsdn-holon 09506000134352 \
  --input-kind gtin \
  --brick-code 10000030 \
  --output build/shacl/gtin-09506000134352.shacl.ttl
```

Or supply a local CSV or JSON lookup file:

```bash
./gs1-gsdn-holon 09506000134352 \
  --input-kind gtin \
  --gtin-map product-gpc-map.csv \
  --gtin-column gtin \
  --brick-column brickCode \
  --output build/shacl/gtin-09506000134352.shacl.ttl
```

By default, `gs1-gsdn-holon` validates the generated SHACL with pySHACL:

- parse-only via RDFLib Turtle parsing
- empty graph validation
- one conforming in-memory test instance
- one deliberately broken in-memory test instance

Use `--no-validate` only when generating shapes in a context where validation
cost is not acceptable.

## 12. Maintenance

When changing the transformer:

1. Update `src/gdsn_tsv_transformer/cli.py`.
2. Update `src/gdsn_tsv_transformer/holon.py` when changing SHACL generation.
3. Keep `artefacts/GDSN-TSV-Mapping-v0.1.0.md` aligned with implemented
   mapping decisions.
4. Run `venv/bin/python -m compileall -q src`.
5. Run `venv/bin/python -m unittest tests.test_holon`.
6. Regenerate TSVs with `venv/bin/gdsn-json-to-tsv --output-dir build/gdsn-tsv`.
7. Review `build/gdsn-tsv/gdsn/diagnostics.tsv`.
8. Run the `uml2semantics` commands for both modules.
9. Run representative SHACL generation with `./gs1-gsdn-holon`.

If third-party Python dependencies are added later, update `requirements.txt`
with pinned package versions.
