from __future__ import annotations

import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD
from rdflib.namespace import OWL

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
        ontology = URIRef(BASE_IRI + "ontology")

        self.assertIn((ontology, OWL.imports, URIRef(str(GDSN))), graph)
        self.assertIn((ontology, OWL.imports, URIRef(str(GPC))), graph)
        self.assertIn((parent, RDF.type, GDSN.c863999331), graph)
        self.assertIn((parent, RDF.type, GPC["10000002"]), graph)
        self.assertIn((parent, GDSN.a5339, Literal("25196100024882", datatype=XSD.string)), graph)
        self.assertIn((child, RDF.type, GDSN.c863999331), graph)
        self.assertIn((child, RDF.type, GPC["10000002"]), graph)
        self.assertIn((child, GDSN.a5339, Literal("25196100024899", datatype=XSD.string)), graph)
        self.assert_kato_extension_modules(graph, parent, "25196100024882", "10", "20")
        self.assert_kato_extension_modules(graph, child, "25196100024899", "1", "1")
        self.assertIn(
            (
                URIRef(BASE_IRI + "extension/25196100024899/dataCarrier/1"),
                GDSN.a874787245,
                GDSN.cv170767,
            ),
            graph,
        )

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

    def assert_kato_extension_modules(self, graph: Graph, trade_item: URIRef, gtin: str, depth: str, net_content: str) -> None:
        info = URIRef(BASE_IRI + f"tradeItemInformation/{gtin}")
        delivery_module = URIRef(BASE_IRI + f"extension/{gtin}/deliveryPurchasingInformationModule")
        delivery_info = URIRef(BASE_IRI + f"extension/{gtin}/deliveryPurchasingInformation")
        description_module = URIRef(BASE_IRI + f"extension/{gtin}/tradeItemDescriptionModule")
        description_info = URIRef(BASE_IRI + f"extension/{gtin}/tradeItemDescriptionInformation")
        brand_info = URIRef(BASE_IRI + f"extension/{gtin}/brandNameInformation")
        measurements_module = URIRef(BASE_IRI + f"extension/{gtin}/tradeItemMeasurementsModule")
        measurements = URIRef(BASE_IRI + f"extension/{gtin}/tradeItemMeasurements")
        weight = URIRef(BASE_IRI + f"extension/{gtin}/tradeItemWeight")
        functional_name = URIRef(BASE_IRI + f"value/{gtin}/functionalName")
        depth_value = URIRef(BASE_IRI + f"value/{gtin}/depth")
        net_content_value = URIRef(BASE_IRI + f"value/{gtin}/netContent")
        gross_weight_value = URIRef(BASE_IRI + f"value/{gtin}/grossWeight")

        self.assertIn((trade_item, GDSN["assoc_863999331_1352305416_11"], info), graph)
        for module in [delivery_module, description_module, measurements_module]:
            self.assertIn((info, GDSN.extensionModule, module), graph)
            self.assertIn((module, RDF.type, GDSN.GDSNExtensionModule), graph)

        self.assertIn((delivery_module, RDF.type, GDSN.c1952808552), graph)
        self.assertIn((delivery_module, GDSN["assoc_1952808552_1362_1"], delivery_info), graph)
        self.assertIn((delivery_info, GDSN.a1727163091, Literal("2026-07-11T04:41:53.737+00:00", datatype=XSD.dateTime)), graph)

        self.assertIn((description_module, RDF.type, GDSN.c1343046870), graph)
        self.assertIn((description_module, GDSN["assoc_1343046870_1204161147_1"], description_info), graph)
        self.assertIn((description_info, GDSN.a1986433438, functional_name), graph)
        self.assertIn((functional_name, RDF.type, GDSN.c1441), graph)
        self.assertIn((functional_name, RDF.value, Literal("Fruit – Unprepared/Unprocessed", lang="en")), graph)
        qualifier_datatype = XSD.string
        self.assertIn((functional_name, GDSN.a7139, Literal("en", datatype=qualifier_datatype)), graph)
        self.assertIn((description_info, GDSN["assoc_1204161147_1350303678_4"], brand_info), graph)
        self.assertIn((brand_info, GDSN.a308904173, Literal("Kiln_TT9", datatype=XSD.string)), graph)

        self.assertIn((measurements_module, RDF.type, GDSN["c-1559145472"]), graph)
        self.assertIn((measurements_module, GDSN["assoc_-1559145472_-1443794077_1"], measurements), graph)
        self.assertIn((measurements, GDSN.a652919722, depth_value), graph)
        self.assertIn((depth_value, RDF.type, GDSN.c1490), graph)
        self.assertIn((depth_value, RDF.value, Literal(depth, datatype=XSD.decimal)), graph)
        self.assertIn((depth_value, GDSN.a7085, Literal("MMT", datatype=qualifier_datatype)), graph)
        self.assertIn((measurements, GDSN["a-930082660"], net_content_value), graph)
        self.assertIn((net_content_value, RDF.type, GDSN.c1490), graph)
        self.assertIn((net_content_value, RDF.value, Literal(net_content, datatype=XSD.decimal)), graph)
        self.assertIn((net_content_value, GDSN.a7085, Literal("H87", datatype=qualifier_datatype)), graph)
        self.assertIn((measurements, GDSN["assoc_-1443794077_-113081611_1"], weight), graph)
        self.assertIn((weight, GDSN["a-387099093"], gross_weight_value), graph)
        self.assertIn((gross_weight_value, RDF.type, GDSN.c1490), graph)
        self.assertIn((gross_weight_value, RDF.value, Literal(net_content, datatype=XSD.decimal)), graph)
        self.assertIn((gross_weight_value, GDSN.a7085, Literal("KGM", datatype=qualifier_datatype)), graph)

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
