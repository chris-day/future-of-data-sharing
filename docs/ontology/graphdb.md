---
icon: lucide/database
---

# GraphDB Named Graphs

The generated Turtle files are ordinary RDF graphs. They do not contain named
graph wrappers. Assign named graphs during GraphDB import.

Recommended import sequence:

1. `build/gpc.ttl`
2. `build/gdsn.ttl`
3. `build/google-product-taxonomy.ttl`
4. `build/KATO/kato-instances.ttl`
5. generated SHACL shapes, if validating shapes in GraphDB

Recommended named graphs:

| File | Named graph |
| --- | --- |
| `build/gpc.ttl` | `urn:gs1:std:gpc:` |
| `build/gdsn.ttl` | `urn:gs1:std:gdsn:` |
| `build/google-product-taxonomy.ttl` | `urn:google:product-taxonomy:` |
| `build/KATO/kato-instances.ttl` | `urn:gs1:sample:kato:ontology` |
| generated holon SHACL shapes | `urn:gs1:shapes:gpc:` |

KATO product instance IRIs:

```text
urn:gs1:sample:kato:gtin/25196100024882
urn:gs1:sample:kato:gtin/25196100024899
```

The ontology imports in `kato-instances.ttl` are RDF triples. They are not
GraphDB named graph declarations.
