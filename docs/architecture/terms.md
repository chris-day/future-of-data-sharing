---
icon: lucide/list-checks
source: artefacts/GS1_Product_Holon_Architecture_v2.1.0.md
---

# Terms and Conformance Checklist
## Annex A — Terms and definitions

| Term | Definition in this document |
|---|---|
| Product Holon | A bounded, versioned product-instance knowledge graph anchored by a GS1 identifier and linked to wider semantic and product graphs. |
| Product Holon view | An audience- and policy-specific representation derived from a Product Holon. |
| Semantic control plane | Design-time processes and artefacts used to generate, govern, compile and test reusable semantics. |
| Product data plane | Per-product processes that construct, validate, project and publish product-instance data. |
| Semantic bridge package | The released combination of SSSOM mappings, compiled OWL/rules, projection queries, publication policies and tests. |
| Mapping candidate | A possible correspondence awaiting review. |
| Reviewed mapping | A mapping decision approved through the designated governance process. |
| Route 1 | Direct same-meaning, compatible-shape semantic correspondence. |
| Route 2 | Governed structural or conditional transformation. |
| Route 3 | Generic publication through `schema:PropertyValue`. |
| Route 4 | Exclusion from the applicable publication view. |
| Source-derived artefact | A semantic or validation artefact generated from an authoritative source model. |
| Publication profile | A governed selection and transformation policy for a target audience or interface. |
| HTML Semantic Proof | A human-readable product page that embeds or links machine-readable Product Holon views, source-authority metadata, conformance evidence and a canonical Verifiable Product Statement. |
| Verifiable Product Statement | A W3C Verifiable Credential binding an issuer to product statements or to integrity-protected resources containing them. |
| Source authority | The scoped entitlement of an identified organisation to assert a particular product fact for a product, market, qualifier and effective period. |
| Evidence-backed reliance decision | A verifier’s decision based on issuer identity and authority, provenance, evidence, conformance, cryptographic integrity, status and contextual applicability. |

## Annex B — Proposed implementation conformance checklist

An implementation claiming Product Holon Architecture alignment should be able to answer **yes** to the applicable statements:

- [ ] The product representation is anchored by a valid GS1 identifier.
- [ ] The GPC Brick and source release are declared.
- [ ] Product assertions are bounded to the represented item and context.
- [ ] Source and transformation provenance are retained.
- [ ] Ontologies, SHACL shapes, mapping sets and product instances are separate artefacts.
- [ ] Required SHACL validation has completed successfully.
- [ ] Mapping candidates and approved mappings are distinguishable.
- [ ] Approved mappings are stored in a versioned SSSOM set.
- [ ] Direct equivalence has passed meaning, shape and cardinality review.
- [ ] Structural transforms are versioned and tested.
- [ ] Public publication uses an explicit allow-list.
- [ ] Generic fallbacks retain the source property identifier.
- [ ] Manufacturer product facts are separated from marketplace offers and reviews.
- [ ] LLM output is downstream of deterministic retrieval, validation and reasoning.
- [ ] Every published representation identifies its Product Holon, bridge and profile versions.
- [ ] Superseded and withdrawn representations can be detected.
- [ ] The HTML page declares the Semantic Proof profile and stable JSON-LD script identifiers.
- [ ] The canonical native Product Holon and public discovery projection identify the same GTIN and release.
- [ ] Source authority is scoped by issuer role, product, claim, market and effective period.
- [ ] A canonical Verifiable Product Statement is discoverable using `application/vc`.
- [ ] The credential securing mechanism verifies with the declared verification method.
- [ ] Every relied-upon external resource passes its `relatedResource` digest check.
- [ ] Credential validity and current status have been checked.
- [ ] The issuer’s authority for the asserted scope has been verified independently of the signature.
- [ ] The verification result does not describe cryptographic validity alone as proof of factual truth.
- [ ] A retained verification report records signature, digest, status, authority, context and SHACL outcomes.

## Annex C — Version history

| Version | Date | Change |
|---|---|---|
| 2.1.0 | 2026-08-17 | Adds the GS1 Product Holon Verifiable Publication Profile and HTML Semantic Proof as the Phase 4 end deliverable. Defines canonical GDSN/GPC and schema.org/GS1 Web Vocabulary representations, source-authority and provenance requirements, a W3C Verifiable Product Statement credential, related-resource integrity binding, credential status, the verification-and-truth boundary, PH-C7 conformance, reference deployment components, acceptance tests and the proposed 8.3.b → 8.4.a → 8.4.b hand-off. |
| 2.0.0 | 2026-08-02 | Major restructure of `gs1-gdsn-holon-v1.31.0.md` into a core architecture. Introduces the two-plane model; moves K10X, technical code, detailed validation evidence, mapping experiments and research history to a companion technical evidence pack; consolidates superseded conclusions; adopts institutional working-draft tone; separates Product Holon instances, shapes, mapping sets and compiled bridge artefacts. |

## Annex D — Companion artefact

Detailed evidence, code, worked examples, mapping results, Architecture Decision Records and source references are contained in:

`GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md`
