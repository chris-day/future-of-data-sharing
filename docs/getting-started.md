---
icon: lucide/terminal
---

# Environment

Use the repository virtual environment for all Python work:

```bash
.venv/bin/python --version
.venv/bin/python -m pip check
```

Expected project entry points:

```text
.venv/bin/gdsn-json-to-tsv
.venv/bin/google-taxonomy-to-tsv
.venv/bin/gdsn-xml-to-rdf
.venv/bin/gs1-gdsn-holon
.venv/bin/zensical
```

Install or refresh the editable package:

```bash
.venv/bin/python -m pip install -e .
```

Run the focused health checks:

```bash
.venv/bin/python -m unittest tests.test_google_taxonomy
.venv/bin/python -m compileall -q src tests
```

Preview this documentation with Zensical:

```bash
.venv/bin/zensical serve
```

Build the static site:

```bash
.venv/bin/zensical build
```
