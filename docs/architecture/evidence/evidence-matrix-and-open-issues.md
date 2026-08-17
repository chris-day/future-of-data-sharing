---
icon: lucide/clipboard-list
source: artefacts/GS1_Product_Holon_Architecture_Technical_Evidence_and_Reference_Implementation_v1.3.0.md
---

# Evidence Matrix and Open Issues
## Part IX — Evidence matrix and unresolved issues

## 31. Evidence matrix

| Architectural assertion | Evidence basis | Strength |
|---|---|---|
| GPC supports Brick-scoped controlled facets | Direct inspection and counts from `gpc.ttl`; generated shapes | Strong observed evidence. |
| GDSN provides rich deep product semantics and code lists | Direct inspection and counts from `gdsn.ttl` | Strong observed evidence. |
| A bounded product graph is preferable to exposing the full models | Size/scope analysis and five worked Product Holons; four are backed by supplied generated Brick shapes | Strong architectural inference. |
| Brick-scoped SHACL can be generated automatically | Generator design and `gs1-gdsn-holon` implementation | Demonstrated. |
| Shapes distinguish conforming and broken records | Reported `pySHACL` runs | Demonstrated for representative cases. |
| The current selected GDSN shape is constant across four Bricks | Direct diff reported in source baseline | Strong observed evidence. |
| That selected shape is incomplete for category detail | Cheese-relevant GDSN terms absent from shape | Strong observed evidence. |
| Lexical matching yields useful but sparse candidates | 28,101-term LOOM run and 237 pairs | Demonstrated. |
| GDSN-to-Web Vocabulary overlap exceeds GPC-to-Web Vocabulary overlap | Mapping-pair distribution | Demonstrated lexical evidence. |
| SSSOM is suitable for governing mappings | SSSOM model and mapping-literature review | Strong standards-based design choice. |
| Direct equivalence cannot perform conditional reshaping | OWL/DL expressiveness analysis | Strong formal basis. |
| Deterministic engines should execute final rules | Reported structured-decomposition ablation and architecture tests | Strong supporting evidence. |
| Digital Link can resolve multiple representations | Resolver-standard mechanisms | Standards-backed. |
| Product Holon is a GS1-defined term | No supporting evidence found | Rejected. |
| An HTML document can expose addressable JSON-LD script blocks by `id` | JSON-LD 1.1 Recommendation | Strong standards evidence |
| W3C VC verification establishes issuer authorship, integrity and status but not claim truth | VC Data Model v2.0 Recommendation | Strong standards evidence |
| A VC can integrity-bind external Product Holon, shape, validation and mapping resources | VC Data Model v2.0 `relatedResource` and digest requirements | Strong standards evidence |
| The supplied GDSN notification provides sender, content-owner, information-provider, brand-owner, GTIN, Brick, market and time evidence | `CatalogueItemNotification_ADD.xml` | Observed. |
| The corresponding RDF instance confirms a GDSN/GPC-aligned graph with controlled code IRIs and linked classification, party, market, date and description nodes | `kato-instances(1).ttl`, checked against `gdsn(1).ttl` and `gpc(1).ttl` | Observed. |
| A GS1 Product Statement Credential profile and issuer-authority trust model already exist as approved GS1 standards | Not established | Proposed. |
| A decentralised autonomous product node is required by GS1 standards | No supporting evidence found | Rejected. |

---

## 32. Validation and test inventory

| Test | Input | Expected result | Reported status |
|---|---|---|---|
| SHACL parse | Generated Cheese shape | Parses | Passed. |
| SHACL conforming instance | Valid Cheese values and nested records | `Conforms: True` | Passed. |
| SHACL invalid firmness | `SQUISHY` | `sh:InConstraintComponent` | Passed. |
| SHACL invalid nutrient code | `PROTEIN_XYZ` | `sh:InConstraintComponent` | Passed. |
| SHACL missing containment | Allergen without level | `sh:MinCountConstraintComponent` | Passed. |
| Shape generalisation | Cheese, Smartphones, Beer | Parse and conforming check | Passed. |
| Cross-Brick GDSN diff | Four supplied shape files | Identical selected GDSN blocks | Confirmed in source report. |
| Route 3 generic rule | Real Cheese Brick facts | Four `PropertyValue` nodes | Passed. |
| Representative nutrient projection | Gouda holon | Four schema.org nutrient facts | Passed. |
| Residual nutrient projection | Calcium | One generic property | Passed. |
| LOOM count reconciliation | 474 records | 237 unique pairs and expected split | Passed. |
| Web Vocabulary allergen range | v1.16 source slice | `rdf:langString` | Observed. |
| Manchester parsing | `gs1-holon-bridge.omn` | Formal parse | Not performed in reported session. |
| Catalogue-scale performance | Large product set | Defined service targets | Not performed. |
| Security and access-control tests | Partner/public views | No unauthorised disclosure | Not performed. |

---

## 33. Unresolved technical questions

### 33.1 Namespace and persistence

The generated `gdsn:` and `gpc:` identifiers require an authoritative namespace and persistence policy. Source-ID-based CURIEs are traceable but not self-describing. The architecture needs rules for stability across source releases, deprecation and redirects.

### 33.2 Complete shape composition

The evidence does not establish whether every class referenced by `sh:class` in the selected GDSN shape also has a corresponding NodeShape that validates its internal properties. A production shape package shall make this explicit.

### 33.3 Product construction graph convention

The selected GDSN shape flattens properties from several source domains onto a TradeItem-targeted validation shape. The actual Product Holon construction convention must state whether the instance graph is similarly flattened or preserves the full module hierarchy and uses composed shapes.

### 33.4 Mapping approval body

The evidence defines a mapping process but not the GS1 group authorised to approve mappings. Roles, quorum, domain review and release authority remain unresolved.

### 33.5 Web Vocabulary coverage

The completed lexical run establishes absence of lexical candidates for many tested facets, not proof that no semantically suitable term exists under a dissimilar label. Structural and domain-informed matching should complement lexical review.

The baseline contains an internal count discrepancy: one passage describes nineteen residual facets out of twenty, while the reproduced per-Brick lists name fewer facets. The mapping records should be re-counted directly by Brick before any aggregate coverage percentage is published.

### 33.6 Rule-engine portability

DL-safe SWRL support and behaviour vary across reasoners. A production profile shall name supported rule syntax, built-ins, safety restrictions, materialisation behaviour and conformance tests.

### 33.7 Downstream treatment of generic properties

The evidence notes that `schema:PropertyValue` may receive less weight from search engines, feeds or LLM agents than first-class terms. Empirical downstream tests are required.

### 33.8 Resolver security

Media-type and link selection do not replace authorisation. The evidence contains no production access-control design for partner-only Product Holon views.

### 33.9 Performance

No catalogue-scale benchmark exists for ontology generation, SHACL validation, reasoner execution, projection or resolver latency.

### 33.10 Licence

The licence for the architecture, source-derived artefacts, mapping sets and examples remains unresolved.

### 33.11 Verifiable publication profile namespace

The persistent namespace, JSON-LD contexts, HTML profile URI and script identifiers for the HTML Semantic Proof require governance.

### 33.12 Issuer authority and trust framework

The sources do not define how a verifier proves that a signing organisation is authorised for a GTIN, claim type, market and effective period. A registry, delegation and authority-evidence model is required.

### 33.13 Cryptographic suite and key policy

The approved securing mechanisms, cryptosuites, verification-method format, key custody, rotation, compromise and historical verification policies remain to be selected.

### 33.14 Credential granularity and lifecycle

It remains to be decided whether credentials are issued per Product Holon release, assertion set, claim, market, batch or serial, and how renewal, expiry, supersession, revocation and withdrawal interact with product-data updates.

### 33.15 Embedded versus linked credential

The canonical credential should be served as `application/vc`. Whether the HTML also embeds a synchronised copy requires a policy that prevents divergence and preserves exact verification semantics.

### 33.16 Credential status infrastructure

The status-list issuer, hosting, privacy, availability and operational service levels are not established.

### 33.17 Canonicalisation and resource-digest policy

The architecture must define whether digests bind exact bytes, canonical RDF datasets or both, and how content negotiation, language variants and remote JSON-LD contexts affect repeatable verification.

### 33.18 FoDS workstream ownership

The proposed 8.3.b → 8.4.a → 8.4.b hand-off needs confirmation against the authoritative 8.4.a plan and project governance.

---
