"""Compare Web Vocabulary IRI local names with GDSN labels (no inference)."""

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from rdflib import Graph, Namespace, OWL, RDF, RDFS, URIRef, XSD


GDSN = Namespace("urn:gs1:std:gdsn:")


def language_projection(graph, subject, range_class):
    """Describe an object-to-langString candidate using declared range axioms."""
    owners = {range_class}
    pending = [range_class]
    while pending:
        for parent in graph.objects(pending.pop(), RDFS.subClassOf):
            if isinstance(parent, URIRef) and parent not in owners:
                owners.add(parent)
                pending.append(parent)
    qualifiers = set()
    for owner in owners:
        qualifiers.update(graph.subjects(RDFS.domain, owner))
        for restriction in graph.objects(owner, RDFS.subClassOf):
            qualifiers.update(graph.objects(restriction, OWL.onProperty))
    languages = {p for p in qualifiers if any(
        normalize(str(label)) == "languagecode" for label in graph.objects(p, RDFS.label))}
    structured = (graph.value(range_class, GDSN.sourceType) is not None
                  and str(graph.value(range_class, GDSN.sourceType)) == "3"
                  and (range_class, GDSN.valueDatatype, XSD.string) in graph
                  and (range_class, RDF.type, OWL.Class) in graph)
    return {
        "range_class": str(range_class),
        "range_label": values(graph, range_class, RDFS.label),
        "range_source_type": values(graph, range_class, GDSN.sourceType),
        "value_datatype": values(graph, range_class, GDSN.valueDatatype),
        "structured_text_confirmed": structured,
        "value_path": f"<{subject}>/<{RDF.value}>" if structured else "",
        "language_properties": " | ".join(sorted(map(str, languages))),
        "language_paths": " | ".join(f"<{subject}>/<{p}>" for p in sorted(languages)),
        "other_qualifiers": " | ".join(
            f"{p} ({values(graph, p, RDFS.label)})" for p in sorted(qualifiers - languages)),
        "projection_status": ("structured text with language qualifier" if structured and languages
                              else "structured text; language qualifier not found" if structured
                              else "review range structure"),
    }


def normalize(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def kind(graph, subject):
    types = set(graph.objects(subject, RDF.type))
    for iri, name in [(OWL.ObjectProperty, "object property"),
                      (OWL.DatatypeProperty, "datatype property"),
                      (OWL.AnnotationProperty, "annotation property"),
                      (RDF.Property, "property"),
                      (OWL.Class, "class"), (RDFS.Class, "class"),
                      (RDFS.Datatype, "datatype")]:
        if iri in types:
            return name
    return "individual/other"


def values(graph, subject, predicate):
    return " | ".join(sorted(str(x) for x in graph.objects(subject, predicate)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gdsn", type=Path, default=Path("build/gdsn.ttl"))
    parser.add_argument("--webvoc", type=Path, default=Path("artefacts/WebVoc/gs1Voc.ttl"))
    parser.add_argument("--output-dir", type=Path, default=Path("artefacts/WebVoc/gdsn-matches"))
    args = parser.parse_args()
    gdsn, voc = Graph().parse(args.gdsn), Graph().parse(args.webvoc)
    index = defaultdict(set)
    for subject, label in gdsn.subject_objects(RDFS.label):
        if isinstance(subject, URIRef) and str(subject).startswith("urn:gs1:std:gdsn:"):
            index[normalize(str(label))].add((subject, str(label)))
    gdsn_terms = {str(subject) for candidates in index.values() for subject, _ in candidates}
    terms = sorted({s for s in voc.subjects() if isinstance(s, URIRef)
                    and str(s).startswith("https://ref.gs1.org/voc/")
                    and str(s) != "https://ref.gs1.org/voc/"})
    rows, unmatched, language_rows = [], [], []
    for term in terms:
        local = str(term).removeprefix("https://ref.gs1.org/voc/")
        matches = sorted(index.get(normalize(local), set()))
        if not matches:
            unmatched.append({"webvoc_iri": str(term), "local_name": local,
                              "kind": kind(voc, term)})
        for subject, label in matches:
            method = ("exact" if local == label else "case-insensitive"
                      if local.casefold() == label.casefold() else "normalized")
            row = {"match_method": method, "webvoc_iri": str(term),
                   "webvoc_local_name": local, "gdsn_iri": str(subject),
                   "gdsn_label": label, "candidate_count": len(matches)}
            for name, graph, resource in [("webvoc", voc, term), ("gdsn", gdsn, subject)]:
                row[name + "_kind"] = kind(graph, resource)
                for key, predicate in [("types", RDF.type), ("domain", RDFS.domain),
                                       ("range", RDFS.range), ("comment", RDFS.comment)]:
                    row[name + "_" + key] = values(graph, resource, predicate)
            row["same_kind"] = row["webvoc_kind"] == row["gdsn_kind"]
            row["object_to_langstring"] = (
                (term, RDF.type, OWL.DatatypeProperty) in voc
                and (term, RDFS.range, RDF.langString) in voc
                and (subject, RDF.type, OWL.ObjectProperty) in gdsn)
            if row["object_to_langstring"]:
                for range_class in sorted(set(gdsn.objects(subject, RDFS.range))):
                    language_rows.append({**row, **language_projection(gdsn, subject, range_class)})
            rows.append(row)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, records in [("matches.tsv", rows), ("unmatched-webvoc.tsv", unmatched),
                              ("structured-language-matches.tsv", language_rows)]:
        if records:
            with (args.output_dir / filename).open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(records[0]), delimiter="\t")
                writer.writeheader()
                writer.writerows(records)
    summary = {
        "gdsn_triples": len(gdsn), "webvoc_triples": len(voc),
        "webvoc_terms": len(terms), "match_pairs": len(rows),
        "gdsn_labelled_terms_examined": len(gdsn_terms),
        "unmatched_gdsn_labelled_terms": len(gdsn_terms - {r["gdsn_iri"] for r in rows}),
        "matched_webvoc_terms": len({r["webvoc_iri"] for r in rows}),
        "matched_gdsn_resources": len({r["gdsn_iri"] for r in rows}),
        "pairs_by_method": dict(Counter(r["match_method"] for r in rows)),
        "distinct_webvoc_terms_by_method": {
            method: len({r["webvoc_iri"] for r in rows if r["match_method"] == method})
            for method in ["exact", "case-insensitive", "normalized"]},
        "distinct_gdsn_terms_by_method": {
            method: len({r["gdsn_iri"] for r in rows if r["match_method"] == method})
            for method in ["exact", "case-insensitive", "normalized"]},
        "pairs_by_kind": dict(Counter(r["webvoc_kind"] + " -> " + r["gdsn_kind"] for r in rows)),
        "ambiguous_webvoc_terms": len({r["webvoc_iri"] for r in rows if r["candidate_count"] > 1}),
        "unmatched_webvoc_terms": len(unmatched),
        "object_to_langstring_pairs": sum(r["object_to_langstring"] for r in rows),
        "structured_language_range_rows": len(language_rows),
        "confirmed_structured_language_rows": sum(r["structured_text_confirmed"] for r in language_rows),
        "structured_language_webvoc_terms": len({r["webvoc_iri"] for r in language_rows}),
        "structured_language_gdsn_terms": len({r["gdsn_iri"] for r in language_rows}),
        "structured_language_range_classes": len({r["range_class"] for r in language_rows}),
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
