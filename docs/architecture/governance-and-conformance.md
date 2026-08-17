---
icon: lucide/shield-check
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Governance and Conformance
## 9. Cross-cutting governance and conformance

### 9.1 Governance domains

The architecture requires coordinated governance across six domains:

1. source-model governance;
2. semantic artefact generation;
3. mapping governance;
4. product-data governance;
5. publication and resolver governance;
6. issuer authority, credential, key and status governance.

A change in one domain may trigger rebuild and regression in the others.

### 9.2 Source authority

Source authority shall be explicit. A generated ontology is authoritative only as a faithful, traceable representation of its source release; it does not supersede the approved source standard. A Product Holon assertion is authoritative only to the extent that its publisher is entitled to state the fact. A valid signature proves control of a verification method, not authority for a GTIN or claim; the issuer-to-product and issuer-to-claim relationship shall therefore be established through GS1 identity, registry, delegation or other governed evidence.

### 9.3 Mapping governance lifecycle

The proposed lifecycle is:

`discovered → candidate → under review → approved/rejected → compiled → released → superseded/deprecated`.

Rejected mappings remain in the registry with rationale so that automated tools do not repeatedly reintroduce them without evidence.

### 9.4 Change management

A release-impact assessment shall be triggered by:

- source model additions, removals or identifier changes;
- label or definition changes;
- datatype, domain, range or cardinality changes;
- code-list changes;
- target vocabulary deprecation;
- mapping approval or rejection;
- change to a publication allow-list;
- rule or query modification;
- resolver-profile or access-policy change.

### 9.5 Security and access control

The architecture separates public, partner, restricted and internal facts. Implementations shall define:

- authentication and authorisation mechanisms;
- recipient and purpose controls;
- protection of commercially sensitive data;
- audit logging;
- rate limiting and abuse controls;
- integrity protection for released artefacts;
- signing-key generation, storage, rotation, recovery and compromise response;
- credential status, revocation, suspension and expiry;
- remote JSON-LD context and related-resource integrity controls;
- incident and withdrawal procedures.

No security mechanism was demonstrated in the source evidence; these controls are required for production architecture completion.

### 9.6 Privacy

Most product master data is not personal data, but provenance, user context, personalisation, reviews, account identifiers and scan analytics may introduce privacy obligations. Product Holon identity shall not be conflated with user identity. Resolver and agent implementations shall minimise and govern personal-context processing.

### 9.7 Proposed conformance levels

| Level | Name | Minimum evidence |
|---|---|---|
| PH-C1 | Semantic foundation | Versioned GDSN/GPC artefacts, diagnostics, parse tests and source provenance. |
| PH-C2 | Product construction | Identifier, classification, bounded assertions, provenance and release metadata. |
| PH-C3 | Validation | Applicable SHACL profiles and a successful validation report. |
| PH-C4 | Governed alignment | Released SSSOM mapping set, approved bridge package and regression tests. |
| PH-C5 | Publication | Authorised view, product/offer separation, publication provenance and media/profile metadata. |
| PH-C6 | Resolution and agent use | Resolver/API behaviour, access policy, current-version discovery and deterministic reasoning boundary. |
| PH-C7 | Verifiable publication proof | HTML Semantic Proof, canonical and discovery representations, source-authority evidence, successful credential and resource-digest verification, issuer-authority check, current credential status and a retained verification report. |

An implementation may conform to an earlier level without implementing every later publication capability. A future formal conformance specification would need testable normative criteria for each level.

### 9.8 Conformance evidence retention

Evidence should be retained for the lifetime of a released representation and an agreed period after supersession. At minimum, this includes source checksums, build manifests, shape versions, validation reports, mapping approvals, compiled artefact checksums, related-resource digests, credential issuance and status events, key and verification-method history, verification reports, publication events and withdrawal records.

### 9.9 Licence and intellectual property

The licence for source-derived semantic artefacts, mapping sets, generated shapes and examples shall be established before external publication. Tool licences and source-model usage rights shall be recorded separately from document copyright.

---
