---
icon: lucide/map
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Roadmap, Benefits, and Risks
## 11. Benefits, limitations and risks

### 11.1 Benefits for brand owners

- reduces repeated transformation by establishing one governed product representation;
- exposes source-data quality issues before publication;
- maintains a traceable relationship between internal facts and external representations;
- supports multiple channels without manually duplicating product descriptions;
- allows category-specific extension without exposing the entire GDSN model.

### 11.2 Benefits for trading partners and marketplaces

- supports reuse of authoritative product truth;
- separates stable product facts from seller-specific offers;
- provides explicit version, provenance and validation evidence;
- permits B2B detail and public detail to coexist without one universal payload;
- improves the basis for faceted search through GPC-controlled values.

### 11.3 Benefits for consumers and AI agents

- bounded product context reduces irrelevant attributes;
- controlled values improve exact filtering for allergies, claims, certifications and category facets;
- validation catches structural and value errors before publication;
- resolvable identifiers support current representations;
- provenance and deterministic rules improve explainability and auditability.

### 11.4 Interoperability benefits

The architecture does not require all systems to adopt one physical model. It provides explicit semantic modules, mappings and publication profiles that allow different systems to retain their operational structures while sharing meaning and evidence.

### 11.5 Known limitations

- Product Holon is not yet an approved GS1 term;
- the current source-derived namespaces and persistence policy require governance;
- Web Vocabulary coverage of Brick-specific facets is limited;
- generic `PropertyValue` publication may be interpreted less strongly by downstream systems;
- mapping approval is labour-intensive and cannot be replaced by lexical matching;
- a fixed cross-category GDSN shape is not sufficient for all categories;
- the source evidence does not demonstrate production-scale performance or security;
- resolver mechanisms are reusable, but a Product Holon-specific profile is not yet standardised.

### 11.6 Risk register

| Risk | Consequence | Mitigation |
|---|---|---|
| Working term is mistaken for approved GS1 terminology | Governance and stakeholder confusion | Retain status notice; obtain formal architecture decision before external positioning. |
| Lexical candidate is compiled as equivalence | Incorrect inference and publication | Mandatory SSSOM review gate; structural and cardinality tests. |
| Generated opaque IRIs change between releases | Broken mappings and references | Persistence policy, source-ID tracking, release diff and deprecation records. |
| Shape profile is too broad or too narrow | Inapplicable fields or missing validation | Modular core plus category/use-case profiles; monitor validation and Route 4 rates. |
| Product and Offer facts are merged | Incorrect authority and stale commercial data | Separate product, offer, seller and review objects with provenance. |
| LLM performs final rule logic | Non-deterministic results and poor auditability | Deterministic SHACL/OWL/rule/query services; LLM restricted to retrieval and narration. |
| Public view leaks partner-specific data | Commercial or contractual harm | Explicit allow-lists, access control, data classification and publication tests. |
| Vocabulary drift silently removes facts | Incomplete or misleading views | Release-pinned bridge packages and regression tests. |
| Route 3 facts are ignored by consumers | Reduced discoverability | Prioritise first-class mappings, publish source IDs, measure downstream behaviour. |
| Valid signature is treated as factual truth | False confidence in an incorrect or unauthorised claim | Require authority, evidence, market/time and semantic-conformance checks; use “Verifiable Product Statement”. |
| Issuer key is compromised or mis-scoped | Forged or over-broad product statements | Key protection and rotation, scoped authority, credential status, compromise response and audit. |
| Related Product Holon changes after credential issuance | Credential appears valid while the relied-upon resource has drifted | Bind exact resources with `relatedResource` digests and fail verification on mismatch. |
| Credential and embedded page copy diverge | Conflicting verification results | Prefer one canonical `application/vc` resource; embed only under strict synchronisation and digest controls. |
| Licence remains unresolved | Publication or reuse blocked | Resolve document, source and generated-artefact licensing before external release. |

### 11.7 Open architecture decisions

The following decisions should be taken through a formal architecture process:

- name and status of the Product Holon concept;
- authoritative hosting and namespace policy;
- minimum Product Holon profile;
- mapping governance membership and approval thresholds;
- modular GDSN shape strategy;
- public, partner and internal publication profiles;
- Product Holon resolver link types or profiles;
- HTML Semantic Proof and Product Statement Credential profile namespace;
- issuer-authority trust model, approved cryptosuites, verification methods and status infrastructure;
- credential granularity, expiry, renewal and withdrawal rules;
- formal workstream ownership across 8.3.b, 8.4.a and 8.4.b;
- conformance levels and certification approach;
- security and operational requirements.

---

## 12. Adoption roadmap

### 12.1 Stage 0 — Architecture decision and governance setup

- approve or rename the working concept;
- nominate source-model, semantic, mapping and publication owners;
- resolve licence and publication status;
- approve the two-plane and four-phase architecture;
- establish an Architecture Decision Record and SSSOM repository.

### 12.2 Stage 1 — Minimum viable Product Holon profile

Use the four demonstrated Bricks as an initial test set:

- Cheese (Frozen), `10000030`;
- Smartphones, `10001198`;
- Beer, `10000159`;
- Sugar/Sugar Substitutes (Shelf Stable), `10000043`.

Define:

- the minimum identity, classification, provenance and validation fields;
- a modular cross-category GDSN core;
- category-specific GDSN additions;
- canonical JSON-LD contexts;
- expected conforming and non-conforming examples.

### 12.3 Stage 2 — Mapping-governance pilot

- import all 237 unique LOOM candidate pairs into SSSOM;
- prioritise the GDSN-to-Web Vocabulary candidates relevant to the MVP Bricks;
- review cardinality, graph shape and publication route;
- record rejected mappings as well as approved mappings;
- compile a bridge package and regression suite;
- measure Route 1, Route 2, Route 3 and Route 4 distribution.

### 12.4 Stage 3 — Verifiable publication and resolver pilot

- define the versioned HTML Semantic Proof and GS1 Product Statement Credential profiles;
- publish validated native GDSN/GPC and schema.org/GS1 Web Vocabulary representations for the MVP Product Holons;
- expose a human-readable page with stable JSON-LD script identifiers and canonical alternate links;
- bind the Product Holon, script, SHACL profile, validation report and mapping release using credential `relatedResource` digests;
- implement an issuer verification method, signing policy and credential-status service using W3C Recommendation-track standards;
- preserve Product and Offer separation;
- test media-type, profile, language and link-type selection;
- introduce access control for partner-only representations;
- demonstrate verification of signature, resource integrity, issuer authority, status, validity, context and SHACL conformance;
- test retrieval by an AI agent that is unable to bypass validation, verification and reasoning services.

### 12.5 Stage 4 — Scale and harden

- expand Brick and attribute coverage;
- benchmark catalogue-scale build, validation and publication performance;
- implement incremental rebuilds;
- introduce security, monitoring, withdrawal and service-level controls;
- validate namespace persistence and deprecation behaviour;
- establish production release management.

### 12.6 Stage 5 — Standardisation and ecosystem adoption

- evaluate whether the architecture should become a GS1 architecture principle, technical specification, implementation guideline or profile;
- align terminology and artefact status with GS1 governance;
- publish conformance tests and implementation guidance;
- engage data pools, Member Organisations, brand owners, marketplaces and AI ecosystem participants;
- define migration and coexistence with existing implementations.

### 12.7 Success measures

Proposed measures include:

- percentage of Product Holons passing validation on first submission;
- reduction in duplicated channel-specific transformation logic;
- proportion of published facts using reviewed first-class mappings;
- Route 3 fallback rate by Brick and property;
- mapping review throughput and rejection rate;
- time to detect and remediate vocabulary drift;
- resolver freshness and availability;
- percentage of HTML Semantic Proofs passing JSON-LD, profile and linked-resource tests;
- credential verification, status and authority-resolution success rates;
- number and rate of digest mismatches, revocations, suspensions and stale credentials;
- time for an agent to retrieve and verify an evidence-backed product answer;
- reduction in divergent marketplace product descriptions;
- AI answer accuracy against validated product facts;
- traceability of every published assertion to source and mapping release.

---
