---
icon: lucide/package-check
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Worked Product Holons
## Part III — Worked Product Holons

## 7. Product Holon construction pattern

The worked examples use the following identifiers. Digital Link AI (01) paths and GDSN GTIN values use GTIN-14 representation.

| Example | Supplied identifier | GTIN-14 used in the Product Holon | GPC Brick | Brick-scoped value used |
|---|---:|---:|---:|---|
| Cheese (Frozen) — Gouda | `09506000134352` | `09506000134352` | `10000030` | Type of Cheese = `GOUDA` |
| Smartphone | GTIN-13 `0195950643718` | `00195950643718` | `10001198` | Input Registration = `TOUCHSCREEN` |
| Beer — illustrative IPA | GTIN-14 `00083783000085` | `00083783000085` | `10000159` | Style of Beer = `INDIA PALE ALE (IPA)` |
| Sugar/Sugar Substitutes | `04005500023340` | `04005500023340` | `10000043` | Type of Sugar/Sugar Substitute = `SUCROSE` |
| Compote classification example | GTIN-13 `5000119096753` | `05000119096753` | `10000217` | Type of Jam/Marmalade = `COMPOTE` (`30000728`) |
| Milk hierarchy example — Whole Milk | GTIN-14 `05000169015254` | `05000169015254` | `10000025` (verified normalisation) | Fat content = `Whole`; Packaging type = `Plastic bottle` (user-supplied labels; GPC Attribute codes unresolved) |

### 7.1 Logical construction algorithm

For a product identifier:

1. resolve the product record and GPC Brick;
2. retain the classification ancestor chain;
3. collect populated Brick-scoped GPC facts;
4. collect applicable GDSN facts selected by the profile;
5. preserve structured records and units;
6. attach provenance and version information;
7. validate the instance graph;
8. link parent or child Product Holons where required;
9. release only after validation and publication policy checks.

### 7.2 Cheese (Frozen), Brick `10000030`

The real generated shape contained six GPC properties:

| GPC property | Label | Example value used |
|---|---|---|
| `gpc:20002867` | Sharpness of Cheese | not populated in the Gouda example |
| `gpc:20000505` | Origin of Cheese | not populated in the Gouda example |
| `gpc:20000031` | Type of Cheese | `GOUDA` |
| `gpc:20003080` | Intended Use of Cheese | `DIRECT CONSUMPTION` |
| `gpc:20000192` | Firmness of Cheese | `FIRM/SEMI-HARD` |
| `gpc:20003081` | Kind of Cheese | `SEMI-HARD CHEESE` |

The following example uses the real opaque GDSN CURIEs reported in the supplied shape where available. Nested logical property names are retained for readability where the baseline did not reproduce every opaque identifier.

```json
{
  "@id": "https://example.com/01/09506000134352",
  "@type": ["gpc:10000030", "gdsn:c863999331"],
  "gpc:20000031": "GOUDA",
  "gpc:20000192": "FIRM/SEMI-HARD",
  "gpc:20003080": "DIRECT CONSUMPTION",
  "gpc:20003081": "SEMI-HARD CHEESE",
  "gdsn:a-1292425203": "09506000134352",
  "gdsn:a812659001": "Pasteurised milk, salt, rennet, cheese cultures.",
  "gdsn:a212299678": 0.30,
  "gdsn:allergenRelatedInformation": {
    "gdsn:allergen": {
      "gdsn:allergenTypeCode": "ML",
      "gdsn:levelOfContainmentCode": "CONTAINS"
    }
  },
  "gdsn:nutrientHeader": {
    "gdsn:nutrientDetail": [
      { "gdsn:nutrientTypeCode": "ENERC", "gdsn:quantityContained": 1500 },
      { "gdsn:nutrientTypeCode": "FAT", "gdsn:quantityContained": 28 },
      { "gdsn:nutrientTypeCode": "PRO-", "gdsn:quantityContained": 24 },
      { "gdsn:nutrientTypeCode": "NA", "gdsn:quantityContained": 620 }
    ]
  }
}
```

The values are illustrative. The shape makes Sharpness and Origin optional, so leaving them absent is distinct from asserting a value.

### 7.3 Smartphones, Brick `10001198`

The supplied shape defined:

- `gpc:20002603` — Input Registration: `QWERTZ/QWERTY KEYBOARD`, `REDUCED PHONE KEYBOARD`, `TOUCHSCREEN`;
- `gpc:20001127` — System: `1 G`, `2 G`, `2.5 G`, `3 G`.

Illustrative Product Holon:

```json
{
  "@id": "https://example.com/01/00195950643718",
  "@type": ["gpc:10001198", "gdsn:c863999331"],
  "gpc:20002603": "TOUCHSCREEN",
  "gpc:20001127": "3 G",
  "gdsn:a-1292425203": "00195950643718",
  "gdsn:a212299678": 0.15
}
```

The supplied product identifier is GTIN-13 `0195950643718`. The Digital Link AI (01) path and the GDSN value above use its zero-padded GTIN-14 representation, `00195950643718`. The enumeration’s lack of 4G and 5G is a source-model limitation. It must be governed as a model issue rather than corrected silently in generated shapes.

### 7.4 Beer, Brick `10000159`

The supplied shape excerpt included:

- Colour of Beer;
- Style of Beer;
- Flavoured or mixed status;
- Type of Beer;
- Origin of Beer;
- Taste.

Illustrative Product Holon:

```json
{
  "@id": "https://example.com/01/00083783000085",
  "@type": ["gpc:10000159", "gdsn:c863999331"],
  "gpc:20003020": "AMBER",
  "gpc:20000170": "INDIA PALE ALE (IPA)",
  "gpc:20002868": "NO, BEER ONLY",
  "gpc:20000017": "ALE",
  "gpc:20000502": "UNITED KINGDOM - ENGLAND - KENT",
  "gpc:20002973": "BITTER",
  "gdsn:a-1292425203": "00083783000085",
  "gdsn:a812659001": "Water, Malted Barley, Hops, Yeast.",
  "gdsn:a212299678": 0.25,
  "gdsn:allergenRelatedInformation": {
    "gdsn:allergen": {
      "gdsn:allergenTypeCode": "BA",
      "gdsn:levelOfContainmentCode": "CONTAINS"
    }
  }
}
```

The source baseline used `BA` as a valid code but did not independently confirm its human-readable expansion. The example therefore does not assert an expansion beyond the code itself.

The supplied Beer identifier is the valid GTIN-14 `00083783000085`. It is used unchanged in the Digital Link AI (01) path and GDSN value.

### 7.5 Sugar/Sugar Substitutes, Brick `10000043`

The supplied shape defined one Brick-specific property, Type of Sugar/Sugar Substitute. An illustrative Product Holon is:

```json
{
  "@id": "https://example.com/01/04005500023340",
  "@type": ["gpc:10000043", "gdsn:c863999331"],
  "gpc:20000172": "SUCROSE",
  "gdsn:a-1292425203": "04005500023340",
  "gdsn:a812659001": "Sugar (100% sucrose).",
  "gdsn:a212299678": 0.40,
  "gdsn:nutrientHeader": {
    "gdsn:nutrientDetail": [
      { "gdsn:nutrientTypeCode": "ENERC", "gdsn:quantityContained": 1700 },
      { "gdsn:nutrientTypeCode": "FAT", "gdsn:quantityContained": 0 },
      { "gdsn:nutrientTypeCode": "PRO-", "gdsn:quantityContained": 0 },
      { "gdsn:nutrientTypeCode": "NA", "gdsn:quantityContained": 0 }
    ]
  }
}
```

An explicit zero is an assertion. An omitted nutrient is not equivalent to zero.

The earlier illustrative Sugar identifier ended in an invalid check digit. This release corrects it to valid GTIN-14 `04005500023340`; it remains illustrative and is not an assertion about an actual commercial product.

### 7.6 Compote classification example, Brick `10000217`

The supplied classification code `30000728` is not a GPC Brick identifier. It is the GPC Attribute Value **COMPOTE** for Attribute `20000118`, **Type of Jam/Marmalade**, within Brick `10000217`, **Jams/Marmalades (Shelf Stable)**. The Product Holon is therefore normalised to Brick `10000217` while retaining `30000728` as the controlled Attribute Value.

No generated SHACL shape for Brick `10000217` was supplied with the original evidence set. This example demonstrates product-instance normalisation only; it does not claim that a Brick-specific generated shape has been executed or validated for this category. Because no authoritative product master-data record was supplied, `COMPOTE` is retained as an illustrative, user-supplied classification value and requires brand-owner verification before it is treated as product truth.

```json
{
  "@id": "https://example.com/01/05000119096753",
  "@type": ["gpc:10000217", "gdsn:c863999331"],
  "gpc:20000118": "COMPOTE",
  "gdsn:a-1292425203": "05000119096753"
}
```

The supplied product identifier is GTIN-13 `5000119096753`. The Digital Link AI (01) path and GDSN value use its valid zero-padded GTIN-14 representation, `05000119096753`. No ingredients, nutrition, claims or other product assertions have been invented for this example.

### 7.7 Milk hierarchy example — Whole Milk, GTIN `05000169015254`

The supplied GTIN `05000169015254` is a valid GTIN-14. The hierarchy supplied with the example is preserved below as request provenance, but it is not used unchanged as the verified GPC classification because several supplied codes conflict with GS1 GPC source material.

| Level | Hierarchy supplied with the example | Verified GPC normalisation used in this pack |
|---|---|---|
| Segment | `10000000` — Food, Beverages and Tobacco | `50000000` — Food/Beverage/Tobacco |
| Family | `50131700` — Dairy Products | `50130000` — Milk/Butter/Cream/Yogurts/Cheese/Eggs/Substitutes |
| Class | `50131701` — Milk (Perishable) | `50131700` — Milk/Milk Substitutes |
| Brick | `10000236` — Milk - Cow's (Fresh) | `10000025` — Milk (Perishable) |

Official GS1 mapping material places `50000000` at Segment level, `50130000` at Family level, `50131700` at Class level and `10000025` at Brick level for perishable milk. Code `10000236` is used for a Nuts/Seeds prepared/processed Brick rather than a milk Brick. The label **Milk - Cow's (Fresh)** is therefore retained as a human-readable description of the requested product example, not asserted as the official label of Brick `10000236`.

The requested Brick characteristics are retained as illustrative facts:

- Fat content = `Whole`;
- Packaging type = `Plastic bottle`.

No GPC Attribute Type or Attribute Value identifiers were supplied for those characteristics, and no generated SHACL shape for Brick `10000025` was part of the evidence set. The example therefore does not invent GPC Attribute codes. It uses generic `schema:PropertyValue` records until the applicable Brick-scoped GPC attributes and controlled values are resolved from the authoritative GPC release.

```json
{
  "@context": {
    "gpc": "gpc:",
    "gdsn": "gdsn:",
    "schema": "https://schema.org/",
    "example": "https://example.com/holon-evidence/"
  },
  "@id": "https://example.com/01/05000169015254",
  "@type": ["gpc:10000025", "gdsn:c863999331"],
  "gdsn:a-1292425203": "05000169015254",
  "example:gpcHierarchy": [
    { "level": "Segment", "@id": "gpc:50000000", "label": "Food/Beverage/Tobacco" },
    { "level": "Family", "@id": "gpc:50130000", "label": "Milk/Butter/Cream/Yogurts/Cheese/Eggs/Substitutes" },
    { "level": "Class", "@id": "gpc:50131700", "label": "Milk/Milk Substitutes" },
    { "level": "Brick", "@id": "gpc:10000025", "label": "Milk (Perishable)" }
  ],
  "schema:additionalProperty": [
    {
      "@type": "schema:PropertyValue",
      "schema:name": "Fat content",
      "schema:value": "Whole",
      "example:mappingStatus": "User-supplied illustrative value; GPC Attribute identifier unresolved"
    },
    {
      "@type": "schema:PropertyValue",
      "schema:name": "Packaging type",
      "schema:value": "Plastic bottle",
      "example:mappingStatus": "User-supplied illustrative value; GPC Attribute identifier unresolved"
    }
  ]
}
```

The generic property representation is deliberate: it preserves the requested facts without misrepresenting unverified labels as governed GPC Attribute Type or Attribute Value identifiers. A later generated Brick `10000025` SHACL profile can replace these generic records with GPC-native predicates and controlled values once those identifiers have been verified.

### 7.8 Cross-Brick comparison of the selected GDSN shape

The four supplied `TradeItemGDSNShape` blocks were reported as identical. The selected properties were:

| Logical label | Reported generated path or target |
|---|---|
| GTIN | `gdsn:a-1292425203` |
| ingredientStatement | `gdsn:a812659001` |
| packagingRecycledContentRatio | `gdsn:a212299678` |
| claimDetail | `gdsn:assoc_45067187_2147348056_4` |
| allergen | `gdsn:assoc_-474206270_1672558995_1` |
| nutrientDetail | `gdsn:assoc_1336934671_1322_1` |
| allergenRelatedInformation | `gdsn:assoc_-1935341322_-474206270_1` |
| nutrientHeader | `gdsn:assoc_1340910615_1336934671_2` |

This fixed profile demonstrates cross-category reuse but also exposes irrelevant food-oriented slots for Smartphones. It should be treated as a reference profile, not the final architecture.

### 7.9 Evidence that the selected shape is too narrow

The mapping output contained cheese-relevant GDSN attributes absent from the fixed selected shape, including:

- `isRindEdible`;
- `fatInMilkContent`;
- `cheeseMaturationPeriodDescription`;
- `maturationMethod`;
- `sourceAnimal`.

This supports a modular approach: a small cross-category core plus category- and use-case-specific GDSN modules.

### 7.10 Variety packs

The source baseline reported 338 GPC Variety Pack Bricks. The product-level pattern is:

- the pack has its own GTIN and one Variety Pack Brick;
- each constituent item has its own GTIN, Brick and Product Holon;
- GDSN trade-item hierarchy relationships link parent and children;
- quantities and component counts remain explicit;
- each child remains independently validated and resolvable.

This is analogous to nested holons but should not be confused with a claim that GPC alone models every component relationship.

---
