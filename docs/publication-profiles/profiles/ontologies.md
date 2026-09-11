---
title: Ontologies and Web Vocabularies
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
- 7.3 GS1 Ontology and Web Vocabulary Publication Profile
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Ontologies and Web Vocabularies

*Source version 1.2.0. Draft for discussion and validation.*

## 7.3 GS1 Ontology and Web Vocabulary Publication Profile

**Purpose:** Govern publication of ontologies, semantic modules and mappings that provide machine-interpretable meaning.

**Applicable outputs:**

- GS1 Web Vocabulary releases;
- domain ontology modules;
- regulatory extensions;
- mappings from GDSN, CBV, SDD and GPC;
- context-specific subsets of larger semantic models.

**Required capabilities:**

- ontology and module identifiers;
- canonical term IRIs;
- version IRI and prior-version relations;
- class, property and individual declarations;
- definitions, usage notes and examples;
- import and dependency policy;
- semantic mapping assertions;
- deprecation and replacement policy;
- OWL consistency checks where applicable;
- SHACL validation shapes;
- release-difference report.

**Example:** A product sustainability module contains only the terms needed for materials, origin, repairability, recyclability, certification, manufacturer and facility identity while retaining links to the authoritative GS1 Web Vocabulary terms.

---

## Relationship to This Repository

[Ontology generation](../../ontology/uml2semantics.md) and [GraphDB imports](../../ontology/graphdb.md).
