"""Explicit, verified identity rewriting for labelled RDF vocabularies."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
import re
from typing import Any
from urllib.parse import urlsplit

from rdflib import ConjunctiveGraph, Dataset, Graph, Literal, RDFS, URIRef, XSD

from .errors import JsonLdError, UnsupportedOptionError

_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


class LabelVerificationError(JsonLdError):
    """Label identifiers cannot be assigned without ambiguity or data loss."""

    def __init__(self, issues: list[str]) -> None:
        self.issues = tuple(issues)
        super().__init__("Label verification failed:\n" + "\n".join(issues), code="invalid label identifiers")


def verify_label_ids(graph: Graph, *, prefixes: Mapping[str, str]) -> dict[str, str]:
    """Return original-to-compact IDs, or report all label issues without mutation.

    Only explicitly selected namespaces are rewritten. Labels must be unique
    per namespace and match ASCII [A-Za-z_][A-Za-z0-9_]* exactly.
    """
    if not prefixes:
        raise UnsupportedOptionError("Label rewriting requires at least one prefix mapping")
    for prefix, namespace in prefixes.items():
        if (not _NAME.fullmatch(prefix) or prefix in {"http", "https", "urn", "rdf", "rdfs", "owl", "xsd", "schema"}
                or not urlsplit(namespace).scheme or not namespace.endswith(("/", "#", ":"))):
            raise UnsupportedOptionError(f"Invalid label prefix mapping: {prefix}={namespace}; use a nonreserved prefix and absolute namespace ending in /, #, or :")
    if len(set(prefixes.values())) != len(prefixes):
        raise UnsupportedOptionError("Each label namespace must have exactly one prefix")
    graphs = list(graph.graphs()) if isinstance(graph, (Dataset, ConjunctiveGraph)) else [graph]
    identifiers: set[str] = set()
    labels: dict[str, set[Any]] = defaultdict(set)
    for context in graphs:
        if isinstance(graph, (Dataset, ConjunctiveGraph)) and context.identifier != (graph.default_graph.identifier if isinstance(graph, Dataset) else graph.default_context.identifier):
            if isinstance(context.identifier, URIRef):
                identifiers.add(str(context.identifier))
        for subject, predicate, obj in context:
            identifiers.update(str(term) for term in (subject, predicate, obj) if isinstance(term, URIRef))
            if isinstance(obj, Literal) and obj.datatype:
                identifiers.add(str(obj.datatype))
            if predicate == RDFS.label and isinstance(subject, URIRef):
                labels[str(subject)].add(obj)
    issues: list[str] = []
    for iri in sorted(identifiers):
        if any(iri.startswith(prefix + ":") for prefix in prefixes):
            issues.append(f"{iri}: prefix would reinterpret an existing absolute IRI")
    mapping: dict[str, str] = {}
    targets: dict[str, list[str]] = defaultdict(list)
    namespaces = sorted(prefixes.items(), key=lambda pair: -len(pair[1]))
    for iri in sorted(identifiers):
        match = next(((p, ns) for p, ns in namespaces if iri.startswith(ns) and iri != ns), None)
        if match is None:
            continue
        prefix, namespace = match
        values = labels[iri]
        if not values:
            issues.append(f"{iri}: missing rdfs:label")
            continue
        languages = {(value.language or '').lower() for value in values if isinstance(value, Literal)}
        if len(languages) > 1:
            issues.append(f"{iri}: multiple label languages {sorted(languages)!r}")
        if len(values) != 1:
            issues.append(f"{iri}: multiple labels {sorted(map(str, values))!r}")
            continue
        value = next(iter(values))
        if not isinstance(value, Literal) or value.datatype not in (None, XSD.string) and not value.language:
            issues.append(f"{iri}: label must be a plain, string, or language-tagged literal")
            continue
        if not _NAME.fullmatch(str(value)):
            issues.append(f"{iri}: unsuitable label {str(value)!r}; expected [A-Za-z_][A-Za-z0-9_]*")
            continue
        target = namespace + str(value)
        targets[target].append(iri)
        mapping[iri] = f"{prefix}:{value}"
        if target in identifiers and target != iri:
            issues.append(f"{iri}: target {target} already exists in the input")
    for target, sources in sorted(targets.items()):
        if len(sources) > 1:
            issues.append(f"{target}: duplicate label identifier for {', '.join(sources)}")
    if issues:
        raise LabelVerificationError(issues)
    if not mapping:
        raise LabelVerificationError(["No identifiers matched the selected namespaces"])
    return mapping


def rewrite_label_ids(document: Any, graph: Graph, *, prefixes: Mapping[str, str]) -> dict[str, Any]:
    """Verify labels and rewrite IDs, types and predicates in generated JSON-LD.

    Preserves literal payloads, graph structure, and external IRIs. The source
    RDF graph and JSON-LD document are not mutated. This changes RDF identity.
    """
    mapping = verify_label_ids(graph, prefixes=prefixes)

    def identifier(value: Any) -> Any:
        if isinstance(value, list):
            return [identifier(item) for item in value]
        return mapping.get(value, value) if isinstance(value, str) else value

    def visit(value: Any) -> Any:
        if isinstance(value, list):
            return [visit(item) for item in value]
        if not isinstance(value, dict):
            return value
        return {mapping.get(key, key): (item if key in {"@value", "@context"} else
                identifier(item) if key in {"@id", "@type"} else visit(item))
                for key, item in value.items()}

    result = visit(document)
    context = {prefix: {"@id": namespace, "@prefix": True} for prefix, namespace in prefixes.items()}
    if isinstance(result, list):
        return {"@context": context, "@graph": result}
    existing = result.get("@context", {})
    if not isinstance(existing, dict) or set(existing) & set(context):
        raise UnsupportedOptionError("Label prefixes conflict with the output context")
    return {**result, "@context": {**existing, **context}}
