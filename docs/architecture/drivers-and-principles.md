---
icon: lucide/compass
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Drivers and Principles
## 2. Architecture drivers and principles

### 2.1 Current-state challenges

The architecture responds to six related challenges.

**Application-centric transformation.** Brand owners and trading partners commonly transform data from PLM, PIM, ERP, DAM, regulatory and supplier systems into application-specific message or feed structures. Repeating this transformation for GDSN, marketplaces, web pages, AI feeds and connected packaging creates duplication and semantic drift.

**Large source models.** The inspected GDSN ontology contains thousands of attributes and hundreds of code lists, including retailer- and region-specific extensions. The inspected GPC ontology contains 22,281 classes, including 5,318 Bricks and thousands of attribute types and values. These models are valuable sources but are not suitable as unrestricted per-product payloads.

**Category specificity.** Web Vocabulary and schema.org provide generic publication terms but do not reproduce every GPC Brick-specific facet. Conversely, GPC provides category-specific facets but is not the vocabulary that public web parsers and product feeds generally expect.

**Validation gap.** Publishing structured data does not, by itself, prove that the data is complete, structurally sound or category-appropriate. A product graph needs a validation contract generated from the same source semantics.

**Mapping governance.** Opaque generated identifiers, structural differences and differing vocabulary scope make naive local-name or label matching unsafe. Mapping candidates require provenance, review, cardinality analysis, structural analysis and version control.

**AI trust.** AI agents need bounded, current and traceable product facts. They should not be asked to infer product truth from an unrestricted model, execute final compliance rules or silently repair invalid source data.

### 2.2 Stakeholders and use cases

| Stakeholder | Representative use cases |
|---|---|
| Brand owner or manufacturer | Construct a governed product representation from source systems; validate it before publication; maintain provenance and lifecycle. |
| Data pool and trading partner | Exchange complete, recipient-appropriate master data using GDSN mechanisms. |
| Retailer or distributor | Consume authoritative product facts; apply local assortment and commercial data; publish selected views. |
| Marketplace | Reuse product truth while adding seller-owned `Offer`, availability, price and review information. |
| Regulator or conformity assessor | Trace assertions to source, rules and validation evidence. |
| Consumer application | Retrieve a bounded, human-appropriate and machine-readable product representation. |
| AI agent | Retrieve validated product facts, follow semantic links and generate grounded answers without inventing attributes. |
| Standards and vocabulary steward | Govern source models, mapping sets, semantic releases and deprecations. |

### 2.3 Proposed architecture requirements

| ID | Requirement |
|---|---|
| PH-R01 | Every Product Holon shall have a stable identity anchored by an applicable GS1 identifier. |
| PH-R02 | A Product Holon shall declare its product classification and the version of the classification scheme used. |
| PH-R03 | A Product Holon shall contain only assertions applicable to the represented product, context and release. |
| PH-R04 | Each assertion shall be traceable to an authoritative source, publisher or transformation. |
| PH-R05 | Product-instance data shall be validated against released SHACL shapes before approved publication. |
| PH-R06 | Validation shapes, ontology modules, mapping sets and product instances shall remain distinct artefact classes. |
| PH-R07 | Semantic mappings shall be versioned and governed as first-class records, not embedded only in application code. |
| PH-R08 | Automated lexical matches shall remain candidates until reviewed by an authorised human or governance process. |
| PH-R09 | Direct OWL equivalence shall only be compiled where meaning, cardinality and graph shape are compatible. |
| PH-R10 | The architecture shall support multiple audience-specific representations derived from one governed product representation. |
| PH-R11 | Manufacturer-owned product facts shall be distinguishable from seller- or marketplace-owned commercial facts. |
| PH-R12 | Deterministic engines shall perform validation, entailment and approved transformations at the trust boundary. |
| PH-R13 | The architecture shall preserve unmapped but publishable facts without presenting them as first-class mapped terms. |
| PH-R14 | Non-public, commercially sensitive or recipient-specific facts shall be controlled by explicit publication policy. |
| PH-R15 | Every release shall be reproducible from versioned source models, mapping records, build tools and tests. |

### 2.4 Architecture principles

1. **Identity-centred.** Product information is organised around persistent GS1 identifiers rather than application records.
2. **Bounded but extensible.** A Product Holon is deliberately right-sized for one product and context, while retaining links to broader models.
3. **Semantically explicit.** Classes, properties, code values and mappings use resolvable identifiers and declared meanings.
4. **Source-authoritative.** Assertions retain the authority and provenance of the system or organisation entitled to state them.
5. **Validated before publication.** Machine-readable publication follows validation rather than substituting for it.
6. **Open-world compatible.** New facts and domain extensions may be added without forcing one closed, monolithic payload on every consumer.
7. **Representation-independent.** One governed product representation may produce several serialisations and audience views.
8. **Human-governed, machine-executable.** Machines generate candidates and compiled artefacts; accountable humans approve semantic commitments.
9. **Deterministic at the trust boundary.** Validation and rule execution are delegated to deterministic engines.
10. **Versioned and reproducible.** Source, generated, reviewed and compiled artefacts form a traceable release chain.

### 2.5 Assumptions and constraints

The architecture assumes that an implementation can obtain an authoritative product-to-GPC-Brick classification from a PIM, GDSN record, lookup file or service. The ontology files alone do not contain per-GTIN product instances. It also assumes that generated ontology identifiers may be opaque and that labels are therefore candidate-generation aids rather than semantic keys.

The current reference implementation demonstrates selected attributes and four Bricks. It does not establish complete GDSN coverage, production throughput, formal security controls or universal downstream parser behaviour.

### 2.6 Non-goals

The architecture does not seek to expose all available data to every consumer, flatten every GDSN code list into named Web Vocabulary properties, or use an LLM as a substitute for an ontology, validation engine, mapping registry or rules engine.

---
