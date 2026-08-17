---
icon: lucide/database-zap
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Semantic Source Evidence
## 3. Direct GPC and GDSN observations

### 3.1 GPC observations

The source baseline reports that the supplied GPC ontology contains 22,281 `owl:Class` resources across six levels:

| Level | Count reported |
|---|---:|
| Segment | 45 |
| Family | 162 |
| Class | 938 |
| Brick | 5,318 |
| Attribute Type | 2,085 |
| Attribute Value | 13,733 |

The evidence establishes that GPC is more than a category tree. Each Brick may define Attribute Types and controlled Attribute Values. This creates a category-scoped faceting model suitable for Product Holon construction and SHACL generation.

The Cheese (Frozen) chain used throughout the examples is:

`50000000 Food/Beverage → 50130000 Milk/Butter/Cream/Yogurts/Cheese/Eggs/Substitutes → 50131800 Cheese/Cheese Substitutes → 10000030 Cheese (Frozen)`.

### 3.2 GDSN observations

The source baseline reports:

- 30,630 RDF descriptions;
- approximately 3,946 core trade-item attributes;
- numerous retailer- and region-specific extension groups;
- 557 distinct code lists.

Examples of extension-group sizes included BestBuy, Australasian Healthcare, Carrefour and GS1 US Healthcare. The important architectural conclusion is that the source model includes both globally relevant product facts and recipient-specific or operational detail. A public Product Holon view therefore requires a deliberate allow-list.

The baseline identified code lists and attributes relevant to consumer and AI use cases, including:

- 218 allergen-type values;
- 1,080 nutrient-type values;
- 937 packaging-marked accreditation values;
- 292 claim-element values;
- ingredient statements;
- preparation instructions;
- recipes;
- recycled-content ratio;
- carbon-footprint and sustainability details;
- channel-specific marketing content.

These counts and examples are observations from the supplied source-derived ontology. They do not imply that the current reference shape exposes all of them.

### 3.3 Evidence for a bounded product unit

The source models are too large to use as per-product payloads. The evidence supports selecting a bounded subgraph based on:

1. product identifier;
2. GPC Brick and ancestor chain;
3. Brick-scoped Attribute Types and populated values;
4. populated GDSN facts selected by a profile;
5. product relationships and provenance.

This product-specific graph is the evidence basis for the Product Holon concept.

### 3.4 Value for shopping and agent use cases

The source observations support the following capabilities:

- category-appropriate faceted filtering using controlled GPC values;
- allergen and dietary filtering using structured codes and statements;
- certification and trust-signalling through controlled accreditation data;
- nutrition comparison beyond basic macros where downstream profiles support it;
- claim substantiation and regulatory context;
- sustainability and packaging information;
- localised connected-pack content.

The public interpretation layer remains Web Vocabulary/schema.org or another approved target profile rather than raw exposure of the entire source model.

---
