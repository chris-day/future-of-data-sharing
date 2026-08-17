---
icon: lucide/git-compare
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Semantic Bridge Evidence
## Part IV — Semantic bridge evidence

## 8. Mapping routes and structural distinctions

### 8.1 Route framework

The final route framework is:

| Route | Evidence-based description |
|---|---|
| 1 | Same meaning and compatible graph shape; eligible for reviewed direct alignment. |
| 2 | Meaning can be preserved only through conditional or structural transformation. |
| 3 | Publishable fact without a first-class target; use `schema:PropertyValue`. |
| 4 | Inapplicable, private, B2B-only or deliberately excluded fact. |

### 8.2 Direct correspondence versus structural transform

The central technical distinction is whether the source and target assertions have the same graph shape.

A direct property equivalence can entail the same relationship under another property. It cannot:

- convert an object record into a string;
- inspect one property’s literal value to select another output property;
- create a new `PropertyValue` node with several fields;
- aggregate or format several values into one output.

Those operations require a rule or transform.

### 8.3 Allergen correction

The real Web Vocabulary v1.16 source described `gs1:allergenStatement` as a datatype property with range `rdf:langString` and a definition indicating one textual string. The real GDSN allergen structure is a two-hop coded record. Therefore:

- the structured chain is not soundly equivalent to `gs1:allergenStatement`;
- a rule may derive a text statement from the structured chain if governance approves the vocabulary lookup and formatting;
- the LOOM output identified a separate flat GDSN attribute, `gdsn:a-1463136308`, as a direct lexical candidate for `gs1:allergenStatement`;
- the flat statement and structured allergen records are related but distinct source representations.

### 8.4 Nutrient mapping

The source baseline mapped four nutrient codes to schema.org nutrition properties:

| GDSN code | Target property |
|---|---|
| `ENERC` | `schema:calories` |
| `FAT` | `schema:fatContent` |
| `PRO-` | `schema:proteinContent` |
| `NA` | `schema:sodiumContent` |

The mapping is conditional on the code in a structured record and is therefore Route 2. Calcium (`CA`) had no corresponding property in the examined `schema:NutritionInformation` set and used Route 3 in the worked example.

### 8.5 GPC generic projection

Most tested GPC Brick facets had no Web Vocabulary candidate. The generic publication pattern is:

```json
{
  "@type": "schema:PropertyValue",
  "schema:propertyID": "gpc:20000031",
  "schema:name": "Type of Cheese",
  "schema:value": "GOUDA"
}
```

This preserves the source identifier and readable label without asserting a native target property.

### 8.6 Publication allow-list

A mapping does not automatically authorise publication. Route 4 is a separate policy decision. The source evidence repeatedly distinguishes:

- internal or recipient-specific GDSN detail;
- public product facts;
- marketplace-owned commercial facts;
- inapplicable cross-category shape slots.

The bridge package therefore requires both semantic mappings and a publication allow-list.

---

## 9. SSSOM governance model

### 9.1 Why a mapping registry is required

The source evidence shows that mapping knowledge cannot safely remain in label-comparison scripts or hard-coded queries. A governed registry is needed to retain:

- candidate source;
- review status;
- mapping predicate;
- confidence;
- cardinality;
- structural assumptions;
- source and target releases;
- reviewer and decision date;
- rejection rationale;
- compilation status.

### 9.2 Representative SSSOM seed records

The following rows are based on the real LOOM output and reconciliation. They remain candidates until formally reviewed.

| subject_id | predicate_id | object_id | justification | cardinality | status note |
|---|---|---|---|---|---|
| `gdsn:a-1292425203` | `skos:closeMatch` | `gs1:gtin` | `semapv:LexicalMatching` | n:1 context | Three sibling GDSN GTIN attributes also matched; packaging level requires review. |
| `gdsn:a812659001` | `skos:closeMatch` | `gs1:ingredientStatement` | `semapv:LexicalMatching` | 1:1 candidate | Tool-corroborated; range and domain review still required. |
| `gpc:20002867` | `skos:closeMatch` | `gs1:sharpnessOfCheese` | `semapv:LexicalMatching` | 1:1 candidate | Term correspondence corroborated; value-set equivalence remains unreviewed. |
| `gdsn:a-1463136308` | `skos:closeMatch` | `gs1:allergenStatement` | `semapv:LexicalMatching` | 1:1 candidate | More structurally plausible direct candidate than the coded chain. |
| `gdsn:a2008988543` | `skos:closeMatch` | `gs1:nutrientBasisQuantity` | `semapv:LexicalMatching` | 1:1 candidate | Corroborates the earlier direct-source finding. |

### 9.3 Promotion and compilation

A candidate is not promoted merely by changing `skos:closeMatch` to `owl:equivalentProperty`. The review shall establish:

- semantic equivalence or the intended weaker relation;
- domain and range compatibility;
- datatype and language compatibility;
- graph-shape compatibility;
- cardinality and packaging-level meaning;
- target publication role;
- regression examples.

Approved SSSOM records are the source of truth. OWL axioms and rules are compiled outputs.

### 9.4 Mapping cardinality

The GTIN result demonstrates why cardinality metadata matters. Four GDSN attributes matched one target term. A reviewer must determine whether the source attributes represent:

- the same concept at different packaging levels;
- distinct roles that should map to narrower targets;
- context-specific aliases;
- false lexical matches.

Collapsing them without review could publish the wrong identifier.

### 9.5 Rejected mappings

Rejected candidates should remain in the SSSOM set with rationale. This prevents repeated rediscovery and supports audits when source labels or definitions change.
