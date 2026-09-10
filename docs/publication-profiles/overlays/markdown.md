---
title: Markdown Serialisation
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
- 10. Markdown Serialisation Overlay
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Markdown Serialisation

*Source version 1.2.0. Draft for discussion and validation.*

## 10. Markdown Serialisation Overlay

### 10.1 Purpose

Markdown is valuable for standards-as-code, source control, diffing, static-site publication, AI retrieval and human review. However, a raw conversion from PDF or Word to Markdown can lose identity, hierarchy, table semantics, normative status, references and provenance. The Markdown profile therefore defines a **source-preserving semantic serialisation**, not merely a text conversion.

### 10.2 Required Markdown controls

| Concern | Requirement |
| --- | --- |
| Document metadata | YAML front matter identifies title, artefact identifier, version, status, language, publisher, source and licence. |
| Stable hierarchy | Headings reflect the authoritative structural hierarchy and carry stable anchors. |
| Component identity | Clauses, requirements, tables, figures, notes and examples have explicit identifiers where they are independently cited or retrieved. |
| Normative status | Normative, informative, note, example, warning and deprecated content are explicitly marked. |
| Requirement semantics | Normative keywords and obligation level are preserved and, where feasible, represented in a sidecar manifest. |
| Tables | Simple tables use Markdown; complex normative tables retain a structured JSON/CSV/JSON-LD sidecar linked from the Markdown. |
| References | Internal and external references resolve to stable identifiers, not page numbers alone. |
| Figures | Alt text, figure identifier, caption and source are mandatory. |
| Code and schemas | Language-labelled fenced blocks are used; downloadable source files remain authoritative where appropriate. |
| Provenance | Generation tool, source version, timestamp and content hash are recorded. |
| Retrieval units | A chunk manifest maps retrieval units to authoritative component identifiers and source locations. |
| Round-trip protection | The profile states whether Markdown is authoritative source, generated view or both. |
| Security | Embedded HTML and executable content are restricted by policy. |

### 10.3 Recommended front matter

```yaml
title: "GS1 Standard Component Title"
artefact_id: "<persistent artefact identifier>"
component_id: "<persistent component identifier>"
version: "<standard version>"
status: "normative"
language: "en"
publisher: "GS1"
source:
  title: "<authoritative source standard>"
  version: "<source version>"
  component: "<source clause or table>"
representations:
  html: "<canonical HTML location>"
  json_ld: "<JSON-LD distribution>"
  schema: "<validation schema>"
provenance:
  generated_at: "<timestamp>"
  generator: "<pipeline and version>"
  content_hash: "<digest>"
```

### 10.4 Semantic Markdown sidecars

Markdown should be accompanied by sidecars when semantics cannot be expressed safely in prose:

- `manifest.jsonld` — artefact and distribution metadata;
- `components.json` — heading, clause, table and requirement identifiers;
- `requirements.jsonld` — machine-readable obligations and applicability;
- `tables/*.json` — structured normative table content;
- `links.jsonld` — qualified references and dependencies;
- `provenance.ttl` — derivation and publication history;
- `chunks.json` — retrieval units and citation anchors.

### 10.5 AI retrieval requirements

A conformant Markdown publication should allow an AI retrieval system to:

- retrieve a clause without losing its parent standard and version;
- distinguish normative requirements from examples and commentary;
- cite a stable component identifier;
- follow definitions and referenced concepts;
- determine applicability and effective date;
- identify superseded content;
- verify that the retrieved text matches the authoritative version.

---
