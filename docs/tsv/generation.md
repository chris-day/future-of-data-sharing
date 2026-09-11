---
icon: lucide/table
---

# TSV Generation

The TSV bundles are generated for `uml2semantics-python` from the GDSN UML JSON
dump and taxonomy sources. The current implementation is in
`src/gdsn_tsv_transformer/cli.py` and follows the repository mapping documents:

- `artefacts/GDSN-TSV-Mapping-v0.1.0.md`
- `GDSN-TSV-Mapping-v0.1.0.md`
- `GDSN_TSV_Transformer_README_v0.1.0.md`

Each module writes the standard file set:

```text
Classes.tsv
Attributes.tsv
Datatypes.tsv
Enumerations.tsv
EnumerationNamedValues.tsv
AnnotationProperties.tsv
Annotations.tsv
diagnostics.tsv
```

## GDSN and GPC

Generate GDSN and GPC TSVs together. The `--input-dir` value is the default,
but it is shown explicitly for repeatability:

```bash
.venv/bin/gdsn-json-to-tsv \
  --input-dir artefacts/GDSN_Current_v3.1.35 \
  --output-dir build/gdsn-tsv
```

Generate only GDSN:

```bash
.venv/bin/gdsn-json-to-tsv \
  --input-dir artefacts/GDSN_Current_v3.1.35 \
  --output-dir build/gdsn-tsv \
  --skip-gpc
```

Output directories:

```text
build/gdsn-tsv/gdsn/
build/gdsn-tsv/gpc/
```

The executable always writes the GDSN module to `build/gdsn-tsv/gdsn/`. Unless
`--skip-gpc` is supplied, it also writes the separate GPC module to
`build/gdsn-tsv/gpc/`.

## Google Product Taxonomy

Generate Google Product Taxonomy TSVs:

```bash
.venv/bin/google-taxonomy-to-tsv \
  --input-file artefacts/google/taxonomy-with-ids.en-GB.txt \
  --output-dir build/gdsn-tsv
```

Output directory:

```text
build/gdsn-tsv/google/
```

## Source Inputs

The GDSN transformer reads these source files from
`artefacts/GDSN_Current_v3.1.35/`:

The source files can be obtained from navigator.gs1.org

| Source file | Use |
| --- | --- |
| `gdsn_classes.json` | UML classes, datatypes, code-list classes, enumerations, associations, and generalisations |
| `gdsn_classAttributes.json` | Owned UML attributes and structured type-3 qualifiers |
| `gdsn_codeValues.json` | Standard GDSN code-list values |
| `gdsn_instances.json` | XPath, BMS ID, path ID, semantic resource URN, and extension-module detection metadata |
| `gdsn_avps.json` | Attribute Value Pair metadata, emitted into a synthetic container |
| `gdsn_extendedAttributes.json` | Extended attributes, emitted into synthetic group containers |
| `gdsn_extendedCodeValues.json` | Extended code-list enumerations and values |
| `iso3166Countries.json` | ISO 3166 country-code named values |
| `version.json` | Ontology-level version annotations |
| `GPCv20260520GB.json` | Separate GPC taxonomy module |
| `gdsn_gpcBricks.json` | GPC Brick context-code annotations |

## Implemented Type Rules

The GDSN UML dump uses numeric `type` values. The transformer applies these
rules:

| Type | Meaning | Implemented TSV treatment |
| ---: | --- | --- |
| `1` | Data class / primitive | Resolved to `xsd:` primitives where possible, otherwise `xsd:string` |
| `2` | Real UML class | Emitted to `Classes.tsv`, except records treated as enumerations |
| `3` | GS1-defined datatype or structured value type | Simple records go to `Datatypes.tsv`; records with owned attributes go to `Classes.tsv` as value classes |
| `4` | GS1 code list | Emitted to `Enumerations.tsv` |
| `5` | Enumeration | Emitted to `Enumerations.tsv` |
| `6` | Message | Recognised as source knowledge, but not currently emitted unless present in the class set and needed by modelling |

Attribute `type` values in `gdsn_classAttributes.json` are separate from class
type values. Attributes owned by structured type-3 records are emitted as
normal attributes on the generated value class.

## GDSN Classes

`Classes.tsv` contains:

- type-2 UML classes;
- structured type-3 value classes;
- synthetic containers for AVPs, extended attributes, and extension modules.

Class CURIEs are stable and source-ID based:

```text
gdsn:c{id}
```

Generalisation extensions in `gdsn_classes.json` become `ParentNames`. A
generalisation is identified as an extension with `type == 1`,
`name == "Generalization"`, and `destinationClassId` pointing at the parent.

## GDSN Attributes

`Attributes.tsv` contains:

- owned UML attributes from `gdsn_classAttributes.json`;
- association extensions from `gdsn_classes.json` where `extension.type == 2`;
- AVP properties on `gdsn:GDSNAVP`;
- extended attributes on `gdsn:GDSNExtendedAttribute` or a synthetic group
  class;
- a synthetic `gdsn:extensionModule` property from `TradeItemInformation` to
  `gdsn:GDSNExtensionModule`.

Attribute CURIEs are stable and source-ID based:

```text
gdsn:a{id}
```

Association property CURIEs are generated from the source class, destination
class, and association position:

```text
gdsn:assoc_{sourceClassId}_{destinationClassId}_{index}
```

Ranges are resolved in this order:

1. `xsd:` primitive when the source type name is a known XML Schema datatype.
2. GDSN enumeration when the range points to a code list or enumeration.
3. GDSN class or datatype CURIE for known source class IDs.
4. Extended-code enumeration when an extended attribute type name matches
   `gdsn_extendedCodeValues.json`.
5. `xsd:string` fallback when the source type cannot be resolved.

Malformed multiplicities are not guessed. `MinMultiplicity` and
`MaxMultiplicity` are left blank, the source value is preserved as
`gdsn:originalMultiplicity`, and a warning is written to `diagnostics.tsv`.

## Datatypes and Limits

Simple type-3 records become `Datatypes.tsv` rows. Base datatypes are resolved
by walking type-1/type-3 generalisations to the ultimate XML Schema primitive.

Structured type-3 records are not emitted as datatypes. If a type-3 record owns
attributes, it is emitted as a class with a `gdsn:valueDatatype` annotation.
This preserves qualified values such as language-tagged descriptions and
measurements with units.

For example:

| Source type-3 record | TSV treatment | Qualifier attributes |
| --- | --- | --- |
| `Measurement` / `gdsn:c1490` | Class with `gdsn:valueDatatype "xsd:decimal"` | `measurementUnitCode` |
| `Description35` / `gdsn:c1441` | Class with `gdsn:valueDatatype "xsd:string"` | `languageCode` |

Normal GDSN string limits such as `{1..200}` are converted into named synthetic
datatypes, not inline attribute facets. This avoids anonymous datatype ranges
that caused Protege rendering and parsing issues.

Example implemented mapping:

| Attribute | Range emitted in `Attributes.tsv` | Datatype row |
| --- | --- | --- |
| `registrationAgency` | `gdsn:dt_string_MinLength1_MaxLength200` | `BaseDatatype = xsd:string`, `MinLength = 1`, `MaxLength = 200` |
| `registrationNumber` | `gdsn:dt_string_MinLength1_MaxLength70` | `BaseDatatype = xsd:string`, `MinLength = 1`, `MaxLength = 70` |

Extended attribute limits are deliberately not converted into datatype facets.
Their `limit` values are preserved as `gdsn:originalLimit` annotations instead.
This decision avoids invalid datatype classes from malformed or ambiguous
extended-attribute metadata, including the Carrefour and US FoodService cases
that previously surfaced as `ErrorNN` ranges in Protege.

## Enumerations and Named Values

`Enumerations.tsv` contains:

- GDSN type-4 code lists;
- GDSN type-5 enumerations;
- classes referenced by `gdsn_codeValues.json`;
- generated fallback code-list classes when code values reference a missing
  class;
- `gdsn:ISO3166CountryCode`;
- generated extended-code enumerations from `gdsn_extendedCodeValues.json`.

`EnumerationNamedValues.tsv` contains:

- standard GDSN code values as `gdsn:cv{id}`;
- ISO 3166 alpha-3 values as `iso3166:{alpha3}`;
- extended-code values as `gdsn:extcv{id}_{groupName}`.

The `iso3166:` prefix is intentionally preserved for ontology generation, so
the `uml2semantics` command should include:

```text
iso3166:urn:iso:std:iso:3166
```

## AVPs and Extended Attributes

AVPs and extended attributes are generated into synthetic containers because
their explicit ownership is not available in the same way as normal UML class
attributes.

| Source | Container |
| --- | --- |
| `gdsn_avps.json` | `gdsn:GDSNAVP` |
| `gdsn_extendedAttributes.json` without `groupName` | `gdsn:GDSNExtendedAttribute` |
| `gdsn_extendedAttributes.json` with `groupName` | `gdsn:extGroup_{groupName}` subclass of `gdsn:GDSNExtendedAttribute` |

If an AVP has inline code values, the transformer emits a generated
`gdsn:avpCode_{name}` enumeration. If an extended attribute type name matches a
group in `gdsn_extendedCodeValues.json`, the range becomes
`gdsn:extCode_{groupName}`.

Implemented examples:

| Extended attribute | Owner | Range |
| --- | --- | --- |
| Carrefour `maximumRange` | `gdsn:extGroup_Carrefour` | `gdsn:extCode_maximumRange` |
| Carrefour `voltageRatingCode` | `gdsn:extGroup_Carrefour` | `gdsn:extCode_voltageRatingCode` |
| US FoodService `notSignificantSourceOfNutrient` | `gdsn:extGroup_US_FoodService` | `xsd:string` |

## Extension Module Detection

Extension modules are represented with a synthetic superclass:

```text
gdsn:GDSNExtensionModule
```

The implemented detection rule marks 77 module classes. A class is treated as
an extension module when it is a type-2 class whose name ends with `Module` and
it appears under a `gdsn_instances.json` XPath containing:

```text
/tradeItemInformation/extension/*
```

The implementation also includes module-like type-2 classes ending in `Module`
that are not present in `gdsn_instances.json`. This captures the known orphan
module class `FoodAndBeveragePropertiesInformationModule` and keeps the module
inventory at 77.

Each detected concrete module class gets `gdsn:GDSNExtensionModule` in
`ParentNames`, and the synthetic `gdsn:extensionModule` property links
`TradeItemInformation` to that superclass.

## Annotations and Provenance

`AnnotationProperties.tsv` and `Annotations.tsv` preserve source metadata used
for traceability and downstream SHACL/RDF generation:

| Annotation property | Meaning |
| --- | --- |
| `gdsn:sourceId` | Original UML or code-value numeric identifier |
| `gdsn:sourceType` | Original type code or source category |
| `dct:source` | Source JSON filename |
| `gdsn:bmsId` | BMS identifier from instance or AVP metadata |
| `gdsn:pathId` | Source path identifier |
| `gdsn:xPath` | Source XML XPath |
| `gdsn:semanticResourceUrn` | GDD semantic resource URN |
| `gdsn:originalMultiplicity` | Original multiplicity string |
| `gdsn:originalLimit` | Original limit string |
| `gdsn:conversionWarning` | Generated diagnostic warning |
| `gdsn:valueDatatype` | Primitive `rdf:value` datatype for structured value classes |

## GPC Module

GPC is generated as a separate ontology module using the `gpc:` namespace. The
source hierarchy from `GPCv20260520GB.json` becomes classes with parent
relationships. The namespace base for generated `gpc:` CURIEs is:

```text
urn:gs1:std:gpc:
```

GPC annotations include:

- `gpc:level`;
- `gpc:active`;
- `gpc:definitionExcludes`;
- `gpc:contextCode` from `gdsn_gpcBricks.json`;
- `dct:source`.

## Google Product Taxonomy Module

Google Product Taxonomy is also generated as a separate ontology module. It
uses the `google:` prefix and follows the same broad taxonomy pattern as GPC:
categories become classes, hierarchy becomes parent relationships, and category
metadata is emitted as annotations.

## Diagnostics and Validation

Diagnostics are written to each module's `diagnostics.tsv`.

The implemented unit tests validate the key TSV-generation decisions:

- Carrefour extended-code attributes resolve to generated extended-code
  enumerations.
- Carrefour string extended attributes remain `xsd:string` and do not receive
  converted length facets.
- normal GDSN string limits become named synthetic datatypes.
- US FoodService `notSignificantSourceOfNutrient` remains `xsd:string` with no
  facet conversion.
- extension-module detection marks 77 module classes.
- structured type-3 records such as `Measurement` and `Description35` are value
  classes, not datatypes.

Run the TSV test suite with:

```bash
.venv/bin/python -m unittest tests.test_tsv_transformer tests.test_google_taxonomy
```
