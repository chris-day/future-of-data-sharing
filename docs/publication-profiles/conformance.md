---
title: Conformance and Readiness
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
- 14. Conformance model
- 21. Core test of semantic publication readiness
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Conformance and Readiness

*Source version 1.2.0. Draft for discussion and validation.*

## 14. Conformance model

A publication may claim conformance to one base profile and multiple overlays.

### 14.1 Suggested conformance classes

| Class | Meaning |
| --- | --- |
| **MR — Machine-readable** | The artefact is expressed in a structured format with an authoritative schema or model. Primarily an 8.3.a outcome. |
| **SP — Semantically published** | Core identity, metadata, semantics, versioning, provenance, relationships, validation and representations conform to an 8.3.b base profile. |
| **FAIR — FAIR-conformant publication** | The publication meets the FAIR overlay requirements and supplies a conformance report. |
| **LD — Linked Data** | The publication supplies conformant RDF/JSON-LD representations and resolvable semantic links. |
| **MD — Semantic Markdown** | The Markdown representation preserves authority, hierarchy, identifiers, normative status and provenance. |
| **AIR — AI-retrievable** | Retrieval units, citations, version context and integrity information support grounded AI retrieval. |
| **GAPI — GenAI-enabled API** | OpenAPI, JSON Schema and JSON-LD context conform to the API profile and support governed deterministic projection to MCP and related agent interfaces. |
| **AG — Agent-ready** | API, workflow or agent capability descriptions include semantic, trust, policy, safety and side-effect metadata. |

### 14.2 Example conformance claim

```yaml
conforms_to:
  - GS1-Core-Semantic-Publication-Profile-v1
  - GS1-Standards-Artefact-Profile-v1
  - GS1-FAIR-Overlay-v1
  - GS1-Markdown-Overlay-v1
  - GS1-AI-Retrieval-Overlay-v1
```

### 14.3 Conformance evidence

Every claim should link to:

- profile version;
- validation date;
- validation engine and version;
- test suite version;
- machine-readable validation report;
- exceptions or warnings;
- responsible publisher.

---

## 21. Core test of semantic publication readiness

A GS1 artefact is semantically publication-ready when an unfamiliar authorised machine can determine:

- what the artefact is;
- who published and approved it;
- which version is authoritative;
- what its concepts and fields mean;
- which vocabularies and standards it depends on;
- how it relates to other GS1 artefacts;
- which representations are available;
- how to retrieve it;
- which access and usage conditions apply;
- how it was derived;
- whether it passes its declared constraints;
- whether it is current, superseded or deprecated;
- how to cite it;
- which safe actions and workflows are available through downstream interfaces.

When these questions can be answered from machine-readable metadata and validated artefacts, the output has progressed beyond machine readability to **FAIR, semantically governed and agent-ready publication**.

---

## Relationship to This Repository

The publication classes MR, SP, FAIR, LD, MD, AIR, GAPI and AG are distinct from [Product Holon PH-C conformance levels](../architecture/governance-and-conformance.md). No equivalence between the two schemes is asserted. Building this documentation is not profile conformance validation.
