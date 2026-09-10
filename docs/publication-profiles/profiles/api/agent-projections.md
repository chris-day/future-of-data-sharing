---
title: API Agent Projections
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
- Deterministic MCP projection contract
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# API Agent Projections

*Source version 1.2.0. Draft for discussion and validation.*

## Deterministic MCP projection contract

A conformant API profile must define whether and how each operation is projected into MCP.

| OpenAPI/API construct | MCP projection requirement |
| --- | --- |
| Readable semantic artefact or static reference data | Project as an MCP resource when application-driven context selection is appropriate. |
| Parameterised retrievable resource | Project as an MCP resource template when the operation is resource-oriented and free of side effects. |
| Model-invokable operation | Project as an MCP tool only when the operation is explicitly approved for agent invocation. |
| `operationId` | Source for a stable MCP tool name, subject to the MCP naming constraints and a governed collision strategy. |
| `summary` | Source for the MCP tool title. |
| Agent-oriented `description` | Source for the MCP tool description; must retain non-goals, risk and effect information. |
| Request parameters/body | Combined deterministically into MCP `inputSchema`. |
| Successful structured response | Project into MCP `outputSchema` where a stable structured result exists. |
| Structured API response | Returned through MCP `structuredContent`; a compatible textual rendering may also be supplied. |
| OpenAPI links | Candidate next actions or related resources, not automatic permission to invoke. |
| Effect and confirmation metadata | Mapped to MCP annotations and enforced by the host or gateway policy. |
| Security scopes | Mapped to MCP authorisation and runtime policy; credentials are never embedded in generated tool definitions. |
| API errors | Mapped to actionable tool-execution errors that allow a model to correct inputs or decide not to retry. |
| Provenance and citations | Included in structured results or linked MCP resources. |
| Version/deprecation | Propagated to tool metadata and list-change notifications where supported. |

The generator must use an explicit inclusion policy. The presence of an OpenAPI operation does not automatically authorise exposure as an MCP tool.

## MCP tool eligibility rules

An operation may be projected as an MCP tool only when:

- its purpose and outcome are unambiguous;
- inputs and outputs have complete JSON Schemas;
- effects, idempotency and confirmation requirements are declared;
- authentication and authorisation requirements can be enforced;
- input validation and output sanitisation are defined;
- structured errors support correction or safe termination;
- rate, cost and data-classification constraints are known;
- the operation has passed security and misuse review;
- provenance and audit requirements are supported;
- the generated tool can be tested against approved positive and negative examples.

State-changing, financially material, legally significant, privacy-sensitive or irreversible operations require explicit human confirmation or an approved delegated-authority policy.

## Arazzo and A2A projections

Arazzo should be used when a user or agent outcome requires multiple OpenAPI operations, branching, parameter transfer, success criteria or recovery actions. The workflow must reference operations by stable identifiers and preserve semantic profiles, confirmation points and audit outputs.

A2A should be used only where the capability is genuinely presented as an autonomous or semi-autonomous agent skill with task lifecycle, delegation and status semantics. A2A must not be used merely to wrap a single deterministic API call when an MCP tool is sufficient.

## Trust, safety and policy requirements

A conformant GenAI-enabled API publication must include:

- input validation at the API and agent-gateway boundaries;
- output validation and sanitisation before results are supplied to a model;
- explicit data-exfiltration and prompt-injection controls for externally sourced content;
- allow-listed remote JSON-LD contexts and external schema references;
- SSRF and unsafe-reference protections for remote retrieval;
- least-privilege security scopes;
- rate limiting, timeouts and circuit-breaking;
- user confirmation for sensitive tools;
- audit logging of tool selection, supplied arguments, identity, authority, result and policy decision;
- separation of model-generated narrative from authoritative structured evidence;
- cryptographic or digest-based integrity for generated artefacts;
- a revocation or withdrawal mechanism for compromised tools, contexts or profiles;
- continuous equivalence tests between OpenAPI, JSON-LD contexts and generated MCP/A2A artefacts.

## Relationship to This Repository

[API contract](index.md), [semantic context](semantic-context.md), agent projections, [publication and conformance](publication-and-conformance.md). See also the [Agentic Interface overlay](../../overlays/agentic-interfaces.md).
