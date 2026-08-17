---
icon: lucide/tags
---

# Google Product Taxonomy

The Google Product Taxonomy source file is:

```text
artefacts/google/taxonomy-with-ids.en-GB.txt
```

It is a hierarchy similar to GPC, not a UML class model.

Parsed source facts:

| Measure | Value |
| --- | ---: |
| Taxonomy version | `2021-09-21` |
| Total category rows | 5,595 |
| Unique category IDs | 5,595 |
| Missing parent paths | 0 |
| Maximum depth | 7 |
| Leaf categories | 4,719 |

Recommended ontology module:

| Setting | Value |
| --- | --- |
| Prefix | `google:` |
| Ontology IRI | `urn:google:product-taxonomy:` |
| Root class | `google:GoogleProductTaxonomyCategory` |
| Output | `build/google-product-taxonomy.ttl` |

Low-level example:

```text
google:543683
urn:google:product-taxonomy:543683
```

Label:

```text
Prescription Cat Food
```

Full path:

```text
Animals & Pet Supplies > Pet Supplies > Cat Supplies > Cat Food > Prescription Cat Food
```

For the detailed semantic mapping notes, see
[Google Product Taxonomy Mapping](../reference/google-product-taxonomy.md).
