"""Command-line document I/O; all conversion is delegated to the public API."""
from __future__ import annotations

import argparse
from importlib.metadata import version
import json
import os
import tempfile
from pathlib import Path
import sys
from typing import Any, Sequence
from urllib.parse import urlparse

from rdflib import Dataset, Graph, plugin
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.util import guess_format

from . import JsonLdError, from_rdf, owl_to_schema_org, to_rdf
from .conformance import DEFAULT_MANIFEST, read_resource, run_suite
from .core import strict_json
from .errors import InvalidInputError, UnsupportedOptionError
from .parsing import parse_rdf

DATASET_FORMATS = frozenset({"trig", "trix", "nquads", "application/n-quads", "json-ld", "application/ld+json", "application/trig", "application/trix", "hext", "patch"})
JSONLD_FORMATS = frozenset({"json-ld", "application/ld+json"})
ALIASES = {"jsonld": "json-ld", "json": "json-ld", "nq": "nquads", "n-quads": "nquads",
           "ttl": "turtle", "rdf": "xml", "rdfxml": "xml", "owl": "xml"}


class UsageError(ValueError):
    """Invalid combination of command-line arguments (exit code 2)."""


def _flags(parser: argparse.ArgumentParser, *, suppress: bool = False) -> None:
    default = argparse.SUPPRESS if suppress else False
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verbose", action="store_true", default=default, help="Show detailed diagnostics and test outcomes on stderr.")
    group.add_argument("--quiet", action="store_true", default=default, help="Suppress successful validation and conformance summaries.")


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input", metavar="INPUT", help="UTF-8 input file, HTTP(S) URL, or - for stdin.")
    parser.add_argument("--base", metavar="IRI", help="Base IRI for resolving relative identifiers (defaults to the input location).")
    parser.add_argument("--rdf-direction", choices=("i18n-datatype", "compound-literal", "none"), default="none",
                        help="Direction-literal handling mode (default: none).")


def _json_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ordered", action=argparse.BooleanOptionalAction, default=False,
                        help="Order nodes and unordered values deterministically for fixed blank-node labels.")
    parser.add_argument("--use-native-types", action="store_true", help="Convert eligible XSD literals to JSON booleans/numbers.")
    parser.add_argument("--use-rdf-type", action="store_true", help="Keep rdf:type as a predicate instead of @type.")
    parser.add_argument("--schema-org", action="store_true", help="Lossy OWL vocabulary projection to a Schema.org extension.")
    parser.add_argument("--indent", type=int, default=2, metavar="INTEGER", help="JSON indentation in spaces (default: 2).")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON text without indentation.")
    parser.add_argument("--ensure-ascii", action="store_true", help="Escape non-ASCII characters in JSON output.")


def _rdf_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--context", metavar="PATH_OR_URL", help="External JSON-LD context document (UTF-8 file or HTTP(S) URL).")
    parser.add_argument("--generalized-rdf", action="store_true", help="Allow RDFLib-supported blank-node predicates.")


def build_parser() -> argparse.ArgumentParser:
    """Build the shared console/module command parser."""
    parser = argparse.ArgumentParser(prog="owl-jsonld", description="Convert RDF datasets and JSON-LD; project OWL vocabularies to Schema.org.")
    parser.add_argument("--version", action="version", version=version("gdsn-tsv-transformer"), help="Print the installed package version and exit.")
    _flags(parser)
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")
    descriptions = {
        "rdf-to-jsonld": "Convert RDF to expanded JSON-LD or a lossy Schema.org projection.",
        "jsonld-to-rdf": "Parse JSON-LD into RDF, preserving named graphs.",
        "convert": "Infer RDF/JSON-LD conversion direction from input and output formats.",
        "validate": "Parse RDF or JSON-LD without writing a converted document.",
        "formats": "List RDFLib parser/serializer formats and graph/dataset capabilities.",
        "test-w3c": "Run the bundled or supplied W3C From RDF manifest.",
        "version": "Print the installed package version.",
    }
    sub = {name: commands.add_parser(name, help=desc, description=desc) for name, desc in descriptions.items()}
    for child in sub.values():
        _flags(child, suppress=True)
    for name in ("rdf-to-jsonld", "jsonld-to-rdf", "convert", "validate"):
        _common(sub[name])
    for name in ("rdf-to-jsonld", "jsonld-to-rdf"):
        sub[name].add_argument("-o", "--output", default="-", metavar="PATH", help="Output file or - for stdout (default: -).")
    for name in ("rdf-to-jsonld", "jsonld-to-rdf", "convert"):
        sub[name].add_argument("--force", action="store_true", help="Allow overwriting an existing output file.")
    for name in ("rdf-to-jsonld", "convert"):
        _json_options(sub[name])
    for name in ("jsonld-to-rdf", "convert"):
        _rdf_options(sub[name])
    for name in ("rdf-to-jsonld", "validate"):
        sub[name].add_argument("-f", "--input-format", metavar="FORMAT", help="RDFLib input format; required for stdin when unknown.")
    sub["jsonld-to-rdf"].add_argument("-f", "--output-format", metavar="FORMAT", help="RDFLib output format; defaults to extension, N-Quads for datasets, or Turtle.")
    sub["convert"].add_argument("output", metavar="OUTPUT", help="Output file or - for stdout.")
    sub["convert"].add_argument("--input-format", metavar="FORMAT", help="Explicit input format instead of filename inference.")
    sub["convert"].add_argument("--output-format", metavar="FORMAT", help="Explicit output format instead of filename inference.")
    sub["test-w3c"].add_argument("--manifest", default=DEFAULT_MANIFEST, metavar="PATH_OR_URL", help="From RDF manifest (default: bundled offline fixtures).")
    sub["test-w3c"].add_argument("--filter", metavar="PATTERN", help="Test identifier substring or shell wildcard pattern.")
    sub["test-w3c"].add_argument("--fail-fast", action="store_true", help="Stop after the first failed test.")
    sub["test-w3c"].add_argument("--offline", action="store_true", help="Reject all network fixture reads.")
    sub["test-w3c"].add_argument("--report", metavar="PATH", help="Write a JSON report to a new file, or - for stdout.")
    return parser


def _format(explicit: str | None, source: str) -> str | None:
    value = explicit or guess_format(urlparse(source).path, fmap={"jsonld": "json-ld", "json": "json-ld", "owl": "xml", "nq": "nquads"}) or guess_format(urlparse(source).path)
    return ALIASES.get(value, value) if value else None


def _read(source: str) -> str:
    return sys.stdin.read() if source == "-" else read_resource(source)


def _base(source: str, explicit: str | None) -> str | None:
    if explicit or source == "-":
        return explicit
    return source if urlparse(source).scheme in ("http", "https") else Path(source).resolve().as_uri()


def _write(text: str, destination: str, force: bool = False) -> None:
    if destination == "-":
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        return
    target = Path(destination)
    # Publish only complete output, and make no-overwrite atomic across writers.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                     dir=target.parent, prefix=".owl-jsonld-", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(text)
            if not text.endswith("\n"):
                stream.write("\n")
            stream.flush()
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        if force:
            os.replace(temporary, target)
        else:
            os.link(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def _json(source: str) -> Any:
    try:
        return strict_json(_read(source))
    except (ValueError, UnicodeError) as exc:
        raise InvalidInputError(f"Invalid JSON: {exc}") from exc


def _parse(args: argparse.Namespace, input_format: str) -> Graph:
    base = _base(args.input, args.base)
    direction = None if args.rdf_direction == "none" else args.rdf_direction
    if input_format in JSONLD_FORMATS:
        context_source = getattr(args, "context", None)
        context = _json(context_source) if context_source else None
        if context_source:
            if "@direction" in json.dumps(context):
                raise UnsupportedOptionError("Context-level @direction is not supported; use expanded values")
            # Retain the context document's location so RDFLib can resolve nested
            # relative context references against it, not against the RDF input.
            context = _base(context_source, None)
        return to_rdf(_json(args.input), base=base, context=context,
                      rdf_direction=direction, generalized_rdf=getattr(args, "generalized_rdf", False))
    try:
        plugin.get(input_format, Parser)
    except plugin.PluginException as exc:
        raise UsageError(f"Unknown input format {input_format!r}; see 'owl-jsonld formats'") from exc
    return parse_rdf(_read(args.input), format=input_format, base=base)


def _has_named(graph: Graph) -> bool:
    return isinstance(graph, Dataset) and any(g.identifier != graph.default_graph.identifier for g in graph.graphs())


def _serialize(graph: Graph, output_format: str) -> str:
    try:
        plugin.get(output_format, Serializer)
    except plugin.PluginException as exc:
        raise UsageError(f"Unknown output format {output_format!r}; see 'owl-jsonld formats'") from exc
    if _has_named(graph) and output_format not in DATASET_FORMATS:
        raise UnsupportedOptionError(f"Output format {output_format!r} would lose named graphs; choose trig, nquads, or trix")
    if isinstance(graph, Dataset) and output_format not in DATASET_FORMATS:
        graph = graph.default_graph
    elif not isinstance(graph, Dataset) and output_format in DATASET_FORMATS:
        dataset = Dataset()
        for triple in graph:
            dataset.default_graph.add(triple)
        graph = dataset
    try:
        return graph.serialize(format=output_format)
    except Exception as exc:
        raise JsonLdError(f"RDF serialization failed: {exc}") from exc


def _convert(args: argparse.Namespace) -> None:
    input_format = "json-ld" if args.command == "jsonld-to-rdf" else _format(args.input_format, args.input)
    if not input_format:
        raise UsageError("Cannot infer input format; supply --input-format (required for stdin)")
    output_format = "json-ld" if args.command == "rdf-to-jsonld" else _format(args.output_format, args.output)
    if args.command == "convert" and (not output_format or (input_format in JSONLD_FORMATS) == (output_format in JSONLD_FORMATS)):
        raise UsageError("Ambiguous conversion: specify --input-format and --output-format with exactly one JSON-LD format")
    if args.command == "jsonld-to-rdf" and output_format in JSONLD_FORMATS:
        raise UsageError("jsonld-to-rdf requires a non-JSON-LD output format; choose turtle, trig, or nquads")
    schema = getattr(args, "schema_org", False)
    if schema and (input_format in JSONLD_FORMATS or output_format not in JSONLD_FORMATS):
        raise UsageError("--schema-org requires RDF/OWL input and JSON-LD output")
    if args.command == "rdf-to-jsonld" and input_format in JSONLD_FORMATS:
        raise UsageError("rdf-to-jsonld requires RDF input; use jsonld-to-rdf for JSON-LD")
    if getattr(args, "indent", 0) < 0:
        raise UsageError("--indent must be nonnegative")
    if args.command == "convert":
        if output_format in JSONLD_FORMATS and (args.context or args.generalized_rdf):
            raise UsageError("--context and --generalized-rdf apply only to JSON-LD input")
        if input_format in JSONLD_FORMATS and (args.use_native_types or args.use_rdf_type or args.ordered or args.compact or args.ensure_ascii or args.indent != 2):
            raise UsageError("JSON output options apply only when the output is JSON-LD")
    if schema and (args.use_native_types or args.use_rdf_type or args.rdf_direction != "none"):
        raise UsageError("--schema-org does not use native-types, rdf-type, or rdf-direction conversion options")
    graph = _parse(args, input_format)
    if output_format in JSONLD_FORMATS:
        document = owl_to_schema_org(graph, ordered=args.ordered) if schema else from_rdf(
            graph, ordered=args.ordered, use_native_types=args.use_native_types,
            use_rdf_type=args.use_rdf_type, rdf_direction=None if args.rdf_direction == "none" else args.rdf_direction,
        )
        text = json.dumps(document, ensure_ascii=args.ensure_ascii, allow_nan=False,
                          indent=None if args.compact else args.indent,
                          separators=(",", ":") if args.compact else None)
    else:
        text = _serialize(graph, output_format or ("nquads" if _has_named(graph) else "turtle"))
    _write(text, args.output, args.force)


def _formats() -> None:
    readers = {str(p.name) for p in plugin.plugins(None, Parser)}
    writers = {str(p.name) for p in plugin.plugins(None, Serializer)}
    print("FORMAT\tREAD\tWRITE\tGRAPH\tDATASET")
    for name in sorted(readers | writers):
        print(f"{name}\t{'yes' if name in readers else '-'}\t{'yes' if name in writers else '-'}\tyes\t{'yes' if name in DATASET_FORMATS else 'no/unknown'}")


def _tests(args: argparse.Namespace) -> int:
    report = run_suite(args.manifest, pattern=args.filter, offline=args.offline, fail_fast=args.fail_fast)
    if not report["total"]:
        raise UsageError("No FromRDFTest cases matched the manifest/filter")
    for result in report["results"]:
        if result["status"] == "failed" or (args.verbose and not args.quiet):
            print(f"{result['identifier']}: {result['status']}\n{result['detail']}", file=sys.stderr)
    if not args.quiet:
        print("W3C From RDF: " + ", ".join(f"{report[key]} {key}" for key in ("passed", "failed", "skipped", "total")), file=sys.stderr)
    if args.report:
        _write(json.dumps(report, indent=2, ensure_ascii=False), args.report)
    return 1 if report["failed"] else 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI with exit codes 0 success, 1 processing, 2 usage, 3 I/O."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.verbose and args.quiet:
        parser.error("--verbose and --quiet cannot be combined")
    if not args.command:
        parser.print_help()
        return 0
    try:
        if args.command == "version":
            print(version("gdsn-tsv-transformer"))
        elif args.command == "formats":
            _formats()
        elif args.command == "test-w3c":
            return _tests(args)
        elif args.command == "validate":
            input_format = _format(args.input_format, args.input)
            if not input_format:
                raise UsageError("Cannot infer input format; supply --input-format")
            _parse(args, input_format)
            if not args.quiet:
                print(f"{args.input}: valid {input_format}", file=sys.stderr)
        else:
            _convert(args)
        return 0
    except UsageError as exc:
        print(f"owl-jsonld: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError) as exc:
        print(f"owl-jsonld: I/O error: {exc}", file=sys.stderr)
        return 3
    except (JsonLdError, ValueError, TypeError) as exc:
        source = getattr(args, "input", getattr(args, "manifest", "input"))
        code = f" [{exc.code}]" if args.verbose and isinstance(exc, JsonLdError) else ""
        print(f"{source}: {exc}{code}", file=sys.stderr)
        return 1
