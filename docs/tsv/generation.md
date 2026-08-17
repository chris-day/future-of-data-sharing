---
icon: lucide/table
---

# TSV Generation

The TSV bundles are generated for `uml2semantics-python`. Each module writes
the standard files:

```text
Classes.tsv
Attributes.tsv
Datatypes.tsv
Enumerations.tsv
EnumerationNamedValues.tsv
AnnotationProperties.tsv
Annotations.tsv
diagnostics.tsv
```

## GDSN and GPC

Generate GDSN and GPC TSVs together:

```bash
.venv/bin/gdsn-json-to-tsv \
  --input-dir artefacts/GDSN_Current_v3.1.35 \
  --output-dir build/gdsn-tsv
```

Generate only GDSN:

```bash
.venv/bin/gdsn-json-to-tsv \
  --input-dir artefacts/GDSN_Current_v3.1.35 \
  --output-dir build/gdsn-tsv \
  --skip-gpc
```

Output directories:

```text
build/gdsn-tsv/gdsn/
build/gdsn-tsv/gpc/
```

## Google Product Taxonomy

Generate Google Product Taxonomy TSVs:

```bash
.venv/bin/google-taxonomy-to-tsv \
  --input-file artefacts/google/taxonomy-with-ids.en-GB.txt \
  --output-dir build/gdsn-tsv
```

Output directory:

```text
build/gdsn-tsv/google/
```

## Mapping Choices

GDSN type-2 records become classes. Simple type-3 records become datatypes.
Structured type-3 records with owned attributes, such as `Measurement` and
`Description35`, become value classes with `gdsn:valueDatatype` annotations.

GPC and Google Product Taxonomy are taxonomy modules. Categories are emitted as
classes with hierarchy represented through `ParentNames` and, after ontology
build, `rdfs:subClassOf`.

## Diagnostics

Diagnostics are written to each module's `diagnostics.tsv`. Malformed
multiplicities are left blank in `Attributes.tsv` and reported as diagnostics.
