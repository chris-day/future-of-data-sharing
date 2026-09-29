"""JSON-LD 1.1 From RDF algorithm, independent of document I/O."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
import math
import re
from typing import Any, Literal as TypingLiteral

from rdflib import BNode, ConjunctiveGraph, Dataset, Graph, Literal, RDF, URIRef, XSD
from rdflib.term import Node

from .errors import InvalidInputError, JsonLdError, UnsupportedOptionError

type Direction = TypingLiteral["i18n-datatype", "compound-literal"] | None
type JsonObject = dict[str, Any]
type NodeMap = dict[str, JsonObject]
I18N = "https://www.w3.org/ns/i18n#"
FIRST, REST, NIL = str(RDF.first), str(RDF.rest), str(RDF.nil)
LANGUAGE, DIRECTION, VALUE = (str(RDF) + n for n in ("language", "direction", "value"))
INTEGER = re.compile(r"[+-]?[0-9]+\Z")
DOUBLE = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
LANG = re.compile(r"[a-zA-Z]{1,8}(?:-[a-zA-Z0-9]{1,8})*\Z")


def check_direction(mode: Direction) -> None:
    if mode not in (None, "i18n-datatype", "compound-literal"):
        raise UnsupportedOptionError(f"Unsupported rdf_direction: {mode!r}")


def identifier(term: Node) -> str:
    if isinstance(term, BNode):
        return "_:" + str(term)
    if isinstance(term, URIRef):
        return str(term)
    raise InvalidInputError(f"Expected IRI or blank node, got {term!r}")


def _reject_constant(value: str) -> Any:
    raise ValueError(f"Not a JSON number: {value}")


def strict_json(text: str) -> Any:
    """Decode RFC 8259 JSON, rejecting NaN and Infinity extensions."""
    return json.loads(text, parse_constant=_reject_constant)


def _value(term: Node, direction: Direction, native: bool) -> JsonObject:
    if isinstance(term, (URIRef, BNode)):
        return {"@id": identifier(term)}
    if not isinstance(term, Literal):
        raise InvalidInputError(f"Unsupported RDF object: {term!r}")
    lexical, datatype = str(term), term.datatype
    result: JsonObject = {"@value": lexical}
    if datatype == RDF.JSON:
        try:
            return {"@value": strict_json(lexical), "@type": "@json"}
        except ValueError as exc:
            raise JsonLdError(f"Invalid rdf:JSON literal: {exc}", code="invalid JSON literal") from exc
    if direction == "i18n-datatype" and str(datatype).startswith(I18N):
        language, separator, base_direction = str(datatype)[len(I18N):].partition("_")
        if not separator or base_direction not in ("ltr", "rtl"):
            raise JsonLdError(f"Invalid base direction: {base_direction!r}", code="invalid base direction")
        if language:
            _check_language(language)
            result["@language"] = language.lower()
        result["@direction"] = base_direction
        return result
    if term.language:
        result["@language"] = term.language.lower()
        return result
    if native:
        if datatype == XSD.boolean and lexical in ("true", "false", "1", "0"):
            return {"@value": lexical in ("true", "1")}
        if datatype == XSD.integer and INTEGER.fullmatch(lexical):
            return {"@value": int(lexical)}
        if datatype == XSD.double and DOUBLE.fullmatch(lexical):
            number = float(lexical)
            if math.isfinite(number):
                return {"@value": number}
    if datatype and datatype != XSD.string:
        result["@type"] = str(datatype)
    return result


def _check_language(language: str) -> None:
    if not LANG.fullmatch(language):
        raise JsonLdError(f"Invalid language tag: {language!r}", code="invalid language-tagged string")


@dataclass
class Usage:
    node: JsonObject
    property: str
    value: JsonObject


def _graphs(source: Graph) -> list[tuple[str, Graph]]:
    if isinstance(source, (Dataset, ConjunctiveGraph)):
        default = source.default_graph if isinstance(source, Dataset) else source.default_context
        contexts = source.graphs() if isinstance(source, Dataset) else source.contexts()
        return [("@default", default)] + [
            (identifier(g.identifier), g) for g in contexts
            if g.identifier != default.identifier
        ]
    return [("@default", source)]


def _equivalent(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(_equivalent(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(_equivalent(a, b) for a, b in zip(left, right))
    return left == right


def _append(node: JsonObject, key: str, value: Any) -> Any:
    values = node.setdefault(key, [])
    # JSON booleans and numbers are different even though Python True == 1.
    for old in values:
        if _equivalent(old, value):
            return old
    values.append(value)
    return value


def _node_maps(
    source: Graph, direction: Direction, native: bool, rdf_type: bool, ordered: bool,
) -> tuple[dict[str, NodeMap], dict[str, Usage | None], dict[str, list[Usage]], dict[str, set[str]]]:
    maps: dict[str, NodeMap] = {"@default": {}}
    references: dict[str, Usage | None] = {}
    nil_usages: dict[str, list[Usage]] = defaultdict(list)
    compounds: dict[str, set[str]] = defaultdict(set)
    for name, graph in _graphs(source):
        nodes = maps.setdefault(name, {})
        if name != "@default":
            maps["@default"].setdefault(name, {"@id": name})
        triples = sorted(graph, key=lambda triple: tuple(t.n3() for t in triple)) if ordered else graph
        for subject, predicate, obj in triples:
            sid, prop = identifier(subject), identifier(predicate)
            node = nodes.setdefault(sid, {"@id": sid})
            if direction == "compound-literal" and prop == DIRECTION:
                compounds[name].add(sid)
            if isinstance(obj, (URIRef, BNode)):
                oid = identifier(obj)
                nodes.setdefault(oid, {"@id": oid})
            if predicate == RDF.type and not rdf_type and isinstance(obj, (URIRef, BNode)):
                _append(node, "@type", identifier(obj))
                continue
            value = _append(node, prop, _value(obj, direction, native))
            usage = Usage(node, prop, value)
            if obj == RDF.nil:
                nil_usages[name].append(usage)
            elif isinstance(obj, BNode):
                oid = identifier(obj)
                references[oid] = None if oid in references else usage
    return maps, references, nil_usages, compounds


def _compound_literals(nodes: NodeMap, subjects: set[str], refs: dict[str, Usage | None]) -> None:
    for sid in sorted(subjects):
        usage = refs.get(sid)
        if usage is None or sid not in nodes:
            continue
        node = nodes[sid]

        def scalar(prop: str, required: bool = True) -> str | None:
            values = node.get(prop, [])
            if not values and not required:
                return None
            if len(values) != 1 or not isinstance(values[0].get("@value"), str):
                raise InvalidInputError(f"Compound literal {sid} requires one string {prop}")
            return values[0]["@value"]

        value, language, direction = scalar(VALUE), scalar(LANGUAGE, False), scalar(DIRECTION)
        if language is not None:
            _check_language(language)
        if direction not in ("ltr", "rtl"):
            raise JsonLdError(f"Invalid base direction: {direction!r}", code="invalid base direction")
        usage.value.clear()
        usage.value.update({"@value": value, "@direction": direction})
        if language:
            usage.value["@language"] = language.lower()
        del nodes[sid]


def _lists(nodes: NodeMap, usages: list[Usage], refs: dict[str, Usage | None], mode: str) -> None:
    for usage in usages:
        node, prop, head = usage.node, usage.property, usage.value
        items: list[JsonObject] = []
        removed: list[str] = []
        while (
            prop == REST and node["@id"].startswith("_:")
            and isinstance(refs.get(node["@id"]), Usage)
            and len(node.get(FIRST, [])) == 1 and len(node.get(REST, [])) == 1
            and set(node) <= {"@id", FIRST, REST, "@type"}
            and ("@type" not in node or node["@type"] == [str(RDF.List)])
        ):
            sid = node["@id"]
            if sid in removed:  # Defensive: a terminating singly referenced list cannot cycle.
                break
            items.append(node[FIRST][0])
            removed.append(sid)
            previous = refs[sid]
            assert previous is not None
            node, prop, head = previous.node, previous.property, previous.value
            if not node["@id"].startswith("_:"):
                break
        # JSON-LD 1.0 did not allow lists of lists (manifest t0008).
        if mode == "json-ld-1.0" and prop == FIRST:
            if not removed:
                continue
            head_id = removed.pop()
            items.pop()
            head = nodes[head_id][REST][0]
        head.pop("@id", None)
        head["@list"] = list(reversed(items))
        for sid in removed:
            nodes.pop(sid, None)


def from_rdf(
    dataset: Graph | Dataset | ConjunctiveGraph, *, ordered: bool = False,
    rdf_direction: Direction = None, use_native_types: bool = False,
    use_rdf_type: bool = False, processing_mode: str = "json-ld-1.1",
) -> list[JsonObject]:
    """Serialize RDF as expanded JSON-LD without changing the input dataset.

    Malformed/shared collections retain their RDF structure (possibly with a
    well-formed suffix converted to @list), as required by the W3C algorithm.
    Ordering is stable for fixed RDF blank-node identifiers, not canonicalization.
    """
    if not isinstance(dataset, Graph):
        raise InvalidInputError("from_rdf requires an rdflib Graph, Dataset, or ConjunctiveGraph")
    check_direction(rdf_direction)
    if processing_mode not in ("json-ld-1.0", "json-ld-1.1"):
        raise UnsupportedOptionError(f"Unsupported processing_mode: {processing_mode}")
    maps, refs, nils, compounds = _node_maps(dataset, rdf_direction, use_native_types, use_rdf_type, ordered)
    for name, nodes in maps.items():
        _compound_literals(nodes, compounds[name], refs)
        _lists(nodes, nils[name], refs, processing_mode)
    default = maps["@default"]
    result = []
    for sid in sorted(default) if ordered else default:
        node = default[sid]
        if sid in maps:
            graph = maps[sid]
            node["@graph"] = [graph[k] for k in (sorted(graph) if ordered else graph) if len(graph[k]) > 1]
        if len(node) > 1:
            result.append(node)
    return result


def serialize_rdf(dataset: Graph | Dataset | ConjunctiveGraph, **options: Any) -> str:
    """Return Unicode JSON text for expanded JSON-LD; encode as UTF-8 for files."""
    return json.dumps(from_rdf(dataset, **options), ensure_ascii=False, allow_nan=False, indent=2)
