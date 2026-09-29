import json
from importlib.metadata import version
from pathlib import Path
import subprocess
import sys

import pytest
from rdflib import Dataset, Graph

from gdsn_tsv_transformer.jsonld.conformance import DEFAULT_MANIFEST

COMMANDS = ("rdf-to-jsonld", "jsonld-to-rdf", "convert", "validate", "formats", "test-w3c", "version")
CONSOLE = str(Path(sys.executable).parent / "owl-jsonld")
TTL = '@prefix owl: <http://www.w3.org/2002/07/owl#> . <https://example.org/Book> a owl:Class .'
NQ = '<urn:s> <urn:p> "default" .\n<urn:s> <urn:p> "named" <urn:g> .\n'


def run(*args, stdin=None, module=False):
    command = [sys.executable, "-m", "gdsn_tsv_transformer.jsonld"] if module else [CONSOLE]
    return subprocess.run([*command, *map(str, args)], input=stdin, text=True, encoding="utf-8", capture_output=True, timeout=30)


@pytest.mark.parametrize("args", [(), ("--help",)])
@pytest.mark.parametrize("module", [False, True])
def test_top_help(args, module):
    result = run(*args, module=module)
    assert result.returncode == 0
    assert all(command in result.stdout for command in COMMANDS)
    assert not result.stderr


@pytest.mark.parametrize("command", COMMANDS)
def test_sub_help(command):
    result = run(command, "--help")
    assert result.returncode == 0
    assert "usage:" in result.stdout


def test_versions():
    assert run("--version").stdout.strip() == run("version").stdout.strip() == version("gdsn-tsv-transformer")


def test_formats():
    result = run("formats")
    assert result.returncode == 0
    assert "READ\tWRITE\tGRAPH\tDATASET" in result.stdout
    assert "nquads\tyes\tyes\tyes\tyes" in result.stdout


def test_file_conversion_and_overwrite(tmp_path):
    source, target = tmp_path / "ontology.ttl", tmp_path / "ontology.jsonld"
    source.write_text(TTL)
    result = run("rdf-to-jsonld", source, "-o", target)
    assert result.returncode == 0, result.stderr
    assert not result.stdout and not result.stderr
    original = target.read_text()
    assert isinstance(json.loads(original), list)
    assert run("rdf-to-jsonld", source, "-o", target).returncode == 3
    assert target.read_text() == original
    assert run("rdf-to-jsonld", source, "-o", target, "--force").returncode == 0
    rdf = tmp_path / "ontology.trig"
    assert run("jsonld-to-rdf", target, "-o", rdf, "--output-format", "trig").returncode == 0
    assert len(Dataset().parse(rdf, format="trig")) == 1


def test_named_roundtrip_and_default_formats(tmp_path):
    source, target = tmp_path / "data.nq", tmp_path / "data.jsonld"
    source.write_text(NQ)
    assert run("convert", source, target).returncode == 0
    result = run("jsonld-to-rdf", target)
    assert result.returncode == 0, result.stderr
    graph = Dataset().parse(data=result.stdout, format="nquads")
    assert len(list(graph.quads())) == 2
    assert run("jsonld-to-rdf", target, "-f", "turtle").returncode == 1
    assert run("convert", target, tmp_path / "data.trig").returncode == 0


@pytest.mark.parametrize("command", ["rdf-to-jsonld", "convert"])
@pytest.mark.parametrize("input_format", ["turtle", "xml"])
def test_schema_stdin_stdout(command, input_format):
    source = Graph().parse(data=TTL, format="turtle").serialize(format=input_format)
    args = [command, "-"]
    if command == "convert":
        args += ["-", "--output-format", "json-ld"]
    result = run(*args, "--input-format", input_format, "--schema-org", "--ordered", stdin=source)
    assert result.returncode == 0, result.stderr
    doc = json.loads(result.stdout)
    assert set(doc) == {"@context", "@graph"}
    assert doc["@graph"][0]["@type"] == "Class"
    assert "_:" not in result.stdout
    assert not result.stderr
    assert len(Graph().parse(data=result.stdout, format="json-ld")) > 0


def test_schema_file_xml_and_overwrite(tmp_path):
    source, output = tmp_path / "ontology.owl", tmp_path / "extension.jsonld"
    Graph().parse(data=TTL, format="turtle").serialize(source, format="xml")
    assert run("rdf-to-jsonld", source, "--schema-org", "-o", output).returncode == 0
    assert run("rdf-to-jsonld", source, "--schema-org", "-o", output).returncode == 3
    assert run("rdf-to-jsonld", source, "--schema-org", "-o", output, "--force").returncode == 0


@pytest.mark.parametrize("args", [
    ("jsonld-to-rdf", "-", "--schema-org"),
    ("convert", "x.jsonld", "x.ttl", "--schema-org"),
    ("convert", "x.ttl", "x.ttl", "--schema-org"),
    ("convert", "-", "-", "--schema-org"),
    ("rdf-to-jsonld", "-"),
    ("rdf-to-jsonld", "x.ttl", "--indent", "-1"),
    ("rdf-to-jsonld", "x.ttl", "--input-format", "nonexistent"),
    ("convert", "x.ttl", "x.jsonld", "--generalized-rdf"),
    ("convert", "x.jsonld", "x.ttl", "--use-native-types"),
])
def test_usage_errors(args):
    result = run(*args)
    assert result.returncode == 2
    assert not result.stdout
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("source,format", [("not valid turtle", "turtle"), ("{", "json-ld"), ('{"@id": 12}', "json-ld")])
def test_invalid_diagnostics(source, format):
    result = run("validate", "-", "--input-format", format, stdin=source)
    assert result.returncode == 1
    assert not result.stdout and "-:" in result.stderr
    assert "Traceback" not in result.stderr
    if source == "{":
        assert "line 1 column 2" in result.stderr


def test_missing_input_and_output_directory(tmp_path):
    result = run("rdf-to-jsonld", tmp_path / "missing.ttl")
    assert result.returncode == 3
    assert "missing.ttl" in result.stderr
    result = run("rdf-to-jsonld", "-", "-f", "turtle", "-o", tmp_path / "missing" / "x.jsonld", stdin=TTL)
    assert result.returncode == 3


def test_stdin_pipeline_and_ascii():
    source = '<urn:s> <urn:p> "Café" .'
    result = run("--verbose", "rdf-to-jsonld", "-", "-f", "turtle", "--compact", "--ensure-ascii", stdin=source)
    assert result.returncode == 0 and not result.stderr
    assert "\\u00e9" in result.stdout and len(result.stdout.splitlines()) == 1
    back = run("jsonld-to-rdf", "-", "-f", "nt", stdin=result.stdout)
    assert back.returncode == 0 and not back.stderr
    assert "Café" in back.stdout


def test_base_and_context(tmp_path):
    context = tmp_path / "context.jsonld"
    context.write_text('{"@context":{"name":"urn:name"}}')
    result = run("jsonld-to-rdf", "-", "--base", "https://example.org/", "--context", context,
                 stdin='{"@id":"person","name":"Jane"}')
    assert result.returncode == 0, result.stderr
    assert "https://example.org/person" in result.stdout


def test_validate_quiet():
    result = run("validate", "-", "-f", "turtle", stdin=TTL)
    assert result.returncode == 0 and not result.stdout and "valid" in result.stderr
    result = run("--quiet", "validate", "-", "-f", "turtle", stdin=TTL)
    assert result.returncode == 0 and not result.stdout and not result.stderr


def test_conformance_success_filter_report(tmp_path):
    report = tmp_path / "report.json"
    result = run("test-w3c", "--offline", "--report", report)
    assert result.returncode == 0, result.stderr
    assert "54 passed, 0 failed, 0 skipped, 54 total" in result.stderr
    assert not result.stdout and "Traceback" not in result.stderr
    assert json.loads(report.read_text())["total"] == 54
    result = run("test-w3c", "--filter", "t0001", "--verbose", "--offline")
    assert result.returncode == 0 and "#t0001: passed" in result.stderr
    assert run("test-w3c", "--filter", "missing").returncode == 2


def test_conformance_failure_negative_and_failfast(tmp_path):
    manifest = tmp_path / "manifest.jsonld"
    entry = {"@id": "#broken", "@type": ["jld:FromRDFTest"], "input": "input.nq", "expect": "expected.jsonld"}
    manifest.write_text(json.dumps({"sequence": [entry, entry]}))
    (tmp_path / "input.nq").write_text('<urn:s> <urn:p> "value" .')
    (tmp_path / "expected.jsonld").write_text('[]')
    result = run("test-w3c", "--manifest", manifest, "--fail-fast", "--offline")
    assert result.returncode == 1
    assert "0 passed, 1 failed, 0 skipped, 1 total" in result.stderr
    assert "#broken" in result.stderr and "--- expected" in result.stderr
    entry.pop("expect")
    entry["expectErrorCode"] = "invalid JSON literal"
    manifest.write_text(json.dumps({"sequence": [entry]}))
    assert run("test-w3c", "--manifest", manifest).returncode == 1
    (tmp_path / "input.nq").write_text('<urn:s> <urn:p> "wrong"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#JSON> .')
    assert run("test-w3c", "--manifest", manifest).returncode == 0
    manifest.write_text('{"sequence": null}')
    malformed = run("test-w3c", "--manifest", manifest)
    assert malformed.returncode == 1 and "Traceback" not in malformed.stderr


def test_normal_conversion_regression():
    normal = run("rdf-to-jsonld", "-", "-f", "turtle", stdin=TTL)
    projected = run("rdf-to-jsonld", "-", "-f", "turtle", "--schema-org", stdin=TTL)
    assert isinstance(json.loads(normal.stdout), list)
    assert isinstance(json.loads(projected.stdout), dict)
    assert "http://www.w3.org/2002/07/owl#Class" in normal.stdout


def test_reject_jsonld_output_and_conflicting_verbosity():
    assert run("jsonld-to-rdf", "-", "-f", "json-ld", stdin='[]').returncode == 2
    assert run("--verbose", "validate", "-", "--quiet", "-f", "turtle", stdin=TTL).returncode == 2


def test_nested_relative_context(tmp_path):
    (tmp_path / "nested.jsonld").write_text('{"@context":{"name":"urn:name"}}')
    context = tmp_path / "context.jsonld"
    context.write_text('{"@context":"nested.jsonld"}')
    result = run("jsonld-to-rdf", "-", "--context", context, "--base", "https://example.org/", stdin='{"@id":"person","name":"Jane"}')
    assert result.returncode == 0, result.stderr
    assert any(str(p) == "urn:name" for _, p, _ in Graph().parse(data=result.stdout, format="turtle"))
