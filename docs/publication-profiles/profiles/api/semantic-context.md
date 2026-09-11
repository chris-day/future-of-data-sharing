---
title: API Semantic Context
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
- JSON-LD semantic context requirements
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# API Semantic Context

*Source version 1.2.0. Draft for discussion and validation.*

## JSON-LD semantic context requirements

JSON-LD provides the semantic bridge between compact API payload names and globally identified concepts. Each GenAI-enabled API must publish one or more versioned JSON-LD 1.1 contexts covering the API's principal request and response models.

The context must:

- have a persistent, dereferenceable and versioned identifier;
- use `@version: 1.1`;
- protect governed term definitions using `@protected: true` where appropriate;
- define stable namespace prefixes;
- map payload terms to GS1 or approved external IRIs;
- declare IRI-valued fields using `@type: "@id"`;
- declare datatypes for dates, times, quantities and other typed literals where required;
- define language handling and multilingual containers where applicable;
- define array/set/list semantics through `@container` where these distinctions matter;
- avoid ambiguous term reuse across incompatible payload meanings;
- document imported, scoped and nested contexts;
- identify the source vocabulary version and semantic publication profile;
- provide provenance, publisher, release date and integrity information;
- remain resolvable after supersession through a persistence or tombstone policy;
- pass JSON-LD expansion, compaction and round-trip tests against approved examples.

Remote contexts are executable semantic dependencies. They must therefore be governed, immutable within a released version, cacheable, integrity-protected and subject to an allow-list or equivalent trust control in production agent environments.

## Supported JSON-LD publication patterns

The profile permits three controlled patterns.

| Pattern | Use | Requirements |
| --- | --- | --- |
| **Native JSON-LD** | The API directly sends or receives `application/ld+json`. | The payload includes its `@context` in the document body. Request and response schemas describe the compacted form and the semantic graph is validated separately where required. |
| **Ordinary JSON with external context** | Existing clients require `application/json`. | The OpenAPI document links the payload schema to a versioned context. HTTP responses should provide a single `Link` header using `rel="http://www.w3.org/ns/json-ld#context"` and `type="application/ld+json"` when ordinary JSON is to be interpreted as JSON-LD. |
| **Semantic sidecar mapping** | Payloads cannot be altered and HTTP headers cannot be controlled. | A governed sidecar maps each schema and property JSON Pointer to a semantic IRI and context term. The sidecar is linked from OpenAPI and included in the publication manifest. |

Native JSON-LD is preferred for new semantic APIs. Ordinary JSON plus a governed external context is appropriate for compatibility. A sidecar is the minimum acceptable pattern for legacy APIs and should have a migration plan.

## Semantic alignment between OpenAPI and JSON-LD

| OpenAPI element | Semantic publication treatment |
| --- | --- |
| OpenAPI document | Persistent API-description identifier and semantic API IRI. |
| `info` | Publisher, licence, authority, service classification and catalogue metadata. |
| Tag | Capability domain or controlled thematic concept. |
| Path item | Addressable resource pattern or interaction surface. |
| Operation | Persistent action/capability IRI, intent, effect and outcome. |
| Parameter | Semantic property IRI, identifier type, datatype and value constraints. |
| Schema | Semantic class/profile IRI and JSON-LD context reference. |
| Schema property | Semantic property IRI and value-node semantics. |
| Enumeration | Link to a controlled concept scheme and individual concept identifiers. |
| Response | Outcome class, evidence profile, provenance and freshness semantics. |
| Error response | Error concept, retryability and remediation semantics. |
| Link object | Typed transition to a related operation or resource. |
| Security scope | Governed permission or policy concept. |
| Server | Deployment environment, operator and jurisdiction metadata. |

## Candidate OpenAPI extension vocabulary

Standard OpenAPI fields must be used whenever they express the requirement. The following `x-gs1-*` extensions are candidate profile terms for requirements not represented by standard fields:

```yaml
x-gs1-semantic-id: "https://ref.gs1.org/api/id/registry"
x-gs1-profile:
  - "https://ref.gs1.org/profile/genai-api/1.0"
x-gs1-jsonld-context:
  href: "https://ref.gs1.org/context/registry/1.0.0.jsonld"
  version: "1.0.0"
  integrity: "sha256-..."
  appliesTo:
    - request
    - response
x-gs1-authority:
  publisher: "GS1"
  sourceStandard: "https://ref.gs1.org/standards/..."
x-gs1-agent-action:
  intent: "verify-product-identity"
  outcome: "authoritative registry evidence returned"
  effect: "read"
  idempotent: true
  confirmation: "none"
  retryable: true
x-gs1-input-profile: "https://ref.gs1.org/profile/registry-query/1.0"
x-gs1-output-profile: "https://ref.gs1.org/profile/registry-evidence/1.0"
x-gs1-provenance-profile: "https://ref.gs1.org/profile/provenance/1.0"
x-gs1-mcp:
  exposeAs: "tool"
  name: "gs1.verify_product_identity"
  outputMode: "structuredContent"
x-gs1-data-classification: "public"
x-gs1-human-review:
  required: false
  escalationPolicy: "https://ref.gs1.org/policy/..."
```

These names are illustrative until approved through a controlled extension registry. Their schemas, permitted locations, cardinalities, inheritance rules and compatibility policy must be machine-readable.

## Illustrative OpenAPI fragment

```yaml
openapi: 3.2.0
$self: https://ref.gs1.org/api/registry/openapi/1.0.0
jsonSchemaDialect: https://json-schema.org/draft/2020-12/schema

info:
  title: GS1 Registry Verification API
  summary: Verify a GS1 identifier and retrieve authoritative evidence.
  description: >
    Resolves a supported GS1 identifier and returns current registry evidence,
    authority, validity and provenance. This API does not establish product
    authenticity beyond the evidence explicitly returned.
  version: 1.0.0
  license:
    name: GS1 terms
    url: https://www.gs1.org/terms-use
  x-gs1-semantic-id: https://ref.gs1.org/api/id/registry-verification
  x-gs1-profile:
    - https://ref.gs1.org/profile/genai-api/1.0
  x-gs1-jsonld-context:
    href: https://ref.gs1.org/context/registry/1.0.0.jsonld
    version: 1.0.0

paths:
  /identifiers/{identifier}:
    get:
      operationId: verifyGs1Identifier
      summary: Verify a GS1 identifier
      description: >
        Use when authoritative GS1 registry evidence is required for a supplied
        identifier. Returns verification status, authoritative party, temporal
        validity and provenance. Do not use as the sole basis for an authenticity
        decision when additional evidence is required.
      x-gs1-semantic-id: https://ref.gs1.org/api/action/verify-identifier
      x-gs1-agent-action:
        intent: verify-product-identity
        outcome: authoritative-registry-evidence
        effect: read
        idempotent: true
        confirmation: none
      x-gs1-mcp:
        exposeAs: tool
        name: gs1.verify_identifier
        outputMode: structuredContent
      parameters:
        - name: identifier
          in: path
          required: true
          description: Canonical GS1 identifier value or GS1 Digital Link URI.
          schema:
            type: string
            minLength: 1
          x-gs1-semantic-id: https://ref.gs1.org/voc/gs1Identifier
      responses:
        "200":
          description: Current verification evidence.
          content:
            application/ld+json:
              schema:
                $ref: "#/components/schemas/VerificationEvidence"
        "400":
          description: The identifier is malformed or unsupported.
          content:
            application/problem+json:
              schema:
                $ref: "#/components/schemas/Problem"
```

## Illustrative JSON-LD context

The following is illustrative and subject to GS1 namespace governance:

```json
{
  "@context": {
    "@version": 1.1,
    "@protected": true,
    "gs1": "https://ref.gs1.org/voc/",
    "prov": "http://www.w3.org/ns/prov#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",

    "identifier": {
      "@id": "gs1:gs1Identifier"
    },
    "verificationStatus": {
      "@id": "gs1:verificationStatus",
      "@type": "@id"
    },
    "authoritativeParty": {
      "@id": "gs1:authoritativeParty",
      "@type": "@id"
    },
    "validFrom": {
      "@id": "gs1:validFrom",
      "@type": "xsd:dateTime"
    },
    "validThrough": {
      "@id": "gs1:validThrough",
      "@type": "xsd:dateTime"
    },
    "generatedAtTime": {
      "@id": "prov:generatedAtTime",
      "@type": "xsd:dateTime"
    },
    "wasDerivedFrom": {
      "@id": "prov:wasDerivedFrom",
      "@type": "@id"
    }
  }
}
```

## Relationship to This Repository

[API contract](index.md), semantic context, [agent projections](agent-projections.md), [publication and conformance](publication-and-conformance.md). See also the [Agentic Interface overlay](../../overlays/agentic-interfaces.md).
