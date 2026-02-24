# Solver Directory Template

Each solver is a self-contained directory with its own config, parser config, run script, and supporting files. This document defines the canonical structure and conventions.

---

## Directory Structure

```
configs/solvers/<solver-name>/   # solvers directory is inside configs
├── solver.yaml           # Required: metadata, entrypoint, allowed systems
├── parser_config.yaml    # Optional: regex patterns for metric extraction
├── run.sh                # Required (or run.py): entrypoint script
├── build.sh              # Optional: build/compile step
├── inputs/               # Optional: input files, test cases
│   └── ...
└── ...                   # Any other solver-specific files
```

**Key principle:** All paths in `solver.yaml` and `parser_config.yaml` are relative to the solver directory. The loader resolves them from the solver folder.

---

## solver.yaml Specification

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Solver identifier (should match directory name) |
| `entrypoint` | Yes | Script to run (`run.sh`, `run.py`, etc.) |
| `allowed_systems` | Yes | List of system names this solver can run on |
| `version` | No | Default `0.0.0` |
| `parser_config` | No | Path to parser YAML (e.g. `parser_config.yaml`) |
| `metrics` | No | List of `{name, unit, min, max, required}` for validation |
| `log_names` | No | Expected log file names |
| `cwd` | No | Default `true` = use solver dir as cwd |

### parser_config.yaml Specification

| Field | Description |
|-------|-------------|
| `patterns` | List of extraction rules |

Each pattern:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Metric name |
| `regex` | string | Regex with one capture group |
| `type` | string | `str`, `float`, or `int` |

---

## Example: Minimal Solver (echo-style)

**configs/solvers/echo-solver/solver.yaml**

```yaml
name: echo-solver
version: "1.0.0"
entrypoint: run.sh
allowed_systems: [dev-system, hpc-cluster-01]
metrics: []
log_names: []
```

**configs/solvers/echo-solver/run.sh**

```bash
#!/usr/bin/env bash
echo "Solver started"
echo "Solver finished successfully"
```

---

## Example: Solver with Metrics (python-solver style)

**configs/solvers/python-solver/solver.yaml**

```yaml
name: python-solver
version: "1.0.0"
entrypoint: run.py
allowed_systems: [dev-system]
parser_config: parser_config.yaml
metrics:
  - name: mlups
    unit: MLUPS
    min: 0
    required: true
  - name: runtime_seconds
    unit: s
    required: true
log_names: [stdout]
```

**configs/solvers/python-solver/parser_config.yaml**

```yaml
patterns:
  - name: mlups
    regex: 'MLUPS:\s*([\d.e+-]+)'
    type: float
  - name: runtime_seconds
    regex: 'runtime_seconds:\s*([\d.]+)'
    type: float
  - name: status
    regex: 'status:\s*(\w+)'
    type: str
```

**configs/solvers/python-solver/run.py**

```python
#!/usr/bin/env python3
import sys
print("MLUPS: 2.1e6")
print("runtime_seconds: 38.5")
print("status: success")
sys.exit(0)
```

---

## Conventions

1. **Naming:** Solver directory name should match `name` in `solver.yaml`.
2. **Path resolution:** Paths in `solver.yaml` (e.g. `parser_config`, `entrypoint`) are relative to the solver directory.
3. **Run script:** Must exist at `entrypoint` path. Executed as black-box; platform passes env vars; script controls execution (local, SLURM, etc.).
4. **Template directory:** `configs/solvers/_template/` is ignored by the loader. Copy it to create new solvers.

---

## Creating a New Solver

1. Copy `configs/solvers/_template/` to `configs/solvers/<your-solver-name>/` (both under configs)
2. Edit `solver.yaml`: set `name`, `entrypoint`, `allowed_systems`
3. Implement the run script
4. Optionally add `parser_config.yaml` and define metrics
5. Add a job in `configs/jobs/` that references your solver
