---
icon: lucide/file-code
---

# KATO Instance RDF

Convert the KATO GDSN XML sample to RDF:

```bash
./gdsn-xml-to-rdf \
  --input artefacts/KATO/add.xml \
  --gdsn build/gdsn.ttl \
  --gpc build/gpc.ttl \
  --output build/KATO/kato-instances.ttl \
  --extension-report build/KATO/kato-extensions.json \
  --report-json build/KATO/kato-instances.report.json \
  --print-extensions
```

KATO GTINs:

| GTIN | Generated instance IRI |
| --- | --- |
| `25196100024882` | `urn:gs1:sample:kato:gtin/25196100024882` |
| `25196100024899` | `urn:gs1:sample:kato:gtin/25196100024899` |

The generated instance graph preserves qualified values as RDF value nodes.
For example, measurements use `gdsn:c1490` value nodes with decimal
`rdf:value` and `measurementUnitCode`.

Example value node:

```turtle
<urn:gs1:sample:kato:value/25196100024899/height>
  a gdsn:c1490 ;
  rdf:value "1.0"^^xsd:decimal ;
  gdsn:a7085 "MMT"^^xsd:string .
```

Implemented extension modules include:

| XML module | RDF path |
| --- | --- |
| `deliveryPurchasingInformationModule` | `TradeItemInformation -> extensionModule -> DeliveryPurchasingInformationModule` |
| `tradeItemDescriptionModule` | `TradeItemInformation -> extensionModule -> TradeItemDescriptionModule` |
| `tradeItemMeasurementsModule` | `TradeItemInformation -> extensionModule -> TradeItemMeasurementsModule` |
| `tradeItemDataCarrierAndIdentificationModule` | `TradeItemInformation -> extensionModule -> TradeItemDataCarrierAndIdentificationModule` |
