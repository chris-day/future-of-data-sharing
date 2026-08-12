# Google Product Taxonomy TSV Mapping

## 1. Purpose

This document investigates `artefacts/google/taxonomy-with-ids.en-GB.txt` for
mapping into `uml2semantics-python` TSV artefacts.

The source is a Google Product Taxonomy text dump. Its semantics are similar to
GPC in that it is a product classification hierarchy rather than a UML class
model. It should therefore be generated as a separate taxonomy ontology module,
not folded into the main GDSN ontology.

## 2. Source File

Source path:

```text
artefacts/google/taxonomy-with-ids.en-GB.txt
```

Header:

```text
# Google_Product_Taxonomy_Version: 2021-09-21
```

Record format:

```text
<category-id> - <level-1 label> > <level-2 label> > ... > <leaf label>
```

Example:

```text
543683 - Animals & Pet Supplies > Pet Supplies > Cat Supplies > Cat Food > Prescription Cat Food
```

## 3. Observed Structure

Parsed source statistics:

| Measure | Value |
| --- | ---: |
| Taxonomy version | `2021-09-21` |
| Total category rows | 5,595 |
| Unique category IDs | 5,595 |
| Duplicate category IDs | 0 |
| Unique full paths | 5,595 |
| Duplicate full paths | 0 |
| Missing parent paths | 0 |
| Maximum depth | 7 |
| Leaf categories | 4,719 |
| Non-leaf categories | 876 |

Depth distribution:

| Depth | Category count |
| ---: | ---: |
| 1 | 21 |
| 2 | 192 |
| 3 | 1,349 |
| 4 | 2,203 |
| 5 | 1,385 |
| 6 | 397 |
| 7 | 48 |

Top-level category counts:

| Top-level category | Rows under root |
| --- | ---: |
| Home & Garden | 1,035 |
| Sporting Goods | 801 |
| Hardware | 522 |
| Arts & Entertainment | 500 |
| Electronics | 418 |
| Food, Beverages & Tobacco | 364 |
| Health & Beauty | 346 |
| Clothing & Accessories | 240 |
| Vehicles & Parts | 230 |
| Business & Industrial | 224 |
| Toys & Games | 174 |
| Office Supplies | 166 |
| Animals & Pet Supplies | 125 |
| Furniture | 121 |
| Cameras & Optics | 104 |
| Baby & Toddler | 87 |
| Mature | 38 |
| Software | 35 |
| Media | 30 |
| Luggage & Bags | 22 |
| Religious & Ceremonial | 13 |

## 4. Source Semantics

Each row identifies one Google product category.

The numeric ID is the stable category identifier. The text after ` - ` is the
complete hierarchy path for that category. Parent-child relationships are not
expressed by explicit parent IDs, but they are recoverable from the path:

```text
Animals & Pet Supplies > Pet Supplies > Cat Supplies > Cat Food
```

is the parent path of:

```text
Animals & Pet Supplies > Pet Supplies > Cat Supplies > Cat Food > Prescription Cat Food
```

The file includes both branch nodes and leaf nodes. Since every parent path is
present as its own row, the hierarchy can be reconstructed without synthetic
intermediate categories.

## 5. Ontology Module Recommendation

Recommended output:

```text
build/gdsn-tsv/google/
```

Generate the TSV bundle with:

```bash
google-taxonomy-to-tsv \
  --input-file artefacts/google/taxonomy-with-ids.en-GB.txt \
  --output-dir build/gdsn-tsv
```

The command follows the same output-directory convention as
`gdsn-json-to-tsv`: `--output-dir` is the parent output directory and the
module is written below it. By default the module subdirectory is `google`.

Recommended ontology IRI:

```text
urn:google:product-taxonomy:
```

Recommended namespace prefix:

```text
google:
```

Recommended root class:

```text
google:GoogleProductTaxonomyCategory
```

This should be a separate ontology output, like GPC. It should not be generated
inside the GDSN ontology because it is an external product classification
taxonomy and has independent lifecycle/versioning.

## 6. TSV Mapping Strategy

### 6.1 Classes.tsv

Emit every Google category as a class.

Recommended class CURIE:

```text
google:<category-id>
```

Example:

```text
google:543683
```

Recommended parent mapping:

- top-level categories: parent is `google:GoogleProductTaxonomyCategory`
- nested categories: parent is the category ID for the immediate parent path

Recommended `Classes.tsv` columns:

| TSV column | Source |
| --- | --- |
| `Curie` | `google:<category-id>` |
| `Name` | final path segment, normalised for display |
| `ParentNames` | parent category CURIE, or `google:GoogleProductTaxonomyCategory` for depth 1 |
| `Definition` | `Google Product Taxonomy category: <full path>` |
| `IsAbstract` | blank |
| `ChoiceOf` | blank |
| `ChoiceSemantics` | blank |

Example rows:

| Curie | Name | ParentNames | Definition |
| --- | --- | --- | --- |
| `google:GoogleProductTaxonomyCategory` | Google Product Taxonomy Category |  | Root class for Google Product Taxonomy categories. |
| `google:1` | Animals & Pet Supplies | `google:GoogleProductTaxonomyCategory` | Google Product Taxonomy category: Animals & Pet Supplies |
| `google:2` | Pet Supplies | `google:1` | Google Product Taxonomy category: Animals & Pet Supplies > Pet Supplies |
| `google:4` | Cat Supplies | `google:2` | Google Product Taxonomy category: Animals & Pet Supplies > Pet Supplies > Cat Supplies |
| `google:3367` | Cat Food | `google:4` | Google Product Taxonomy category: Animals & Pet Supplies > Pet Supplies > Cat Supplies > Cat Food |
| `google:543683` | Prescription Cat Food | `google:3367` | Google Product Taxonomy category: Animals & Pet Supplies > Pet Supplies > Cat Supplies > Cat Food > Prescription Cat Food |

### 6.2 Attributes.tsv

No category attributes are present in the source file.

Recommended handling:

- emit an empty `Attributes.tsv`, with header only
- do not infer attributes from category labels

### 6.3 Datatypes.tsv

No datatypes are present in the source file.

Recommended handling:

- emit an empty `Datatypes.tsv`, with header only

### 6.4 Enumerations.tsv and EnumerationNamedValues.tsv

The Google taxonomy is hierarchical class data, not a flat code list.

Recommended handling:

- emit categories as classes, not enumeration values
- emit empty `Enumerations.tsv` and `EnumerationNamedValues.tsv`, with headers
  only

This keeps the output aligned with GPC, where product categories are navigable
classes and hierarchy is represented through `rdfs:subClassOf`.

### 6.5 AnnotationProperties.tsv

Recommended Google-specific annotation properties:

| Curie | Name | Definition |
| --- | --- | --- |
| `google:categoryId` | Category ID | Google Product Taxonomy numeric category identifier. |
| `google:level` | Level | One-based depth in the Google Product Taxonomy path. |
| `google:path` | Path | Full Google Product Taxonomy category path. |
| `google:parentCategoryId` | Parent category ID | Immediate parent Google Product Taxonomy category identifier. |
| `google:isLeaf` | Is leaf | Whether the category has no child categories in this taxonomy version. |
| `google:taxonomyVersion` | Taxonomy version | Google Product Taxonomy source version. |
| `google:sourceLine` | Source line | Source line number in `taxonomy-with-ids.en-GB.txt`. |

### 6.6 Annotations.tsv

Emit annotations for each category class.

Recommended annotations:

| TargetCurie | AnnotationProperty | Value |
| --- | --- | --- |
| category class | `google:categoryId` | numeric ID |
| category class | `google:level` | path depth |
| category class | `google:path` | full path |
| category class | `google:parentCategoryId` | parent ID, blank for depth 1 |
| category class | `google:isLeaf` | `true` or `false` |
| category class | `google:taxonomyVersion` | `2021-09-21` |
| category class | `google:sourceLine` | line number |

The root class should also receive:

| TargetCurie | AnnotationProperty | Value |
| --- | --- | --- |
| `google:GoogleProductTaxonomyCategory` | `google:taxonomyVersion` | `2021-09-21` |

## 7. CURIE and Label Considerations

The numeric Google category IDs are stable identifiers and should be used in the
CURIE local part.

Recommended:

```text
google:543683
```

Avoid generating CURIEs from labels such as:

```text
google:PrescriptionCatFood
```

Label-derived CURIEs are less stable and can collide if labels change. The
source analysis found no duplicate final labels in this file, but ID-based
CURIEs are still preferable because the taxonomy is explicitly ID-driven.

The category label should be preserved as `rdfs:label`, and the full path
should be preserved with `google:path`.

## 8. Relationship to GPC and GDSN

Google Product Taxonomy is similar to GPC because both are product category
hierarchies. The main semantic difference is that GPC also carries level-5
attribute types and level-6 allowed values, which are used by the holon SHACL
generator. This Google source file only carries category hierarchy.

Recommended module separation:

| Module | Purpose | Namespace |
| --- | --- | --- |
| GDSN | GDSN trade item ontology | `gdsn:` |
| GPC | GPC taxonomy and attribute/value taxonomy | `gpc:` |
| Google Product Taxonomy | Google product category taxonomy | `google:` |

Recommended linking strategy:

- Do not assert automatic equivalence between Google categories and GPC Bricks.
- If mappings are available later, generate a separate bridge file rather than
  embedding inferred alignments in either taxonomy ontology.
- Candidate bridge predicates could include `skos:exactMatch`,
  `skos:closeMatch`, or a project-specific mapping annotation, depending on
  mapping confidence.

## 9. Validation Rules

The TSV generator should validate:

1. Every data row matches `<id> - <path>`.
2. Every category ID is unique.
3. Every full path is unique.
4. Every non-root parent path exists as a source row.
5. Every generated parent CURIE resolves to a generated class row.
6. The parsed source version is emitted as an annotation.

Current file status:

| Check | Result |
| --- | --- |
| Valid data-row format | Pass |
| Unique IDs | Pass |
| Unique paths | Pass |
| Parent paths present | Pass |
| Maximum depth detected | 7 |
| Version detected | `2021-09-21` |

## 10. Example uml2semantics Command

After generating TSVs under `build/gdsn-tsv/google/`, build the ontology with:

```bash
uml2semantics \
  --classes build/gdsn-tsv/google/Classes.tsv \
  --attributes build/gdsn-tsv/google/Attributes.tsv \
  --datatypes build/gdsn-tsv/google/Datatypes.tsv \
  --enumerations build/gdsn-tsv/google/Enumerations.tsv \
  --enum-values build/gdsn-tsv/google/EnumerationNamedValues.tsv \
  --annotation-properties build/gdsn-tsv/google/AnnotationProperties.tsv \
  --annotations build/gdsn-tsv/google/Annotations.tsv \
  --output build/google-product-taxonomy.ttl \
  --ontology-iri urn:google:product-taxonomy: \
  --prefixes "google:urn:google:product-taxonomy:,gpc:urn:gs1:std:gpc:,gdsn:urn:gs1:std:gdsn:,xsd:http://www.w3.org/2001/XMLSchema#,dct:http://purl.org/dc/terms/" \
  --format turtle \
  --profile generic
```

## 11. Recommended Implementation Phases

1. Parse the source version from the header.
2. Parse every data row into `category_id`, `path`, `label`, and `level`.
3. Build a path-to-ID index.
4. Resolve each parent path to a parent category ID.
5. Determine leaf status from child counts.
6. Emit `Classes.tsv` with one synthetic root class and one class per category.
7. Emit empty attribute, datatype, enumeration, and enum-value TSVs.
8. Emit Google annotation properties and category annotations.
9. Run `uml2semantics-python` validation.
10. Load the resulting Google taxonomy ontology as a separate module.
