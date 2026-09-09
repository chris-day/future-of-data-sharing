---
icon: lucide/network
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Architecture Overview
## 4. Architecture overview

### 4.1 Four phases

| Phase | Purpose | Primary outputs |
|---|---|---|
| **1. Build the semantic foundation** | Transform source models into separately versioned GDSN and GPC semantic modules and validation inputs. | TSV artefacts, OWL modules, diagnostics, generated SHACL resources. |
| **2. Construct and validate Product Holons** | Assemble a bounded product-instance graph and test it against the applicable profiles. | Product Holon, validation report, provenance and release metadata. |
| **3. Align through a governed semantic bridge** | Curate and compile mappings from source semantics to approved publication semantics. | SSSOM mapping set, OWL bridge module, DL-safe rule module, export queries and regression tests. |
| **4. Publish, resolve and consume** | Generate and distribute audience-appropriate representations to systems, marketplaces, applications and AI agents. | GDSN/GPC-native representation, Web Vocabulary/schema.org JSON-LD, HTML Semantic Proof, Verifiable Product Statement, resolver links, APIs and feeds. |

### 4.2 Semantic control plane

The semantic control plane owns artefacts that apply across many products:

- source-model extracts and transformation rules;
- GDSN and GPC ontology modules;
- code-list and datatype resources;
- generated SHACL profiles;
- candidate mapping outputs;
- SSSOM mapping sets and review status;
- compiled OWL and DL-safe rule modules;
- projection/export queries;
- conformance tests, release manifests and deprecation records.

Changes in the control plane require controlled release and regression testing before they affect product publication.

### 4.3 Product data plane

The product data plane processes product-specific facts:

- resolve GTIN and GPC Brick;
- retrieve authoritative source values;
- assemble the Product Holon;
- validate it against the released profiles;
- select an authorised publication profile;
- apply the released bridge package;
- generate the canonical native representation and approved web discovery projection;
- package the human-readable page, machine-readable scripts, authority metadata and conformance evidence as an HTML Semantic Proof;
- issue or link a Verifiable Product Statement and status record;
- publish, distribute or resolve the proof package and its related resources;
- record provenance, validation, credential and publication evidence.

### 4.4 Logical components

| Component | Responsibility |
|---|---|
| Source-model repository | Stores versioned Navigator extracts and related source files. |
| Semantic transformation pipeline | Produces TSV and OWL artefacts, preserving diagnostics and source identifiers. |
| GDSN semantic module | Represents GDSN classes, properties, datatypes, associations and code-list structures. |
| GPC semantic module | Represents classification hierarchy, Bricks, Attribute Types and Attribute Values. |
| Shape-generation service | Produces Brick-scoped and selected cross-category SHACL shapes. |
| Product Holon construction service | Resolves classification and assembles bounded product-instance graphs. |
| Validation service | Runs SHACL and returns machine-readable reports. |
| Mapping candidate service | Generates lexical or other candidate correspondences across source and target vocabularies. |
| SSSOM mapping registry | Stores mappings, provenance, confidence, cardinality, justification and review status. |
| Bridge compiler | Generates reasoner-usable axioms/rules and export artefacts from approved mapping records. |
| Projection service | Produces Web Vocabulary, schema.org or other profile-specific representations. |
| HTML Semantic Proof publisher | Packages human-readable content, identifiable JSON-LD scripts, representation links, authority metadata and conformance evidence. |
| Credential issuer | Issues Verifiable Product Statements using an approved credential profile and signing policy. |
| Credential-status service | Publishes revocation, suspension or other current-status information. |
| Credential and authority verifier | Verifies securing mechanisms, resource digests, status and the issuer’s authority for the asserted product scope. |
| Publication repository or API | Stores or serves released Product Holons and derived representations. |
| GS1 Digital Link resolver | Selects appropriate links or representations using standard resolver mechanisms. |
| Provenance and audit store | Records source, build, validation, mapping, credential and publication evidence. |

### 4.5 End-to-end information flow

1. A source-model release is ingested and transformed.
2. Diagnostics are reviewed; no malformed multiplicity or limit is silently guessed.
3. Separate GDSN and GPC ontology modules and SHACL resources are released.
4. Candidate semantic mappings are generated over the released models and target vocabularies.
5. Mapping stewards review candidates in SSSOM and approve, reject or qualify them.
6. A bridge package is compiled and tested.
7. A product’s authoritative record supplies its GTIN, Brick and populated facts.
8. The Product Holon construction service creates a bounded graph.
9. The validation service applies the relevant Brick and GDSN shapes.
10. An authorised publication profile selects facts and invokes the released bridge package.
11. The publication service produces the canonical GDSN/GPC-aligned representation and the schema.org/GS1 Web Vocabulary discovery projection.
12. The HTML Semantic Proof publisher binds the page, script identifiers, source authority and conformance resources into one release.
13. The credential issuer signs selected product statements or cryptographic digests of the related resources and publishes credential status.
14. The proof package is published through the appropriate B2B, feed, API or resolver channel.
15. Consumers retrieve only the representation and authority level appropriate to their role and apply their own reliance policy.

### 4.6 Roles and responsibilities

| Role | Accountable responsibilities |
|---|---|
| GS1 source-model steward | Maintain authoritative model releases and change records. |
| Semantic artefact steward | Maintain transformation rules, namespaces, ontology releases and diagnostics. |
| Mapping steward | Review candidate mappings and record decisions in SSSOM. |
| Brand owner or data source | State and maintain product facts for which it is authoritative. |
| Data-pool or exchange operator | Transport and synchronise authorised B2B product data. |
| Resolver or publication operator | Serve approved representations according to link, media-type and access policies. |
| Credential issuer | Sign product statements only for the product, claim scope, market and effective period for which the issuer is authorised. |
| Trust and status operator | Publish issuer verification material, authority evidence and credential status. |
| Verifier or relying party | Validate the credential, resources, authority, context and evidence against a declared reliance policy. |
| Marketplace | Add and govern seller, offer, availability, rating and merchandising facts. |
| Conformance operator | Execute validation and regression tests and retain evidence. |
| AI agent | Retrieve, verify, interpret and narrate approved facts; it is not an authority for product truth. |

### 4.7 Trust and authority model

| Information category | Primary authority | Architectural treatment |
|---|---|---|
| Identifier allocation and key structure | Applicable GS1 identification governance | Used as the identity anchor; not inferred by an LLM. |
| GPC classification and value definitions | GPC governance and released source model | Referenced by version; used for scope and validation. |
| GDSN semantic definitions | GDSN/Global Data Model governance and released source model | Transformed into source-derived semantic artefacts with provenance. |
| Manufacturer product facts | Brand owner or authorised data source | Stored in the Product Holon with assertion provenance. |
| Mapping decisions | Designated semantic mapping governance | Recorded in SSSOM; compiled only after approval. |
| Price, availability and seller identity | Seller or marketplace | Added as `Offer`-level or equivalent commercial facts, separate from manufacturer product truth. |
| Reviews and ratings | Marketplace or review platform | Retain separate provenance and publication policy. |
| Credential authorship and integrity | Credential issuer controlling the approved verification method | Verified cryptographically and checked against current credential status. |
| Authority to assert product facts | Brand owner, authorised information provider, certification body, laboratory, regulator or other scoped authority | Verified independently of signature validity through registry, delegation, role, market and effective-period evidence. |
| Generated narrative | Application or AI agent | Derived output; shall reference validated facts and shall not be treated as a source assertion. |

### 4.8 Authoritative, generated and compiled artefacts

The architecture distinguishes four release classes:

1. **Authoritative source artefacts:** GS1 source-model releases and authoritative product records.
2. **Source-derived artefacts:** TSV, OWL and SHACL generated from those sources.
3. **Governed mapping artefacts:** SSSOM mapping records approved through review.
4. **Compiled and instance artefacts:** bridge axioms, rules, queries, Product Holons, validation reports, publication views, HTML Semantic Proofs and Verifiable Product Statements.

A compiled artefact shall be reproducible from its source release, tool version and mapping-set version.

### 4.9 Architecture decisions summary

The detailed decision records are retained in the companion technical evidence pack. The current binding decisions are:

- maintain separate GDSN and GPC modules;
- separate semantic control-plane processing from per-product data-plane processing;
- treat mappings as governed data in SSSOM;
- compile only reviewed mappings;
- use direct equivalence only for same-meaning, same-shape correspondences;
- use DL-safe rules for conditional semantic derivations where appropriate;
- keep SPARQL outside the ontology as a projection/export mechanism or explicitly versioned transform;
- use generic `PropertyValue` projection for publishable unmapped facts;
- exclude non-public facts through an explicit allow-list;
- require deterministic engines for validation, inference and approved transformation;
- retain a GDSN/GPC-aligned canonical Product Holon and derive the Web Vocabulary/schema.org projection;
- use an HTML Semantic Proof as the Phase 4 inspectable publication package;
- use Verifiable Product Statements for authorship, integrity and current-status verification, while keeping factual reliance dependent on source authority and evidence.


---

## Part I — Semantic foundation

The following section describes the semantic foundation used to construct and
validate Product Holons.

Continue to [Semantic Foundation](semantic-foundation.md) for Phase 1.
