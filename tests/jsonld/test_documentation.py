"""Execute the user guide's examples, using isolated output directories."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
GUIDE = (ROOT / "docs/ontology/jsonld.md").read_text(encoding="utf-8")
BASH_EXAMPLES = re.findall(r"```bash\n(# example: ([^\n]+)\n.*?)```", GUIDE, re.S)
PYTHON_EXAMPLES = re.findall(r"```python\n(.*?)```", GUIDE, re.S)


@pytest.mark.parametrize("script,name", BASH_EXAMPLES, ids=[example[1] for example in BASH_EXAMPLES])
def test_documented_cli_example(script, name, tmp_path):
    shutil.copytree(ROOT / "docs/ontology/examples", tmp_path / "docs/ontology/examples")
    env = dict(os.environ, PATH=str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"])
    result = subprocess.run(["bash", "-euo", "pipefail", "-c", script], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, f"{name}: {result.stderr}"


@pytest.mark.parametrize("script", PYTHON_EXAMPLES)
def test_documented_api_example(script):
    exec(compile(script, "jsonld.md", "exec"), {})
