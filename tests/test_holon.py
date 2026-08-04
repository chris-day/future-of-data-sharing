from __future__ import annotations

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from pyshacl import validate
from rdflib import Graph

from gdsn_tsv_transformer.holon import (
    add_gpc_brick_shape,
    bind_common,
    build_validation_graphs,
    load_graph,
    main,
)


GPC_PATH = Path("build/gpc.ttl")


class GpcBrickShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not GPC_PATH.exists():
            raise unittest.SkipTest(f"{GPC_PATH} is required; generate it before running tests")
        cls.gpc_graph = load_graph(GPC_PATH)

    def assert_brick_shape_validates(self, brick_code: str, expected_label: str, expected_attribute_count: int) -> None:
        shapes = Graph()
        bind_common(shapes)
        report = add_gpc_brick_shape(shapes, self.gpc_graph, brick_code)

        self.assertEqual(report["brick_label"], expected_label)
        self.assertEqual(len(report["attribute_types"]), expected_attribute_count)

        Graph().parse(data=shapes.serialize(format="turtle"), format="turtle")
        conforming, broken = build_validation_graphs(self.gpc_graph, brick_code, include_gdsn=False)
        self.assertTrue(validate(data_graph=Graph(), shacl_graph=shapes, inference="none")[0])
        self.assertTrue(validate(data_graph=conforming, shacl_graph=shapes, inference="none")[0])
        self.assertFalse(validate(data_graph=broken, shacl_graph=shapes, inference="none")[0])

    def test_example_brick_shapes_validate(self) -> None:
        examples = [
            ("10000030", "Cheese (Frozen)", 6),
            ("10001198", "Smartphones", 2),
            ("10000159", "Beer", 6),
            ("10000043", "Sugar/Sugar Substitutes (Shelf Stable)", 1),
        ]
        for brick_code, expected_label, expected_attribute_count in examples:
            with self.subTest(brick_code=brick_code):
                self.assert_brick_shape_validates(brick_code, expected_label, expected_attribute_count)

    def test_cli_stdout_mode(self) -> None:
        with TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(["10000043", "--no-validate", "--report-json", str(report_path)])
            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())
            self.assertIn("gpc-shapes:Brick10000043Shape", stdout.getvalue())
            self.assertIn('"output": "stdout"', stderr.getvalue())

    def test_write_tests_requires_output(self) -> None:
        with self.assertRaises(SystemExit):
            main(["10000043", "--write-tests"])


if __name__ == "__main__":
    unittest.main()
