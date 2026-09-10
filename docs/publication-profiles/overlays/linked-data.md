---
title: Linked Data Serialisation
subtitle: A profile family for FAIR, linked-data, Markdown and agent-ready publication
  of GS1 standards and data assets
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
- 9. Linked Data Serialisation Overlay
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Linked Data Serialisation

*Source version 1.2.0. Draft for discussion and validation.*

## 9. Linked Data Serialisation Overlay

### 9.1 Purpose

The Linked Data overlay defines how a profile-conformant GS1 artefact is represented as an RDF graph and connected to other GS1 and external resources.

### 9.2 Required representations

The selected representation set should be based on the artefact and intended consumers. A typical package may include:

- JSON-LD for Web and developer integration;
- Turtle for ontology and expert review;
- RDF dataset formats where named graphs or provenance bundles are required;
- HTML with embedded structured data for human and machine discovery;
- SHACL shapes in Turtle or JSON-LD;
- a JSON-LD context where compact developer-facing JSON is needed.

### 9.3 Linked Data rules

1. Use canonical HTTPS IRIs for addressable GS1 resources where an approved identifier policy exists.
2. Distinguish the conceptual artefact from a version and from each distribution.
3. Make IRIs dereferenceable to useful metadata or representations.
4. Support content negotiation where operationally practical.
5. Use explicit RDF types.
6. Reuse established vocabularies before defining new terms.
7. Publish the meaning and governance of every GS1-specific term.
8. Qualify mappings and references rather than relying indiscriminately on `owl:sameAs`.
9. Represent provenance at artefact and distribution level.
10. Publish SHACL constraints for expected graph structures.
11. Preserve language tags and datatype semantics.
12. Provide deterministic identifiers or skolem IRIs where blank nodes would impede citation or comparison.

### 9.4 Candidate vocabulary stack

| Concern | Candidate vocabulary or standard |
| --- | --- |
| Catalogue and distributions | DCAT 3 |
| General metadata | Dublin Core Terms |
| Provenance | PROV-O |
| Controlled concepts | SKOS |
| Ontology semantics | RDF Schema and OWL 2 |
| Validation | SHACL |
| Linked-data JSON | JSON-LD 1.1 |
| Rights and policy | DCTERMS and ODRL where justified |
| Products and organisations | GS1 Web Vocabulary and GS1 identifiers |
| Web discovery | schema.org mappings where semantically appropriate |

### 9.5 Linked Data package example

```text
publication-package/
├── manifest.jsonld
├── metadata.ttl
├── artefact.jsonld
├── artefact.ttl
├── shapes.ttl
├── context.jsonld
├── provenance.ttl
├── examples/
│   ├── valid-example.jsonld
│   └── invalid-example.jsonld
└── validation-report.ttl
```

---
