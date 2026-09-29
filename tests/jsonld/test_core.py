"""Focused public API tests; W3C cases are independently parametrized."""
import json

import pytest
from rdflib import BNode, ConjunctiveGraph, Dataset, Graph, Literal, RDF, URIRef, XSD
from rdflib.compare import isomorphic

from gdsn_tsv_transformer.jsonld import (
    InvalidInputError, JsonLdError, UnsupportedOptionError, from_rdf, serialize_rdf, to_rdf,
)
from gdsn_tsv_transformer.jsonld.conformance import discover, normalize, run_case, structural_difference
from gdsn_tsv_transformer.jsonld.parsing import parse_rdf

S, P, O = map(URIRef, ("urn:s", "urn:p", "urn:o"))


def graph_with(value):
    return Graph().add((S, P, value))


@pytest.mark.parametrize("entry", discover(offline=True), ids=lambda e: e["@id"])
def test_w3c(entry):
    outcome = run_case(entry, offline=True)
    assert outcome.status == "passed", f"{outcome.identifier}\n{outcome.detail}"


def test_nodes_duplicates_and_type():
    g = graph_with(O).add((S, P, O)).add((S, RDF.type, O)).add((BNode("a"), P, S))
    assert from_rdf(g, ordered=True) == [
        {"@id": "_:a", "urn:p": [{"@id": "urn:s"}]},
        {"@id": "urn:s", "urn:p": [{"@id": "urn:o"}], "@type": ["urn:o"]},
    ]
    assert str(RDF.type) in from_rdf(g, use_rdf_type=True, ordered=True)[1]


@pytest.mark.parametrize("lexical,datatype,native,expected", [
    ("hello", None, False, {"@value": "hello"}),
    ("hello", XSD.string, False, {"@value": "hello"}),
    ("001", XSD.integer, False, {"@value": "001", "@type": str(XSD.integer)}),
    ("001", XSD.integer, True, {"@value": 1}),
    ("false", XSD.boolean, True, {"@value": False}),
    ("1", XSD.boolean, True, {"@value": True}),
    ("0", XSD.boolean, True, {"@value": False}),
    ("2.50E+1", XSD.double, True, {"@value": 25.0}),
    ("INF", XSD.double, True, {"@value": "INF", "@type": str(XSD.double)}),
    ("NaN", XSD.double, True, {"@value": "NaN", "@type": str(XSD.double)}),
    ("wrong", XSD.integer, True, {"@value": "wrong", "@type": str(XSD.integer)}),
    ("1.0", XSD.decimal, True, {"@value": "1.0", "@type": str(XSD.decimal)}),
    ("true", URIRef("urn:custom"), True, {"@value": "true", "@type": "urn:custom"}),
])
def test_literals(lexical, datatype, native, expected):
    g = graph_with(Literal(lexical, datatype=datatype, normalize=False))
    assert from_rdf(g, use_native_types=native)[0][str(P)] == [expected]


def test_language_case_and_boolean_number_dedup():
    g = graph_with(Literal("hello", lang="EN")).add((S, P, Literal("hello", lang="en")))
    assert from_rdf(g)[0][str(P)] == [{"@value": "hello", "@language": "en"}]
    g = graph_with(Literal("true", datatype=XSD.boolean)).add((S, P, Literal(1)))
    assert len(from_rdf(g, use_native_types=True)[0][str(P)]) == 2


@pytest.mark.parametrize("value", [None, True, False, 1, 1.2, "hello", [1, 2], {"key": [2, 1]}])
def test_json_literals(value):
    g = graph_with(Literal(json.dumps(value), datatype=RDF.JSON, normalize=False))
    assert from_rdf(g)[0][str(P)] == [{"@value": value, "@type": "@json"}]


@pytest.mark.parametrize("lexical", ["undefined", "{", "NaN", "Infinity", "[1,]"])
def test_invalid_json_literal(lexical):
    with pytest.raises(JsonLdError) as error:
        from_rdf(graph_with(Literal(lexical, datatype=RDF.JSON, normalize=False)))
    assert error.value.code == "invalid JSON literal"


def test_named_graph_round_trip():
    d = Dataset()
    d.default_graph.add((S, P, O))
    d.graph(URIRef("urn:g")).add((S, P, Literal("named")))
    d.graph(BNode("graph")).add((O, P, Literal("blank graph")))
    doc = from_rdf(d, ordered=True)
    parsed = to_rdf(doc)
    assert isinstance(parsed, Dataset)
    assert set(parsed.default_graph) == set(d.default_graph)
    assert set(parsed.graph(URIRef("urn:g"))) == set(d.graph(URIRef("urn:g")))
    assert len(list(parsed.quads())) == 3
    assert any(isinstance(g.identifier, BNode) for g in parsed.graphs())


def test_conjunctive_graph_input():
    graph = ConjunctiveGraph()
    graph.default_context.add((S, P, O))
    graph.get_context(URIRef("urn:g")).add((O, P, S))
    result = from_rdf(graph, ordered=True)
    assert result == [{"@id": "urn:g", "@graph": [{"@id": "urn:o", "urn:p": [{"@id": "urn:s"}]}]},
                      {"@id": "urn:s", "urn:p": [{"@id": "urn:o"}]}]


@pytest.mark.parametrize("mode", ["i18n-datatype", "compound-literal"])
@pytest.mark.parametrize("named", [False, True])
def test_direction_round_trip(mode, named):
    node = {"@id": "urn:s", "urn:p": [{"@value": "مرحبا", "@language": "ar", "@direction": "rtl"}]}
    doc = [{"@id": "urn:g", "@graph": [node]}] if named else [node]
    assert from_rdf(to_rdf(doc, rdf_direction=mode), rdf_direction=mode) == doc


def test_direction_context_gap_explicit():
    with pytest.raises(UnsupportedOptionError, match="context-level|Context-level"):
        to_rdf({"@context": {"@direction": "rtl", "@vocab": "urn:"}, "name": "hello"})


def test_base_context_and_plain_graph():
    graph = to_rdf({"@id": "person", "name": "Jane"}, base="https://example.org/", context={"name": "urn:name"})
    assert not isinstance(graph, Dataset)
    assert (URIRef("https://example.org/person"), URIRef("urn:name"), Literal("Jane")) in graph


@pytest.mark.parametrize("doc", ["hello", 1, [{"@id": 123}], {"@value": [], "@type": "urn:t"}, {"@value": 1, "@language": "en"}])
def test_invalid_document(doc):
    with pytest.raises(InvalidInputError):
        to_rdf(doc)


def test_invalid_options():
    with pytest.raises(InvalidInputError):
        from_rdf("wrong")
    with pytest.raises(UnsupportedOptionError):
        from_rdf(Graph(), rdf_direction="wrong")
    with pytest.raises(UnsupportedOptionError):
        to_rdf({}, rdf_direction="wrong")
    with pytest.raises(UnsupportedOptionError):
        from_rdf(Graph(), processing_mode="wrong")


def test_ordered_stable_and_list_order_preserved():
    triples = [(S, P, Literal(x)) for x in ("z", "a", "b")]
    a, b = Graph(), Graph()
    for t in triples:
        a.add(t)
    for t in reversed(triples):
        b.add(t)
    assert serialize_rdf(a, ordered=True) == serialize_rdf(b, ordered=True)
    doc = [{"@id": "urn:s", "urn:p": [{"@list": [{"@value": "z"}, {"@value": "a"}]}]}]
    assert from_rdf(to_rdf(doc), ordered=True) == doc


def test_lexical_preservation_and_global_restore():
    import rdflib
    original = rdflib.NORMALIZE_LITERALS
    parsed = parse_rdf('<urn:s> <urn:p> "001"^^<http://www.w3.org/2001/XMLSchema#integer> .', format="nquads")
    assert from_rdf(parsed)[0][str(P)][0]["@value"] == "001"
    assert rdflib.NORMALIZE_LITERALS is original
    with pytest.raises(InvalidInputError):
        parse_rdf("not RDF", format="turtle")
    assert rdflib.NORMALIZE_LITERALS is original


def test_comparison_rules():
    assert normalize({"urn:p": [{"@value": "a"}, {"@value": "b"}]}) == normalize({"urn:p": [{"@value": "b"}, {"@value": "a"}]})
    assert structural_difference({"@list": [1, 2]}, {"@list": [2, 1]})
    assert structural_difference({"@type": "@json", "@value": [1, 2]}, {"@type": "@json", "@value": [2, 1]})
    assert not structural_difference({"@language": "EN"}, {"@language": "en"})
    assert structural_difference({"@value": True}, {"@value": 1})


@pytest.mark.parametrize("case", ["0004", "0010", "0011", "0012", "0013", "0014", "0015", "0020", "0021", "li01", "li02"])
def test_list_regression_roundtrip(case):
    # W3C cases cover valid/broken/cyclic/shared lists, extra properties, and
    # cross-graph references; compare RDF structure independently of JSON order.
    from gdsn_tsv_transformer.jsonld.conformance import DEFAULT_MANIFEST, read_resource, resolve
    source = read_resource(resolve(DEFAULT_MANIFEST, f"fromRdf/{case}-in.nq"), offline=True)
    g = parse_rdf(source, format="nquads")
    doc = from_rdf(g)
    roundtrip = to_rdf(doc)
    # Dataset-wide isomorphism via RDFLib's TriG parse preserves blank-node scope.
    def union(dataset):
        result = Graph()
        for _, _, _, context in dataset.quads():
            for triple in dataset.graph(context):
                result.add(triple)
        return result
    actual = union(roundtrip) if isinstance(roundtrip, Dataset) else roundtrip
    assert isomorphic(union(g), actual)


def test_strict_list_validation():
    from gdsn_tsv_transformer.jsonld import MalformedListError, validate_rdf_list
    node = BNode("list")
    g = Graph().add((node, RDF.first, Literal("item"))).add((node, RDF.rest, RDF.nil))
    assert validate_rdf_list(g, node) == [Literal("item")]
    assert validate_rdf_list(g, RDF.nil) == []
    g.set((node, RDF.rest, node))
    with pytest.raises(MalformedListError, match="Cyclic"):
        validate_rdf_list(g, node)
    g.remove((node, RDF.rest, node))
    with pytest.raises(MalformedListError, match="exactly one"):
        validate_rdf_list(g, node)


def test_generalized_rdf():
    doc = [{"@id": "urn:s", "_:predicate": [{"@id": "urn:o"}]}]
    assert len(to_rdf(doc)) == 0
    g = to_rdf(doc, generalized_rdf=True)
    assert len(g) == 1
    assert isinstance(next(iter(g))[1], BNode)


def test_json_content_not_rewritten():
    content = {"@value": "literal", "@direction": "rtl"}
    doc = [{"@id": "urn:s", "urn:p": [{"@value": content, "@type": "@json"}]}]
    assert from_rdf(to_rdf(doc, rdf_direction="compound-literal")) == doc


def test_compound_invalid_language_and_direction():
    for predicate, lexical, expected in [("language", "bad_tag!", "invalid language-tagged string"),
                                          ("direction", "up", "invalid base direction")]:
        g = Graph().add((S, P, BNode("cl")))
        g.add((BNode("cl"), RDF.value, Literal("text")))
        g.add((BNode("cl"), URIRef(str(RDF) + "direction"), Literal("rtl")))
        g.set((BNode("cl"), URIRef(str(RDF) + predicate), Literal(lexical)))
        with pytest.raises(JsonLdError) as exc:
            from_rdf(g, rdf_direction="compound-literal")
        assert exc.value.code == expected


def test_numeric_equivalence_and_empty_named_graph():
    g = graph_with(Literal('1', datatype=XSD.integer, normalize=False))
    g.add((S, P, Literal('1.0', datatype=XSD.double, normalize=False)))
    assert len(from_rdf(g, use_native_types=True)[0][str(P)]) == 1
    assert not structural_difference({"@value": 1}, {"@value": 1.0})
    d = Dataset()
    d.graph(URIRef("urn:empty"))
    assert from_rdf(d) == [{"@id": "urn:empty", "@graph": []}]


def test_empty_named_graph_preserved_with_context_aliases():
    doc = {"@context": {"id": "@id", "graph": "@graph", "ex": "https://example.org/"},
           "id": "ex:empty", "graph": []}
    dataset = to_rdf(doc)
    assert isinstance(dataset, Dataset)
    assert from_rdf(dataset) == [{"@id": "https://example.org/empty", "@graph": []}]
