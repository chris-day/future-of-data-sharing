"""Reproduce the section-preserving Zensical view of publication profiles v1.2.0."""

import hashlib
import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "artefacts/GS1_8_3b_Semantic_Publication_Profiles_v1.2.0.md"
DEST = ROOT / "docs/publication-profiles"


def main():
    raw = SOURCE.read_text(encoding="utf-8")
    lines = raw.splitlines(keepends=True)
    metadata = yaml.safe_load(raw.split("---", 2)[1])
    headings = {}
    fenced = False
    for index, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
        if not fenced and re.match(r"^#{2,4} ", line):
            headings[line.strip()] = index

    def section(number):
        return next(i for h, i in headings.items() if h.startswith(f"## {number}. "))

    pages = []

    def add(path, title, spans, shift=0, related=""):
        pages.append((path, title, spans, shift, related))

    add("index.md", "Semantic Publication Profiles", [(headings["## Executive summary"], section(3))])
    add("workstream-boundaries.md", "Workstream Boundaries", [(section(3), section(4))], related=
        "The Product Holon architecture also proposes an 8.4.a discovery and proof role. "
        "These are separate draft allocations; this conversion does not reconcile their ownership. "
        "See [the architecture handoff](../architecture/publication-and-consumption.md).")
    add("core-profile.md", "Core Requirements and Profile Family", [(section(4), section(7))])
    base = [
        ("standards-artefacts", "Standards Artefacts", ""),
        ("controlled-vocabularies", "Controlled Vocabularies and Code Lists", "[GPC and TSV generation](../../tsv/generation.md) and [Google taxonomy generation](../../tsv/google-product-taxonomy.md)."),
        ("ontologies", "Ontologies and Web Vocabularies", "[Ontology generation](../../ontology/uml2semantics.md) and [GraphDB imports](../../ontology/graphdb.md)."),
        ("context-data-products", "Context Data Products", "[Holon Construction](../../architecture/product-holon-construction.md) and [SHACL holons](../../holon/shacl.md)."),
        ("semantic-mappings", "Semantic Mappings", "[Semantic Bridge](../../architecture/semantic-bridge.md)."),
        ("registry-records", "Registry Records", ""),
        ("verifiable-claims", "Verifiable Claims", "[Publication and Consumption](../../architecture/publication-and-consumption.md) and [the illustrative HTML holon](../../holon/example/index.md). The HTML example is not conformance evidence."),
    ]
    def base_start(n):
        return next(i for h, i in headings.items() if h.startswith(f"### 7.{n} "))
    for n, (slug, title, related) in enumerate(base, 1):
        add(f"profiles/{slug}.md", title, [(base_start(n), base_start(n + 1))], -1, related)
    api_starts = [base_start(8), headings["#### JSON-LD semantic context requirements"],
                  headings["#### Deterministic MCP projection contract"], headings["#### Publication package"], section(8)]
    for n, (slug, title) in enumerate([
        ("index", "GenAI-Enabled API Contract"), ("semantic-context", "API Semantic Context"),
        ("agent-projections", "API Agent Projections"), ("publication-and-conformance", "API Publication and Conformance")]):
        add(f"profiles/api/{slug}.md", title, [(api_starts[n], api_starts[n + 1])], -1 if n == 0 else -2,
            "[API contract](index.md), [semantic context](semantic-context.md), "
            "[agent projections](agent-projections.md), [publication and conformance](publication-and-conformance.md). "
            "See also the [Agentic Interface overlay](../../overlays/agentic-interfaces.md).")
    for n, (slug, title) in enumerate([
        ("fair", "FAIR Conformance"), ("linked-data", "Linked Data Serialisation"),
        ("markdown", "Markdown Serialisation"), ("agentic-interfaces", "Agentic Interfaces"),
        ("ai-retrieval", "AI-Retrievable Standards")], 8):
        add(f"overlays/{slug}.md", title, [(section(n), section(n + 1))], related=
            "[GenAI-Enabled API profile](../profiles/api/index.md). The overlay and base profile retain their separate requirements."
            if n == 11 else "")
    add("worked-examples.md", "Worked Examples", [(section(13), section(14))])
    add("conformance.md", "Conformance and Readiness", [(section(14), section(15)), (section(21), section(22))], related=
        "The publication classes MR, SP, FAIR, LD, MD, AIR, GAPI and AG are distinct from "
        "[Product Holon PH-C conformance levels](../architecture/governance-and-conformance.md). "
        "No equivalence between the two schemes is asserted. Building this documentation is not profile conformance validation.")
    add("pilots.md", "Pilots and Deliverables", [(section(15), section(17))])
    add("governance.md", "Governance and Risks", [(section(17), section(19))])
    add("decisions-and-measures.md", "Measures and Decisions", [(section(19), section(21))])
    add("references.md", "References", [(section(22), section(23))])
    add("changelog.md", "Changes and Roadmap", [(section(23), len(lines))])

    coverage = []
    manifest = {"source": str(SOURCE.relative_to(ROOT)), "source_version": metadata["version"],
                "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "pages": []}
    for path, title, spans, shift, related in pages:
        body = []
        fenced = False
        for start, end in spans:
            coverage.extend(range(start, end))
            for line in lines[start:end]:
                if line.startswith("```"):
                    fenced = not fenced
                if not fenced and shift and re.match(r"^#{2,4} ", line):
                    marks, rest = line.split(" ", 1)
                    line = "#" * (len(marks) + shift) + " " + rest
                body.append(line)
        assert not fenced, path
        page_meta = dict(metadata)
        page_meta.pop("subtitle", None)
        page_meta.update(title=title, source=str(SOURCE.relative_to(ROOT)),
                         source_sections=[lines[start].strip().lstrip("# ") for start, _ in spans],
                         source_sha256=manifest["source_sha256"], icon="lucide/book-open")
        text = "---\n" + yaml.safe_dump(page_meta, allow_unicode=True, sort_keys=False) + "---\n\n"
        text += f"# {title}\n\n*Source version {metadata['version']}. {metadata['status']}.*\n\n"
        if path == "index.md":
            text += f"**Publication terms:** {metadata['licence']}.\n\n"
            text += "This is a curated documentation view of the source draft, not an approved profile release.\n\n"
        text += "".join(body).strip() + "\n"
        if related:
            related = re.sub(r"\[([^\]]+)\]\(" + re.escape(Path(path).name) + r"\)", r"\1", related)
            text += "\n## Relationship to This Repository\n\n" + related + "\n"
        if path == "index.md":
            text += "\n## Section Guide\n\n"
            text += "\n".join(f"- [{t}]({p})" for p, t, *_ in pages if p != path) + "\n"
        target = DEST / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        manifest["pages"].append({"path": str(target.relative_to(ROOT)), "title": title,
                                  "source_line_spans": [[a + 1, b] for a, b in spans]})
    # Section 7 is only a grouping heading; its seven profiles and API content are all retained.
    excluded = set(range(section(7), base_start(1)))
    expected = set(range(headings["## Executive summary"], len(lines))) - excluded
    assert set(coverage) == expected and len(coverage) == len(set(coverage))
    manifest["coverage"] = {"source_body_lines": len(expected), "mapped_once": len(coverage),
                            "excluded": "Original front matter/title/TOC and empty section 7 grouping heading; metadata retained on every page."}
    (ROOT / "artefacts/Semantic_Publication_Profiles_Zensical_Source_Map_v1.2.0.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(pages)} pages; {len(coverage)} source body lines mapped exactly once.")


if __name__ == "__main__":
    main()
