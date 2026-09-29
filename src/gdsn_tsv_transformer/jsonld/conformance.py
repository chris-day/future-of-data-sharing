"""Offline-first runner for the W3C From RDF manifest (also used by pytest)."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import difflib
import fnmatch
from importlib.resources import files
import json
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen

from .core import from_rdf, strict_json
from .errors import InvalidInputError, JsonLdError, UnsupportedOptionError
from .parsing import parse_rdf

DEFAULT_MANIFEST = str(files(__package__).joinpath("w3c/fromRdf-manifest.jsonld"))


def read_resource(source: str, *, offline: bool = False) -> str:
    """Read a UTF-8 fixture from disk or HTTP(S); prohibit HTTP(S) in offline mode."""
    if urlparse(source).scheme in ("http", "https"):
        if offline:
            raise OSError(f"Offline mode cannot read {source}")
        with urlopen(source, timeout=30) as response:
            return response.read().decode("utf-8")
    return Path(source).read_text(encoding="utf-8")


def resolve(manifest: str, reference: str) -> str:
    if urlparse(reference).scheme in ("http", "https"):
        return reference
    if urlparse(manifest).scheme in ("http", "https"):
        return urljoin(manifest, reference)
    return str(Path(manifest).parent / reference)


def normalize(value: Any, *, ordered_array: bool = False, raw_json: bool = False) -> Any:
    """Compare JSON-LD arrays as sets of values, preserving @list and @json arrays."""
    if isinstance(value, dict):
        is_json = value.get("@type") == "@json"
        return {key: (item.lower() if key == "@language" and isinstance(item, str) and not raw_json
                      else normalize(item, ordered_array=key == "@list", raw_json=raw_json or (is_json and key == "@value")))
                for key, item in sorted(value.items())}
    if isinstance(value, list):
        result = [normalize(item, raw_json=raw_json) for item in value]
        return result if ordered_array or raw_json else sorted(result, key=lambda x: json.dumps(x, sort_keys=True))
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def structural_difference(expected: Any, actual: Any) -> str:
    left = json.dumps(normalize(expected), ensure_ascii=False, indent=2, sort_keys=True).splitlines()
    right = json.dumps(normalize(actual), ensure_ascii=False, indent=2, sort_keys=True).splitlines()
    return "\n".join(difflib.unified_diff(left, right, fromfile="expected", tofile="actual", lineterm=""))


@dataclass
class TestResult:
    """One conformance outcome, with diagnostic information on failure."""
    identifier: str
    status: str
    detail: str = ""

    __test__ = False


def discover(manifest: str = DEFAULT_MANIFEST, *, offline: bool = False) -> list[dict[str, Any]]:
    data = strict_json(read_resource(manifest, offline=offline))
    if not isinstance(data, dict) or not isinstance(data.get("sequence"), list):
        raise InvalidInputError("A From RDF manifest requires a sequence array")
    cases = []
    for entry in data["sequence"]:
        if not isinstance(entry, dict):
            raise InvalidInputError("Manifest sequence entries must be objects")
        kinds = entry.get("@type", [])
        kinds = [kinds] if isinstance(kinds, str) else kinds
        if not isinstance(kinds, list):
            raise InvalidInputError("Manifest @type must be a string or array")
        if not any(kind in kinds for kind in ("jld:FromRDFTest", "https://w3c.github.io/json-ld-api/tests/vocab#FromRDFTest")):
            continue
        if not all(isinstance(entry.get(key), str) for key in ("@id", "input")):
            raise InvalidInputError("Each FromRDFTest requires string @id and input fields")
        if not isinstance(entry.get("option", {}), dict):
            raise InvalidInputError(f"{entry['@id']}: option must be an object")
        if not any(isinstance(entry.get(key), str) for key in ("expect", "expectErrorCode")):
            raise InvalidInputError(f"{entry['@id']}: expected output or error code is required")
        cases.append(entry)
    return cases


def run_case(entry: dict[str, Any], manifest: str = DEFAULT_MANIFEST, *, offline: bool = True) -> TestResult:
    """Run one manifest case, including its exact expected negative error code."""
    identifier = entry["@id"]
    expected_error = entry.get("expectErrorCode")
    try:
        options = {}
        mapping = {"useNativeTypes": "use_native_types", "useRdfType": "use_rdf_type",
                   "rdfDirection": "rdf_direction", "ordered": "ordered", "processingMode": "processing_mode"}
        for name, value in entry.get("option", {}).items():
            if name in mapping:
                options[mapping[name]] = value
            elif name == "specVersion":
                options.setdefault("processing_mode", value)
            elif name != "normative":
                raise UnsupportedOptionError(f"Unimplemented manifest option: {name}")
        source = read_resource(resolve(manifest, entry["input"]), offline=offline)
        graph = parse_rdf(source, format="nquads")
        actual = from_rdf(graph, **options)
        if expected_error:
            return TestResult(identifier, "failed", f"Expected {expected_error!r}, but conversion succeeded")
        expected = strict_json(read_resource(resolve(manifest, entry["expect"]), offline=offline))
        diff = structural_difference(expected, actual)
        return TestResult(identifier, "failed" if diff else "passed", diff)
    except JsonLdError as exc:
        if expected_error == exc.code:
            return TestResult(identifier, "passed")
        return TestResult(identifier, "failed", f"{exc.code}: {exc}; expected error: {expected_error!r}")
    except Exception as exc:
        return TestResult(identifier, "failed", f"{type(exc).__name__}: {exc}")


def run_suite(manifest: str = DEFAULT_MANIFEST, *, pattern: str | None = None,
              offline: bool = False, fail_fast: bool = False) -> dict[str, Any]:
    """Run all selected FromRDFTest entries and return a JSON-serializable report."""
    results = []
    for entry in discover(manifest, offline=offline):
        if pattern and not (fnmatch.fnmatch(entry["@id"], pattern) or pattern in entry["@id"]):
            continue
        result = run_case(entry, manifest, offline=offline)
        results.append(result)
        if fail_fast and result.status == "failed":
            break
    return {"passed": sum(r.status == "passed" for r in results),
            "failed": sum(r.status == "failed" for r in results),
            "skipped": sum(r.status == "skipped" for r in results),
            "total": len(results), "results": [asdict(r) for r in results]}
