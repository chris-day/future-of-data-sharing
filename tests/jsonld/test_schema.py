import json

import pytest
from rdflib import BNode, Graph, Literal, OWL, RDF, RDFS, URIRef, XSD

from gdsn_tsv_transformer.jsonld import PRIMITIVE_DATATYPES, from_rdf, owl_to_schema_org, to_rdf

EX = "https://example.com/vocab/"
BOOK, TITLE = URIRef(EX + "Book"), URIRef(EX + "title")


def test_envelope_and_classes_properties():
    g = Graph().add((BOOK, RDF.type, OWL.Class)).add((TITLE, RDF.type, OWL.ObjectProperty))
    g.add((TITLE, RDF.type, OWL.DatatypeProperty))
    g.add((TITLE, RDFS.domain, BOOK)).add((TITLE, RDFS.range, XSD.string))
    doc = owl_to_schema_org(g, ordered=True)
    assert doc["@context"] == {
        "@vocab": "https://schema.org/", "schema": "https://schema.org/", "rdfs": str(RDFS), "owl": str(OWL), "xsd": str(XSD),
        "domainIncludes": {"@id": "https://schema.org/domainIncludes", "@type": "@id"},
        "rangeIncludes": {"@id": "https://schema.org/rangeIncludes", "@type": "@id"},
    }
    assert set(doc) == {"@context", "@graph"}
    assert doc["@graph"] == [
        {"@id": str(BOOK), "@type": "Class", "rdfs:label": "Book"},
        {"@id": str(TITLE), "@type": "Property", "rdfs:label": "title", "domainIncludes": {"@id": str(BOOK)},
         "rangeIncludes": {"@id": "https://schema.org/Text"}},
    ]
    assert len(to_rdf(doc)) > 0


EXPECTED_PRIMITIVES = {
    "string": "Text", "normalizedString": "Text", "token": "Text", "language": "Text",
    "boolean": "Boolean", "integer": "Integer", "nonPositiveInteger": "Integer",
    "negativeInteger": "Integer", "long": "Integer", "int": "Integer", "short": "Integer",
    "byte": "Integer", "nonNegativeInteger": "Integer", "unsignedLong": "Integer",
    "unsignedInt": "Integer", "unsignedShort": "Integer", "unsignedByte": "Integer",
    "positiveInteger": "Integer", "decimal": "Number", "float": "Number", "double": "Number",
    "date": "Date", "dateTime": "DateTime", "dateTimeStamp": "DateTime", "time": "Time",
    "duration": "Duration", "dayTimeDuration": "Duration", "yearMonthDuration": "Duration",
    "anyURI": "URL",
}


@pytest.mark.parametrize("datatype,expected", [
    (str(XSD) + key, "https://schema.org/" + value) for key, value in EXPECTED_PRIMITIVES.items()
])
def test_primitive_mapping(datatype, expected):
    graph = Graph().add((TITLE, RDF.type, OWL.DatatypeProperty)).add((TITLE, RDFS.range, URIRef(datatype)))
    assert owl_to_schema_org(graph)["@graph"][0]["rangeIncludes"] == {"@id": expected}


def test_mapping_immutable_and_unknown():
    assert dict(PRIMITIVE_DATATYPES) == {str(XSD) + k: "https://schema.org/" + v for k, v in EXPECTED_PRIMITIVES.items()}
    with pytest.raises(TypeError):
        PRIMITIVE_DATATYPES["urn:custom"] = "wrong"
    g = Graph().add((TITLE, RDF.type, OWL.DatatypeProperty)).add((TITLE, RDFS.range, URIRef("urn:custom")))
    assert owl_to_schema_org(g)["@graph"][0]["rangeIncludes"] == {"@id": "urn:custom"}


def test_multiple_sorted_and_deduplicated():
    g = Graph().add((BOOK, RDF.type, OWL.Class)).add((TITLE, RDF.type, OWL.ObjectProperty))
    for iri in ("urn:z", "urn:a", "urn:z"):
        g.add((BOOK, RDFS.subClassOf, URIRef(iri)))
        g.add((TITLE, RDFS.domain, URIRef(iri)))
        g.add((TITLE, RDFS.range, URIRef(iri)))
    doc = owl_to_schema_org(g, ordered=True)
    refs = [{"@id": "urn:a"}, {"@id": "urn:z"}]
    assert doc["@graph"][0]["rdfs:subClassOf"] == refs
    assert doc["@graph"][1]["domainIncludes"] == refs
    assert doc["@graph"][1]["rangeIncludes"] == refs
    other = Graph()
    for triple in reversed(list(g)):
        other.add(triple)
    assert json.dumps(doc) == json.dumps(owl_to_schema_org(other, ordered=True))


def test_labels():
    g = Graph().add((BOOK, RDF.type, OWL.Class))
    g.add((BOOK, RDFS.label, Literal("Book")))
    assert owl_to_schema_org(g)["@graph"][0]["rdfs:label"] == "Book"
    g.add((BOOK, RDFS.label, Literal("Livre", lang="FR")))
    assert owl_to_schema_org(g, ordered=True)["@graph"][0]["rdfs:label"] == ["Book", {"@value": "Livre", "@language": "fr"}]


@pytest.mark.parametrize("iri,label", [("https://example.org/#A%20Book", "A Book"),
    ("https://example.org/a/Caf%C3%A9/", "Café"), ("https://example.org", "https://example.org"),
    ("urn:example", "urn:example")])
def test_fallback(iri, label):
    g = Graph().add((URIRef(iri), RDF.type, OWL.Class))
    assert owl_to_schema_org(g)["@graph"][0]["rdfs:label"] == label


def test_no_logical_axioms_or_blank_nodes():
    g = Graph().add((BOOK, RDF.type, OWL.Class)).add((TITLE, RDF.type, OWL.ObjectProperty))
    b = BNode("restriction")
    for kind in (OWL.Class, OWL.Restriction, OWL.ObjectProperty):
        g.add((b, RDF.type, kind))
    for predicate in (OWL.unionOf, OWL.intersectionOf, OWL.complementOf, OWL.inverseOf,
                      OWL.cardinality, OWL.qualifiedCardinality, OWL.equivalentClass, OWL.equivalentProperty,
                      OWL.propertyChainAxiom, OWL.disjointWith, OWL.hasKey, RDFS.subClassOf, RDFS.domain, RDFS.range):
        g.add((BOOK, predicate, b)).add((TITLE, predicate, b))
    g.add((b, RDF.first, BOOK)).add((b, RDF.rest, RDF.nil))
    normal = from_rdf(g, ordered=True)
    doc = owl_to_schema_org(g, ordered=True)
    assert all(set(node) == {"@id", "@type", "rdfs:label"} for node in doc["@graph"])
    assert "_:" not in json.dumps(doc)
    assert len(doc["@graph"]) == 2
    assert from_rdf(g, ordered=True) == normal
