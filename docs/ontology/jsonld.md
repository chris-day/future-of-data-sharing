---
icon: lucide/braces
---

# OWL/RDF and JSON-LD

`owl-jsonld` converts RDF graphs and datasets to expanded JSON-LD and parses
JSON-LD back into RDF. It also offers an explicit, lossy projection of named OWL
vocabulary terms into a Schema.org extension document. It does not perform OWL
reasoning, JSON-LD framing, general-purpose compaction, or RDF canonicalization.

The Python module is `gdsn_tsv_transformer.jsonld`, within the existing
`gdsn-tsv-transformer` distribution. The installed command is `owl-jsonld`.

## Install and run

The supported and tested interpreter is **CPython 3.14.4**. The repository's
`.python-version` and CI select that version; package metadata allows
`>=3.14.4,<3.15` and makes no claim about older Python versions.

From the repository root:

```bash
python3.14 --version  # Must report Python 3.14.4 for the verified setup.
python3.14 -m venv .venv
.venv/bin/python -m pip install -e .
source .venv/bin/activate
owl-jsonld --help
python -m gdsn_tsv_transformer.jsonld --help
```

Both `owl-jsonld` without arguments and `owl-jsonld --help` list every command.
The [command reference](jsonld-cli.md) describes all options. See
[development and conformance](jsonld-development.md) for testing and verification.

## Convert files and datasets

These examples run from the repository root with the environment activated.
They use the downloadable [Turtle ontology](examples/ontology.ttl) and
[TriG dataset](examples/dataset.trig). `--force` explicitly permits replacement
of these example outputs on subsequent runs.

```bash
# example: roundtrip
owl-jsonld rdf-to-jsonld docs/ontology/examples/ontology.ttl -o ontology.jsonld --ordered --force
owl-jsonld jsonld-to-rdf ontology.jsonld -o ontology.trig --output-format trig --force
owl-jsonld validate ontology.trig
```

```bash
# example: datasets
owl-jsonld convert docs/ontology/examples/dataset.trig dataset.jsonld --force
owl-jsonld convert dataset.jsonld dataset.nq --force
owl-jsonld validate dataset.nq
```

The default graph and named graphs are kept separate. Named graphs appear in
JSON-LD as nodes containing `@id` and `@graph`. Dataset output requires a format
that supports graphs, such as TriG or N-Quads; choosing Turtle for a named-graph
dataset is an error rather than silently discarding graph names.

## Pipes, text encoding, and diagnostics

```bash
# example: pipeline
cat docs/ontology/examples/ontology.ttl | owl-jsonld rdf-to-jsonld - -f turtle --compact | owl-jsonld jsonld-to-rdf - -f nquads | owl-jsonld validate - -f nquads
```

`-` means stdin or stdout. Files and HTTP(S) resources are read as UTF-8. Input
format is inferred from the URL path or filename; specify `--input-format` for
stdin and unfamiliar extensions. `.json` and `.jsonld` mean JSON-LD, `.owl` and
`.rdf` mean RDF/XML, `.ttl` means Turtle, and `.nq` means N-Quads. RDFLib supplies
additional extension mappings.

Only requested documents, help, versions, and format listings go to stdout.
Diagnostics and conformance summaries go to stderr. Conversion emits no progress
messages, including with `--verbose`. Existing output files are protected unless
`--force` is supplied; missing output directories are not created automatically.
Errors include the input source and the parser's line/column details when available.

| Exit code | Meaning |
| --- | --- |
| `0` | Successful conversion, validation, or conformance run |
| `1` | RDF/JSON-LD processing, validation, or conformance failure |
| `2` | Invalid command usage, ambiguous direction, unknown format, or empty test selection |
| `3` | Input/output failure, including overwrite refusal |

Remote JSON-LD contexts may be fetched by RDFLib. Only `test-w3c --offline`
prohibits network fixture reads; general conversion is not an offline/network
sandbox. Use locally controlled inputs and contexts where that distinction matters.

## Library API

```python
from rdflib import Dataset, Graph, Literal, URIRef
from gdsn_tsv_transformer.jsonld import from_rdf, serialize_rdf, to_rdf

s, p = URIRef("https://example.com/book"), URIRef("https://example.com/title")
graph = Graph().add((s, p, Literal("A book", lang="en")))
expanded = from_rdf(graph, ordered=True)
text = serialize_rdf(graph, ordered=True)
restored = to_rdf(expanded)

dataset = Dataset()
dataset.default_graph.add((s, p, Literal("Default")))
dataset.graph(URIRef("https://example.com/catalogue")).add((s, p, Literal("Named")))
restored_dataset = to_rdf(from_rdf(dataset, ordered=True))
assert isinstance(restored_dataset, Dataset)
```

| API | Options and result |
| --- | --- |
| `from_rdf(dataset, *, ordered=False, rdf_direction=None, use_native_types=False, use_rdf_type=False, processing_mode="json-ld-1.1")` | `Graph`, `Dataset`, or legacy `ConjunctiveGraph` to a list of expanded node objects |
| `serialize_rdf(dataset, **options)` | The same conversion as UTF-8-compatible Unicode JSON text; accepts `from_rdf` options |
| `to_rdf(document, *, base=None, context=None, rdf_direction=None, generalized_rdf=False)` | A decoded JSON object/array to `Graph` when only a default graph exists, otherwise `Dataset` |
| `owl_to_schema_org(graph, *, ordered=False)` | A lossy vocabulary projection with an inline context and flat graph |
| `validate_rdf_list(graph, head)` | Optional strict list-chain validation; returns the RDF items or raises `MalformedListError` |

`to_rdf` takes decoded JSON, not a filename or JSON string. File/URL handling
belongs to the CLI. It accepts inline or RDFLib-supported external contexts via
`context`. Blank-node predicates require `generalized_rdf=True` and a compatible
output format; standard RDF syntaxes need not support generalized triples.

`JsonLdError` is the base processing exception and carries a stable `code`.
`InvalidInputError` and `UnsupportedOptionError` distinguish invalid input and
unsupported behavior. Invalid `rdf:JSON` values raise code `invalid JSON literal`;
direction errors use `invalid base direction` or `invalid language-tagged string`.
Malformed RDF lists normally remain RDF structures. Only the optional strict
validator raises `MalformedListError` (code `malformed RDF list`).

## Conversion behavior and RDFLib boundaries

The package implements the [JSON-LD 1.1 From RDF algorithm](https://www.w3.org/TR/json-ld11-api/#serialize-rdf-as-json-ld-algorithm)
itself: node maps, reference tracking, named graphs, literal conversion,
compound literals, and backward list reconstruction. It does not delegate
From RDF conversion to RDFLib's JSON-LD serializer or to PyLD. RDFLib handles
RDF storage, RDF parsing/serialization, and the JSON-LD-to-RDF parser.

- IRI and blank-node objects become `@id` references. `rdf:type` becomes `@type`
  unless `use_rdf_type=True`. Repeated values are suppressed.
- Plain/XSD string literals become `@value`; datatype and language information
  is retained. Language tags are compared case-insensitively and emitted lowercase.
- With native types enabled, valid XSD booleans, integers, and finite doubles
  become JSON scalars. Other datatypes, invalid lexical forms, and nonfinite
  doubles retain their spelling and datatype. Decimal/float and integer-derived
  datatypes are not silently converted to native numbers.
- `rdf:JSON` becomes `@type: "@json"` with decoded JSON content. Invalid JSON,
  including nonstandard `NaN`/`Infinity` tokens, is rejected.
- Well-formed singly referenced blank-node collection chains become `@list`.
  Empty lists work; broken, cyclic, shared, multiply referenced, or annotated
  nodes retain their RDF structure. A well-formed suffix may still become a list.
- `ordered=True` produces stable output for fixed RDF node identifiers and sorts
  unordered values for reproducibility. It never reorders list items or JSON
  literal arrays. It is not blank-node canonicalization across separate parses.
- `processing_mode="json-ld-1.0"` is provided for legacy list-of-lists behavior
  exercised by the W3C manifest; the default is JSON-LD 1.1.

!!! note "Native boolean specification/test-suite difference"
    W3C test `t0027` expects the XSD boolean spellings `0` and `1` to become
    `false` and `true`. The prose algorithm mentions only `false` and `true`.
    This implementation follows the test suite and the XSD lexical space.

RDFLib normally normalizes literal spellings while parsing. The CLI and
conformance parser temporarily disable normalization and restore the setting
under a package-local lock. Other threads calling RDFLib directly do not share
that lock. For an application creating literals itself, use
`Literal("001", datatype=XSD.integer, normalize=False)` to retain the original
spelling; a converter cannot recover a spelling already normalized by its caller.

### Direction-aware values

From RDF supports both `i18n-datatype` and `compound-literal`. In the reverse
direction the wrapper supports explicit expanded `@value`/`@direction` objects,
including inside named graphs. Example:

```python
from gdsn_tsv_transformer.jsonld import from_rdf, to_rdf

document = [{"@id": "urn:subject", "urn:label": [
    {"@value": "مرحبا", "@language": "ar", "@direction": "rtl"}
]}]
for mode in ("i18n-datatype", "compound-literal"):
    rdf = to_rdf(document, rdf_direction=mode)
    assert from_rdf(rdf, rdf_direction=mode) == document
```

RDFLib 7.6.0 does not implement context-level `@direction`. Locally supplied
contexts with that keyword are explicitly rejected; supply expanded directional
value objects instead. The wrapper is not a full JSON-LD expansion or syntax
conformance implementation: aliases, scoped/remote context behaviors and other
JSON-LD-to-RDF features follow RDFLib's parser. It validates common invalid value
objects but does not claim to pass the separate W3C To RDF suite. With
`rdf_direction=None`, explicit direction is discarded, as specified for a null
RDF direction option.

## Lossy Schema.org projection

!!! warning "Vocabulary projection, not an OWL equivalence transformation"
    `--schema-org` deliberately removes logical axioms. Restrictions, unions,
    intersections, complements, inverses, cardinalities, equivalence, property
    chains, disjointness, keys, negative assertions, and anonymous expressions
    are omitted. Do not use this mode for lossless OWL exchange or reasoning.

```bash
# example: schema
owl-jsonld rdf-to-jsonld docs/ontology/examples/ontology.ttl --schema-org -o extension.jsonld --ordered --force
owl-jsonld convert docs/ontology/examples/ontology.ttl extension-via-convert.jsonld --schema-org --force
owl-jsonld validate extension.jsonld
```

The result always has one inline `@context` and one flat `@graph`. The context
uses `https://schema.org/` with its trailing slash and defines `schema`, `rdfs`,
`owl`, `xsd`, and IRI-valued `domainIncludes`/`rangeIncludes`. Source entity IRIs
are preserved; the projection does not mint replacement Schema.org identifiers.

Named subjects explicitly typed `owl:Class` become `Class`. Named subjects typed
`owl:ObjectProperty` or `owl:DatatypeProperty` become `Property`. Multiple property
types produce one entry; a term typed as both a class and a property has both
projected types. Named superclasses become `rdfs:subClassOf` references. Named
domains and ranges become `domainIncludes` and `rangeIncludes`. Blank-node
subjects, superclasses, domains, and ranges are ignored. No arbitrary source
predicates are copied. Datasets are projected over their union, discarding graph
provenance.

Labels retain text and language tags; language-tagged labels are value objects.
One label/reference is a scalar and multiple values form a deduplicated array.
If a label is absent, the percent-decoded URI fragment or final nonempty path
segment is used, then the complete IRI as a fallback. With `--ordered`, entries
are sorted by source `@id` and references by expanded IRI.

| XSD range | Schema.org range |
| --- | --- |
| `string`, `normalizedString`, `token`, `language` | `Text` |
| `boolean` | `Boolean` |
| `integer`, `nonPositiveInteger`, `negativeInteger`, `long`, `int`, `short`, `byte`, `nonNegativeInteger`, `unsignedLong`, `unsignedInt`, `unsignedShort`, `unsignedByte`, `positiveInteger` | `Integer` |
| `decimal`, `float`, `double` | `Number` |
| `date` | `Date` |
| `dateTime`, `dateTimeStamp` | `DateTime` |
| `time` | `Time` |
| `duration`, `dayTimeDuration`, `yearMonthDuration` | `Duration` |
| `anyURI` | `URL` |

The immutable `PRIMITIVE_DATATYPES` mapping is exported from the package. Unknown
named range IRIs are retained. No blank-node identifiers are emitted.
