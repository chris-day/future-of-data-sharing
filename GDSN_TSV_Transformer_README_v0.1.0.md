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

Source class `type` values are interpreted as:

| Type | Meaning | Main TSV treatment |
|---:|---|---|
| `1` | Data class / primitive | Reference as `xsd:` primitive or primitive-backed range |
| `2` | Real class | Emit to `Classes.tsv` |
| `3` | GS1-defined datatype | Emit to `Datatypes.tsv` |
| `4` | Code list | Emit to `Enumerations.tsv` |
| `5` | Enumeration | Emit to `Enumerations.tsv` |
| `6` | Message | Emit only when present and needed for message-level modelling |

## 6. Generated GPC TSVs

The GPC output directory is:

```text
build/gdsn-tsv/gpc/
```

It contains the same TSV file set, but only the relevant files are populated.
The GPC hierarchy is represented as a separate ontology module using `gpc:`
CURIEs, with hierarchy encoded through class parent relationships.

## 7. Generated Google Product Taxonomy TSVs

The Google Product Taxonomy output directory is:

```text
build/gdsn-tsv/google/
```

Generate it from the Google text taxonomy with:

```bash
.venv/bin/google-taxonomy-to-tsv \
  --input-file artefacts/google/taxonomy-with-ids.en-GB.txt \
  --output-dir build/gdsn-tsv
```

The Google taxonomy is represented as a separate ontology module using
`google:` CURIEs, with hierarchy encoded through class parent relationships.
See `Google_Product_Taxonomy.md` for the semantic mapping notes.

## 8. Diagnostics

Each module includes:

```text
diagnostics.tsv
```

For GDSN, diagnostics capture conversion warnings such as:

- malformed multiplicities left blank in `Attributes.tsv`
- limits that could not be safely converted to datatype facets
- missing code-list class records
- structured type-3 value classes emitted to `Classes.tsv`

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

## 9. Build the GDSN Ontology

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

## 10. Build the GPC Ontology

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

## 11. GraphDB Import Named Graphs

The generated Turtle files are ordinary RDF graphs. They do not contain named
graph wrappers; the named graph is assigned by GraphDB at import time.

Recommended GraphDB import sequence:

1. Import `build/gpc.ttl`.
2. Import `build/gdsn.ttl`.
3. Import `build/google-product-taxonomy.ttl`, if using Google Product
   Taxonomy.
4. Import `build/KATO/kato-instances.ttl`, if using KATO instance data.
5. Load generated SHACL shapes separately for validation, not as ontology
   schema.

Recommended named graphs:

| File | Named graph |
| --- | --- |
| `build/gpc.ttl` | `urn:gs1:std:gpc:` |
| `build/gdsn.ttl` | `urn:gs1:std:gdsn:` |
| `build/google-product-taxonomy.ttl` | `urn:google:product-taxonomy:` |
| `build/KATO/kato-instances.ttl` | `urn:gs1:sample:kato:ontology` |
| generated holon SHACL shapes | `urn:gs1:shapes:gpc:` |

The KATO instance file declares ontology imports for GDSN and GPC, but those
imports are ontology triples, not GraphDB named graph declarations. In GraphDB,
choose the target named graph during import or via the import API.

For KATO product instances generated with base IRI `urn:gs1:sample:kato:`, the
sample GTIN resources are:

```text
urn:gs1:sample:kato:gtin/25196100024882
urn:gs1:sample:kato:gtin/25196100024899
```

## 12. Validation Checks

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

## 13. Generate RDF Instance Graphs

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

The KATO sample contains these GTIN trade item instances:

| GTIN | Generated instance URN |
| --- | --- |
| `25196100024882` | `urn:gs1:sample:kato:gtin/25196100024882` |
| `25196100024899` | `urn:gs1:sample:kato:gtin/25196100024899` |

The output file is an instance graph only. It does not embed or rewrite
`build/gdsn.ttl` or `build/gpc.ttl`; instead, the generated instance ontology
imports the reusable GDSN and GPC ontology IRIs:

```turtle
kato:ontology a owl:Ontology ;
  owl:imports
    <urn:gs1:std:gdsn:> ,
    <urn:gs1:std:gpc:> .
```

In Protege, map those import IRIs to the local `gdsn.ttl` and `gpc.ttl` files
through the ontology catalog.

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
- supported extension modules are attached below `TradeItemInformation` through
  the synthetic `gdsn:extensionModule` object property.
- structured type-3 values are emitted as typed value nodes. For example,
  `functionalName` points to a `gdsn:c1441` node with language-tagged
  `rdf:value` and `languageCode`; measurements point to `gdsn:c1490` nodes
  with decimal `rdf:value` and `measurementUnitCode`.

The value-node pattern preserves XML qualifiers that would be lost if the
converter emitted only datatype literals. A KATO height such as
`<height measurementUnitCode="MMT">1</height>` becomes:

```turtle
<urn:gs1:sample:kato:value/25196100024899/height>
  a gdsn:c1490 ;
  rdf:value "1.0"^^xsd:decimal ;
  gdsn:a7085 "MMT"^^xsd:string .
```

Instance literals are emitted with primitive RDF datatypes such as
`xsd:string`, `xsd:decimal`, and `xsd:dateTime` for SHACL and tool
interoperability. The generated GDSN ontology still declares the richer GDSN
datatype range, and the holon report retains that source range.

The generated GDSN TSVs include a synthetic `gdsn:GDSNExtensionModule`
superclass and `gdsn:extensionModule` property. Module classes are detected
from the JSON dump using these rules:

1. inspect `gdsn_instances.json` for class rows whose `xPath` contains
   `/tradeItemInformation/extension/*`;
2. filter those rows to type-2 classes whose source class name ends in
   `Module`;
3. add module-like type-2 classes with names ending in `Module` that have no
   extension-root XPath. In v3.1.35 this adds
   `FoodAndBeveragePropertiesInformationModule`, giving 77 module classes.

Class `1297183996` is the datatype named `extension`; it has no class
`extensions` records. The concrete module roots are identified from
`gdsn_instances.json`, using the `TradeItemInformation.extension` attribute as
the core bridge point. Detected module classes are made subclasses of
`gdsn:GDSNExtensionModule`, so instance traversal can move from `TradeItem` to
`TradeItemInformation` and then to any implemented concrete module.

The KATO converter currently materialises these extension modules:

| XML module | GDSN path emitted |
| --- | --- |
| `deliveryPurchasingInformationModule` | `TradeItemInformation -> extensionModule -> DeliveryPurchasingInformationModule -> deliveryPurchasingInformation -> DeliveryPurchasingInformation -> startAvailabilityDateTime` |
| `tradeItemDescriptionModule` | `TradeItemInformation -> extensionModule -> TradeItemDescriptionModule -> tradeItemDescriptionInformation -> TradeItemDescriptionInformation -> functionalName`, plus `brandNameInformation -> BrandNameInformation -> brandName` |
| `tradeItemMeasurementsModule` | `TradeItemInformation -> extensionModule -> TradeItemMeasurementsModule -> tradeItemMeasurements -> TradeItemMeasurements -> depth/height/netContent/width`, plus `tradeItemWeight -> TradeItemWeight -> grossWeight` |
| `tradeItemDataCarrierAndIdentificationModule` | `TradeItemInformation -> extensionModule -> TradeItemDataCarrierAndIdentificationModule -> dataCarrier -> DataCarrier -> dataCarrierTypeCode` |

`--extension-report` still records every extension module found in the XML. In
the KATO sample, `variableTradeItemInformationModule` is currently report-only
and is not yet emitted as RDF instance data.

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

To retrieve both KATO GTINs with reachable instance properties, values, and
ontology labels/comments for clarity, use this Protege-compatible query. It
uses full GTIN IRIs rather than `kato:` prefixed local names because some
Protege SPARQL parsers reject `/` in prefixed local names.

```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gdsn: <urn:gs1:std:gdsn:>
PREFIX gpc:  <urn:gs1:std:gpc:>

SELECT DISTINCT
  ?gtin
  ?subject
  ?subjectType
  ?subjectTypeLabel
  ?property
  ?propertyLabel
  ?propertyComment
  ?value
  ?valueType
  ?valueLabel
  ?valueComment
WHERE {
  VALUES ?root {
    <urn:gs1:sample:kato:gtin/25196100024882>
    <urn:gs1:sample:kato:gtin/25196100024899>
  }

  ?root gdsn:a5339 ?gtin .

  {
    BIND(?root AS ?subject)
    ?subject ?property ?value .
  }
  UNION
  {
    ?root ?p1 ?subject .
    ?subject ?property ?value .
  }
  UNION
  {
    ?root ?p1 ?n1 .
    ?n1 ?p2 ?subject .
    ?subject ?property ?value .
  }
  UNION
  {
    ?root ?p1 ?n1 .
    ?n1 ?p2 ?n2 .
    ?n2 ?p3 ?subject .
    ?subject ?property ?value .
  }
  UNION
  {
    ?root ?p1 ?n1 .
    ?n1 ?p2 ?n2 .
    ?n2 ?p3 ?n3 .
    ?n3 ?p4 ?subject .
    ?subject ?property ?value .
  }

  OPTIONAL { ?subject rdf:type ?subjectType . }
  OPTIONAL { ?subjectType rdfs:label ?subjectTypeLabel . }

  OPTIONAL { ?property rdfs:label ?propertyLabel . }
  OPTIONAL { ?property rdfs:comment ?propertyComment . }

  OPTIONAL { ?value rdf:type ?valueType . }
  OPTIONAL { ?value rdfs:label ?valueLabel . }
  OPTIONAL { ?value rdfs:comment ?valueComment . }

  FILTER(?property != rdf:type)
}
ORDER BY ?gtin ?subject ?property ?value
```

To retrieve the underlying source data used for the Holons of both KATO sample
GTINs, use this combined query. It returns the GTIN-rooted GDSN instance facts
and the GPC Brick attribute/value slots that feed the GPC part of the Holon
shape.

```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gdsn: <urn:gs1:std:gdsn:>
PREFIX gpc:  <urn:gs1:std:gpc:>

SELECT DISTINCT
  ?section
  ?gtin
  ?brick
  ?brickLabel
  ?subject
  ?subjectType
  ?subjectTypeLabel
  ?property
  ?propertyLabel
  ?propertyComment
  ?value
  ?valueType
  ?valueLabel
  ?valueComment
  ?attributeType
  ?attributeTypeLabel
  ?allowedValue
  ?allowedValueLabel
WHERE {
  VALUES ?root {
    <urn:gs1:sample:kato:gtin/25196100024882>
    <urn:gs1:sample:kato:gtin/25196100024899>
  }

  ?root gdsn:a5339 ?gtin .

  OPTIONAL {
    ?root rdf:type ?brick .
    ?brick gpc:level 4 .
    OPTIONAL { ?brick rdfs:label ?brickLabel . }
  }

  {
    BIND("GDSN instance fact" AS ?section)

    {
      BIND(?root AS ?subject)
      ?subject ?property ?value .
    }
    UNION
    {
      ?root ?p1 ?subject .
      ?subject ?property ?value .
    }
    UNION
    {
      ?root ?p1 ?n1 .
      ?n1 ?p2 ?subject .
      ?subject ?property ?value .
    }
    UNION
    {
      ?root ?p1 ?n1 .
      ?n1 ?p2 ?n2 .
      ?n2 ?p3 ?subject .
      ?subject ?property ?value .
    }
    UNION
    {
      ?root ?p1 ?n1 .
      ?n1 ?p2 ?n2 .
      ?n2 ?p3 ?n3 .
      ?n3 ?p4 ?subject .
      ?subject ?property ?value .
    }

    FILTER(?property != rdf:type)

    OPTIONAL { ?subject rdf:type ?subjectType . }
    OPTIONAL { ?subjectType rdfs:label ?subjectTypeLabel . }

    OPTIONAL { ?property rdfs:label ?propertyLabel . }
    OPTIONAL { ?property rdfs:comment ?propertyComment . }

    OPTIONAL { ?value rdf:type ?valueType . }
    OPTIONAL { ?value rdfs:label ?valueLabel . }
    OPTIONAL { ?value rdfs:comment ?valueComment . }
  }
  UNION
  {
    BIND("GPC holon attribute/value" AS ?section)

    ?root rdf:type ?brick .
    ?brick gpc:level 4 .
    OPTIONAL { ?brick rdfs:label ?brickLabel . }

    ?attributeType rdfs:subClassOf ?brick .
    ?attributeType gpc:level 5 .
    OPTIONAL { ?attributeType rdfs:label ?attributeTypeLabel . }

    ?allowedValue rdfs:subClassOf ?attributeType .
    ?allowedValue gpc:level 6 .
    OPTIONAL { ?allowedValue rdfs:label ?allowedValueLabel . }
  }
}
ORDER BY ?gtin ?section ?subject ?property ?attributeTypeLabel ?allowedValueLabel
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
| `--gdsn-import-iri` | GDSN ontology IRI imported by the generated instance ontology |
| `--gpc-import-iri` | GPC ontology IRI imported by the generated instance ontology |
| `--extension-report` | JSON file containing all extension-module values found in the source XML |
| `--print-extensions` | Print a concise extension-module summary |
| `--report-json` | JSON conversion report with trade items, diagnostics, and validation status |
| `--no-validate` | Skip RDF parse validation of generated output |
| `--include-message-envelope` / `--no-include-message-envelope` | Include or omit notification/catalogue item envelope instances |

## 14. Generate SHACL Holon Shapes

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
sh:hasValue "09506000134352"^^xsd:string ;
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

The sample `product-gpc-map.csv` contains these holon examples:

| GTIN | GPC Brick | Brick label |
| --- | --- | --- |
| `09506000134352` | `10000030` | Cheese (Frozen) |
| `00195950643718` | `10001198` | Smartphones |
| `00083783000085` | `10000159` | Beer |
| `04005500023340` | `10000043` | Sugar/Sugar Substitutes (Shelf Stable) |
| `05000119096753` | `10000217` | Jams/Marmalades (Shelf Stable) |
| `05000169015254` | `10000025` | Milk (Perishable) |
| `25196100024882` | `10000002` | Fruit - Unprepared/Unprocessed (Frozen) |
| `25196100024899` | `10000002` | Fruit - Unprepared/Unprocessed (Frozen) |

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
`ChildTradeItem`, reachable `PartyInRole` objects, and implemented extension
modules reached through `TradeItemInformation -> extensionModule`.

The default `--instance-max-depth 5` covers the outgoing product-instance depth
used by the generated KATO graph, including structured type-3 value nodes. The
longest implemented KATO path is:

```text
TradeItem
  -> tradeItemInformation
  -> extensionModule
  -> tradeItemMeasurements
  -> tradeItemWeight
  -> grossWeight value node
```

Depth 4 still reaches the `grossWeight` property assertion, but depth 5 is
needed to emit a nested SHACL node shape for the `gdsn:c1490 Measurement` value
node itself. Depth 5 therefore covers all outgoing GTIN-rooted product data in
`build/KATO/kato-instances.ttl`, including the implemented extension module
objects and their structured value nodes.

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

## 15. Maintenance

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
