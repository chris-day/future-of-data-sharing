---
icon: lucide/flask-conical
---

# JSON-LD development and conformance

The implementation lives in `src/gdsn_tsv_transformer/jsonld/`, alongside the
existing transformer package. Its [user guide](jsonld.md) and
[command reference](jsonld-cli.md) are part of this Zensical site.

## Environment and checks

Use **CPython 3.14.4** and the existing `.venv` workflow. Dependency pins remain in
the repository's `pyproject.toml` and `requirements.txt`; pytest is in the `dev`
extra. There is no separate project or dependency environment for this tool.

```bash
.venv/bin/python --version
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pip check
.venv/bin/python -m pytest tests/jsonld -q
.venv/bin/python -m pytest -q
.venv/bin/owl-jsonld test-w3c --offline
.venv/bin/python -m compileall -q src/gdsn_tsv_transformer/jsonld
.venv/bin/zensical build --clean
git diff --check
```

The repository has no configured formatter, linter, or static type checker.
Public APIs and implementation functions have type hints, and the subpackage
ships `py.typed`. Compile checks and whitespace checks are not substitutes for
static type checking; no mypy/Ruff result is claimed. CI selects Python 3.14.4
and runs the complete pytest suite, the offline conformance command, dependency
checks, and the existing Zensical build.

The new tests use pytest, which also discovers the existing unittest-based
project tests. Existing integration tests can skip when their generated ontology
artefacts are absent; the W3C suite has no exclusions or expected-failure skips.
Unit tests, CLI tests, and W3C fixtures do not require network access. HTTP behavior
is tested with mocked transport. The guide's marked CLI examples run automatically
in temporary directories, including its stdin/stdout pipeline; its Python
examples run as tests as well.

## W3C fixture snapshot and runner

The complete [W3C From RDF manifest](https://w3c.github.io/json-ld-api/tests/fromRdf-manifest.html)
contains **54 tests** in the vendored snapshot. Current conformance status:
**54 passed, 0 failed, 0 skipped, 54 total**. This includes both negative
`rdf:JSON` cases and the direction tests marked non-normative upstream.

The manifest, context, and referenced N-Quads/JSON-LD files are bundled under
`src/gdsn_tsv_transformer/jsonld/w3c/` and included in wheels. The default command
works offline even outside a source checkout. Fixture files are unmodified;
`PROVENANCE.md` records the upstream repository/snapshot, and `LICENSE.md` plus
`LICENSE.html` reproduce the upstream licensing attribution. Copyright belongs
to W3C and contributors under the
[W3C Software and Document License](https://www.w3.org/Consortium/Legal/copyright-software).

```bash
.venv/bin/owl-jsonld test-w3c --offline
.venv/bin/owl-jsonld test-w3c --filter t0001 --verbose --offline
.venv/bin/owl-jsonld test-w3c --manifest src/gdsn_tsv_transformer/jsonld/w3c/fromRdf-manifest.jsonld --offline
.venv/bin/owl-jsonld test-w3c --offline --report /tmp/owl-jsonld-w3c-report.json
.venv/bin/python -m pytest tests/jsonld/test_core.py -k 'w3c and t0001' -q
```

Use a new report path on repeated runs; report files are not overwritten.
`--filter t0115` is a valid selector syntax but this particular snapshot has no
`t0115`, so it correctly returns usage status `2` instead of reporting a vacuous
success.

The runner discovers every `jld:FromRDFTest`, parses N-Quads through RDFLib with
literal normalization disabled, and applies the manifest's processing options.
N-Quads blank-node labels are preserved for comparison within each independent
fixture. Expected documents are compared structurally: map order is irrelevant,
arrays are unordered except `@list`, language tags are case-insensitive, and JSON
literal arrays retain their ordinary JSON ordering. Boolean and numeric values
are distinct. Failures include the test identifier and a unified structural diff.
Negative cases require the exact expected JSON-LD processing error code.

No expected output is rewritten. Unsupported manifest options fail visibly. When
refreshing fixtures, fetch the upstream snapshot, copy the manifest and all its
referenced resources without editing their contents, update provenance and
licenses, then run the entire suite and update the verified counts here.

## Implementation map

| Module | Responsibility |
| --- | --- |
| `core.py` | RDF-to-value conversion, graph/node maps, reference tracking, compound literals, lists, expanded output |
| `parsing.py` | RDFLib parsing, lexical-form preservation, input checks, direction compatibility adapter |
| `lists.py` | Optional strict collection validation |
| `schema.py` | Allowlisted OWL projection and immutable primitive datatype mapping |
| `conformance.py` | Resource resolution, manifest discovery, comparison, reports |
| `cli.py` | Argument parsing and UTF-8 document I/O; no RDF conversion algorithm |
| `__init__.py` | Stable public API exports |
| `__main__.py` | Delegation to the shared CLI entry point |

The design reference was the
[Java OWL API JSON-LD integration](https://github.com/stain/owlapi-jsonld).
The normative behavior comes from the W3C algorithm and fixtures; no Java or
third-party From RDF implementation was ported or used as the core converter.
The [user guide](jsonld.md#conversion-behavior-and-rdflib-boundaries) records the
RDFLib parser boundaries, literal-normalization caveat, and boolean lexical-form
specification/test-suite difference. Passing From RDF tests does not imply
conformance with the separate expansion, compaction, framing, or To RDF suites.

## Verification record — 2026-09-28

Verified in this repository with **CPython 3.14.4** and RDFLib **7.6.0**:

| Command | Result |
| --- | --- |
| `.venv/bin/python --version` | Python 3.14.4 |
| `.venv/bin/python -m pip install -e '.[dev]'` | Normal isolated-build editable installation succeeded |
| `.venv/bin/python -m pip check` | No broken requirements |
| `.venv/bin/python -m pytest tests/jsonld -q --disable-warnings` | 204 passed; includes 54 W3C cases and all marked guide examples |
| `.venv/bin/python -m pytest -q --disable-warnings` | 224 passed, 8 unittest subtests passed, no skips |
| `.venv/bin/owl-jsonld test-w3c --offline` | 54 passed, 0 failed, 0 skipped, 54 total |
| `.venv/bin/owl-jsonld --version` | 0.1.0 |
| `.venv/bin/python -m compileall -q src/gdsn_tsv_transformer/jsonld` | Passed |
| `git diff --check` | Passed |
| `.venv/bin/zensical build --clean` | Passed, no issues found |
| `.venv/bin/python -m pip wheel --no-build-isolation --no-deps . -w /tmp/owl-jsonld-wheels` | Wheel built with the CLI, type marker, licenses, and offline fixtures |

The full pytest run reported 536 warnings, principally RDFLib's use of deprecated
context APIs inside its parsers, plus legacy `ConjunctiveGraph` coverage. Warning
summaries were suppressed for readability, not converted into skipped tests.
No formatter/linter/type checker was configured, so those checks were not run.

The wheel was installed into a separate temporary directory and its complete
From RDF suite passed outside the repository checkout. All 108 upstream fixture
files were compared byte-for-byte with the downloaded archive. Generated links
on all three JSON-LD documentation pages were checked against the built site.
The remaining JSON-LD-to-RDF limitations are described explicitly in the
[user guide](jsonld.md#conversion-behavior-and-rdflib-boundaries).
