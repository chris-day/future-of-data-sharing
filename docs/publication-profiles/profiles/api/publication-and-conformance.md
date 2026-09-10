---
title: API Publication and Conformance
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
- Publication package
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# API Publication and Conformance

*Source version 1.2.0. Draft for discussion and validation.*

## Publication package

A complete API profile package should contain:

```text
api-publication-package/
├── openapi.yaml
├── overlays/
│   ├── semantic.overlay.yaml
│   ├── trust.overlay.yaml
│   └── agent-safety.overlay.yaml
├── schemas/
│   ├── request.schema.json
│   ├── response.schema.json
│   └── problem.schema.json
├── contexts/
│   └── api-context-1.0.0.jsonld
├── shapes/
│   └── response.shacl.ttl
├── workflows/
│   └── outcome.arazzo.yaml
├── mcp/
│   ├── projection-manifest.json
│   ├── tools.json
│   └── resources.json
├── a2a/
│   └── agent-card.json
├── examples/
│   ├── valid-request.json
│   ├── valid-response.jsonld
│   └── invalid-request.json
├── provenance/
│   └── publication-prov.jsonld
├── tests/
│   ├── openapi-conformance/
│   ├── json-schema/
│   ├── json-ld/
│   ├── mcp-equivalence/
│   └── security/
└── manifest.jsonld
```

Only artefacts applicable to the API need be present, but every omission must be justified by the declared conformance class.

## Conformance requirements

A publication claiming conformance to the **GS1 GenAI-Enabled API Semantic Publication Profile** must pass:

1. OpenAPI structural and profile-rule validation.
2. JSON Schema validation for all examples.
3. JSON-LD context syntax, expansion and semantic-mapping tests.
4. Referential-integrity tests for external schemas, contexts and profile identifiers.
5. Operation-description quality checks.
6. Effect, idempotency, confirmation and data-classification completeness checks.
7. Security-scheme and scope validation.
8. Error-schema and retry-behaviour tests.
9. Deterministic MCP projection and schema-equivalence tests where MCP is claimed.
10. Arazzo workflow resolution tests where workflows are claimed.
11. A2A Agent Card and skill-reference tests where A2A is claimed.
12. Provenance, versioning, integrity and deprecation tests.
13. Positive, negative, misuse and prompt-injection test cases.
14. Human review for operations with material side effects.

## Profile test question

> Can an unfamiliar authorised AI system determine what this API does, when it should and should not use each operation, what every input and output means, which authority and standards support the result, what effects and risks invocation creates, how to recover from failure, and how to generate an equivalent MCP tool or resource without inventing missing semantics?

If any answer depends on undocumented institutional knowledge, the API is not yet fully GenAI-enabled.

---

## Relationship to This Repository

[API contract](index.md), [semantic context](semantic-context.md), [agent projections](agent-projections.md), publication and conformance. See also the [Agentic Interface overlay](../../overlays/agentic-interfaces.md).
