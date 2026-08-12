from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

from lxml import etree
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD


GDSN = Namespace("urn:gs1:std:gdsn:")
GPC = Namespace("urn:gs1:std:gpc:")
ISO3166 = Namespace("urn:iso:std:iso:3166")


SUPPORTED_EXTENSION_MODULES = {
    "deliveryPurchasingInformationModule",
    "tradeItemDataCarrierAndIdentificationModule",
    "tradeItemDescriptionModule",
    "tradeItemMeasurementsModule",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gdsn-xml-to-rdf",
        description="Generate a separate RDF instance graph from a GDSN Catalogue Item Notification XML file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  Generate KATO sample instances:
    gdsn-xml-to-rdf \\
      --input artefacts/KATO/add.xml \\
      --gdsn build/gdsn.ttl \\
      --gpc build/gpc.ttl \\
      --output build/KATO/kato-instances.ttl \\
      --extension-report build/KATO/kato-extensions.json \\
      --report-json build/KATO/kato-instances.report.json

  Write Turtle to stdout and report extension-module contents:
    gdsn-xml-to-rdf \\
      --input artefacts/KATO/add.xml \\
      --gdsn build/gdsn.ttl \\
      --gpc build/gpc.ttl \\
      --extension-report build/KATO/kato-extensions.json \\
      --print-extensions
""",
    )
    parser.add_argument("--input", required=True, type=Path, help="GDSN XML input file.")
    parser.add_argument("--gdsn", default=Path("build/gdsn.ttl"), type=Path, help="Generated GDSN ontology.")
    parser.add_argument("--gpc", default=Path("build/gpc.ttl"), type=Path, help="Generated GPC ontology.")
    parser.add_argument("--output", type=Path, help="Output RDF instance file. If omitted, Turtle is written to stdout.")
    parser.add_argument("--format", choices=["turtle", "xml", "nt", "json-ld"], default="turtle", help="RDF output format.")
    parser.add_argument("--base-iri", default="urn:gs1:sample:kato:", help="Base IRI for generated instance resources.")
    parser.add_argument("--prefix", default="kato", help="Prefix to bind for --base-iri.")
    parser.add_argument("--gdsn-import-iri", default=str(GDSN), help="Ontology IRI imported by the generated instance ontology for GDSN.")
    parser.add_argument("--gpc-import-iri", default=str(GPC), help="Ontology IRI imported by the generated instance ontology for GPC.")
    parser.add_argument("--extension-report", type=Path, help="Write all extension module contents found in the XML to JSON.")
    parser.add_argument("--print-extensions", action="store_true", help="Print a concise summary of extension modules found in the XML.")
    parser.add_argument("--report-json", type=Path, help="Write conversion summary and diagnostics to JSON.")
    parser.add_argument("--no-validate", action="store_true", help="Skip RDF parse validation of generated output.")
    parser.add_argument(
        "--include-message-envelope",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include CatalogueItemNotification and CatalogueItem envelope instances.",
    )
    return parser.parse_args(argv)


def load_graph(path: Path) -> Graph:
    text = path.read_text(encoding="utf-8", errors="replace").lstrip()
    rdf_format = "xml" if text.startswith("<?xml") or text.startswith("<rdf:RDF") else "turtle"
    return Graph().parse(path, format=rdf_format)


def local_name(element: etree._Element) -> str:
    return etree.QName(element).localname


def children(element: etree._Element, name: str) -> list[etree._Element]:
    return [child for child in element if local_name(child) == name]


def child(element: etree._Element, name: str) -> etree._Element | None:
    matches = children(element, name)
    return matches[0] if matches else None


def text(element: etree._Element | None, name: str | None = None) -> str:
    target = child(element, name) if element is not None and name is not None else element
    return (target.text or "").strip() if target is not None and target.text else ""


def descendants(element: etree._Element, name: str) -> list[etree._Element]:
    return [item for item in element.iter() if local_name(item) == name]


def resource(base: str, *parts: str) -> URIRef:
    return URIRef(base + "/".join(quote(str(part), safe="") for part in parts))


def bind(graph: Graph, instance_prefix: str, base_iri: str) -> None:
    graph.bind(instance_prefix, Namespace(base_iri))
    graph.bind("gdsn", GDSN)
    graph.bind("gpc", GPC)
    graph.bind("iso3166", ISO3166)
    graph.bind("owl", OWL)
    graph.bind("dct", DCTERMS)


def literal_for(value: str, datatype: URIRef | None) -> Literal:
    if datatype == XSD.boolean:
        return Literal(value.strip().lower() == "true", datatype=XSD.boolean)
    if datatype in {XSD.integer, XSD.nonNegativeInteger}:
        return Literal(int(value), datatype=datatype)
    if datatype == XSD.decimal:
        return Literal(value, datatype=XSD.decimal)
    if datatype == XSD.float:
        return Literal(value, datatype=XSD.float)
    if datatype == XSD.dateTime:
        return Literal(value, datatype=XSD.dateTime)
    return Literal(value, datatype=datatype) if datatype is not None else Literal(value)


class OntologyIndex:
    def __init__(self, gdsn: Graph, gpc: Graph) -> None:
        self.gdsn = gdsn
        self.gpc = gpc
        self.properties_by_label: dict[tuple[URIRef, str], URIRef] = {}
        self.range_by_property: dict[URIRef, URIRef] = {}
        self.type_by_property: dict[URIRef, URIRef] = {}
        self.code_values: dict[tuple[URIRef, str], URIRef] = {}
        self.iso_by_numeric: dict[str, URIRef] = {}
        self.value_datatype_by_class: dict[URIRef, URIRef] = {}
        self.literal_datatype_by_datatype: dict[URIRef, URIRef] = {}
        self._index()

    def _index(self) -> None:
        for prop, label in self.gdsn.subject_objects(RDFS.label):
            domain = next(self.gdsn.objects(prop, RDFS.domain), None)
            range_ref = next(self.gdsn.objects(prop, RDFS.range), None)
            prop_type = next(self.gdsn.objects(prop, RDF.type), None)
            if isinstance(domain, URIRef):
                self.properties_by_label[(domain, str(label))] = prop
            if isinstance(range_ref, URIRef):
                self.range_by_property[prop] = range_ref
            if isinstance(prop_type, URIRef):
                self.type_by_property[prop] = prop_type

        for value, value_type in self.gdsn.subject_objects(RDF.type):
            value_label = next(self.gdsn.objects(value, RDFS.label), None)
            if isinstance(value, URIRef) and isinstance(value_type, URIRef) and value_label is not None:
                self.code_values[(value_type, str(value_label))] = value

        for country, numeric in self.gdsn.subject_objects(ISO3166.numericCode):
            if isinstance(country, URIRef):
                self.iso_by_numeric[str(numeric)] = country

        for cls, datatype in self.gdsn.subject_objects(GDSN.valueDatatype):
            if isinstance(cls, URIRef):
                self.value_datatype_by_class[cls] = self.curie_or_uri(str(datatype))

        for datatype in self.gdsn.subjects(RDF.type, RDFS.Datatype):
            if not isinstance(datatype, URIRef):
                continue
            equivalent = next(self.gdsn.objects(datatype, OWL.equivalentClass), None)
            if isinstance(equivalent, URIRef) and str(equivalent).startswith(str(XSD)):
                self.literal_datatype_by_datatype[datatype] = equivalent
            elif equivalent is not None:
                base = next(self.gdsn.objects(equivalent, OWL.onDatatype), None)
                if isinstance(base, URIRef):
                    self.literal_datatype_by_datatype[datatype] = base

    @staticmethod
    def curie_or_uri(value: str) -> URIRef:
        if value.startswith("xsd:"):
            return URIRef(str(XSD) + value.removeprefix("xsd:"))
        if value.startswith("gdsn:"):
            return GDSN[value.removeprefix("gdsn:")]
        if value.startswith("http:") or value.startswith("https:") or value.startswith("urn:"):
            return URIRef(value)
        return URIRef(value)

    def literal_datatype(self, datatype: URIRef | None) -> URIRef | None:
        if datatype is None:
            return None
        return self.literal_datatype_by_datatype.get(datatype, datatype)

    def prop(self, domain: URIRef, label: str) -> URIRef:
        value = self.properties_by_label.get((domain, label))
        if value is None:
            raise KeyError(f"No GDSN property labelled {label!r} on {domain}")
        return value

    def object_value(self, prop: URIRef, lexical: str) -> URIRef | None:
        range_ref = self.range_by_property.get(prop)
        if range_ref == GDSN.c1436:
            return self.iso_by_numeric.get(lexical)
        if range_ref is None:
            return None
        return self.code_values.get((range_ref, lexical))

    def add_value(self, graph: Graph, subject: URIRef, prop: URIRef, lexical: str, diagnostics: list[str]) -> None:
        if lexical == "":
            return
        prop_type = self.type_by_property.get(prop)
        range_ref = self.range_by_property.get(prop)
        if prop_type == OWL.ObjectProperty:
            obj = self.object_value(prop, lexical)
            if obj is None:
                diagnostics.append(f"Unresolved code value {lexical!r} for {prop}")
                graph.add((subject, prop, Literal(lexical)))
            else:
                graph.add((subject, prop, obj))
            return
        graph.add((subject, prop, literal_for(lexical, self.literal_datatype(range_ref))))

    def add_qualified_value(
        self,
        graph: Graph,
        subject: URIRef,
        domain: URIRef,
        label: str,
        xml: etree._Element,
        diagnostics: list[str],
        value_node: URIRef | None = None,
    ) -> None:
        lexical = text(xml)
        if lexical == "":
            return
        prop = self.prop(domain, label)
        prop_type = self.type_by_property.get(prop)
        range_ref = self.range_by_property.get(prop)
        if prop_type != OWL.ObjectProperty or range_ref not in self.value_datatype_by_class:
            self.add_value(graph, subject, prop, lexical, diagnostics)
            return

        value_node = value_node or URIRef(f"{subject}/{quote(label, safe='')}")
        graph.add((subject, prop, value_node))
        graph.add((value_node, RDF.type, range_ref))
        value_datatype = self.value_datatype_by_class[range_ref]
        lang = xml.attrib.get("languageCode")
        if lang and value_datatype == XSD.string:
            graph.add((value_node, RDF.value, Literal(lexical, lang=lang.lower())))
        else:
            graph.add((value_node, RDF.value, literal_for(lexical, self.literal_datatype(value_datatype))))

        for raw_name, raw_value in xml.attrib.items():
            qualifier_name = etree.QName(raw_name).localname
            try:
                qualifier_prop = self.prop(range_ref, qualifier_name)
            except KeyError:
                diagnostics.append(f"Unresolved structured value qualifier {qualifier_name!r} for {range_ref}")
                continue
            self.add_value(graph, value_node, qualifier_prop, raw_value, diagnostics)


def add_text_value(index: OntologyIndex, graph: Graph, subject: URIRef, domain: URIRef, label: str, value: str, diagnostics: list[str]) -> None:
    index.add_value(graph, subject, index.prop(domain, label), value, diagnostics)


def add_party(index: OntologyIndex, graph: Graph, base: str, parent: URIRef, parent_domain: URIRef, xml: etree._Element, role: str, gtin: str, diagnostics: list[str]) -> URIRef:
    party = resource(base, "party", gtin, role)
    graph.add((party, RDF.type, GDSN.c845))
    graph.add((parent, index.prop(parent_domain, role), party))
    add_text_value(index, graph, party, GDSN.c845, "gln", text(xml, "gln"), diagnostics)
    add_text_value(index, graph, party, GDSN.c845, "partyName", text(xml, "partyName"), diagnostics)
    return party


def add_classification(index: OntologyIndex, graph: Graph, base: str, trade_item: URIRef, xml: etree._Element, gtin: str, diagnostics: list[str]) -> str:
    classification = resource(base, "classification", gtin)
    graph.add((classification, RDF.type, GDSN["c-1698192853"]))
    graph.add((trade_item, index.prop(GDSN.c863999331, "gDSNTradeItemClassification"), classification))
    brick_code = text(xml, "gpcCategoryCode")
    definition = text(xml, "gpcCategoryDefinition")
    add_text_value(index, graph, classification, GDSN["c-1698192853"], "gpcCategoryCode", brick_code, diagnostics)
    add_text_value(index, graph, classification, GDSN["c-1698192853"], "gpcCategoryDefinition", definition, diagnostics)
    if brick_code and (GPC[brick_code], None, None) in index.gpc:
        graph.add((trade_item, RDF.type, GPC[brick_code]))
    elif brick_code:
        diagnostics.append(f"GPC Brick {brick_code} was not found in gpc.ttl")
    return brick_code


def add_target_market(index: OntologyIndex, graph: Graph, base: str, trade_item: URIRef, xml: etree._Element, gtin: str, diagnostics: list[str]) -> None:
    market = resource(base, "targetMarket", gtin)
    graph.add((market, RDF.type, GDSN.c919))
    graph.add((trade_item, index.prop(GDSN.c863999331, "targetMarket"), market))
    add_text_value(index, graph, market, GDSN.c919, "targetMarketCountryCode", text(xml, "targetMarketCountryCode"), diagnostics)


def add_sync_dates(index: OntologyIndex, graph: Graph, base: str, trade_item: URIRef, xml: etree._Element, gtin: str, diagnostics: list[str]) -> None:
    dates = resource(base, "syncDates", gtin)
    graph.add((dates, RDF.type, GDSN.c1327077224))
    graph.add((trade_item, index.prop(GDSN.c863999331, "tradeItemSynchronisationDates"), dates))
    add_text_value(index, graph, dates, GDSN.c1327077224, "lastChangeDateTime", text(xml, "lastChangeDateTime"), diagnostics)
    add_text_value(index, graph, dates, GDSN.c1327077224, "effectiveDateTime", text(xml, "effectiveDateTime"), diagnostics)


def add_next_lower_level(index: OntologyIndex, graph: Graph, base: str, trade_item: URIRef, xml: etree._Element, gtin: str, diagnostics: list[str]) -> None:
    info = resource(base, "nextLowerLevel", gtin)
    graph.add((info, RDF.type, GDSN.c652864357))
    graph.add((trade_item, index.prop(GDSN.c863999331, "nextLowerLevelTradeItemInformation"), info))
    add_text_value(index, graph, info, GDSN.c652864357, "quantityOfChildren", text(xml, "quantityOfChildren"), diagnostics)
    add_text_value(index, graph, info, GDSN.c652864357, "totalQuantityOfNextLowerLevelTradeItem", text(xml, "totalQuantityOfNextLowerLevelTradeItem"), diagnostics)
    for child_trade_item in children(xml, "childTradeItem"):
        child_gtin = text(child_trade_item, "gtin")
        child = resource(base, "childTradeItem", gtin, child_gtin or "unknown")
        graph.add((child, RDF.type, GDSN.c282496455))
        graph.add((info, index.prop(GDSN.c652864357, "childTradeItem"), child))
        add_text_value(index, graph, child, GDSN.c788, "gtin", child_gtin, diagnostics)
        add_text_value(index, graph, child, GDSN.c282496455, "quantityOfNextLowerLevelTradeItem", text(child_trade_item, "quantityOfNextLowerLevelTradeItem"), diagnostics)


def add_leaf_value(
    index: OntologyIndex,
    graph: Graph,
    subject: URIRef,
    domain: URIRef,
    label: str,
    xml: etree._Element | None,
    diagnostics: list[str],
    value_node: URIRef | None = None,
) -> None:
    if xml is None:
        return
    index.add_qualified_value(graph, subject, domain, label, xml, diagnostics, value_node)


def add_extension_module_link(graph: Graph, trade_item_information: URIRef, module: URIRef) -> None:
    graph.add((trade_item_information, GDSN.extensionModule, module))


def add_delivery_purchasing_information(index: OntologyIndex, graph: Graph, base: str, trade_item_information: URIRef, module_xml: etree._Element, gtin: str, diagnostics: list[str]) -> None:
    module = resource(base, "extension", gtin, "deliveryPurchasingInformationModule")
    info = resource(base, "extension", gtin, "deliveryPurchasingInformation")
    graph.add((module, RDF.type, GDSN.GDSNExtensionModule))
    graph.add((module, RDF.type, GDSN.c1952808552))
    add_extension_module_link(graph, trade_item_information, module)
    graph.add((info, RDF.type, GDSN.c1362))
    graph.add((module, index.prop(GDSN.c1952808552, "deliveryPurchasingInformation"), info))
    info_xml = child(module_xml, "deliveryPurchasingInformation")
    add_leaf_value(index, graph, info, GDSN.c1362, "startAvailabilityDateTime", child(info_xml, "startAvailabilityDateTime") if info_xml is not None else None, diagnostics)


def add_trade_item_data_carrier_module(index: OntologyIndex, graph: Graph, base: str, trade_item_information: URIRef, module_xml: etree._Element, gtin: str, diagnostics: list[str]) -> None:
    module = resource(base, "extension", gtin, "tradeItemDataCarrierAndIdentificationModule")
    graph.add((module, RDF.type, GDSN.GDSNExtensionModule))
    graph.add((module, RDF.type, GDSN["c-1966439330"]))
    add_extension_module_link(graph, trade_item_information, module)
    for position, data_carrier_xml in enumerate(children(module_xml, "dataCarrier"), start=1):
        data_carrier = resource(base, "extension", gtin, "dataCarrier", str(position))
        graph.add((data_carrier, RDF.type, GDSN["c-1841074127"]))
        graph.add((module, index.prop(GDSN["c-1966439330"], "dataCarrier"), data_carrier))
        add_leaf_value(index, graph, data_carrier, GDSN["c-1841074127"], "dataCarrierTypeCode", child(data_carrier_xml, "dataCarrierTypeCode"), diagnostics)


def add_trade_item_description_module(index: OntologyIndex, graph: Graph, base: str, trade_item_information: URIRef, module_xml: etree._Element, gtin: str, diagnostics: list[str]) -> None:
    module = resource(base, "extension", gtin, "tradeItemDescriptionModule")
    description = resource(base, "extension", gtin, "tradeItemDescriptionInformation")
    graph.add((module, RDF.type, GDSN.GDSNExtensionModule))
    graph.add((module, RDF.type, GDSN.c1343046870))
    add_extension_module_link(graph, trade_item_information, module)
    graph.add((description, RDF.type, GDSN.c1204161147))
    graph.add((module, index.prop(GDSN.c1343046870, "tradeItemDescriptionInformation"), description))
    description_xml = child(module_xml, "tradeItemDescriptionInformation")
    if description_xml is None:
        return
    add_leaf_value(
        index,
        graph,
        description,
        GDSN.c1204161147,
        "functionalName",
        child(description_xml, "functionalName"),
        diagnostics,
        resource(base, "value", gtin, "functionalName"),
    )
    brand_xml = child(description_xml, "brandNameInformation")
    if brand_xml is not None:
        brand = resource(base, "extension", gtin, "brandNameInformation")
        graph.add((brand, RDF.type, GDSN.c1350303678))
        graph.add((description, index.prop(GDSN.c1204161147, "brandNameInformation"), brand))
        add_leaf_value(index, graph, brand, GDSN.c1350303678, "brandName", child(brand_xml, "brandName"), diagnostics)


def add_trade_item_measurements_module(index: OntologyIndex, graph: Graph, base: str, trade_item_information: URIRef, module_xml: etree._Element, gtin: str, diagnostics: list[str]) -> None:
    module = resource(base, "extension", gtin, "tradeItemMeasurementsModule")
    measurements = resource(base, "extension", gtin, "tradeItemMeasurements")
    graph.add((module, RDF.type, GDSN.GDSNExtensionModule))
    graph.add((module, RDF.type, GDSN["c-1559145472"]))
    add_extension_module_link(graph, trade_item_information, module)
    graph.add((measurements, RDF.type, GDSN["c-1443794077"]))
    graph.add((module, index.prop(GDSN["c-1559145472"], "tradeItemMeasurements"), measurements))
    measurements_xml = child(module_xml, "tradeItemMeasurements")
    if measurements_xml is None:
        return
    for name in ["depth", "height", "netContent", "width"]:
        add_leaf_value(
            index,
            graph,
            measurements,
            GDSN["c-1443794077"],
            name,
            child(measurements_xml, name),
            diagnostics,
            resource(base, "value", gtin, name),
        )
    weight_xml = child(measurements_xml, "tradeItemWeight")
    if weight_xml is not None:
        weight = resource(base, "extension", gtin, "tradeItemWeight")
        graph.add((weight, RDF.type, GDSN["c-113081611"]))
        graph.add((measurements, index.prop(GDSN["c-1443794077"], "tradeItemWeight"), weight))
        add_leaf_value(
            index,
            graph,
            weight,
            GDSN["c-113081611"],
            "grossWeight",
            child(weight_xml, "grossWeight"),
            diagnostics,
            resource(base, "value", gtin, "grossWeight"),
        )


def add_supported_extension_modules(index: OntologyIndex, graph: Graph, base: str, trade_item: URIRef, xml: etree._Element, gtin: str, diagnostics: list[str]) -> None:
    extension = child(child(xml, "tradeItemInformation"), "extension")
    if extension is None:
        return
    supported = [module for module in extension if local_name(module) in SUPPORTED_EXTENSION_MODULES]
    if not supported:
        return
    trade_item_information = resource(base, "tradeItemInformation", gtin)
    graph.add((trade_item_information, RDF.type, GDSN.c1352305416))
    graph.add((trade_item, index.prop(GDSN.c863999331, "tradeItemInformation"), trade_item_information))
    for module in supported:
        module_name = local_name(module)
        if module_name == "deliveryPurchasingInformationModule":
            add_delivery_purchasing_information(index, graph, base, trade_item_information, module, gtin, diagnostics)
        elif module_name == "tradeItemDataCarrierAndIdentificationModule":
            add_trade_item_data_carrier_module(index, graph, base, trade_item_information, module, gtin, diagnostics)
        elif module_name == "tradeItemDescriptionModule":
            add_trade_item_description_module(index, graph, base, trade_item_information, module, gtin, diagnostics)
        elif module_name == "tradeItemMeasurementsModule":
            add_trade_item_measurements_module(index, graph, base, trade_item_information, module, gtin, diagnostics)


def add_trade_item(index: OntologyIndex, graph: Graph, base: str, xml: etree._Element, diagnostics: list[str]) -> tuple[URIRef, str, str]:
    gtin = text(xml, "gtin")
    trade_item = resource(base, "gtin", gtin or "unknown")
    graph.add((trade_item, RDF.type, GDSN.c863999331))
    add_text_value(index, graph, trade_item, GDSN.c788, "gtin", gtin, diagnostics)
    for name in [
        "contextIdentification",
        "isTradeItemABaseUnit",
        "isTradeItemAConsumerUnit",
        "isTradeItemADespatchUnit",
        "isTradeItemAnInvoiceUnit",
        "isTradeItemAnOrderableUnit",
        "tradeItemUnitDescriptorCode",
    ]:
        add_text_value(index, graph, trade_item, GDSN.c863999331, name, text(xml, name), diagnostics)

    for role in ["brandOwner", "informationProviderOfTradeItem"]:
        role_xml = child(xml, role)
        if role_xml is not None:
            add_party(index, graph, base, trade_item, GDSN.c863999331, role_xml, role, gtin, diagnostics)

    brick_code = ""
    classification_xml = child(xml, "gdsnTradeItemClassification")
    if classification_xml is not None:
        brick_code = add_classification(index, graph, base, trade_item, classification_xml, gtin, diagnostics)

    target_xml = child(xml, "targetMarket")
    if target_xml is not None:
        add_target_market(index, graph, base, trade_item, target_xml, gtin, diagnostics)

    sync_xml = child(xml, "tradeItemSynchronisationDates")
    if sync_xml is not None:
        add_sync_dates(index, graph, base, trade_item, sync_xml, gtin, diagnostics)

    nlli_xml = child(xml, "nextLowerLevelTradeItemInformation")
    if nlli_xml is not None:
        add_next_lower_level(index, graph, base, trade_item, nlli_xml, gtin, diagnostics)

    add_supported_extension_modules(index, graph, base, trade_item, xml, gtin, diagnostics)

    return trade_item, gtin, brick_code


def add_catalogue_item(index: OntologyIndex, graph: Graph, base: str, xml: etree._Element, diagnostics: list[str]) -> tuple[URIRef, str, str]:
    trade_xml = child(xml, "tradeItem")
    gtin = text(trade_xml, "gtin") if trade_xml is not None else "unknown"
    catalogue_item = resource(base, "catalogueItem", gtin)
    graph.add((catalogue_item, RDF.type, GDSN.c1402))
    add_text_value(index, graph, catalogue_item, GDSN.c1402, "dataRecipient", text(xml, "dataRecipient"), diagnostics)
    add_text_value(index, graph, catalogue_item, GDSN.c1402, "sourceDataPool", text(xml, "sourceDataPool"), diagnostics)

    state_xml = child(xml, "catalogueItemState")
    if state_xml is not None:
        state = resource(base, "catalogueItemState", gtin)
        graph.add((state, RDF.type, GDSN.c1404))
        graph.add((catalogue_item, index.prop(GDSN.c1402, "catalogueItemState"), state))
        add_text_value(index, graph, state, GDSN.c1404, "catalogueItemStateCode", text(state_xml, "catalogueItemStateCode"), diagnostics)

    brick_code = ""
    if trade_xml is not None:
        trade_item, _, brick_code = add_trade_item(index, graph, base, trade_xml, diagnostics)
        graph.add((catalogue_item, index.prop(GDSN.c1402, "tradeItem"), trade_item))

    for link_xml in children(xml, "catalogueItemChildItemLink"):
        link = resource(base, "catalogueItemChildItemLink", gtin)
        graph.add((link, RDF.type, GDSN.c1403))
        graph.add((catalogue_item, index.prop(GDSN.c1402, "catalogueItemChildItemLink"), link))
        add_text_value(index, graph, link, GDSN.c1403, "quantity", text(link_xml, "quantity"), diagnostics)
        child_catalogue_xml = child(link_xml, "catalogueItem")
        if child_catalogue_xml is not None:
            child_catalogue, _, _ = add_catalogue_item(index, graph, base, child_catalogue_xml, diagnostics)
            graph.add((link, index.prop(GDSN.c1403, "catalogueItem"), child_catalogue))

    return catalogue_item, gtin, brick_code


def relative_path(root: etree._Element, leaf: etree._Element) -> str:
    path = []
    current: etree._Element | None = leaf
    while current is not None and current is not root:
        path.append(local_name(current))
        current = current.getparent()
    path.reverse()
    return "/".join(path)


def extension_report(root: etree._Element) -> list[dict[str, Any]]:
    report = []
    for trade_item in descendants(root, "tradeItem"):
        gtin = text(trade_item, "gtin")
        extension = child(child(trade_item, "tradeItemInformation"), "extension")
        if extension is None:
            continue
        modules = []
        for module in extension:
            values = []
            for leaf in module.iter():
                if len(leaf) == 0 and (leaf.text or "").strip():
                    values.append(
                        {
                            "path": relative_path(module, leaf),
                            "name": local_name(leaf),
                            "value": leaf.text.strip(),
                            "attributes": {etree.QName(key).localname: value for key, value in leaf.attrib.items()},
                        }
                    )
            modules.append(
                {
                    "module": local_name(module),
                    "namespace": etree.QName(module).namespace,
                    "values": values,
                }
            )
        report.append({"gtin": gtin, "modules": modules})
    return report


def summarize_extensions(report: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "gtin": item["gtin"],
            "modules": [
                {
                    "module": module["module"],
                    "namespace": module["namespace"],
                    "value_count": len(module["values"]),
                    "paths": [value["path"] for value in module["values"]],
                }
                for module in item["modules"]
            ],
        }
        for item in report
    ]


def summarize_trade_items(graph: Graph, gpc_graph: Graph) -> list[dict[str, str]]:
    summary = []
    for trade_item in sorted(graph.subjects(RDF.type, GDSN.c863999331), key=str):
        gtin = next(graph.objects(trade_item, GDSN.a5339), None)
        brick_code = ""
        for rdf_type in graph.objects(trade_item, RDF.type):
            if isinstance(rdf_type, URIRef) and str(rdf_type).startswith(str(GPC)) and (rdf_type, GPC.level, Literal(4)) in gpc_graph:
                brick_code = str(rdf_type).removeprefix(str(GPC))
                break
        summary.append({"uri": str(trade_item), "gtin": str(gtin or ""), "gpc_brick": brick_code})
    return summary


def convert(
    xml_path: Path,
    gdsn_path: Path,
    gpc_path: Path,
    base_iri: str,
    prefix: str,
    include_message_envelope: bool = True,
    gdsn_import_iri: str = str(GDSN),
    gpc_import_iri: str = str(GPC),
) -> tuple[Graph, dict[str, Any]]:
    tree = etree.parse(str(xml_path))
    root = tree.getroot()
    gdsn_graph = load_graph(gdsn_path)
    gpc_graph = load_graph(gpc_path)
    index = OntologyIndex(gdsn_graph, gpc_graph)
    graph = Graph()
    bind(graph, prefix, base_iri)
    ontology = resource(base_iri, "ontology")
    graph.add((ontology, RDF.type, OWL.Ontology))
    graph.add((ontology, DCTERMS.source, Literal(str(xml_path))))
    if gdsn_import_iri:
        graph.add((ontology, OWL.imports, URIRef(gdsn_import_iri)))
    if gpc_import_iri:
        graph.add((ontology, OWL.imports, URIRef(gpc_import_iri)))

    diagnostics: list[str] = []
    notification = descendants(root, "catalogueItemNotification")[0]
    if include_message_envelope:
        notification_id = text(child(notification, "catalogueItemNotificationIdentification"), "entityIdentification") or "notification"
        notification_node = resource(base_iri, "catalogueItemNotification", notification_id)
        graph.add((notification_node, RDF.type, GDSN.c1401))
        add_text_value(index, graph, notification_node, GDSN.c1401, "isReload", text(notification, "isReload"), diagnostics)
        for catalogue_xml in children(notification, "catalogueItem"):
            catalogue_item, gtin, brick_code = add_catalogue_item(index, graph, base_iri, catalogue_xml, diagnostics)
            graph.add((notification_node, index.prop(GDSN.c1401, "catalogueItem"), catalogue_item))
    else:
        for trade_xml in descendants(root, "tradeItem"):
            add_trade_item(index, graph, base_iri, trade_xml, diagnostics)

    report = {
        "input": str(xml_path),
        "trade_items": summarize_trade_items(graph, gpc_graph),
        "triple_count": len(graph),
        "diagnostics": diagnostics,
        "imports": {
            "gdsn": gdsn_import_iri,
            "gpc": gpc_import_iri,
        },
        "extension_modules": extension_report(root),
    }
    report["extension_summary"] = summarize_extensions(report["extension_modules"])
    return graph, report


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    graph, report = convert(
        args.input,
        args.gdsn,
        args.gpc,
        args.base_iri,
        args.prefix,
        args.include_message_envelope,
        args.gdsn_import_iri,
        args.gpc_import_iri,
    )
    text_output = graph.serialize(format=args.format)
    if not args.no_validate:
        Graph().parse(data=text_output, format=args.format)
        report["validation"] = {"parse": True}

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text_output, encoding="utf-8")
        report["output"] = str(args.output)
    else:
        sys.stdout.write(text_output)
        report["output"] = "stdout"

    if args.extension_report:
        args.extension_report.parent.mkdir(parents=True, exist_ok=True)
        args.extension_report.write_text(json.dumps(report["extension_modules"], indent=2), encoding="utf-8")

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    status_stream = sys.stdout if args.output else sys.stderr
    if args.print_extensions:
        print(json.dumps(report["extension_summary"], indent=2), file=status_stream)
    print(json.dumps({k: v for k, v in report.items() if k != "extension_modules"}, indent=2), file=status_stream)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
