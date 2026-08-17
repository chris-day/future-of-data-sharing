---
icon: lucide/target
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Purpose and Scope
## 1. Purpose and scope

### 1.1 Purpose

The purpose of this document is to define a coherent Product Holon Architecture that connects GS1 source models, semantic artefacts, validation, mapping governance, publication and AI consumption. It states the current consolidated architecture rather than reproducing the chronological research path by which it was developed.

### 1.2 Scope

The architecture covers:

- transformation of GDSN and GPC source-model extracts into machine-readable semantic artefacts;
- generation of GPC Brick-scoped and selected GDSN SHACL constraints;
- construction of a bounded Product Holon for a GTIN or other appropriately qualified GS1 identifier;
- validation of product-instance data against released shapes;
- governance of mappings between GDSN, GPC, GS1 Web Vocabulary and schema.org;
- compilation of reviewed mappings into executable bridge artefacts;
- generation of business-to-business, marketplace, public-web and agent-facing representations;
- publication and resolution through APIs, feeds and GS1 Digital Link mechanisms;
- deterministic validation and reasoning in support of AI-enabled product discovery and interpretation.

### 1.3 Intended audience

The primary audience comprises architecture and standards specialists. Secondary audiences include product-data publishers, solution providers, data-pool operators, marketplaces, resolver operators and AI-agent developers who need to understand the authority, validation and publication boundaries.

### 1.4 Out of scope

The following are outside the present scope:

- replacement of GDSN data-pool publication and subscription services;
- replacement of GPC classification governance;
- definition of a new GS1 identification key;
- redesign of GS1 Web Vocabulary or schema.org;
- definition of marketplace pricing, availability, seller or review models beyond their relationship to product truth;
- autonomous or decentralised product nodes as a requirement of GS1 Digital Link;
- a complete production security architecture;
- formal GS1 approval, standardisation or certification;
- a claim that every GDSN or GPC term has a Web Vocabulary equivalent.

### 1.5 Relationship to GS1 standards and services

The architecture reuses existing GS1 assets in distinct roles:

| Asset | Role in the architecture |
|---|---|
| GDSN and the Global Data Model | Authoritative source semantics and business-to-business product facts, subject to the governance of the applicable GS1 standards and implementations. |
| GPC | Product classification, Brick scope, Brick-specific attribute types and controlled values. |
| GS1 Web Vocabulary | Public, schema.org-aligned publication vocabulary for supported product concepts. |
| GS1 Digital Link | Identification and resolution mechanisms for linking GS1 identifiers to one or more representations or services. |
| GS1 identifiers | Stable identity anchors for product and related entities. |

The architecture does not treat these assets as competitors. It assigns them complementary roles within one information lifecycle.

### 1.6 Status of the Product Holon concept

“Holon” originates outside GS1 and denotes a unit that is both a whole and part of a larger whole. The source investigation found no evidence that “Product Holon” is an existing GS1-defined term. This architecture therefore uses it as an explicit proposal. Standards-backed behaviours, source-derived artefacts and new architectural choices are labelled separately throughout.

### 1.7 Document conventions

Logical property names are used in conceptual examples for readability. The current generated GDSN ontology uses opaque source-ID-based CURIEs such as `gdsn:a812659001` and `gdsn:assoc_-1935341322_-474206270_1`. Production bindings shall be generated from the released semantic artefacts and mapping registry rather than inferred from the readability-oriented examples in this document.

---
