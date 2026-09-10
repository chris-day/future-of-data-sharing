---
title: Verifiable Claims
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
- 7.7 GS1 Verifiable Claims Publication Profile
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Verifiable Claims

*Source version 1.2.0. Draft for discussion and validation.*

## 7.7 GS1 Verifiable Claims Publication Profile

**Purpose:** Define the semantics of claims that may be issued, signed, verified or revoked through Verifiable Credentials or equivalent trust mechanisms.

**Candidate claims:**

- country of origin;
- organic certification;
- product authenticity;
- sustainability assertion;
- facility accreditation;
- recall status;
- regulatory conformance.

**Required capabilities:**

- identified claim subject, normally anchored by a GS1 identifier;
- claim type and semantic definition;
- issuer identity and authority;
- evidence and source;
- issue, validity and expiry dates;
- jurisdiction and scope;
- verification method;
- credential status or revocation mechanism;
- provenance;
- links to governing vocabulary terms and standards.

---

## Relationship to This Repository

[Publication and Consumption](../../architecture/publication-and-consumption.md) and [the illustrative HTML holon](../../holon/example/index.md). The HTML example is not conformance evidence.
