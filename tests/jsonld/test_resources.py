"""Resource resolution and network isolation without any live HTTP requests."""
from io import BytesIO

import pytest

from gdsn_tsv_transformer.jsonld import conformance
from gdsn_tsv_transformer.jsonld.cli import _format, main


def test_url_read_and_offline(monkeypatch):
    calls = []

    def fake_open(url, timeout):
        calls.append((url, timeout))
        return BytesIO('"Café"'.encode())

    monkeypatch.setattr(conformance, "urlopen", fake_open)
    assert conformance.read_resource("https://example.org/test") == '"Café"'
    assert calls == [("https://example.org/test", 30)]
    with pytest.raises(OSError, match="Offline"):
        conformance.read_resource("https://example.org/test", offline=True)
    assert len(calls) == 1


def test_resolve_and_inference():
    assert conformance.resolve("https://w3c.github.io/json-ld-api/tests/fromRdf-manifest.jsonld", "fromRdf/0001-in.nq") == "https://w3c.github.io/json-ld-api/tests/fromRdf/0001-in.nq"
    assert _format(None, "https://example.org/ontology.ttl?version=1") == "turtle"
    assert _format(None, "https://example.org/ontology.owl") == "xml"


def test_cli_url_without_network(monkeypatch, capsys):
    monkeypatch.setattr(conformance, "urlopen", lambda *args, **kwargs: BytesIO(b'<urn:s> <urn:p> "value" .'))
    assert main(["rdf-to-jsonld", "https://example.org/test.ttl"]) == 0
    captured = capsys.readouterr()
    assert '"urn:s"' in captured.out and not captured.err
