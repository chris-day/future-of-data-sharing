---
title: Controlled Vocabularies and Code Lists
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
- 7.2 GS1 Controlled Vocabulary and Code List Publication Profile
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Controlled Vocabularies and Code Lists

*Source version 1.2.0. Draft for discussion and validation.*

## 7.2 GS1 Controlled Vocabulary and Code List Publication Profile

**Purpose:** Publish controlled values as resolvable, multilingual, versioned semantic resources.

**Applicable outputs:**

- Application Identifiers;
- GPC concepts;
- Core Business Vocabulary terms;
- EDI code lists;
- glossary terms;
- regulatory code lists.

**Recommended semantic basis:** SKOS, supplemented by OWL and GS1-specific terms where the semantics exceed thesaurus relationships.

**Required capabilities:**

- concept scheme and concept identifiers;
- code or notation;
- preferred, alternative and hidden labels;
- definitions, scope notes and examples;
- language tagging;
- broader, narrower and related relationships;
- exact, close, broad and narrow mappings where appropriate;
- status, effective dates and deprecation;
- scheme and concept provenance;
- hierarchy and label validation.

**Example:** A GPC brick is published with its code, multilingual labels, hierarchy, inclusion/exclusion notes, mappings to GS1 Web Vocabulary classes, release provenance, JSON-LD/RDF distributions and SHACL validation.

---

## Relationship to This Repository

[GPC and TSV generation](../../tsv/generation.md) and [Google taxonomy generation](../../tsv/google-product-taxonomy.md).
