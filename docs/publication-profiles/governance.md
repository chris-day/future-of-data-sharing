---
title: Governance and Risks
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
- 17. Governance model
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Governance and Risks

*Source version 1.2.0. Draft for discussion and validation.*

## 17. Governance model

### 17.1 Governance principles

- **One authoritative meaning:** Serialisations and interfaces must derive from the same governed semantic source.
- **Profiles before platforms:** Agree the publication contract before selecting or extending infrastructure.
- **No hidden transformations:** Every generated representation must be traceable to its source and transformation activity.
- **Version everything independently:** Artefact, profile, vocabulary, schema, mapping and interface versions must be explicit.
- **Persistent metadata:** Withdrawn resources retain resolvable metadata and status.
- **Executable conformance:** Narrative requirements should be backed by validation rules wherever practical.
- **Federation-aware design:** Global semantics remain consistent while MOs can publish conformant local distributions and services.
- **Open standards first:** Reuse W3C, OpenAPI Initiative and recognised agent protocol specifications before adding GS1-specific extensions.

### 17.2 Candidate decision rights

| Decision | Proposed owner or forum |
| --- | --- |
| Authoritative standards content | Relevant GSMP governance and 8.3.a business owners |
| Core semantic publication profile | 8.3.b with Standards, Web Technology and Product review |
| GS1 semantic vocabulary terms | Established semantic governance authority |
| OpenAPI agentic overlay | Joint 8.3.b and 8.4.b review |
| Runtime interface behaviour | 8.4.b and product/service owner |
| FAIR conformance criteria | 8.3.b with FAIR and data governance expertise |
| Publication platform implementation | Relevant product and technology owner |
| External protocol alignment | Architecture, Standards and ecosystem liaison governance |

---

## 18. Key risks and controls

| Risk | Consequence | Control |
| --- | --- | --- |
| Format-first delivery | JSON or Markdown is labelled AI-ready without semantic governance. | Require profile conformance and machine-readable evidence. |
| Duplicate semantics | OpenAPI, MCP and A2A descriptions diverge. | Generate projections from a shared semantic source and test equivalence. |
| Profile proliferation | Every project creates a bespoke profile. | Use a core profile plus reusable overlays. |
| Unstable identifiers | Citations, mappings and agent references break. | Approve persistent identifier and tombstone policy early. |
| Lossy Markdown conversion | Normative meaning or table structure is lost. | Use source-preserving transformation and structured sidecars. |
| FAIR interpreted as open | Restricted or sensitive data is exposed incorrectly. | Separate FAIR accessibility from open access; publish auth and policy metadata. |
| OpenAPI extension sprawl | Tooling ignores uncontrolled `x-` fields. | Prefer standard fields and Overlay documents; govern a minimal extension registry. |
| Semantic context drift | OpenAPI schemas and JSON-LD contexts evolve independently. | Version them independently, bind them through profile metadata and run schema-to-context equivalence tests. |
| Unsafe remote context resolution | A compromised or unexpected JSON-LD context changes payload meaning or triggers unsafe retrieval. | Use versioned immutable contexts, integrity checks, caching and an approved context allow-list. |
| Automatic over-exposure | Every OpenAPI operation is generated as an MCP tool regardless of risk or relevance. | Require explicit operation eligibility and human/security approval before projection. |
| Agent unsafe action | An agent invokes a state-changing operation without confirmation. | Declare side effects, idempotency, risk and confirmation requirements. |
| Semantic drift | Artefacts and mappings change independently. | Version dependencies and automate impact assessment. |
| Platform scope creep | 8.3.b becomes a broad implementation programme. | Keep scope on profiles, publication pipelines, validation and initial pilots. |

---
