---
title: FAIR Conformance
document_id: GS1_8_3b_Semantic_Publication_Profiles
version: 1.2.0
status: Draft for discussion and validation
date: '2026-07-06'
programme: 'GS1 Vision 2030 — Objective 8: Future of Data Sharing'
workstream: 8.3.b — Semantic and AI-ready publication
related_workstreams:
- 8.3.a — Machine-readable standards and models
- 8.4.b — AI Interfaces
language: en-GB
licence: Internal GS1 working document — confirm publication terms before external
  release
keywords:
- semantic publication
- machine-readable standards
- AI-ready
- agentic interfaces
- GenAI-enabled API
- API semantic publication
- JSON Schema
- MCP generation
- OpenAPI
- Arazzo
- MCP
- A2A
- Markdown
- linked data
- JSON-LD
- RDF
- SHACL
- FAIR Data Principles
- provenance
- GS1 Web Vocabulary
source: artefacts/GS1_8_3b_Semantic_Publication_Profiles_v1.2.0.md
source_sections:
- 8. FAIR conformance overlay
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# FAIR Conformance

*Source version 1.2.0. Draft for discussion and validation.*

## 8. FAIR conformance overlay

### 8.1 Positioning

FAIR means that digital resources are **Findable, Accessible, Interoperable and Reusable** by humans and machines. FAIR does not mean that every resource must be openly accessible, nor does FAIR alone guarantee intrinsic data quality, ethics, security or fitness for a particular decision. A resource may be FAIR while requiring authentication or operating under restrictive usage conditions, provided those conditions are explicit and machine-readable.

FAIR should be embedded as a cross-cutting conformance overlay across the GS1 profile family.

### 8.2 FAIR-to-profile requirements mapping

| FAIR principle | Semantic publication requirement |
| --- | --- |
| F1 | Assign globally unique and persistent identifiers to artefacts, versions and significant components. |
| F2 | Provide rich descriptive, technical, administrative, governance and provenance metadata. |
| F3 | Ensure metadata explicitly identify the artefact or distribution they describe. |
| F4 | Register or index metadata in a searchable catalogue, registry or discovery service. |
| A1 | Make metadata and permitted representations retrievable by identifier using a standard protocol. |
| A1.1 | Prefer open, implementable Web protocols and documented media types. |
| A1.2 | Support authentication and authorisation where needed without obscuring access conditions. |
| A2 | Preserve metadata and tombstone records even when a distribution or version is withdrawn. |
| I1 | Use formal, accessible and broadly applicable knowledge-representation languages, including RDF/JSON-LD, SKOS, OWL and SHACL where appropriate. |
| I2 | Use vocabularies that are themselves identified, documented, versioned and accessible. |
| I3 | Express qualified links to related artefacts, standards, concepts, mappings and provenance. |
| R1 | Provide accurate, relevant and sufficiently rich attributes for reuse beyond the original publication channel. |
| R1.1 | State licence and usage conditions clearly and machine-readably. |
| R1.2 | Associate detailed provenance with artefacts and distributions. |
| R1.3 | Conform to GS1 and domain-relevant community standards and profiles. |

### 8.3 FAIR profile deliverables

A FAIR-conformant publication package should include:

- a persistent identifier policy;
- DCAT or equivalent discovery metadata;
- a machine-readable licence;
- PROV-O or equivalent provenance;
- distribution metadata and access URLs;
- authentication and authorisation metadata where relevant;
- vocabulary dependencies;
- qualified relationships;
- a persistence and tombstone policy;
- a FAIR conformance report.

### 8.4 FAIR profile test question

> Can a machine find the artefact, retrieve its metadata and permitted representations, interpret the semantics using accessible vocabularies, establish provenance and usage conditions, and determine whether it is suitable for reuse?

---
