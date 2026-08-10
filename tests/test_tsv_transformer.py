from __future__ import annotations

import unittest
from pathlib import Path

from gdsn_tsv_transformer.cli import GdsnTransformer


INPUT_DIR = Path("artefacts/GDSN_Current_v3.1.35")


class GdsnTsvTransformerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output = GdsnTransformer(INPUT_DIR).transform()
        cls.attributes = {row["Curie"]: row for row in cls.output.attributes}
        cls.datatypes = {row["Curie"]: row for row in cls.output.datatypes}
        cls.enumerations = {row["Curie"] for row in cls.output.enumerations}

    def test_carrefour_extended_code_attributes_resolve_to_enumerations(self) -> None:
        examples = {
            "gdsn:extAttr1084": "gdsn:extCode_maximumRange",
            "gdsn:extAttr1115": "gdsn:extCode_voltageRatingCode",
        }
        for attr_curie, enum_curie in examples.items():
            with self.subTest(attr_curie=attr_curie):
                self.assertEqual(self.attributes[attr_curie]["Class"], "gdsn:extGroup_Carrefour")
                self.assertEqual(self.attributes[attr_curie]["ClassEnumOrPrimitiveType"], enum_curie)
                self.assertIn(enum_curie, self.enumerations)
                self.assertEqual(self.attributes[attr_curie]["MinLength"], "")
                self.assertEqual(self.attributes[attr_curie]["MaxLength"], "")

    def test_carrefour_string_extended_attributes_keep_length_facets(self) -> None:
        row = self.attributes["gdsn:extAttr1054"]
        self.assertEqual(row["Class"], "gdsn:extGroup_Carrefour")
        self.assertEqual(row["ClassEnumOrPrimitiveType"], "xsd:string")
        self.assertEqual(row["MinLength"], "")
        self.assertEqual(row["MaxLength"], "")

    def test_attribute_limits_use_named_synthetic_datatypes(self) -> None:
        examples = {
            "gdsn:a-1712713250": ("registrationAgency", "gdsn:dt_string_MinLength1_MaxLength200", "200"),
            "gdsn:a-72181753": ("registrationNumber", "gdsn:dt_string_MinLength1_MaxLength70", "70"),
        }
        for attr_curie, (name, datatype_curie, max_length) in examples.items():
            with self.subTest(attr_curie=attr_curie):
                row = self.attributes[attr_curie]
                self.assertEqual(row["Name"], name)
                self.assertEqual(row["Class"], "gdsn:c1753294155")
                self.assertEqual(row["ClassEnumOrPrimitiveType"], datatype_curie)
                self.assertEqual(row["MinLength"], "")
                self.assertEqual(row["MaxLength"], "")

                datatype = self.datatypes[datatype_curie]
                self.assertEqual(datatype["BaseDatatype"], "xsd:string")
                self.assertEqual(datatype["MinLength"], "1")
                self.assertEqual(datatype["MaxLength"], max_length)

    def test_extended_attribute_limits_are_preserved_without_facets(self) -> None:
        row = self.attributes["gdsn:extAttr688"]
        self.assertEqual(row["Class"], "gdsn:extGroup_US_FoodService")
        self.assertEqual(row["Name"], "notSignificantSourceOfNutrient")
        self.assertEqual(row["ClassEnumOrPrimitiveType"], "xsd:string")
        self.assertEqual(row["MinMultiplicity"], "0")
        self.assertEqual(row["MaxMultiplicity"], "*")
        self.assertEqual(row["MinLength"], "")
        self.assertEqual(row["MaxLength"], "")


if __name__ == "__main__":
    unittest.main()
