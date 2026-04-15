# User Interface Specification — HPC Regression Platform (Streamlit)

| Field | Value |
|--------|--------|
| **Document type** | User interface specification |
| **Implementation** | `src/ui/app.py`, `src/ui/matrix_grid_style.py`, `src/ui/charts.py`, `src/ui/api_config.py` |
| **Authors** | Shree Patel, Shawn Schulz |
| **Last updated** | 15 April 2026 |

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
| **Purpose** | Select **solver × system** pairs (allowed combinations only) and start **background** runs: one invocation per selected cell (`POST /api/run_solvers` with `background: true`). Optional **session label** tags runs (`session_label` / `job_batch_name`). **Saved presets** persist checkbox selections in the API database. |
| **Primary heading** | “Run Matrix” |
| **Caption** | Explains session labels and **GET/PUT/DELETE `/api/matrix_presets`**. |
| **`data-testid`** | `page-run-matrix`; grid region `run-matrix-grid` (inside the matrix **fragment**). |
| **Session row (main block)** | **Session label (optional)** — text input (`run-matrix-session-label`). Typing a name that matches a saved preset (case-insensitive) loads that preset into the matrix. **Save** / **Delete** — fixed-width buttons aligned with the text field; **Save** PUTs the current selection under the session label; **Delete** asks for confirmation then DELETEs the preset. |
| **Presets** | **GET `/api/matrix_presets`** populates the **Saved presets** select box (leading option **“—”** clears the matrix and session label). Choosing a preset loads cells and fills the session label; state updates are coordinated so the dropdown and text field stay in sync (including **deferred** updates on **Save** / **Run** so Streamlit session state is not written after widgets are instantiated). |
| **Select runs row (fragment)** | Subheader **“Select runs”**. **Saved presets** and **“Run selected (N)”** share the same column weights as the session row so widths line up. **Run selected** is disabled when N=0. After a successful run, optional PUT to save the selection under the session label; toast + full rerun. |
| **Matrix** | Rendered inside **`@st.fragment(run_every=…)`** (~4s): polls **`GET /api/invocations?active_only=true`** for active jobs. Rows = solvers; columns = systems; disallowed pairs show an em dash in a dashed cell. **Checkboxes** select cells; **↔** toggles a solver row; **↕** toggles a system column. Active invocations show a **●** (green) in the cell with a tooltip (status, ids, progress, etc.). |
| **Layout / CSS** | Column weights, row spacing, and whole-grid **translate** for the matrix shell come from **`MatrixRunLayoutTuning`** defaults in `src/ui/matrix_grid_style.py` (not exposed as sidebar sliders in the current UI). Injected CSS: `matrix_grid_control_css` (toggle/checkbox alignment, fragment-safe selectors). |
| **Primary action** | **“Run selected (N)”** — primary button. On success, toast; user is pointed to **Job Activity** in copy. |
| **API** | `GET /api/systems`, `GET /api/solvers`, `GET /api/matrix_presets`, `GET /api/matrix_presets/{label}`, `PUT /api/matrix_presets/{label}`, `DELETE /api/matrix_presets/{label}`, `GET /api/invocations?active_only=true`, `POST /api/run_solvers` |
| **Empty / error** | Error if API unreachable; warning if no solvers/systems in config (page returns before the matrix). |

---

### 5.3 Job Activity

| Item | Specification |
|------|----------------|
| **Purpose** | Single place for **live invocations** (in-memory) and **stored runs** (database): pick one job, inspect details, cancel in-flight work, delete a stored run, set a baseline. |
| **Primary heading** | “Job Activity” |
| **`data-testid`** | `page-job-activity` |
| **Captions** | (1) Explains live vs stored icons and that **Filter by solver** / **Filter by system** apply to both. (2) Notes the list reloads on interaction and new runs come from **Run Matrix**. |
| **Filters** | **Filter by solver** and **Filter by system** — options **“(all)”** or values drawn from invocations + stored runs. **Running jobs only** — checkbox: show only **queued** / **running** invocations; stored runs are omitted from the unified list while checked. |
| **Data loading** | `GET /api/invocations` (full list). `GET /api/runs` without params for baseline matching; **filtered** `GET /api/runs?solver=&system=` drives the stored-run side of the picker. Client-side filter for invocations by solver/system; running-only further narrows invocations. |
| **Summary line** | **“Jobs (this filter):”** *N* live invocation(s), *M* stored run(s) (newest first); adds a note when **Running only** is on. |
| **Unified pick** | **`st.selectbox` “Job”** (`job-history-unified-pick`): internal keys `inv:{invocation_id}` and `run:{id}` with formatted labels (status icons, solver@system, timestamps). Duplicates suppressed when a finished invocation already has a matching stored run in the filtered set. If nothing matches, an info empty state and early return. If the current pick falls off the list, selection resets to the first option. |
| **Drill-down / defer** | **Long-Term Trends** can set **`jh_preselect_run_id`** to pre-select a stored run. Internal **`jh_defer_job_history_pick`** clears or sets the unified pick after delete/navigation without violating widget session-state rules. |
| **Invocation branch** | Loads **`GET /api/invocations/{id}`**. **Queued/running:** completion poller, status line, optional backend caption, **stdout** via live log viewer (follow-to-bottom control; caption from shared job-log help). **Cancel invocation** POSTs **`/api/invocations/{id}/cancel`**. **Completed/failed/cancelled** without a stored run yet: may show results JSON, stdout snapshot, or defer-switch to the new stored run row after **`jh_pending_switch_to_stored`**. |
| **Stored run branch** | Header row: **Run id**, job name, timestamp; **Baseline** (primary if current baseline, else clickable **set baseline** POST **`/api/runs/{id}/set_baseline`**); **Delete** — confirm **Yes, delete** / **Cancel**, then **`DELETE /api/runs`** with JSON body `{ "ids": [...] }`. Detail body: session label / batch uuid when present; solver, system, return code, runtime; **stdout** / **stderr** / metrics / validation via log viewers or code blocks; SLURM refresh and related helpers where **`_render_run_record_detail_body`** applies. |
| **API** | `GET /api/invocations`, `GET /api/invocations/{id}`, `POST /api/invocations/{id}/cancel`, `GET /api/runs`, `GET /api/runs` (query: `solver`, `system`), `DELETE /api/runs`, `POST /api/runs/{id}/set_baseline`, `GET /api/runs/{id}/slurm_status` as applicable |

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
- **Run Matrix** checkbox states persist until the session ends or the user clears them. **Saved presets** (`run-matrix-saved-pick`, `run-matrix-session-label`) and sync keys (`_run_matrix_synced_pick`, deferred `_run_matrix_defer_saved_pick` after Save/Run) persist for continuity across reruns.
- **Job Activity** unified pick and filters use dedicated `session_state` keys (`job-history-*`, `ja_pending_delete_run_id`, etc.).

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
- Run Matrix layout/CSS: `src/ui/matrix_grid_style.py`
- Charts helpers: `src/ui/charts.py`
- REST API: `src/api/` (OpenAPI under `/docs` when the API is running)
