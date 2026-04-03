"""Streamlit UI — minimal scaffolding for the HPC Regression Platform."""

import os
import sys
from datetime import timedelta
from pathlib import Path
import pandas as pd

import streamlit as st
import streamlit.components.v1 as components
import requests
from typing import Any
import plotly.graph_objects as go
import numpy as np
import json

# Allow importing runner from the same directory when launched via `streamlit run`
from config_editor import (  # noqa: E402
    discover_config_files,
    read_config,
    ConfigFile,
)
from metrics_dashboard import (  # noqa: E402
    get_runtime_trend_data,
    get_mlups_trend_data,
    get_baseline_values_for_metric,
    get_solver_baseline_metrics,
    get_baseline_comparison,
)
from charts import (
    render_runtime_trend,
    render_mlups_trend,
    single_solver_heatmap,
    multi_solver_heatmap,
    render_manual_baseline_overrides,
    render_single_solver_runs_vs_baseline,
    render_multi_solver_runs_vs_baseline,
)  # noqa: E402

from harness import get_db_path

from api_config import API_URL  # noqa: E402

DB_PATH = get_db_path()


def _testid(id: str) -> None:
    """Inject hidden data-testid marker for Playwright."""
    st.markdown(
        f'<span data-testid="{id}" style="display:none" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )


st.set_page_config(layout="wide", page_title="HPC Regression Platform")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if st.session_state.page == "Test Results":
    st.session_state.page = "Tests"
if st.session_state.page == "Run Solvers":
    st.session_state.page = "Solvers"
if st.session_state.get("page_radio") == "Run Solvers":
    st.session_state.page_radio = "Solvers"

if "test_result" not in st.session_state:
    st.session_state.test_result = None
if "run_job_results" not in st.session_state:
    st.session_state.run_job_results = None
if "page_change_requested" not in st.session_state:
    st.session_state.page_change_requested = False
if "page_radio" not in st.session_state:
    st.session_state.page_radio = st.session_state.page

# ---------------------------------------------------------------------------
# Global theme overrides (dark sidebar, card styles)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ── Dark sidebar ── */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #111827;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 6px;
        padding: 0.35rem 0.75rem;
        transition: background-color 0.15s ease;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: rgba(255, 255, 255, 0.07);
    }
    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
    }
    /* ── Expanders ── */
    details {
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
    }
    /* ── Dividers ── */
    hr { border-color: #E2E8F0; }
    /* ── Main content: wide usable width (Solvers, Long-Term Trends, tables) ── */
    .block-container {
        max-height: 95%;
        max-width: 95%;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    /* ── Run History: compact Baseline button on the right; shaded (primary) when set; clearer on hover ── */
    [data-testid="stHorizontalBlock"]:has(.stButton) .stButton button {
        opacity: 0.7;
        transition: opacity 0.15s ease;
        padding: 0.2rem 0.5rem !important;
        font-size: 0.8rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.stButton):hover .stButton button {
        opacity: 1;
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stCaptionContainer"]) [data-testid="stCaptionContainer"] {
        opacity: 0.85;
        transition: opacity 0.15s ease;
    }
    [data-testid="stHorizontalBlock"]:hover [data-testid="stCaptionContainer"] {
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = ["Home", "Solvers", "Run History", "Individual Trends", "Long-Term Trends", "Configs"]

st.sidebar.markdown(
    '<span data-testid="nav-sidebar" style="display:none" aria-hidden="true"></span>',
    unsafe_allow_html=True,
)

st.sidebar.title("Navigation")
if os.environ.get("RUN_SLURM_E2E") == "1":
    st.sidebar.caption("SLURM/LAMMPS mode — API must have Docker + job env (see `make start-services-slurm`).")
page_index = PAGES.index(st.session_state.page) if st.session_state.page in PAGES else 0

st.sidebar.markdown("---")

if 'page' not in st.session_state:
    st.session_state.page = PAGES[0]

def on_page_change():
    st.session_state.page = st.session_state.page_radio
    st.session_state.page_change_requested = False

# Sync the radio widget to match any programmatic page change.
# Must happen before the radio is instantiated — Streamlit forbids
# writing to a widget-bound key after the widget renders.
if st.session_state.get("page_change_requested"):
    st.session_state.page_radio = st.session_state.page
    st.session_state.page_change_requested = False

selected_page = st.sidebar.radio(
    "Go to",
    PAGES,
    key="page_radio",
    on_change=on_page_change
)

# ---------------------------------------------------------------------------
# Page: Home (welcome / platform overview)
# ---------------------------------------------------------------------------

def page_home() -> None:
    _testid("page-home")
    st.header("Welcome to the HPC Regression Platform")

    st.markdown(
        """
        **Target:** Run solver jobs and track performance over time in one place—whether you use
        the UI or the CLI—without tying the harness to a specific scheduler or MPI layout.

        - **Execution-agnostic:** solvers are black-box scripts; the platform works across HPC workloads.
        - **Operate:** submit jobs, watch live **Active runs**, and inspect stdout/stderr and metrics when they finish.
        - **Understand:** stored runs, per-solver charts, and long-term trend views support baselines and drift detection.
        - **Configure:** solver, system, and resource definitions live under `configs/` (browse YAML from the sidebar or read `docs/architecture.md`).
        """
    )

    st.markdown("Use the sidebar to navigate to **Solvers**, **Run History**, and **Trends**.")


# ---------------------------------------------------------------------------
# Page: Solvers (overview + run solvers)
# ---------------------------------------------------------------------------

def page_solvers() -> None:
    _testid("page-solvers")
    st.header("Solvers", help = "Every solver is listed below. Use **Batch run** to start several at once, or use each section’s **Run** for a single solver. Runs are always **queued in the background** (invocation ids); **Active runs** auto-refreshes live **execution_status**. **Quick status** / **Scheduler output** are for pasted ids or raw SLURM output; **Last run** shows stored results.")
    _testid("page-run-solvers")
    _render_run_solvers_panel()


# ---------------------------------------------------------------------------
# Page: Individual Trends (formerly Home — Metrics over job history)
# ---------------------------------------------------------------------------

def page_individual_trends() -> None:
    _testid("page-individual-trends")
    st.header("Individual Trends")
    st.write("Metrics for each solver over the entire job history.")

    available: list[dict[str, str]] = []
    try:
        available = requests.get(API_URL + "/api/available_metrics").json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

    if not available:
        st.info("No metrics data yet. Run solvers from the **Solvers** page or the CLI to collect metrics.")
        return

    options = [f"{dictionary['solver']} / {dictionary['metric']}" for dictionary in available]
    selected = st.selectbox(
        "Select solver and metric to view",
        options=options,
        key="home-metric-select",
        help="Solver metric combinations are defined in the backend configuration .yaml files. To add more, edit your configuration files on your backend host's filesystem.",
    )
    if not selected:
        return

    idx = options.index(selected)
    solver_name, metric_name = available[idx]["solver"], available[idx]["metric"]
    # history = get_metric_history(solver_name, metric_name, limit=500)

    history: list[dict[str, Any]] = []
    try:
        history = requests.get(API_URL + "/api/metrics/" + solver_name + "/" + metric_name).json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

    if not history:
        st.warning("No history for this metric.")
        return

    df = pd.DataFrame(history, columns=["timestamp", "value"])
    df = df.set_index("timestamp")

    # Try to fetch baseline for this solver/metric and plot it as a flat line
    baseline_val = None
    try:
        resp = requests.get(API_URL + f"/api/solvers/{solver_name}/baseline")
        if resp.status_code == 200:
            data = resp.json()
            metrics = data.get("metrics") or {}
            val = metrics.get(metric_name)
            if isinstance(val, (int, float)):
                baseline_val = float(val)
    except requests.exceptions.RequestException:
        baseline_val = None

    if baseline_val is not None:
        df["baseline"] = baseline_val
        subplot_help = (
            "Displays the metric over time for this solver. "
            "The flat 'baseline' line comes from the solver's current baseline run."
        )
    else:
        subplot_help = (
            "Displays the metric over time for this solver. "
            "No baseline line is shown because no baseline run is configured for this solver/metric."
        )

    st.subheader(f"{solver_name} — {metric_name}", help=subplot_help)
    st.line_chart(df)

    with st.expander("View raw data"):
        raw_df = pd.DataFrame(history, columns=["timestamp", "value"])
        st.dataframe(raw_df, width="stretch")


# ---------------------------------------------------------------------------
# Page: Run History
# ---------------------------------------------------------------------------

def page_run_history() -> None:
    _testid("page-run-history")
    st.header("Run History")
    st.write("Browse past runs. Filter by solver or processor.")

    runs_all: list[dict[str, Any]] = []
    try:
        runs_all = requests.get(API_URL + "/api/runs").json()
    except requests.exceptions.RequestException as e:
        st.error(f"API unavailable: {e}")
        return

    if not runs_all:
        st.info("No runs in database.")
        return

    solvers = sorted({r["solver_name"] for r in runs_all})
    processors = sorted({r.get("processor") or "unknown" for r in runs_all})

    col1, col2 = st.columns(2)
    with col1:
        solver_filter = st.selectbox("Filter by solver", ["(all)"] + solvers, key="history-solver")
    with col2:
        processor_filter = st.selectbox("Filter by processor", ["(all)"] + processors, key="history-processor")

    solver_arg = solver_filter if solver_filter != "(all)" else None
    processor_arg = processor_filter if processor_filter != "(all)" else None

    params = {"solver": solver_arg, "processor": processor_arg}
    filtered: list[dict[str, Any]] = []
    try:
        filtered = requests.get(API_URL + "/api/runs", params=params).json()
    except requests.exceptions.RequestException as e:
        st.error(f"API unavailable: {e}")
        return

    try:
        job_batch_uuids = requests.get(API_URL + "/api/get_job_batch_uuids").json()
    except requests.exceptions.RequestException:
        print("Failed to get batch job uuids")
        return

    # Use a graph mapping uuids to index of result in filtered to make a batch job
    # view
    batch_index_graph: dict[str, list[int]] = {}

    job_batch_uuids.append("")
    batch_count = 0
    for job in job_batch_uuids:
        for i, r in enumerate(filtered):
            if job == r['job_batch_uuid']:
                batch_count  += 1
                if job not in batch_index_graph:
                    batch_index_graph[job] = [i]
                else:
                    batch_index_graph[job].append(i)

    st.write(f"Showing {len(batch_index_graph)} batch(s) with {len(filtered)} run(s)")

    id_to_label = {
        int(r["id"]): f"{r['id']}: {r['job_name']} @ {r.get('timestamp', '')[:19]}"
        for r in filtered
        if r.get("id") is not None
    }
    delete_options = sorted(id_to_label.keys(), reverse=True)
    del_pick = st.multiselect(
        "Select runs to delete from the database",
        options=delete_options,
        format_func=lambda i: id_to_label[i],
        key="history-delete-multiselect",
    )
    if "pending_delete_ids" not in st.session_state:
        st.session_state.pending_delete_ids = None
    col_del_a, col_del_b = st.columns(2)
    with col_del_a:
        if st.button("Delete selected runs", type="primary", disabled=not del_pick, key="history-delete-btn"):
            st.session_state.pending_delete_ids = list(del_pick)
    with col_del_b:
        if st.session_state.pending_delete_ids:
            st.warning(f"Confirm deletion of {len(st.session_state.pending_delete_ids)} run(s)?")
            if st.button("Yes, delete permanently", key="history-delete-confirm"):
                try:
                    resp = requests.delete(
                        API_URL + "/api/runs",
                        json={"ids": st.session_state.pending_delete_ids},
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        st.success(f"Deleted {resp.json().get('deleted', '?')} run(s).")
                        st.session_state.pending_delete_ids = None
                        st.rerun()
                    else:
                        st.error(resp.text or str(resp.status_code))
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
            if st.button("Cancel", key="history-delete-cancel"):
                st.session_state.pending_delete_ids = None
                st.rerun()

    for batch_uuid in batch_index_graph.keys():
        batch_name = filtered[batch_index_graph[batch_uuid][0]]["job_batch_name"]
        batch_date = filtered[batch_index_graph[batch_uuid][0]]["job_batch_date"]
        i = batch_index_graph[batch_uuid]
        if batch_name != "":
            label = f"Batch ID: {batch_uuid} Batch Name: {batch_name} Batch Run Initiated On: {batch_date}"
        else:
            label = f"Batch ID: {batch_uuid} Batch Run Initiated On: {batch_date}"
        with st.expander(label, expanded=True):
            for i in batch_index_graph[batch_uuid]:
                render_job_expander(filtered[i])

def render_job_expander(r: dict[str: Any]) -> None:

    passed = "Passed" if r.get("passed") else "Failed"
    if r.get("passed"):
        icon = "✅"
    else:
        # ❌ if system failed (returncode != 0); ⚠️ only when failed solely due to validation
        returncode = r.get("returncode", 0)
        try:
            errs = json.loads(r.get("validation_errors") or "[]")
            has_validation_errors = isinstance(errs, list) and len(errs) > 0
        except (json.JSONDecodeError, TypeError):
            has_validation_errors = False
        if r.get("returncode", 0) != 0:
            icon = "❌"  # system/process failure
        elif r.get("validation_errors"):
            icon = "⚠️"  # validation only (returncode was 0)
        else:
            icon = "❌"
    is_baseline = r.get("is_baseline", False)
    run_id = r.get("id")
    # Row: expander (tab) on left, baseline control on the right; hover shows right side clearer
    col_expander, col_baseline = st.columns([5, 1])
    with col_expander:
        with st.expander(f"{icon} {r['job_name']} — {passed}({r.get('timestamp', '')})"):
            st.write(f"**Solver:** {r['solver_name']} | **System:** {r['system_name']} | **Returncode:** {r.get('returncode')} | **Runtime:** {r.get('runtime_seconds')}s")
            if r.get("stdout"):
                st.subheader("stdout")
                st.code(r["stdout"], language="text")
            if r.get("stderr"):
                st.subheader("stderr")
                st.code(r["stderr"], language="text")
            if r.get("metrics_json"):
                try:
                    metrics = json.loads(r["metrics_json"])
                    st.subheader("Metrics")
                    st.json(metrics)
                except json.JSONDecodeError:
                    st.text(r["metrics_json"])
            raw_errors = r.get("validation_errors")
            if raw_errors and raw_errors != "[]":
                if isinstance(raw_errors, str):
                    try:
                        validation_errors = json.loads(raw_errors)
                        st.subheader("Validation Errors")
                        st.json(validation_errors)
                    except json.JSONDecodeError:
                        st.subheader("Validation Errors")
                        st.text(raw_errors)
                else:
                    st.subheader("Validation Errors")
                    st.json(raw_errors)
            sids = r.get("scheduler_job_ids")
            if isinstance(sids, str):
                try:
                    sids = json.loads(sids or "[]")
                except (json.JSONDecodeError, TypeError):
                    sids = []
            if sids:
                st.caption(
                    f"SLURM job id(s): {', '.join(str(s) for s in sids)}"
                    + (f" — submit target: `{r.get('submit_container') or '?'}`" if r.get("submit_container") else "")
                )
                if st.button("Refresh SLURM status", key=f"slurm-refresh-{run_id}"):
                    try:
                        sresp = requests.get(
                            API_URL + f"/api/runs/{run_id}/slurm_status",
                            timeout=120,
                        )
                        st.session_state[f"slurm_status_{run_id}"] = sresp.json()
                    except requests.exceptions.RequestException as e:
                        st.session_state[f"slurm_status_{run_id}"] = {"message": str(e)}
                snap = st.session_state.get(f"slurm_status_{run_id}")
                if snap:
                    st.code(json.dumps(snap, indent=2), language="json")
    with col_baseline:
        if run_id is not None:
            if is_baseline:
                st.button(
                    "Baseline",
                    key=f"set-baseline-{run_id}",
                    type="primary",
                    help="This run is the current baseline",
                )
            else:
                if st.button(
                    "Baseline",
                    key=f"set-baseline-{run_id}",
                    help="Set this run as the baseline for comparison",
                ):
                    try:
                        resp = requests.post(API_URL + f"/api/runs/{run_id}/set_baseline")
                        if resp.status_code == 200:
                            st.success("Baseline set.")
                            st.rerun()
                        else:
                            st.error(resp.text or f"Error {resp.status_code}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Request failed: {e}")

# ---------------------------------------------------------------------------
# Run Solvers panel (embedded on Solvers page)
# ---------------------------------------------------------------------------

def _run_solver_spec_for_name(solver_by_name: dict[str, Any], sn: str) -> dict[str, Any]:
    """Build one POST /api/run_solvers solver entry (name + optional system)."""
    s = solver_by_name[sn]
    allowed = s.get("allowed_systems") or []
    default = s.get("default_system")
    need_pick = len(allowed) > 1 and not default
    if need_pick:
        sys_name = st.session_state.get(f"run-solver-system-{sn}")
        return {"name": sn, "system": sys_name}
    return {"name": sn, "system": None}


def _register_background_invocations(invs: list[dict[str, Any]]) -> None:
    """Remember invocation ids per solver and sync global monitor field."""
    by_solver = st.session_state.setdefault("run_solvers_last_invocation_by_solver", {})
    for inv in invs:
        sn = inv.get("solver_name")
        iid = inv.get("invocation_id", "")
        if sn and iid:
            by_solver[sn] = iid
            st.session_state[f"run-solvers-mon-id-{sn}"] = iid
    inv_top = ""
    if invs:
        inv_top = invs[0].get("invocation_id", "")
    st.session_state.last_solver_invocations = invs
    st.session_state.last_invocation_id = inv_top
    if inv_top:
        st.session_state._pending_run_solvers_monitor_invocation_id = inv_top


def _post_run_solvers(specs: list[dict[str, Any]], batch_name_input: str) -> bool:
    """
    POST run_solvers with background=True (queued invocations). Returns True after session updates on 202.
    """
    payload: dict[str, Any] = {"solvers": specs, "background": True}
    bn = (batch_name_input or "").strip()
    if bn:
        payload["batch_name"] = bn
    endpoint = API_URL + "/api/run_solvers"
    try:
        response = requests.post(endpoint, json=payload, timeout=60)
        response.raise_for_status()
        if response.status_code != 202:
            st.error(f"Expected 202 from run_solvers with background; got {response.status_code}.")
            return False
        data = response.json()
        invs = data.get("invocations") or []
        _register_background_invocations(invs)
        inv_top = data.get("invocation_id") or (invs[0].get("invocation_id", "") if invs else "")
        n = len(invs)
        if n > 1:
            st.success(f"Started {n} background invocations (one per solver). See **Active runs** above.")
        else:
            st.success(f"Background invocation started: `{inv_top}`")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Run request failed: {e}")
        st.caption(f"API: `{API_URL}` — ensure the API is running and reachable.")
    except Exception as e:
        st.error(f"Unexpected error while running solvers: {e}")
    return False


def _display_last_run_compact(r: dict[str, Any], *, run_id_key_prefix: str) -> None:
    """Show one stored run (from GET /api/runs) in compact form."""
    passed = r.get("passed")
    icon = "✅" if passed else "❌"
    rid = r.get("id")
    ts = (r.get("timestamp") or "")[:19]
    st.markdown(
        f"{icon} **{r.get('job_name', '')}** · {ts} · "
        f"return {r.get('returncode')} · **{r.get('runtime_seconds')}s** · "
        f"system `{r.get('system_name', '')}`"
    )
    raw_err = r.get("validation_errors")
    if raw_err and raw_err != "[]":
        if isinstance(raw_err, str):
            try:
                errs = json.loads(raw_err)
                if errs:
                    st.json(errs)
            except json.JSONDecodeError:
                st.text(raw_err)
        else:
            st.json(raw_err)
    with st.expander("Output & metrics", expanded=False):
        if r.get("stdout"):
            st.caption("stdout")
            st.code(r["stdout"], language="text")
        if r.get("stderr"):
            st.caption("stderr")
            st.code(r["stderr"], language="text")
        if r.get("metrics_json"):
            try:
                st.json(json.loads(r["metrics_json"]))
            except json.JSONDecodeError:
                st.text(r["metrics_json"])
        if rid is not None and st.button("Refresh SLURM status", key=f"{run_id_key_prefix}-slurm-{rid}"):
            try:
                sresp = requests.get(API_URL + f"/api/runs/{rid}/slurm_status", timeout=120)
                st.session_state[f"run_solvers_run_slurm_{rid}"] = sresp.json()
            except requests.exceptions.RequestException as e:
                st.session_state[f"run_solvers_run_slurm_{rid}"] = {"message": str(e)}
        snap = st.session_state.get(f"run_solvers_run_slurm_{rid}")
        if snap:
            st.code(json.dumps(snap, indent=2), language="json")


def _render_invocation_status_summary(payload: dict[str, Any]) -> None:
    """Human-readable lines for GET /api/invocations/{id}/execution_status (local or SLURM)."""
    status = payload.get("status") or "—"
    ex = payload.get("execution") or {}
    backend = ex.get("backend") or "—"
    loc = ex.get("local") or {}
    if isinstance(loc, dict) and loc.get("pid") is not None:
        local_line = f"pid **{loc.get('pid')}** · alive={loc.get('alive')}"
    else:
        local_line = "no local subprocess snapshot"
    jc = payload.get("jobs_completed", 0)
    jt = payload.get("jobs_total", 0)
    sids = payload.get("scheduler_job_ids") or ex.get("scheduler_job_ids") or []
    sched_ids = ", ".join(str(x) for x in sids) if sids else "—"
    detail = payload.get("scheduler_detail") or {}
    if isinstance(detail, dict) and detail:
        sched_state = "live scheduler data (see Full JSON expander)"
    elif sids:
        sched_state = "job ids recorded; live query empty or disabled"
    else:
        sched_state = "no scheduler jobs"
    err = payload.get("error")
    st.markdown(
        f"**Status:** {status} · **Backend:** `{backend}` · **Jobs:** {jc}/{jt}  \n"
        f"**Local:** {local_line}  \n"
        f"**Scheduler ids:** {sched_ids} · _{sched_state}_"
    )
    if err:
        st.warning(str(err))


def _render_invocation_execution_payload(payload: dict[str, Any]) -> None:
    """Summary plus full JSON in an expander (unified execution_status shape)."""
    _render_invocation_status_summary(payload)
    st.caption("_Full payload matches the summary above (for debugging)._")
    with st.expander("Full JSON (same execution_status)", expanded=False):
        st.json(payload)


def _render_invocation_quick_status(payload: dict[str, Any]) -> None:
    """execution_status summary lines only (no raw JSON expander)."""
    _render_invocation_status_summary(payload)


def _invocation_has_scheduler_jobs(rec: dict[str, Any]) -> bool:
    ex = rec.get("execution") or {}
    sids = rec.get("scheduler_job_ids") or ex.get("scheduler_job_ids") or []
    return bool(sids)


def _scheduler_hint_for_invocation_id(iid: str) -> bool:
    """Resolve whether an invocation has scheduler job ids (cached per id in session state)."""
    ck = f"run-solvers-sched-hint-{iid}"
    if ck in st.session_state:
        return bool(st.session_state[ck])
    try:
        r = requests.get(API_URL + f"/api/invocations/{iid}", timeout=15)
        if not r.ok:
            st.session_state[ck] = False
            return False
        st.session_state[ck] = _invocation_has_scheduler_jobs(r.json())
        return bool(st.session_state[ck])
    except requests.exceptions.RequestException:
        st.session_state[ck] = False
        return False


def _secondary_status_label_help(has_scheduler: bool | None) -> tuple[str, str]:
    """Button label and help for the secondary status action when scheduler presence is known or unknown."""
    if has_scheduler is True:
        return (
            "Raw scheduler output",
            "GET /slurm_status — raw squeue/sacct-style output (manual refresh).",
        )
    if has_scheduler is False:
        return (
            "Quick status",
            "GET /execution_status — summary only (pid, job counts, ids). Full snapshots auto-refresh under **Active runs**.",
        )
    return (
        "Quick status",
        "Enter an invocation id below; the label switches to Raw scheduler output when that invocation has scheduler job ids.",
    )


def _compact_secondary_status_label_help(has_scheduler: bool | None) -> tuple[str, str]:
    """Action button label + help for manual execution_status vs slurm_status pulls."""
    lbl, hlp = _secondary_status_label_help(has_scheduler)
    if has_scheduler is True:
        return "Scheduler output", hlp
    return lbl, hlp


def _run_secondary_invocation_status(iid: str, *, has_scheduler: bool) -> None:
    if has_scheduler:
        try:
            sr = requests.get(API_URL + f"/api/invocations/{iid}/slurm_status", timeout=90)
            if sr.ok:
                st.json(sr.json())
            else:
                st.error(sr.text)
        except requests.exceptions.RequestException as ex:
            st.error(str(ex))
    else:
        try:
            er = requests.get(API_URL + f"/api/invocations/{iid}/execution_status", timeout=90)
            if er.ok:
                _render_invocation_quick_status(er.json())
            else:
                st.error(er.text)
        except requests.exceptions.RequestException as ex:
            st.error(str(ex))


def _active_invocation_sig(rows: list[dict[str, Any]]) -> tuple[str, ...]:
    ids = [str(r.get("invocation_id", "") or "") for r in rows]
    return tuple(sorted(ids))


def _fetch_active_invocations_safe() -> list[dict[str, Any]]:
    try:
        active_resp = requests.get(
            API_URL + "/api/invocations",
            params={"active_only": True},
            timeout=15,
        )
        active_resp.raise_for_status()
        rows = active_resp.json()
        return rows if isinstance(rows, list) else []
    except (requests.exceptions.RequestException, ValueError, TypeError):
        return []


@st.fragment(run_every=timedelta(seconds=4))
def _run_solvers_active_runs_live_fragment() -> None:
    rows = _fetch_active_invocations_safe()
    sig = _active_invocation_sig(rows)
    prev = st.session_state.get("_run_solvers_active_sig")

    st.session_state["run_solvers_active_rows"] = rows

    if prev is not None and prev != sig:
        st.session_state["_run_solvers_active_sig"] = sig
        st.rerun()

    st.session_state["_run_solvers_active_sig"] = sig

    if not rows:
        return

    for rec in rows:
        iid = rec.get("invocation_id", "")
        solver = rec.get("solver_name") or "(unknown)"
        jids = ", ".join(rec.get("scheduler_job_ids") or []) or None
        bname = rec.get("batch_name") or None
        jc = rec.get("jobs_completed") or 0
        jt = rec.get("jobs_total") or 0
        ex = rec.get("execution") or {}
        backend = ex.get("backend") or "local"
        status = rec.get("status") or "running"
        has_sched_row = _invocation_has_scheduler_jobs(rec)
        sec_lbl_row, sec_hlp_row = _compact_secondary_status_label_help(has_sched_row)

        # ── Card header: solver name + id chip + status + Stop ──
        col_title, col_stop = st.columns([8, 1])
        with col_title:
            meta_parts = [f"`{backend}`"]
            if bname:
                meta_parts.append(f"batch: *{bname}*")
            if jids:
                meta_parts.append(f"scheduler ids: `{jids}`")
            st.markdown(
                f"**{solver}**"
                f"&nbsp;<code style='font-size:0.75rem;padding:2px 6px;"
                f"background:#e2e8f0;border-radius:4px'>{iid[:10]}…</code>"
                f"&nbsp;<span style='color:gray;font-size:0.85rem'>{status}</span>",
                unsafe_allow_html=True,
            )
            st.caption(" · ".join(meta_parts))
        with col_stop:
            st.markdown("<div style='padding-top:0.35rem'></div>", unsafe_allow_html=True)
            if st.button("⏹ Stop", key=f"run-solvers-cancel-{iid}", type="secondary"):
                try:
                    cresp = requests.post(
                        API_URL + f"/api/invocations/{iid}/cancel",
                        timeout=30,
                    )
                    st.json(cresp.json())
                except requests.exceptions.RequestException as ex:
                    st.error(str(ex))

        # ── Progress bar ──
        progress_frac = (jc / jt) if jt > 0 else 0.0
        prog_col, count_col = st.columns([7, 1])
        with prog_col:
            st.progress(progress_frac)
        with count_col:
            st.markdown(
                f"<div style='text-align:right;padding-top:0.25rem'><b>{jc}/{jt}</b> jobs</div>",
                unsafe_allow_html=True,
            )

        # ── Scheduler output button + collapsible execution details ──
        if has_sched_row:
            if st.button(sec_lbl_row, key=f"run-solvers-slurm-active-{iid}", help=sec_hlp_row):
                _run_secondary_invocation_status(iid, has_scheduler=has_sched_row)

        with st.expander("Details", expanded=False):
            try:
                er = requests.get(
                    API_URL + f"/api/invocations/{iid}/execution_status",
                    timeout=90,
                )
                if er.ok:
                    _render_invocation_execution_payload(er.json())
                else:
                    st.error(er.text)
            except requests.exceptions.RequestException as ex:
                st.error(str(ex))


@st.fragment(run_every=timedelta(seconds=4))
def _run_solvers_pasted_ids_live_fragment() -> None:
    names = st.session_state.get("_run_solvers_page_solver_names") or []
    for sn in names:
        mid_key = f"run-solvers-mon-id-{sn}"
        focus = (st.session_state.get(mid_key) or "").strip()
        if not focus:
            continue
        st.markdown(f"**{sn}** — pasted invocation `{focus[:12]}…`")
        try:
            er = requests.get(API_URL + f"/api/invocations/{focus}/execution_status", timeout=90)
            if er.ok:
                _render_invocation_execution_payload(er.json())
            else:
                st.error(f"{er.status_code}: {er.text}")
        except requests.exceptions.RequestException as e:
            st.error(str(e))


@st.fragment(run_every=timedelta(seconds=4))
def _run_solvers_advanced_invocation_live_fragment() -> None:
    focus = (st.session_state.get("run_solvers_monitor_invocation_id") or "").strip()
    if not focus:
        return
    try:
        er = requests.get(API_URL + f"/api/invocations/{focus}/execution_status", timeout=90)
        if er.ok:
            _render_invocation_execution_payload(er.json())
        else:
            st.error(f"{er.status_code}: {er.text}")
    except requests.exceptions.RequestException as e:
        st.error(str(e))


def _render_run_solvers_panel() -> None:
    st.session_state.pop("run_solver_results", None)

    solvers: list[dict[str, Any]] = []
    try:
        r1 = requests.get(API_URL + "/api/systems", timeout=15)
        r1.raise_for_status()
        _ = r1.json()
        r2 = requests.get(API_URL + "/api/solvers", timeout=15)
        r2.raise_for_status()
        solvers = r2.json()
    except requests.exceptions.RequestException as e:
        st.error(
            "Cannot reach the HPC Regression API. Start it with `make api` (or `uv run uvicorn ...`) "
            "from the project root, or set `HPC_API_URL` if the API runs elsewhere."
        )
        st.caption(f"Request failed: {e}")
        st.caption(f"Current `API_URL`: `{API_URL}` (override with env `HPC_API_URL`).")
        return
    except (ValueError, TypeError) as e:
        st.error("The API returned a response that is not valid JSON. Check API logs and `/docs`.")
        st.caption(str(e))
        return

    if not solvers:
        st.warning("No solvers configured. Add solvers under configs/solvers/.")
        return

    solver_by_name = {s["name"]: s for s in solvers}
    overview = [
        {
            "Solver": s["name"],
            "default_system": s.get("default_system") or "—",
            "allowed_systems": ", ".join(s.get("allowed_systems") or []),
        }
        for s in sorted(solvers, key=lambda x: x["name"])
    ]
    df_cfg = pd.DataFrame(overview)
    summaries_list: list[dict[str, Any]] = []
    try:
        raw_sum = requests.get(API_URL + "/api/solver_summaries", timeout=10).json()
        if isinstance(raw_sum, list):
            summaries_list = raw_sum
    except (requests.exceptions.RequestException, ValueError, TypeError):
        summaries_list = []

    if summaries_list:
        df_sum = pd.DataFrame(summaries_list)
        if not df_sum.empty and "solver_name" in df_sum.columns:
            df_sum = df_sum.rename(columns={"solver_name": "Solver"})
            merged = df_cfg.merge(df_sum, on="Solver", how="left")
            if "total_runs" in merged.columns:
                merged["total_runs"] = merged["total_runs"].fillna(0).astype(int)
            if "pass_count" in merged.columns:
                merged["pass_count"] = merged["pass_count"].fillna(0).astype(int)
            for col in ("last_timestamp", "last_job_name"):
                if col in merged.columns:
                    merged[col] = merged[col].where(pd.notna(merged[col]), "—")
            if "last_passed" in merged.columns:
                merged["last_passed"] = merged["last_passed"].apply(
                    lambda v: "—" if pd.isna(v) else ("yes" if v else "no")
                )
        else:
            merged = df_cfg.copy()
            merged["total_runs"] = 0
            merged["pass_count"] = 0
            merged["last_timestamp"] = "—"
            merged["last_job_name"] = "—"
            merged["last_passed"] = "—"
    else:
        merged = df_cfg.copy()
        merged["total_runs"] = 0
        merged["pass_count"] = 0
        merged["last_timestamp"] = "—"
        merged["last_job_name"] = "—"
        merged["last_passed"] = "—"

    _testid("run-solvers-overview")
    with st.expander("Solver overview", expanded=False):
        st.caption("Configured solvers plus aggregates from stored runs (when the database has history).")
        st.dataframe(merged, width="stretch", hide_index=True)

    st.session_state.setdefault("run_solvers_last_invocation_by_solver", {})
    if "_pending_run_solvers_monitor_invocation_id" in st.session_state:
        st.session_state.run_solvers_monitor_invocation_id = st.session_state.pop(
            "_pending_run_solvers_monitor_invocation_id"
        )
    elif "run_solvers_monitor_invocation_id" not in st.session_state:
        st.session_state.run_solvers_monitor_invocation_id = ""
    st.session_state.setdefault("last_invocation_id", "")

    solver_names = sorted(solver_by_name.keys())

    def _batch_select_all_cb() -> None:
        for n in solver_names:
            st.session_state[f"run-solvers-include-{n}"] = True

    def _batch_clear_cb() -> None:
        for n in solver_names:
            st.session_state[f"run-solvers-include-{n}"] = False

    st.subheader("Batch run", help = "Check the solvers to run together, then **Run batch**. Below: each solver has **Run**, then **Invocation** or **Last run**.")
    b_row1 = st.columns([4, 1, 1])
    with b_row1[0]:
        batch_name_input = st.text_input(
            "Batch name (optional)",
            value="",
            key="run-solvers-batch-name",
            help="Optional label stored with this run batch (same as API field batch_name).",
            placeholder="Enter an optional batch name here"
        )
    with b_row1[1]:
        st.button(
            "Select all",
            key="run-solvers-batch-all",
            help="Include every solver in the batch",
            on_click=_batch_select_all_cb,
        )
    with b_row1[2]:
        st.button(
            "Clear batch",
            key="run-solvers-batch-none",
            help="Uncheck all batch inclusions",
            on_click=_batch_clear_cb,
        )

    _testid("run-solvers-batch-picks")
    st.markdown("**Include in batch**")
    _BATCH_PICK_COLS = 4
    for i in range(0, len(solver_names), _BATCH_PICK_COLS):
        chunk = solver_names[i : i + _BATCH_PICK_COLS]
        cols = st.columns(len(chunk))
        for col, sn in zip(cols, chunk, strict=True):
            with col:
                st.checkbox(
                    sn,
                    key=f"run-solvers-include-{sn}",
                    help="Add this solver to the batch when you click Run batch.",
                )

    n_in_batch = sum(1 for sn in solver_names if st.session_state.get(f"run-solvers-include-{sn}", False))
    run_batch = st.button(
        f"Run batch ({n_in_batch})",
        type="primary",
        key="run-solvers-go",
        disabled=n_in_batch == 0,
    )

    if run_batch:
        batch_specs = [_run_solver_spec_for_name(solver_by_name, sn) for sn in solver_names if st.session_state.get(f"run-solvers-include-{sn}", False)]
        with st.spinner(f"Starting {len(batch_specs)} solver(s)…"):
            ok = _post_run_solvers(batch_specs, batch_name_input)
        if ok:
            st.rerun()

    with st.expander("How manual status works", expanded=False):
        st.markdown(
            "**Active runs** (immediately below) is the canonical live monitor: full `execution_status` (~4s) plus **Stop**. "
            "When the job has scheduler ids, **Scheduler output** there runs one-off `slurm_status`. "
            "Per-solver **Invocation** (below Active runs): active jobs point you to **Active runs**; paste a *different* id for "
            "**Quick status** / **Scheduler output** or **Cancel**."
        )
    st.divider()

    h_active, h_refresh = st.columns([5, 1])
    with h_active:
        st.subheader("Active runs", help = "Each background solver has its own invocation (cancel independently). **Active runs** polls `GET /execution_status` about every 4s while something is active, and triggers a full page refresh when the active set changes so cards stay in sync. **Scheduler output** appears only when SLURM job ids exist (raw `GET /slurm_status`).")
    with h_refresh:
        if st.button("Refresh", key="run-solvers-refresh-active", help="Reload the active invocations list"):
            st.rerun()
    _testid("run-solvers-active-runs")

    active_rows = _fetch_active_invocations_safe()
    sig0 = _active_invocation_sig(active_rows)
    st.session_state["run_solvers_active_rows"] = active_rows
    st.session_state["_run_solvers_active_sig"] = sig0

    if active_rows:
        _run_solvers_active_runs_live_fragment()
    else:
        st.caption("_No active runs._")

    st.divider()

    active_rows = st.session_state.get("run_solvers_active_rows", [])
    st.subheader("Solvers")

    active_by_solver: dict[str, list[dict[str, Any]]] = {}
    for rec in active_rows:
        sname = (rec.get("solver_name") or "").strip()
        if sname:
            active_by_solver.setdefault(sname, []).append(rec)

    def render_solver_card(sn: str, active_for_sn: list[dict[str, Any]]) -> None:
        s = solver_by_name[sn]
        allowed = s.get("allowed_systems") or []
        default_sys = s.get("default_system") or "—"
        allowed_txt = ", ".join(allowed) if allowed else "—"
        need_pick = len(allowed) > 1 and not s.get("default_system")

        run_left, name_right = st.columns([1, 6])
        with run_left:
            run_one = st.button(
                "Run",
                key=f"run-solvers-one-{sn}",
                type="primary",
                help="Queue this solver in the background (batch name from above); watch **Active runs**.",
            )
        with name_right:
            st.subheader(sn)
        st.caption(f"default_system: `{default_sys}` · allowed: {allowed_txt}")

        if need_pick:
            st.selectbox(
                "System (required for this solver)",
                options=allowed,
                key=f"run-solver-system-{sn}",
                help="Used for **Run** on this row and for **Run batch** when this solver is checked.",
            )

        if run_one:
            specs = [_run_solver_spec_for_name(solver_by_name, sn)]
            with st.spinner(f"Starting {sn}…"):
                ok = _post_run_solvers(specs, batch_name_input)
            if ok:
                st.rerun()

        view = st.radio(
            "Panel",
            ["Last run", "Enter Invocation ID"],
            horizontal=True,
            key=f"run-solvers-tab-{sn}",
            label_visibility="collapsed",
        )

        if view == "Enter Invocation ID":
            canonical_active_iid = ""
            if active_for_sn:
                if len(active_for_sn) == 1:
                    ar0 = active_for_sn[0]
                    a_iid = (ar0.get("invocation_id") or "").strip()
                    canonical_active_iid = a_iid
                    st.caption(
                        f"**Active** · `{a_iid[:12]}…` · _{ar0.get('status')}_ · "
                        f"jobs {ar0.get('jobs_completed', 0)}/{ar0.get('jobs_total', 0)}"
                    )
                    st.caption(
                        "Live **execution_status** and **Stop** for this job are in **Active runs** above "
                        "(auto-refresh; no duplicate status button here)."
                    )
                else:
                    st.caption("Multiple active invocations — pick one (details still live under **Active runs**).")
                    idx_key = f"run-solvers-active-pick-{sn}"
                    pick_labels = [
                        f"{(r.get('invocation_id') or '')[:12]}… · {r.get('status')} · "
                        f"{r.get('jobs_completed', 0)}/{r.get('jobs_total', 0)}"
                        for r in active_for_sn
                    ]
                    choice_i = st.selectbox(
                        "Active invocation for this solver",
                        range(len(active_for_sn)),
                        format_func=lambda i: pick_labels[i],
                        key=idx_key,
                        label_visibility="collapsed",
                    )
                    sel_rec = active_for_sn[choice_i]
                    canonical_active_iid = (sel_rec.get("invocation_id") or "").strip()
                    st.caption(
                        "Live **execution_status** and **Stop** for the selected invocation are in **Active runs** above."
                    )
            else:
                st.caption("_No active background invocation for this solver._")

            mid_key = f"run-solvers-mon-id-{sn}"
            st.session_state.setdefault(
                mid_key,
                st.session_state["run_solvers_last_invocation_by_solver"].get(sn, ""),
            )
            st.text_input(
                "Invocation id",
                key=mid_key,
                label_visibility="collapsed",
                placeholder="Invocation id (optional — enables live view below)",
                help=(
                    "Paste another invocation id to fetch **Quick status** or **Scheduler output** once, or **Cancel**. "
                    "If this matches the active job above, use **Active runs** for live status (same as **Stop** vs **Cancel**)."
                ),
            )
            focus = (st.session_state.get(mid_key) or "").strip()
            hint_paste = _scheduler_hint_for_invocation_id(focus) if focus else None
            c_lbl_paste, c_hlp_paste = _compact_secondary_status_label_help(hint_paste)
            paste_same_as_canonical = bool(
                canonical_active_iid and focus and focus == canonical_active_iid
            )
            if paste_same_as_canonical:
                st.caption(
                    "_Invocation id matches the active job — use **Active runs** above for live status and **Stop**._"
                )
            id_btn_l, id_btn_m, _ = st.columns([1, 1, 8])
            with id_btn_l:
                refresh_secondary_paste = st.button(
                    c_lbl_paste,
                    key=f"run-solvers-slurm-inv-{sn}",
                    help=c_hlp_paste,
                    disabled=paste_same_as_canonical,
                )
            with id_btn_m:
                cancel_picked = st.button(
                    "Cancel",
                    key=f"run-solvers-cancel-inv-{sn}",
                    type="secondary",
                    help="POST /api/invocations/{id}/cancel",
                )
            if refresh_secondary_paste:
                if not focus:
                    st.warning("Enter an invocation id.")
                elif paste_same_as_canonical:
                    pass
                else:
                    hs = hint_paste if hint_paste is not None else _scheduler_hint_for_invocation_id(focus)
                    _run_secondary_invocation_status(focus, has_scheduler=hs)
            if cancel_picked:
                if not focus:
                    st.warning("Enter an invocation id.")
                else:
                    try:
                        cr = requests.post(
                            API_URL + f"/api/invocations/{focus}/cancel",
                            timeout=30,
                        )
                        st.json(cr.json())
                    except requests.exceptions.RequestException as e:
                        st.error(str(e))

        elif view == "Last run":
            cache = st.session_state.setdefault("run_solvers_last_run_cache", {})
            lr_a, lr_b = st.columns([1, 3])
            with lr_a:
                load_lr = st.button("Refresh", key=f"run-solvers-lastrun-refresh-{sn}")
            with lr_b:
                st.caption("Loads the most recent stored run for this solver (same data as Run History).")

            if load_lr:
                try:
                    rows = requests.get(
                        API_URL + "/api/runs",
                        params={"solver": sn, "limit": 1},
                        timeout=15,
                    ).json()
                    if rows:
                        cache[sn] = rows[0]
                    else:
                        cache[sn] = None
                except requests.exceptions.RequestException as e:
                    st.error(str(e))
            entry = cache.get(sn)
            if sn not in cache:
                st.caption("Click **Refresh** to load the latest stored run.")
            elif entry is None:
                st.info("No completed runs in the database for this solver yet.")
            else:
                _display_last_run_compact(entry, run_id_key_prefix=f"run-solvers-lr-{sn}")

    tab_labels = [
        f"🔵 {sn}" if sn in active_by_solver else sn
        for sn in solver_names
    ]
    solver_tabs = st.tabs(tab_labels)
    for tab, sn in zip(solver_tabs, solver_names):
        with tab:
            render_solver_card(sn, active_by_solver.get(sn, []))

    any_paste = any((st.session_state.get(f"run-solvers-mon-id-{sn}") or "").strip() for sn in solver_names)
    if any_paste:
        with st.expander("Live view for pasted invocation ids", expanded=True):
            st.caption("~4s auto-refresh per id (`execution_status`).")
            st.session_state["_run_solvers_page_solver_names"] = tuple(solver_names)
            _run_solvers_pasted_ids_live_fragment()

    with st.expander("Advanced: inspect invocation by id", expanded=False):
        _testid("run-solvers-background-panel")
        st.caption(
            "Global id field (not tied to a solver row). Live JSON below refreshes ~4s when set. "
            "**Quick status** / **Scheduler output** = manual one-off pull (same as per-solver pasted id)."
        )
        st.text_input(
            "Invocation id to inspect",
            key="run_solvers_monitor_invocation_id",
            label_visibility="collapsed",
            placeholder="Invocation id",
            help="Paste any id; **Quick status** or **Scheduler output** matches the per-solver invocation field.",
        )
        focus_adv = (st.session_state.get("run_solvers_monitor_invocation_id") or "").strip()
        hint_adv = _scheduler_hint_for_invocation_id(focus_adv) if focus_adv else None
        c_lbl_adv, c_hlp_adv = _compact_secondary_status_label_help(hint_adv)
        adv_btn_l, adv_btn_m, _ = st.columns([1, 1, 8])
        with adv_btn_l:
            refresh_secondary_adv = st.button(
                c_lbl_adv,
                key="run-solvers-refresh-inv-slurm",
                help=c_hlp_adv,
            )
        with adv_btn_m:
            cancel_picked_adv = st.button(
                "Cancel",
                key="run-solvers-cancel-picked-invocation",
                type="secondary",
                help="POST /api/invocations/{id}/cancel",
            )

        if focus_adv:
            _run_solvers_advanced_invocation_live_fragment()

        if refresh_secondary_adv:
            if not focus_adv:
                st.warning("Enter an invocation id above.")
            else:
                hs_adv = hint_adv if hint_adv is not None else _scheduler_hint_for_invocation_id(focus_adv)
                _run_secondary_invocation_status(focus_adv, has_scheduler=hs_adv)
        if cancel_picked_adv:
            if not focus_adv:
                st.warning("Enter an invocation id above.")
            else:
                try:
                    cr = requests.post(
                        API_URL + f"/api/invocations/{focus_adv}/cancel",
                        timeout=30,
                    )
                    st.json(cr.json())
                except requests.exceptions.RequestException as e:
                    st.error(str(e))


# ---------------------------------------------------------------------------
# Page: Configs
# ---------------------------------------------------------------------------

# Shawn: Would be better to have the backend handle what we need from this
# but its less of a headache to remove dependencies so will keep for now
def page_configs() -> None:
    _testid("page-configs")
    st.header("Configs")
    st.write("View resources, solvers, and systems configurations.")

    config_files = discover_config_files()
    if not config_files:
        st.warning("No config files found in configs/.")
        return

    # Group by category
    by_category: dict[str, list[ConfigFile]] = {}
    for cf in config_files:
        by_category.setdefault(cf.category, []).append(cf)

    category = st.selectbox(
        "Category",
        options=sorted(by_category.keys()),
        key="config-category",
    )
    files_in_cat = by_category[category]
    selected = st.selectbox(
        "File",
        options=files_in_cat,
        format_func=lambda f: f.display_name,
        key="config-file",
    )

    if not selected:
        return

    # Load current content
    try:
        current_content = read_config(selected.path)
    except OSError as e:
        st.error(f"Cannot read file: {e}")
        return

    st.code(current_content, language="yaml")


# ---------------------------------------------------------------------------
# Page: Long-Term Trends (Page 4)
# ---------------------------------------------------------------------------

def page_long_term_trends() -> None:

    _testid("page-long-term-trends")

    # Focus whichever Plotly iframe the user hovers over, so their first click
    # hits the data point directly (avoids the browser iframe focus-first click).
    components.html("""
    <script>
        (function() {
            function attachHoverFocus() {
                const iframes = window.parent.document.querySelectorAll('iframe');
                iframes.forEach(function(iframe) {
                    if (!iframe.dataset.hoverFocusAttached) {
                        iframe.dataset.hoverFocusAttached = 'true';
                        iframe.addEventListener('mouseenter', function() {
                            iframe.focus();
                        });
                    }
                });
            }
            // Run now and after a short delay to catch iframes rendered late.
            attachHoverFocus();
            setTimeout(attachHoverFocus, 800);
        })();
    </script>
    """, height=0)

    st.header("Long-Term Trends", help = "Performance of solvers over time. Use the sidebar to filter by solver, system, and date range.")

    df_all = get_runtime_trend_data(str(DB_PATH))

    if df_all.empty:
        st.info("No run data available yet. Run solvers from the **Solvers** page or the CLI to collect data.")
        return

    # --- Sidebar filters ---------------------------------------------------
    all_solvers = sorted(df_all["solver_name"].unique().tolist())
    all_systems = sorted(df_all["system_name"].unique().tolist())

    min_date = df_all["timestamp"].dt.date.min()
    max_date = df_all["timestamp"].dt.date.max()

    # Persist date range in session state so it survives page navigation
    if "trend_date_start" not in st.session_state:
        st.session_state.trend_date_start = min_date
    if "trend_date_end" not in st.session_state:
        st.session_state.trend_date_end = max_date

    st.sidebar.markdown("### Long-Term Trends Filters")

    selected_solvers = st.sidebar.multiselect(
        "Solver(s)",
        options=all_solvers,
        default=all_solvers,
        key="trend-solver-filter",
    )
    selected_systems = st.sidebar.multiselect(
        "System(s)",
        options=all_systems,
        default=all_systems,
        key="trend-system-filter",
    )
    date_range = st.sidebar.date_input(
        "Date range",
        value=(st.session_state.trend_date_start, st.session_state.trend_date_end),
        min_value=min_date,
        max_value=max_date,
        key="trend-date-filter",
    )

    # Update session state whenever the widget changes
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        st.session_state.trend_date_start = date_range[0]
        st.session_state.trend_date_end = date_range[1]
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0] if date_range else min_date

    # --- Filter DataFrame --------------------------------------------------
    import pandas as pd

    mask = (
        df_all["solver_name"].isin(selected_solvers)
        & df_all["system_name"].isin(selected_systems)
        & (df_all["timestamp"].dt.date >= start_date)
        & (df_all["timestamp"].dt.date <= end_date)
    )
    df_filtered = df_all[mask]

    tab_heatmap, tab_runtime, tab_mlups = st.tabs(["Heatmap", "Runtime Trend", "MLUPS Trend"])

    with tab_heatmap:
        # --- Heatmap -----------------------------------------------------------
        # st.subheader("Metrics Heatmap")

        heatmap_mode = st.radio(
            "Heatmap mode",
            options=["All metrics for one solver/system", "One metric across all solvers/systems"],
            horizontal=True,
            key="heatmap-mode",
        )

        # Fetch runs from API and apply date + system filters in Python
        try:
            params = {}
            if len(selected_solvers) == 1:
                params["solver"] = selected_solvers[0]
            heatmap_runs = requests.get(API_URL + "/api/runs", params=params).json()
            heatmap_runs = [
                r for r in heatmap_runs
                if r.get("metrics_json")
                and start_date <= pd.Timestamp(r["timestamp"]).date() <= end_date
                and r.get("system_name") in selected_systems
            ]
        except requests.exceptions.RequestException as e:
            st.warning(f"Could not fetch runs for heatmap: {e}")
            heatmap_runs = []

        if not heatmap_runs:
            st.info("No data available for heatmap with the current filters.")
        elif heatmap_mode == "All metrics for one solver/system":
            # This mode is intended for a single solver + system. If multiple are selected,
            # let the user pick which one to visualize.
            solver_pick = selected_solvers[0] if selected_solvers else None
            system_pick = selected_systems[0] if selected_systems else None
            if len(selected_solvers) > 1:
                solver_pick = st.selectbox(
                    "Solver (for all-metrics heatmap)",
                    options=selected_solvers,
                    key="heatmap-all-metrics-solver-pick",
                )
            if len(selected_systems) > 1:
                system_pick = st.selectbox(
                    "System (for all-metrics heatmap)",
                    options=selected_systems,
                    key="heatmap-all-metrics-system-pick",
                )

            solver_runs = [
                r
                for r in heatmap_runs
                if r.get("solver_name") == solver_pick and r.get("system_name") == system_pick
            ]
            if not solver_runs:
                st.info("No metric data for the selected solver/system in this date range.")
            else:
                heatmap_color_mode_single = st.selectbox(
                    "Heatmap color scaling",
                    options=["Default (min-max)", "Baseline (per metric)"],
                    key="heatmap-color-mode-single",
                    help="Baseline mode colors each metric relative to its baseline value for this solver.",
                )

                if heatmap_color_mode_single.startswith("Baseline") and solver_pick:
                    baseline_metrics_api = get_solver_baseline_metrics(str(solver_pick))

                    # Manual overrides (per-metric) for this solver
                    metric_keys = sorted(json.loads(solver_runs[0]["metrics_json"]).keys())
                    baseline_metrics = render_manual_baseline_overrides(
                        item_labels=metric_keys,
                        defaults=baseline_metrics_api,
                        key_prefix=f"manual_baseline_all_{solver_pick}",
                        caption_text=(
                            "Type a baseline value per metric to use instead of (or when there is no) "
                            "run-based baseline. Pre-filled from the current baseline run when available."
                        ),
                        input_help="Baseline value for {label}",
                    )

                    if not baseline_metrics:
                        st.info("No baseline metrics available. Set a baseline in Run History or enter manual values above.")
                        single_solver_heatmap(solver_runs, solver_name=str(solver_pick))
                    else:
                        baseline_comparison_data = get_baseline_comparison(
                            solver_name=str(solver_pick), limit=200
                        )
                        single_solver_heatmap(
                            solver_runs,
                            solver_name=str(solver_pick),
                            baseline_metrics=baseline_metrics,
                            baseline_comparison_data=baseline_comparison_data if baseline_comparison_data else None,
                        )
                else:
                    single_solver_heatmap(solver_runs, solver_name=str(solver_pick or ""))
        else:
            available_metrics_hm = sorted({
                k
                for r in heatmap_runs
                for k in json.loads(r["metrics_json"]).keys()
            })
            if not available_metrics_hm:
                st.info("No dynamic metrics available for the selected filters.")
            else:
                selected_hm_metric = st.selectbox(
                    "Metric",
                    options=available_metrics_hm,
                    key="heatmap-metric-select",
                )
                heatmap_color_mode = st.selectbox(
                    "Heatmap color scaling",
                    options=["Default (spec / min-max)", "Baseline (per solver)"],
                    key="heatmap-color-mode",
                    help="Baseline mode colors each solver relative to its baseline value for the selected metric.",
                )
                if selected_hm_metric == "mlups":
                    metric_dictionary = {"python-solver": (2.1e6, 4e6)}
                elif selected_hm_metric == "runtime_seconds":
                    metric_dictionary = {
                        "python-solver": (0.008, 0.01),
                        "echo-solver": (0.0, 0.01),
                        "cpuinfo-test": (0.0, 0.01),
                    }
                else:
                    metric_dictionary = {}

                if heatmap_color_mode.startswith("Baseline"):
                    solver_names_for_baseline = sorted({r["solver_name"] for r in heatmap_runs})
                    baseline_values_api = get_baseline_values_for_metric(
                        selected_hm_metric, solver_names_for_baseline
                    )
                    baseline_values = render_manual_baseline_overrides(
                        item_labels=solver_names_for_baseline,
                        defaults=baseline_values_api,
                        key_prefix=f"manual_baseline_{selected_hm_metric}",
                        caption_text=(
                            "Type a baseline value per solver to use instead of (or when there is no) "
                            "run-based baseline. Pre-filled from current run baselines when available."
                        ),
                        input_help=f"Baseline value for {selected_hm_metric}",
                    )
                    if not baseline_values:
                        st.info(
                            "No baseline values available. Set baselines in Run History or enter manual values above."
                        )
                        multi_solver_heatmap(selected_hm_metric, heatmap_runs, metric_dictionary or None)
                    else:
                        baseline_comparison_data = get_baseline_comparison(limit=100)
                        multi_solver_heatmap(
                            selected_hm_metric,
                            heatmap_runs,
                            None,
                            baseline_values=baseline_values,
                            baseline_comparison_data=baseline_comparison_data if baseline_comparison_data else None,
                        )
                else:
                    if not metric_dictionary:
                        st.info("Define the spec ranges for each metric for each solver to show a specification range heatmap.")
                    else:
                        multi_solver_heatmap(selected_hm_metric, heatmap_runs, metric_dictionary)


        # --- Raw data expander -------------------------------------------------
        with st.expander("View data summary"):
            if df_filtered.empty:
                st.info("No rows match the current filters.")
            else:
                st.dataframe(
                    df_filtered[["timestamp", "solver_name", "system_name", "job_name", "runtime_seconds", "passed"]],
                    width='stretch',
            )
    with tab_runtime:
        # --- Runtime trend chart -----------------------------------------------
        _testid("section-runtime-trend")
        # st.subheader("Runtime (wall-clock) Trend")
        render_runtime_trend(df_filtered, st.session_state)

    with tab_mlups:
        # --- MLUPS trend chart -------------------------------------------------
        _testid("section-mlups-trend")
        # st.subheader("Throughput Trend (MLUPS)")
        df_mlups_all = get_mlups_trend_data(str(DB_PATH))
        if not df_mlups_all.empty:
            mlups_mask = (
                df_mlups_all["solver_name"].isin(selected_solvers)
                & df_mlups_all["system_name"].isin(selected_systems)
                & (df_mlups_all["timestamp"].dt.date >= start_date)
                & (df_mlups_all["timestamp"].dt.date <= end_date)
            )
            df_mlups_filtered = df_mlups_all[mlups_mask]
        else:
            df_mlups_filtered = df_mlups_all
        render_mlups_trend(df_mlups_filtered, st.session_state)



# ---------------------------------------------------------------------------
# Page: Tests
# ---------------------------------------------------------------------------

#def page_tests() -> None:
#    _testid("page-tests")
#    st.header("Tests")
#    st.write("")
#
#    _testid("btn-run-test")
#    if st.button("Run Test", key="btn-run-test"):
#        with st.spinner("Running tests…"):
#            result = run_tests()
#
#        st.session_state.test_result = result
#        st.rerun()
#
#    st.write("")
#
#    if st.session_state.test_result is None:
#        st.info("No test results yet. Click Run Test above to execute the suite.")
#        return
#
#    result = st.session_state.test_resul
#
#    if result.success:
#        st.success(f"All tests passed  (exit code {result.returncode})")
#    else:
#        st.error(f"Tests failed  (exit code {result.returncode})")
#
#    st.write("")
#
#    if result.stdout:
#        st.subheader("stdout")
#        st.code(result.stdout, language="text")
#
#    if result.stderr:
#        st.subheader("stderr")
#        st.code(result.stderr, language="text")


def goto_selected_run(point):
    '''
    Uses the streamlit on_select event info to goto the run information for a run that was clicked on.
    Uses a custom HTML injection script to scroll to the corresponding component and check the target
    against the text in the <p> element inside of it.
    Notably this feature could conceivably be slow or bork if we implement a date range cutoff that
    is not synced with what is shown in the line plots, should consider adding a separate view
    or refactoring the run history page to suport filtering by a specific date range.
    This should probably go to some job view in the future
    '''
    target = point['x'].replace(' ', 'T', 1).split(".")[0]
    components.html(f"""

    <script>
        const target = "{target}".toLowerCase();

        console.log(target)
        function openAndScroll() {{
            const summaries = window.parent.document.querySelectorAll('summary');

            for (const summary of summaries) {{
                // Check the <p> inside the summary instead of the summary itself
                const p = summary.querySelector('p');
                const text = (p ? p.innerText : summary.innerText).trim().toLowerCase();
                console.log(summary)
                console.log(text)
                console.log(target)
                if (text.includes(target)) {{
                    if (text.includes("—")) {{
                        const expander = summary.closest('details');
                        if (!expander.hasAttribute('open')) {{
                            summary.click();
                        }}
                        summary.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        break;
                    }}
                }}
            }}
        }}

        setTimeout(openAndScroll, 300);
    </script>
    """, height=0)

def single_solver_heatmap(
    filtered,
    solver_name: str = "",
    *,
    baseline_metrics: dict[str, float] | None = None,
    baseline_comparison_data: list[dict[str, Any]] | None = None,
) -> None:
    column_names = [key for key in json.loads(filtered[0]['metrics_json'])]
    row_names = [x['timestamp'] for x in filtered]
    data = []
    # blegh this will have NaN data if some dates are missing metrics
    for i in range(len(filtered)):
        row = []
        metrics_json = json.loads(filtered[i]['metrics_json'])
        for key, value in metrics_json.items():
            row.append(value)
        data.append(row)
    # descending time order is more intuitive
    data.reverse()
    # Min-max normalization (0 to 1)
    df = pd.DataFrame(data, columns=column_names, index=row_names)
    numeric_df = df.apply(pd.to_numeric, errors='coerce')
    numeric_df = numeric_df.dropna(axis=1, how="all")

    # heatmap in baseline mode
    if baseline_metrics:
        # Baseline ratio per metric (value / baseline_metric)
        cols = [c for c in numeric_df.columns if c in baseline_metrics and baseline_metrics.get(c, 0) > 0]
        # check if any of the columns are in the baseline_comparison_data
        if not cols:
            st.info("No baseline values found for the metrics in this heatmap; showing default view.")
            baseline_metrics = None
        else:
            ratio_df = numeric_df[cols].copy()
            # baseline ratio per metric
            for c in cols:
                ratio_df[c] = ratio_df[c] / float(baseline_metrics[c])
            ratio_df = ratio_df.replace([np.inf, -np.inf], np.nan).fillna(0)
            z = ratio_df.transpose() # transpose the dataframe to get the metrics as the columns and the dates as the rows
            custom = numeric_df[cols].transpose() 
            zmin = 0.0
            zmax = 2.0
            colorscale = [
                [0.0, "red"],
                [0.25, "orange"],
                [0.5, "green"],
                [0.75, "orange"],
                [1.0, "red"],
            ]
            colorbar = dict(
                tickvals=[0.0, 1.0, 2.0],
                ticktext=["0× baseline", "1× baseline", "2× baseline"],
                ticks="outside",
            )
            hovertemplate = "Value: %{customdata:.4f}<br>× baseline: %{z:.2f}×<extra></extra>"
            help_text = "Baseline view colors each metric by value ÷ baseline (green near 1×; red further away)."

            fig = go.Figure(
                data=go.Heatmap(
                    customdata=custom,
                    z=z,
                    x=z.columns,
                    y=z.index,
                    zmin=zmin,
                    zmax=zmax,
                    colorscale=colorscale,
                    colorbar=colorbar,
                    xgap=2,
                    ygap=2,
                    hovertemplate=hovertemplate,
                )
            )
    if not baseline_metrics:
        normalized = (numeric_df - numeric_df.min()) / (numeric_df.max() - numeric_df.min())
        normalized = normalized.fillna(0)
        normalized = normalized.transpose()
        fig = go.Figure(
            data=go.Heatmap(
                customdata=numeric_df.transpose(),
                z=normalized,
                x=normalized.columns,
                y=normalized.index,
                colorscale="Viridis",
                xgap=2,
                ygap=2,
                hovertemplate="Non-Normalized Value: %{customdata:.4f}<extra></extra>",
            )
        )
        help_text = (
            "Heatmap compares numeric metrics for a single solver/system using per-metric min-max normalized values."
        )
    fig.update_layout(
        xaxis=dict(
            type="category"
        )
    )
    st.header("All Metrics Heatmap", help=help_text)
    st.plotly_chart(fig)

    # In baseline mode, hide raw table and show comparison expander instead
    # this is just my stylistic choice, we can change this if we want
    if not baseline_metrics:
        with st.expander("View heatmap data"):
            st.dataframe(numeric_df, use_container_width=True)
    else:
        # make it nice and pretty with baseline metrics
        # perhaps, I can move this segment to clean code later
        if baseline_comparison_data:
            render_single_solver_runs_vs_baseline(
                solver_name=solver_name,
                baseline_metrics=baseline_metrics,
                baseline_comparison_data=baseline_comparison_data,
            )

def multi_solver_heatmap(
    metric_name: str,
    filtered,
    min_max_dictionary: dict[str, tuple[float, float]] | None = None,
    *,
    baseline_values: dict[str, float] | None = None,
    baseline_comparison_data: list[dict[str, Any]] | None = None,
) -> None:
    def normalize_row(row):
        solver = row.name
        if baseline_values:
            base_val = baseline_values.get(solver)
            if base_val is None or base_val == 0:
                # No usable baseline for this solver; leave as zeros
                return row * 0.0
            return row / base_val
        if min_max_dictionary:
            if solver in min_max_dictionary:
                min_value, max_value = min_max_dictionary[solver]
            else:
                st.warning(
                    f"Supplied min_max dictionary does not have entry for {solver}, "
                    "will use observed range 0–1."
                )
                min_value, max_value = 0.0, 1.0
            return (row - min_value) / (max_value - min_value)
        # Fallback: simple min–max per solver if no spec or baseline is provided
        observed_min = float(row.min())
        observed_max = float(row.max())
        if observed_max == observed_min:
            return row * 0.0
        return (row - observed_min) / (observed_max - observed_min)
    try:
        solvers: list[dict[str, Any]] = requests.get(API_URL + "/api/solvers").json()
    except requests.exceptions.RequestException:
        solvers = []
    column_names = [x['name'] for x in solvers]
    row_names = [i for i in range(len(filtered))]
    data = []
    # blegh this will have NaN data if some dates are missing metrics
    for i in range(len(filtered)):
        solver_name = filtered[i]['solver_name']
        row = []
        metrics_json = json.loads(filtered[i]['metrics_json'])
        for key, value in metrics_json.items():
            if key == metric_name:
                row.append(value)
                row.append(filtered[i]['timestamp'][:19])
                row.append(metric_name)
                row.append(solver_name)

        data.append(row)
    # descending time order is more intuitive
    data.reverse()
    # Min-max normalization (0 to 1)
    df = pd.DataFrame(data, index=row_names)
    pivot = pd.pivot_table(df, values = 0, columns = 3, index = 1)
    pivot = pivot.transpose()
    # normalize value based on either baseline ratios or the supplied spec ranges
    normalized = pivot.apply(normalize_row, axis=1)

    if baseline_values:
        zmin = 0.0
        zmax = 2.0
        # Divergent scale: green at 1× baseline, red when further from baseline (above or below)
        colorscale = [
            [0.0, "red"],
            [0.25, "orange"],
            [0.5, "green"],
            [0.75, "orange"],
            [1.0, "red"],
        ]
        colorbar = dict(
            tickvals=[0.0, 1.0, 2.0],
            ticktext=["0× baseline", "1× baseline", "2× baseline"],
            ticks="outside",
        )
        help_text = (
            f"Heatmap shows {metric_name} as a ratio to each solver's baseline value. "
            "Green = at baseline; red = further from baseline (above or below)."
        )
    else:
        zmin = 0.0
        zmax = 1.0
        colorscale = [
            [0.0, "green"],
            [0.5, "yellow"],
            [1.0, "red"],
        ]
        colorbar = dict(
            tickvals=np.arange(0.0, 1.0, 1.0 / 3.0),  # center ticks in each band
            ticktext=["Within Spec", "Near Average", "Out of Spec "],
            ticks="outside",
        )
        help_text = (
            f"Heatmap shows whether {metric_name} is within a specified per-solver "
            "normalized range over the time series if a range was supplied; otherwise "
            "it uses observed min/max."
        )

    if baseline_values:
        hovertemplate = "Value: %{customdata:.4f}<br>× baseline: %{z:.2f}×<extra></extra>"
    else:
        hovertemplate = "Non-Normalized Value: %{customdata:.4f}<extra></extra>"

    fig = go.Figure(
        data=go.Heatmap(
            customdata=pivot,
            z=normalized,
            x=normalized.columns,
            y=normalized.index,
            zmin=zmin,
            zmax=zmax,
            colorscale=colorscale,
            colorbar=colorbar,
            hovertemplate=hovertemplate,
            xgap=2,  # Makes vertical gridlines
            ygap=2,  # Makes horizontal gridlines
        )
    )

    fig.update_layout(xaxis=dict(type="category"))
    st.header(
        f"{metric_name} Heatmap",
        help=help_text,
    )
    # Display in Streamlit
    st.plotly_chart(fig)
    if not baseline_values:
        with st.expander("View heatmap data"):
            st.dataframe(df, use_container_width=True)
    if baseline_values and baseline_comparison_data:
        render_multi_solver_runs_vs_baseline(
            metric_name=metric_name,
            baseline_values=baseline_values,
            baseline_comparison_data=baseline_comparison_data,
        )
    if min_max_dictionary:
        with st.expander("Specification Ranges"):
            st.dataframe(pd.DataFrame(min_max_dictionary).rename(index={0: "Lower Spec Range", 1: "Upper Spec Range"}).transpose(), use_container_width=True)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

if st.session_state.page == "Home":
    page_home()
elif st.session_state.page == "Solvers":
    page_solvers()
elif st.session_state.page == "Individual Trends":
    page_individual_trends()
elif st.session_state.page == "Run History":
    page_run_history()
    if "clicked_point" in st.session_state:
        goto_selected_run(st.session_state["clicked_point"])
        del st.session_state["clicked_point"]

elif st.session_state.page == "Long-Term Trends":
    page_long_term_trends()
#elif st.session_state.page == "Tests":
#    page_tests()
elif st.session_state.page == "Configs":
    page_configs()
