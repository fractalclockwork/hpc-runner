```
# DOW-1-26  
Automated HPC Test Harness

This wiki contains all pertinent information for the Capstone project.

**[Project Wiki](https://github.berkeley.edu/Chem-283/DOW-1-26/wiki)**

---

# Quick Start Guide: Using the Makefile

This project uses a uv‑native Makefile to ensure reproducible, frictionless workflows across all teammates.  
Use these targets instead of manually activating virtual environments or running pip.

---

## 1. If you pulled an earlier version of the project

Start clean. Old lockfiles, stale venvs, and cached artifacts can break the workspace.

Run:

```
make purge
```

This removes:

- all `.venv` directories (recursively)
- all `uv.lock` files
- all `__pycache__`, `.pytest_cache`, `*.egg-info`
- all build artifacts
- uv global caches

Use this whenever the project structure changes or after pulling older commits.

---

## 2. Sync the workspace environment

After purging, rebuild the environment:

```
make sync
```

This:

- creates a workspace-level `.venv`
- installs all workspace members in editable mode
- installs dev dependencies
- ensures CLI entrypoints (`hpc-runner`, Flask API) are available

---

## 3. Run the test suite

To run all tests for the `hpc-runner` project:

```
make test
```

Verbose mode:

```
make testv
```

---

## 4. Run the CLI test runner

To execute the regression test harness with the default config:

```
make runner
```

This runs:

- `prototypes/hpc-runner/configs/runners.yaml`
- the full regression pipeline
- structured JSON output

---

## 5. Run the REST API

To launch the Flask API with auto‑reload:

```
make api
```

This starts a dev server at:

```
http://localhost:5000/
```

Endpoints:

- `/` — loads the UI  
- `/api/run_tests` — executes the runner and returns JSON  

---

## 6. Typical workflow

```
git pull
make purge        # only needed after major changes or old commits
make sync
make test         # optional
make runner       # run the CLI
make api          # run the web UI
```

---

## 7. Summary of Makefile targets

| Target       | Purpose                                           |
|--------------|---------------------------------------------------|
| `purge`      | Remove all venvs, caches, lockfiles, build junk   |
| `sync`       | Rebuild the uv workspace environment              |
| `test`       | Run the hpc-runner test suite                     |
| `runner`     | Execute the CLI test harness                      |
| `api`        | Launch the Flask web interface                    |

---
```

