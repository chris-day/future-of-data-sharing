---
icon: lucide/boxes
---

# uml2semantics

Use `uml2semantics-python` to build Turtle ontologies from the generated TSVs.

## GDSN

```bash
/var/software/gitrepos/uml2semantics-python/.venv/bin/uml2semantics \
  --classes build/gdsn-tsv/gdsn/Classes.tsv \
  --attributes build/gdsn-tsv/gdsn/Attributes.tsv \
  --datatypes build/gdsn-tsv/gdsn/Datatypes.tsv \
  --enumerations build/gdsn-tsv/gdsn/Enumerations.tsv \
  --enum-values build/gdsn-tsv/gdsn/EnumerationNamedValues.tsv \
  --annotation-properties build/gdsn-tsv/gdsn/AnnotationProperties.tsv \
  --annotations build/gdsn-tsv/gdsn/Annotations.tsv \
  --output build/gdsn.ttl \
  --ontology-iri urn:gs1:std:gdsn: \
  --prefixes "gpc:urn:gs1:std:gpc:,gdsn:urn:gs1:std:gdsn:,xsd:http://www.w3.org/2001/XMLSchema#,dct:http://purl.org/dc/terms/,iso3166:urn:iso:std:iso:3166" \
  --format turtle \
  --profile generic
```

## GPC

```bash
/var/software/gitrepos/uml2semantics-python/.venv/bin/uml2semantics \
  --classes build/gdsn-tsv/gpc/Classes.tsv \
  --attributes build/gdsn-tsv/gpc/Attributes.tsv \
  --datatypes build/gdsn-tsv/gpc/Datatypes.tsv \
  --enumerations build/gdsn-tsv/gpc/Enumerations.tsv \
  --enum-values build/gdsn-tsv/gpc/EnumerationNamedValues.tsv \
  --annotation-properties build/gdsn-tsv/gpc/AnnotationProperties.tsv \
  --annotations build/gdsn-tsv/gpc/Annotations.tsv \
  --output build/gpc.ttl \
  --ontology-iri urn:gs1:std:gpc: \
  --prefixes "gpc:urn:gs1:std:gpc:,gdsn:urn:gs1:std:gdsn:,xsd:http://www.w3.org/2001/XMLSchema#,dct:http://purl.org/dc/terms/,iso3166:urn:iso:std:iso:3166" \
  --format turtle \
  --profile generic
```

## Google Product Taxonomy

```bash
/var/software/gitrepos/uml2semantics-python/.venv/bin/uml2semantics \
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
