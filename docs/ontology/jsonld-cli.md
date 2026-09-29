---
icon: lucide/terminal
---

# JSON-LD command reference

See the [user guide](jsonld.md) for installation and working examples, and
[development](jsonld-development.md) for the conformance runner. Every command
supports `-h`/`--help` and uses the same implementation when invoked through
`python -m gdsn_tsv_transformer.jsonld`.

## Global options

`owl-jsonld` and `owl-jsonld --help` display top-level help and all seven commands.

| Option | Behavior |
| --- | --- |
| `-h`, `--help` | Show help and exit successfully |
| `--version` | Print the installed distribution version and exit |
| `--verbose` | Include detailed processing codes and per-test outcomes on stderr |
| `--quiet` | Suppress successful validation/conformance summaries; errors remain visible |

`--verbose` and `--quiet` are mutually exclusive and may be placed before or
after the subcommand.

## rdf-to-jsonld

```text
owl-jsonld rdf-to-jsonld INPUT [-o PATH] [-f FORMAT] [options]
```

| Argument/option | Behavior |
| --- | --- |
| `INPUT` | File, HTTP(S) URL, or `-` for stdin |
| `-o`, `--output PATH` | Output file or `-` for stdout (default) |
| `-f`, `--input-format FORMAT` | RDFLib input format; otherwise infer from extension |
| `--base IRI` | Base IRI for RDF parsing; defaults to the input location |
| `--ordered`, `--no-ordered` | Enable/disable deterministic ordering; default disabled |
| `--use-native-types` | Convert eligible XSD boolean/integer/double literals to native JSON values |
| `--use-rdf-type` | Preserve `rdf:type` instead of converting it to `@type` |
| `--rdf-direction MODE` | `i18n-datatype`, `compound-literal`, or `none` (default) |
| `--schema-org` | Project named OWL terms to a lossy Schema.org extension |
| `--indent INTEGER` | Nonnegative JSON indentation; default `2` |
| `--compact` | Emit compact JSON text, overriding indentation |
| `--ensure-ascii` | Escape non-ASCII JSON characters |
| `--force` | Permit overwriting the destination file |

stdin requires `--input-format`. JSON-LD input is rejected by this command.
Schema.org mode retains format, base, order, indentation, ASCII, and overwrite
options. Native-types, rdf-type, and non-null rdf-direction options are rejected
in projection mode because they do not describe that projection.

## jsonld-to-rdf

```text
owl-jsonld jsonld-to-rdf INPUT [-o PATH] [-f FORMAT] [options]
```

| Argument/option | Behavior |
| --- | --- |
| `INPUT` | JSON-LD file, HTTP(S) URL, or `-` for stdin |
| `-o`, `--output PATH` | Output file or `-` for stdout (default) |
| `-f`, `--output-format FORMAT` | RDFLib serialization format; otherwise infer from output extension |
| `--base IRI` | Base IRI for relative identifiers; defaults to the input location |
| `--context PATH_OR_URL` | Optional external JSON-LD context document |
| `--rdf-direction MODE` | `i18n-datatype`, `compound-literal`, or `none` (default) |
| `--generalized-rdf` | Permit RDFLib-supported blank-node predicates |
| `--force` | Permit overwriting the destination file |

With no inferred/explicit output format, the default is N-Quads for a dataset
with named graphs and Turtle for a default-only graph. A named-graph dataset
cannot be written into a graph-only format. `--schema-org` is not accepted.

## convert

```text
owl-jsonld convert INPUT OUTPUT [options]
```

`INPUT` and `OUTPUT` are positional and support `-`. Use `--input-format FORMAT`
and `--output-format FORMAT` to override extension inference. Exactly one format
must be JSON-LD; ambiguous direction or an RDF-to-RDF conversion is a usage error.

All long conversion options listed above are accepted: `--base`, `--ordered`,
`--no-ordered`, `--use-native-types`, `--use-rdf-type`, `--rdf-direction`,
`--schema-org`, `--indent`, `--compact`, `--ensure-ascii`, `--context`,
`--generalized-rdf`, and `--force`. JSON output controls apply only to RDF input;
context/generalized-RDF controls apply only to JSON-LD input. Options that do not
apply to the selected direction are rejected. `--schema-org` requires RDF/OWL
input and JSON-LD output.

## validate

```text
owl-jsonld validate INPUT [-f FORMAT] [--base IRI] [--rdf-direction MODE]
```

`-f`/`--input-format` overrides inference. `INPUT` supports file, HTTP(S) URL, and
stdin. No converted document is written. A successful parse returns `0` and
prints a concise message to stderr unless quiet; processing failures return `1`
and I/O failures return `3`. This is syntax/parsing validation, not SHACL or OWL
consistency checking. JSON-LD validation has the RDFLib compatibility limits
explained in the [user guide](jsonld.md#conversion-behavior-and-rdflib-boundaries).

## formats

```text
owl-jsonld formats
```

Lists the dynamically registered RDFLib parsers and serializers with `READ`,
`WRITE`, `GRAPH`, and `DATASET` columns. Dataset support is identified for TriG,
TriX, N-Quads, JSON-LD, Hextuples, and RDF Patch, including registered media-type names. Third-party
plugins may have additional capabilities; `no/unknown` means this package has
not established dataset preservation for that format.

## test-w3c

```text
owl-jsonld test-w3c [options]
```

| Option | Behavior |
| --- | --- |
| `--manifest PATH_OR_URL` | Manifest location; defaults to the bundled W3C fixtures |
| `--filter PATTERN` | Identifier substring or shell wildcard pattern |
| `--verbose` | Print each selected case outcome and failure details to stderr |
| `--fail-fast` | Stop at the first failed case |
| `--offline` | Prohibit HTTP(S) fixture/manifest reads |
| `--report PATH` | Save a JSON report to a new file, or `-` for stdout |

The summary reports passed, failed, skipped, and total **executed** cases. A
failing case returns `1`; an empty selection returns `2`. Filtered/unexecuted
cases are not counted as skips. There are no blanket skips. Negative tests pass
only when the exact expected processing code is raised. A report will not
overwrite an existing file. `--quiet` suppresses successful summaries; failures
remain visible. Supplied local manifests resolve references relative to their
own directory; remote manifests resolve references relative to their URL.

## version

```text
owl-jsonld version
owl-jsonld --version
```

Prints the installed `gdsn-tsv-transformer` distribution version. There is no
separate, potentially conflicting version for the JSON-LD subpackage.
