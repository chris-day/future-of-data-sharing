---
title: Measures and Decisions
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
- 19. Success measures
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Measures and Decisions

*Source version 1.2.0. Draft for discussion and validation.*

## 19. Success measures

Success should be measured by conformance and reuse rather than by the number of files converted.

Candidate measures include:

- percentage of pilot artefacts with persistent identifiers at required granularity;
- percentage with complete provenance and version metadata;
- FAIR conformance score and unresolved exceptions;
- percentage of structured outputs passing validation;
- number of serialisations generated from one authoritative source;
- ability to cite exact standards components in AI retrieval results;
- equivalence between OpenAPI and MCP input/output schemas;
- percentage of API schema properties mapped to governed semantic IRIs;
- percentage of JSON-LD contexts passing expansion, integrity and persistence tests;
- percentage of agent-exposed operations passing MCP eligibility, safety and projection tests;
- percentage of agent operations with declared side effects and confirmation policy;
- time required to publish a new conformant artefact version;
- number of downstream services reusing the same profile;
- reduction in bespoke semantic mappings and publication patterns;
- successful validation by selected MOs, regulators, data-space participants or solution providers.

---

## 20. Recommended immediate decisions

1. Approve the concept of a **Core Semantic Publication Profile plus specialised base profiles and overlays**.
2. Confirm FAIR as a cross-cutting conformance overlay, not a standalone serialisation.
3. Confirm that Markdown and Linked Data are complementary representations of the same governed artefact.
4. Approve the **GS1 GenAI-Enabled API Semantic Publication Profile** as the base profile for APIs intended for AI and agent consumption.
5. Require a governed JSON-LD context and deterministic MCP projection manifest for every API claiming GenAI-enabled conformance.
6. Use OpenAPI Overlay rather than forking source OpenAPI descriptions for GS1 semantic and agentic augmentation.
7. Use Arazzo for multi-operation outcome workflows where justified.
8. Treat MCP and A2A descriptions as projections from authoritative semantic and API artefacts, not as independent sources of meaning.
9. Select the four validation pilots and agree explicit exit criteria.
10. Establish a small controlled registry for profile identifiers, versions and approved `x-gs1-*` extensions.
11. Align profile lifecycle and change governance with the emerging 8.3.a MRS maintenance process.
12. Preserve the boundary that 8.3.b defines publication capability while 8.4.b implements operational AI interfaces.

---
