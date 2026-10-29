import json

import pytest
from rdflib import Dataset, Graph, Literal, RDF, RDFS, URIRef

from gdsn_tsv_transformer.jsonld import (
    LabelVerificationError, from_rdf, rewrite_label_ids, verify_label_ids,
)
from gdsn_tsv_transformer.jsonld.cli import main

NS = 'https://example.org/gdsn/'
PREFIXES = {'gdsn': NS}
A, P, C = (URIRef(NS + value) for value in ('001', '002', '003'))


def vocabulary():
    graph = Graph()
    for term, label in ((A, 'TradeItem'), (P, 'hasType'), (C, 'Category')):
        graph.add((term, RDFS.label, Literal(label, lang='en')))
    graph.add((A, P, C))
    graph.add((A, RDF.type, C))
    return graph


def test_rewrite_preserves_references_and_literal_payloads():
    graph = vocabulary()
    graph.add((A, URIRef('urn:literal'), Literal(str(A))))
    graph.add((A, URIRef('urn:json'), Literal(json.dumps({'@id': str(A)}), datatype=RDF.JSON)))
    original = from_rdf(graph, ordered=True)
    result = rewrite_label_ids(original, graph, prefixes=PREFIXES)
    assert original == from_rdf(graph, ordered=True)
    node = next(n for n in result['@graph'] if n['@id'] == 'gdsn:TradeItem')
    assert node['@type'] == ['gdsn:Category']
    assert node['gdsn:hasType'] == [{'@id': 'gdsn:Category'}]
    assert node['urn:literal'] == [{'@value': str(A)}]
    assert node['urn:json'][0]['@value'] == {'@id': str(A)}
    parsed = Graph().parse(data=json.dumps(result), format='json-ld')
    assert (URIRef(NS + 'TradeItem'), URIRef(NS + 'hasType'), URIRef(NS + 'Category')) in parsed


@pytest.mark.parametrize('labels,expected', [
    ([], 'missing'), ([Literal('A'), Literal('B')], 'multiple labels'),
    ([Literal('A', lang='en'), Literal('A', lang='fr')], 'multiple label languages'),
    ([Literal('Trade item')], 'unsuitable'), ([Literal('123')], 'unsuitable'),
    ([Literal('A/B')], 'unsuitable'), ([Literal('Étiquette')], 'unsuitable'),
    ([URIRef('urn:label')], 'label must be'),
])
def test_verification_errors(labels, expected):
    graph = Graph()
    graph.add((A, RDF.type, URIRef('urn:Class')))
    for label in labels:
        graph.add((A, RDFS.label, label))
    with pytest.raises(LabelVerificationError, match=expected):
        verify_label_ids(graph, prefixes=PREFIXES)


def test_duplicates_and_existing_target():
    graph = vocabulary()
    graph.add((URIRef(NS + 'other'), RDFS.label, Literal('TradeItem')))
    graph.add((URIRef(NS + 'TradeItem'), RDFS.label, Literal('Existing')))
    with pytest.raises(LabelVerificationError) as error:
        verify_label_ids(graph, prefixes=PREFIXES)
    assert 'duplicate label' in str(error.value)
    assert 'already exists' in str(error.value)


def test_named_graph_and_same_labels_across_namespaces():
    dataset = Dataset()
    for triple in vocabulary():
        dataset.graph(C).add(triple)
    other = URIRef('https://example.org/gpc/1')
    dataset.default_graph.add((other, RDFS.label, Literal('TradeItem')))
    result = rewrite_label_ids(from_rdf(dataset), dataset,
                               prefixes={**PREFIXES, 'gpc': 'https://example.org/gpc/'})
    assert any(node['@id'] == 'gdsn:Category' and '@graph' in node for node in result['@graph'])
    assert any(node['@id'] == 'gpc:TradeItem' for node in result['@graph'])
    parsed = Dataset().parse(data=json.dumps(result), format='json-ld')
    assert len(parsed.graph(URIRef(NS + 'Category'))) == len(vocabulary())


def test_cli_verification_conversion_and_no_output_on_failure(tmp_path, capsys):
    source, output = tmp_path / 'vocab.ttl', tmp_path / 'out.jsonld'
    graph = vocabulary()
    graph.serialize(source, format='turtle')
    options = ['--label-ids', '--label-prefix', 'gdsn=' + NS]
    assert main(['validate', str(source), *options]) == 0
    assert not capsys.readouterr().out
    for command in (['rdf-to-jsonld', str(source), '-o', str(output)],
                    ['convert', str(source), str(output), '--schema-org']):
        assert main([*command, *options, '--force']) == 0
        assert '@context' in json.loads(output.read_text())
    graph.add((A, RDFS.label, Literal('Ambiguous')))
    graph.serialize(source, format='turtle')
    before = output.read_text()
    assert main(['rdf-to-jsonld', str(source), '-o', str(output), '--force', *options]) == 1
    assert output.read_text() == before
    assert 'multiple labels' in capsys.readouterr().err


@pytest.mark.parametrize('options', [ ['--label-ids'], ['--label-prefix', 'gdsn=' + NS],
    ['--label-ids', '--label-prefix', 'invalid'],
    ['--label-ids', '--label-prefix', 'gdsn=' + NS, '--label-prefix', 'gdsn=' + NS]])
def test_cli_invalid_options(options):
    assert main(['rdf-to-jsonld', 'unused.ttl', *options]) == 2


def test_existing_compact_looking_iri_rejected():
    graph = vocabulary()
    graph.add((A, URIRef('urn:reference'), URIRef('gdsn:Unrelated')))
    with pytest.raises(LabelVerificationError, match='reinterpret'):
        verify_label_ids(graph, prefixes=PREFIXES)


def test_schema_projection_label_rewrite():
    from rdflib import OWL
    from gdsn_tsv_transformer.jsonld import owl_to_schema_org
    graph = vocabulary()
    graph.add((A, RDF.type, OWL.Class))
    graph.add((C, RDF.type, OWL.Class))
    graph.add((A, RDFS.subClassOf, C))
    result = rewrite_label_ids(owl_to_schema_org(graph), graph, prefixes=PREFIXES)
    node = next(n for n in result['@graph'] if n['@id'] == 'gdsn:TradeItem')
    assert node['rdfs:subClassOf'] == {'@id': 'gdsn:Category'}
    assert result['@context']['@vocab'] == 'https://schema.org/'
    assert len(Graph().parse(data=json.dumps(result), format='json-ld')) > 0


def test_no_match_and_selected_object_without_label():
    with pytest.raises(LabelVerificationError, match='No identifiers matched'):
        verify_label_ids(Graph(), prefixes=PREFIXES)
    graph = vocabulary()
    graph.add((A, P, URIRef(NS + 'missing')))
    with pytest.raises(LabelVerificationError, match='missing rdfs:label'):
        verify_label_ids(graph, prefixes=PREFIXES)


def test_verification_suggests_executable_quoted_command(tmp_path, capsys):
    import shlex
    source = tmp_path / "vocab 'with spaces;$.ttl"
    vocabulary().serialize(source, format='turtle')
    args = ['validate', str(source), '--input-format', 'turtle', '--label-ids', '--label-prefix', 'gdsn=' + NS,
            '--label-prefix', 'gpc=https://example.org/gpc/',
            '--base', 'https://example.org/base/', '--rdf-direction', 'i18n-datatype']
    assert main(args) == 0
    captured = capsys.readouterr()
    assert not captured.out
    command = next(line for line in captured.err.splitlines() if line.startswith('owl-jsonld '))
    tokens = shlex.split(command)
    assert tokens[-1] == str(source)
    assert tokens.count('--label-prefix') == 2
    assert '--base=https://example.org/base/' in tokens
    assert 'i18n-datatype' in tokens
    assert '--force' not in tokens
    assert main(tokens[1:]) == 0
    assert '@context' in json.loads(capsys.readouterr().out)
    assert main([*args, '--quiet']) == 0
    assert capsys.readouterr() == ('', '')


def test_failed_verification_does_not_suggest_command(tmp_path, capsys):
    source = tmp_path / 'invalid.ttl'
    source.write_text(f'<{NS}1> <urn:p> <urn:o> .')
    assert main(['validate', str(source), '--label-ids', '--label-prefix', 'gdsn=' + NS]) == 1
    captured = capsys.readouterr()
    assert not captured.out
    assert 'Suggested conversion' not in captured.err


def test_stdin_verification_suggestion(monkeypatch, capsys):
    import io
    import shlex
    monkeypatch.setattr('sys.stdin', io.StringIO(vocabulary().serialize(format='turtle')))
    assert main(['validate', '-', '-f', 'turtle', '--label-ids', '--label-prefix', 'gdsn=' + NS]) == 0
    captured = capsys.readouterr()
    assert 'Supply the same RDF input on stdin again' in captured.err
    command = next(line for line in captured.err.splitlines() if line.startswith('owl-jsonld '))
    tokens = shlex.split(command)
    assert tokens[-1] == '-'
    assert tokens[tokens.index('--input-format') + 1] == 'turtle'
