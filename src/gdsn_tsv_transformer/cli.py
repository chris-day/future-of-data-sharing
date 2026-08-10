from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


FACET_COLUMNS = [
    "Pattern",
    "MinLength",
    "MaxLength",
    "MinInclusive",
    "MaxInclusive",
    "MinExclusive",
    "MaxExclusive",
    "TotalDigits",
    "FractionDigits",
]

CLASSES_HEADER = [
    "Curie",
    "Name",
    "ParentNames",
    "Definition",
    "IsAbstract",
    "ChoiceOf",
    "ChoiceSemantics",
]
ATTRIBUTES_HEADER = [
    "Class",
    "Curie",
    "Name",
    "ClassEnumOrPrimitiveType",
    "MinMultiplicity",
    "MaxMultiplicity",
    "Definition",
    *FACET_COLUMNS,
]
DATATYPES_HEADER = ["Curie", "Name", "BaseDatatype", "Definition", *FACET_COLUMNS]
ENUMERATIONS_HEADER = ["Curie", "Name", "Definition"]
ENUM_VALUES_HEADER = ["Enumeration", "Curie", "Name", "Definition"]
ANNOTATION_PROPERTIES_HEADER = ["Curie", "Name", "Definition"]
ANNOTATIONS_HEADER = ["TargetCurie", "AnnotationProperty", "Value", "Language", "Datatype"]
DIAGNOSTICS_HEADER = ["Severity", "SourceFile", "SourceId", "TargetCurie", "Field", "Value", "Message"]

XSD_TYPES = {
    "anyURI",
    "base64Binary",
    "boolean",
    "date",
    "dateTime",
    "decimal",
    "duration",
    "float",
    "gDay",
    "gMonth",
    "gMonthDay",
    "gYear",
    "gYearMonth",
    "hexBinary",
    "integer",
    "negativeInteger",
    "nonNegativeInteger",
    "nonPositiveInteger",
    "positiveInteger",
    "string",
    "time",
    "unsignedInt",
}


@dataclass
class OutputSet:
    classes: list[dict[str, str]] = field(default_factory=list)
    attributes: list[dict[str, str]] = field(default_factory=list)
    datatypes: list[dict[str, str]] = field(default_factory=list)
    enumerations: list[dict[str, str]] = field(default_factory=list)
    enum_values: list[dict[str, str]] = field(default_factory=list)
    annotation_properties: list[dict[str, str]] = field(default_factory=list)
    annotations: list[dict[str, str]] = field(default_factory=list)
    diagnostics: list[dict[str, str]] = field(default_factory=list)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8-sig") as f:
        return json.load(f)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_name(value: Any) -> str:
    return clean_text(value)


def local_token(value: Any, fallback: str = "value") -> str:
    text = clean_text(value)
    text = text.lstrip("\ufeff")
    text = re.sub(r"[^0-9A-Za-z_]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        text = fallback
    if text[0].isdigit():
        text = f"_{text}"
    return text


def gdsn_class_curie(source_id: Any) -> str:
    return f"gdsn:c{source_id}"


def gdsn_attribute_curie(source_id: Any) -> str:
    return f"gdsn:a{source_id}"


def gdsn_code_value_curie(source_id: Any) -> str:
    return f"gdsn:cv{source_id}"


def parse_multiplicity(value: Any) -> tuple[str, str, str | None]:
    raw = "" if value is None else str(value).strip()
    if raw == "":
        return "", "", None
    if raw == "1":
        return "1", "1", None
    match = re.fullmatch(r"(\d+)\.\.(\d+|\*)", raw)
    if match:
        return match.group(1), match.group(2), None
    return "", "", f"Malformed multiplicity '{raw}' left blank"


def parse_limit(value: Any, string_like: bool = True) -> tuple[dict[str, str], str | None]:
    raw = "" if value is None else str(value).strip()
    if raw == "":
        return {}, None
    length_match = re.fullmatch(r"\{(\d+)\.\.(\d+)\}", raw)
    if length_match and string_like:
        return {"MinLength": length_match.group(1), "MaxLength": length_match.group(2)}, None
    pattern_match = re.fullmatch(r"\{(\\\\d\{\d+\}|\\d\{\d+\})\}", raw)
    if pattern_match:
        pattern = pattern_match.group(1).replace("\\\\", "\\")
        return {"Pattern": pattern}, None
    return {}, f"Unparsed limit '{raw}' preserved as annotation"


def blank_row(header: Iterable[str]) -> dict[str, str]:
    return {column: "" for column in header}


def annotation(target: str, prop: str, value: Any, datatype: str = "") -> dict[str, str] | None:
    text = clean_text(value)
    if not target or not prop or text == "":
        return None
    return {
        "TargetCurie": target,
        "AnnotationProperty": prop,
        "Value": text,
        "Language": "",
        "Datatype": datatype,
    }


def add_annotation(rows: list[dict[str, str]], target: str, prop: str, value: Any, datatype: str = "") -> None:
    row = annotation(target, prop, value, datatype)
    if row:
        rows.append(row)


def add_diag(
    output: OutputSet,
    severity: str,
    source_file: str,
    source_id: Any,
    target_curie: str,
    field_name: str,
    value: Any,
    message: str,
) -> None:
    output.diagnostics.append(
        {
            "Severity": severity,
            "SourceFile": source_file,
            "SourceId": clean_text(source_id),
            "TargetCurie": target_curie,
            "Field": field_name,
            "Value": clean_text(value),
            "Message": message,
        }
    )
    add_annotation(output.annotations, target_curie, "gdsn:conversionWarning", message)


def write_tsv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


class GdsnTransformer:
    def __init__(self, input_dir: Path) -> None:
        self.input_dir = input_dir
        self.classes = load_json(input_dir / "gdsn_classes.json")
        self.attributes = load_json(input_dir / "gdsn_classAttributes.json")
        self.code_values = load_json(input_dir / "gdsn_codeValues.json")
        self.instances = load_json(input_dir / "gdsn_instances.json")
        self.avps = load_json(input_dir / "gdsn_avps.json")
        self.extended_attributes = load_json(input_dir / "gdsn_extendedAttributes.json")
        self.extended_code_values = load_json(input_dir / "gdsn_extendedCodeValues.json")
        self.countries = load_json(input_dir / "iso3166Countries.json")
        self.version = load_json(input_dir / "version.json")
        self.by_id = {c["id"]: c for c in self.classes}
        self.by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for cls in self.classes:
            self.by_name[clean_name(cls.get("name"))].append(cls)
        self.extended_code_names = {
            clean_name(row.get("name"))
            for row in self.extended_code_values
            if clean_name(row.get("name"))
        }
        self.code_class_ids = {cv.get("classId") for cv in self.code_values if cv.get("classId") in self.by_id}
        self.type4_ids = {c["id"] for c in self.classes if c.get("type") == 4}
        self.type5_ids = {c["id"] for c in self.classes if c.get("type") == 5}
        self.enum_ids = self.code_class_ids | self.type4_ids | self.type5_ids
        self.synthetic_datatypes: dict[tuple[str, tuple[tuple[str, str], ...]], str] = {}
        self.output = OutputSet()

    def transform(self) -> OutputSet:
        self.output.annotation_properties.extend(self.annotation_properties())
        self.generate_enumerations()
        self.generate_classes()
        self.generate_datatypes()
        self.generate_attributes()
        self.generate_avp_and_extended_attributes()
        self.generate_version_annotations()
        self.generate_instance_annotations()
        self.dedupe()
        return self.output

    def annotation_properties(self) -> list[dict[str, str]]:
        definitions = {
            "gdsn:sourceId": ("Source ID", "Original UML or code-value numeric identifier."),
            "gdsn:bmsId": ("BMS ID", "BMS identifier from GDSN instance or AVP metadata."),
            "gdsn:pathId": ("Path ID", "Path identifier from gdsn_instances.json."),
            "gdsn:xPath": ("XPath", "XML XPath from gdsn_instances.json."),
            "gdsn:semanticResourceUrn": ("Semantic resource URN", "GDD semantic resource identifier."),
            "gdsn:sourceType": ("Source type", "Original UML type code or source category."),
            "gdsn:originalMultiplicity": ("Original multiplicity", "Unparsed source multiplicity."),
            "gdsn:originalLimit": ("Original limit", "Unparsed source limit."),
            "gdsn:conversionWarning": ("Conversion warning", "Diagnostic note emitted during TSV generation."),
            "gdsn:groupName": ("Group name", "Original GDSN group name."),
            "gdsn:example": ("Example", "Source example value."),
            "gdsn:validationRules": ("Validation rules", "Source validation rules text."),
            "gdsn:codeListName": ("Code list name", "Source code-list name."),
            "gdsn:externalLink": ("External link", "Source external reference link."),
            "gdsn:hierarchyLevel": ("Hierarchy level", "Source hierarchy-level marker."),
            "gdsn:targetMarket": ("Target market", "Source target-market marker."),
            "gpc:level": ("GPC level", "GPC hierarchy level."),
            "gpc:active": ("GPC active", "GPC active status."),
            "gpc:contextCode": ("GPC context code", "GPC context code associated with a brick."),
            "iso3166:numericCode": ("ISO 3166 numeric code", "ISO 3166 numeric country code."),
            "iso3166:countryName": ("ISO 3166 country name", "ISO 3166 country name."),
            "owl:versionInfo": ("Version info", "Ontology or source version information."),
            "dct:source": ("Source", "Source artefact path or name."),
        }
        return [
            {"Curie": curie, "Name": name, "Definition": definition}
            for curie, (name, definition) in definitions.items()
        ]

    def generate_classes(self) -> None:
        for cls in self.classes:
            cid = cls["id"]
            if cls.get("type") != 2 or cid in self.enum_ids:
                continue
            curie = gdsn_class_curie(cid)
            row = blank_row(CLASSES_HEADER)
            row.update(
                {
                    "Curie": curie,
                    "Name": clean_name(cls.get("name")),
                    "ParentNames": "|".join(self.parent_curies(cls)),
                    "Definition": clean_text(cls.get("definition")),
                }
            )
            self.output.classes.append(row)
            self.annotate_source(curie, "gdsn_classes.json", cid, cls.get("type"))

        self.output.classes.extend(
            [
                {
                    "Curie": "gdsn:GDSNAVP",
                    "Name": "GDSN AVP",
                    "ParentNames": "",
                    "Definition": "Synthetic container for GDSN Attribute Value Pair records.",
                    "IsAbstract": "",
                    "ChoiceOf": "",
                    "ChoiceSemantics": "",
                },
                {
                    "Curie": "gdsn:GDSNExtendedAttribute",
                    "Name": "GDSN Extended Attribute",
                    "ParentNames": "",
                    "Definition": "Synthetic container for GDSN extended attribute records.",
                    "IsAbstract": "",
                    "ChoiceOf": "",
                    "ChoiceSemantics": "",
                },
            ]
        )

    def generate_datatypes(self) -> None:
        for cls in self.classes:
            cid = cls["id"]
            if cls.get("type") != 3 or cid in self.enum_ids:
                continue
            curie = gdsn_class_curie(cid)
            row = blank_row(DATATYPES_HEADER)
            row.update(
                {
                    "Curie": curie,
                    "Name": clean_name(cls.get("name")),
                    "BaseDatatype": self.ultimate_xsd_base(cls),
                    "Definition": clean_text(cls.get("definition")),
                }
            )
            row.update(self.datatype_facets(cls))
            self.output.datatypes.append(row)
            self.annotate_source(curie, "gdsn_classes.json", cid, cls.get("type"))

    def generate_enumerations(self) -> None:
        for cid in sorted(self.enum_ids, key=lambda x: str(x)):
            cls = self.by_id.get(cid)
            if not cls:
                continue
            curie = gdsn_class_curie(cid)
            self.output.enumerations.append(
                {
                    "Curie": curie,
                    "Name": clean_name(cls.get("name")),
                    "Definition": clean_text(cls.get("definition")),
                }
            )
            self.annotate_source(curie, "gdsn_classes.json", cid, cls.get("type"))

        missing_names = sorted(
            {
                clean_text(cv.get("codeListName")).lstrip("\ufeff")
                for cv in self.code_values
                if cv.get("classId") not in self.by_id
            }
        )
        for name in missing_names:
            curie = f"gdsn:codeList_{local_token(name)}"
            self.output.enumerations.append({"Curie": curie, "Name": name, "Definition": ""})
            add_diag(self.output, "warning", "gdsn_codeValues.json", "", curie, "classId", "", "Code-list class missing from gdsn_classes.json")

        self.output.enumerations.append(
            {
                "Curie": "gdsn:ISO3166CountryCode",
                "Name": "ISO3166CountryCode",
                "Definition": "ISO 3166 country codes supplied with the GDSN artefacts.",
            }
        )

        for group_name, rows in sorted(self.group_by(self.extended_code_values, "name").items()):
            curie = f"gdsn:extCode_{local_token(group_name)}"
            definition = next((clean_text(r.get("definition")) for r in rows if clean_text(r.get("definition"))), "")
            self.output.enumerations.append({"Curie": curie, "Name": clean_name(group_name), "Definition": definition})

        self.generate_enum_values()

    def generate_enum_values(self) -> None:
        for cv in self.code_values:
            enum_curie = self.enum_curie_for_code_value(cv)
            name = clean_text(cv.get("codeValue")) or clean_name(cv.get("name"))
            curie = gdsn_code_value_curie(cv.get("id"))
            self.output.enum_values.append(
                {
                    "Enumeration": enum_curie,
                    "Curie": curie,
                    "Name": name,
                    "Definition": clean_text(cv.get("definition")),
                }
            )
            self.annotate_source(curie, "gdsn_codeValues.json", cv.get("id"), "codeValue")
            add_annotation(self.output.annotations, curie, "gdsn:codeListName", cv.get("codeListName"))
            add_annotation(self.output.annotations, curie, "gdsn:externalLink", cv.get("externalLink"))

        for country in self.countries:
            curie = f"iso3166:{local_token(country.get('alpha3'))}"
            self.output.enum_values.append(
                {
                    "Enumeration": "gdsn:ISO3166CountryCode",
                    "Curie": curie,
                    "Name": clean_text(country.get("alpha3")),
                    "Definition": clean_text(country.get("name")),
                }
            )
            add_annotation(self.output.annotations, curie, "iso3166:numericCode", country.get("code"))
            add_annotation(self.output.annotations, curie, "iso3166:countryName", country.get("name"))

        for group_name, rows in sorted(self.group_by(self.extended_code_values, "name").items()):
            enum_curie = f"gdsn:extCode_{local_token(group_name)}"
            for row_data in rows:
                curie = f"gdsn:extcv{row_data.get('id')}_{local_token(group_name)}"
                self.output.enum_values.append(
                    {
                        "Enumeration": enum_curie,
                        "Curie": curie,
                        "Name": clean_text(row_data.get("codeValue")) or clean_name(row_data.get("name")),
                        "Definition": clean_text(row_data.get("definition")),
                    }
                )
                self.annotate_source(curie, "gdsn_extendedCodeValues.json", row_data.get("id"), "extendedCodeValue")

    def generate_attributes(self) -> None:
        class_ids = {c["id"] for c in self.classes if c.get("type") == 2 and c["id"] not in self.enum_ids}
        for attr in self.attributes:
            parent_id = attr.get("parentClassId")
            curie = gdsn_attribute_curie(attr.get("id"))
            if parent_id not in class_ids:
                add_diag(
                    self.output,
                    "info",
                    "gdsn_classAttributes.json",
                    attr.get("id"),
                    curie,
                    "parentClassId",
                    parent_id,
                    "Attribute owner is not a generated class; preserving source metadata only",
                )
                self.annotate_source(curie, "gdsn_classAttributes.json", attr.get("id"), attr.get("type"))
                continue
            self.add_attribute_row(
                source_file="gdsn_classAttributes.json",
                source_id=attr.get("id"),
                owner_curie=gdsn_class_curie(parent_id),
                curie=curie,
                name=attr.get("name"),
                range_ref=self.range_for_class_id(attr.get("dataClassId")),
                definition=attr.get("definition"),
                multiplicity=attr.get("multiplicity"),
                limit=attr.get("limit"),
            )

        for cls in self.classes:
            cid = cls["id"]
            if cid not in class_ids:
                continue
            assoc_index = 0
            for ext in cls.get("extensions") or []:
                if ext.get("type") != 2:
                    continue
                assoc_index += 1
                dest_id = ext.get("destinationClassId")
                curie = f"gdsn:assoc_{cid}_{dest_id}_{assoc_index}"
                name = clean_name(ext.get("name")) or self.lower_first(self.by_id.get(dest_id, {}).get("name")) or f"association{assoc_index}"
                self.add_attribute_row(
                    source_file="gdsn_classes.json",
                    source_id=cid,
                    owner_curie=gdsn_class_curie(cid),
                    curie=curie,
                    name=name,
                    range_ref=self.range_for_class_id(dest_id),
                    definition=ext.get("definition"),
                    multiplicity=ext.get("multiplicity"),
                    limit=None,
                )

    def generate_avp_and_extended_attributes(self) -> None:
        for avp in self.avps:
            curie = f"gdsn:avp{avp.get('id')}"
            self.add_attribute_row(
                source_file="gdsn_avps.json",
                source_id=avp.get("id"),
                owner_curie="gdsn:GDSNAVP",
                curie=curie,
                name=avp.get("name"),
                range_ref=self.range_for_type_name(avp.get("dataTypeClassName")),
                definition=avp.get("definition"),
                multiplicity=avp.get("multiplicity"),
                limit=avp.get("limit"),
            )
            for prop in ["bmsId", "example", "validationRules", "hierarchyLevel", "targetMarket"]:
                add_annotation(self.output.annotations, curie, f"gdsn:{prop}", avp.get(prop), "xsd:integer" if prop in {"bmsId", "hierarchyLevel"} else "")

            code_values = avp.get("codeValues") or []
            if code_values:
                enum_curie = f"gdsn:avpCode_{local_token(avp.get('name'))}"
                self.output.enumerations.append({"Curie": enum_curie, "Name": f"{clean_name(avp.get('name'))}Code", "Definition": clean_text(avp.get("definition"))})
                for idx, code in enumerate(code_values, start=1):
                    self.output.enum_values.append({"Enumeration": enum_curie, "Curie": f"{enum_curie}_{idx}", "Name": clean_text(code), "Definition": ""})

        group_classes: set[str] = set()
        for ext_attr in self.extended_attributes:
            group_name = clean_name(ext_attr.get("groupName"))
            owner = "gdsn:GDSNExtendedAttribute"
            if group_name:
                group_curie = f"gdsn:extGroup_{local_token(group_name)}"
                owner = group_curie
                if group_curie not in group_classes:
                    group_classes.add(group_curie)
                    self.output.classes.append(
                        {
                            "Curie": group_curie,
                            "Name": group_name,
                            "ParentNames": "gdsn:GDSNExtendedAttribute",
                            "Definition": "Synthetic group container for GDSN extended attributes.",
                            "IsAbstract": "",
                            "ChoiceOf": "",
                            "ChoiceSemantics": "",
                        }
                    )
            curie = f"gdsn:extAttr{ext_attr.get('id')}"
            self.add_attribute_row(
                source_file="gdsn_extendedAttributes.json",
                source_id=ext_attr.get("id"),
                owner_curie=owner,
                curie=curie,
                name=ext_attr.get("name"),
                range_ref=self.range_for_type_name(ext_attr.get("dataTypeClassName")),
                definition=ext_attr.get("definition"),
                multiplicity=ext_attr.get("multiplicity"),
                limit=ext_attr.get("limit"),
                convert_limit_facets=False,
            )
            add_annotation(self.output.annotations, curie, "gdsn:groupName", group_name)
            for prop in ["example", "validationRules", "hierarchyLevel"]:
                add_annotation(self.output.annotations, curie, f"gdsn:{prop}", ext_attr.get(prop), "xsd:integer" if prop == "hierarchyLevel" else "")

    def add_attribute_row(
        self,
        source_file: str,
        source_id: Any,
        owner_curie: str,
        curie: str,
        name: Any,
        range_ref: str,
        definition: Any,
        multiplicity: Any,
        limit: Any,
        convert_limit_facets: bool = True,
    ) -> None:
        min_mult, max_mult, mult_warning = parse_multiplicity(multiplicity)
        if convert_limit_facets:
            facets, limit_warning = parse_limit(limit, self.is_string_like(range_ref))
        else:
            facets, limit_warning = {}, None
        if facets:
            datatype_ref = self.synthetic_datatype_for_facets(range_ref, facets)
            if datatype_ref:
                range_ref = datatype_ref
                facets = {}
        row = blank_row(ATTRIBUTES_HEADER)
        row.update(
            {
                "Class": owner_curie,
                "Curie": curie,
                "Name": clean_name(name),
                "ClassEnumOrPrimitiveType": range_ref,
                "MinMultiplicity": min_mult,
                "MaxMultiplicity": max_mult,
                "Definition": clean_text(definition),
            }
        )
        row.update(facets)
        self.output.attributes.append(row)
        self.annotate_source(curie, source_file, source_id, "attribute")
        add_annotation(self.output.annotations, curie, "gdsn:originalMultiplicity", multiplicity)
        add_annotation(self.output.annotations, curie, "gdsn:originalLimit", limit)
        if mult_warning:
            add_diag(self.output, "warning", source_file, source_id, curie, "multiplicity", multiplicity, mult_warning)
        if limit_warning:
            add_diag(self.output, "warning", source_file, source_id, curie, "limit", limit, limit_warning)

    def parent_curies(self, cls: dict[str, Any]) -> list[str]:
        parents = []
        for ext in cls.get("extensions") or []:
            if ext.get("type") == 1 and clean_name(ext.get("name")) == "Generalization":
                parent_id = ext.get("destinationClassId")
                if parent_id in self.enum_ids:
                    parents.append(gdsn_class_curie(parent_id))
                elif parent_id in self.by_id and self.by_id[parent_id].get("type") == 2:
                    parents.append(gdsn_class_curie(parent_id))
        return parents

    def ultimate_xsd_base(self, cls: dict[str, Any], seen: set[Any] | None = None) -> str:
        seen = seen or set()
        cid = cls.get("id")
        if cid in seen:
            return "xsd:string"
        seen.add(cid)
        name = clean_name(cls.get("name"))
        if cls.get("type") == 1 and name in XSD_TYPES:
            return f"xsd:{name}"
        for ext in cls.get("extensions") or []:
            if ext.get("type") == 1:
                parent = self.by_id.get(ext.get("destinationClassId"))
                if parent:
                    return self.ultimate_xsd_base(parent, seen)
        return "xsd:string"

    def datatype_facets(self, cls: dict[str, Any]) -> dict[str, str]:
        name = clean_name(cls.get("name"))
        match = re.search(r"(?:String|Description)(\d+)$", name)
        if match:
            return {"MaxLength": match.group(1)}
        return {}

    def synthetic_datatype_for_facets(self, range_ref: str, facets: dict[str, str]) -> str:
        if not range_ref.startswith("xsd:"):
            return ""
        key = (range_ref, tuple(sorted(facets.items())))
        existing = self.synthetic_datatypes.get(key)
        if existing:
            return existing

        base_name = range_ref.removeprefix("xsd:")
        parts = [base_name]
        if facets.get("Pattern"):
            pattern_token = hashlib.sha1(facets["Pattern"].encode("utf-8")).hexdigest()[:12]
            parts.append(f"Pattern{pattern_token}")
        for field in [
            "MinLength",
            "MaxLength",
            "MinInclusive",
            "MaxInclusive",
            "MinExclusive",
            "MaxExclusive",
            "TotalDigits",
            "FractionDigits",
        ]:
            if facets.get(field):
                parts.append(f"{field}{facets[field]}")
        name = "".join(part[:1].upper() + part[1:] for part in parts)
        curie = f"gdsn:dt_{local_token('_'.join(parts))}"
        row = blank_row(DATATYPES_HEADER)
        row.update(
            {
                "Curie": curie,
                "Name": name,
                "BaseDatatype": range_ref,
                "Definition": f"Synthetic datatype for {range_ref} attribute limits.",
            }
        )
        row.update(facets)
        self.output.datatypes.append(row)
        self.synthetic_datatypes[key] = curie
        return curie

    def range_for_class_id(self, class_id: Any) -> str:
        cls = self.by_id.get(class_id)
        if not cls:
            return "xsd:string"
        if class_id in self.enum_ids:
            return gdsn_class_curie(class_id)
        name = clean_name(cls.get("name"))
        if cls.get("type") == 1 and name in XSD_TYPES:
            return f"xsd:{name}"
        if cls.get("type") == 1:
            return "xsd:string"
        if cls.get("type") == 3:
            return gdsn_class_curie(class_id)
        return gdsn_class_curie(class_id)

    def range_for_type_name(self, type_name: Any) -> str:
        name = clean_name(type_name)
        if name in XSD_TYPES:
            return f"xsd:{name}"
        if name in self.extended_code_names:
            return f"gdsn:extCode_{local_token(name)}"
        matches = self.by_name.get(name) or []
        if matches:
            preferred = sorted(matches, key=lambda c: (c.get("type") not in {3, 4, 5}, str(c.get("id"))))[0]
            return self.range_for_class_id(preferred.get("id"))
        return "xsd:string"

    def enum_curie_for_code_value(self, cv: dict[str, Any]) -> str:
        class_id = cv.get("classId")
        if class_id in self.by_id:
            return gdsn_class_curie(class_id)
        name = clean_text(cv.get("codeListName")).lstrip("\ufeff")
        return f"gdsn:codeList_{local_token(name)}"

    def is_string_like(self, range_ref: str) -> bool:
        if range_ref == "xsd:string":
            return True
        if not range_ref.startswith("gdsn:c"):
            return False
        try:
            cid = int(range_ref.removeprefix("gdsn:c"))
        except ValueError:
            return False
        if cid in self.enum_ids:
            return False
        cls = self.by_id.get(cid)
        return bool(cls and self.ultimate_xsd_base(cls) == "xsd:string")

    def annotate_source(self, curie: str, source_file: str, source_id: Any, source_type: Any) -> None:
        add_annotation(self.output.annotations, curie, "gdsn:sourceId", source_id)
        add_annotation(self.output.annotations, curie, "gdsn:sourceType", source_type)
        add_annotation(self.output.annotations, curie, "dct:source", source_file)

    def generate_version_annotations(self) -> None:
        for key in ["number", "displayName", "containerName", "comment"]:
            add_annotation(self.output.annotations, "gdsn:Ontology", "owl:versionInfo" if key == "number" else "dct:source", self.version.get(key))

    def generate_instance_annotations(self) -> None:
        for inst in self.instances:
            target = ""
            if inst.get("classId") in self.by_id:
                target = gdsn_class_curie(inst.get("classId"))
            elif inst.get("attributeId") is not None:
                target = gdsn_attribute_curie(inst.get("attributeId"))
            if not target:
                continue
            add_annotation(self.output.annotations, target, "gdsn:bmsId", inst.get("bmsId"), "xsd:integer")
            add_annotation(self.output.annotations, target, "gdsn:pathId", inst.get("pathId"))
            add_annotation(self.output.annotations, target, "gdsn:xPath", inst.get("xPath"))
            add_annotation(self.output.annotations, target, "gdsn:semanticResourceUrn", inst.get("semanticResourceUrn"))

    def dedupe(self) -> None:
        self.output.classes = self.unique_rows(self.output.classes, ["Curie"])
        self.output.datatypes = self.unique_rows(self.output.datatypes, ["Curie"])
        self.output.enumerations = self.unique_rows(self.output.enumerations, ["Curie"])
        self.output.enum_values = self.unique_rows(self.output.enum_values, ["Curie"])
        self.output.annotation_properties = self.unique_rows(self.output.annotation_properties, ["Curie"])
        self.output.annotations = self.unique_rows(self.output.annotations, ANNOTATIONS_HEADER)

    @staticmethod
    def unique_rows(rows: list[dict[str, str]], keys: list[str]) -> list[dict[str, str]]:
        seen = set()
        result = []
        for row in rows:
            key = tuple(row.get(k, "") for k in keys)
            if key in seen:
                continue
            seen.add(key)
            result.append(row)
        return result

    @staticmethod
    def lower_first(value: Any) -> str:
        text = clean_name(value)
        return text[:1].lower() + text[1:] if text else ""

    @staticmethod
    def group_by(rows: Iterable[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[clean_name(row.get(key))].append(row)
        return grouped


class GpcTransformer:
    def __init__(self, input_dir: Path) -> None:
        self.input_dir = input_dir
        self.gpc = load_json(input_dir / "GPCv20260520GB.json")
        self.bricks = load_json(input_dir / "gdsn_gpcBricks.json")
        self.output = OutputSet()

    def transform(self) -> OutputSet:
        self.output.annotation_properties.extend(
            [
                {"Curie": "gpc:level", "Name": "GPC level", "Definition": "GPC hierarchy level."},
                {"Curie": "gpc:active", "Name": "GPC active", "Definition": "GPC active status."},
                {"Curie": "gpc:definitionExcludes", "Name": "GPC definition excludes", "Definition": "Text describing excluded concepts."},
                {"Curie": "gpc:contextCode", "Name": "GPC context code", "Definition": "GDSN context code associated with a GPC brick."},
                {"Curie": "dct:source", "Name": "Source", "Definition": "Source artefact path or name."},
            ]
        )
        self.walk(self.gpc.get("Schema") or [], None)
        for brick in self.bricks:
            target = f"gpc:{brick.get('brickCode')}"
            add_annotation(self.output.annotations, target, "gpc:contextCode", brick.get("contextCode"))
        self.output.classes = GdsnTransformer.unique_rows(self.output.classes, ["Curie"])
        self.output.annotations = GdsnTransformer.unique_rows(self.output.annotations, ANNOTATIONS_HEADER)
        return self.output

    def walk(self, nodes: list[dict[str, Any]], parent_curie: str | None) -> None:
        for node in nodes:
            curie = f"gpc:{node.get('Code')}"
            row = blank_row(CLASSES_HEADER)
            row.update(
                {
                    "Curie": curie,
                    "Name": clean_name(node.get("Title")),
                    "ParentNames": parent_curie or "",
                    "Definition": clean_text(node.get("Definition")),
                }
            )
            self.output.classes.append(row)
            add_annotation(self.output.annotations, curie, "gpc:level", node.get("Level"), "xsd:integer")
            add_annotation(self.output.annotations, curie, "gpc:active", str(node.get("Active")).lower())
            add_annotation(self.output.annotations, curie, "gpc:definitionExcludes", node.get("DefinitionExcludes"))
            add_annotation(self.output.annotations, curie, "dct:source", "GPCv20260520GB.json")
            self.walk(node.get("Childs") or [], curie)


def write_output_set(output_dir: Path, output: OutputSet) -> None:
    write_tsv(output_dir / "Classes.tsv", CLASSES_HEADER, output.classes)
    write_tsv(output_dir / "Attributes.tsv", ATTRIBUTES_HEADER, output.attributes)
    write_tsv(output_dir / "Datatypes.tsv", DATATYPES_HEADER, output.datatypes)
    write_tsv(output_dir / "Enumerations.tsv", ENUMERATIONS_HEADER, output.enumerations)
    write_tsv(output_dir / "EnumerationNamedValues.tsv", ENUM_VALUES_HEADER, output.enum_values)
    write_tsv(output_dir / "AnnotationProperties.tsv", ANNOTATION_PROPERTIES_HEADER, output.annotation_properties)
    write_tsv(output_dir / "Annotations.tsv", ANNOTATIONS_HEADER, output.annotations)
    write_tsv(output_dir / "diagnostics.tsv", DIAGNOSTICS_HEADER, output.diagnostics)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transform GDSN UML JSON dumps into uml2semantics TSV artefacts.")
    parser.add_argument("--input-dir", type=Path, default=Path("artefacts/GDSN_Current_v3.1.35"), help="Directory containing the GDSN JSON dump.")
    parser.add_argument("--output-dir", type=Path, default=Path("build/gdsn-tsv"), help="Directory to write generated TSV artefacts.")
    parser.add_argument("--skip-gpc", action="store_true", help="Do not generate the separate GPC TSV ontology module.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    gdsn_output = GdsnTransformer(args.input_dir).transform()
    write_output_set(args.output_dir / "gdsn", gdsn_output)
    print(f"Wrote GDSN TSV artefacts to {args.output_dir / 'gdsn'}")
    if not args.skip_gpc:
        gpc_output = GpcTransformer(args.input_dir).transform()
        write_output_set(args.output_dir / "gpc", gpc_output)
        print(f"Wrote GPC TSV artefacts to {args.output_dir / 'gpc'}")
    return 0
