"""Optional strict collection validation, separate from From RDF serialization."""
from rdflib import BNode, Graph, RDF, URIRef
from rdflib.term import Node

from .errors import MalformedListError


def validate_rdf_list(graph: Graph, head: URIRef | BNode) -> list[Node]:
    """Return list items or raise MalformedListError for broken/cyclic scaffolding.

    Unlike this opt-in validator, from_rdf preserves malformed collection RDF
    rather than rejecting a dataset. Extra properties and shared heads are legal
    RDF and do not by themselves invalidate the collection's first/rest chain.
    """
    items: list[Node] = []
    visited: set[Node] = set()
    node: Node = head
    while node != RDF.nil:
        if not isinstance(node, (URIRef, BNode)) or node in visited:
            raise MalformedListError(f"Cyclic or non-resource list node: {node}", code="malformed RDF list")
        visited.add(node)
        first, rest = list(graph.objects(node, RDF.first)), list(graph.objects(node, RDF.rest))
        if len(first) != 1 or len(rest) != 1:
            raise MalformedListError(f"List node {node} requires exactly one rdf:first and rdf:rest", code="malformed RDF list")
        items.append(first[0])
        node = rest[0]
    return items
