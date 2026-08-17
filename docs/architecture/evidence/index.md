---
icon: lucide/microscope
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Technical Evidence Overview
Companion evidence pack for the Product Holon Architecture. These pages retain observations, validation evidence, examples, ADRs, open issues, and references.

## Technical Evidence and Reference Implementation

**Version:** 1.3.0  
**Date:** 17 August 2026  
**Status:** Working Draft — companion to `GS1_Product_Holon_Architecture_v2.1.0.md`  
**Authority notice:** The Product Holon is a proposed architectural construct. The evidence pack distinguishes approved GS1 capabilities, source-derived semantic artefacts, reference implementations, candidate mappings and proposed design choices.

---

## Document control

### Purpose

This document preserves the technical evidence, implementation detail and decision history underlying the core GS1 Product Holon Architecture. It replaces the chronological research-dossier structure of `gs1-gdsn-holon-v1.31.0.md` with an evidence-oriented structure. Superseded conclusions are not repeated as current recommendations; they are retained through Architecture Decision Records and explicit correction notes.

### Relationship to the core architecture

The core architecture defines the proposed model, phases, components, governance and adoption roadmap. This companion provides:

- the source inventory and verification boundaries;
- direct observations from the supplied GDSN, GPC, SHACL and mapping artefacts;
- the K10X use case that motivated the initial investigation;
- worked Product Holons and SHACL examples;
- the ontology and shape-generation pipeline;
- mapping-candidate generation and SSSOM curation evidence;
- OWL, DL-safe SWRL and SPARQL design exhibits;
- validation and reconciliation results;
- Architecture Decision Records;
- limitations, unresolved questions and references;
- the HTML Semantic Proof and Verifiable Product Statement reference profile, including a source-authority example, HTML scripts, credential structure and acceptance tests.

### Evidence labels

| Label | Meaning in this pack |
|---|---|
| **Observed** | Directly present in or computed from a supplied artefact. |
| **Demonstrated** | Executed or validated in the source investigation or reference implementation. |
| **Corroborated candidate** | Supported by more than one source or method but still awaiting formal governance review. |
| **Proposed** | An architectural or implementation choice not established as an existing GS1 requirement. |
| **Superseded** | A historical conclusion replaced by later evidence. |
| **Unresolved** | The available sources do not establish the answer. |

### Editorial policy

The evidence pack uses an institutional technical voice. First-person session language, conversational corrections and version annotations in headings have been removed. The evidence itself remains traceable to the source document and named files.

---

## Evidence Guide

- [Evidence Basis](evidence-basis.md)
- [Semantic Source Evidence](semantic-source-evidence.md)
- [Ontology and SHACL Pipeline](ontology-and-shacl-pipeline.md)
- [SHACL Generation and Validation](shacl-validation.md)
- [Worked Product Holons](worked-product-holons.md)
- [Semantic Bridge Evidence](semantic-bridge.md)
- [Bridge Technical Exhibits](bridge-technical-exhibits.md)
- [Mapping Experiment Evidence](mapping-experiment-evidence.md)
- [Architecture Decision Records](adrs.md)
- [AI, Retrieval, and Publication Evidence](ai-retrieval-and-publication.md)
- [Verifiable Publication Evidence](verifiable-publication-evidence.md)
- [Evidence Matrix and Open Issues](evidence-matrix-and-open-issues.md)
- [Migration and Traceability](migration-and-traceability.md)
- [References](references.md)

---

## Executive evidence summary

The source investigation began as an analysis of a K10X “Layer 1 — AI Data Interpretation” explainer and the role of GS1 Web Vocabulary in AI-enabled shopping. Direct inspection of supplied GDSN and GPC semantic artefacts broadened the work into a product-centred architecture. The evidence showed that:

- GPC provides category scope through Bricks, Attribute Types and controlled Attribute Values;
- GDSN provides deep product semantics, structured records, code lists and recipient-oriented business data;
- Web Vocabulary and schema.org provide the public and agent-facing publication layer for a bounded subset;
- a product-specific graph can be constructed by resolving a GTIN to a Brick and selecting only populated, applicable facts;
- Brick-scoped SHACL shapes can be generated mechanically and validated with deterministic tooling;
- the current `gs1-gdsn-holon` implementation independently converged on the same Brick-scoped generation and validation pattern;
- real generated GDSN CURIEs are opaque, so name matching cannot be implemented as a simple namespace substitution;
- lexical tools can generate useful candidate mappings but cannot approve them;
- SSSOM provides an appropriate source of truth for candidate, reviewed and rejected mappings;
- direct OWL equivalence is only sound for semantically and structurally compatible terms;
- conditional or structural mappings require DL-safe rules or versioned transforms;
- SPARQL remains an export/projection mechanism outside the ontology;
- Product and Offer data require separate authority and provenance;
- an LLM should retrieve and narrate validated facts rather than execute final rule logic.

The completed LOOM/BioPortal run produced 28,101 unique terms, 237 unique cross-ontology candidate pairs and 474 directional `skos:closeMatch` records. GDSN-to-Web Vocabulary candidates dominated, while GPC-to-Web Vocabulary candidates were sparse. Reconciliation with specific terms produced useful corroboration and several corrections, including the distinction between a flat GDSN allergen-statement attribute and the separate structured allergen-code chain.

This revision adds the publication proof required to make the architecture independently consumable. The proposed HTML Semantic Proof exposes a canonical GDSN/GPC-aligned Product Holon and a schema.org/GS1 Web Vocabulary discovery projection, connects them to source authority and SHACL evidence, and links a W3C Verifiable Product Statement that binds an authorised issuer to selected statements or integrity-protected resources. The credential is treated as proof of authorship, integrity and current status, not as automatic proof of factual truth.

---
