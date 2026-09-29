"""Allowlisted, deliberately lossy OWL vocabulary projection."""
from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping
from urllib.parse import unquote, urlsplit

from rdflib import ConjunctiveGraph, Dataset, Graph, Literal, OWL, RDF, RDFS, URIRef, XSD

from .core import _graphs, _value
from .errors import InvalidInputError

SCHEMA = "https://schema.org/"
_DATATYPES = {
    **dict.fromkeys(("string", "normalizedString", "token", "language"), "Text"),
    "boolean": "Boolean",
    **dict.fromkeys(("integer", "nonPositiveInteger", "negativeInteger", "long", "int", "short", "byte",
                     "nonNegativeInteger", "unsignedLong", "unsignedInt", "unsignedShort", "unsignedByte",
                     "positiveInteger"), "Integer"),
    **dict.fromkeys(("decimal", "float", "double"), "Number"),
    "date": "Date", "dateTime": "DateTime", "dateTimeStamp": "DateTime", "time": "Time",
    **dict.fromkeys(("duration", "dayTimeDuration", "yearMonthDuration"), "Duration"),
    "anyURI": "URL",
}
PRIMITIVE_DATATYPES: Mapping[str, str] = MappingProxyType(
    {str(XSD) + key: SCHEMA + value for key, value in _DATATYPES.items()}
)


def _context() -> dict[str, Any]:
    return {"@vocab": SCHEMA, "schema": SCHEMA, "rdfs": str(RDFS), "owl": str(OWL), "xsd": str(XSD),
            "domainIncludes": {"@id": SCHEMA + "domainIncludes", "@type": "@id"},
            "rangeIncludes": {"@id": SCHEMA + "rangeIncludes", "@type": "@id"}}


def _fallback(iri: str) -> str:
    try:
        parts = urlsplit(iri)
    except ValueError:
        return iri
    if parts.fragment:
        return unquote(parts.fragment, encoding="utf-8")
    # Opaque IRIs such as urn:example have no hierarchical path segment.
    if parts.netloc or parts.path.startswith("/"):
        segments = [segment for segment in parts.path.split("/") if segment]
        if segments:
            return unquote(segments[-1], encoding="utf-8")
    return iri


def _one_or_many(values: list[Any]) -> Any:
    return values[0] if len(values) == 1 else values


def owl_to_schema_org(graph: Graph, *, ordered: bool = False) -> dict[str, Any]:
    """Project explicitly named OWL terms; omit all non-allowlisted logical axioms.

    A dataset is projected over its union. This mode does not preserve graph
    provenance or OWL semantics; source IRIs and supported labels are retained.
    """
    if not isinstance(graph, Graph):
        raise InvalidInputError("owl_to_schema_org requires an rdflib graph or dataset")
    if isinstance(graph, (Dataset, ConjunctiveGraph)):
        union = Graph()
        for _, context in _graphs(graph):
            for triple in context:
                union.add(triple)
        graph = union
    classes = {s for s in graph.subjects(RDF.type, OWL.Class) if isinstance(s, URIRef)}
    properties = {s for kind in (OWL.ObjectProperty, OWL.DatatypeProperty)
                  for s in graph.subjects(RDF.type, kind) if isinstance(s, URIRef)}
    result: list[dict[str, Any]] = []
    subjects = classes | properties
    for subject in sorted(subjects, key=str) if ordered else subjects:
        kinds = (["Class"] if subject in classes else []) + (["Property"] if subject in properties else [])
        node: dict[str, Any] = {"@id": str(subject), "@type": _one_or_many(kinds)}
        labels: list[Any] = []
        literals = [label for label in graph.objects(subject, RDFS.label) if isinstance(label, Literal)]
        if ordered:
            literals.sort(key=lambda label: (str(label), (label.language or "").lower(), str(label.datatype or "")))
        for label in literals:
            value = _value(label, None, False)
            item = value["@value"] if set(value) == {"@value"} else value
            if item not in labels:
                labels.append(item)
        node["rdfs:label"] = _one_or_many(labels) if labels else _fallback(str(subject))
        predicates = []
        if subject in classes:
            predicates.append((RDFS.subClassOf, "rdfs:subClassOf"))
        if subject in properties:
            predicates.extend(((RDFS.domain, "domainIncludes"), (RDFS.range, "rangeIncludes")))
        for predicate, key in predicates:
            refs = {PRIMITIVE_DATATYPES.get(str(obj), str(obj)) if predicate == RDFS.range else str(obj)
                    for obj in graph.objects(subject, predicate) if isinstance(obj, URIRef)}
            if refs:
                node[key] = _one_or_many([{"@id": iri} for iri in (sorted(refs) if ordered else refs)])
        result.append(node)
    return {"@context": _context(), "@graph": result}
