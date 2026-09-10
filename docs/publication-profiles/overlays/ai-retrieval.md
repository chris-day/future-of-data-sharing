---
title: AI-Retrievable Standards
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
- 12. AI-Retrievable Standards Overlay
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# AI-Retrievable Standards

*Source version 1.2.0. Draft for discussion and validation.*

## 12. AI-Retrievable Standards Overlay

### 12.1 Purpose

This overlay makes standards content reliably retrievable, interpretable and citable by AI-assisted search and retrieval-augmented generation systems without prescribing a particular model, vector database or vendor.

### 12.2 Requirements

- stable identifiers at document, clause, table, rule and concept level;
- explicit document hierarchy;
- normative/informative classification;
- language and jurisdiction metadata;
- effective version and applicability;
- machine-readable definitions and references;
- retrieval units aligned to semantic boundaries rather than arbitrary token windows;
- citations back to authoritative identifiers;
- supersession and deprecation relationships;
- integrity hash and publication timestamp;
- access and rights metadata;
- examples and counterexamples separated from normative requirements;
- links to schemas and SHACL shapes.

### 12.3 Retrieval result contract

A retrieval response should be able to return:

- the authoritative text or structured assertion;
- component identifier;
- parent standard and version;
- normative status;
- effective date;
- definitions required for interpretation;
- referenced components;
- provenance and validation status;
- canonical human-readable link.

---
