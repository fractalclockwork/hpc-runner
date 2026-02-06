# tests/test_runner.py
import tempfile
import os
import yaml
from hpc_regression.runner import run_from_config

def test_run_minimal(tmp_path, capsys):
    cfg = {
        "runners": [
            {"name": "echo-test", "command": ["echo", "hi-from-test"]},
            {"name": "py-test", "command": ["python3", "-c", "print('py-ok')"]},
        ]
    }
    cfg_path = tmp_path / "runners.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")

    results = run_from_config(str(cfg_path))
    # two runners executed
    assert len(results) == 2
    assert any("hi-from-test" in (r["stdout"] or "") for r in results)
    assert any("py-ok" in (r["stdout"] or "") for r in results)
    # return codes should be zero
    assert all(r["returncode"] == 0 for r in results)

