---
title: Semantic Publication Profiles
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
- Executive summary
source_sha256: 956bd350a32f98a231b3f2908ec7f44303f5c81a455a5618f3afa2676fb19b3a
icon: lucide/book-open
---

# Semantic Publication Profiles

*Source version 1.2.0. Draft for discussion and validation.*

**Publication terms:** Internal GS1 working document — confirm publication terms before external release.

This is a curated documentation view of the source draft, not an approved profile release.

## Executive summary

A **semantic publication profile** is a governed, testable publication contract defining how a class of GS1 digital artefact is identified, described, structured, linked, validated, versioned, discovered, represented and made usable by humans, software and AI agents.

### Executive formulation

> **Semantic publication profiles define the repeatable rules by which GS1 standards, models and data assets are transformed from merely machine-readable artefacts into trusted, discoverable and AI-ready resources. They specify how each artefact is identified, described, versioned, linked, validated, governed and published across formats such as Linked Data, JSON-LD, Markdown and OpenAPI, while also embedding FAIR principles, provenance and agentic access patterns. In doing so, they create a consistent semantic contract between 8.3.a and downstream capabilities: 8.3.a produces the authoritative machine-readable content, 8.3.b makes that content semantically explicit and reusable, and 8.4.b exposes it through interfaces that machines, registries, data spaces and AI agents can reliably discover, interpret, verify and act upon.**

It is not simply a choice of file format. Publishing a standard as JSON, rendering it as Markdown or exposing an endpoint through OpenAPI does not, by itself, make the result semantically explicit, FAIR or agent-ready. The profile must establish the meaning, authority, provenance, lifecycle, relationships, access conditions and conformance requirements that allow an unfamiliar machine to use the artefact correctly.

The intended workstream relationship is:

- **8.3.a — Machine-readable standards and models** creates and maintains authoritative structured standards artefacts, data models, code lists, schemas and related machine-readable outputs.
- **8.3.b — Semantic and AI-ready publication** defines and validates the repeatable semantic publication profiles applied to those outputs, including FAIR metadata, linked-data representations, Markdown serialisations, validation rules and agentic description overlays.
- **8.4.b — AI Interfaces** uses the published semantic contracts to expose trustworthy discovery, retrieval, interpretation, validation and action capabilities through APIs, tools, search, agent protocols and other interfaces.

The central handoff can be summarised as:

> **8.3.a produces the authoritative digital artefact; 8.3.b turns it into a governed semantic publication package; 8.4.b exposes and applies that package through AI-compatible interfaces.**

This document proposes a profile family consisting of a common core and specialised profiles for standards artefacts, code lists, ontologies, context data products, mappings, registry records, verifiable claims and GenAI-enabled APIs, together with Markdown, linked-data, AI-retrieval and agentic-interface overlays. FAIR Data Principles are treated as cross-cutting conformance requirements rather than a separate publication format.

---

## 1. Purpose

This document defines candidate semantic publication profiles for GS1 workstream **8.3.b — Semantic and AI-ready publication**. It expands the initial profile examples to include:

- FAIR Data Principles;
- agentic profiles;
- a dedicated GenAI-Enabled API Semantic Publication Profile;
- OpenAPI enhancement and overlay patterns;
- JSON-LD contexts that provide machine-interpretable API and payload semantics;
- deterministic projection requirements for MCP resources and tools;
- Arazzo workflow descriptions;
- MCP resource and tool projections;
- A2A agent capability descriptions;
- Markdown serialisation requirements;
- linked-data serialisations;
- discovery, provenance and validation controls;
- clear handoffs to 8.3.a and 8.4.b.

The document is intended to support FY26/27 profile definition, pilot selection, validation and governance planning. It deliberately avoids assuming that 8.3.b must create a new standalone platform. The capability may be implemented through common specifications, publication pipelines, sidecars, overlays, templates, validation services and governance controls applied across existing GS1 publication channels.

---

## 2. Strategic context

The 8.3.a project defines machine-readable standards as GS1 standards content published in a structured formal format so software can discover, interpret and use it without relying on human interpretation of narrative text. Its planned outputs include structured General Specifications artefacts, Application Identifier semantics, EDI artefacts, GPC, EPCIS and CBV updates, TDS/TDT artefacts, glossary data, Web Vocabulary mappings, and regulatory artefacts for EUDR and Digital Product Passports.

Those outputs create the authoritative digital source material, but downstream use still requires a consistent publication contract. Different artefacts may otherwise use inconsistent identifiers, metadata, versioning, semantic modelling, provenance, access mechanisms and validation rules. This would reproduce document-era fragmentation in machine-readable form.

8.3.b therefore addresses the question:

> **How should GS1 standards and data assets be published so that machines and agents can determine what an artefact is, what it means, whether it is authoritative, which version applies, how it relates to other artefacts, how it may be accessed, and whether a given use conforms?**

This is the difference between **machine-readable syntax** and **machine-actionable semantic publication**.

---

## Section Guide

- [Workstream Boundaries](workstream-boundaries.md)
- [Core Requirements and Profile Family](core-profile.md)
- [Standards Artefacts](profiles/standards-artefacts.md)
- [Controlled Vocabularies and Code Lists](profiles/controlled-vocabularies.md)
- [Ontologies and Web Vocabularies](profiles/ontologies.md)
- [Context Data Products](profiles/context-data-products.md)
- [Semantic Mappings](profiles/semantic-mappings.md)
- [Registry Records](profiles/registry-records.md)
- [Verifiable Claims](profiles/verifiable-claims.md)
- [GenAI-Enabled API Contract](profiles/api/index.md)
- [API Semantic Context](profiles/api/semantic-context.md)
- [API Agent Projections](profiles/api/agent-projections.md)
- [API Publication and Conformance](profiles/api/publication-and-conformance.md)
- [FAIR Conformance](overlays/fair.md)
- [Linked Data Serialisation](overlays/linked-data.md)
- [Markdown Serialisation](overlays/markdown.md)
- [Agentic Interfaces](overlays/agentic-interfaces.md)
- [AI-Retrievable Standards](overlays/ai-retrieval.md)
- [Worked Examples](worked-examples.md)
- [Conformance and Readiness](conformance.md)
- [Pilots and Deliverables](pilots.md)
- [Governance and Risks](governance.md)
- [Measures and Decisions](decisions-and-measures.md)
- [References](references.md)
- [Changes and Roadmap](changelog.md)
