# User Interface Specification — HPC Regression Platform (Streamlit)

| Field | Value |
|--------|--------|
| **Document type** | User interface specification |
| **Implementation** | `src/ui/app.py`, `src/ui/charts.py`, `src/ui/api_config.py` |
| **Authors** | Shree Patel, Shawn Schulz |
| **Last updated** | 14 April 2026 |

---

## 1. Purpose and scope

### 1.1 Purpose

This document specifies the **browser-facing user interface** of the HPC Regression Platform prototype: navigation, screens, primary controls, data sources, and cross-cutting behaviors. It reflects the **current** Streamlit implementation.

### 1.2 Audience

Engineers, testers, and stakeholders who need a single reference for **what the UI does today**—not for backend harness internals or solver configuration authoring (see non-goals).

### 1.3 Business context (summary)

Dow’s HPC environment requires frequent security-driven updates; the platform helps detect when those changes break or degrade scientific software performance. The UI supports running solver workloads, monitoring jobs, inspecting results, and exploring performance over time.

---

## 2. System context

### 2.1 Architecture

| Layer | Responsibility |
|--------|----------------|
| **Browser** | Streamlit app (`streamlit run src/ui/app.py`). |
| **API** | REST API (FastAPI). The UI **does not** invoke the CLI or import harness Python modules directly. |
| **Configuration** | YAML/TOML under `configs/` on the host; the UI reads files for **Configs** only where implemented. |

### 2.2 API availability

- Default base URL comes from `HPC_API_URL` (see `src/ui/api_config.py`); typical local dev: `http://localhost:8000`.
- Without a reachable API, pages that depend on `/api/*` show errors or empty states (e.g. Run Matrix cannot load solvers/systems).

### 2.3 SLURM / integration mode

When `RUN_SLURM_E2E=1`, the sidebar may show a caption that the stack expects Docker + job environment for SLURM-backed demos.

---

## 3. Definitions

| Term | Meaning |
|------|---------|
| **Solver** | A configured workload definition (e.g. under `configs/solvers/`). |
| **System** | A target execution environment (e.g. cluster, local dev). |
| **solver@system** | Harness job identity for a run of a given solver on a given system. |
| **Invocation** | An in-memory background run tracked by the API (`GET /api/invocations`, …). |
| **Stored run** | A persisted row in the database (`GET /api/runs`, …). |
| **Session label** | Optional tag sent as `session_label` on run requests; stored with runs as batch/session metadata (`job_batch_name` / legacy `batch_name`). |

---

## 4. Global UI requirements

### 4.1 Navigation

- **Location:** Left sidebar, title **Navigation**.
- **Control:** Radio group **“Go to”** with options **exactly** as listed in [§5](#5-page-specifications).
- **Default page:** **Home** on first load.
- **Hidden marker:** `data-testid="nav-sidebar"` (for automation).

### 4.2 Session migration (backward compatibility)

Older session keys may still map to current pages (e.g. legacy page names are rewritten to **Run Matrix** or **Job Activity**). This is implementation detail; users should rely on the sidebar labels in §5.

### 4.3 Global run-completion notifications

- A **fragment** polls active invocations on **every** page.
- When the active set changes and jobs finish, **toast** messages encourage opening **Job Activity** for results.

### 4.4 Trends → Job Activity (drill-down)

- On **Long-Term Trends**, **clicking** a point in supported Plotly charts sets session state and navigates to **Job Activity**, with the corresponding stored run pre-selected when the match can be resolved.

### 4.5 Automation hooks (`data-testid`)

Primary pages expose stable test ids (see each page). E2E tests rely on these.

---

## 5. Page specifications

Navigation order and titles:

1. **Home**
2. **Run Matrix**
3. **Job Activity**
4. **Individual Trends**
5. **Long-Term Trends**
6. **Configs**

---

### 5.1 Home

| Item | Specification |
|------|----------------|
| **Purpose** | Welcome and high-level orientation (execution-agnostic harness, operate vs understand, pointer to `configs/` and docs). |
| **Primary heading** | “Welcome to the HPC Regression Platform” |
| **`data-testid`** | `page-home` |
| **Content** | Markdown: goals, bullets for **Run Matrix**, **Job Activity**, trends, configuration; short navigation hint. |
| **API** | None required. |

---

### 5.2 Run Matrix

| Item | Specification |
|------|----------------|
| **Purpose** | Select **solver × system** pairs (allowed combinations only) and start **background** runs: one invocation per selected cell (`POST /api/run_solvers` with `background: true`). |
| **Primary heading** | “Run Matrix” |
| **`data-testid`** | `page-run-matrix`; grid region `run-matrix-grid` |
| **Inputs** | **Session label (optional)** — text field; sent as `session_label`. |
| **Matrix** | Rows = solvers; columns = systems; disallowed pairs show “—”. **Checkboxes** select cells; **↔** toggles an entire solver row; **↕** toggles an entire system column. |
| **Live status** | Matrix **fragment** refreshes on a short interval; active invocations show a **dot** in the cell and tooltips with status, invocation id, backend, progress, scheduler ids when present. |
| **Primary action** | **“Run selected (N)”** — primary button; disabled when N=0. On success, user is directed to **Job Activity** for monitoring. |
| **API** | `GET /api/systems`, `GET /api/solvers`, `GET /api/invocations?active_only=true`, `POST /api/run_solvers` |
| **Empty / error** | Message if API unreachable; warning if no solvers/systems in config. |

---

### 5.3 Job Activity

| Item | Specification |
|------|----------------|
| **Purpose** | Single place for **live invocations** (queued/running/…) and **stored runs** (database): pick one job, inspect details, cancel in-flight work, delete stored rows, set baseline runs. |
| **Primary heading** | “Job Activity” |
| **`data-testid`** | `page-job-activity` |
| **Filters** | **Filter by solver (stored runs)** and **Filter by system (stored runs)** — narrow which stored runs appear in the combined list. |
| **Actions** | **Refresh list**; **multiselect stored runs** + **Delete selected runs** with confirmation; **Baseline** on stored run detail (when not already baseline). |
| **Unified pick** | **Select box “Job”** lists invocations and stored runs in one list (formatted labels with status icons). |
| **Invocation branch** | Shows status, live log viewer (with auto-scroll behavior where applicable), **Cancel invocation** when relevant. |
| **Stored run branch** | Run metadata, **Baseline** control, stdout/stderr/metrics/validation as viewers, **Refresh SLURM status** when scheduler metadata exists. |
| **API** | `GET /api/invocations`, `GET /api/invocations/{id}`, `GET /api/runs` (with filters), `DELETE /api/runs`, `POST /api/runs/{id}/set_baseline`, `POST /api/invocations/{id}/cancel`, `GET /api/runs/{id}/slurm_status` as applicable |

---

### 5.4 Individual Trends

| Item | Specification |
|------|----------------|
| **Purpose** | Per-solver **metric history** over time as a **line chart**; optional **baseline** line when the solver’s baseline run defines that metric. |
| **Primary heading** | “Individual Trends” |
| **`data-testid`** | `page-individual-trends` |
| **Selection** | **Select box** “Select solver and metric to view” — options from `GET /api/available_metrics`. |
| **Chart** | `st.line_chart` for timestamp vs value; if baseline exists, extra series **baseline**. |
| **Raw data** | Expander **“View raw data”** with a dataframe. |
| **API** | `GET /api/available_metrics`, `GET /api/metrics/{solver}/{metric}`, `GET /api/solvers/{solver}/baseline` |
| **Empty** | Info when no metrics yet (suggests **Run Matrix** or CLI). |

---

### 5.5 Long-Term Trends

| Item | Specification |
|------|----------------|
| **Purpose** | Multi-solver / multi-system views over a **date range**: **heatmaps** and **metric trend** visualizations (Plotly), with **sidebar** filters persisted in session state. |
| **Primary heading** | “Long-Term Trends” |
| **`data-testid`** | `page-long-term-trends` |
| **Sidebar (this page)** | **Solver(s)** multiselect, **System(s)** multiselect, **Date range** — applied to the main content. |
| **Data source** | Local DB via `get_trend_runs_data` for the main table; heatmap path also uses `GET /api/runs` with optional solver filter. |
| **Tabs** | **Heatmap** \| **Metric trends** |
| **Heatmap** | Modes: all metrics for one solver/system, or one metric across solvers/systems; color scaling options include default min-max and **baseline-relative** where implemented. |
| **Metric trends** | Plotly charts; **click** on a point triggers navigation to **Job Activity** (see [§4.4](#44-trends--job-activity-drill-down)). |
| **Empty** | Info when no run data (suggests **Run Matrix** or CLI). |

---

### 5.6 Configs

| Item | Specification |
|------|----------------|
| **Purpose** | **Read-only** browse of YAML files discovered under `configs/` (grouped by category). |
| **Primary heading** | “Configs” |
| **`data-testid`** | `page-configs` |
| **Controls** | **Category** select box, **File** select box. |
| **Content** | Selected file rendered as **syntax-highlighted code** (YAML). |
| **Persistence** | No save; no edit workflow in the current implementation. |

---

## 6. Visual design and theming

### 6.1 Framework

- Streamlit default typography and components unless overridden by **CSS** injected in `app.py` (e.g. dark sidebar, card-style metrics, wide main content).

### 6.2 Principles (non-prescriptive)

- Prefer **clear hierarchy** (headers, captions, help) over dense controls.
- **Primary actions** use Streamlit primary button styling where applicable (e.g. **Run selected** on Run Matrix).
- Status feedback uses standard Streamlit patterns: `st.success`, `st.warning`, `st.error`, `st.toast`, progress indicators.

### 6.3 Icons and symbols

- The UI uses **status icons** and compact symbols in lists (e.g. job status, matrix active dot). **Emoji** appear in some captions (e.g. Job Activity legend); this is intentional for scanability in the current build.

---

## 7. State and persistence

### 7.1 Streamlit `session_state`

- **Page navigation** is bound to `page_radio` / `page` with sync rules for programmatic changes (e.g. chart drill-down).
- **Filters** persist across navigation where keys are set (e.g. Long-Term Trends date range, heatmap mode, solver/system filters, Individual Trends metric selection).
- **Run Matrix** checkbox states persist until the session ends or the user clears them.

### 7.2 Minimum state principle

- Persist only what is needed for UX continuity (filters, selections, scroll positions for log viewers where implemented). Avoid duplicating server state that the API already owns.

---

## 8. Backend communication

- **Transport:** HTTP only (`requests`, `API_URL` / `HPC_API_URL`).
- **JSON** request bodies for non-trivial POST/DELETE (e.g. `run_solvers`, bulk delete runs).
- **Asynchronous jobs:** Run Matrix uses **background** invocations (`202`); synchronous `run_solvers` exists for automation but is not the primary Streamlit path.

---

## 9. Goals and non-goals (UI)

### 9.1 Goals

- Submit and monitor solver runs (**Run Matrix**, **Job Activity**).
- Inspect outputs and metrics (Job Activity, trends pages).
- Visualize historical and comparative performance (**Individual Trends**, **Long-Term Trends**).
- Browse configuration files read-only (**Configs**).

### 9.2 Non-goals (current)

- **Authoring new solvers** entirely within the UI.
- **Editing** harness YAML/TOML through the UI (Configs is view-only; validation/save flows elsewhere are out of scope for this document).

---

## 10. References

- Application entry: `src/ui/app.py`
- Charts helpers: `src/ui/charts.py`
- REST API: `src/api/` (OpenAPI under `/docs` when the API is running)
