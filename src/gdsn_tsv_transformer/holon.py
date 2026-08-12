from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any
from urllib.parse import quote

from pyshacl import validate
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, XSD


SH = Namespace("http://www.w3.org/ns/shacl#")
GPC = Namespace("urn:gs1:std:gpc:")
GDSN = Namespace("urn:gs1:std:gdsn:")
GPC_SHAPES = Namespace("urn:gs1:shapes:gpc:")
EX = Namespace("urn:gs1:example:")

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

  Print the GDSN ontology traversal paths used by the holon:
    ./gs1-gdsn-holon 09506000134352 \\
      --input-kind gtin \\
      --gtin-map product-gpc-map.csv \\
      --gdsn build/gdsn.ttl \\
      --print-traversal \\
      --output build/shacl/gtin-09506000134352-with-gdsn.shacl.ttl

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

  Generate an instance-aware KATO holon from a GDSN RDF instance graph:
    ./gs1-gdsn-holon 25196100024882 \\
      --input-kind gtin \\
      --instance-data build/KATO/kato-instances.ttl \\
      --instance-base-iri urn:gs1:sample:kato: \\
      --gpc build/gpc.ttl \\
      --gdsn build/gdsn.ttl \\
      --include-gdsn \\
      --include-instance-objects \\
      --output build/shacl/kato-25196100024882-holon.shacl.ttl
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
        "--instance-data",
        type=Path,
        help="Optional RDF instance graph used to resolve GTINs and generate instance-aware GDSN object shapes.",
    )
    parser.add_argument(
        "--instance-base-iri",
        default="",
        help="Base IRI for generated instance resources, for example urn:gs1:sample:kato:.",
    )
    parser.add_argument(
        "--include-instance-objects",
        action="store_true",
        help="Use --instance-data to discover reachable GDSN objects/properties and emit nested SHACL node shapes.",
    )
    parser.add_argument(
        "--instance-max-depth",
        type=int,
        default=5,
        help="Maximum outgoing GDSN object-property depth to traverse from the selected GTIN instance.",
    )
    parser.add_argument(
        "--print-traversal",
        action="store_true",
        help="Print ontology traversal paths discovered with SPARQL. Implies --include-gdsn.",
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
    value = next(graph.objects(subject, GPC.level), None)
    return str(value) if value is not None else ""


def ensure_base_iri(value: str) -> str:
    if not value:
        return ""
    return value if value.endswith(("/", "#", ":")) else f"{value}/"


def instance_gtin_node(base_iri: str, gtin: str) -> URIRef:
    base = ensure_base_iri(base_iri)
    if not base:
        raise SystemExit("--instance-base-iri is required when resolving a GTIN against --instance-data")
    return URIRef(base + "gtin/" + quote(gtin, safe=""))


def resolve_brick_code(args: argparse.Namespace, gpc_graph: Graph) -> str:
    if args.brick_code:
        return args.brick_code.strip()
    if args.input_kind == "brick":
        return args.input.strip()
    if args.input_kind == "auto":
        candidate = GPC[args.input.strip()]
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


def resolve_brick_code_from_instance(instance_graph: Graph, gpc_graph: Graph, root: URIRef, gdsn_graph: Graph | None = None) -> str:
    for rdf_type in instance_graph.objects(root, RDF.type):
        if isinstance(rdf_type, URIRef) and str(rdf_type).startswith(str(GPC)) and gpc_level(gpc_graph, rdf_type) == "4":
            return str(rdf_type).removeprefix(str(GPC))

    if gdsn_graph is not None:
        trade_item = gdsn_class_by_label(gdsn_graph, "TradeItem")
        classification = gdsn_class_by_label(gdsn_graph, "GDSNTradeItemClassification")
        if trade_item is not None and classification is not None:
            classification_path = gdsn_object_property_path(gdsn_graph, trade_item, classification)
            gpc_category_code = choose_gdsn_property_by_domain(gdsn_graph, "gpcCategoryCode", classification)
            if classification_path and gpc_category_code is not None:
                nodes = [root]
                for prop in classification_path:
                    nodes = [obj for node in nodes for obj in instance_graph.objects(node, prop) if isinstance(obj, URIRef)]
                for node in nodes:
                    value = next(instance_graph.objects(node, gpc_category_code), None)
                    if value is not None:
                        return str(value)
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
    brick = GPC[brick_code]
    if (brick, None, None) not in gpc_graph:
        raise SystemExit(f"Brick code '{brick_code}' was not found in gpc.ttl")
    if gpc_level(gpc_graph, brick) != "4":
        raise SystemExit(f"GPC code '{brick_code}' exists but is not a level-4 Brick")

    brick_label = label(gpc_graph, brick)
    shape = GPC_SHAPES[f"Brick{brick_code}Shape"]
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


def sparql_literal(value: str) -> str:
    return json.dumps(value)


def sparql_uri(value: URIRef) -> str:
    return f"<{value}>"


def gdsn_class_by_label(graph: Graph, name: str) -> URIRef | None:
    query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?class WHERE {{
          ?class rdfs:label {sparql_literal(name)} .
        }}
        LIMIT 1
    """
    return next((row["class"] for row in graph.query(query)), None)


def choose_gdsn_property_by_domain(graph: Graph, name: str, domain: URIRef, range_ref: URIRef | None = None) -> URIRef | None:
    range_clause = f"FILTER(?range = {sparql_uri(range_ref)})" if range_ref is not None else ""
    query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?property WHERE {{
          ?property rdfs:label {sparql_literal(name)} ;
                    rdfs:domain {sparql_uri(domain)} ;
                    rdfs:range ?range .
          {range_clause}
        }}
        LIMIT 1
    """
    return next((row["property"] for row in graph.query(query)), None)


def choose_gdsn_property_for_class(graph: Graph, name: str, target_class: URIRef) -> URIRef | None:
    query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?property ?domain WHERE {{
          ?property rdfs:label {sparql_literal(name)} ;
                    rdfs:domain ?domain .
          {sparql_uri(target_class)} rdfs:subClassOf* ?domain .
        }}
        ORDER BY DESC(?domain = {sparql_uri(target_class)})
        LIMIT 1
    """
    return next((row["property"] for row in graph.query(query)), None)


def gdsn_outgoing_object_properties(graph: Graph, source_class: URIRef) -> list[tuple[URIRef, URIRef]]:
    query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?property ?range WHERE {{
          ?property a owl:ObjectProperty ;
                    rdfs:domain ?domain ;
                    rdfs:range ?range .
          {sparql_uri(source_class)} rdfs:subClassOf* ?domain .
        }}
        ORDER BY ?property
    """
    return [(row["property"], row["range"]) for row in graph.query(query)]


def gdsn_object_property_path(
    graph: Graph,
    source_class: URIRef,
    target_class: URIRef,
    max_depth: int = 5,
) -> list[URIRef]:
    queue: list[tuple[URIRef, list[URIRef]]] = [(source_class, [])]
    seen = {source_class}
    while queue:
        current_class, path = queue.pop(0)
        if len(path) >= max_depth:
            continue
        for prop, next_class in gdsn_outgoing_object_properties(graph, current_class):
            next_path = path + [prop]
            if next_class == target_class:
                return next_path
            if next_class not in seen:
                seen.add(next_class)
                queue.append((next_class, next_path))
    return []


def format_gdsn_traversal(graph: Graph, title: str, source_class: URIRef, path: list[URIRef]) -> str:
    lines = [title, label(graph, source_class)]
    for prop in path:
        range_ref = next(graph.objects(prop, RDFS.range), None)
        prop_label = label(graph, prop)
        if range_ref is None:
            lines.append(f"  -> {prop_label}")
            break
        lines.append(f"  -> {prop_label}")
        lines.append(f"     {label(graph, range_ref)}")
    return "\n".join(lines)


def gdsn_traversal_report(graph: Graph, trade_item: URIRef, gtin: str | None = None) -> str:
    sections = []
    classification = gdsn_class_by_label(graph, "GDSNTradeItemClassification")
    if classification is not None:
        path = gdsn_object_property_path(graph, trade_item, classification)
        if path:
            sections.append(format_gdsn_traversal(graph, "GPC classification bridge", trade_item, path))

    classification_attribute = gdsn_class_by_label(graph, "GDSNTradeItemClassificationAttribute")
    if classification_attribute is not None:
        path = gdsn_object_property_path(graph, trade_item, classification_attribute)
        if path:
            sections.append(format_gdsn_traversal(graph, "GPC classification attribute traversal", trade_item, path))

    additional_classification = gdsn_class_by_label(graph, "AdditionalTradeItemClassification")
    if additional_classification is not None:
        path = gdsn_object_property_path(graph, trade_item, additional_classification)
        if path:
            sections.append(format_gdsn_traversal(graph, "Additional classification traversal", trade_item, path))

    if gtin:
        gtin_property = choose_gdsn_property_for_class(graph, "gtin", trade_item)
        if gtin_property is not None:
            sections.append("\n".join(["GTIN identity bridge", label(graph, trade_item), f"  -> {label(graph, gtin_property)}"]))

    return "\n\n".join(sections)


def add_gdsn_classification_bridge(
    shapes: Graph,
    gdsn_graph: Graph,
    shape: URIRef,
    trade_item: URIRef,
    brick_code: str,
    has_value: Literal | None = None,
) -> dict[str, str]:
    classification = gdsn_class_by_label(gdsn_graph, "GDSNTradeItemClassification")
    if classification is None:
        raise SystemExit("Could not locate the GDSNTradeItemClassification class in gdsn.ttl")

    classification_path = gdsn_object_property_path(gdsn_graph, trade_item, classification)
    if not classification_path:
        raise SystemExit("Could not locate an ontology path from TradeItem to GDSNTradeItemClassification in gdsn.ttl")

    gpc_category_code = choose_gdsn_property_by_domain(
        gdsn_graph,
        "gpcCategoryCode",
        classification,
    )
    if gpc_category_code is None:
        raise SystemExit("Could not locate the GDSNTradeItemClassification.gpcCategoryCode property in gdsn.ttl")

    property_shape = BNode()
    path = BNode()
    Collection(shapes, path, classification_path + [gpc_category_code])
    shapes.add((shape, SH.property, property_shape))
    shapes.add((property_shape, SH.path, path))
    shapes.add((property_shape, SH.name, Literal("GPC Brick classification")))
    shapes.add((property_shape, SH.description, Literal("Links the GDSN TradeItem to the GPC Brick used by this holon.")))
    value = has_value if has_value is not None else Literal(brick_code)
    shapes.add((property_shape, SH.hasValue, value))
    shapes.add((property_shape, SH.minCount, Literal(1, datatype=XSD.integer)))
    shapes.add((property_shape, SH.maxCount, Literal(1, datatype=XSD.integer)))

    return {
        "path": " / ".join(str(part) for part in classification_path + [gpc_category_code]),
        "has_value": brick_code,
        "has_value_datatype": str(value.datatype) if isinstance(value, Literal) and value.datatype else "",
        "classification_path": [str(part) for part in classification_path],
        "gpc_category_code_property": str(gpc_category_code),
    }


def add_gdsn_gtin_bridge(
    shapes: Graph,
    gdsn_graph: Graph,
    shape: URIRef,
    trade_item: URIRef,
    gtin: str,
) -> dict[str, str]:
    gtin_property = choose_gdsn_property_for_class(gdsn_graph, "gtin", trade_item)
    if gtin_property is None:
        raise SystemExit("Could not locate the TradeItem GTIN property in gdsn.ttl")
    range_ref = next(gdsn_graph.objects(gtin_property, RDFS.range), None)
    gtin_value = Literal(gtin, datatype=shacl_datatype(gdsn_graph, range_ref if isinstance(range_ref, URIRef) else None))

    property_shape = BNode()
    shapes.add((shape, SH.property, property_shape))
    shapes.add((property_shape, SH.path, gtin_property))
    shapes.add((property_shape, SH.name, Literal("GTIN identity")))
    shapes.add((property_shape, SH.description, Literal("Links the GDSN TradeItem instance to the GTIN used to create this holon.")))
    shapes.add((property_shape, SH.hasValue, gtin_value))
    shapes.add((property_shape, SH.minCount, Literal(1, datatype=XSD.integer)))
    shapes.add((property_shape, SH.maxCount, Literal(1, datatype=XSD.integer)))

    return {
        "path": str(gtin_property),
        "has_value": gtin,
        "gtin_property": str(gtin_property),
        "datatype": str(range_ref) if range_ref else "",
    }


def gtin_input_value(args: argparse.Namespace, gpc_graph: Graph) -> str | None:
    if args.input_kind == "gtin":
        return args.input.strip()
    if args.input_kind != "auto":
        return None
    candidate = GPC[args.input.strip()]
    if (candidate, None, None) in gpc_graph and gpc_level(gpc_graph, candidate) == "4":
        return None
    if args.gtin_map or args.brick_code:
        return args.input.strip()
    return None


def add_gdsn_trade_item_shape(
    shapes: Graph,
    gdsn_graph: Graph,
    brick_code: str,
    gtin: str | None = None,
    target_node: URIRef | None = None,
    classification_value: Literal | None = None,
) -> dict[str, Any]:
    trade_item = next((subject for subject, value in gdsn_graph.subject_objects(RDFS.label) if str(value) == "TradeItem"), None)
    if trade_item is None:
        raise SystemExit("Could not locate the GDSN TradeItem class in gdsn.ttl")

    shape = GPC_SHAPES.TradeItemGDSNShape
    shapes.add((shape, RDF.type, SH.NodeShape))
    if target_node is not None:
        shapes.add((shape, SH.targetNode, target_node))
    else:
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

    bridge = add_gdsn_classification_bridge(shapes, gdsn_graph, shape, trade_item, brick_code, classification_value)
    gtin_bridge = add_gdsn_gtin_bridge(shapes, gdsn_graph, shape, trade_item, gtin) if gtin else None
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
        multiplicity = next(gdsn_graph.objects(prop, GDSN.originalMultiplicity), None)
        low, high = parse_multiplicity(multiplicity)
        if low:
            shapes.add((property_shape, SH.minCount, Literal(int(low), datatype=XSD.integer)))
        if high and high != "*":
            shapes.add((property_shape, SH.maxCount, Literal(int(high), datatype=XSD.integer)))
        if prop_type == OWL.DatatypeProperty:
            shapes.add((property_shape, SH.datatype, shacl_datatype(gdsn_graph, range_ref if isinstance(range_ref, URIRef) else None)))
        elif prop_type == OWL.ObjectProperty and range_ref is not None:
            shapes.add((property_shape, SH["class"], range_ref))
        if domain is not None:
            shapes.add((property_shape, SH.description, Literal(f"Source domain: {label(gdsn_graph, domain)} ({domain})")))
        if prop_type is not None:
            shapes.add((property_shape, SH.description, Literal(f"Source rdf:type: {prop_type}")))
        code_lists = sorted({str(value) for value in gdsn_graph.objects(prop, GDSN.codeListName)})
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
    report: dict[str, Any] = {"target_class": str(trade_item), "classification_bridge": bridge, "properties": emitted}
    if target_node is not None:
        report["target_node"] = str(target_node)
    if gtin_bridge is not None:
        report["gtin_bridge"] = gtin_bridge
    return report


def first_gdsn_type(instance_graph: Graph, node: URIRef) -> URIRef | None:
    return next(
        (
            rdf_type
            for rdf_type in instance_graph.objects(node, RDF.type)
            if isinstance(rdf_type, URIRef) and str(rdf_type).startswith(str(GDSN))
        ),
        None,
    )


def instance_shape_iri(node: URIRef) -> URIRef:
    token = quote(str(node), safe="").replace("%", "_")
    return GPC_SHAPES[f"Instance_{token}"]


def property_allowed_values(gdsn_graph: Graph, range_ref: URIRef | None) -> list[URIRef]:
    if range_ref is None:
        return []
    values = [subject for subject in gdsn_graph.subjects(RDF.type, range_ref) if isinstance(subject, URIRef)]
    return sorted(values, key=lambda value: label(gdsn_graph, value))


def shacl_datatype(gdsn_graph: Graph, datatype: URIRef | None) -> URIRef:
    if datatype is None:
        return XSD.string
    if str(datatype).startswith(str(XSD)):
        return datatype
    equivalent = next(gdsn_graph.objects(datatype, OWL.equivalentClass), None)
    if isinstance(equivalent, URIRef) and str(equivalent).startswith(str(XSD)):
        return equivalent
    if equivalent is not None:
        base = next(gdsn_graph.objects(equivalent, OWL.onDatatype), None)
        if isinstance(base, URIRef):
            return base
    return datatype


def add_cardinality(shapes: Graph, gdsn_graph: Graph, property_shape: BNode, prop: URIRef, observed_count: int) -> tuple[int | None, int | None]:
    multiplicity = next(gdsn_graph.objects(prop, GDSN.originalMultiplicity), None)
    low, high = parse_multiplicity(multiplicity)
    min_count = max(int(low), 1) if low else 1
    max_count = int(high) if high and high != "*" else None
    shapes.add((property_shape, SH.minCount, Literal(min_count, datatype=XSD.integer)))
    if max_count is not None:
        shapes.add((property_shape, SH.maxCount, Literal(max_count, datatype=XSD.integer)))
    return min_count, max_count


def add_instance_property_shape(
    shapes: Graph,
    gdsn_graph: Graph,
    parent_shape: URIRef,
    prop: URIRef,
    values: list[Any],
    child_shapes: dict[URIRef, URIRef],
) -> dict[str, Any]:
    property_shape = BNode()
    shapes.add((parent_shape, SH.property, property_shape))
    shapes.add((property_shape, SH.path, prop))
    shapes.add((property_shape, SH.name, Literal(label(gdsn_graph, prop))))
    min_count, max_count = add_cardinality(shapes, gdsn_graph, property_shape, prop, len(values))

    prop_type = next(gdsn_graph.objects(prop, RDF.type), None)
    domain = next(gdsn_graph.objects(prop, RDFS.domain), None)
    range_ref = next(gdsn_graph.objects(prop, RDFS.range), None)
    if domain is not None:
        shapes.add((property_shape, SH.description, Literal(f"Source domain: {label(gdsn_graph, domain)} ({domain})")))
    if prop_type is not None:
        shapes.add((property_shape, SH.description, Literal(f"Source rdf:type: {prop_type}")))

    literal_values = [value for value in values if isinstance(value, Literal)]
    object_values = [value for value in values if isinstance(value, URIRef)]
    if prop_type == OWL.DatatypeProperty or literal_values:
        datatype = range_ref if isinstance(range_ref, URIRef) else None
        if datatype is None and literal_values:
            datatype = RDF.langString if literal_values[0].language else literal_values[0].datatype
        shapes.add((property_shape, SH.datatype, shacl_datatype(gdsn_graph, datatype)))
        for value in literal_values:
            shapes.add((property_shape, SH.hasValue, value))
    elif prop_type == OWL.ObjectProperty or object_values:
        nested_shapes = [child_shapes[value] for value in object_values if value in child_shapes]
        if len(nested_shapes) == 1:
            if range_ref is not None:
                shapes.add((property_shape, SH["class"], range_ref))
            shapes.add((property_shape, SH.node, nested_shapes[0]))
        elif len(nested_shapes) > 1:
            if range_ref is not None:
                shapes.add((property_shape, SH["class"], range_ref))
            for value in object_values:
                shapes.add((property_shape, SH.hasValue, value))
        allowed_values = property_allowed_values(gdsn_graph, range_ref if isinstance(range_ref, URIRef) else None)
        non_nested_values = [value for value in object_values if value not in child_shapes]
        if allowed_values and all(value in allowed_values for value in non_nested_values):
            if range_ref is not None:
                shapes.add((property_shape, SH["class"], range_ref))
            allowed_node = BNode()
            Collection(shapes, allowed_node, allowed_values)
            shapes.add((property_shape, SH["in"], allowed_node))
        for value in non_nested_values:
            shapes.add((property_shape, SH.hasValue, value))

    return {
        "property": str(prop),
        "label": label(gdsn_graph, prop),
        "rdf_type": str(prop_type) if prop_type else "",
        "domain": str(domain) if domain else "",
        "range": str(range_ref) if range_ref else "",
        "observed_values": len(values),
        "min_count": min_count,
        "max_count": max_count,
    }


def reachable_instance_nodes(instance_graph: Graph, root: URIRef, max_depth: int) -> list[URIRef]:
    seen = {root}
    queue: deque[tuple[URIRef, int]] = deque([(root, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for prop, value in instance_graph.predicate_objects(node):
            if not str(prop).startswith(str(GDSN)):
                continue
            if isinstance(value, URIRef) and first_gdsn_type(instance_graph, value) is not None and value not in seen:
                seen.add(value)
                queue.append((value, depth + 1))
    return sorted(seen, key=str)


def is_instance_shape_property(prop: URIRef) -> bool:
    return prop == RDF.value or str(prop).startswith(str(GDSN))


def add_instance_object_shapes(
    shapes: Graph,
    gdsn_graph: Graph,
    instance_graph: Graph,
    root: URIRef,
    root_shape: URIRef,
    max_depth: int,
) -> dict[str, Any]:
    nodes = reachable_instance_nodes(instance_graph, root, max_depth)
    child_shapes = {node: (root_shape if node == root else instance_shape_iri(node)) for node in nodes}
    emitted_nodes = []

    for node in nodes:
        shape = child_shapes[node]
        shapes.add((shape, RDF.type, SH.NodeShape))
        shapes.add((shape, SH.targetNode, node))
        node_type = first_gdsn_type(instance_graph, node)
        if node_type is not None:
            shapes.add((shape, SH["class"], node_type))
            shapes.add((shape, RDFS.label, Literal(f"{label(gdsn_graph, node_type)} instance shape")))
        if node != root:
            shapes.add((shape, SH.name, Literal(str(node))))

        emitted_props = []
        predicates = sorted(
            {
                prop
                for prop, value in instance_graph.predicate_objects(node)
                if isinstance(prop, URIRef) and is_instance_shape_property(prop)
            },
            key=str,
        )
        for prop in predicates:
            values = list(instance_graph.objects(node, prop))
            emitted_props.append(add_instance_property_shape(shapes, gdsn_graph, shape, prop, values, child_shapes))
        emitted_nodes.append(
            {
                "node": str(node),
                "shape": str(shape),
                "class": str(node_type) if node_type else "",
                "class_label": label(gdsn_graph, node_type) if node_type else "",
                "properties": emitted_props,
            }
        )

    return {"root": str(root), "max_depth": max_depth, "nodes": emitted_nodes}


def instance_classification_literal(
    instance_graph: Graph,
    gdsn_graph: Graph,
    root: URIRef,
) -> Literal | None:
    trade_item = gdsn_class_by_label(gdsn_graph, "TradeItem")
    classification = gdsn_class_by_label(gdsn_graph, "GDSNTradeItemClassification")
    if trade_item is None or classification is None:
        return None
    classification_path = gdsn_object_property_path(gdsn_graph, trade_item, classification)
    gpc_category_code = choose_gdsn_property_by_domain(gdsn_graph, "gpcCategoryCode", classification)
    if not classification_path or gpc_category_code is None:
        return None
    nodes = [root]
    for prop in classification_path:
        nodes = [obj for node in nodes for obj in instance_graph.objects(node, prop) if isinstance(obj, URIRef)]
    for node in nodes:
        value = next(instance_graph.objects(node, gpc_category_code), None)
        if isinstance(value, Literal):
            return value
    return None


def validate_instance_shapes(shapes: Graph, instance_graph: Graph, *context_graphs: Graph) -> dict[str, Any]:
    Graph().parse(data=shapes.serialize(format="turtle"), format="turtle")
    data_graph = Graph()
    for graph in (instance_graph, *context_graphs):
        for triple in graph:
            data_graph.add(triple)
    conforms, _, report = validate(data_graph=data_graph, shacl_graph=shapes, inference="none")
    return {"parse": True, "instance_graph_conforms": bool(conforms), "instance_report": str(report)}


def build_validation_graphs(gpc_graph: Graph, brick_code: str, include_gdsn: bool, gtin: str | None = None) -> tuple[Graph, Graph]:
    brick = GPC[brick_code]
    attrs = brick_attributes(gpc_graph, brick)
    conforming = Graph()
    broken = Graph()
    bind_common(conforming)
    bind_common(broken)
    ok_node = EX[f"brick-{brick_code}-ok"]
    bad_node = EX[f"brick-{brick_code}-bad"]
    conforming.add((ok_node, RDF.type, brick))
    broken.add((bad_node, RDF.type, brick))
    if attrs:
        attribute_type, values = attrs[0]
        conforming.add((ok_node, attribute_type, Literal(label(gpc_graph, values[0]))))
        broken.add((bad_node, attribute_type, Literal("__INVALID_GPC_VALUE__")))
        if len(values) > 1:
            broken.add((bad_node, attribute_type, Literal(label(gpc_graph, values[0]))))
    if include_gdsn:
        trade_ok = EX["gdsn-tradeitem-ok"]
        trade_bad = EX["gdsn-tradeitem-bad"]
        ok_classification = EX["gdsn-tradeitem-ok-classification"]
        bad_classification = EX["gdsn-tradeitem-bad-classification"]
        conforming.add((trade_ok, RDF.type, GDSN.c863999331))
        conforming.add((trade_ok, GDSN["assoc_863999331_-1698192853_1"], ok_classification))
        conforming.add((ok_classification, GDSN.a289210221, Literal(brick_code)))
        if gtin:
            conforming.add((trade_ok, GDSN.a5339, Literal(gtin, datatype=XSD.string)))
        broken.add((trade_bad, RDF.type, GDSN.c863999331))
        broken.add((trade_bad, GDSN["assoc_863999331_-1698192853_1"], bad_classification))
        broken.add((bad_classification, GDSN.a289210221, Literal("__WRONG_GPC_BRICK__")))
        if gtin:
            broken.add((trade_bad, GDSN.a5339, Literal("__WRONG_GTIN__", datatype=XSD.string)))
        broken.add((trade_bad, GDSN.a212299678, Literal("not-a-float")))
        broken.add((trade_bad, GDSN.a212299678, Literal("also-not-a-float")))
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
    gtin = gtin_input_value(args, gpc_graph)
    include_gdsn = args.include_gdsn or args.print_traversal or args.include_instance_objects
    if args.include_instance_objects and args.instance_data is None:
        raise SystemExit("--include-instance-objects requires --instance-data")
    if args.write_tests and args.output is None:
        raise SystemExit("--write-tests requires --output so test data files can be written next to the SHACL file")
    if args.write_tests and args.include_instance_objects:
        raise SystemExit("--write-tests is only available for synthetic validation, not --include-instance-objects")
    output_path = args.output
    shapes = Graph()
    bind_common(shapes)

    instance_graph = load_graph(args.instance_data, default_format="turtle") if args.instance_data else None
    instance_root = instance_gtin_node(args.instance_base_iri, gtin) if instance_graph is not None and gtin else None

    gdsn_graph = None
    if include_gdsn or instance_graph is not None:
        if not args.gdsn.exists():
            raise SystemExit(f"GDSN traversal was requested, but {args.gdsn} does not exist")
        gdsn_graph = load_graph(args.gdsn, default_format="turtle")

    if args.brick_code:
        brick_code = args.brick_code.strip()
    elif instance_graph is not None and instance_root is not None:
        brick_code = resolve_brick_code_from_instance(instance_graph, gpc_graph, instance_root, gdsn_graph)
        if not brick_code:
            raise SystemExit(f"Could not resolve a GPC Brick for {instance_root} from {args.instance_data}")
    else:
        brick_code = resolve_brick_code(args, gpc_graph)

    report: dict[str, Any] = {"input": args.input, "input_kind": args.input_kind, "resolved_brick_code": brick_code}
    if instance_graph is not None:
        report["instance_data"] = str(args.instance_data)
    if instance_root is not None:
        report["instance_root"] = str(instance_root)
    report["gpc_shape"] = add_gpc_brick_shape(shapes, gpc_graph, brick_code)

    if include_gdsn:
        assert gdsn_graph is not None
        classification_value = (
            instance_classification_literal(instance_graph, gdsn_graph, instance_root)
            if instance_graph is not None and instance_root is not None
            else None
        )
        target_node = instance_root if args.include_instance_objects and instance_root is not None else None
        report["gdsn_shape"] = add_gdsn_trade_item_shape(shapes, gdsn_graph, brick_code, gtin, target_node, classification_value)
        if args.include_instance_objects:
            assert instance_graph is not None
            assert instance_root is not None
            report["instance_object_shapes"] = add_instance_object_shapes(
                shapes,
                gdsn_graph,
                instance_graph,
                instance_root,
                GPC_SHAPES.TradeItemGDSNShape,
                args.instance_max_depth,
            )

    shape_text = shapes.serialize(format="turtle")
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(shape_text, encoding="utf-8")
        report["output"] = str(output_path)
    else:
        sys.stdout.write(shape_text)
        report["output"] = "stdout"

    if not args.no_validate:
        if args.include_instance_objects and instance_graph is not None:
            context_graphs = [gpc_graph]
            if gdsn_graph is not None:
                context_graphs.append(gdsn_graph)
            report["validation"] = validate_instance_shapes(shapes, instance_graph, *context_graphs)
        else:
            conforming, broken = build_validation_graphs(gpc_graph, brick_code, include_gdsn, gtin)
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
    if args.print_traversal and gdsn_graph is not None:
        trade_item = gdsn_class_by_label(gdsn_graph, "TradeItem")
        if trade_item is None:
            raise SystemExit("Could not locate the GDSN TradeItem class in gdsn.ttl")
        traversal_text = gdsn_traversal_report(gdsn_graph, trade_item, gtin)
        if traversal_text:
            print(traversal_text, file=status_stream)
            print(file=status_stream)
    print(json.dumps({k: v for k, v in report.items() if k not in {"validation"}}, indent=2), file=status_stream)
    if "validation" in report:
        validation = report["validation"]
        if "instance_graph_conforms" in validation:
            print(
                "Validation: "
                f"parse={validation['parse']} "
                f"instance_graph_conforms={validation['instance_graph_conforms']}",
                file=status_stream,
            )
        else:
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
