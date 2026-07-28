# GDSN JSON to TSV Mapping Investigation

Version: 0.1.0

Date: 2026-07-24

Source artefacts:
`/var/software/gitrepos/gs1/gs1-future-of-data-sharing/artefacts/GDSN_Current_v3.1.35`

Target specification: `docs/TSV-Specification.md`

## 1. Summary

The GDSN JSON files are a dump from a UML model and can be mapped into the
`uml2semantics-python` TSV artefacts with a mostly deterministic conversion.
The core mapping is:

- UML classes become `Classes.tsv`.
- UML owned attributes and association extensions become `Attributes.tsv`.
- UML code lists and code values become `Enumerations.tsv` and
  `EnumerationNamedValues.tsv`.
- UML simple datatypes become `Datatypes.tsv` where they are pure lexical
  restrictions.
- Source identifiers, BMS IDs, XPath values, semantic resource URNs, version
  data, and conversion diagnostics should become annotation assertions.

There are several modelling decisions to make before implementation,
especially around AVP ownership and malformed limit values.

## 2. Repository TSV Model

The local TSV specification and loader define the following target files:

- `Classes.tsv`
- `Attributes.tsv`
- `Datatypes.tsv`
- `Enumerations.tsv`
- `EnumerationNamedValues.tsv`
- `AnnotationProperties.tsv`
- `Annotations.tsv`

The loader also accepts some implementation details that are useful for this
mapping:

- `Classes.tsv` supports `IsAbstract`.
- `Classes.tsv` supports `ChoiceOf` and `ChoiceSemantics`.
- `Attributes.tsv` supports either `ClassEnumOrPrimitiveType` or the legacy
  spelling `ClassEnumOrPrimativeType`.
- Attribute ranges may reference classes, enumerations, named datatypes, or
  `xsd:` primitives.
- `Annotations.tsv` can be used for metadata on classes, properties,
  datatypes, individuals, and ontology-level resources.

## 3. JSON Artefact Inventory

The inspected directory contains these JSON files:

- `GPCv20260520GB.json`
- `gdsn_avps.json`
- `gdsn_classAttributes.json`
- `gdsn_classes.json`
- `gdsn_codeValues.json`
- `gdsn_extendedAttributes.json`
- `gdsn_extendedCodeValues.json`
- `gdsn_gpcBricks.json`
- `gdsn_instances.json`
- `gdsn_validationRules.json`
- `iso3166Countries.json`
- `version.json`

The main UML model inputs are:

- `gdsn_classes.json`
- `gdsn_classAttributes.json`
- `gdsn_codeValues.json`
- `gdsn_instances.json`

The other files are useful as supplementary vocabularies, extension artefacts,
validation metadata, or ontology annotations.

## 4. Observed UML Type Codes

`gdsn_classes.json` contains 1,206 records with these type-code counts:

| Type code | Count | Observed meaning |
|---:|---:|---|
| 1 | 23 | XML Schema primitive-like datatypes |
| 2 | 508 | UML business classes |
| 3 | 70 | GDSN named datatypes or structured simple types |
| 4 | 593 | GS1 code-list classes |
| 5 | 12 | Enumeration classes |

In this document, `type-n` means the numeric `type` field present on records
in the GDSN UML JSON dump. The source files do not include a local legend for
these numeric values, so the meanings below are inferred from record names,
definitions, generalizations, attribute ranges, and code-value references.

| Shorthand | JSON field value | Meaning in this investigation | Typical TSV treatment |
|---|---:|---|---|
| `type-1` | `1` | XML Schema primitive-like datatype record, such as `string`, `decimal`, `date`, or `boolean` | Usually referenced as `xsd:` primitive, not emitted as a GDSN class |
| `type-2` | `2` | UML business class or aggregate class, such as `CatalogueItem`, `PartyIdentification`, or module classes | Emit to `Classes.tsv`, unless the record is actually code-valued |
| `type-3` | `3` | GDSN named datatype or structured simple type, such as `GTIN`, `GLN`, `Description500`, or `GS1Code` | Emit to `Datatypes.tsv` using the same named-datatype approach as ISO 20022 |
| `type-4` | `4` | GS1 code-list class, usually generalizing `GS1Code` | Emit to `Enumerations.tsv` |
| `type-5` | `5` | UML enumeration class, such as `DocumentStatusEnumeration` | Emit to `Enumerations.tsv` |

There is a related `type` field on `gdsn_classAttributes.json`. In the sampled
data, attribute `type-1` records are normal owned attributes and attribute
`type-2` records are owned attributes of GDSN type-3 records. The latter are
important because they expose structured details such as `languageCode` and
`codeListVersion`. Following the ISO 20022 approach, type-3 records remain
named datatypes; structured details that cannot be represented as datatype
facets should be preserved as annotations or diagnostics rather than promoting
the type-3 record to a class by default.

Generalizations are represented as class `extensions` records with:

- `type == 1`
- `name == "Generalization"`
- `destinationClassId` pointing at the parent class/datatype

Class-to-class associations are represented as class `extensions` records with:

- `type == 2`
- `destinationClassId` pointing at the associated class
- `multiplicity` carrying the association cardinality
- `name` sometimes populated, but often blank

There are 522 association-extension records.

## 5. Proposed TSV Mapping

### 5.1 Classes.tsv

Map GDSN UML business classes to `Classes.tsv`.

Recommended source rows:

- `gdsn_classes.json` records with `type == 2`
- Exclude any class that is used as a code-list class by `gdsn_codeValues.json`

Recommended columns:

| TSV column | Source |
|---|---|
| `Curie` | Stable generated CURIE, for example `gdsn:c1401` |
| `Name` | `name` |
| `ParentNames` | Parent class CURIEs from generalization extensions |
| `Definition` | Cleaned `definition` |
| `IsAbstract` | Blank unless abstractness can be inferred elsewhere |
| `ChoiceOf` | Blank initially |
| `ChoiceSemantics` | Blank initially |

Using stable source IDs in CURIEs is important because class names are not
unique.

Approximate base count: 506 rows, excluding code-valued classes.

### 5.2 Attributes.tsv

Map both owned UML attributes and class association extensions to
`Attributes.tsv`.

Recommended source rows:

- `gdsn_classAttributes.json`
- `gdsn_classes.json` `extensions` where `type == 2`

Recommended columns for `gdsn_classAttributes.json`:

| TSV column | Source |
|---|---|
| `Class` | CURIE of `parentClassId` |
| `Curie` | Stable generated CURIE, for example `gdsn:a5334` |
| `Name` | `name` |
| `ClassEnumOrPrimitiveType` | Resolved range from `dataClassId` |
| `MinMultiplicity` | Parsed lower bound from `multiplicity` |
| `MaxMultiplicity` | Parsed upper bound from `multiplicity` |
| `Definition` | Cleaned `definition` |
| Facets | Parsed from `limit`, when reliable |

Recommended columns for association extensions:

| TSV column | Source |
|---|---|
| `Class` | CURIE of containing class record |
| `Curie` | Stable generated CURIE based on source and destination IDs |
| `Name` | Extension `name`, or derived from destination class name |
| `ClassEnumOrPrimitiveType` | CURIE of `destinationClassId` |
| `MinMultiplicity` | Parsed lower bound from extension `multiplicity` |
| `MaxMultiplicity` | Parsed upper bound from extension `multiplicity` |
| `Definition` | Extension `definition` |

Approximate base count:

- 2,288 owned attribute rows
- 522 association rows
- 2,810 total rows

### 5.3 Datatypes.tsv

Map GDSN type-3 records to `Datatypes.tsv` using the same approach as the
ISO 20022 TSV artefacts: generate named datatype rows with stable datatype
CURIEs, human-readable names, XSD base datatypes, definitions, and any reliable
facets.

Recommended source rows:

- `gdsn_classes.json` records with `type == 3`
- Exclude any type-3 class referenced by `gdsn_codeValues.json`

Recommended columns:

| TSV column | Source |
|---|---|
| `Curie` | Stable generated CURIE, for example `gdsn:c1452` |
| `Name` | `name` |
| `BaseDatatype` | Ultimate XML Schema primitive ancestor, for example `xsd:string` |
| `Definition` | Cleaned `definition` |
| Facets | Derived from datatype name, inherited simple type, or `limit` where reliable |

Approximate non-code type-3 count: 69 rows.

Important caveat: 43 non-code type-3 records have owned attributes such as
`languageCode`, `codeListVersion`, or `formattingPattern`. `Datatypes.tsv` can
represent lexical restrictions, but it cannot represent owned attributes on a
datatype. Following the ISO 20022 approach, keep the type-3 record as a named
datatype and preserve those structured details as annotations or conversion
diagnostics where needed.

### 5.4 Enumerations.tsv

Map controlled vocabularies to `Enumerations.tsv`.

Recommended source rows:

- Any `gdsn_classes.json` record whose ID appears as `classId` in
  `gdsn_codeValues.json`
- Missing code-list class names found in `gdsn_codeValues.json`
- Optionally `iso3166Countries.json`
- Optionally `gdsn_extendedCodeValues.json` grouped by `name`

Do not rely only on `gdsn_classes.json` type code `4`. Some controlled
vocabularies are typed as `2` or `3` but still have code values.

Recommended columns:

| TSV column | Source |
|---|---|
| `Curie` | Stable generated CURIE |
| `Name` | UML class `name` or code-list name |
| `Definition` | Class `definition` or `codeListDefinition` |

Approximate count from GDSN code-valued existing classes: 551 rows.

One missing code-list class was observed:

- `FeedLifeStageCode`, with a leading byte-order mark in source
  `codeListName`

### 5.5 EnumerationNamedValues.tsv

Map code values to enumeration individuals.

Recommended source rows:

- `gdsn_codeValues.json`
- Optionally `gdsn_extendedCodeValues.json`
- Optionally `iso3166Countries.json`
- Optionally GPC level-6 attribute values, if GPC is included

Recommended columns:

| TSV column | Source |
|---|---|
| `Enumeration` | CURIE or name of the owning enumeration |
| `Curie` | Stable generated CURIE, for example `gdsn:cv168323` |
| `Name` | `codeValue`; fall back to `name` only if needed |
| `Definition` | `definition` |

Approximate count from `gdsn_codeValues.json`: 13,125 rows.

There were no duplicate `codeValue` values within each observed code-list
class.

### 5.6 AnnotationProperties.tsv

Define a small GDSN provenance and diagnostics annotation vocabulary.

Recommended annotation properties:

| Curie | Name | Purpose |
|---|---|---|
| `gdsn:sourceId` | Source ID | Original UML or code-value numeric ID |
| `gdsn:bmsId` | BMS ID | BMS identifier from instance or AVP metadata |
| `gdsn:pathId` | Path ID | Path identifier from `gdsn_instances.json` |
| `gdsn:xPath` | XPath | XML path from `gdsn_instances.json` |
| `gdsn:semanticResourceUrn` | Semantic resource URN | GDD semantic resource identifier |
| `gdsn:sourceType` | Source type | Original UML type code or source category |
| `gdsn:originalMultiplicity` | Original multiplicity | Unparsed source multiplicity |
| `gdsn:originalLimit` | Original limit | Unparsed source limit |
| `gdsn:conversionWarning` | Conversion warning | Diagnostic note |
| `owl:versionInfo` | Version info | Source version from `version.json` |
| `dct:source` | Source | Source artefact path or name |

### 5.7 Annotations.tsv

Use `Annotations.tsv` to retain source traceability and conversion diagnostics.

Recommended annotations:

- Every generated class, datatype, enumeration, individual, and property:
  `gdsn:sourceId`
- Every generated attribute:
  `gdsn:originalMultiplicity`, `gdsn:originalLimit` where present
- Entities referenced by `gdsn_instances.json`:
  `gdsn:bmsId`, `gdsn:pathId`, `gdsn:xPath`, `gdsn:semanticResourceUrn`
- Ontology-level target:
  `owl:versionInfo` and `dct:source` from `version.json`
- Any row affected by source cleanup:
  `gdsn:conversionWarning`

## 6. Multiplicity and Limit Normalisation

Observed attribute multiplicities:

| Multiplicity | Count |
|---|---:|
| `0..1` | 1,368 |
| `0..*` | 657 |
| `1..1` | 238 |
| `1..*` | 11 |
| malformed or incomplete | 15 |

Malformed values include:

- `..`
- `1..`
- `0...1`

Recommended policy:

- Parse `0..1`, `1..1`, `0..*`, and `1..*` directly.
- Treat extension multiplicity `1` as `1..1`.
- For malformed multiplicities, leave `MinMultiplicity` and `MaxMultiplicity`
  blank in `Attributes.tsv`.
- Preserve the original source value in `Annotations.tsv` using
  `gdsn:originalMultiplicity`.
- Emit a conversion warning using `gdsn:conversionWarning`.

Observed limits are mostly length constraints such as `{1..80}`, but there are
also pattern-like or malformed values:

- `{\\d{8}}`
- `{\\d{4}}`
- `{1.70}`
- `{1,,70}`
- `(1..200}`
- blank-space-only values

Recommended policy:

- Convert `{n..m}` to `MinLength = n`, `MaxLength = m` for string-like ranges.
- Convert `{\\d{8}}` to `Pattern = \\d{8}` if XML Schema regex compatibility
  is confirmed.
- Emit diagnostics for malformed limit values and preserve the original in
  annotations.

## 7. GPC and Country Artefacts

### 7.1 GPC

`GPCv20260520GB.json` is a hierarchy, not a simple UML class list.

Observed counts:

| GPC level | Count |
|---:|---:|
| 1 | 45 |
| 2 | 162 |
| 3 | 938 |
| 4 | 5,318 |
| 5 | 10,188 |
| 6 | 184,323 |

Recommended handling:

- Treat GPC as a separate taxonomy/code-list ontology output.
- Use `gpc:` as the namespace prefix for generated GPC CURIEs.
- Do not fold the full GPC hierarchy blindly into the main UML `Classes.tsv`.
- If represented with current TSVs, model levels as classes and values as
  enumeration individuals only after deciding how to preserve hierarchy.
- `gdsn_gpcBricks.json` can annotate or filter GPC bricks by context code.

### 7.2 ISO 3166 Countries

`iso3166Countries.json` contains 249 records with:

- numeric `code`
- country `name`
- alpha-3 `alpha3`

Recommended handling:

- Create a `CountryCode` or `ISO3166CountryCode` enumeration.
- Use alpha-3 as the individual `Name`.
- Preserve numeric code and country name as annotations.

## 8. AVP and Extended Artefacts

`gdsn_avps.json` and `gdsn_extendedAttributes.json` are not normal class-owned
UML attributes. They need an owner-class strategy before conversion.

Decision: generate AVPs and extended attributes into synthetic container
classes.

Recommended synthetic containers:

- `gdsn:GDSNAVP`
- `gdsn:GDSNExtendedAttribute`

Group-based synthetic subclasses may also be generated where `groupName` is
available, but AVP and extended attribute ownership should not be inferred onto
existing GDSN UML classes unless a reliable source relation is found later.

`gdsn_extendedCodeValues.json` contains 2,610 rows across 352 groups. These can
map to optional enumerations, but their owning model context should be decided
before merging them with core GDSN code lists.

## 9. Identifier Policy

Generated CURIEs should be stable and collision-resistant.

Namespace decision: use `gdsn:` as the namespace prefix for generated GDSN
CURIEs.

Recommended pattern:

- Classes and datatypes: `gdsn:c{id}`
- Attributes: `gdsn:a{id}`
- Code values: `gdsn:cv{id}`
- Association extensions without source IDs:
  `gdsn:assoc_{sourceClassId}_{destinationClassId}_{index}`
- ISO countries: `iso3166:{alpha3}`
- GPC nodes: `gpc:{code}`

Do not use plain source names as CURIE local names without collision handling.
Duplicate class names were observed, including:

- `PartyIdentification`
- `EntityIdentification`
- `TradeItemIdentification`
- `Country`
- `String1000`
- `String250`
- several code-list names

## 10. Recommended Implementation Phases

1. Build a JSON inspection and normalisation layer.
2. Generate stable IDs and source-to-CURIE indexes.
3. Generate `Enumerations.tsv` and `EnumerationNamedValues.tsv` from
   code-valued classes first.
4. Generate `Classes.tsv` for UML business classes.
5. Generate `Datatypes.tsv` for type-3 named datatypes using the ISO 20022
   named-datatype approach.
6. Generate `Attributes.tsv` from owned attributes and association extensions.
7. Generate annotation property and annotation TSVs for traceability.
8. Emit a diagnostics report for malformed multiplicities, malformed limits,
   duplicate names, missing code-list classes, and type-3 details preserved
   outside datatype facets.
9. Run the generated TSVs through `uml2semantics-python` validation/build.
