"""Find source-backed code-list matches, retaining Web Vocabulary lifecycle evidence."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

from rdflib import DCTERMS, Graph, Literal, Namespace, OWL, RDF, RDFS, SKOS, URIRef

from match_gdsn_labels import GDSN, values


GS1 = Namespace("https://ref.gs1.org/voc/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gdsn", type=Path, default=Path("build/gdsn.ttl"))
    parser.add_argument("--webvoc", type=Path, default=Path("artefacts/WebVoc/gs1Voc.ttl"))
    parser.add_argument("--source-dir", type=Path, default=Path("artefacts/GDSN_Current_v3.1.35"))
    parser.add_argument("--output-dir", type=Path, default=Path("artefacts/WebVoc/gdsn-matches"))
    args = parser.parse_args()
    gdsn, voc = Graph().parse(args.gdsn), Graph().parse(args.webvoc)
    source = json.loads((args.source_dir / "gdsn_codeValues.json").read_text())
    source_index = defaultdict(list)
    for record in source:
        source_index[(record["codeListName"], record["codeValue"])].append(record)
    gdsn_ids = defaultdict(set)
    for subject in gdsn.subjects(GDSN.sourceType, Literal("codeValue")):
        for identifier in gdsn.objects(subject, GDSN.sourceId):
            gdsn_ids[str(identifier)].add(subject)

    rows, unmatched = [], []
    original_terms = {s for s in voc.subjects(GS1.originalCodeValue, None)
                      if isinstance(s, URIRef) and str(s).startswith(str(GS1))}
    source_list_names = {k[0] for k in source_index}
    candidates = {s for s in voc.subjects(RDF.type, None)
                  if isinstance(s, URIRef) and str(s).startswith(str(GS1))
                  and any(str(t).startswith(str(GS1)) and str(t).removeprefix(str(GS1)) in source_list_names
                          for t in voc.objects(s, RDF.type))}
    for subject in sorted(original_terms | candidates):
        found = False
        for cls in sorted(voc.objects(subject, RDF.type)):
            if not str(cls).startswith(str(GS1)):
                continue
            list_name = str(cls).removeprefix(str(GS1))
            codes = sorted(voc.objects(subject, GS1.originalCodeValue))
            method = "type-and-original-code"
            prefix = str(cls) + "-"
            if not codes and unquote(str(subject)).startswith(prefix):
                codes = [Literal(unquote(str(subject))[len(prefix):])]
                method = "type-and-iri-code"
            for code in codes:
                for record in source_index.get((list_name, str(code)), []):
                    for target in sorted(gdsn_ids.get(str(record["id"]), set())):
                        target_class = GDSN[f"c{record['classId']}"]
                        # Check identity against the actual GDSN graph, not just minted IRI guesses.
                        if ((target, RDF.type, target_class) not in gdsn
                                or (target, GDSN.codeListName, Literal(list_name)) not in gdsn
                                or (target, RDFS.label, Literal(record["codeValue"])) not in gdsn):
                            continue
                        found = True
                        rows.append({
                            "webvoc_iri": str(subject), "gdsn_iri": str(target),
                            "match_method": method,
                            "code_list": list_name, "original_code": str(code),
                            "source_id": record["id"], "source_name": record.get("name", ""),
                            "source_definition": record.get("definition", ""),
                            "webvoc_class": str(cls), "gdsn_class": str(target_class),
                            "webvoc_label": values(voc, subject, RDFS.label),
                            "webvoc_comment": values(voc, subject, RDFS.comment),
                            "webvoc_pref_label": values(voc, subject, SKOS.prefLabel),
                            "iri_pattern_matches": unquote(str(subject)) == str(GS1) + list_name + "-" + str(code),
                            "deprecated": any(v.toPython() is True for v in voc.objects(subject, OWL.deprecated)),
                            "replaced_by": values(voc, subject, DCTERMS.isReplacedBy),
                            "evidence": "rdf:type + " + ("originalCodeValue" if method == "type-and-original-code" else "IRI code suffix") + " + JSON sourceId/classId + GDSN codeListName/label",
                        })
        if not found:
            unmatched.append({"webvoc_iri": str(subject), "types": values(voc, subject, RDF.type),
                              "original_codes": values(voc, subject, GS1.originalCodeValue)})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, records, fields in [
        ("code-value-matches.tsv", rows, list(rows[0]) if rows else ["webvoc_iri", "gdsn_iri"]),
        ("unmatched-webvoc-code-values.tsv", unmatched, ["webvoc_iri", "types", "original_codes"]),
    ]:
        with (args.output_dir / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(records)
    pairs = {(r["webvoc_iri"], r["gdsn_iri"]) for r in rows}
    nondeprecated = [r for r in rows if not r["deprecated"]]
    summary = {
        "source_records": len(source), "source_code_lists": len({r['codeListName'] for r in source}),
        "webvoc_terms_with_original_code": len(original_terms),
        "webvoc_code_candidates_examined": len(original_terms | candidates),
        "code_match_pairs": len(pairs),
        "matched_webvoc_terms": len({r["webvoc_iri"] for r in rows}),
        "matched_gdsn_terms": len({r["gdsn_iri"] for r in rows}),
        "matched_code_lists": len({r["code_list"] for r in rows}),
        "nondeprecated_webvoc_terms": len({r["webvoc_iri"] for r in nondeprecated}),
        "gdsn_terms_with_nondeprecated_matches": len({r["gdsn_iri"] for r in nondeprecated}),
        "deprecated_webvoc_terms": len({r["webvoc_iri"] for r in rows if r["deprecated"]}),
        "pairs_matching_iri_pattern": len({(r['webvoc_iri'], r['gdsn_iri']) for r in rows if r['iri_pattern_matches']}),
        "unmatched_webvoc_code_candidates": len(unmatched),
        "unmatched_webvoc_terms_with_original_code": sum(URIRef(r['webvoc_iri']) in original_terms for r in unmatched),
        "pairs_by_method": {method: sum(r['match_method'] == method for r in rows)
                            for method in ["type-and-original-code", "type-and-iri-code"]},
    }
    label_file = args.output_dir / "matches.tsv"
    if label_file.exists():
        with label_file.open(encoding="utf-8") as stream:
            label_pairs = {(r["webvoc_iri"], r["gdsn_iri"]) for r in csv.DictReader(stream, delimiter="\t")}
        combined = label_pairs | pairs
        summary.update(label_code_pair_overlap=len(label_pairs & pairs),
                       combined_pairs=len(combined), combined_webvoc_terms=len({w for w, _ in combined}),
                       combined_gdsn_terms=len({g for _, g in combined}))
    (args.output_dir / "code-value-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
