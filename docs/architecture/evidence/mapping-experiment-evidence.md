---
icon: lucide/chart-scatter
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Mapping Experiment Evidence
## Part V — Mapping experiment evidence

## 11. Web Vocabulary source inspection

### 11.1 Source version and retrieval limit

The source investigation identified the Web Vocabulary `v1.16` directory as containing:

- `gs1Voc.ttl`, approximately 1.34 MB;
- `gs1Voc.jsonld`, approximately 2.37 MB.

The available fetch mechanism truncated both files, so only the alphabetically early portion was inspected directly in that pass. This prevented a complete direct-source review of all target terms. Later LOOM term extraction and mapping output provided broader lexical coverage but did not replace semantic review.

### 11.2 Direct allergen-statement evidence

The inspected source declared `gs1:allergenStatement` as:

- an `owl:DatatypeProperty` and `rdf:Property`;
- domain `gs1:FoodBeverageTobaccoProduct`;
- range `rdf:langString`;
- a textual description specified as one string;
- equivalent only to Web Vocabulary mirror-domain URIs, not to a generated `gdsn:` term.

This is the evidence for the Route 2 correction concerning the coded GDSN allergen chain.

### 11.3 Absence of a published generated-GDSN crosswalk

In the inspected source slice, Web Vocabulary alignments pointed to schema.org, older vocabularies or Web Vocabulary mirror URIs. No alignment to the locally generated `gdsn:` namespace was observed. This is expected because the generated namespace is not a public GS1 Web Vocabulary dependency.

The architecture therefore treats the GDSN/GPC-to-Web Vocabulary mapping set as a separately governed asset.

---

## 12. LOOM/BioPortal candidate generation

### 12.1 Aggregate results

| Metric | Result |
|---|---:|
| Extracted terms | 28,101 |
| Unique terms | 28,101 |
| Directional mapping records | 474 |
| Unique bidirectional pairs | 237 |
| GDSN ↔ GPC unique pairs | 38 |
| GDSN ↔ Web Vocabulary unique pairs | 184 |
| GPC ↔ Web Vocabulary unique pairs | 15 |

The arithmetic is internally consistent: `38 + 184 + 15 = 237`, and the bidirectional serialisation doubles that to `474` records.

### 12.2 Distribution

| Pair | Share of 237 unique pairs | Interpretation |
|---|---:|---|
| GDSN ↔ Web Vocabulary | 77.6% | Consistent with shared subject matter and Web Vocabulary’s derivation from GS1 product semantics. |
| GDSN ↔ GPC | 16.0% | Reflects overlap between master-data and classification vocabularies. |
| GPC ↔ Web Vocabulary | 6.3% | Consistent with sparse Web Vocabulary coverage of Brick-specific facets. |

### 12.3 Mapping relation

Every directional record used `skos:closeMatch`, not `skos:exactMatch`. This is appropriate for unreviewed lexical candidates and aligns with the architecture’s candidate-versus-approved distinction.

### 12.4 Yield

The 237 candidate pairs represent approximately 0.84% of the 28,101 terms when expressed as unique pairs per term count. Even under the generous assumption that each pair uses two otherwise unique terms, only a small portion of terms participates in any candidate. This confirms that lexical overlap is sparse and cannot provide a universal crosswalk.

### 12.5 Role of the result

The LOOM output is valuable for:

- prioritising manual review;
- discovering candidate terms missed by ad hoc searches;
- identifying n:1 or 1:n mapping patterns;
- supplying provenance for candidate generation;
- detecting broad overlap between vocabulary families.

It is not sufficient for:

- semantic equivalence;
- structural compatibility;
- code-value equivalence;
- publication authorisation;
- automatic compilation into OWL axioms.

---

## 13. Reconciliation of candidate mappings

### 13.1 Directly corroborated candidates

The parsed mapping output corroborated the following:

| Source | Target | Evidence consequence |
|---|---|---|
| `gdsn:a-1292425203` and three sibling GTIN fields | `gs1:gtin` | Strong lexical evidence but a packaging-level n:1 review is required. |
| `gdsn:a812659001` | `gs1:ingredientStatement` | Resolves the earlier inconclusive web-source lookup into a real lexical candidate. |
| `gpc:20002867` | `gs1:sharpnessOfCheese` | Independently corroborates the direct Web Vocabulary term finding. |
| `gdsn:a2008988543` | `gs1:nutrientBasisQuantity` | Corroborates the earlier target-term identification. |
| `gdsn:a-1463136308` | `gs1:allergenStatement` | Identifies a flat statement candidate distinct from the structured allergen chain. |

Additional allergen-domain candidates included source terms corresponding lexically to allergen type, specification name and specification agency.

### 13.2 Structural correction for allergen data

The reconciliation produced a two-representation model:

1. **Flat statement:** a GDSN textual allergen statement is a plausible Route 1 candidate for `gs1:allergenStatement` after review.
2. **Structured codes:** the coded allergen hierarchy supports filtering and deterministic statement generation but remains Route 2.

An implementation may prefer the authoritative flat statement when present and derive a text representation from codes only under an explicit profile.

### 13.3 Confirmed lexical negatives

The source term list contained `packagingRecycledContentRatio` and `claimDetail`, but the complete lexical run produced no Web Vocabulary candidate for either. This is stronger than a failed search-engine lookup: the terms were included in the candidate set and did not match.

`claimDetail` should not automatically be treated as wholly unmappable. Related domain terms aligned separately to certification, regulatory, award and compulsory-information concepts. This indicates that the source record may require decomposition rather than one direct target.

### 13.4 GPC facet results across the four Bricks

| Brick | Facet | Current mapping route |
|---|---|---|
| Cheese | Sharpness of Cheese | Corroborated Route 1 candidate at term level; value-level review outstanding. |
| Cheese | Type, Firmness, Intended Use, Kind, Origin | Route 3; absent from the completed GPC-to-Web Vocabulary candidate set. |
| Smartphones | Input Registration, System | Route 3; absent from the completed candidate set. |
| Beer | Colour, Style, Flavoured/Mixed, Type, Origin, Taste | Route 3; absent from the completed candidate set. |
| Sugar | Type of Sugar/Sugar Substitute | Route 3; absent from the completed candidate set. |
| Compote example | Type of Jam/Marmalade = `COMPOTE` (`30000728`) | Not part of the original four-Brick worked mapping reconciliation; retain as a GPC-native fact and use Route 3 by default until reviewed. |
| Milk hierarchy example | Fat content = `Whole`; Packaging type = `Plastic bottle` | User-supplied label-level facts only. The verified product Brick is `10000025`; no Brick Attribute identifiers were supplied or reconciled, so retain as Route 3 `schema:PropertyValue` records until a generated Brick shape and mapping review establish GPC-native predicates. |

All residual facets reproduced in the table remain Route 3 under the current evidence. The source baseline also states that nineteen of twenty facets were residual, but the named lists reproduced there total fewer items; this internal count discrepancy is unresolved and the pack therefore relies on the term-level results rather than the disputed aggregate.

### 13.5 Shared GDSN attribute status

| Source concept | Current status |
|---|---|
| GTIN | Strong candidate; packaging-level cardinality review required. |
| ingredientStatement | Corroborated candidate; formal range/domain review required. |
| flat allergenStatement | Corroborated candidate; review separately from coded chain. |
| coded allergen chain | Route 2 structural transform. |
| ENERC/FAT/PRO-/NA nutrient codes | Route 2 to schema.org nutrition properties. |
| CA and other unsupported nutrients | Route 3 unless a governed target is established. |
| packagingRecycledContentRatio | No lexical target; Route 3 or Route 4 pending semantic review. |
| claimDetail | No single target; likely decomposition plus Route 3 residuals or Route 4. |

### 13.6 Review priority

A pragmatic review order is:

1. identity and core product properties;
2. food safety and allergen properties;
3. nutrition properties;
4. ingredient and regulated claim properties;
5. category-specific facets for pilot Bricks;
6. sustainability and packaging facts;
7. remaining public-product facts;
8. B2B-only and extension attributes.

---

## 14. Mapping test and release evidence

### 14.1 Representative entailment/projection test

The source baseline reports that `holon_webvoc_alignment_test.py` executed a representative Gouda graph through `rdflib` and `owlrl`, then applied fixed projection rules. The programmatic assertions confirmed:

- target allergen facts under the illustrative Route 1 model used at that stage;
- four mapped nutrition facts;
- five `PropertyValue` nodes, comprising four GPC facts and calcium as a residual nutrient.

Later evidence corrected the allergen direct-equivalence assumption. The test remains evidence that deterministic transformation is executable, but its allergen axiom is superseded by the current two-representation model.

### 14.2 Real Brick Route 3 test

`verify_brick10000030_route3.py` reportedly populated the real Cheese shape with four GPC values and ran the generic Route 3 query without changing the query. It produced the expected four `schema:PropertyValue` nodes.

This supports the claim that one generic GPC projection rule can handle many Brick Attribute Types, provided the Product Holon construction convention exposes the source identifier, label and value in a consistent graph pattern.

### 14.3 Regression implications

A production release should convert each reported test into a versioned regression fixture:

- source Product Holon graph;
- semantic-release manifest;
- mapping-set version;
- expected entailment closure;
- expected publication graph;
- expected absent facts;
- expected validation report;
- deprecation and drift test variants.
