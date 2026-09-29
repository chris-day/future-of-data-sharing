"""RDFLib parsing adapters and explicit JSON-LD compatibility boundaries."""
from __future__ import annotations

from contextlib import contextmanager
import json
import logging
import warnings
from threading import RLock
from typing import Any, Iterator

import rdflib
from rdflib import BNode, Dataset, Graph, Literal, RDF, URIRef
from rdflib.plugins.parsers.jsonld import Parser as JsonLdParser
from rdflib.plugins.shared.jsonld.context import Context

from .core import Direction, I18N, _check_language, check_direction
from .errors import InvalidInputError, JsonLdError, UnsupportedOptionError

_LITERAL_LOCK = RLock()


class _LiteralDiagnostics(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # RDFLib logs a traceback for valid RDF with an ill-typed literal.
        # Keep lexical forms without emitting misleading parse failures.
        return not record.getMessage().startswith("Failed to convert Literal lexical form")


@contextmanager
def preserve_lexical_forms() -> Iterator[None]:
    """Scope RDFLib's normalization switch; serialize this package's parsers."""
    with _LITERAL_LOCK:
        previous = rdflib.NORMALIZE_LITERALS
        rdflib.NORMALIZE_LITERALS = False
        diagnostic_filter = _LiteralDiagnostics()
        logger = logging.getLogger("rdflib.term")
        logger.addFilter(diagnostic_filter)
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Parsing weird boolean", category=UserWarning)
                yield
        finally:
            logger.removeFilter(diagnostic_filter)
            rdflib.NORMALIZE_LITERALS = previous


class _BlankLabels(dict[str, BNode]):
    def get(self, key: str, default: Any = None) -> BNode:
        return self.setdefault(key, BNode(key))


def parse_rdf(data: str, *, format: str, base: str | None = None) -> Dataset:
    """Parse RDF text with RDFLib, retaining literal lexical forms and N-Quads labels."""
    result = Dataset()
    kwargs: dict[str, Any] = {}
    if format in ("nquads", "n-quads", "nt", "ntriples", "nt11"):
        kwargs["bnode_context"] = _BlankLabels()
    try:
        with preserve_lexical_forms():
            result.parse(data=data, format=format, publicID=base, **kwargs)
    except Exception as exc:
        raise InvalidInputError(f"Invalid {format} RDF: {exc}") from exc
    return result


def _prepare_direction(document: Any, mode: Direction, compounds: dict[str, dict[str, Any]]) -> Any:
    if isinstance(document, list):
        return [_prepare_direction(item, mode, compounds) for item in document]
    if not isinstance(document, dict):
        return document
    if "@context" in document and "@direction" in json.dumps(document["@context"]):
        raise UnsupportedOptionError(
            "RDFLib does not implement context-level @direction; supply expanded value objects with @direction"
        )
    if document.get("@type") == "@json":
        return document
    if "@direction" in document and "@value" in document:
        direction = document["@direction"]
        if direction not in ("ltr", "rtl"):
            raise JsonLdError(f"Invalid base direction: {direction!r}", code="invalid base direction")
        if not isinstance(document["@value"], str) or "@type" in document:
            raise InvalidInputError("A direction-aware value must be a string without @type")
        language = document.get("@language", "")
        if language:
            _check_language(language)
        if mode == "i18n-datatype":
            return {"@value": document["@value"], "@type": I18N + language.lower() + "_" + direction}
        if mode == "compound-literal":
            # A unique datatype marker lets RDFLib handle all graph/context placement;
            # replace its literal objects with compound nodes only after parsing.
            marker = "urn:owl-jsonld:direction:" + str(BNode())
            compounds[marker] = document
            return {"@value": document["@value"], "@type": marker}
        return {k: v for k, v in document.items() if k != "@direction"}
    return {key: _prepare_direction(value, mode, compounds) if key != "@context" else value
            for key, value in document.items()}


def _validate_document(value: Any) -> None:
    if not isinstance(value, (dict, list)):
        raise InvalidInputError("A JSON-LD document must be an object or array")
    if isinstance(value, list):
        for item in value:
            _validate_document(item)
        return
    if "@id" in value and not isinstance(value["@id"], str):
        raise InvalidInputError("@id must be a string")
    if "@value" in value:
        datatype = value.get("@type")
        if datatype != "@json" and isinstance(value["@value"], (dict, list)):
            raise InvalidInputError("Object/array @value requires @type: @json")
        if "@language" in value:
            if not isinstance(value["@language"], str) or not isinstance(value["@value"], str):
                raise InvalidInputError("Language-tagged values require strings")
            _check_language(value["@language"])
        if "@language" in value and datatype is not None:
            raise InvalidInputError("A value cannot have both @language and @type")
        return  # @json contents are ordinary JSON, not JSON-LD.
    for key, item in value.items():
        if key == "@context":
            continue
        if isinstance(item, dict):
            _validate_document(item)
        elif isinstance(item, list):
            for child in item:
                if isinstance(child, (dict, list)):
                    _validate_document(child)


class _ParsingDataset(Dataset):
    """Retain graph declarations even when RDFLib adds no triples to them."""

    def get_context(self, identifier: URIRef | BNode | str | None,
                    quoted: bool = False, base: str | None = None) -> Graph:
        graph = super().get_context(identifier, quoted=quoted, base=base)
        self.store.add_graph(graph)
        return graph


def to_rdf(
    document: Any, *, base: str | None = None, context: Any | None = None,
    rdf_direction: Direction = None, generalized_rdf: bool = False,
) -> Graph | Dataset:
    """Parse a JSON value through RDFLib, returning a graph or a named-graph dataset.

    Direction modes support expanded value objects. Context-level directions
    are rejected rather than silently lost by RDFLib. Remote contexts may be
    fetched by RDFLib; this API is not a network sandbox.
    """
    check_direction(rdf_direction)
    _validate_document(document)
    if context is not None and "@direction" in json.dumps(context):
        raise UnsupportedOptionError("Context-level @direction is not supported; use expanded values")
    compounds: dict[str, dict[str, Any]] = {}
    try:
        prepared = _prepare_direction(document, rdf_direction, compounds)
        json.dumps(prepared, ensure_ascii=False, allow_nan=False)
        result = _ParsingDataset()
        with preserve_lexical_forms():
            active_context = Context(base=base, version=1.1)
            if context:
                context_base = base or (context if isinstance(context, str) else None)
                active_context.load(context, base=context_base)
            JsonLdParser(generalized_rdf=generalized_rdf).parse(prepared, active_context, result)
        for graph in list(result.graphs()):
            for s, p, o in list(graph):
                if isinstance(o, Literal) and str(o.datatype) in compounds:
                    value = compounds[str(o.datatype)]
                    node = BNode()
                    graph.remove((s, p, o))
                    graph.add((s, p, node))
                    graph.add((node, RDF.value, Literal(value["@value"], normalize=False)))
                    graph.add((node, URIRef(str(RDF) + "direction"), Literal(value["@direction"])))
                    if value.get("@language"):
                        graph.add((node, URIRef(str(RDF) + "language"), Literal(value["@language"].lower())))
    except JsonLdError:
        raise
    except Exception as exc:
        raise JsonLdError(f"JSON-LD parsing failed: {exc}") from exc
    if any(g.identifier != result.default_graph.identifier for g in result.graphs()):
        return result
    return result.default_graph
