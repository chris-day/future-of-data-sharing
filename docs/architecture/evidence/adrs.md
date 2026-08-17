---
icon: lucide/landmark
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Architecture Decision Records
## Part VI — Architecture Decision Records

## 15. ADR-001 — Use “Product Holon” only as a proposed working term

**Status:** Accepted for working-draft use; formal GS1 adoption unresolved.

**Context:** The term usefully describes a bounded product unit that is both independently coherent and part of larger semantic and product graphs. The reviewed citations did not establish it as existing GS1 terminology.

**Decision:** Retain “Product Holon” with an explicit proposal notice. Do not describe it as an approved GS1 concept.

**Consequences:** Stakeholder communication must separate the architectural analogy from standards-backed capabilities. A future governance decision may approve, rename or reject the term without invalidating the underlying bounded-graph design.

---

## 16. ADR-002 — Maintain GDSN and GPC as separate semantic modules

**Status:** Accepted.

**Context:** GDSN and GPC have different source structures and purposes. The JSON-to-TSV pipeline independently generated separate modules, consistent with the semantic analysis.

**Decision:** Generate, version and publish GDSN and GPC modules separately. Express relationships through mappings, imports or references rather than folding GPC into the GDSN class table.

**Consequences:** Release management is clearer and source provenance is preserved. Cross-module reasoning requires explicit relationships.

---

## 17. ADR-003 — Use a bounded product-instance graph as the architecture unit

**Status:** Accepted.

**Context:** The full source models are too large and contain many facts irrelevant to one product or audience.

**Decision:** Construct one bounded Product Holon per identity and relevant context, containing only applicable populated facts, relationships, provenance and validation evidence.

**Consequences:** AI and publication payloads remain right-sized. Implementations require reliable GTIN-to-Brick and source-record resolution.

---

## 18. ADR-004 — Separate the semantic control plane from the product data plane

**Status:** Accepted; corrects the source baseline’s final linear diagram.

**Context:** Ontology generation, candidate mapping and SSSOM review are reusable design-time activities. Product construction, validation and projection run per product.

**Decision:** Place model transformation, mapping curation, bridge compilation and regression testing in the semantic control plane. Place Product Holon construction, validation, projection and publication in the product data plane.

**Consequences:** LOOM and SSSOM do not run per Product Holon. Released control-plane artefacts can be applied consistently to large catalogues.

---

## 19. ADR-005 — Keep Product Holon instances and SHACL shapes separate

**Status:** Accepted; supersedes an earlier statement that described them as the same document in two forms.

**Context:** Instance data and validation contracts have different identity, provenance and release cycles.

**Decision:** Treat the Product Holon as ABox/product-instance data and SHACL shapes as separately versioned contracts.

**Consequences:** Validation evidence becomes reproducible and shape releases can evolve independently of product releases.

---

## 20. ADR-006 — Use SSSOM as the mapping source of truth

**Status:** Accepted.

**Context:** Real generated GDSN identifiers are opaque. Lexical matching is useful for discovery but unsafe as an unreviewed crosswalk.

**Decision:** Import automated candidates into a versioned SSSOM mapping set with provenance, justification, confidence, cardinality and review status. Compile reasoner-active artefacts only from approved records.

**Consequences:** Mapping governance becomes auditable. A build tool is required to compile approved records into OWL, rule and query artefacts.

---

## 21. ADR-007 — Compile direct OWL equivalence only for compatible meaning and graph shape

**Status:** Accepted.

**Context:** An OWL equivalence axiom does not perform record-to-literal conversion, conditional routing or node construction.

**Decision:** Require semantic, datatype, cardinality and graph-shape review before compiling direct equivalence. Use property chains only where they compose object-property paths to a compatible target.

**Consequences:** Some plausible label matches remain Route 2 or Route 3. The bridge avoids unsound entailments.

---

## 22. ADR-008 — Use a hybrid OWL/DL-safe-rule ontology with separate SPARQL export

**Status:** Accepted.

**Context:** Conditional mappings exceed pure OWL DL. SWRL-style Horn rules can express them, while publication consumers require plain target graphs rather than a live reasoner.

**Decision:** Keep stable classes and direct axioms in the core bridge ontology. Place volatile, approved DL-safe rules in an independently versioned imported module. Keep SPARQL outside the ontology for export/projection and for any explicitly governed transform not implemented in the reasoner.

**Consequences:** One reasoning session can evaluate ontology and DL-safe rules. Export remains portable and testable. Release manifests must link all modules.

---

## 23. ADR-009 — Use `schema:PropertyValue` as the generic publication fallback

**Status:** Accepted.

**Context:** Web Vocabulary and schema.org do not provide first-class properties for most tested GPC Brick facets.

**Decision:** Publish approved residual facts through `schema:additionalProperty` and `schema:PropertyValue`, preserving the source property identifier, label and value.

**Consequences:** Facts are not lost, but downstream systems may interpret them less strongly than named properties. Route 3 is not a substitute for future first-class mappings where those are justified.

---

## 24. ADR-010 — Separate product truth from Offer and marketplace facts

**Status:** Accepted.

**Context:** Price, availability, seller identity and reviews have different owners and change cycles from manufacturer product facts.

**Decision:** Keep Product Holon facts separate from `Offer`, `AggregateOffer`, rating and marketplace merchandising data.

**Consequences:** One product representation can be reused across sellers. Provenance and freshness remain accurate.

---

## 25. ADR-011 — Restrict LLMs to retrieval, interpretation and narration

**Status:** Accepted.

**Context:** The reviewed structured-decomposition paper reported lower performance when the LLM executed the final rule application rather than a deterministic reasoner. The architecture also requires reproducible validation and mapping behaviour.

**Decision:** Use deterministic SHACL, OWL, rule and SPARQL engines at the trust boundary. Use LLMs to identify entities, retrieve bounded graphs, explain results and generate natural-language output.

**Consequences:** Tool interfaces and evidence traces become essential. The LLM cannot override validation or silently create a mapping.

---

## 26. ADR-012 — Replace the fixed selected GDSN shape with modular profiles

**Status:** Proposed for the next reference implementation release.

**Context:** The current selected eight-property GDSN shape is identical across four unrelated Bricks. It exposes inapplicable food fields for Smartphones and omits several cheese-relevant attributes.

**Decision:** Retain a small cross-category core and add category-, use-case- or publication-specific GDSN shape modules selected by profile.

**Consequences:** Shape generation becomes more expressive and requires profile governance. Validation becomes more relevant and less noisy.

---
