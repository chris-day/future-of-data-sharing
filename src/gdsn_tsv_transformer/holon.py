from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from pyshacl import validate
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, XSD


SH = Namespace("http://www.w3.org/ns/shacl#")
GPC = Namespace("gpc:")
GDSN = Namespace("gdsn:")
GPC_SHAPES = Namespace("gpc-shapes:")
EX = Namespace("example:")

GDSN_CROSS_CATEGORY_LABELS = [
    "gtin",
    "allergenRelatedInformation",
    "allergen",
    "nutrientHeader",
    "nutrientDetail",
    "ingredientStatement",
    "packagingRecycledContentRatio",
    "claimDetail",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gs1-gdsn-holon",
        description="Generate SHACL shapes for GPC Brick holons and optional GDSN cross-category TradeItem constraints.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
epilog="""examples:
  Generate a GPC Brick SHACL shape to stdout:
    ./gs1-gdsn-holon 10000043 > build/shacl/gpc-brick-10000043.shacl.ttl

  Generate a GPC Brick SHACL shape to a file:
    ./gs1-gdsn-holon 10000043 \\
      --gpc build/gpc.ttl \\
      --output build/shacl/gpc-brick-10000043.shacl.ttl \\
      --write-tests \\
      --report-json build/shacl/gpc-brick-10000043.report.json

  Include the optional GDSN cross-category TradeItem shape:
    ./gs1-gdsn-holon 10000043 \\
      --gpc build/gpc.ttl \\
      --gdsn build/gdsn.ttl \\
      --include-gdsn \\
      --output build/shacl/gpc-brick-10000043-with-gdsn.shacl.ttl

  Resolve a GTIN with a known Brick code:
    ./gs1-gdsn-holon 09506000134352 \\
      --input-kind gtin \\
      --brick-code 10000030 \\
      --output build/shacl/gtin-09506000134352.shacl.ttl

  Resolve a GTIN from a local CSV or JSON mapping file:
    ./gs1-gdsn-holon 09506000134352 \\
      --input-kind gtin \\
      --gtin-map product-gpc-map.csv \\
      --gtin-column gtin \\
      --brick-column brickCode \\
      --output build/shacl/gtin-09506000134352.shacl.ttl
""",
    )
    parser.add_argument(
        "input",
        help="GPC Brick code, or GTIN when --input-kind gtin is used.",
    )
    parser.add_argument(
        "--input-kind",
        choices=["auto", "brick", "gtin"],
        default="auto",
        help="Interpret the input as a Brick code, GTIN, or infer from gpc.ttl. Auto prefers an existing Brick code.",
    )
    parser.add_argument("--gpc", type=Path, default=Path("build/gpc.ttl"), help="Path to the GPC ontology.")
    parser.add_argument("--gdsn", type=Path, default=Path("build/gdsn.ttl"), help="Path to the optional GDSN ontology.")
    parser.add_argument(
        "--gtin-map",
        type=Path,
        help="CSV or JSON file that maps GTINs to Brick codes. Required for GTIN input unless --brick-code is supplied.",
    )
    parser.add_argument(
        "--brick-code",
        help="Resolved Brick code for a GTIN input. Overrides --gtin-map lookup.",
    )
    parser.add_argument(
        "--gtin-column",
        default="gtin",
        help="GTIN column/key name for --gtin-map CSV or JSON records.",
    )
    parser.add_argument(
        "--brick-column",
        default="brickCode",
        help="Brick code column/key name for --gtin-map CSV or JSON records.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output SHACL file. If omitted, SHACL Turtle is written to stdout and status messages go to stderr.",
    )
    parser.add_argument(
        "--include-gdsn",
        action="store_true",
        help="Also include the GDSN TradeItem cross-category shape when --gdsn is available.",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip pySHACL parse and test-instance validation.",
    )
    parser.add_argument(
        "--write-tests",
        action="store_true",
        help="Write conforming and deliberately broken test data graphs next to the SHACL output.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        help="Write a JSON validation and generation report.",
    )
    return parser.parse_args(argv)


def bind_common(graph: Graph) -> None:
    graph.bind("sh", SH)
    graph.bind("xsd", XSD)
    graph.bind("gpc", GPC)
    graph.bind("gdsn", GDSN)
    graph.bind("gpc-shapes", GPC_SHAPES)
    graph.bind("example", EX)


def load_graph(path: Path, default_format: str = "turtle") -> Graph:
    text = path.read_text(encoding="utf-8", errors="replace").lstrip()
    rdf_format = "xml" if text.startswith("<?xml") or text.startswith("<rdf:RDF") else default_format
    return Graph().parse(path, format=rdf_format)


def label(graph: Graph, subject: URIRef) -> str:
    return str(next(graph.objects(subject, RDFS.label), subject))


def gpc_level(graph: Graph, subject: URIRef) -> str:
    value = next(graph.objects(subject, URIRef("gpc:level")), None)
    return str(value) if value is not None else ""


def resolve_brick_code(args: argparse.Namespace, gpc_graph: Graph) -> str:
    if args.brick_code:
        return args.brick_code.strip()
    if args.input_kind == "brick":
        return args.input.strip()
    if args.input_kind == "auto":
        candidate = URIRef(f"gpc:{args.input.strip()}")
        if (candidate, None, None) in gpc_graph and gpc_level(gpc_graph, candidate) == "4":
            return args.input.strip()
    if args.input_kind in {"auto", "gtin"}:
        if not args.gtin_map:
            raise SystemExit(
                "GTIN input requires --brick-code or --gtin-map because the ontology does not contain per-GTIN product instances."
            )
        resolved = lookup_gtin(args.gtin_map, args.input.strip(), args.gtin_column, args.brick_column)
        if not resolved:
            raise SystemExit(f"GTIN '{args.input}' was not found in {args.gtin_map}")
        return resolved
    return args.input.strip()


def lookup_gtin(path: Path, gtin: str, gtin_column: str, brick_column: str) -> str:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        records = data if isinstance(data, list) else data.get("records", [])
        for row in records:
            if str(row.get(gtin_column, "")).strip() == gtin:
                return str(row.get(brick_column, "")).strip()
        return ""
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if str(row.get(gtin_column, "")).strip() == gtin:
                return str(row.get(brick_column, "")).strip()
    return ""


def brick_attributes(graph: Graph, brick: URIRef) -> list[tuple[URIRef, list[URIRef]]]:
    result: list[tuple[URIRef, list[URIRef]]] = []
    for attribute_type in graph.subjects(RDFS.subClassOf, brick):
        if gpc_level(graph, attribute_type) != "5":
            continue
        values = [
            value
            for value in graph.subjects(RDFS.subClassOf, attribute_type)
            if gpc_level(graph, value) == "6"
        ]
        if values:
            result.append((attribute_type, sorted(values, key=lambda value: label(graph, value))))
    return sorted(result, key=lambda pair: label(graph, pair[0]))


def add_gpc_brick_shape(shapes: Graph, gpc_graph: Graph, brick_code: str) -> dict[str, Any]:
    brick = URIRef(f"gpc:{brick_code}")
    if (brick, None, None) not in gpc_graph:
        raise SystemExit(f"Brick code '{brick_code}' was not found in gpc.ttl")
    if gpc_level(gpc_graph, brick) != "4":
        raise SystemExit(f"GPC code '{brick_code}' exists but is not a level-4 Brick")

    brick_label = label(gpc_graph, brick)
    shape = URIRef(f"gpc-shapes:Brick{brick_code}Shape")
    shapes.add((shape, RDF.type, SH.NodeShape))
    shapes.add((shape, SH.targetClass, brick))
    shapes.add((shape, SH.name, Literal(f"{brick_label} GPC Brick shape")))
    shapes.add((shape, RDFS.label, Literal(f"{brick_label} GPC Brick shape")))

    emitted = []
    for attribute_type, values in brick_attributes(gpc_graph, brick):
        property_shape = BNode()
        shapes.add((shape, SH.property, property_shape))
        shapes.add((property_shape, SH.path, attribute_type))
        shapes.add((property_shape, SH.name, Literal(label(gpc_graph, attribute_type))))
        shapes.add((property_shape, SH.maxCount, Literal(1, datatype=XSD.integer)))
        allowed_list = BNode()
        Collection(shapes, allowed_list, [Literal(label(gpc_graph, value)) for value in values])
        shapes.add((property_shape, SH["in"], allowed_list))
        emitted.append({"uri": str(attribute_type), "label": label(gpc_graph, attribute_type), "values": len(values)})

    return {"brick_code": brick_code, "brick_label": brick_label, "attribute_types": emitted}


def parse_multiplicity(value: Any) -> tuple[str, str]:
    raw = str(value or "").strip()
    if raw == "1":
        return "1", "1"
    if ".." in raw:
        low, high = raw.split("..", 1)
        if low.isdigit() and (high.isdigit() or high == "*"):
            return low, high
    return "", ""


def choose_gdsn_property(graph: Graph, name: str) -> URIRef | None:
    candidates = [subject for subject, value in graph.subject_objects(RDFS.label) if str(value) == name]
    if not candidates:
        return None
    if name == "gtin":
        preferred_domains = ["TradeItemIdentification", "CatalogueItemSubscription", "RegistryCatalogueItem"]
        for preferred in preferred_domains:
            for candidate in candidates:
                domain = next(graph.objects(candidate, RDFS.domain), None)
                if domain is not None and label(graph, domain) == preferred:
                    return candidate
    return candidates[0]


def add_gdsn_trade_item_shape(shapes: Graph, gdsn_graph: Graph) -> dict[str, Any]:
    trade_item = next((subject for subject, value in gdsn_graph.subject_objects(RDFS.label) if str(value) == "TradeItem"), None)
    if trade_item is None:
        raise SystemExit("Could not locate the GDSN TradeItem class in gdsn.ttl")

    shape = URIRef("gpc-shapes:TradeItemGDSNShape")
    shapes.add((shape, RDF.type, SH.NodeShape))
    shapes.add((shape, SH.targetClass, trade_item))
    shapes.add((shape, SH.name, Literal("Cross-category GDSN TradeItem shape")))
    shapes.add(
        (
            shape,
            RDFS.comment,
            Literal(
                "Generated from selected GDSN properties. Source property domains are preserved as sh:description because not all selected properties are direct TradeItem properties in the generated ontology."
            ),
        )
    )

    emitted = []
    for prop_name in GDSN_CROSS_CATEGORY_LABELS:
        prop = choose_gdsn_property(gdsn_graph, prop_name)
        if prop is None:
            continue
        property_shape = BNode()
        shapes.add((shape, SH.property, property_shape))
        shapes.add((property_shape, SH.path, prop))
        shapes.add((property_shape, SH.name, Literal(prop_name)))
        prop_type = next(gdsn_graph.objects(prop, RDF.type), None)
        domain = next(gdsn_graph.objects(prop, RDFS.domain), None)
        range_ref = next(gdsn_graph.objects(prop, RDFS.range), None)
        multiplicity = next(gdsn_graph.objects(prop, URIRef("gdsn:originalMultiplicity")), None)
        low, high = parse_multiplicity(multiplicity)
        if low:
            shapes.add((property_shape, SH.minCount, Literal(int(low), datatype=XSD.integer)))
        if high and high != "*":
            shapes.add((property_shape, SH.maxCount, Literal(int(high), datatype=XSD.integer)))
        if prop_type == OWL.DatatypeProperty:
            shapes.add((property_shape, SH.datatype, range_ref if range_ref is not None else XSD.string))
        elif prop_type == OWL.ObjectProperty and range_ref is not None:
            shapes.add((property_shape, SH["class"], range_ref))
        if domain is not None:
            shapes.add((property_shape, SH.description, Literal(f"Source domain: {label(gdsn_graph, domain)} ({domain})")))
        if prop_type is not None:
            shapes.add((property_shape, SH.description, Literal(f"Source rdf:type: {prop_type}")))
        code_lists = sorted({str(value) for value in gdsn_graph.objects(prop, URIRef("gdsn:codeListName"))})
        if code_lists:
            code_list_node = BNode()
            Collection(shapes, code_list_node, [Literal(value) for value in code_lists])
            shapes.add((property_shape, SH["in"], code_list_node))
        emitted.append(
            {
                "name": prop_name,
                "uri": str(prop),
                "rdf_type": str(prop_type) if prop_type else "",
                "domain": str(domain) if domain else "",
                "range": str(range_ref) if range_ref else "",
                "multiplicity": str(multiplicity or ""),
                "code_list_values": len(code_lists),
            }
        )
    return {"target_class": str(trade_item), "properties": emitted}


def build_validation_graphs(gpc_graph: Graph, brick_code: str, include_gdsn: bool) -> tuple[Graph, Graph]:
    brick = URIRef(f"gpc:{brick_code}")
    attrs = brick_attributes(gpc_graph, brick)
    conforming = Graph()
    broken = Graph()
    bind_common(conforming)
    bind_common(broken)
    ok_node = URIRef(f"example:brick-{brick_code}-ok")
    bad_node = URIRef(f"example:brick-{brick_code}-bad")
    conforming.add((ok_node, RDF.type, brick))
    broken.add((bad_node, RDF.type, brick))
    if attrs:
        attribute_type, values = attrs[0]
        conforming.add((ok_node, attribute_type, Literal(label(gpc_graph, values[0]))))
        broken.add((bad_node, attribute_type, Literal("__INVALID_GPC_VALUE__")))
        if len(values) > 1:
            broken.add((bad_node, attribute_type, Literal(label(gpc_graph, values[0]))))
    if include_gdsn:
        trade_ok = URIRef("example:gdsn-tradeitem-ok")
        trade_bad = URIRef("example:gdsn-tradeitem-bad")
        conforming.add((trade_ok, RDF.type, URIRef("gdsn:c863999331")))
        broken.add((trade_bad, RDF.type, URIRef("gdsn:c863999331")))
        broken.add((trade_bad, URIRef("gdsn:a212299678"), Literal("not-a-float")))
        broken.add((trade_bad, URIRef("gdsn:a212299678"), Literal("also-not-a-float")))
    return conforming, broken


def validate_shapes(shapes: Graph, conforming: Graph, broken: Graph) -> dict[str, Any]:
    Graph().parse(data=shapes.serialize(format="turtle"), format="turtle")
    empty_conforms, _, empty_report = validate(data_graph=Graph(), shacl_graph=shapes, inference="none")
    ok_conforms, _, ok_report = validate(data_graph=conforming, shacl_graph=shapes, inference="none")
    bad_conforms, _, bad_report = validate(data_graph=broken, shacl_graph=shapes, inference="none")
    return {
        "parse": True,
        "empty_graph_conforms": bool(empty_conforms),
        "conforming_test_conforms": bool(ok_conforms),
        "broken_test_conforms": bool(bad_conforms),
        "empty_report": str(empty_report),
        "conforming_report": str(ok_report),
        "broken_report": str(bad_report),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    gpc_graph = load_graph(args.gpc, default_format="turtle")
    brick_code = resolve_brick_code(args, gpc_graph)
    if args.write_tests and args.output is None:
        raise SystemExit("--write-tests requires --output so test data files can be written next to the SHACL file")
    output_path = args.output
    shapes = Graph()
    bind_common(shapes)

    report: dict[str, Any] = {"input": args.input, "input_kind": args.input_kind, "resolved_brick_code": brick_code}
    report["gpc_shape"] = add_gpc_brick_shape(shapes, gpc_graph, brick_code)

    if args.include_gdsn:
        if not args.gdsn.exists():
            raise SystemExit(f"--include-gdsn was requested, but {args.gdsn} does not exist")
        gdsn_graph = load_graph(args.gdsn, default_format="turtle")
        report["gdsn_shape"] = add_gdsn_trade_item_shape(shapes, gdsn_graph)

    shape_text = shapes.serialize(format="turtle")
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(shape_text, encoding="utf-8")
        report["output"] = str(output_path)
    else:
        sys.stdout.write(shape_text)
        report["output"] = "stdout"

    if not args.no_validate:
        conforming, broken = build_validation_graphs(gpc_graph, brick_code, args.include_gdsn)
        report["validation"] = validate_shapes(shapes, conforming, broken)
        if args.write_tests:
            assert output_path is not None
            conforming_path = output_path.with_suffix(".conforming.ttl")
            broken_path = output_path.with_suffix(".broken.ttl")
            conforming_path.write_text(conforming.serialize(format="turtle"), encoding="utf-8")
            broken_path.write_text(broken.serialize(format="turtle"), encoding="utf-8")
            report["test_data"] = {"conforming": str(conforming_path), "broken": str(broken_path)}

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    status_stream = sys.stdout if output_path is not None else sys.stderr
    print(json.dumps({k: v for k, v in report.items() if k not in {"validation"}}, indent=2), file=status_stream)
    if "validation" in report:
        validation = report["validation"]
        print(
            "Validation: "
            f"parse={validation['parse']} "
            f"empty_graph_conforms={validation['empty_graph_conforms']} "
            f"conforming_test_conforms={validation['conforming_test_conforms']} "
            f"broken_test_conforms={validation['broken_test_conforms']}",
            file=status_stream,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
