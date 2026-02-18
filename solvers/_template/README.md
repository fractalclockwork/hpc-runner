# Solver Template

This directory is a template for creating new solvers. **It is ignored by the loader** (prefix `_`).

## Quick Start

1. Copy this directory to create a new solver:
   ```bash
   cp -r solvers/_template solvers/my-solver
   ```

2. Edit `solver.yaml`:
   - Set `name` to match the directory (e.g. `my-solver`)
   - Set `entrypoint` to your run script
   - Set `allowed_systems` to compatible system names

3. Implement `run.sh` (or `run.py`):
   - The platform passes env vars from the System
   - Your script controls execution (local, SLURM, etc.)
   - Print metrics to stdout for extraction

4. Optional: Add `parser_config.yaml` to extract metrics from logs.

5. Add a job in `configs/jobs/` that references your solver.

See [docs/solver_template.md](../../docs/solver_template.md) for full specification.
