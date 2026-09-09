# GDSN to GS1 Web Vocabulary name matching

Version: 0.1.0

## Inputs and method

Compared `build/gdsn.ttl` (207,400 triples) with
`artefacts/WebVoc/gs1Voc.ttl` (18,749 triples; declared vocabulary version 1.18).
Both files were parsed using RDFLib in the repository `.venv`.

The comparison uses the local part of each **subject IRI** in
`https://ref.gs1.org/voc/` against `rdfs:label` strings on GDSN IRI subjects in
`urn:gs1:std:gdsn:`. It does not use the Web Vocabulary labels. The namespace
IRI itself, external vocabulary terms, blank nodes, and IRIs appearing only
as objects are excluded from the Web Vocabulary candidate set.

Each pair is assigned its strongest matching method:

1. Exact: local name equals the GDSN label, including case.
2. Case-insensitive: strings match after case folding.
3. Normalized: strings match after case folding and removing everything
   except ASCII letters and digits, including spaces and underscores.

No fuzzy matching, inference, imported ontology retrieval, or equivalence
axioms are used. All matching GDSN resources are retained, including classes,
properties, datatypes, and code-list individuals. Name matches are candidates
for review, not assertions of semantic equivalence.

## Results

| Measure | Count |
| --- | ---: |
| Web Vocabulary terms examined | 2,539 |
| Labelled GDSN terms examined | 21,391 |
| Web Vocabulary terms with any name match | 191 |
| Distinct matching GDSN resources | 291 |
| Total candidate pairs | 298 |
| Exact pairs | 187 |
| Additional case-insensitive pairs | 92 |
| Additional normalized pairs | 19 |
| Web Vocabulary terms with multiple GDSN candidates | 68 |
| Web Vocabulary terms without a name match | 2,348 |
| Labelled GDSN terms without a name match | 21,100 |

Counts of terms use distinct IRIs, not distinct labels or match rows. The
GDSN denominator includes only labelled GDSN IRI subjects, since these are
the resources searched; the four unlabelled GDSN subjects are excluded.

| Match category | Candidate pairs | Distinct Web Vocabulary terms | Distinct GDSN terms |
| --- | ---: | ---: | ---: |
| Exact | 187 | 156 | 187 |
| Case-insensitive (excluding exact pairs) | 92 | 76 | 91 |
| Normalized (excluding the above pairs) | 19 | 14 | 19 |
| All name matches | 298 | 191 | 291 |
| Structured object to language-tagged literal (subset of exact) | 29 | 29 | 29 |

Distinct term counts overlap between methods and must not be added together.
Of the 187 exact pairs, 111 also have the same broad RDF entity kind.
Across all matching methods, there are 58 datatype-property pairs, 48
object-property pairs, and 5 class pairs. Matching kind alone does not prove
compatible domains, ranges, or value structures.

## Examples

Here `gs1:` means `https://ref.gs1.org/voc/` and `gdsn:` means
`urn:gs1:std:gdsn:`. All examples below are exact name matches.

| Web Vocabulary IRI | GDSN resource(s) | Observation |
| --- | --- | --- |
| `gs1:gtin` | `gdsn:a-1292425203`, `gdsn:a5339`, `gdsn:a5681`, `gdsn:a6979` | Four datatype properties; select by owner/domain and instance path. |
| `gs1:brandName` | `gdsn:a308904173` | Datatype properties, but Web Vocabulary range is `rdf:langString` and GDSN uses a constrained string datatype. |
| `gs1:grossWeight` | `gdsn:a-387099093`, `gdsn:a135085091`, `gdsn:a662369953` | Object properties; GDSN range `gdsn:c1490` needs a value/unit projection to `gs1:QuantitativeValue`. |
| `gs1:netContent` | `gdsn:a-930082660` | Same quantitative-value modelling issue as gross weight. |
| `gs1:ingredientStatement` | `gdsn:a812659001` | GDSN object property versus Web Vocabulary datatype property with range `rdf:langString`. |
| `gs1:targetMarket` | `gdsn:assoc_-2110977878_919_2`, `gdsn:assoc_1406_919_2`, `gdsn:assoc_863999331_919_6` | Object properties with different GDSN owners; map the relevant instance path. |
| `gs1:Country` | `gdsn:c1287`, `gdsn:c1673496745` | Class matches are ambiguous. |
| `gs1:RegulatoryInformation` | `gdsn:c-1049209724` | Class-to-class candidate. |

Other exact class-to-class pairs are `gs1:CompulsoryAdditionalInformation`
with `gdsn:c1650738053` and `gs1:RegulatoryIdentifier` with
`gdsn:c2147348370`.

## Structured objects to language-tagged literals

The search explicitly includes object-to-literal transformations. The main
table flags these with `object_to_langstring`; the
[structured language match table](gdsn-matches/structured-language-matches.tsv)
provides the range class, value datatype, value path, language qualifier paths,
other qualifiers, and a structure-confirmation flag for each candidate.

There are **29 exact-name pairs covering 29 Web Vocabulary properties,
29 distinct GDSN properties, and eight GDSN structured text range classes**.
The range classes describe the matched properties and are counted separately;
they are not additional matched terms in this category.
These are a subset of the original 298
candidate pairs, not additional matches.

Detection requires a Web Vocabulary `owl:DatatypeProperty` with declared
`rdfs:range rdf:langString` and a matching GDSN `owl:ObjectProperty`.
For each GDSN range, confirmation checks `owl:Class`, `gdsn:sourceType "3"`,
and `gdsn:valueDatatype xsd:string`. Qualifiers are discovered using
`rdfs:domain` and `owl:onProperty` on superclass restrictions, including named
ancestors. A qualifier labelled `languageCode` identifies the language path.
All 29 candidates in these files pass the structure and language checks.

| GDSN range label | Matching Web Vocabulary IRI local names |
| --- | --- |
| Description35 | `functionalName` |
| Description70 | `cheeseMaturationPeriodDescription`, `clothingCut`, `collarType`, `consumerSafetyInformation`, `dietTypeDescription`, `ingredientName`, `responsibility`, `seasonName`, `styleDescription` |
| Description80 | `colourDescription`, `descriptiveSize` |
| Description500 | `awardPrizeDescription`, `countryOfOriginStatement`, `numberOfServingsRangeDescription`, `provenanceStatement`, `servingSizeDescription`, `variantDescription` |
| Description1000 | `allergenStatement`, `preparationConsumptionPrecautions`, `servingSuggestion` |
| Description5000 | `consumerPackageDisclaimer`, `consumerRecyclingInstructions`, `consumerStorageInstructions`, `consumerUsageInstructions`, `preparationInstructions`, `warningCopyDescription` |
| FormattedDescription500 | `regulatedProductName` |
| FormattedDescription5000 | `ingredientStatement` |

For example, the converter's `OntologyIndex.add_qualified_value` in
`src/gdsn_tsv_transformer/xml_to_rdf.py` can produce this illustrative source
structure when the XML contains a language code:

```turtle
@prefix gdsn: <urn:gs1:std:gdsn:> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<urn:example:ingredient-module> gdsn:a812659001 [
    a gdsn:c1481031847 ;
    rdf:value "Milk, salt"@en ;
    gdsn:a1898337069 "en"
] .
```

The value path is `gdsn:a812659001/rdf:value`. The separate language-code
path is `gdsn:a812659001/gdsn:a1898337069`. A reviewed product projection
can retain the tagged literal directly:

```turtle
@prefix gs1: <https://ref.gs1.org/voc/> .

<urn:example:product> gs1:ingredientStatement "Milk, salt"@en .
```

These paths start at the GDSN owner of the attribute. A product projection
must additionally traverse from the trade item to that owner; it cannot
assume the attribute is directly on the trade item.

The use of `rdf:value` is verified against the repository converter, rather
than inferred from the class label. Preserve an existing language tag. If
the value is untagged, constructing a language-tagged literal requires a
present, valid language code. Do not invent a default language; flag missing,
invalid, or conflicting language information for review.

For `ingredientStatement`, the other qualifiers are `formattingPattern`
(`gdsn:a-430496472`), `codeListVersion` (`gdsn:a1011214172`), and
`sequenceNumber` (`gdsn:a1253275657`). A literal-only projection does not
preserve these; retain the source structure and apply an explicit formatting
and ordering policy if these qualifiers occur. Confirmation here establishes
the structural conversion candidate, not full semantic equivalence.

## Implications for a semantic bridge

- Repeated labels require domain and traversal context. Do not choose the
  first matching GDSN IRI: `gtin`, for example, has four exact property matches.
- There are 41 candidate pairs where the Web Vocabulary term is a datatype
  property and the GDSN resource is an object property. Structured descriptions,
  amounts, and code-list references need explicit value extraction or conversion.
- Normalization produces false candidates: `brandOwner` also matches the
  code label `BRAND_OWNER`; `targetMarket` also matches the annotation property
  labelled `Target market`. Entity kinds must be checked before mapping.
- Name matching misses semantic candidates. GDSN `height` does not match a
  Web Vocabulary `height` term: this file defines `gs1:inPackageHeight` and
  `gs1:outOfPackageHeight`. Packaging context is required to select between them.
- A matching property name and kind still need range and definition review.
  Measurement nodes need their values and units preserved; language-bearing
  structures need their language preserved when projected to literals.

Start bridge review with exact property-to-property and class-to-class pairs,
then inspect definitions, domains, ranges, GDSN paths, and representative KATO
instances. This investigation does not justify automatically emitting
`owl:equivalentProperty` or `owl:equivalentClass`.

## Reproduction and outputs

From the repository root:

```bash
.venv/bin/python artefacts/WebVoc/match_gdsn_labels.py \
  --gdsn build/gdsn.ttl \
  --webvoc artefacts/WebVoc/gs1Voc.ttl \
  --output-dir artefacts/WebVoc/gdsn-matches
```

- [Complete candidate table](gdsn-matches/matches.tsv): full IRIs, GDSN labels,
  method, candidate counts, RDF kinds, declared types, domains, ranges, comments,
  and a same-kind flag. Multiple RDF values are separated by ` | `.
- [Unmatched Web Vocabulary terms](gdsn-matches/unmatched-webvoc.tsv).
- [Structured object to language literal candidates](gdsn-matches/structured-language-matches.tsv).
- [Machine-readable counts](gdsn-matches/summary.json).
- [Reproducible comparison script](match_gdsn_labels.py).

The comparison completed successfully against both Turtle inputs. Report
counts were checked against the exported rows. This validates the name
comparison, not the semantic correctness of a future mapping.
Focused checks also verified inherited language qualifiers, cycle handling,
value path construction, and rejection of a numeric structured value as text.
All 29 exported language candidates were checked for exact name matches,
confirmed structured text, and a discovered language qualifier.
