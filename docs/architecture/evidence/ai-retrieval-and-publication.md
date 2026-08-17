---
icon: lucide/brain-circuit
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# AI, Retrieval, and Publication Evidence
## Part VII — AI, retrieval and publication evidence

## 27. Neuro-symbolic execution model

### 27.1 Reported structured-decomposition evidence

The source baseline reviewed Sadowski and Chudziak, “Structured Decomposition for LLM Reasoning: Cross-Domain Validation and Semantic Web Integration” (arXiv:2601.01609). The reported architecture separated:

- LLM entity identification and assertion extraction;
- deterministic OWL/SWRL reasoning;
- result inspection.

The reported ablation showed that the reasoner-driven condition outperformed direct LLM rule application by 9.7 F1 points overall and by 19.9 points on the clinical-trial task. The source analysis used this as evidence for the execution boundary, not as evidence about Product Holons specifically.

### 27.2 Product Holon application

The analogous Product Holon pattern is:

1. resolve the product identity and retrieve authoritative data;
2. construct a bounded graph;
3. validate with SHACL;
4. infer and transform with approved deterministic rules;
5. export a target graph;
6. let the LLM explain or compare the resulting facts.

### 27.3 Auditability

The architecture can retain:

- the source record;
- the Product Holon graph;
- the validation report;
- the mapping records;
- the rule and query versions;
- the target graph;
- the generated narrative.

This provides a reviewable path from a natural-language response to the product facts and rules that supported it.

---

## 28. Graph-grounded retrieval

### 28.1 Retrieval pattern

The Product Holon is created by structural graph traversal rather than by retrieving arbitrary text chunks:

- identifier to product record;
- product record to GPC Brick;
- Brick to ancestor chain;
- Brick to Attribute Types and Values;
- product to populated GDSN records;
- product to parent, child or component links.

### 28.2 Advantages over unrestricted vector retrieval

- controlled values are matched exactly;
- category scope prevents irrelevant attributes;
- multi-hop parent/child and ancestor relationships remain explicit;
- source identifiers and provenance are preserved;
- current resolver-linked data can be retrieved rather than relying only on a stale text index;
- the bounded graph fits the intended reasoning context.

### 28.3 Distinction from graph construction from text

Microsoft GraphRAG work commonly constructs graphs from unstructured text with LLM assistance. The Product Holon architecture starts from governed semantic and product-data sources. An LLM may navigate or narrate the graph but does not define the authoritative classification or code values.

---

## 29. Resolver and publication evidence

### 29.1 Standards-backed mechanisms

The source baseline identified these GS1-Conformant Resolver mechanisms as relevant:

- `Accept`-based media-type negotiation;
- JSON-LD linkset responses;
- `linkType` selection;
- `Accept-Language` and context differentiation;
- batch/lot and serial qualifiers;
- links inherited or selected according to resolver rules.

### 29.2 Proposed Product Holon use

A conformant resolver could link a GTIN to:

- a human-readable product page;
- an approved Web Vocabulary/schema.org JSON-LD representation;
- a nutrition resource;
- a product-safety or regulatory resource;
- an authenticated partner representation;
- a Product Holon API.

A Product Holon-specific link type or authenticated audience convention is proposed, not established by the evidence as existing GS1 guidance.

### 29.3 Live versus cached construction

Two implementation modes are consistent with the architecture:

- pre-build and cache validated Product Holons and their views;
- construct on request from current authoritative data, then validate and cache.

The source evidence did not benchmark either mode. Production choice requires latency, freshness and governance analysis.

---
