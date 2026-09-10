---
title: Agentic Interfaces
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
- 11. Agentic Interface Overlay
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Agentic Interfaces

*Source version 1.2.0. Draft for discussion and validation.*

## 11. Agentic Interface Overlay

### 11.1 Purpose

The Agentic Interface Overlay is applied to APIs that first conform to the **GS1 GenAI-Enabled API Semantic Publication Profile** in section 7.8. It augments that authoritative API publication so an AI agent can safely discover, select, plan and invoke capabilities using authoritative GS1 semantics.

An agentic profile should not create a second, divergent API definition. The preferred approach is:

1. maintain an authoritative OpenAPI description;
2. apply a reusable GS1 semantic and agentic **OpenAPI Overlay**;
3. describe multi-operation outcomes using **Arazzo**;
4. project selected operations into MCP resources or tools;
5. describe agent-level skills through A2A Agent Cards where agent-to-agent delegation is required;
6. preserve the same semantic identifiers, schemas, policies and provenance across every projection.

### 11.2 OpenAPI baseline

The current OpenAPI publication family includes OpenAPI Specification 3.2.0. GS1 should select an organisational baseline based on tooling support, while defining a controlled migration path from existing 3.0 or 3.1 descriptions.

The semantic publication profile should avoid directly forking OpenAPI. Use standard fields where available and controlled `x-gs1-*` extensions or Overlay documents for GS1-specific semantics.

### 11.3 Agent-relevant OpenAPI enhancements

| Agent requirement | OpenAPI/profile treatment |
| --- | --- |
| Stable operation identity | Stable `operationId` plus a persistent semantic operation IRI. |
| Purpose and outcome | Concise description of intended outcome, not only implementation behaviour. |
| Input meaning | Schema properties linked to GS1 semantic terms and identifier types. |
| Output meaning | Response schemas linked to profiles, shapes and provenance expectations. |
| Preconditions | Machine-readable conditions that must be true before invocation. |
| Postconditions | Expected state or evidence after successful invocation. |
| Side effects | Explicit declaration of read-only, state-changing, transactional or irreversible behaviour. |
| Idempotency | Stated semantics and idempotency-key requirements. |
| Authorisation | OAuth scopes and policy semantics understandable to planning systems. |
| Data classification | Public, restricted, personal, confidential or regulated classification. |
| Trust and authority | Publisher, authoritative source, verification level and provenance. |
| Freshness | Timestamp, validity period, cacheability and real-time check requirements. |
| Failure semantics | Structured error codes, remediation guidance and retry policy. |
| Human escalation | Conditions requiring confirmation, review or manual intervention. |
| Rate and service constraints | Limits, latency expectations and service-level metadata relevant to planning. |
| Citation | Source artefact and component identifiers supporting returned data. |

### 11.4 Candidate GS1 OpenAPI extensions

The following are illustrative extension names for profile validation. They should not become normative until reviewed for overlap with standard OpenAPI, JSON Schema, security and policy mechanisms.

```yaml
x-gs1-semantic-id: "<persistent semantic identifier for the operation>"
x-gs1-standard-source:
  artefact: "<standard identifier>"
  component: "<clause, table or rule identifier>"
  version: "<standard version>"
x-gs1-agent-action:
  intent: "verify-product-identity"
  outcome: "authoritative registry evidence returned"
  sideEffect: "none"
  idempotent: true
  confirmationRequired: false
x-gs1-input-profile: "<semantic input profile identifier>"
x-gs1-output-profile: "<semantic output profile identifier>"
x-gs1-provenance-profile: "<provenance profile identifier>"
x-gs1-data-classification: "public"
x-gs1-trust-level: "authoritative-gs1-source"
x-gs1-digital-link-relations:
  - "<supported link relation identifier>"
```

### 11.5 Use of the OpenAPI Overlay Specification

The OpenAPI Overlay Specification is suited to 8.3.b because it allows metadata and transformations to remain separate from the source OpenAPI description. A GS1 agentic overlay can therefore:

- add semantic identifiers;
- insert provenance metadata;
- add or refine operation descriptions for agent interpretation;
- declare side effects and confirmation requirements;
- attach semantic profile identifiers to schemas;
- remove internal-only operations before external publication;
- apply a consistent GS1 publication policy across multiple APIs;
- generate audience-specific views without changing the authoritative source.

Candidate overlay types include:

- **GS1 Semantic Overlay** — semantic identifiers and vocabulary mappings;
- **GS1 Trust Overlay** — authority, provenance and verification metadata;
- **GS1 Agent Safety Overlay** — side effects, confirmation, escalation and policy;
- **GS1 Public Publication Overlay** — redaction and audience-specific descriptions;
- **GS1 FAIR Overlay** — identifiers, licences, catalogue and persistence metadata.

### 11.6 Arazzo workflow profile

OpenAPI describes individual HTTP operations. Agents often need an outcome requiring several calls. Arazzo can describe ordered calls and dependencies as a workflow.

Candidate GS1 workflows include:

- identify a product, retrieve registry evidence and resolve authorised links;
- retrieve a DPP context product, validate it and return provenance;
- check recall status, retrieve manufacturer guidance and subscribe to updates;
- classify an item using GPC and validate required attributes;
- validate an EPCIS event and retrieve relevant CBV definitions.

The GS1 Arazzo profile should require:

- a persistent workflow identifier;
- intended business outcome;
- referenced OpenAPI source descriptions;
- input and output semantic profiles;
- step preconditions and success criteria;
- failure and compensation paths;
- human confirmation points;
- provenance and audit outputs;
- examples and conformance tests.

### 11.7 MCP projection profile

MCP provides standard constructs for exposing resources and tools to AI applications. The 8.3.b profile should define a deterministic projection from GS1 semantic publication packages rather than treating an MCP server as the source of truth.

**MCP resources** are appropriate for:

- standards clauses and tables;
- vocabulary concepts;
- ontology modules;
- profile specifications;
- validation reports;
- registry metadata that is safe to retrieve as a resource.

**MCP tools** are appropriate for controlled actions such as:

- resolve a GS1 identifier;
- verify a registry record;
- validate JSON-LD against a GS1 profile;
- retrieve the current definition of an Application Identifier;
- classify a product against GPC candidates;
- obtain a Digital Link relation set;
- check whether an artefact version is current.

The profile should require:

- stable mapping from OpenAPI operation to MCP tool;
- tool name and description generated from authoritative metadata;
- JSON Schema `inputSchema` and, where stable structured results exist, `outputSchema`;
- structured results through MCP `structuredContent`, with a compatible textual rendering where required;
- semantic profile identifiers and JSON-LD context references;
- side-effect and confirmation metadata;
- authorisation scope mapping;
- source citations in tool results;
- provenance and validation status;
- version and deprecation policy.

### 11.8 A2A projection profile

A2A is appropriate when a GS1 capability is presented as an independent agent able to receive, manage and return tasks, rather than as a simple API tool.

A GS1 A2A profile should define:

- Agent Card identity and publisher;
- supported skills;
- input and output modes;
- semantic profile identifiers for each skill;
- authentication requirements;
- task lifecycle and status semantics;
- provenance and evidence returned with results;
- delegated authority boundaries;
- error, cancellation and human escalation behaviour;
- links back to the source OpenAPI/Arazzo descriptions.

Candidate agent skills include:

- product identity verification;
- standards interpretation with citations;
- semantic validation;
- Digital Product Passport compliance checking;
- registry evidence assembly;
- standards artefact impact analysis.

### 11.9 Relationship between OpenAPI, MCP and A2A

| Layer | Primary role | Source of semantics |
| --- | --- | --- |
| OpenAPI | HTTP operation description | 8.3.a schemas plus 8.3.b semantic and trust overlays |
| Arazzo | Multi-operation outcome and workflow | OpenAPI operations plus 8.3.b workflow semantics |
| MCP | Agent-to-tool/resource access | Projection from OpenAPI, schemas and semantic publication packages |
| A2A | Agent-to-agent discovery, delegation and task interaction | Projection from approved GS1 agent skills and workflows |
| 8.4.b implementation | Runtime interface, gateway, search or agent service | Must preserve the 8.3.b semantic contract |

---

## Relationship to This Repository

[GenAI-Enabled API profile](../profiles/api/index.md). The overlay and base profile retain their separate requirements.
