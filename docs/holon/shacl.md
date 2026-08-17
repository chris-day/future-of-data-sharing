---
icon: lucide/hexagon
---

# SHACL Holon Shapes

Generate a GPC Brick SHACL shape:

```bash
./gs1-gdsn-holon 10000030 \
  --gpc build/gpc.ttl \
  --output build/shacl/gpc-brick-10000030.shacl.ttl
```

Generate a GTIN holon using `product-gpc-map.csv`:

```bash
./gs1-gdsn-holon 09506000134352 \
  --input-kind gtin \
  --gtin-map product-gpc-map.csv \
  --gtin-column gtin \
  --brick-column brickCode \
  --output build/shacl/gtin-09506000134352.shacl.ttl
```

Generate an instance-aware KATO holon:

```bash
./gs1-gdsn-holon 25196100024882 \
  --input-kind gtin \
  --instance-data build/KATO/kato-instances.ttl \
  --instance-base-iri urn:gs1:sample:kato: \
  --gpc build/gpc.ttl \
  --gdsn build/gdsn.ttl \
  --include-gdsn \
  --include-instance-objects \
  --output build/shacl/kato-25196100024882-holon.shacl.ttl \
  --report-json build/shacl/kato-25196100024882-holon.report.json
```

The default `--instance-max-depth 5` covers the implemented KATO extension
module paths and structured type-3 value nodes.

When `--output` is omitted, the SHACL Turtle is written to stdout.
