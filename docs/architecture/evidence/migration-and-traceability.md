---
icon: lucide/route
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Migration and Traceability
## Part X — Migration and traceability

## 34. Source-section migration map

| Source baseline material | Location in this pack or core architecture |
|---|---|
| K10X video and Web Vocabulary context | Sections 2.1–2.2 of this pack. |
| GDSN versus Web Vocabulary analysis | Core Sections 1–3; Pack Sections 2–3. |
| Initial Product Holon and Gouda example | Core Section 3 and 6; Pack Section 7. |
| Citation fact-check | Pack Section 2.3. |
| SHACL design, corrections and generator | Pack Sections 5–6. |
| Variety packs and Digital Link | Core Sections 6 and 8; Pack Sections 7.10 and 29. |
| Publication route model | Core Section 7; Pack Section 8. |
| OWL, SWRL and CONSTRUCT reasoning | Core Section 7; Pack Sections 10 and ADR-007/008. |
| Neuro-symbolic and Graph-RAG discussion | Core Section 8; Pack Sections 27–28. |
| Navigator-to-OWL pipeline | Core Section 5; Pack Section 4. |
| Real generated shapes | Core Section 6; Pack Sections 6–7. |
| Opaque CURIE correction | Core Section 7; Pack Sections 1.5, 9 and ADR-006. |
| SSSOM adoption | Core Sections 7 and 9; Pack Section 9 and ADR-006. |
| LOOM aggregate and detailed reconciliation | Pack Sections 12–14. |
| Four-phase diagram | Replaced by the two-plane model in Core Executive Summary and Section 4. |
| Phase 4 proof, authority and credential concept | Pack Section 30 and Core Section 8. |
| Source appendices A–E | Consolidated into Pack Sections 7, 11–14 and the evidence matrix. |
| Source list | Pack Section 36. |

---

## 35. Version history

| Version | Date | Change |
|---|---|---|
| 1.3.0 | 2026-08-17 | Adds Part VIII, defining the HTML Semantic Proof and Verifiable Product Statement reference profile. Incorporates the supplied Vision 2030 narratives, Phase 4 presentation, `CatalogueItemNotification_ADD.xml`, current GDSN/GPC ontology copies and the corresponding RDF instance graph; adds a concrete source-authority evidence chain, structurally aligned native and web JSON-LD script examples, a VC Data Model v2.0 credential example with `relatedResource`, evidence and status, standards-status guidance, verification algorithm, truth boundary, acceptance-test catalogue, proposed 8.3.b → 8.4.a → 8.4.b hand-off, implementation work items, evidence-matrix entries and unresolved governance questions. Aligns the companion with Core Architecture v2.1.0. |
| 1.2.0 | 2026-08-04 | Adds the Whole Milk hierarchy example using valid GTIN-14 `05000169015254`. Preserves the hierarchy supplied with the request as provenance, but normalises the implemented GPC chain to Segment `50000000`, Family `50130000`, Class `50131700` and Brick `10000025`; records that supplied code `10000236` is not a milk Brick. Retains Fat content = `Whole` and Packaging type = `Plastic bottle` as generic, user-supplied facts because their GPC Attribute identifiers were not supplied or verified. |
| 1.1.0 | 2026-08-04 | Replaces the illustrative Beer identifier with supplied GTIN-14 `00083783000085`. Adds a Compote classification example using supplied GTIN-13 `5000119096753` and canonical GTIN-14 `05000119096753`; normalises supplied code `30000728` from a claimed Brick to the GPC Attribute Value `COMPOTE` within Brick `10000217` (Jams/Marmalades (Shelf Stable)). Corrects the pre-existing illustrative Sugar GTIN check digit from `04005500023344` to valid GTIN-14 `04005500023340`. |
| 1.0.1 | 2026-08-04 | Replaces the illustrative Smartphone identifier with supplied GTIN-13 `0195950643718`; uses canonical zero-padded GTIN-14 `00195950643718` in the Digital Link AI (01) URI and GDSN value. |
| 1.0.0 | 2026-08-02 | First technical evidence companion. Reorganises the evidence from `gs1-gdsn-holon-v1.31.0.md`; removes research-diary tone; consolidates superseded conclusions; adds formal Architecture Decision Records; separates observed, demonstrated, candidate and proposed material; aligns with `GS1_Product_Holon_Architecture_v2.0.0.md`. |
