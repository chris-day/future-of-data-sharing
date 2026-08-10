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
| `.venv/` | Local virtual environment, ignored by Git |
| `artefacts/GDSN_Current_v3.1.35/` | Source GDSN JSON dump |
| `artefacts/GDSN-TSV-Mapping-v0.1.0.md` | Mapping specification |
| `build/gdsn-tsv/gdsn/` | Generated GDSN TSVs |
| `build/gdsn-tsv/gpc/` | Generated GPC TSVs |
| `artefacts/KATO/add.xml` | Sample GDSN Catalogue Item Notification instance source |
| `build/KATO/` | Generated RDF instances and extension-module reference reports |

## 3. Environment Setup

Use the local virtual environment for all Python work.

If `.venv/` already exists:

```bash
.venv/bin/python --version
```

If it needs to be recreated:

```bash
python3 -m venv .venv
```

Install the local transformer package into the virtual environment:

```bash
.venv/bin/python -m pip install -e .
```

The package uses pinned runtime dependencies in `requirements.txt`, including
`rdflib`, `pyshacl`, `lxml`, and `xml2rfc`.

## 4. Generate TSV Artefacts

Run the full transform from the repository root:

```bash
.venv/bin/gdsn-json-to-tsv --output-dir build/gdsn-tsv
```

Equivalent module form:

```bash
.venv/bin/python -m gdsn_tsv_transformer --output-dir build/gdsn-tsv
```

To generate only the GDSN module and skip the separate GPC module:

```bash
.venv/bin/gdsn-json-to-tsv \
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
- extended code enumerations: `gdsn:extCode_{groupName}`
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

Extended attributes can use generated extended-code enumerations as their
range. If an extended attribute `dataTypeClassName` matches a
`gdsn_extendedCodeValues.json` group, `ClassEnumOrPrimitiveType` is emitted as
`gdsn:extCode_{groupName}`. For example, Carrefour `maximumRange` maps to
`gdsn:extCode_maximumRange` and `voltageRatingCode` maps to
`gdsn:extCode_voltageRatingCode`. Ordinary extended string attributes, such as
Carrefour `additionalTaxAgencyCode` and US FoodService
`notSignificantSourceOfNutrient`, remain `xsd:string`; their source `limit`
values are preserved as `gdsn:originalLimit` annotations rather than converted
to datatype facets.

For normal GDSN class attributes, parseable string limits are represented as
named synthetic datatypes instead of inline `Attributes.tsv` facets. For
example, a primitive string attribute with source `limit = {1..200}` uses
`ClassEnumOrPrimitiveType = gdsn:dt_string_MinLength1_MaxLength200`, with the
`MinLength` and `MaxLength` facets stored on that row in `Datatypes.tsv`. This
keeps OWL property ranges named and avoids anonymous datatype ranges in Protege.

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
.venv/bin/python -m compileall -q src
.venv/bin/python -m unittest tests.test_holon tests.test_xml_to_rdf
.venv/bin/gdsn-json-to-tsv --output-dir build/gdsn-tsv
```

Inspect generated row counts:

```bash
.venv/bin/python - <<'PY'
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

## 11. Generate RDF Instance Graphs

The package installs a GDSN XML instance converter:

```bash
.venv/bin/gdsn-xml-to-rdf --help
```

The repository also includes a standalone wrapper that prefers `.venv`:

```bash
./gdsn-xml-to-rdf --help
```

Generate a separate RDF instance graph from the KATO Catalogue Item
Notification sample:

```bash
./gdsn-xml-to-rdf \
  --input artefacts/KATO/add.xml \
  --gdsn build/gdsn.ttl \
  --gpc build/gpc.ttl \
  --output build/KATO/kato-instances.ttl \
  --extension-report build/KATO/kato-extensions.json \
  --report-json build/KATO/kato-instances.report.json \
  --print-extensions
```

The output file is an instance graph only. It imports no generated ontology
content and does not rewrite `build/gdsn.ttl` or `build/gpc.ttl`.

Current instance mapping scope:

- `catalogueItemNotification`, `catalogueItem`, `catalogueItemState`, and
  child catalogue item links are emitted when `--include-message-envelope` is
  enabled.
- each `tradeItem` is emitted as a `gdsn:TradeItem` instance using the
  ontology property for `gtin`.
- when the XML contains a `gpcCategoryCode` found in `build/gpc.ttl`, the
  trade item is also typed as the corresponding GPC Brick class.
- code-list values are resolved to generated GDSN code-value IRIs where the
  ontology range provides a code-list class.
- ISO 3166 numeric target-market country codes are resolved to ISO country
  resources when present in the generated ontology.

Extension modules are deliberately ignored for RDF generation because their
instance ownership and module-to-core traversal rules need revisiting. The
converter still records what it finds for reference in `--extension-report` and
the summary JSON. In the KATO sample this currently includes delivery
purchasing, trade item description, measurements, variable trade item
information, and child data-carrier details.

To inspect the generated KATO instances in Protege, load `build/gdsn.ttl`,
`build/gpc.ttl`, and `build/KATO/kato-instances.ttl` into the same Protege
session. The following SPARQL query extracts the direct, one-hop, and two-hop
facts associated with GTIN `25196100024882`:

```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gdsn: <urn:gs1:std:gdsn:>
PREFIX gpc:  <urn:gs1:std:gpc:>
PREFIX kato: <urn:gs1:sample:kato:>

SELECT ?subject ?predicate ?predicateLabel ?object ?objectLabel
WHERE {
  VALUES ?root { <urn:gs1:sample:kato:gtin/25196100024882> }

  {
    ?root ?predicate ?object .
    BIND(?root AS ?subject)
  }
  UNION
  {
    ?root ?link ?subject .
    ?subject ?predicate ?object .
  }
  UNION
  {
    ?root ?link1 ?mid .
    ?mid ?link2 ?subject .
    ?subject ?predicate ?object .
  }

  OPTIONAL { ?predicate rdfs:label ?predicateLabel . }
  OPTIONAL { ?object rdfs:label ?objectLabel . }
}
ORDER BY ?subject ?predicate ?object
```

Use the same pattern for the child GTIN `25196100024899`:

```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gdsn: <urn:gs1:std:gdsn:>
PREFIX gpc:  <urn:gs1:std:gpc:>

SELECT ?subject ?predicate ?predicateLabel ?object ?objectLabel
WHERE {
  VALUES ?root { <urn:gs1:sample:kato:gtin/25196100024899> }

  {
    ?root ?predicate ?object .
    BIND(?root AS ?subject)
  }
  UNION
  {
    ?root ?link ?subject .
    ?subject ?predicate ?object .
  }
  UNION
  {
    ?root ?link1 ?mid .
    ?mid ?link2 ?subject .
    ?subject ?predicate ?object .
  }

  OPTIONAL { ?predicate rdfs:label ?predicateLabel . }
  OPTIONAL { ?object rdfs:label ?objectLabel . }
}
ORDER BY ?subject ?predicate ?object
```

To retrieve the GPC attribute slots and allowed values that would be used in a
Holon SHACL shape for GTIN `25196100024882`, query the trade item's level-4
Brick, then its level-5 Attribute Types and level-6 Attribute Values:

```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gpc:  <urn:gs1:std:gpc:>

SELECT ?brick ?brickLabel ?attributeType ?attributeTypeLabel ?allowedValue ?allowedValueLabel
WHERE {
  VALUES ?tradeItem { <urn:gs1:sample:kato:gtin/25196100024882> }

  ?tradeItem rdf:type ?brick .
  ?brick gpc:level 4 .
  OPTIONAL { ?brick rdfs:label ?brickLabel . }

  ?attributeType rdfs:subClassOf ?brick .
  ?attributeType gpc:level 5 .
  OPTIONAL { ?attributeType rdfs:label ?attributeTypeLabel . }

  ?allowedValue rdfs:subClassOf ?attributeType .
  ?allowedValue gpc:level 6 .
  OPTIONAL { ?allowedValue rdfs:label ?allowedValueLabel . }
}
ORDER BY ?attributeTypeLabel ?allowedValueLabel
```

Useful options:

| Option | Purpose |
|---|---|
| `--input` | Source GDSN XML file |
| `--gdsn` | Generated GDSN ontology used for class, property, datatype, and code-list lookup |
| `--gpc` | Generated GPC ontology used for Brick typing |
| `--output` | RDF instance output; omit to write RDF to stdout |
| `--format` | RDF serialisation: `turtle`, `xml`, `nt`, or `json-ld` |
| `--base-iri` | Base IRI for generated instance resources |
| `--prefix` | Prefix bound to `--base-iri` |
| `--extension-report` | JSON file containing ignored extension-module values |
| `--print-extensions` | Print a concise extension-module summary |
| `--report-json` | JSON conversion report with trade items, diagnostics, and validation status |
| `--no-validate` | Skip RDF parse validation of generated output |
| `--include-message-envelope` / `--no-include-message-envelope` | Include or omit notification/catalogue item envelope instances |

## 12. Generate SHACL Holon Shapes

The package also installs a SHACL generator executable:

```bash
.venv/bin/gs1-gdsn-holon --help
```

The repository also includes a standalone wrapper that prefers the local
virtual environment and can be run directly:

```bash
./gs1-gdsn-holon --help
```

Generate a GPC Brick SHACL shape from a Brick code:

```bash
./gs1-gdsn-holon 10000030 > build/shacl/gpc-brick-10000030.shacl.ttl
```

When `--output` is omitted, SHACL Turtle is written to standard output and
the JSON summary plus validation result are written to standard error.

```bash
./gs1-gdsn-holon 10000030 \
  --gpc build/gpc.ttl \
  --output build/shacl/gpc-brick-10000030.shacl.ttl \
  --write-tests \
  --report-json build/shacl/gpc-brick-10000030.report.json
```

Example for Brick `10000043`, Sugar/Sugar Substitutes Shelf Stable:

```bash
./gs1-gdsn-holon 10000043 \
  --gpc build/gpc.ttl \
  --output build/shacl/gpc-brick-10000043.shacl.ttl \
  --write-tests \
  --report-json build/shacl/gpc-brick-10000043.report.json
```

Generate a Brick shape and include the optional GDSN cross-category
`TradeItemGDSNShape`:

```bash
./gs1-gdsn-holon 10001198 \
  --gpc build/gpc.ttl \
  --gdsn build/gdsn.ttl \
  --include-gdsn \
  --output build/shacl/gpc-brick-10001198-with-gdsn.shacl.ttl \
  --write-tests \
  --report-json build/shacl/gpc-brick-10001198-with-gdsn.report.json
```

When `--include-gdsn` is used, `TradeItemGDSNShape` also includes a GPC
classification bridge from `gdsn:TradeItem` to the selected Brick code:

```turtle
sh:path (
  gdsn:assoc_863999331_-1698192853_1
  gdsn:a289210221
) ;
sh:hasValue "10001198" ;
sh:minCount 1 ;
sh:maxCount 1 .
```

The object-property leg of this bridge is discovered with SPARQL over the
generated ontology axioms, using `rdfs:domain`, `rdfs:range`,
`rdfs:subClassOf*`, and `owl:ObjectProperty`.

Use `--print-traversal` to display the ontology paths used by the holon:

```bash
./gs1-gdsn-holon 09506000134352 \
  --input-kind gtin \
  --gtin-map product-gpc-map.csv \
  --gdsn build/gdsn.ttl \
  --print-traversal \
  --output build/shacl/gtin-09506000134352-with-gdsn.shacl.ttl
```

Example traversal output:

```text
GPC classification attribute traversal
TradeItem
  -> gDSNTradeItemClassification
     GDSNTradeItemClassification
  -> gDSNTradeItemClassificationAttribute
     GDSNTradeItemClassificationAttribute
```

When `--output` is omitted, SHACL Turtle is written to stdout and traversal
details are written to stderr.

When the command input is a GTIN, `TradeItemGDSNShape` also includes a GTIN
identity bridge on the root trade item GTIN property:

```turtle
sh:path gdsn:a5339 ;
sh:hasValue "09506000134352"^^gdsn:c1450 ;
sh:minCount 1 ;
sh:maxCount 1 .
```

Example for Brick `10000043` with the optional GDSN cross-category shape:

```bash
./gs1-gdsn-holon 10000043 \
  --gpc build/gpc.ttl \
  --gdsn build/gdsn.ttl \
  --include-gdsn \
  --output build/shacl/gpc-brick-10000043-with-gdsn.shacl.ttl
```

For GTIN input, the ontology alone is not enough to resolve product
classification. Supply either a resolved Brick code:

```bash
./gs1-gdsn-holon 09506000134352 \
  --input-kind gtin \
  --brick-code 10000030 \
  --output build/shacl/gtin-09506000134352.shacl.ttl
```

Or supply a local CSV or JSON lookup file:

```bash
./gs1-gdsn-holon 09506000134352 \
  --input-kind gtin \
  --gtin-map product-gpc-map.csv \
  --gtin-column gtin \
  --brick-column brickCode \
  --output build/shacl/gtin-09506000134352.shacl.ttl
```

When RDF instance data is available, `gs1-gdsn-holon` can generate an
instance-aware holon. This mode resolves the selected GTIN resource from the
instance base IRI, discovers reachable outgoing GDSN objects and properties,
and emits nested SHACL node shapes using the generated GDSN ontology for
property names, ranges, datatypes, classes, multiplicities, and code-list
constraints.

Example for the KATO parent GTIN:

```bash
./gs1-gdsn-holon 25196100024882 \
  --input-kind gtin \
  --instance-data build/KATO/kato-instances.ttl \
  --instance-base-iri urn:gs1:sample:kato: \
  --gpc build/gpc.ttl \
  --gdsn build/gdsn.ttl \
  --include-gdsn \
  --include-instance-objects \
  --output build/shacl/kato-25196100024882-holon.shacl.ttl \
  --report-json build/shacl/kato-25196100024882-holon.report.json
```

In this mode, the GDSN shape uses `sh:targetNode` for the selected instance
instead of `sh:targetClass gdsn:TradeItem`, so a GTIN-specific holon does not
accidentally target every trade item in the loaded data graph. The validation
step runs pySHACL against the supplied instance graph plus the loaded GDSN and
GPC ontology context.

The KATO instance-aware holon currently discovers and shapes the parent
`TradeItem`, `GDSNTradeItemClassification`, `TargetMarket`,
`TradeItemSynchronisationDates`, `NextLowerLevelTradeItemInformation`,
`ChildTradeItem`, and the reachable `PartyInRole` objects. Extension modules
remain excluded until their ownership and traversal rules are revisited.

The default `--instance-max-depth 4` covers the theoretical outgoing
object-property depth from `gdsn:TradeItem` in the generated GDSN ontology. In
the KATO instance data the actual outgoing depth is smaller: GTIN
`25196100024882` reaches all outgoing product-instance GDSN resources by depth
2, and GTIN `25196100024899` reaches all outgoing product-instance GDSN
resources by depth 1. Depth 4 therefore covers all outgoing GTIN-rooted product
data in `build/KATO/kato-instances.ttl`.

This does not include inverse or envelope context such as `CatalogueItem`,
`CatalogueItemState`, `CatalogueItemChildItemLink`, and
`CatalogueItemNotification`. Those resources wrap or point to the TradeItem
rather than being outgoing product objects from it. A catalogue-notification
holon should use a separate inverse/envelope traversal mode if that context is
needed.

By default, `gs1-gdsn-holon` validates the generated SHACL with pySHACL:

- parse-only via RDFLib Turtle parsing
- empty graph validation
- one conforming in-memory test instance
- one deliberately broken in-memory test instance

When `--include-instance-objects` is used, validation is against the supplied
instance graph instead of the synthetic in-memory examples.

Use `--no-validate` only when generating shapes in a context where validation
cost is not acceptable.

## 13. Maintenance

When changing the transformer:

1. Update `src/gdsn_tsv_transformer/cli.py`.
2. Update `src/gdsn_tsv_transformer/holon.py` when changing SHACL generation.
3. Update `src/gdsn_tsv_transformer/xml_to_rdf.py` when changing XML instance
   generation.
4. Keep `artefacts/GDSN-TSV-Mapping-v0.1.0.md` aligned with implemented
   mapping decisions.
5. Run `.venv/bin/python -m compileall -q src tests`.
6. Run `.venv/bin/python -m unittest tests.test_holon tests.test_xml_to_rdf`.
7. Regenerate TSVs with `.venv/bin/gdsn-json-to-tsv --output-dir build/gdsn-tsv`.
8. Review `build/gdsn-tsv/gdsn/diagnostics.tsv`.
9. Run the `uml2semantics` commands for both modules.
10. Run representative SHACL generation with `./gs1-gdsn-holon`.
11. Run representative instance generation with `./gdsn-xml-to-rdf`.

If third-party Python dependencies are added later, update `requirements.txt`
with pinned package versions.
