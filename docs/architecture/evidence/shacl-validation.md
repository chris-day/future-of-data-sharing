---
icon: lucide/badge-check
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# SHACL Generation and Validation
## 5. SHACL generation design

### 5.1 Deterministic Brick-scoped generation

For a GPC Brick:

1. locate the level-4 Brick;
2. collect level-5 children as Attribute Types;
3. collect level-6 children as allowed Attribute Values;
4. emit one `sh:NodeShape` targeting the Brick;
5. emit one property shape per populated Attribute Type;
6. use `sh:in` for controlled values and `sh:maxCount 1` where supported by the demonstrated model;
7. add cross-category or category-specific GDSN shape modules separately.

### 5.2 Reusable generation prompt

The baseline contained the following reusable implementation prompt, retained here as a technical exhibit with minor editorial normalisation:

```text
You have access to gpc.ttl and, optionally, gdsn.ttl.

Given either:
  (a) a GPC Brick code; or
  (b) a GTIN, in which case first resolve the GTIN to its GPC Brick using
      authoritative trade-item data because the ontology contains schema,
      not per-GTIN product instances;

generate a valid SHACL shape as follows:

1. Locate the Brick in gpc.ttl and verify that it is a level-4 resource.
2. Collect level-5 child classes whose rdfs:subClassOf is the Brick.
3. For each Attribute Type, collect level-6 child classes whose
   rdfs:subClassOf is that Attribute Type.
4. Emit one sh:NodeShape targeting the Brick and one sh:property per
   Attribute Type, including sh:path, sh:name, sh:in and sh:maxCount 1.
5. Declare every prefix required for standalone parsing.
6. Where gdsn.ttl is available, emit the selected GDSN shape as a separate
   sh:NodeShape, using real datatypes, classes, multiplicities and code-list
   references from the generated ontology.
7. Validate the output with pySHACL against at least one conforming and one
   deliberately broken instance, and report the result.
```

### 5.3 Reference generator excerpt

```python
import re


def load_gpc(path="gpc.ttl"):
    text = open(path, encoding="utf-8").read()
    records = text.split("\n\n")

    def parse(record):
        item = {}
        match = re.match(r"gpc:(\S+)", record)
        if match:
            item["id"] = match.group(1)
        match = re.search(r"gpc:level (\d+)", record)
        if match:
            item["level"] = int(match.group(1))
        match = re.search(r'rdfs:label "([^"]*)"', record)
        if match:
            item["label"] = match.group(1)
        match = re.search(r"rdfs:subClassOf gpc:(\S+)", record)
        if match:
            item["parent"] = match.group(1)
        return item

    parsed = [parse(record) for record in records if "a owl:Class" in record]
    by_id = {item["id"]: item for item in parsed if "id" in item}
    children = {}
    for item in parsed:
        if "parent" in item:
            children.setdefault(item["parent"], []).append(item["id"])
    return by_id, children


def gpc_shape_for_brick(brick_code, by_id, children, shape_ns="gpc-shapes:"):
    brick = by_id.get(brick_code)
    if brick is None:
        raise ValueError(f"Brick {brick_code} not found in GPC ontology")

    attribute_types = [
        by_id[child_id]
        for child_id in children.get(brick_code, [])
        if by_id[child_id].get("level") == 5
    ]

    slug = lambda label: re.sub(r"[^A-Za-z0-9]+", "", label)
    shape_name = f"{shape_ns}{slug(brick['label'])}Shape"
    lines = [
        f"{shape_name} a sh:NodeShape ;",
        f"    sh:targetClass gpc:{brick_code} ;  # {brick['label']}",
    ]

    for attribute_type in attribute_types:
        values = [
            by_id[child_id]["label"]
            for child_id in children.get(attribute_type["id"], [])
            if by_id[child_id].get("level") == 6
        ]
        if not values:
            continue
        in_list = " ".join(f'"{value}"' for value in values)
        lines += [
            "    sh:property [",
            f'        sh:path gpc:{attribute_type["id"]} ; '
            f'sh:name "{attribute_type["label"]}" ;',
            f"        sh:in ( {in_list} ) ;",
            "        sh:maxCount 1 ;",
            "    ] ;",
        ]

    lines[-1] = lines[-1].rstrip(" ;") + " ."
    return shape_name, "\n".join(lines)
```

The excerpt demonstrates the deterministic pattern but is not a complete production parser. It relies on source formatting conventions and should be replaced or hardened with RDF parsing where appropriate.


## 6. SHACL validation evidence

### 6.1 Corrected illustrative SHACL

The early source fragments were corrected to provide standalone prefixes and independently targeted node shapes. The following compact form preserves the demonstrated structure:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix gpc: <gpc:> .
@prefix gdsn: <gdsn:> .
@prefix gpc-shapes: <https://example.org/gpc-shapes#> .

gpc-shapes:CheeseFrozenShape a sh:NodeShape ;
    sh:targetClass gpc:10000030 ;
    sh:property [
        sh:path gpc:20000192 ;
        sh:name "Firmness of Cheese" ;
        sh:in ( "HARD" "SOFT" "FIRM/SEMI-HARD" "EXTRA HARD" ) ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path gpc:20000031 ;
        sh:name "Type of Cheese" ;
        sh:in ( "GOUDA" "CHEDDAR" "BRIE" "FETA" "MOZZARELLA" "EDAM" "PARMESAN" "GRUYERE" ) ;
        sh:maxCount 1 ;
    ] .

gpc-shapes:TradeItemGDSNShape a sh:NodeShape ;
    sh:targetClass gdsn:TradeItem ;
    sh:property [
        sh:path gdsn:gtin ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path gdsn:allergenRelatedInformation ;
        sh:maxCount 1 ;
        sh:node [
            a sh:NodeShape ;
            sh:property [
                sh:path gdsn:allergen ;
                sh:node [
                    a sh:NodeShape ;
                    sh:property [
                        sh:path gdsn:allergenTypeCode ;
                        sh:in ( "ML" "MFD" "BA" "SU" "PHD" "TUR" ) ;
                        sh:minCount 1 ;
                        sh:maxCount 1 ;
                    ] ;
                    sh:property [
                        sh:path gdsn:levelOfContainmentCode ;
                        sh:minCount 1 ;
                        sh:maxCount 1 ;
                    ] ;
                ] ;
            ] ;
        ] ;
    ] ;
    sh:property [
        sh:path gdsn:nutrientHeader ;
        sh:maxCount 1 ;
        sh:node [
            a sh:NodeShape ;
            sh:property [
                sh:path gdsn:nutrientDetail ;
                sh:node [
                    a sh:NodeShape ;
                    sh:property [
                        sh:path gdsn:nutrientTypeCode ;
                        sh:in ( "ENERC" "FAT" "PRO-" "NA" "CA" ) ;
                        sh:minCount 1 ;
                        sh:maxCount 1 ;
                    ] ;
                    sh:property [
                        sh:path gdsn:quantityContained ;
                        sh:datatype xsd:decimal ;
                    ] ;
                ] ;
            ] ;
        ] ;
    ] .
```

This is an illustrative logical-name shape. The real generated artefacts use source-ID-based CURIEs and, for several associations, `sh:class` references rather than anonymous nested `sh:node` blocks.

### 6.2 Reported `pySHACL` results

| Test instance | Reported result |
|---|---|
| Conforming Cheese record with GTIN, permitted GPC values, allergen code plus containment level, and permitted nutrient code | `Conforms: True` |
| Broken record with firmness `SQUISHY`, nutrient code `PROTEIN_XYZ`, and missing containment level | `Conforms: False` |

The broken record produced three reported violations:

- two `sh:InConstraintComponent` violations;
- one `sh:MinCountConstraintComponent` violation.

The tests demonstrate that category-inappropriate values and missing structured subfields can be detected independently.

### 6.3 Generalisation evidence

The source baseline reported successful shape generation and parse/validation checks for:

| Brick | Attribute Types reported | Result |
|---|---:|---|
| `10000030` Cheese (Frozen) | 6 | Parsed; conforming test passed. |
| `10001198` Smartphones | 2 | Parsed; conforming test passed. |
| `10000159` Beer | 9 | Parsed; conforming test passed. |

A fourth supplied shape, Sugar/Sugar Substitutes (Shelf Stable), contained one Attribute Type and the same selected GDSN shape as the other examples.

### 6.4 Separation of shape and instance

A material correction from the source history is retained here:

- the Product Holon is the product-instance graph;
- the SHACL shape is a separately versioned validation contract;
- the GDSN and GPC ontology modules provide semantic definitions;
- the SSSOM mapping set governs semantic correspondences;
- the bridge package implements approved mappings;
- the Web Vocabulary/schema.org graph is a derived publication view.

Conflating these artefacts prevents independent versioning, provenance and conformance testing.

### 6.5 Reusable code-list strategy

Large code lists should not be unnecessarily repeated in every Brick shape. The evidence identified 218 allergen types and 1,080 nutrient types in the inspected GDSN model. A production SHACL design should consider reusable code-list resources, referenced shapes or generated modules so that one code-list change does not require duplicating a large `sh:in` list across thousands of Brick files.


### 6.6 Real generated shape excerpt

The following excerpt preserves the opaque source-ID-based CURIEs from the supplied Cheese (Frozen) shape. Enumerations are abbreviated only where the source baseline itself abbreviated them.

```turtle
@prefix gdsn: <gdsn:> .
@prefix gpc: <gpc:> .
@prefix gpc-shapes: <gpc-shapes:> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

gpc-shapes:Brick10000030Shape a sh:NodeShape ;
    rdfs:label "Cheese (Frozen) GPC Brick shape" ;
    sh:name "Cheese (Frozen) GPC Brick shape" ;
    sh:property [
        sh:in ( "GOUDA" "CHEDDAR" "BRIE" "FETA" "MOZZARELLA" "EDAM" "PARMESAN" "GRUYERE" "..." ) ;
        sh:maxCount 1 ;
        sh:name "Type of Cheese" ;
        sh:path gpc:20000031
    ], [
        sh:in ( "EXTRA HARD" "FIRM/SEMI-HARD" "HARD" "SOFT" ) ;
        sh:maxCount 1 ;
        sh:name "Firmness of Cheese" ;
        sh:path gpc:20000192
    ], [
        sh:in ( "BARBEQUE" "DIRECT CONSUMPTION" "FONDUE" "SMOKING" ) ;
        sh:maxCount 1 ;
        sh:name "Intended Use of Cheese" ;
        sh:path gpc:20003080
    ], [
        sh:in ( "SEMI-HARD CHEESE" "SEMI-SOFT CHEESE" "SOFT / SOFT RIPENED CHEESE" "..." ) ;
        sh:maxCount 1 ;
        sh:name "Kind of Cheese" ;
        sh:path gpc:20003081
    ], [
        sh:in ( "EXTRA EXTRA SHARP" "EXTRA SHARP" "SHARP" ) ;
        sh:maxCount 1 ;
        sh:name "Sharpness of Cheese" ;
        sh:path gpc:20002867
    ], [
        sh:in ( "AUSTRIA - TYROL/VORARLBERG/CARINTHIA" "AUSTRIA - UPPER/LOWER AUSTRIA" ) ;
        sh:maxCount 1 ;
        sh:name "Origin of Cheese" ;
        sh:path gpc:20000505
    ] ;
    sh:targetClass gpc:10000030 .

gpc-shapes:TradeItemGDSNShape a sh:NodeShape ;
    rdfs:comment "Generated from selected GDSN properties. Source property domains are preserved as sh:description because not all selected properties are direct TradeItem properties in the generated ontology." ;
    sh:name "Cross-category GDSN TradeItem shape" ;
    sh:property [
        sh:datatype gdsn:c1450 ;
        sh:maxCount 1 ;
        sh:minCount 0 ;
        sh:name "gtin" ;
        sh:path gdsn:a-1292425203
    ], [
        sh:datatype gdsn:c1481031847 ;
        sh:minCount 0 ;
        sh:name "ingredientStatement" ;
        sh:path gdsn:a812659001
    ], [
        sh:datatype xsd:float ;
        sh:maxCount 1 ;
        sh:minCount 0 ;
        sh:name "packagingRecycledContentRatio" ;
        sh:path gdsn:a212299678
    ], [
        sh:class gdsn:c2147348056 ;
        sh:minCount 0 ;
        sh:name "claimDetail" ;
        sh:path gdsn:assoc_45067187_2147348056_4
    ], [
        sh:class gdsn:c1672558995 ;
        sh:minCount 0 ;
        sh:name "allergen" ;
        sh:path gdsn:assoc_-474206270_1672558995_1
    ], [
        sh:class gdsn:c1322 ;
        sh:minCount 0 ;
        sh:name "nutrientDetail" ;
        sh:path gdsn:assoc_1336934671_1322_1
    ], [
        sh:class gdsn:c-474206270 ;
        sh:minCount 0 ;
        sh:name "allergenRelatedInformation" ;
        sh:path gdsn:assoc_-1935341322_-474206270_1
    ], [
        sh:class gdsn:c1336934671 ;
        sh:minCount 0 ;
        sh:name "nutrientHeader" ;
        sh:path gdsn:assoc_1340910615_1336934671_2
    ] ;
    sh:targetClass gdsn:c863999331 .
```

The shape’s own comment records the flattening decision: selected properties from several source domains are validated against a TradeItem-targeted shape, while the original domains remain annotations. This decision must be aligned with the Product Holon construction convention.

---
