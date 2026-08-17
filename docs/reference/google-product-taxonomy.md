---
icon: lucide/book-open
---

# Google Product Taxonomy Mapping Notes

The full semantic source document is maintained at:

```text
Google_Product_Taxonomy.md
```

Key choices:

- Google Product Taxonomy is a separate module with prefix `google:`.
- Ontology IRI is `urn:google:product-taxonomy:`.
- Category IDs become class CURIEs, for example `google:543683`.
- Category hierarchy is encoded as class parent relationships.
- No attributes, datatypes, enumerations, or enum values are inferred from the
  source file.

Build command:

```bash
.venv/bin/google-taxonomy-to-tsv \
  --input-file artefacts/google/taxonomy-with-ids.en-GB.txt \
  --output-dir build/gdsn-tsv
```

Then run `uml2semantics` as documented in
[uml2semantics](../ontology/uml2semantics.md).
