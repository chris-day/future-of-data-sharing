---
icon: lucide/network
---

# GS1 Future of Data Sharing

This documentation describes the local tooling for turning GS1 artefacts into
semantic TSV bundles, OWL ontologies, RDF instance data, and SHACL holon shapes.

The current pipeline covers:

- Product Holon architecture and companion technical evidence.
- GDSN UML JSON dumps to `uml2semantics-python` TSV.
- GPC taxonomy extraction as a separate ontology module.
- Google Product Taxonomy extraction as a separate ontology module.
- KATO GDSN XML instance conversion to RDF.
- GTIN/GPC/GDSN instance-aware SHACL holon generation.
- GraphDB named graph import guidance.

## Main Outputs

| Output | Path |
| --- | --- |
| GDSN TSV bundle | `build/gdsn-tsv/gdsn/` |
| GPC TSV bundle | `build/gdsn-tsv/gpc/` |
| Google Product Taxonomy TSV bundle | `build/gdsn-tsv/google/` |
| GDSN ontology | `build/gdsn.ttl` |
| GPC ontology | `build/gpc.ttl` |
| Google Product Taxonomy ontology | `build/google-product-taxonomy.ttl` |
| KATO instance graph | `build/KATO/kato-instances.ttl` |
| Holon SHACL shapes | `build/shacl/` |

## Start Here

1. Set up the Python environment in [Environment](getting-started.md).
2. Read the [Product Holon Architecture](architecture/index.md).
3. Generate TSV bundles in [TSV Generation](tsv/generation.md).
4. Build OWL/Turtle outputs in [uml2semantics](ontology/uml2semantics.md).
5. Load outputs into GraphDB using [Named Graphs](ontology/graphdb.md).
6. Generate instance-aware SHACL with [Holon Shapes](holon/shacl.md).

## Design Principle

GDSN, GPC, and Google Product Taxonomy are separate semantic modules. GDSN
models trade item data, while GPC and Google Product Taxonomy model external
classification hierarchies. Cross-links should be generated as bridge data, not
hard-coded into the source ontologies.
