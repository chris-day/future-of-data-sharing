---
icon: lucide/file-search
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Evidence Basis
## Part I — Evidence basis

## 1. Scope, method and provenance

### 1.1 Source baseline

The authoritative baseline for this restructuring is:

- `gs1-gdsn-holon-v1.31.0.md`, version 1.31.0, dated 30 July 2026.

The baseline combined 29 numbered sections, five appendices and a source list. It recorded the progressive development of the architecture, including findings later corrected by real generated artefacts. This pack consolidates the final position while retaining the reasoning behind material changes.

### 1.2 Supplied and referenced artefacts

The source baseline reports direct inspection or use of the following artefacts:

| Artefact | Reported role |
|---|---|
| `gdsn.ttl` | Source-derived GDSN ontology, RDF/XML despite the extension, 30,630 RDF descriptions. |
| `gpc.ttl` | GPC ontology, Turtle, 22,281 `owl:Class` resources. |
| `GDSN_TSV_Transformer_README_v0.1.0.md` | Documentation for Navigator JSON to TSV transformation. |
| `GDSN-TSV-Mapping-v0.1.0.md` | Mapping decisions for TSV generation. |
| `gpc-brick-10000030-with-gdsn.shacl.ttl` | Generated Cheese (Frozen) shape with selected GDSN constraints. |
| `gpc-brick-10001198-with-gdsn.shacl.ttl` | Generated Smartphones shape with selected GDSN constraints. |
| `gpc-brick-10000159-with-gdsn.shacl.ttl` | Generated Beer shape with selected GDSN constraints. |
| `gpc-brick-10000043-with-gdsn.shacl.ttl` | Generated Sugar/Sugar Substitutes shape with selected GDSN constraints. |
| `gs1_mappings_001.ttl` | 474 directional LOOM/BioPortal mapping records. |
| `gs1_terms.txt` | 28,101 extracted terms used for candidate generation. |
| `gs1_sortedUnique.txt` | Deduplicated term list, also 28,101 terms. |
| `holon_webvoc_alignment_test.py` | Representative OWL-RL and SPARQL projection verification. |
| `verify_brick10000030_route3.py` | Verification that the generic Route 3 rule handled the real Cheese shape without modification. |
| `gs1-holon-bridge.omn` | Manchester Syntax representation of the illustrative bridge and Gouda ABox. |
| `holon-webvoc-construct-rules.sparql` | Consolidated Route 2 and Route 3 SPARQL rules. |
| `CatalogueItemNotification_ADD.xml` | Concrete GDSN source-evidence example containing sender, receiver, data recipient, source data pool, content owner, information provider, brand owner, GTIN hierarchy, GPC Brick, target market and effective-time fields. |
| `gdsn(1).ttl` | Supplied GDSN ontology copy used in this revision to confirm the canonical `urn:gs1:std:gdsn:` namespace, exact source-derived CURIEs and object/datatype structure. |
| `gpc(1).ttl` | Supplied GPC ontology copy used in this revision to confirm the canonical `urn:gs1:std:gpc:` namespace and Brick identity. |
| `kato-instances(1).ttl` | Supplied RDF instance graph derived from the GDSN notification; used to confirm the native TradeItem, classification, party, market, description and code-value graph pattern. |
| `GA slide narratives.docx` | Vision 2030 narrative framing identifiers, Web Vocabulary/schema.org as grammar, Verifiable Credentials as proof, registries as the trust layer and Digital Link as the connection mechanism. |
| `Beideman Excerpts from GA meeting.pptx` | Portfolio narrative and use-case evidence for signed claims, authority-ready registries, agent reachability and standards-as-code. |
| `GS1_GDSN_Product_Holon_Architecture_Presentation_v1.1.0.pptx` | Visual architecture evidence; Phase 4 depicts JSON-LD, conformance, provenance, metadata and an optional Verifiable Credential in the publication package. |

The current conversation supplied the baseline Markdown file and, for this revision, the GDSN notification XML, the corresponding RDF instance graph, current GDSN/GPC ontology copies, portfolio narratives and Holon presentation listed above. Other historical implementation artefacts remain treated according to the evidence reported in the baseline unless separately inspected.

### 1.3 Evidence method

The original work used several evidence methods:

- direct parsing and counting of GDSN and GPC ontology artefacts;
- inspection of GPC hierarchy, Brick attributes and controlled values;
- inspection of generated SHACL shapes;
- execution of `pySHACL` against conforming and deliberately invalid instances;
- execution of `rdflib` and `owlrl` for representative entailment tests;
- execution of SPARQL CONSTRUCT rules and programmatic output checks;
- inspection of a real Web Vocabulary v1.16 source slice;
- execution and parsing of LOOM/BioPortal mappings;
- literature review of ontology mapping, SSSOM, SWRL, description logic and Graph-RAG;
- review of GS1 Digital Link resolver mechanisms;
- comparison of the evolving design with the independently implemented `gs1-gdsn-holon` tool.

### 1.4 Verification boundaries

Several limitations remain important:

- the K10X video narration and on-screen content were not transcribed directly;
- the full Web Vocabulary v1.16 source could not be fetched in one pass by the tool used in the source investigation, although later LOOM output covered the extracted full term set;
- the source baseline reports direct inspection of artefacts that are not all present in the current conversation;
- mapping outputs remain candidates until formal human review;
- illustrative product values are not claims about real commercial products;
- the Manchester Syntax listing was hand-checked but not formally parsed in the reported session;
- no production security, performance or resolver deployment was demonstrated.

### 1.5 Current-versus-historical conclusions

The following historical conclusions were superseded and are not used as current architecture positions:

| Historical statement | Current consolidated position |
|---|---|
| The GDSN-to-Web Vocabulary transition is often a local-name namespace substitution. | Real generated GDSN CURIEs are opaque. Labels and annotations may generate candidates, but mappings require SSSOM curation and structural review. |
| Allergen mapping is a direct equivalence from a coded chain to `gs1:allergenStatement`. | `gs1:allergenStatement` is a language-tagged string. The structured chain is a Route 2 transform; a separate flat GDSN statement attribute is the plausible direct candidate. |
| All six Cheese facets require generic Route 3 publication. | `gpc:20002867` has a corroborated candidate relationship to `gs1:sharpnessOfCheese`; value-level review is still required. |
| The bridge ontology contains OWL axioms, SWRL and CONSTRUCT. | The bridge **package** contains an OWL module, an imported DL-safe rule module and separate SPARQL projection/export artefacts. |
| Mapping candidate generation follows the validated Product Holon in the runtime chain. | Candidate generation and SSSOM curation are design-time control-plane processes over semantic models. |
| The Product Holon and its SHACL shape are the same document described two ways. | The Product Holon is instance data; the SHACL shape is a separate validation contract. |
| SWRL is a second infrastructure layer separate from OWL. | SWRL rules may be serialised in an imported ontology module and evaluated in the same reasoning session, subject to DL-safety and tool support. |

---

## 2. Motivating use case and terminology evidence

### 2.1 K10X context

The initial investigation concerned a K10X explainer titled “Layer 1 — AI Data Interpretation”. The source baseline described K10X as a product-data and connected-packaging company founded by Aziz Shariff, with Alfonso Bravi identified as CTO and Karim Waljee as COO/AI Lead. It identified K10X as a GS1 Australia Associate Alliance Partner and described the proposition as auditing, enriching and structuring data from PIM, ERP, supplier feeds and spreadsheets for machine-readable shopping experiences.

The video itself was not transcribed in the source investigation because the available retrieval environment could not render and play the JavaScript-based YouTube page. The K10X interpretation was therefore reconstructed from the title, channel metadata, the company’s published product pages and public GS1 material. Statements about the precise narration or diagrams remain unverified.

The motivating logic was:

- product data originates in multiple internal and supplier sources;
- machine interpretation requires standardised, structured product facts;
- GS1 Web Vocabulary and schema.org provide an appropriate public representation layer;
- GS1 Digital Link and 2D barcodes provide a route from an identifier to digital resources;
- trusted personalisation depends on accurate underlying product facts, especially for allergens, claims and regulated information.

The source did not establish that K10X uses the exact Product Holon design defined here. The case is therefore treated as a motivating example, not proof of architecture adoption.

### 2.2 Web Vocabulary role

The source investigation positioned GS1 Web Vocabulary as a public, schema.org-aligned vocabulary whose terms are informed by existing GS1 standards. Its role is to expose supported product information in forms that web pages, search engines, product feeds and AI agents can interpret.

The architecture does not treat Web Vocabulary as a complete internal product model. Its bounded scope is a strength for public publication and a limitation for Brick-specific or deep GDSN semantics. The source baseline also noted public GS1 programme material describing GDSN modernisation and semantic modelling using Web Vocabulary, schema.org and JSON-LD. That contextual material supports convergence between source semantics and web publication rather than a competing ontology strategy, but it does not by itself define the Product Holon architecture.

The resulting pattern is:

> construct and validate the Product Holon in source-derived GDSN/GPC semantics; publish an approved view in Web Vocabulary/schema.org semantics.

### 2.3 Evidence concerning the term “Product Holon”

The source baseline reviewed a set of citations offered in support of a “GS1 Product Holon” framework. It found that:

- only one cited source used “holon”, and it did so in a generic enterprise/supply-chain context rather than a GS1 standards context;
- other sources supported genuine GS1 capabilities such as GTIN, SSCC, GLN, EPCIS aggregation and context-based Digital Link resolution;
- the citations did not establish decentralised autonomous product nodes or a GS1-defined holon concept;
- the proposed Product Holon was therefore an external architectural analogy applied to GS1 assets.

The evidence supports use of the term only with an explicit proposal notice. It does not support presenting it as established GS1 terminology.

### 2.4 Standards-backed and proposed elements

| Element | Evidence status |
|---|---|
| GTIN, GLN, SSCC and other GS1 identifiers | GS1 standard capability. |
| GDSN product-data exchange | GS1 standard/service capability. |
| GPC classification | GS1 standard capability. |
| Web Vocabulary | Published GS1 vocabulary. |
| Digital Link resolver mechanisms | GS1 standard capability. |
| EPCIS aggregation relationships | GS1 standard capability. |
| Product Holon | Proposed architecture. |
| Autonomous decentralised product node | Not established by the supplied GS1 sources. |
| One resolver serving public and authenticated Product Holon lenses | Proposed use of existing resolver and HTTP primitives. |

---
