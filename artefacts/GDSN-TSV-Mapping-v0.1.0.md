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
especially around malformed limit values.

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
in the GDSN UML JSON dump. The meanings below use the known GDSN UML dump type
legend.

| Shorthand | JSON field value | Meaning | Typical TSV treatment |
|---|---:|---|---|
| `type-1` | `1` | Data class / primitive-like datatype record, such as `string`, `decimal`, `date`, or `boolean` | Usually referenced as `xsd:` primitive, not emitted as a GDSN class |
| `type-2` | `2` | Real UML class or aggregate class, such as `CatalogueItem`, `PartyIdentification`, or module classes | Emit to `Classes.tsv`, unless the record is actually code-valued |
| `type-3` | `3` | GS1-defined datatype or structured value type, such as `GTIN`, `GLN`, `Description35`, `Measurement`, or `GS1Code` | Emit simple records to `Datatypes.tsv`; emit records with owned attributes to `Classes.tsv` as structured value classes |
| `type-4` | `4` | GS1 code list, usually generalizing `GS1Code` | Emit to `Enumerations.tsv` |
| `type-5` | `5` | Enumeration | Emit to `Enumerations.tsv` |
| `type-6` | `6` | Message | Emit to `Classes.tsv` only when present in the source class list and needed for message-level modelling |

In `gdsn_classes.json` v3.1.35, class `extensions` records observed during
this investigation use only extension types `1` and `2`; no class-extension
records with `type == 6` were present. Type 6 remains part of the known source
legend for message records.

There is a related `type` field on `gdsn_classAttributes.json`. In the sampled
data, attribute `type-1` records are normal owned attributes and attribute
`type-2` records are owned attributes of GDSN type-3 records. The latter are
important because they expose structured details such as `languageCode`,
`measurementUnitCode`, `codeListVersion`, and `formattingPattern`. A type-3
record with owned attributes is therefore treated as a structured value class,
not as a datatype. The scalar lexical value is represented by `rdf:value`, and
the generated class carries `gdsn:valueDatatype` to identify the primitive
datatype to use for that scalar value.

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
| Facets | Leave blank; parsed limits are represented as named datatypes where reliable |

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

Map simple GDSN type-3 records to `Datatypes.tsv` using the same approach as
the ISO 20022 TSV artefacts: generate named datatype rows with stable datatype
CURIEs, human-readable names, XSD base datatypes, definitions, and any reliable
facets.

Recommended source rows:

- `gdsn_classes.json` records with `type == 3`
- Exclude any type-3 class referenced by `gdsn_codeValues.json`
- Exclude structured type-3 records that own attributes in
  `gdsn_classAttributes.json`; those are emitted to `Classes.tsv`

Recommended columns:

| TSV column | Source |
|---|---|
| `Curie` | Stable generated CURIE, for example `gdsn:c1452` |
| `Name` | `name` |
| `BaseDatatype` | Ultimate XML Schema primitive ancestor, for example `xsd:string` |
| `Definition` | Cleaned `definition` |
| Facets | Derived from datatype name, inherited simple type, or `limit` where reliable |

Approximate non-code type-3 count: 69 rows. In v3.1.35, 44 of those records
own attributes and are structured value classes rather than datatype rows.

Structured type-3 records are emitted to `Classes.tsv` and their owned
attributes are emitted to `Attributes.tsv`. The generated class receives a
`gdsn:valueDatatype` annotation containing the primitive value datatype. For
example, `gdsn:c1490 Measurement` is a class with `gdsn:valueDatatype
"xsd:decimal"` and an owned `measurementUnitCode` attribute, while
`gdsn:c1441 Description35` is a class with `gdsn:valueDatatype "xsd:string"`
and an owned `languageCode` attribute. XML-to-RDF conversion emits these as
value nodes:

```turtle
<urn:gs1:sample:kato:gtin/25196100024899>
  gdsn:a-611376925 <urn:gs1:sample:kato:value/25196100024899/height> .

<urn:gs1:sample:kato:value/25196100024899/height>
  a gdsn:c1490 ;
  rdf:value "1.0"^^xsd:decimal ;
  gdsn:a7085 "MMT"^^xsd:string .
```

For generated instance data, literal values should use primitive RDF datatypes
for tool interoperability. The GDSN ontology retains the richer generated
datatype ranges on properties and the `gdsn:valueDatatype` annotation on
structured value classes.

The KATO sample contains these GTIN trade item instances:

| GTIN | Generated instance URN |
| --- | --- |
| `25196100024882` | `urn:gs1:sample:kato:gtin/25196100024882` |
| `25196100024899` | `urn:gs1:sample:kato:gtin/25196100024899` |

The sample `product-gpc-map.csv` used by `gs1-gdsn-holon` contains these GTIN
to GPC Brick mappings:

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

Extended code-value groups should use generated enumeration CURIEs of the form
`gdsn:extCode_{groupName}`. When an AVP or extended attribute has a
`dataTypeClassName` matching a `gdsn_extendedCodeValues.json` group name, its
`ClassEnumOrPrimitiveType` should reference that generated enumeration rather
than falling back to `xsd:string`.

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

- Convert `{n..m}` on primitive string-like attribute ranges to a generated
  named datatype in `Datatypes.tsv`, then reference that datatype from
  `ClassEnumOrPrimitiveType`. Do not emit inline attribute facets. This avoids
  anonymous datatype restrictions in generated OWL, which Protege can display
  as `ErrorNN`.
- Convert `{\\d{8}}` to `Pattern = \\d{8}` if XML Schema regex compatibility
  is confirmed.
- Emit diagnostics for malformed limit values and preserve the original in
  annotations.

Example generated datatype for a source `xsd:string` attribute with
`limit = {1..200}`:

| TSV file | Relevant output |
|---|---|
| `Attributes.tsv` | `ClassEnumOrPrimitiveType = gdsn:dt_string_MinLength1_MaxLength200` |
| `Datatypes.tsv` | `Curie = gdsn:dt_string_MinLength1_MaxLength200`, `BaseDatatype = xsd:string`, `MinLength = 1`, `MaxLength = 200` |

### 6.3 Extension Module Bridge

GDSN XML extension modules appear below:

```text
TradeItem
  -> TradeItemInformation
     -> extension
        -> <concrete module element>
```

The generated UML ontology has concrete module classes and their internal
module-specific associations, but the XML `extension` element itself is a
string-valued placeholder in the source model. Do not use the generated
`extension` datatype property to connect module instances.

Decision: add a synthetic extension-module bridge to the generated GDSN TSVs:

| TSV file | Row |
|---|---|
| `Classes.tsv` | `gdsn:GDSNExtensionModule`, name `GDSN Extension Module` |
| `Classes.tsv` | detected concrete module classes have `gdsn:GDSNExtensionModule` in `ParentNames` |
| `Attributes.tsv` | `gdsn:extensionModule`, class `gdsn:c1352305416` (`TradeItemInformation`), range `gdsn:GDSNExtensionModule`, multiplicity `0..*` |

Module detection rules for the v3.1.35 JSON dump:

1. Primary source: inspect `gdsn_instances.json` for class rows whose `xPath`
   contains `/tradeItemInformation/extension/*`.
2. Filter those rows to generated type-2 classes whose source class name ends
   in `Module`; this finds 76 concrete extension-root modules.
3. Add module-like type-2 classes with names ending in `Module` that have no
   `gdsn_instances.json` extension-root XPath. In v3.1.35 this adds one
   orphan class, `gdsn:c2147348283`
   (`FoodAndBeveragePropertiesInformationModule`), giving a 77-module
   inventory.

Class `1297183996` is the datatype named `extension`; it has no class
`extensions` entries. The usable source link is the `TradeItemInformation`
attribute named `extension` (`gdsn:a-167571918`) whose `dataClassId` is
`1297183996`, plus the concrete module XPaths in `gdsn_instances.json`.

Instance conversion should then attach supported modules as:

```text
TradeItem
  -> tradeItemInformation
     TradeItemInformation
       -> extensionModule
          <ConcreteModule>
```

Once inside a concrete module, use the existing GDSN ontology associations and
datatype/object properties. For the KATO XML sample, the implemented module
paths are:

| XML module | GDSN path |
|---|---|
| `deliveryPurchasingInformationModule` | `DeliveryPurchasingInformationModule -> deliveryPurchasingInformation -> DeliveryPurchasingInformation -> startAvailabilityDateTime` |
| `tradeItemDescriptionModule` | `TradeItemDescriptionModule -> tradeItemDescriptionInformation -> TradeItemDescriptionInformation -> functionalName`, plus `brandNameInformation -> BrandNameInformation -> brandName` |
| `tradeItemMeasurementsModule` | `TradeItemMeasurementsModule -> tradeItemMeasurements -> TradeItemMeasurements -> depth/height/netContent/width`, plus `tradeItemWeight -> TradeItemWeight -> grossWeight` |
| `tradeItemDataCarrierAndIdentificationModule` | `TradeItemDataCarrierAndIdentificationModule -> dataCarrier -> DataCarrier -> dataCarrierTypeCode` |

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
before merging them with core GDSN code lists. Attribute ranges may still
reference these generated extended-code enumerations directly when the source
`dataTypeClassName` exactly matches the extended-code group name.

Observed Carrefour example from `gdsn_extendedAttributes.json`:

| Source ID | Attribute name | Source `dataTypeClassName` | TSV `ClassEnumOrPrimitiveType` |
|---|---|---|---|
| `1084` | `maximumRange` | `maximumRange` | `gdsn:extCode_maximumRange` |
| `1115` | `voltageRatingCode` | `voltageRatingCode` | `gdsn:extCode_voltageRatingCode` |

String-like extended attributes, such as Carrefour `additionalTaxAgencyCode`
or US FoodService `notSignificantSourceOfNutrient`, continue to map to
`xsd:string`. Do not convert `gdsn_extendedAttributes.json` `limit` values into
datatype facets. Preserve the original limit as `gdsn:originalLimit`; this
avoids generating anonymous datatype restrictions for synthetic extended
attribute containers.

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
5. Generate `Datatypes.tsv` for simple type-3 named datatypes and
   `Classes.tsv`/`Attributes.tsv` for structured type-3 value classes.
6. Generate `Attributes.tsv` from owned attributes and association extensions.
7. Generate annotation property and annotation TSVs for traceability.
8. Emit a diagnostics report for malformed multiplicities, malformed limits,
   duplicate names, missing code-list classes, and structured type-3 value
   classes.
9. Run the generated TSVs through `uml2semantics-python` validation/build.
