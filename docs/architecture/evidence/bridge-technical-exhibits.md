---
icon: lucide/braces
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Bridge Technical Exhibits
## 10. Bridge technical exhibits

### 10.1 Illustrative OWL bridge axioms

Where a reviewed source and target property are semantically and structurally equivalent, the compiled OWL bridge module may contain axioms such as:

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix gs1: <https://ref.gs1.org/voc/> .
@prefix gdsn: <https://example.org/generated-gdsn/> .

## Illustrative only. Production source properties shall use reviewed mappings
## to the real generated GDSN IRIs.

gs1:ingredientStatement
    owl:equivalentProperty gdsn:reviewedIngredientStatementProperty .
```

The example demonstrates compilation form, not approval of a specific mapping.

### 10.2 Manchester Syntax model

The source baseline included a human-readable Manchester Syntax model. The consolidated form below separates stable classes and properties from conditional rules:

```text
Prefix: : <https://example.org/gs1-product-holon-bridge#>
Prefix: owl: <http://www.w3.org/2002/07/owl#>
Prefix: rdfs: <http://www.w3.org/2000/01/rdf-schema#>
Prefix: xsd: <http://www.w3.org/2001/XMLSchema#>
Prefix: gs1: <https://ref.gs1.org/voc/>
Prefix: gdsn: <https://example.org/generated-gdsn/>
Prefix: gpc: <https://example.org/generated-gpc/>
Prefix: schema: <https://schema.org/>

Ontology: <https://example.org/gs1-product-holon-bridge>

Class: gdsn:TradeItem
Class: gpc:FoodBeverage
Class: gpc:CheeseCheeseSubstitutes
    SubClassOf: gpc:FoodBeverage
Class: gpc:CheeseFrozen
    SubClassOf: gpc:CheeseCheeseSubstitutes,
                gdsn:TradeItem

Class: schema:Product
Class: gs1:Product
Class: schema:PropertyValue

ObjectProperty: gdsn:nutrientDetail
    Domain: gdsn:TradeItem

DataProperty: gdsn:nutrientTypeCode
DataProperty: gdsn:quantityContained
DataProperty: schema:calories
DataProperty: schema:fatContent
DataProperty: schema:proteinContent
DataProperty: schema:sodiumContent

ObjectProperty: gpc:hasAttribute
    Domain: gdsn:TradeItem

ObjectProperty: schema:additionalProperty
    Range: schema:PropertyValue

DataProperty: schema:propertyID
DataProperty: schema:name
DataProperty: schema:value
```

The source listing also contained a representative Gouda ABox. Its purpose was to demonstrate the distinction between the TBox, Product Holon instance data and properties deliberately left without direct `EquivalentTo` axioms.

The baseline noted that the Manchester Syntax file had been hand-checked against the grammar but not parsed by a formal Manchester parser. It should therefore be treated as an explanatory exhibit until parser validation is recorded.

### 10.3 DL-safe nutrient rules

The following rules express Route 2 derivations. Syntax varies between rule engines; the logical content is:

```text
TradeItem(?product) ^
nutrientDetail(?product, ?detail) ^
nutrientTypeCode(?detail, "ENERC") ^
quantityContained(?detail, ?quantity)
  -> calories(?product, ?quantity)

TradeItem(?product) ^
nutrientDetail(?product, ?detail) ^
nutrientTypeCode(?detail, "FAT") ^
quantityContained(?detail, ?quantity)
  -> fatContent(?product, ?quantity)

TradeItem(?product) ^
nutrientDetail(?product, ?detail) ^
nutrientTypeCode(?detail, "PRO-") ^
quantityContained(?detail, ?quantity)
  -> proteinContent(?product, ?quantity)

TradeItem(?product) ^
nutrientDetail(?product, ?detail) ^
nutrientTypeCode(?detail, "NA") ^
quantityContained(?detail, ?quantity)
  -> sodiumContent(?product, ?quantity)
```

All variables bind to named Product Holon individuals already present in the ABox. The rule module should be independently versioned and imported by the bridge ontology.

### 10.4 Consolidated SPARQL transform rules

The source baseline executed the following representative rules. Namespace values are illustrative and shall be replaced by compiled real IRIs in production.

```sparql
PREFIX gdsn:   <https://example.org/gdsn/>
PREFIX gpc:    <https://example.org/gpc/>
PREFIX schema: <https://schema.org/>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>

## Route 2 — fixed, one rule per NutrientTypeCode with a schema.org target

CONSTRUCT { ?product schema:calories ?qty }
WHERE {
  ?product gdsn:nutrientDetail ?n .
  ?n gdsn:nutrientTypeCode "ENERC" ;
     gdsn:quantityContained ?qty .
}

CONSTRUCT { ?product schema:fatContent ?qty }
WHERE {
  ?product gdsn:nutrientDetail ?n .
  ?n gdsn:nutrientTypeCode "FAT" ;
     gdsn:quantityContained ?qty .
}

CONSTRUCT { ?product schema:proteinContent ?qty }
WHERE {
  ?product gdsn:nutrientDetail ?n .
  ?n gdsn:nutrientTypeCode "PRO-" ;
     gdsn:quantityContained ?qty .
}

CONSTRUCT { ?product schema:sodiumContent ?qty }
WHERE {
  ?product gdsn:nutrientDetail ?n .
  ?n gdsn:nutrientTypeCode "NA" ;
     gdsn:quantityContained ?qty .
}

## Route 3 — one generic rule for GPC facts

CONSTRUCT {
  ?product schema:additionalProperty [
    a schema:PropertyValue ;
    schema:propertyID ?attr ;
    schema:name ?label ;
    schema:value ?value
  ]
}
WHERE {
  ?product gpc:hasAttribute ?attr .
  ?attr rdfs:label ?label ;
        gpc:value ?value .
}

## Route 3 — generic residual nutrient rule

CONSTRUCT {
  ?product schema:additionalProperty [
    a schema:PropertyValue ;
    schema:propertyID ?code ;
    schema:value ?qty
  ]
}
WHERE {
  ?product gdsn:nutrientDetail ?n .
  ?n gdsn:nutrientTypeCode ?code ;
     gdsn:quantityContained ?qty .
  FILTER(?code NOT IN ("ENERC", "FAT", "PRO-", "NA"))
}
```

In the final architecture, these substantive transforms may be compiled as DL-safe rules where the chosen reasoner supports them, leaving SPARQL as a thin export layer. The executed SPARQL remains valuable as a deterministic reference and regression oracle.

### 10.5 Thin export query pattern

Where the reasoner has already materialised the approved target properties, a thin export query may select only the target profile:

```sparql
PREFIX schema: <https://schema.org/>
PREFIX gs1: <https://ref.gs1.org/voc/>

CONSTRUCT {
  ?product a schema:Product ;
           ?property ?value .
}
WHERE {
  ?product a schema:Product ;
           ?property ?value .
  VALUES ?property {
    schema:gtin
    gs1:ingredientStatement
    schema:calories
    schema:fatContent
    schema:proteinContent
    schema:sodiumContent
    schema:additionalProperty
  }
}
```

The actual allow-list belongs to a versioned publication profile.

### 10.6 Worked Web Vocabulary/schema.org projection

The source baseline used the following logical projection for the Gouda example:

```json
{
  "@context": {
    "gs1": "https://ref.gs1.org/voc/",
    "schema": "https://schema.org/"
  },
  "@id": "https://example.com/01/09506000134352",
  "@type": "schema:Product",
  "schema:gtin": "09506000134352",
  "gs1:ingredientStatement": "Pasteurised milk, salt, rennet, cheese cultures.",
  "schema:nutrition": {
    "@type": "schema:NutritionInformation",
    "schema:calories": "1500 kJ",
    "schema:fatContent": "28 g",
    "schema:proteinContent": "24 g",
    "schema:sodiumContent": "620 mg"
  },
  "schema:additionalProperty": [
    {
      "@type": "schema:PropertyValue",
      "schema:propertyID": "gdsn:NutrientTypeCode-CA",
      "schema:name": "Calcium",
      "schema:value": "700 mg"
    },
    {
      "@type": "schema:PropertyValue",
      "schema:propertyID": "gpc:20000031",
      "schema:name": "Type of Cheese",
      "schema:value": "GOUDA"
    },
    {
      "@type": "schema:PropertyValue",
      "schema:propertyID": "gpc:20000192",
      "schema:name": "Firmness of Cheese",
      "schema:value": "FIRM/SEMI-HARD"
    }
  ]
}
```

The example is an illustrative output structure. Every first-class target term and source-to-target mapping still requires the governance process described above.

### 10.7 Product and Offer composition

A marketplace representation should compose product and commercial facts as separate objects:

```json
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "gtin": "09506000134352",
  "name": "Illustrative Gouda",
  "offers": [
    {
      "@type": "Offer",
      "seller": { "@type": "Organization", "name": "Seller A" },
      "price": "4.50",
      "priceCurrency": "GBP",
      "availability": "https://schema.org/InStock"
    },
    {
      "@type": "Offer",
      "seller": { "@type": "Organization", "name": "Seller B" },
      "price": "4.75",
      "priceCurrency": "GBP",
      "availability": "https://schema.org/InStock"
    }
  ]
}
```

The price and availability are not manufacturer Product Holon facts unless the manufacturer is also the seller and is authoritative for the offer.

---
