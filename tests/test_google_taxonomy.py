from __future__ import annotations

import csv
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from gdsn_tsv_transformer.google_taxonomy import GoogleTaxonomyTransformer, main


INPUT_FILE = Path("artefacts/google/taxonomy-with-ids.en-GB.txt")


class GoogleTaxonomyTransformerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not INPUT_FILE.exists():
            raise unittest.SkipTest(f"{INPUT_FILE} is required")
        cls.transformer = GoogleTaxonomyTransformer(INPUT_FILE)
        cls.output = cls.transformer.transform()
        cls.classes = {row["Curie"]: row for row in cls.output.classes}
        cls.annotations = {
            (row["TargetCurie"], row["AnnotationProperty"]): row
            for row in cls.output.annotations
        }

    def test_google_taxonomy_counts_and_root(self) -> None:
        self.assertEqual(self.transformer.version, "2021-09-21")
        self.assertEqual(len(self.transformer.categories), 5595)
        self.assertEqual(len(self.output.classes), 5596)
        self.assertEqual(self.output.attributes, [])
        self.assertEqual(self.output.datatypes, [])
        self.assertEqual(self.output.enumerations, [])
        self.assertEqual(self.output.enum_values, [])
        self.assertEqual(self.output.diagnostics, [])

        root = self.classes["google:GoogleProductTaxonomyCategory"]
        self.assertEqual(root["Name"], "Google Product Taxonomy Category")
        self.assertEqual(root["ParentNames"], "")

    def test_google_taxonomy_hierarchy_rows(self) -> None:
        self.assertEqual(self.classes["google:1"]["Name"], "Animals & Pet Supplies")
        self.assertEqual(self.classes["google:1"]["ParentNames"], "google:GoogleProductTaxonomyCategory")
        self.assertEqual(self.classes["google:2"]["ParentNames"], "google:1")
        self.assertEqual(self.classes["google:4"]["ParentNames"], "google:2")
        self.assertEqual(self.classes["google:3367"]["ParentNames"], "google:4")
        self.assertEqual(self.classes["google:543683"]["Name"], "Prescription Cat Food")
        self.assertEqual(self.classes["google:543683"]["ParentNames"], "google:3367")

    def test_google_taxonomy_annotations(self) -> None:
        self.assertEqual(self.annotations[("google:543683", "google:categoryId")]["Value"], "543683")
        self.assertEqual(self.annotations[("google:543683", "google:level")]["Value"], "5")
        self.assertEqual(self.annotations[("google:543683", "google:level")]["Datatype"], "xsd:integer")
        self.assertEqual(self.annotations[("google:543683", "google:parentCategoryId")]["Value"], "3367")
        self.assertEqual(self.annotations[("google:543683", "google:isLeaf")]["Value"], "true")
        self.assertEqual(self.annotations[("google:543683", "google:isLeaf")]["Datatype"], "xsd:boolean")
        self.assertEqual(self.annotations[("google:543683", "google:taxonomyVersion")]["Value"], "2021-09-21")

    def test_cli_writes_google_module(self) -> None:
        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--input-file", str(INPUT_FILE), "--output-dir", temp_dir])

            self.assertEqual(exit_code, 0)
            self.assertIn("Wrote Google Product Taxonomy TSV artefacts", stdout.getvalue())
            module_dir = Path(temp_dir) / "google"
            for filename in [
                "Classes.tsv",
                "Attributes.tsv",
                "Datatypes.tsv",
                "Enumerations.tsv",
                "EnumerationNamedValues.tsv",
                "AnnotationProperties.tsv",
                "Annotations.tsv",
                "diagnostics.tsv",
            ]:
                self.assertTrue((module_dir / filename).exists(), filename)

            with (module_dir / "Classes.tsv").open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f, delimiter="\t"))
            self.assertEqual(len(rows), 5596)
            self.assertEqual(rows[0]["Curie"], "google:GoogleProductTaxonomyCategory")


if __name__ == "__main__":
    unittest.main()
