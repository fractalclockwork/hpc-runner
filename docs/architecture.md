# System Architecture

## 1. High-Level Overview

- **Purpose**: Execution-agnostic harness for running solver jobs (HPC regression testing)
- **Entry points**: CLI (`hpc-runner`), Web API + Dashboard
- **Key principle**: Solver scripts are black-box; platform never calls schedulers (SLURM, MPI, etc.)

## 2. Component Architecture

```mermaid
flowchart TB
    subgraph clients [Clients]
        CLI[CLI hpc-runner]
        Browser[Web Browser]
    end
    subgraph api [API Layer]
        Flask[Flask basic_restapi]
    end
    subgraph core [Harness Core]
        Config[Config Loader]
        Runner[Runner]
        Parser[Parser]
        Storage[Storage]
    end
    subgraph data [Data]
        YAML[configs/ jobs/ solvers/]
        DB[(data/harness.db)]
    end
    subgraph external [External]
        SolverScript[Solver run.sh/run.py]
    end
    CLI --> Config
    CLI --> Runner
    CLI --> Storage
    Browser --> Flask
    Flask --> Config
    Flask --> Runner
    Flask --> Storage
    Config --> YAML
    Runner --> Parser
    Runner --> SolverScript
    Parser --> YAML
    Storage --> DB
```

## 3. Data Models

| Model | Location | Purpose |
|-------|----------|---------|
| Resource | `src/core/src/harness/config/schemas.py` | CPU/GPU, memory, node definitions |
| System | `src/core/src/harness/config/schemas.py` | Resource bundle, env vars, constraints |
| Solver | `src/core/src/harness/config/schemas.py` | Entrypoint, parser_config, allowed_systems |
| Job | `src/core/src/harness/config/schemas.py` | Solver+system pairing, success_criteria |
| RunResult | `src/core/src/harness/runner.py` | job_name, returncode, metrics, passed, processor |

## 4. Config Structure

```
configs/
├── resources/     # Resource definitions (cpus, gpus, memory)
├── systems/       # System definitions (resources, env)
├── jobs/          # Job definitions (solver+system pairings)

solvers/
├── <solver-name>/
│   ├── solver.yaml       # Metadata, entrypoint, parser_config path
│   ├── run.sh or run.py  # Executed as black-box
│   └── parser_config.yaml  # Optional: regex patterns for metrics
```

## 5. Job Execution Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Config
    participant Runner
    participant Parser
    participant Solver
    participant Storage
    Client->>API: POST /api/run_jobs
    API->>Config: load_all()
    Config-->>API: jobs, solvers, systems
    API->>Runner: run_jobs(job_list, solvers, systems)
    loop For each job
        Runner->>Solver: subprocess.run(entrypoint)
        Solver-->>Runner: stdout, stderr, returncode
        Runner->>Parser: extract_metrics(stdout+stderr)
        Parser-->>Runner: metrics dict
        Runner-->>API: RunResult
    end
    API->>Storage: store_run() for each result
    API-->>Client: JSON results
```

## 6. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard (index.html) |
| `/api/solvers` | GET | List solvers |
| `/api/jobs` | GET | List jobs |
| `/api/run_jobs` | POST | Run jobs (body: `{"jobs": ["name1"]}`) |
| `/api/runs` | GET | List runs (?solver=, ?processor=, ?limit=) |
| `/api/runs/<id>` | GET | Run detail |
| `/api/metrics/<solver>/<metric>` | GET | Metric history for trends |

## 7. Dashboard Views

- **Test Runs**: Table of runs, "Run All Jobs" button
- **Solvers**: Grid of configured solvers
- **Performance Trends**: Chart.js line chart (solver + metric selector)

## 8. Storage Schema

Table `runs`: id, job_name, solver_name, system_name, returncode, passed, runtime_seconds, timestamp, stdout, stderr, metrics_json, processor (probed at runtime via `platform.machine()`)

## 9. Deployment

- **Local**: `make api`, `make runner`
- **Docker**: `make docker-build`, `make docker-run` (mounts `./data`)
- **docker-compose**: `docker compose up --build`

## 10. Workspace Layout

```
DOW-1-26/
├── configs/           # YAML configs
├── solvers/           # Solver packages
├── data/              # harness.db (gitignored)
├── src/
│   ├── core/          # harness package
│   └── api/           # basic_restapi package
├── pyproject.toml     # uv workspace
└── Makefile
```
