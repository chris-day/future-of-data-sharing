---
icon: lucide/git-branch
---

# Mapping Decisions

The detailed mapping investigation is maintained at:

```text
artefacts/GDSN-TSV-Mapping-v0.1.0.md
```

Important decisions:

- `gdsn:` namespace base is `urn:gs1:std:gdsn:`.
- `gpc:` namespace base is `urn:gs1:std:gpc:`.
- GPC is a separate ontology output.
- Google Product Taxonomy is a separate ontology output.
- Structured GDSN type-3 records with owned attributes are emitted as value
  classes, not datatypes.
- Malformed multiplicities are left blank and reported in diagnostics.
- AVPs and extended attributes are generated into synthetic containers.
- GDSN extension modules are connected through the synthetic
  `gdsn:extensionModule` object property.
