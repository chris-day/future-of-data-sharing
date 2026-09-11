---
title: GenAI-Enabled API Contract
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
- 7.8 GS1 GenAI-Enabled API Semantic Publication Profile
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# GenAI-Enabled API Contract

*Source version 1.2.0. Draft for discussion and validation.*

## 7.8 GS1 GenAI-Enabled API Semantic Publication Profile

**Purpose:** Define the mandatory publication contract for an API description that can be reliably discovered, interpreted, selected, invoked and governed by generative-AI systems and deterministically projected into MCP tools, MCP resources, Arazzo workflows, A2A skills and comparable agent interfaces.

A conformant API is not merely an OpenAPI document that passes syntactic validation. It is an authoritative, semantically explicit and operationally safe capability description in which the meaning of the API, its operations, inputs, outputs, policies, provenance, effects and failure modes can be interpreted without relying on undocumented human knowledge.

The profile establishes a three-layer model:

1. **Authoritative interface contract** — a complete OpenAPI description of the HTTP API.
2. **Semantic context contract** — versioned JSON-LD contexts and profile identifiers that connect API elements and payload fields to GS1 and external semantic resources.
3. **Agent projection contract** — deterministic rules for generating MCP resources and tools, Arazzo workflows, A2A skills and other approved agent-facing representations.

The OpenAPI description remains the authoritative technical interface definition. JSON-LD supplies semantic context; it does not replace JSON Schema validation. MCP, Arazzo and A2A artefacts are governed projections; they must not become independent, divergent sources of API meaning.

**Applicable APIs include:**

- GS1 identifier resolution and verification APIs;
- registry and licence-data APIs;
- GS1 Digital Link services;
- EPCIS capture, query and validation APIs;
- GPC classification and vocabulary APIs;
- standards and semantic-artefact discovery APIs;
- Digital Product Passport and regulatory-data APIs;
- validation, transformation and conformance services;
- data-product and catalogue APIs;
- trusted claims and provenance services.

### Technical baseline

| Concern | Profile baseline |
| --- | --- |
| HTTP interface description | OpenAPI Specification 3.2.0 is the target baseline. OpenAPI 3.1.x may be accepted as a managed migration class where tooling constraints are documented. |
| Schema language | An explicit JSON Schema dialect must be declared. JSON Schema 2020-12 should be used where supported. |
| Semantic context | JSON-LD 1.1 contexts, with stable IRIs and controlled context lifecycle. |
| Semantic validation | SHACL for RDF/JSON-LD graph constraints where graph-level validation is required. |
| OpenAPI augmentation | Standard OpenAPI fields first; controlled `x-gs1-*` extensions and OpenAPI Overlay documents only where required. |
| Multi-operation workflow | Arazzo for defined outcomes involving multiple API operations. |
| Agent-to-tool projection | MCP resources, resource templates and tools generated from approved API operations and semantic publication artefacts. |
| Agent-to-agent projection | A2A Agent Cards and skills where delegation, task lifecycle or independent agent behaviour is required. |
| Provenance | PROV-O or an equivalent governed provenance representation. |
| Discovery | DCAT or an equivalent catalogue profile for API and service discovery where appropriate. |

### Mandatory API-level requirements

| Requirement area | Conformance requirement |
| --- | --- |
| API identity | The OpenAPI description has a persistent identifier, stable retrieval URI and independently versioned API-description identifier. In OpenAPI 3.2, `$self` should identify the description document. |
| API metadata | `info.title`, `info.summary`, `info.description`, `info.version`, publisher/contact, terms of service and licence information are complete and meaningful to humans and machines. |
| Semantic identity | The API has a persistent semantic IRI distinct from its deployment URL and OpenAPI-document location. |
| Audience and purpose | The intended users, systems, agents and business outcomes are declared. |
| Authority | The accountable publisher, service owner, governing standard and authoritative source are explicit. |
| Servers | Every server has a clear purpose, environment classification and policy. Production, test and sandbox endpoints are unambiguous. |
| Version policy | API version, OpenAPI-description version, semantic-profile version and deployment release are distinguished. Compatibility and deprecation rules are published. |
| External documentation | Normative standards, profile specifications, vocabularies, examples and operational guidance are linked through stable references. |
| Security | Security schemes, OAuth scopes, audience restrictions and authentication requirements are fully specified at API and operation level. |
| FAIR service metadata | Discovery metadata, access protocol, licence, publisher, persistence and provenance are available in a catalogue record or publication manifest. |
| Integrity | The publication package provides a digest or signature for the OpenAPI document, contexts, overlays and generated agent artefacts. |

### Mandatory operation-level requirements

Every operation selected for GenAI or agent use must define:

| Requirement | Required treatment |
| --- | --- |
| Stable operation identity | A unique, durable `operationId` and a persistent semantic operation IRI. Renaming either requires explicit replacement metadata. |
| Human-readable name | A precise `summary` that distinguishes the capability from similar operations. |
| Model-readable purpose | A `description` stating the business intent, appropriate use, non-goals and expected outcome. |
| Preconditions | Required state, authority, identifiers, data availability and validation conditions before invocation. |
| Postconditions | The state, evidence or output guaranteed after successful completion. |
| Effects | Classification as read-only, state-changing, transactional, compensatable or irreversible. |
| Idempotency | Explicit declaration of idempotent behaviour and any idempotency-key requirements. |
| Confirmation policy | Whether invocation requires no confirmation, user confirmation, privileged approval or external human review. |
| Data classification | Public, internal, confidential, personal, commercially sensitive or regulated classification for inputs and outputs. |
| Freshness | Currency, effective time, cacheability, validity interval and requirement for real-time verification. |
| Cost and quota | Material cost, rate limits, quotas and expected latency relevant to agent planning. |
| Input profile | The semantic publication profile and JSON-LD context applicable to the request. |
| Output profile | The semantic publication profile, JSON-LD context, provenance and evidence applicable to the response. |
| Errors | Structured error schema, error taxonomy, retrievability, remediation guidance and escalation path. |
| Citations | Stable identifiers for the standards clauses, rules, code lists or registry evidence supporting the operation. |
| Observability | Correlation identifier, traceability, audit event and invocation timestamp requirements. |
| Deprecation | Machine-readable deprecation status, successor operation and withdrawal date where applicable. |
| Agent exposure | Explicit decision on whether the operation may be projected as an MCP tool, MCP resource, Arazzo step, A2A skill or must remain unavailable to agents. |

Descriptions must be sufficiently discriminating for tool selection. Statements such as “gets data”, “updates item” or “processes request” are non-conformant because they do not allow a model to distinguish intent, constraints or effects.

### JSON Schema quality requirements

A GenAI-enabled API depends on schemas that are explicit enough to support model selection, argument construction, validation and self-correction.

Every request and structured response schema should:

- declare its JSON Schema dialect through the OpenAPI `jsonSchemaDialect` default or an explicit `$schema`;
- have a stable `$id` where it is published as an independently reusable schema resource;
- define `type` explicitly;
- identify mandatory properties through `required`;
- define string formats, patterns, length constraints and examples;
- define numeric ranges, units and precision where relevant;
- use enumerations or controlled-value references rather than unconstrained strings;
- state nullability explicitly rather than relying on implementation convention;
- use `readOnly` and `writeOnly` consistently;
- constrain unexpected properties with `additionalProperties: false` or `unevaluatedProperties: false` where closed-world payloads are intended;
- describe array item meaning, ordering, uniqueness and cardinality;
- provide discriminators or unambiguous composition rules for polymorphic payloads;
- include realistic valid examples and representative invalid examples;
- separate transport constraints from semantic constraints;
- link each significant schema and property to its semantic identifier;
- support deterministic conversion into MCP `inputSchema` and, where appropriate, MCP `outputSchema`.

A schema that validates syntactically but leaves key fields semantically undefined is not GenAI-ready.

## Relationship to This Repository

API contract, [semantic context](semantic-context.md), [agent projections](agent-projections.md), [publication and conformance](publication-and-conformance.md). See also the [Agentic Interface overlay](../../overlays/agentic-interfaces.md).
