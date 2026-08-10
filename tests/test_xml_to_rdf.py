from __future__ import annotations

import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

from gdsn_tsv_transformer.xml_to_rdf import GDSN, GPC, convert, main


XML_PATH = Path("artefacts/KATO/add.xml")
GDSN_PATH = Path("build/gdsn.ttl")
GPC_PATH = Path("build/gpc.ttl")
BASE_IRI = "urn:gs1:test:kato:"


class GdsnXmlToRdfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        missing = [path for path in [XML_PATH, GDSN_PATH, GPC_PATH] if not path.exists()]
        if missing:
            raise unittest.SkipTest(f"Required test artefacts are missing: {', '.join(str(path) for path in missing)}")

    def test_kato_instance_graph_and_extension_report(self) -> None:
        graph, report = convert(XML_PATH, GDSN_PATH, GPC_PATH, BASE_IRI, "kato")

        parent = URIRef(BASE_IRI + "gtin/25196100024882")
        child = URIRef(BASE_IRI + "gtin/25196100024899")

        self.assertIn((parent, RDF.type, GDSN.c863999331), graph)
        self.assertIn((parent, RDF.type, GPC["10000002"]), graph)
        self.assertIn((parent, GDSN.a5339, Literal("25196100024882", datatype=GDSN.c1450)), graph)
        self.assertIn((child, RDF.type, GDSN.c863999331), graph)
        self.assertIn((child, RDF.type, GPC["10000002"]), graph)
        self.assertIn((child, GDSN.a5339, Literal("25196100024899", datatype=GDSN.c1450)), graph)

        trade_items = {item["gtin"]: item["gpc_brick"] for item in report["trade_items"]}
        self.assertEqual(trade_items, {"25196100024882": "10000002", "25196100024899": "10000002"})
        self.assertEqual(report["diagnostics"], [])

        extension_modules = {item["gtin"]: [module["module"] for module in item["modules"]] for item in report["extension_modules"]}
        self.assertIn("tradeItemMeasurementsModule", extension_modules["25196100024882"])
        self.assertIn("tradeItemDataCarrierAndIdentificationModule", extension_modules["25196100024899"])

        child_extension_values = [
            value
            for item in report["extension_modules"]
            if item["gtin"] == "25196100024899"
            for module in item["modules"]
            for value in module["values"]
        ]
        self.assertIn(
            {"path": "dataCarrier/dataCarrierTypeCode", "name": "dataCarrierTypeCode", "value": "ITF_14", "attributes": {}},
            child_extension_values,
        )

        Graph().parse(data=graph.serialize(format="turtle"), format="turtle")

    def test_cli_writes_separate_instance_and_reference_reports(self) -> None:
        with TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "instances.ttl"
            extension_report = Path(temp_dir) / "extensions.json"
            report_json = Path(temp_dir) / "report.json"
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--input",
                        str(XML_PATH),
                        "--gdsn",
                        str(GDSN_PATH),
                        "--gpc",
                        str(GPC_PATH),
                        "--output",
                        str(output),
                        "--extension-report",
                        str(extension_report),
                        "--report-json",
                        str(report_json),
                        "--print-extensions",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output.exists())
            self.assertTrue(extension_report.exists())
            self.assertTrue(report_json.exists())
            self.assertIn("tradeItemMeasurementsModule", stdout.getvalue())
            self.assertEqual("", stderr.getvalue())

            Graph().parse(output, format="turtle")
            report = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual(report["output"], str(output))
            self.assertEqual(report["validation"], {"parse": True})


if __name__ == "__main__":
    unittest.main()
