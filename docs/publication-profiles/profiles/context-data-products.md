---
title: Context Data Products
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
- 7.4 GS1 Context Data Product Publication Profile
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Context Data Products

*Source version 1.2.0. Draft for discussion and validation.*

## 7.4 GS1 Context Data Product Publication Profile

**Purpose:** Package a purpose-specific collection of GS1 artefacts, semantics, constraints and examples as a reusable data product for a business, regulatory or AI context.

**Candidate contexts:**

- Digital Product Passport;
- EUDR due diligence;
- customs and cross-border trade;
- food allergens;
- healthcare product safety;
- sustainability and circularity;
- agentic product discovery and commerce.

**Recommended basis:**

- DCAT for catalogue and distribution metadata;
- a data-product vocabulary or DPROD-style wrapper for product-level responsibilities and service expectations;
- GS1 Web Vocabulary for domain semantics;
- SKOS for controlled concepts;
- SHACL for constraints;
- PROV-O for provenance;
- ODRL or an equivalent model for usage policy where needed;
- GS1 identifiers and Digital Link URIs for identity and resolution.

**Required package contents:**

- context and competency questions;
- included semantic modules and code lists;
- data model and constraints;
- sample payloads;
- API and file distributions;
- provenance and ownership;
- quality and service expectations;
- licence and usage conditions;
- change and compatibility policy;
- machine-readable catalogue record.

**Example:** A Television Digital Product Passport Context Data Product contains the relevant Web Vocabulary subset, GPC concepts, GTIN and GLN rules, origin/material/repairability/end-of-life properties, regulatory concepts, SHACL shapes, JSON-LD examples, provenance metadata and links back to source standards.

---

## Relationship to This Repository

[Holon Construction](../../architecture/product-holon-construction.md) and [SHACL holons](../../holon/shacl.md).
