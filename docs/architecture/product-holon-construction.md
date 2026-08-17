---
icon: lucide/hexagon
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Holon Construction
## 6. Phase 2 — Construct and validate Product Holons

### 6.1 Objective

Phase 2 creates a bounded product-instance graph from authoritative product data and validates it against the applicable released semantic profiles. This phase runs in the product data plane.

### 6.2 Required inputs

A construction request requires, at minimum:

- a GTIN or other applicable GS1 identifier;
- a GPC Brick assignment and GPC release;
- authoritative populated product facts;
- the applicable GDSN and GPC semantic-release identifiers;
- the applicable SHACL profile release;
- target-market, language, batch/lot, serial or audience context where relevant;
- source and publisher provenance.

A GTIN alone is insufficient unless a service can resolve it to the relevant product data and GPC Brick.

### 6.3 Construction sequence

1. Validate the identifier syntax and resolve any relevant GS1 Digital Link qualifiers.
2. Retrieve the authoritative product record and its current classification.
3. Load the applicable GPC Brick and ancestor chain.
4. Select populated Brick-scoped facts for the product.
5. Select applicable GDSN facts according to the Product Holon profile and data-access policy.
6. Preserve structured records, units, language and explicit zero values.
7. Attach relationships to parent, child or component Product Holons where required.
8. Attach source, transformation and effective-time provenance.
9. record the semantic and shape release identifiers.
10. emit the Product Holon as a graph suitable for SHACL validation.

### 6.4 Product Holon instance structure

The following example is conceptual and uses readable logical names. The production reference artefacts bind these concepts to generated CURIEs and mapping records.

```json
{
  "@context": {
    "ph": "https://example.org/product-holon/",
    "gpc": "gpc:",
    "gdsn": "gdsn:",
    "prov": "http://www.w3.org/ns/prov#"
  },
  "@id": "https://example.com/01/09506000134352",
  "@type": ["ph:ProductHolon", "gpc:10000030"],
  "ph:identity": {
    "ph:keyType": "GTIN",
    "ph:value": "09506000134352"
  },
  "ph:classification": {
    "ph:brick": "gpc:10000030",
    "ph:label": "Cheese (Frozen)",
    "ph:schemeVersion": "declared-by-release-manifest"
  },
  "ph:assertion": [
    { "ph:property": "gpc:20000031", "ph:value": "GOUDA" },
    { "ph:property": "gpc:20000192", "ph:value": "FIRM/SEMI-HARD" },
    { "ph:property": "gpc:20003081", "ph:value": "SEMI-HARD CHEESE" },
    { "ph:property": "gpc:20003080", "ph:value": "DIRECT CONSUMPTION" }
  ],
  "prov:wasDerivedFrom": "urn:source-record:authoritative-product-record",
  "ph:validationProfile": "urn:shape-release:gpc-brick-10000030-with-gdsn"
}
```

The example is not an assertion about a real commercial product. It demonstrates the bounded graph pattern established by the source evidence.

### 6.5 Brick-scoped attributes

Only Attribute Types defined for the selected Brick are included as category-specific facts. The source investigation showed that different Bricks have materially different profiles:

- Cheese (Frozen), `10000030`: six Attribute Types in the demonstrated release;
- Smartphones, `10001198`: two Attribute Types;
- Beer, `10000159`: nine Attribute Types in the source run, with six reproduced in the supplied shape excerpt;
- Sugar/Sugar Substitutes (Shelf Stable), `10000043`: one Attribute Type.

The architecture follows the released source even when an enumeration appears outdated. For example, the demonstrated Smartphone `System` enumeration stops at `3 G`. The semantic pipeline shall report and govern that source limitation; it shall not silently add `4 G` or `5 G`.

### 6.6 Cross-category GDSN facts

The current reference implementation adds a fixed, selected GDSN shape with eight properties across every tested Brick. The source comparison confirmed that this property set is identical for Cheese, Smartphones, Beer and Sugar. It includes GTIN, ingredient statement, recycled-content ratio, claim detail, allergen and nutrient structures.

This is a reference-implementation choice, not an architectural requirement that every category use the same eight properties. The fixed profile creates two known issues:

- some properties are inapplicable to a category, such as food-allergen slots for Smartphones;
- some clearly category-relevant GDSN properties are absent, including several cheese-related attributes found in the mapping evidence.

A production profile should therefore support a governed combination of cross-category core facts and category- or use-case-specific GDSN modules.

### 6.7 Structured records

The Product Holon shall preserve GDSN structure where that structure carries meaning. Allergen and nutrient data are not merely scalar strings. The real generated shape shows an allergen path through `AllergenRelatedInformation` and `Allergen`, while nutrient data passes through header/detail structures. Flattening may be appropriate for a publication view, but the source graph and the mapping record shall preserve how that flattening was derived.

### 6.8 Variety packs and composite products

GPC includes dedicated Variety Pack Bricks. The pack receives its own GTIN, classification and Product Holon. Constituent trade items retain their own GTINs, Bricks and Product Holons. GDSN trade-item hierarchy relationships link the parent and children, including quantities and component counts where supplied.

A composite Product Holon shall therefore reference child Product Holons rather than merge their category constraints. This supports independent validation, update and resolution of each constituent item.

### 6.9 SHACL validation

The validation service shall apply:

- the Brick-scoped GPC shape;
- the selected GDSN shape modules;
- identity and release-profile constraints;
- additional policy shapes where required for a publication or regulatory profile.

Validation shall return a machine-readable report with focus nodes, paths, constraint components and messages. A failing record shall not be silently repaired at the publication boundary.

### 6.10 Validation evidence

The source evidence records successful `pySHACL` tests in which:

- a conforming Cheese record returned `Conforms: True`;
- a deliberately invalid record returned `Conforms: False`;
- invalid firmness and nutrient codes were reported through `sh:InConstraintComponent`;
- a missing containment level was reported through `sh:MinCountConstraintComponent`;
- generated shapes for Cheese, Smartphones and Beer parsed and validated in the demonstrated generalisation check;
- the `gs1-gdsn-holon` tool incorporated parse, empty-graph, conforming-instance and broken-instance checks by default.

These results demonstrate the pattern, not full production conformance coverage.

### 6.11 Validation and truth

SHACL establishes conformity to the tested graph contract. It does not independently prove that the source assertion is factually correct. The architecture therefore requires both validation evidence and provenance. A valid but incorrectly sourced allergen assertion remains a data-governance failure.

### 6.12 Product Holon release states

A Product Holon may use the following proposed states:

| State | Meaning |
|---|---|
| Draft | Construction is incomplete or validation has not run. |
| Invalid | One or more required profiles fail. |
| Validated | Required profiles pass, but publication approval is pending. |
| Approved | Product and publication policies permit release. |
| Published | One or more representations have been released. |
| Superseded | A later Product Holon version has replaced this release. |
| Withdrawn | Publication is no longer authorised. |

### 6.13 Phase outputs

Phase 2 produces:

- a bounded Product Holon instance;
- a validation report;
- source and transformation provenance;
- links to parent or child Product Holons where applicable;
- a release status;
- the semantic and shape versions required by Phase 3 and Phase 4.

---

## Part III — Governed semantic alignment
