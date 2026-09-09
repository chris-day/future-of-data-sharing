---
icon: lucide/database
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Semantic Foundation
## 5. Phase 1 — Build the semantic foundation

### 5.1 Objective

Phase 1 converts GS1 source-model material into explicit, versioned semantic and validation artefacts. It establishes the design-time foundation consumed by every later Product Holon release. The phase does not create product instances and does not publish Web Vocabulary representations.

### 5.2 Source inputs

The demonstrated pipeline begins with GDSN and GPC UML-model exports from GS1 Navigator. The source investigation identified the following representative inputs:

- `gdsn_classes.json`;
- `gdsn_classAttributes.json`;
- `gdsn_codeValues.json`;
- `gdsn_instances.json`;
- `gdsn_avps.json`;
- `gdsn_extendedAttributes.json`;
- `gdsn_extendedCodeValues.json`;
- `gdsn_gpcBricks.json`;
- `gdsn_validationRules.json`;
- `iso3166Countries.json`;
- `version.json`;
- a GPC hierarchy release such as `GPCv20260520GB.json`.

These files are source-model artefacts rather than product-instance data. A GTIN-to-Brick assignment must be obtained from an authoritative product record, data-pool export, PIM or lookup service.

### 5.3 JSON-to-TSV transformation

The reference tool `gdsn-json-to-tsv` transforms the source JSON into controlled tabular artefacts suitable for semantic generation. The documented outputs include:

- `Classes.tsv`;
- `Attributes.tsv`;
- `Datatypes.tsv`;
- `Enumerations.tsv`;
- `EnumerationNamedValues.tsv`;
- `AnnotationProperties.tsv`;
- `Annotations.tsv`;
- `diagnostics.tsv`.

GDSN and GPC are emitted as separate module directories. Code-valued classes are not duplicated as ordinary business classes and enumerations. Source identifiers and annotations are retained so that generated opaque CURIEs remain traceable to the source model.

### 5.4 Conversion policy

The semantic foundation shall follow a non-invention policy:

- malformed multiplicities or limits shall be preserved in source annotations and diagnostics;
- the transformation shall not guess a plausible cardinality where the source is malformed or incomplete;
- conversion warnings shall remain machine-readable and reviewable;
- source model identifiers shall be retained even where they are not human-readable;
- extended attributes without a reliable natural owner shall be represented through explicit synthetic containers rather than attached to an invented owner class;
- GDSN and GPC shall remain separate modules, with relationships expressed explicitly rather than by merging their source structures.

The source investigation found malformed multiplicities such as `..`, `1..` and `0...1`. The demonstrated policy leaves generated minimum and maximum values blank, preserves the original expression and emits a conversion warning.

### 5.5 TSV-to-OWL generation

The reference tool `uml2semantics-python` converts the TSV artefacts into OWL 2. The generated model may include:

- classes and subclass relations;
- object and datatype properties;
- datatype restrictions and facets;
- enumerations and named values;
- union and disjointness constructs for UML choice patterns;
- OWL 2 property chains where the source relationship supports multi-hop composition;
- annotations linking generated entities to source identifiers and model documentation.

Property chains are suitable for composing object-property paths towards the same target. They do not select a different output property based on a sibling data value; that type of conditional transformation remains a rule concern.

### 5.6 GPC semantic module

The inspected GPC artefact contains 22,281 classes arranged across Segments, Families, Classes, Bricks, Attribute Types and Attribute Values. The source investigation reported:

- 45 Segments;
- 162 Families;
- 938 Classes;
- 5,318 Bricks;
- 2,085 Brick-specific Attribute Types;
- 13,733 Attribute Values.

The architecture uses the GPC module for product classification, ancestor traversal, category-specific attribute scope and controlled values. A Brick’s child Attribute Types and their child Attribute Values provide the input to generated SHACL constraints.

### 5.7 GDSN semantic module

The inspected GDSN artefact contains 30,630 RDF descriptions and approximately 3,946 core trade-item attributes, supplemented by retailer- and region-specific extensions and 557 distinct code lists. The source investigation identified examples relevant to consumer and agent use cases, including allergens, nutrients, claims, certifications, recycled content, preparation instructions and recipes.

The architecture does not infer that all such attributes belong in every Product Holon or public representation. The GDSN module supplies semantic definitions, datatype and cardinality information, code-list references and business-to-business context. Publication remains policy-driven.

### 5.8 SHACL generation inputs

The shape-generation step consumes the GPC and, optionally, GDSN ontology modules. For a Brick:

1. the Brick becomes the `sh:targetClass`;
2. each level-5 child Attribute Type becomes an `sh:property`;
3. each level-6 child Attribute Value becomes a member of the allowed enumeration;
4. the source model supplies cardinality, datatype and code-list information where available;
5. reusable code-list resources should be referenced rather than repeatedly inlined where practical.

The current `gs1-gdsn-holon` reference implementation also supports an `--include-gdsn` option that adds a selected cross-category GDSN shape.

### 5.9 Diagnostics and release quality

A semantic-foundation release shall contain:

- a source manifest;
- transformation-tool versions;
- conversion diagnostics;
- unresolved-source issue counts;
- generated ontology serialisations;
- generated shape artefacts;
- parse and consistency test results;
- a change report from the previous release;
- a deprecation and migration report where identifiers or meanings change.

No generated artefact should be promoted to a release solely because it parses. Semantic diagnostics and regression tests shall be reviewed.

### 5.10 Versioning and provenance

The release manifest shall identify the Navigator/GDSN/GPC source versions, transformation versions, generation date and checksum of each output. Generated IRIs shall have a documented persistence policy. Where source IDs remain opaque, labels and source annotations shall be preserved but shall not be treated as globally unique semantic identifiers.

### 5.11 Phase outputs

Phase 1 produces:

- versioned GDSN and GPC semantic modules;
- SHACL profile inputs and generated shapes;
- code-list resources;
- diagnostics and conversion warnings;
- source-to-generated provenance;
- a release manifest suitable for downstream Product Holon construction and mapping governance.

---

## Part II — Product Holon construction

The next phase uses the semantic foundation to construct bounded Product Holon
instances, validate them, and record their provenance and release status.

Continue to [Holon Construction](product-holon-construction.md) for Phase 2.
