from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .cli import (
    ANNOTATIONS_HEADER,
    CLASSES_HEADER,
    DIAGNOSTICS_HEADER,
    OutputSet,
    add_annotation,
    blank_row,
    clean_name,
    clean_text,
    write_output_set,
)


DEFAULT_INPUT = Path("artefacts/google/taxonomy-with-ids.en-GB.txt")
DEFAULT_OUTPUT_DIR = Path("build/gdsn-tsv")
DEFAULT_MODULE = "google"
DEFAULT_PREFIX = "google"
ROOT_LOCAL_NAME = "GoogleProductTaxonomyCategory"


@dataclass(frozen=True)
class GoogleCategory:
    source_line: int
    category_id: str
    path: tuple[str, ...]

    @property
    def level(self) -> int:
        return len(self.path)

    @property
    def label(self) -> str:
        return self.path[-1]

    @property
    def path_text(self) -> str:
        return " > ".join(self.path)

    @property
    def parent_path_text(self) -> str:
        return " > ".join(self.path[:-1])


def google_curie(prefix: str, local: str) -> str:
    return f"{prefix}:{local}"


def parse_google_taxonomy(path: Path) -> tuple[str, list[GoogleCategory], list[dict[str, str]]]:
    version = ""
    categories: list[GoogleCategory] = []
    diagnostics: list[dict[str, str]] = []
    pattern = re.compile(r"^(\d+)\s+-\s+(.+)$")

    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if line.startswith("# Google_Product_Taxonomy_Version:"):
                version = clean_text(line.split(":", 1)[1])
            continue
        match = pattern.fullmatch(line)
        if not match:
            diagnostics.append(
                {
                    "Severity": "ERROR",
                    "SourceFile": str(path),
                    "SourceId": str(line_no),
                    "TargetCurie": "",
                    "Field": "line",
                    "Value": clean_text(line),
                    "Message": "Malformed Google taxonomy row; expected '<id> - <path>'.",
                }
            )
            continue
        category_id, path_text = match.groups()
        parts = tuple(clean_name(part) for part in path_text.split(">"))
        parts = tuple(part for part in parts if part)
        if not parts:
            diagnostics.append(
                {
                    "Severity": "ERROR",
                    "SourceFile": str(path),
                    "SourceId": category_id,
                    "TargetCurie": "",
                    "Field": "path",
                    "Value": path_text,
                    "Message": "Google taxonomy row has no category path.",
                }
            )
            continue
        categories.append(GoogleCategory(line_no, category_id, parts))

    if not version:
        diagnostics.append(
            {
                "Severity": "WARNING",
                "SourceFile": str(path),
                "SourceId": "",
                "TargetCurie": "",
                "Field": "version",
                "Value": "",
                "Message": "Google taxonomy version header was not found.",
            }
        )
    return version, categories, diagnostics


class GoogleTaxonomyTransformer:
    def __init__(self, input_file: Path, prefix: str = DEFAULT_PREFIX) -> None:
        self.input_file = input_file
        self.prefix = prefix.rstrip(":")
        self.root_curie = google_curie(self.prefix, ROOT_LOCAL_NAME)
        self.version, self.categories, diagnostics = parse_google_taxonomy(input_file)
        self.output = OutputSet(diagnostics=diagnostics)

    def transform(self) -> OutputSet:
        path_to_category = {category.path_text: category for category in self.categories}
        id_counts = Counter(category.category_id for category in self.categories)
        path_counts = Counter(category.path_text for category in self.categories)
        child_counts: defaultdict[str, int] = defaultdict(int)

        for category in self.categories:
            if category.parent_path_text:
                parent = path_to_category.get(category.parent_path_text)
                if parent is None:
                    self.add_diagnostic(category, "parent", category.parent_path_text, "Parent category path is missing.")
                else:
                    child_counts[parent.category_id] += 1

        self.add_annotation_properties()
        self.add_root_class()

        for category in self.categories:
            curie = self.category_curie(category.category_id)
            if id_counts[category.category_id] > 1:
                self.add_diagnostic(category, "category_id", category.category_id, "Duplicate Google taxonomy category ID.")
            if path_counts[category.path_text] > 1:
                self.add_diagnostic(category, "path", category.path_text, "Duplicate Google taxonomy path.")

            parent_curie = self.root_curie
            if category.parent_path_text:
                parent = path_to_category.get(category.parent_path_text)
                parent_curie = self.category_curie(parent.category_id) if parent is not None else ""

            row = blank_row(CLASSES_HEADER)
            row.update(
                {
                    "Curie": curie,
                    "Name": category.label,
                    "ParentNames": parent_curie,
                    "Definition": f"Google Product Taxonomy category: {category.path_text}",
                }
            )
            self.output.classes.append(row)
            self.add_category_annotations(category, child_counts[category.category_id] == 0)

        return self.output

    def category_curie(self, category_id: Any) -> str:
        return google_curie(self.prefix, str(category_id))

    def add_annotation_properties(self) -> None:
        self.output.annotation_properties.extend(
            [
                {"Curie": f"{self.prefix}:categoryId", "Name": "Category ID", "Definition": "Google Product Taxonomy numeric category identifier."},
                {"Curie": f"{self.prefix}:level", "Name": "Level", "Definition": "One-based depth in the Google Product Taxonomy path."},
                {"Curie": f"{self.prefix}:path", "Name": "Path", "Definition": "Full Google Product Taxonomy category path."},
                {"Curie": f"{self.prefix}:parentCategoryId", "Name": "Parent category ID", "Definition": "Immediate parent Google Product Taxonomy category identifier."},
                {"Curie": f"{self.prefix}:isLeaf", "Name": "Is leaf", "Definition": "Whether the category has no child categories in this taxonomy version."},
                {"Curie": f"{self.prefix}:taxonomyVersion", "Name": "Taxonomy version", "Definition": "Google Product Taxonomy source version."},
                {"Curie": f"{self.prefix}:sourceLine", "Name": "Source line", "Definition": "Source line number in taxonomy-with-ids.en-GB.txt."},
            ]
        )

    def add_root_class(self) -> None:
        row = blank_row(CLASSES_HEADER)
        row.update(
            {
                "Curie": self.root_curie,
                "Name": "Google Product Taxonomy Category",
                "Definition": "Root class for Google Product Taxonomy categories.",
            }
        )
        self.output.classes.append(row)
        if self.version:
            add_annotation(self.output.annotations, self.root_curie, f"{self.prefix}:taxonomyVersion", self.version)

    def add_category_annotations(self, category: GoogleCategory, is_leaf: bool) -> None:
        curie = self.category_curie(category.category_id)
        add_annotation(self.output.annotations, curie, f"{self.prefix}:categoryId", category.category_id)
        add_annotation(self.output.annotations, curie, f"{self.prefix}:level", category.level, "xsd:integer")
        add_annotation(self.output.annotations, curie, f"{self.prefix}:path", category.path_text)
        if category.parent_path_text:
            parent = next((item for item in self.categories if item.path_text == category.parent_path_text), None)
            if parent is not None:
                add_annotation(self.output.annotations, curie, f"{self.prefix}:parentCategoryId", parent.category_id)
        add_annotation(self.output.annotations, curie, f"{self.prefix}:isLeaf", str(is_leaf).lower(), "xsd:boolean")
        if self.version:
            add_annotation(self.output.annotations, curie, f"{self.prefix}:taxonomyVersion", self.version)
        add_annotation(self.output.annotations, curie, f"{self.prefix}:sourceLine", category.source_line, "xsd:integer")

    def add_diagnostic(self, category: GoogleCategory, field: str, value: Any, message: str) -> None:
        self.output.diagnostics.append(
            {
                "Severity": "ERROR",
                "SourceFile": str(self.input_file),
                "SourceId": category.category_id,
                "TargetCurie": self.category_curie(category.category_id),
                "Field": field,
                "Value": clean_text(value),
                "Message": message,
            }
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transform Google Product Taxonomy text into uml2semantics TSV artefacts.")
    parser.add_argument("--input-file", type=Path, default=DEFAULT_INPUT, help="Google Product Taxonomy text file.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory to write generated TSV artefacts.")
    parser.add_argument("--module", default=DEFAULT_MODULE, help="Output module subdirectory under --output-dir.")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX, help="CURIE prefix to use for generated Google taxonomy terms.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output = GoogleTaxonomyTransformer(args.input_file, args.prefix).transform()
    target_dir = args.output_dir / args.module
    write_output_set(target_dir, output)
    print(f"Wrote Google Product Taxonomy TSV artefacts to {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
