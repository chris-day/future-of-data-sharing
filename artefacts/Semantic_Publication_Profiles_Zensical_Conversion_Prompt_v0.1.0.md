---
title: Semantic Publication Profiles Zensical Conversion Prompt
version: 0.1.0
date: "2026-09-10"
status: Reusable conversion instructions
source_version: 1.2.0
---

# Semantic Publication Profiles Zensical Conversion Prompt

## Reusable Prompt

Convert `artefacts/GS1_8_3b_Semantic_Publication_Profiles_v1.2.0.md` into the
existing Zensical documentation under `docs/publication-profiles/`. Use `.venv`
for every Python and Zensical command. Inspect repository guidance, existing
navigation, local modifications, and the complete source before editing.

Create a top-level **Semantic Publication Profiles** navigation group next to
Product Holon Architecture in `zensical.toml`. Follow this section mapping:

| Destination | Source sections |
| --- | --- |
| `index.md` | Executive summary, 1-2 |
| `workstream-boundaries.md` | 3 |
| `core-profile.md` | 4-6 |
| `profiles/standards-artefacts.md` | 7.1 |
| `profiles/controlled-vocabularies.md` | 7.2 |
| `profiles/ontologies.md` | 7.3 |
| `profiles/context-data-products.md` | 7.4 |
| `profiles/semantic-mappings.md` | 7.5 |
| `profiles/registry-records.md` | 7.6 |
| `profiles/verifiable-claims.md` | 7.7 |
| `profiles/api/index.md` | 7.8 introduction through JSON Schema quality requirements |
| `profiles/api/semantic-context.md` | JSON-LD semantic context requirements through the illustrative JSON-LD context |
| `profiles/api/agent-projections.md` | Deterministic MCP projection contract through trust, safety and policy requirements |
| `profiles/api/publication-and-conformance.md` | Publication package through profile test question |
| `overlays/fair.md` | 8 |
| `overlays/linked-data.md` | 9 |
| `overlays/markdown.md` | 10 |
| `overlays/agentic-interfaces.md` | 11 |
| `overlays/ai-retrieval.md` | 12 |
| `worked-examples.md` | 13 |
| `conformance.md` | 14 and 21 |
| `pilots.md` | 15-16 |
| `governance.md` | 17-18 |
| `decisions-and-measures.md` | 19-20 |
| `references.md` | 22 |
| `changelog.md` | 23-24 |

Preserve source prose, requirement keywords, tables, diagrams, examples,
references and change history. Do not turn candidate requirements or illustrative
examples into approved standards or claims of implemented conformance. Preserve
the source's reference versions without silently updating their technical basis.

Retain source metadata on every page, including version, draft status, original
date, language, programme and publication terms. Add the source path, source
section headings and SHA-256 digest for traceability. Omit the source subtitle
from generated page metadata to keep the Zensical navigation uncluttered.
Keep the internal-publication
terms visible on the overview. Building documentation is distinct from approving
external publication or claiming semantic Markdown overlay conformance.

Use one H1 per page. Preserve numbered source headings beneath it. Promote
headings as needed when extracting profiles and API subsections, but never
rewrite content inside fenced code blocks. Replace the monolithic source TOC
with Zensical navigation and an overview section guide. Section 7's empty grouping
heading can be omitted when its full profile contents are retained. Do not leave
part or section headings detached from their contents at page boundaries.

Add contextual links to existing Holon Construction, SHACL, Semantic Bridge,
Publication and Consumption, ontology generation, GraphDB, GPC and Google taxonomy
documentation. Link the Verifiable Claims page to the illustrative HTML holon
without presenting it as conformance evidence. Cross-link the four API pages and
the Agentic Interface overlay; retain their distinct requirements. Add a few
reciprocal links in the existing architecture and a link on the site overview.

Make the unresolved governance relationships explicit: the architecture proposes
an 8.4.a discovery/proof role, while this source describes an 8.3.a/8.3.b/8.4.b
handoff. Preserve both proposals without inventing an ownership resolution.
Keep MR/SP/FAIR/LD/MD/AIR/GAPI/AG separate from the Product Holon PH-C levels;
do not imply a conformance crosswalk has been approved.

Record a source-to-page manifest with inclusive source line spans and source hash.
Verify that all substantive source content occurs exactly once, excluding only
the original title/TOC/front matter and the empty grouping heading. Check fenced
examples and Mermaid blocks are unchanged. Check generated internal links and
fragments, page navigation coverage, heading structure and empty sections.

Run `.venv/bin/zensical build --clean`, inspect the generated HTML and report
actual results. Resolve introduced warnings before finishing. Do not deploy the
site as part of conversion. Preserve unrelated user changes.

## How This Conversion Was Performed

The implementation uses
[`convert_publication_profiles_docs.py`](convert_publication_profiles_docs.py)
to locate headings outside fenced code, extract the approved spans, adjust
heading depths, retain metadata, add contextual links and write 26 pages.
All 1,604 source body lines selected for publication are mapped exactly once.
The original source is unchanged.

The generated
[`Semantic_Publication_Profiles_Zensical_Source_Map_v1.2.0.json`](Semantic_Publication_Profiles_Zensical_Source_Map_v1.2.0.json)
records the page mapping and source digest. Navigation, reciprocal architecture
links and this prompt were edited separately.

To regenerate this specific version from the repository root:

```bash
.venv/bin/python artefacts/convert_publication_profiles_docs.py
.venv/bin/zensical build --clean
```

The converter overwrites its 26 generated Markdown pages. Review local edits
before rerunning it. For a later source version, review section boundaries and
update the converter and source map deliberately; the script is version-specific.
