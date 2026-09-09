---
icon: lucide/git-branch
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Semantic Bridge
## 7. Phase 3 — Align through a governed semantic bridge

### 7.1 Objective

Phase 3 creates and governs semantic correspondences between source-derived GDSN/GPC semantics and target publication semantics such as GS1 Web Vocabulary and schema.org. It is a design-time control-plane process. It does not run lexical mapping separately for each product.

### 7.2 Governed semantic bridge package

The bridge is a package of independently versioned artefacts, not a single ontology containing every mechanism:

| Artefact | Role |
|---|---|
| SSSOM mapping set | Source of truth for candidate, reviewed, approved and rejected mappings. |
| OWL bridge module | Compiled equivalence, subclass, subproperty or property-chain axioms where structurally sound. |
| DL-safe rule module | Conditional semantic derivations evaluated with the ontology over named Product Holon individuals. |
| SPARQL projection/export package | Extracts or serialises approved target graphs; may implement explicitly governed transforms that are not placed in the ontology. |
| Publication allow-list | Determines which facts may be emitted to each audience profile. |
| Regression and conformance tests | Demonstrate that released mappings still produce expected results after source or target changes. |
| Release manifest | Links every compiled artefact to the reviewed SSSOM records and source vocabulary releases. |

SPARQL queries are not part of the OWL ontology. They belong to the bridge package and have their own lifecycle.

### 7.3 Four publication routes

Every candidate product fact is assigned one of four routes.

| Route | Condition | Treatment |
|---|---|---|
| **Route 1 — direct semantic correspondence** | Source and target have compatible meaning, value space, cardinality and graph shape. | Compile an approved OWL mapping or deterministic property alias. |
| **Route 2 — structural transformation** | Meaning is compatible but source and target graph structures differ or the output property depends on a code/value condition. | Apply an approved DL-safe rule or versioned transform, then export the result. |
| **Route 3 — generic publication** | The fact is publishable but no approved first-class target term exists. | Emit `schema:additionalProperty` / `schema:PropertyValue` with the source property identifier and label. |
| **Route 4 — excluded** | The fact is B2B-only, commercially sensitive, inapplicable, unsupported or outside the publication profile. | Retain it in the authorised internal or B2B representation; do not emit it publicly. |

Route assignment is a mapping-governance decision, not a runtime guess by an LLM.

### 7.4 Candidate generation

Candidate mappings may be generated through:

- exact or normalised label comparison;
- synonym and annotation comparison;
- structural similarity;
- code-list and value-space comparison;
- source lineage and documentation;
- existing schema.org or Web Vocabulary alignments;
- domain-expert proposals.

The demonstrated LOOM/BioPortal run extracted 28,101 unique terms and produced 237 unique bidirectional candidate pairs, serialised as 474 directional mapping records:

- GDSN ↔ GPC: 38 unique pairs;
- GDSN ↔ GS1 Web Vocabulary: 184 unique pairs;
- GPC ↔ GS1 Web Vocabulary: 15 unique pairs.

All records were expressed as `skos:closeMatch`, which is appropriate for lexical candidates. The output is evidence for review, not authority for equivalence.

### 7.5 Limits of lexical matching

Labels are not semantic keys. Similar labels may hide different scope, range, cardinality or structure; dissimilar labels may express the same concept. Opaque generated GDSN CURIEs make labels necessary for candidate discovery, but labels alone remain insufficient for approval.

The source evidence found several examples:

- `allergenStatement` in Web Vocabulary is a language-tagged string, while the structured GDSN allergen path is a coded multi-hop record;
- a separate flat GDSN allergen-statement attribute is a more plausible direct candidate;
- `claimDetail` has no single lexical match, while components of its surrounding domain align to several distinct Web Vocabulary record types;
- multiple GDSN GTIN attributes map lexically to one `gs1:gtin` or `schema:gtin` concept, creating an n:1 cardinality issue that requires packaging-level review.

### 7.6 SSSOM mapping-set governance

Every mapping shall be represented as a first-class SSSOM record with, where applicable:

- `subject_id` and `subject_label`;
- `predicate_id`;
- `object_id` and `object_label`;
- mapping justification;
- mapping tool and tool version;
- source and target vocabulary releases;
- confidence;
- mapping cardinality;
- author and reviewer identifiers;
- review date and decision;
- comments describing structural assumptions;
- status: candidate, approved, rejected, superseded or deprecated.

An automated candidate should normally use `semapv:LexicalMatching` or the appropriate machine-matching justification. A reviewed decision records manual or composite curation. The exact predicate may remain `skos:closeMatch`, become `skos:exactMatch`, or compile into an OWL axiom only after the review establishes the required semantics.

### 7.7 Human review gate

The review process shall test:

1. identifier resolution and term status;
2. labels, definitions and domain context;
3. source and target value spaces;
4. datatype and language handling;
5. cardinality and mapping cardinality;
6. graph shape and nesting;
7. target publication behaviour;
8. loss, aggregation or transformation risk;
9. authority and intended audience;
10. regression examples and rejection cases.

No candidate shall be compiled into a reasoner-active equivalence solely because a lexical tool generated it.

### 7.8 Direct OWL mappings

An OWL `equivalentProperty` or equivalent-class axiom is appropriate only where the two terms denote the same relation or class over compatible graph structures. Domain aliases within Web Vocabulary are examples of straightforward equivalence. A source-derived GDSN-to-Web Vocabulary equivalence must be explicitly approved because Web Vocabulary does not publish links to the generated local GDSN namespace.

Where a two-hop object-property path reaches the same target individual expected by the target property, an OWL property chain may support a derived property. It shall not be used to convert a structured individual into a literal string or to branch on a data value.

### 7.9 DL-safe rule mappings

Conditional mappings may use DL-safe rules in an independently versioned module imported by the core bridge ontology. Every variable binds to named Product Holon individuals already present in the ABox. Representative cases include:

- mapping nutrient code `FAT` and its quantity to `schema:fatContent`;
- mapping `ENERC`, `PRO-` and `NA` to the corresponding schema.org nutrition properties;
- deriving an approved textual allergen statement from a structured coded chain where no authoritative flat statement is available;
- constructing an isomorphic publication assertion from a named source record.

The rule module shall be tested with the same semantic releases and mapping-set version as the Product Holon publication profile.

### 7.10 SPARQL projection and export

SPARQL may be used to:

- select the entailed target graph;
- construct the final JSON-LD publication graph;
- filter Route 4 properties;
- create generic `PropertyValue` nodes for Route 3;
- serialise audience-specific views;
- implement a transform that governance intentionally keeps outside the reasoner.

Where substantive transformation remains in SPARQL, the query is a governed compiled artefact with tests and provenance. Where SWRL has already entailed the target properties, the export query should remain thin and stable.

### 7.11 Generic `PropertyValue` projection

Route 3 preserves a publishable fact without claiming that it is a native Web Vocabulary or schema.org property. The representation shall include:

- `schema:additionalProperty`;
- a `schema:PropertyValue` node;
- the source property identifier in `schema:propertyID`;
- a human-readable name;
- the value and unit where applicable;
- source or provenance linkage where supported by the profile.

Downstream parsers may give generic properties less weight than first-class properties. The architecture treats Route 3 as loss-minimising publication, not semantic equivalence.

### 7.12 Current evidence-based mapping findings

The evidence pack records the full findings. The consolidated position is:

- GTIN has strong schema.org/Web Vocabulary support, but multiple source GTIN attributes require packaging-level cardinality review;
- `gdsn:a812659001` and `gs1:ingredientStatement` are a tool-corroborated candidate pair pending formal human approval;
- `gpc:20002867` and `gs1:sharpnessOfCheese` are independently corroborated candidate terms, with value-level equivalence still requiring review;
- `gdsn:a-1463136308` is the plausible direct candidate for `gs1:allergenStatement`; the structured allergen chain is a separate Route 2 case;
- nutrient codes `ENERC`, `FAT`, `PRO-` and `NA` have defined schema.org projection targets; other nutrients, such as calcium in the worked example, require Route 3 unless a governed target is added;
- every residual facet reproduced in the four-Brick mapping tables had no LOOM candidate to Web Vocabulary and currently uses Route 3; the source baseline elsewhere reports a 19-of-20 count, but its reproduced per-Brick lists do not reconcile to that total, so no consolidated numeric claim is made here;
- `packagingRecycledContentRatio` and `claimDetail` were present in the candidate term set but produced no direct Web Vocabulary match; they require structural review, decomposition, Route 3 or Route 4 treatment.

These are architectural inputs, not an approved GS1 crosswalk.

### 7.13 Bridge package versioning

A bridge release shall identify:

- source GDSN and GPC releases;
- target Web Vocabulary and schema.org releases;
- SSSOM mapping-set version and checksum;
- approved mapping count by predicate and route;
- rule-module version;
- export-query version;
- allow-list version;
- regression-test results;
- known rejected and deprecated mappings.

### 7.14 Drift detection and regression testing

Regression tests shall detect:

- removed or deprecated source and target terms;
- changed domains, ranges, cardinalities or code values;
- mappings whose graph shapes are no longer compatible;
- unexpected inference closure;
- lost or duplicated publication facts;
- invalid JSON-LD or SHACL output;
- changed Route 3 fallback counts;
- changed public/private classification.

### 7.15 Phase outputs

Phase 3 produces a released governed semantic bridge package, including its SSSOM source of truth, compiled semantic artefacts, export/projection rules, publication allow-lists, tests and release manifest.

---

## Part IV — Publication and consumption

The next phase applies the governed bridge to publication and consumption of
Product Holon representations.

Continue to [Publication and Consumption](publication-and-consumption.md).
