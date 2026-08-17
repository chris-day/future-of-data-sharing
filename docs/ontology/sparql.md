---
icon: lucide/search
---

# SPARQL Examples

## Google Product Taxonomy

Query Google taxonomy categories from the named graph
`urn:google:product-taxonomy:`:

```sparql
PREFIX google: <urn:google:product-taxonomy:>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?category ?categoryId ?level ?label ?path ?parent ?parentLabel ?isLeaf
WHERE {
  GRAPH <urn:google:product-taxonomy:> {
    ?category rdfs:subClassOf* google:GoogleProductTaxonomyCategory ;
              rdfs:label ?label ;
              google:categoryId ?categoryId ;
              google:level ?level ;
              google:path ?path ;
              google:isLeaf ?isLeaf .

    OPTIONAL {
      ?category rdfs:subClassOf ?parent .
      ?parent rdfs:label ?parentLabel .
      FILTER(?parent != google:GoogleProductTaxonomyCategory)
    }
  }
}
ORDER BY xsd:integer(?level) ?path
LIMIT 100
```

## KATO GTIN Facts

```sparql
PREFIX gdsn: <urn:gs1:std:gdsn:>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?property ?propertyLabel ?value
WHERE {
  VALUES ?root {
    <urn:gs1:sample:kato:gtin/25196100024882>
    <urn:gs1:sample:kato:gtin/25196100024899>
  }

  ?root (!<urn:gs1:never:stop>)* ?subject .
  ?subject ?property ?value .

  OPTIONAL { ?property rdfs:label ?propertyLabel }
}
ORDER BY ?subject ?property ?value
LIMIT 500
```
