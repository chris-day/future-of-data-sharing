from __future__ import annotations

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from pyshacl import validate
from rdflib import Graph, Literal, URIRef

from gdsn_tsv_transformer.holon import (
    GDSN,
    SH,
    add_gdsn_trade_item_shape,
    add_gpc_brick_shape,
    bind_common,
    build_validation_graphs,
    gdsn_class_by_label,
    gdsn_object_property_path,
    load_graph,
    main,
)


GPC_PATH = Path("build/gpc.ttl")
GDSN_PATH = Path("build/gdsn.ttl")
KATO_INSTANCE_PATH = Path("build/KATO/kato-instances.ttl")


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

    def test_gdsn_shape_includes_classification_bridge(self) -> None:
        if not GDSN_PATH.exists():
            raise unittest.SkipTest(f"{GDSN_PATH} is required; generate it before running this test")
        gdsn_graph = load_graph(GDSN_PATH)
        shapes = Graph()
        bind_common(shapes)

        report = add_gdsn_trade_item_shape(shapes, gdsn_graph, "10001198")

        self.assertEqual(report["classification_bridge"]["has_value"], "10001198")
        self.assertTrue((None, SH.hasValue, Literal("10001198")) in shapes)

        Graph().parse(data=shapes.serialize(format="turtle"), format="turtle")
        conforming, broken = build_validation_graphs(self.gpc_graph, "10001198", include_gdsn=True)
        self.assertTrue(validate(data_graph=conforming, shacl_graph=shapes, inference="none")[0])
        self.assertFalse(validate(data_graph=broken, shacl_graph=shapes, inference="none")[0])

    def test_gdsn_sparql_traversal_finds_classification_attribute_path(self) -> None:
        if not GDSN_PATH.exists():
            raise unittest.SkipTest(f"{GDSN_PATH} is required; generate it before running this test")
        gdsn_graph = load_graph(GDSN_PATH)

        target = gdsn_class_by_label(gdsn_graph, "GDSNTradeItemClassificationAttribute")
        self.assertIsNotNone(target)
        path = gdsn_object_property_path(gdsn_graph, GDSN.c863999331, target)

        self.assertEqual(
            [str(part) for part in path],
            [
                "urn:gs1:std:gdsn:assoc_863999331_-1698192853_1",
                "urn:gs1:std:gdsn:assoc_-1698192853_1436526793_2",
            ],
        )

    def test_cli_print_traversal(self) -> None:
        if not GDSN_PATH.exists():
            raise unittest.SkipTest(f"{GDSN_PATH} is required; generate it before running this test")
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "shape.ttl"
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main([
                    "10000030",
                    "--gdsn",
                    str(GDSN_PATH),
                    "--print-traversal",
                    "--no-validate",
                    "--output",
                    str(output_path),
                ])

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertIn("GPC classification attribute traversal", stdout.getvalue())
            self.assertIn("TradeItem", stdout.getvalue())
            self.assertIn("  -> gDSNTradeItemClassification", stdout.getvalue())
            self.assertIn("     GDSNTradeItemClassificationAttribute", stdout.getvalue())

    def test_gdsn_shape_includes_gtin_bridge_when_gtin_is_supplied(self) -> None:
        if not GDSN_PATH.exists():
            raise unittest.SkipTest(f"{GDSN_PATH} is required; generate it before running this test")
        gdsn_graph = load_graph(GDSN_PATH)
        shapes = Graph()
        bind_common(shapes)

        report = add_gdsn_trade_item_shape(shapes, gdsn_graph, "10000030", "09506000134352")

        self.assertEqual(report["classification_bridge"]["has_value"], "10000030")
        self.assertEqual(report["gtin_bridge"]["has_value"], "09506000134352")
        self.assertEqual(report["gtin_bridge"]["gtin_property"], "urn:gs1:std:gdsn:a5339")
        self.assertEqual(report["gtin_bridge"]["datatype"], "urn:gs1:std:gdsn:c1450")
        self.assertTrue((None, SH.hasValue, Literal("10000030")) in shapes)
        self.assertTrue((None, SH.hasValue, Literal("09506000134352", datatype=URIRef("http://www.w3.org/2001/XMLSchema#string"))) in shapes)

        Graph().parse(data=shapes.serialize(format="turtle"), format="turtle")
        conforming, broken = build_validation_graphs(
            self.gpc_graph,
            "10000030",
            include_gdsn=True,
            gtin="09506000134352",
        )
        self.assertTrue(validate(data_graph=conforming, shacl_graph=shapes, inference="none")[0])
        self.assertFalse(validate(data_graph=broken, shacl_graph=shapes, inference="none")[0])

    def test_cli_generates_instance_aware_kato_holon(self) -> None:
        if not GDSN_PATH.exists() or not KATO_INSTANCE_PATH.exists():
            raise unittest.SkipTest("build/gdsn.ttl and build/KATO/kato-instances.ttl are required for this test")
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "kato-instance-aware.shacl.ttl"
            report_path = Path(temp_dir) / "kato-instance-aware.report.json"
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main([
                    "25196100024882",
                    "--input-kind",
                    "gtin",
                    "--instance-data",
                    str(KATO_INSTANCE_PATH),
                    "--instance-base-iri",
                    "urn:gs1:sample:kato:",
                    "--gpc",
                    str(GPC_PATH),
                    "--gdsn",
                    str(GDSN_PATH),
                    "--include-gdsn",
                    "--include-instance-objects",
                    "--output",
                    str(output_path),
                    "--report-json",
                    str(report_path),
                ])

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertTrue(report_path.exists())
            self.assertIn("instance_graph_conforms=True", stdout.getvalue())

            shapes = Graph().parse(output_path, format="turtle")
            root = URIRef("urn:gs1:sample:kato:gtin/25196100024882")
            self.assertTrue((None, SH.targetNode, root) in shapes)
            self.assertTrue((None, SH.path, GDSN["assoc_863999331_652864357_8"]) in shapes)
            self.assertTrue((None, SH.path, GDSN.a5682) in shapes)
            self.assertTrue((None, SH.path, GDSN.extensionModule) in shapes)
            self.assertTrue((None, SH.path, GDSN.a1727163091) in shapes)


if __name__ == "__main__":
    unittest.main()
