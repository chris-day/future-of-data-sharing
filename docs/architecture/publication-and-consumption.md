---
icon: lucide/send
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Publication and Consumption
## 8. Phase 4 — Publish, resolve and consume

### 8.1 Objective

Phase 4 produces and serves the representation appropriate to a recipient, purpose and access policy. It culminates in an inspectable HTML Semantic Proof and, for verified-publication conformance, a Verifiable Product Statement. It does not create a second independent source of product truth.

### 8.2 End deliverable — GS1 Product Holon Verifiable Publication Profile

The proposed end deliverable is the **GS1 Product Holon Verifiable Publication Profile — HTML Semantic Proof**:

> A human-readable HTML product page containing or linking an exact GTIN-anchored Product Holon, a schema.org/GS1 Web Vocabulary discovery projection, explicit source-authority and provenance metadata, versioned SHACL conformance evidence, governed mapping metadata and a W3C Verifiable Credential that cryptographically binds an authorised issuer to the structured product statements or to integrity-protected resources containing them.

The profile shall be independently testable. A browser, marketplace, application or AI agent should be able to locate the product scripts, retrieve the canonical resources, verify their integrity and status, identify the source authority and explain which evidence supports reliance on each statement.

### 8.3 Profile composition

| Subprofile | Purpose |
|---|---|
| **Native Product Holon Profile** | Canonical, bounded product graph expressed in GDSN- and GPC-aligned semantics. |
| **Web Discovery Projection Profile** | schema.org and GS1 Web Vocabulary representation for web crawlers, marketplaces and general-purpose agents. |
| **Source Authority and Provenance Profile** | Identifies who asserted a statement, their authority role, the source record, context, effective time and transformation lineage. |
| **Conformance Evidence Profile** | References SHACL shapes, validation report, mapping-set version, bridge release and build evidence. |
| **GS1 Product Statement Credential Profile** | W3C Verifiable Credential binding an authorised issuer to selected product statements or to digests of the resources that carry them. |

The five subprofiles form one release package but remain separate artefacts so that each can be versioned, verified and withdrawn independently.

### 8.4 Canonical native Holon and public discovery projection

The architecture does not choose between GDSN/GPC and Web Vocabulary/schema.org. It assigns them different roles:

```text
Authoritative GDSN/GPC Product Holon
                ↓
       governed semantic bridge
                ↓
schema.org / GS1 Web Vocabulary projection
```

The native Product Holon preserves the semantic depth required for validation and audit. The public discovery projection uses the terms and structures most likely to be recognised by web tooling and AI agents. Both shall identify the same GTIN, Product Holon release, source authority, validation report and mapping release.

The HTML profile may embed both representations in separate, uniquely identified `application/ld+json` script elements. Where the native representation is restricted or too large for the page, the profile shall link to it as an alternate representation and embed the public projection.

### 8.5 Publication lenses

| Lens | Typical recipient | Semantic form | Content direction |
|---|---|---|---|
| Manufacturer/internal | Product-data and governance systems | Native Product Holon, source-derived GDSN/GPC terms | Broad product truth, provenance and validation evidence. |
| Trading partner | GDSN/data-pool participant | GDSN-native or recipient-specific B2B representation | May be broader and recipient-specific. |
| Marketplace/feed | Feed-ingesting platform | Web Vocabulary/schema.org or platform profile | Narrower product facts; excludes internal B2B content. |
| Consumer/application | Browser, app or connected-pack experience | HTML Semantic Proof plus public JSON-LD | Public, comprehensible and policy-approved facts. |
| AI agent | Agent or retrieval service | Bounded JSON-LD/RDF, credential, validation and provenance references | Grounded facts suitable for deterministic verification, retrieval and explanation. |

The lenses are representations derived from the Product Holon. They are not separate holons unless they acquire their own identity, authority and lifecycle as independent data products.

### 8.6 Product and Offer separation

The Product Holon contains manufacturer- or authorised-source product truth. Price, currency, seller, availability, delivery terms and marketplace reviews belong to seller- or marketplace-owned objects such as `schema:Offer`, `schema:AggregateOffer` and rating structures.

A marketplace presenting one GTIN from several sellers should reuse one governed product representation and attach multiple offers. It should not create several divergent copies of the manufacturer’s product facts without provenance. A product-statement credential shall not sign seller-owned facts unless the named issuer is also the authority for those facts and the credential scope states that role explicitly.

### 8.7 HTML Semantic Proof

The HTML Semantic Proof shall provide:

- a canonical product URI based on the exact GS1 identifier and applicable qualifiers;
- a declared profile URI and profile version;
- one or more uniquely identified JSON-LD script elements;
- the public schema.org/GS1 Web Vocabulary projection;
- the native GDSN/GPC Product Holon, embedded or linked according to policy;
- source-authority and provenance references;
- validation, mapping and release references;
- a canonical Verifiable Product Statement served using the `application/vc` media type;
- human-readable status and evidence information that does not overstate verification as factual truth;
- links to superseding, withdrawn or historical releases where applicable.

JSON-LD 1.1 permits an individual script element to be addressed by a fragment identifier matching its `id`. The profile shall use stable script identifiers so that the credential can integrity-bind the exact script block or a canonical external representation. The canonical credential should be served as `application/vc`; an embedded copy may be provided for inspection only when byte-for-byte or dataset-level equivalence and lifecycle synchronisation are assured.

### 8.8 Source authority and grounding

At minimum, the source-authority profile shall identify:

| Element | Required meaning |
|---|---|
| Product subject | Exact GTIN and canonical GS1 Digital Link URI, with qualifiers where applicable. |
| Issuer identity | A resolvable organisation identifier and verification method. |
| GS1 organisation identity | GLN and, where relevant, the relationship to the applicable GS1 Company Prefix or registry record. |
| Authority role | Brand owner, information provider, certification body, laboratory, regulator, seller or other scoped role. |
| Authority scope | Product, claim type, target market, language, batch/lot, serial and effective period for which the issuer is entitled to assert. |
| Source record | PIM release, GDSN notification, certification record, laboratory result, regulatory record or another named source. |
| Source context | Data pool, recipient, target market, language, creation time, effective time and document status where present. |
| Semantic release | GDSN, GPC, Web Vocabulary and profile versions. |
| Mapping release | Reviewed SSSOM mapping set and bridge package. |
| Validation evidence | SHACL shape, validation report, validation time and tool version. |
| Publication release | Product Holon version, generated time, expiry and supersession status. |

Where statements have different authorities, the profile shall retain separate assertion sets or credentials rather than relying on a blanket page-level authority declaration.

### 8.9 Web Vocabulary and schema.org projection

The publication service applies the four routes defined in Phase 3:

- direct approved terms are emitted under their target identifiers;
- structured transformations create target shapes such as `schema:NutritionInformation`;
- residual publishable facets use `schema:PropertyValue`;
- excluded facts remain in authorised internal or B2B views.

A Product Holon remains the governed source representation even where its public projection uses `schema:Product` or `gs1:Product`. The projection shall link to the native Product Holon and identify the mapping release that produced it.

### 8.10 Verifiable Product Statement credential

The credential profile shall be based on stable W3C Recommendations unless a later specification is formally approved for the implementation. The initial baseline is:

- Verifiable Credentials Data Model v2.0;
- Verifiable Credential Data Integrity 1.0 or an approved JOSE/COSE securing method;
- an approved W3C cryptosuite such as the ECDSA Data Integrity Cryptosuites v1.0;
- Controlled Identifiers v1.0 for verification material where applicable;
- Bitstring Status List v1.0 or another approved credential-status method.

The credential shall include or define:

- `id`, `type`, `issuer`, `validFrom` and, where appropriate, `validUntil`;
- a `credentialSubject` that identifies the exact Product Holon or assertion set;
- a `credentialSchema` for the credential envelope and profile constraints;
- `evidence` references supporting the issuer’s reliance decision;
- `relatedResource` digests for the native Holon, web projection, contexts, SHACL profile, validation report and mapping release where those external resources are relied upon;
- `credentialStatus` for revocation, suspension or other lifecycle state;
- a securing mechanism identifying proof type, cryptosuite, verification method and proof purpose.

The credential may contain selected product assertions directly. For larger Product Holons, integrity-binding external resources through `relatedResource` is the preferred pattern because the credential can remain compact while a verifier can detect any change to the secured resources.

### 8.11 Verification and truth boundary

The profile shall use the term **Verifiable Product Statement**, not “cryptographic proof of product truth”. A successful credential verification can establish that:

- the securing mechanism is valid for the supplied verification method;
- the credential is an authentic statement of the issuer;
- the secured content or related resources have not been altered;
- the credential is within its validity period;
- its current status has not invalidated it, where status is supplied.

It does not, by itself, establish that every claim is factually true or that the issuer is entitled to assert it. The relying party must also evaluate issuer authority, source provenance, evidence, market and time context, semantic conformance and its own risk policy.

```text
Issuer identity
+ authority to make the assertion
+ source provenance and evidence
+ semantic and structural conformance
+ cryptographic integrity and authorship
+ credential status
+ market, qualifier and effective-time applicability
= evidence-backed reliance decision
```

### 8.12 GS1 Digital Link resolution

GS1 Digital Link and the GS1-Conformant Resolver mechanisms provide the standards-backed basis for linking a GS1 identifier to representations and services. Relevant mechanisms include:

- media-type negotiation, including JSON-LD requests;
- `linkType` selection for different linked resources;
- language and contextual selection;
- batch/lot and serial qualifiers where present;
- linkset responses and redirection to destination resources.

The resolver should make the HTML Semantic Proof, canonical Product Holon, public projection, validation evidence and Verifiable Product Statement discoverable as distinct linked resources. Product Holon-specific link types, a credential link type or authenticated B2B audience conventions remain proposed implementation choices requiring governance.

### 8.13 Content negotiation and access policy

Content negotiation selects representation; it does not establish authorisation. Non-public views shall require an access-control mechanism appropriate to the deployment. The publication service shall combine:

- requested media type and profile;
- link type;
- language and target market;
- authenticated role or recipient where needed;
- product qualifier and effective time;
- publication allow-list and data classification;
- credential disclosure and privacy policy.

### 8.14 API and feed publication

The architecture supports:

- static or cached JSON-LD documents;
- dynamic Product Holon APIs;
- product-catalogue feeds;
- GDSN-native exchange;
- resolver-linked resources;
- HTML Semantic Proof pages;
- Verifiable Product Statement retrieval and verification endpoints;
- graph query or retrieval services.

Every interface shall expose or make discoverable the product identifier, representation version, effective time, source authority, credential status and provenance sufficient for consumers to detect staleness, supersession and withdrawal.

### 8.15 AI-agent consumption and verification sequence

The preferred AI interaction pattern is neuro-symbolic and verification-aware:

1. resolve the exact GTIN and relevant qualifiers;
2. retrieve the HTML Semantic Proof or declared machine profile;
3. locate the required JSON-LD script by its identifier or retrieve the canonical Product Holon;
4. retrieve the Verifiable Product Statement;
5. verify the credential securing mechanism;
6. verify each relied-upon `relatedResource` digest;
7. resolve the issuer and verify control of the stated verification method;
8. establish that the issuer is authorised for the product, assertion type, market and effective period;
9. check credential status and validity period;
10. validate the Product Holon against the declared SHACL profile and release;
11. check target market, language, batch/lot, serial and effective-time applicability;
12. invoke deterministic OWL, rule or query services for approved derivations;
13. apply the relying party’s claim-specific trust policy;
14. use the LLM only to explain, compare or narrate the verified results, with provenance.

An agent shall abstain, ask for clarification or reduce confidence when identity, authority, integrity, status, applicability or conformance cannot be established.

### 8.16 Graph-based retrieval

A Product Holon is naturally suited to graph-based retrieval because it is constructed by traversing the product identifier, Brick, ancestor chain, applicable attributes and explicit relationships. The bounded graph avoids retrieving the entire source ontology and supports exact controlled-value lookup rather than relying only on embedding similarity.

This architecture uses “Graph-RAG” descriptively for graph-grounded retrieval. It does not require that the underlying authoritative graph be generated from unstructured text by an LLM.

### 8.17 Publication evidence

A publication event should record:

- Product Holon identifier and version;
- publication profile and audience;
- native and web representation identifiers and digests;
- source-authority assertion set;
- bridge-package and mapping-set versions;
- validation report identifier;
- credential identifier, issuer, proof method, status reference and validity period;
- generation time and effective time;
- media type and language;
- access policy;
- destination or resolver link;
- supersession, withdrawal or revocation relationship.

### 8.18 Proposed FoDS workstream hand-off

Subject to formal FoDS governance, the deliverable provides the following hand-off:

| Workstream | Proposed responsibility |
|---|---|
| **8.3.a — Machine-readable standards and models** | Supply governed, versioned source semantic and validation artefacts used by the Product Holon. |
| **8.3.b — Semantic and AI-ready publication** | Define and implement the canonical Product Holon, web projection, provenance, SHACL evidence, mapping release and publication package. |
| **8.4.a — Semantic profile for discovery and proof** | Own the HTML Semantic Proof and GS1 Product Statement Credential profiles, script discovery rules, verification contract and conformance tests. |
| **8.4.b — AI interfaces** | Discover, retrieve, verify, ground and use the proof package through agent-ready interfaces, with evidence-aware abstention and explanation. |

The 8.4.a allocation is a proposed architecture boundary supplied for this revision; it requires confirmation against the authoritative 8.4.a project plan.

### 8.19 Phase outputs

Phase 4 produces authorised native and web representations, an HTML Semantic Proof, a Verifiable Product Statement and status record, APIs, feeds and resolver links, together with source-authority, validation, credential and publication evidence.

---
