"""Streamlit UI — minimal scaffolding for the HPC Regression Platform."""

import html
import os
import sys
import uuid
from urllib.parse import quote
from datetime import timedelta
from typing import Literal
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
    build_metric_trend_frame,
    get_baseline_values_for_metric,
    get_baseline_comparison,
    get_solver_baseline_metrics,
    get_trend_runs_data,
    list_numeric_metric_names,
)
from charts import (
    render_numeric_metric_trend,
    single_solver_heatmap,
    multi_solver_heatmap,
    render_manual_baseline_overrides,
    render_single_solver_runs_vs_baseline,
    render_multi_solver_runs_vs_baseline,
)  # noqa: E402

from harness import get_db_path

from api_config import API_URL  # noqa: E402
from matrix_grid_style import (  # noqa: E402
    DEFAULT_MATRIX_GRID_CONTROL_STYLE,
    DEFAULT_MATRIX_RUN_LAYOUT_TUNING,
    MATRIX_INNER_BAND,
    MatrixRunLayoutTuning,
    matrix_grid_control_css,
)

DB_PATH = get_db_path()

# Live subprocess stdout: fixed viewport (N lines); client polls API for smooth updates; tail pauses when user scrolls up.
_LIVE_LOG_VIEWPORT_LINES = 10
_LIVE_LOG_VIEWPORT_HEIGHT_PX = _LIVE_LOG_VIEWPORT_LINES * 20
_LIVE_LOG_POLL_MS = 400
# Job Activity page (live invocation + stored run): shared help for the unified log viewer.
_JOB_HISTORY_LOG_CAPTION = (
    "The log opens at the **top**. Click **↓** to jump to the bottom"
    " (live jobs follow new output from there); "
    "scroll up to pause, or scroll back to the **bottom** to resume."
)
# Populated before the Job selectbox; value cannot be set after that widget is created (Streamlit).
_JH_DEFER_PICK_CLEAR = "__jh_defer_pick_clear__"


def _stored_run_status_icon(r: dict[str, Any]) -> str:
    """Pass / fail / validation icons — same rules as the former Run History list."""
    if r.get("passed"):
        return "✅"
    if r.get("returncode", 0) != 0:
        return "❌"
    if r.get("validation_errors"):
        return "⚠️"
    return "❌"


def _invocation_row_icon(rec: dict[str, Any]) -> str:
    """Icon for Job Activity dropdown: runner when running, else status-appropriate."""
    st_ = (rec.get("status") or "").strip().lower()
    if st_ == "running":
        return "🏃"
    if st_ == "queued":
        return "⏳"
    if st_ == "completed":
        return "✅"
    if st_ == "failed":
        return "❌"
    if st_ == "cancelled":
        return "🛑"
    return "❔"


def _jh_stored_row_label(r: dict[str, Any]) -> str:
    icon = _stored_run_status_icon(r)
    return (
        f"{icon} {r['id']}: {r['job_name']} @ "
        f"{(r.get('timestamp') or '')[:19]}"
    )


def _jh_invocation_select_label(rec: dict[str, Any]) -> str:
    iid = (rec.get("invocation_id") or "").strip()
    sn = rec.get("solver_name") or "?"
    st_ = rec.get("status") or "?"
    sl = (rec.get("session_label") or rec.get("batch_name") or "").strip()
    tail = f"{iid[:12]}…" if len(iid) > 12 else iid
    jc = rec.get("jobs_completed", 0)
    jt = rec.get("jobs_total", 0)
    extra = f" · {sl}" if sl else ""
    icon = _invocation_row_icon(rec)
    return f"{icon} {sn} · {st_} · jobs {jc}/{jt} · {tail}{extra}"


def _jh_system_names_for_inv_option_list(rec: dict[str, Any]) -> set[str]:
    """Union of API system_names and completed results (for filter dropdown options)."""
    out = {str(x) for x in (rec.get("system_names") or []) if x}
    for item in rec.get("results") or []:
        if isinstance(item, dict) and item.get("system_name"):
            out.add(str(item["system_name"]))
    return out


def _jh_invocation_matches_filters(
    rec: dict[str, Any], *, solver_filter: str, system_filter: str
) -> bool:
    if solver_filter != "(all)":
        if (rec.get("solver_name") or "").strip() != solver_filter:
            return False
    if system_filter != "(all)":
        names = [str(x) for x in (rec.get("system_names") or []) if x]
        if not names:
            return False
        if system_filter not in names:
            return False
    return True


def _match_stored_run_for_invocation(
    inv: dict[str, Any], runs: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Pick the newest stored run row produced by this background invocation (solver + batch + job name)."""
    sl = (inv.get("session_label") or inv.get("batch_name") or "").strip()
    sn = (inv.get("solver_name") or "").strip()
    if not sn:
        return None
    jnames = list(inv.get("job_names") or inv.get("run_labels") or [])
    candidates: list[dict[str, Any]] = []
    for row in runs:
        if (row.get("solver_name") or "") != sn:
            continue
        if sl and (row.get("job_batch_name") or "").strip() != sl:
            continue
        if jnames and row.get("job_name") not in jnames:
            continue
        candidates.append(row)
    if not candidates:
        return None
    return max(candidates, key=lambda x: (x.get("timestamp") or ""))


def _apply_jh_inv_to_stored_switch(runs_all: list[dict[str, Any]]) -> None:
    """Switch job-history pick from inv: to run: before the selectbox is built (Streamlit forbids changing widget state after instantiate)."""
    pend = st.session_state.pop("jh_pending_switch_to_stored", None)
    if isinstance(pend, dict) and pend.get("run_id") is not None:
        rid = int(pend["run_id"])
        iid = (pend.get("invocation_id") or "").strip()
        st.session_state["job-history-unified-pick"] = f"run:{rid}"
        st.session_state["jh_log_key_handoff"] = {"run_id": rid, "invocation_id": iid}
        return
    pick0 = st.session_state.get("job-history-unified-pick")
    if not pick0 or not pick0.startswith("inv:"):
        return
    iid0 = pick0[4:].strip()
    if not iid0:
        return
    try:
        r = requests.get(API_URL + f"/api/invocations/{iid0}", timeout=30)
        if not r.ok:
            return
        inv0 = r.json()
    except requests.exceptions.RequestException:
        return
    st0 = (inv0.get("status") or "").strip()
    if st0 in ("queued", "running"):
        return
    match = _match_stored_run_for_invocation(inv0, runs_all)
    if match is None or match.get("id") is None:
        return
    rid = int(match["id"])
    st.session_state["job-history-unified-pick"] = f"run:{rid}"
    st.session_state["jh_log_key_handoff"] = {"run_id": rid, "invocation_id": iid0}


@st.fragment(run_every=timedelta(seconds=2))
def _jh_invocation_completion_poller(iid: str, runs_all: list[dict[str, Any]]) -> None:
    """Detect when a queued/running invocation finishes; queue switch to [Stored] or rerun the page. Does not render the live log (so the log iframe is not recreated on this interval)."""
    try:
        r = requests.get(API_URL + f"/api/invocations/{iid}", timeout=30)
        if not r.ok:
            return
        inv = r.json()
    except requests.exceptions.RequestException:
        return
    status = (inv.get("status") or "").strip()
    if status in ("queued", "running"):
        return
    match = _match_stored_run_for_invocation(inv, runs_all)
    if match is not None and match.get("id") is not None:
        rid = int(match["id"])
        st.session_state["jh_pending_switch_to_stored"] = {"run_id": rid, "invocation_id": iid}
        st.rerun()
        return
    st.rerun()


def _render_log_viewer(
    initial_text: str,
    *,
    storage_key_suffix: str,
    scope: Literal["default", "job_history"] = "default",
    jump_to_latest_control: bool = False,
    live_invocation_id: str | None = None,
    resume_job_history_session_scroll: bool = False,
) -> None:
    """Fixed-height log in an iframe: live mode polls GET /api/invocations/{{id}}; static mode is read-only with the same scroll/jump UX."""
    h = _LIVE_LOG_VIEWPORT_HEIGHT_PX
    iframe_h = h + 12
    escaped_initial = html.escape(initial_text)
    uid = f"ll-pre-{uuid.uuid4().hex}"
    api_js = json.dumps(API_URL)
    inv_live = (live_invocation_id or "").strip()
    inv_js = json.dumps(inv_live)
    uid_js = json.dumps(uid)
    poll_ms = _LIVE_LOG_POLL_MS
    is_static = live_invocation_id is None
    static_js = "true" if is_static else "false"
    resume_jh_js = "true" if resume_job_history_session_scroll else "false"
    inv_safe = storage_key_suffix.strip()
    if scope == "job_history":
        stick_key = f"hpc_jh_ll_stick_{inv_safe}"
        scroll_key = f"hpc_jh_ll_scroll_{inv_safe}"
    else:
        stick_key = f"hpc_ll_stick_{inv_safe}"
        scroll_key = f"hpc_ll_scroll_{inv_safe}"
    stick_key_js = json.dumps(stick_key)
    scroll_key_js = json.dumps(scroll_key)
    jump_js = "true" if jump_to_latest_control else "false"
    btn_uid = f"ll-jump-{uid}"
    btn_uid_js = json.dumps(btn_uid)
    if jump_to_latest_control:
        pre_dim_style = "height:100%;max-height:100%;"
    else:
        pre_dim_style = f"height:{h}px;max-height:{h}px;"

    jump_title = "Scroll to bottom of log" if is_static else "Go to latest output and follow new lines"
    jump_aria = "Scroll to bottom of log" if is_static else "Go to latest output"

    pre_block = f"""<pre id="{uid}" style="box-sizing:border-box;margin:0;width:100%;{pre_dim_style}overflow:auto;white-space:pre-wrap;word-break:break-word;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:0.75rem;line-height:1.5;background:rgba(49,51,63,0.08);padding:0.5rem 0.75rem;border-radius:0.25rem;">{escaped_initial}</pre>"""
    wrap_open = (
        f'<div style="position:relative;width:100%;height:{h}px;box-sizing:border-box;">'
        if jump_to_latest_control
        else ""
    )
    wrap_close = "</div>" if jump_to_latest_control else ""
    jump_btn = ""
    if jump_to_latest_control:
        jump_btn = f"""<button type="button" id="{btn_uid}" title="{html.escape(jump_title)}" aria-label="{html.escape(jump_aria)}"
  style="position:absolute;left:50%;bottom:0;transform:translateX(-50%);z-index:2;width:2rem;height:2rem;margin:0;padding:0;border:1px solid rgba(0,0,0,0.12);border-radius:6px;background:rgba(255,255,255,0.92);cursor:pointer;box-shadow:0 1px 3px rgba(0,0,0,0.08);font-size:1.25rem;line-height:1;color:rgba(30,41,59,0.88);">&#8595;</button>"""

    components.html(
        f"""<!DOCTYPE html><html><body style="margin:0;padding:0;">
{wrap_open}
{pre_block}
{jump_btn}
{wrap_close}
<script>
(function() {{
  const API = {api_js};
  const INV = {inv_js};
  const STATIC = {static_js};
  const PRE_ID = {uid_js};
  const POLL_MS = {poll_ms};
  const BOTTOM_EPS = 8;
  const JUMP_BTN = {btn_uid_js};
  const SHOW_JUMP = {jump_js};
  const RESUME_JH_SCROLL = {resume_jh_js};
  const stickKey = {stick_key_js};
  const scrollKey = {scroll_key_js};
  const pre = document.getElementById(PRE_ID);
  if (!pre) return;

  // Job Activity (scope job_history): do not follow until the user clicks the ↓ button; other scopes: default follow unless paused.
  // RESUME_JH_SCROLL: same storage keys as live log — restore stick/scroll after completion → stored (new iframe).
  let stickToBottom;
  if (SHOW_JUMP && RESUME_JH_SCROLL) {{
    stickToBottom = sessionStorage.getItem(stickKey) === "1";
  }} else if (SHOW_JUMP) {{
    stickToBottom = false;
  }} else {{
    stickToBottom = sessionStorage.getItem(stickKey) !== "0";
  }}
  let initialTailDone = false;

  function scrollMax() {{
    return Math.max(0, pre.scrollHeight - pre.clientHeight);
  }}

  function scrollTail() {{
    if (stickToBottom) pre.scrollTop = scrollMax();
  }}

  function isAtBottom(el) {{
    return el.scrollHeight - el.clientHeight - el.scrollTop <= BOTTOM_EPS;
  }}

  function syncStickFromScroll() {{
    if (!initialTailDone) return;
    if (SHOW_JUMP) {{
      if (isAtBottom(pre)) {{
        stickToBottom = true;
        sessionStorage.setItem(stickKey, "1");
        sessionStorage.removeItem(scrollKey);
      }} else {{
        stickToBottom = false;
        sessionStorage.setItem(stickKey, "0");
        sessionStorage.setItem(scrollKey, String(pre.scrollTop));
      }}
    }} else {{
      stickToBottom = isAtBottom(pre);
      sessionStorage.setItem(stickKey, stickToBottom ? "1" : "0");
      if (!stickToBottom) sessionStorage.setItem(scrollKey, String(pre.scrollTop));
    }}
  }}

  pre.addEventListener("scroll", syncStickFromScroll, {{ passive: true }});

  if (SHOW_JUMP) {{
    const jb = document.getElementById(JUMP_BTN);
    if (jb) {{
      jb.addEventListener("click", function() {{
        stickToBottom = true;
        sessionStorage.setItem(stickKey, "1");
        sessionStorage.removeItem(scrollKey);
        pre.scrollTop = scrollMax();
      }});
    }}
  }}

  function finishInitialScroll() {{
    initialTailDone = true;
  }}

  if (SHOW_JUMP && RESUME_JH_SCROLL) {{
    const saved = sessionStorage.getItem(scrollKey);
    requestAnimationFrame(function() {{
      requestAnimationFrame(function() {{
        const mx = scrollMax();
        if (stickToBottom) {{
          pre.scrollTop = mx;
        }} else if (saved != null) {{
          const t = parseFloat(saved, 10);
          pre.scrollTop = Math.min(isNaN(t) ? 0 : t, mx);
        }} else {{
          pre.scrollTop = 0;
        }}
        finishInitialScroll();
      }});
    }});
  }} else if (SHOW_JUMP) {{
    try {{ sessionStorage.removeItem(scrollKey); }} catch (e0) {{}}
    requestAnimationFrame(function() {{
      pre.scrollTop = 0;
      requestAnimationFrame(function() {{
        pre.scrollTop = 0;
        finishInitialScroll();
      }});
    }});
  }} else if (!stickToBottom) {{
    const saved = sessionStorage.getItem(scrollKey);
    if (saved != null) {{
      requestAnimationFrame(function() {{
        pre.scrollTop = parseFloat(saved, 10);
        const maxS = scrollMax();
        if (pre.scrollTop > maxS) pre.scrollTop = maxS;
        finishInitialScroll();
      }});
    }} else {{
      finishInitialScroll();
    }}
  }} else {{
    requestAnimationFrame(function() {{
      scrollTail();
      requestAnimationFrame(function() {{
        scrollTail();
        finishInitialScroll();
      }});
    }});
  }}

  function updateText(txt) {{
    if (SHOW_JUMP && !stickToBottom) {{
      const t = pre.scrollTop;
      pre.textContent = txt;
      const nm = scrollMax();
      pre.scrollTop = Math.min(t, nm);
      return;
    }}
    const distFromBottom = pre.scrollHeight - pre.clientHeight - pre.scrollTop;
    pre.textContent = txt;
    if (stickToBottom) {{
      requestAnimationFrame(function() {{
        pre.scrollTop = scrollMax();
      }});
    }} else {{
      const newMax = scrollMax();
      let next = newMax - distFromBottom;
      if (next < 0) next = 0;
      if (next > newMax) next = newMax;
      pre.scrollTop = next;
    }}
  }}

  if (!STATIC) {{
  let pollTimer = null;
  function stopPoll() {{
    if (pollTimer) {{ clearInterval(pollTimer); pollTimer = null; }}
  }}

  function pollOnce() {{
    const url = API + "/api/invocations/" + encodeURIComponent(INV);
    fetch(url, {{ method: "GET", cache: "no-store", mode: "cors", credentials: "omit" }})
      .then(function(r) {{
        if (!r.ok) return Promise.reject(new Error("HTTP " + r.status));
        return r.json();
      }})
      .then(function(data) {{
        const txt = data.live_stdout != null ? String(data.live_stdout) : "";
        if (pre.textContent !== txt) {{
          updateText(txt);
        }} else if (stickToBottom) {{
          requestAnimationFrame(scrollTail);
        }}
        const st = data.status || "";
        if (st === "completed" || st === "failed" || st === "cancelled") stopPoll();
      }})
      .catch(function(err) {{
        if (typeof console !== "undefined" && console.error) console.error("live log poll failed", err);
      }});
  }}

  pollTimer = setInterval(pollOnce, POLL_MS);
  pollOnce();
  }}
}})();
</script>
</body></html>""",
        height=iframe_h,
        scrolling=False,
    )


def _render_live_log_viewer(
    invocation_id: str,
    initial_text: str,
    *,
    scope: Literal["default", "job_history"] = "default",
    jump_to_latest_control: bool = False,
) -> None:
    """Fixed-height live log: browser polls GET /api/invocations/{id} for live_stdout; follow-until-scroll-up."""
    inv = invocation_id.strip()
    if not inv:
        h = _LIVE_LOG_VIEWPORT_HEIGHT_PX
        iframe_h = h + 12
        escaped_initial = html.escape(initial_text)
        components.html(
            f"""<!DOCTYPE html><html><body style="margin:0;padding:0;">
<pre style="box-sizing:border-box;margin:0;width:100%;height:{h}px;max-height:{h}px;overflow:auto;white-space:pre-wrap;word-break:break-word;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:0.75rem;line-height:1.5;background:rgba(49,51,63,0.08);padding:0.5rem 0.75rem;border-radius:0.25rem;">{escaped_initial}</pre>
</body></html>""",
            height=iframe_h,
            scrolling=False,
        )
        return
    _render_log_viewer(
        initial_text,
        storage_key_suffix=inv,
        scope=scope,
        jump_to_latest_control=jump_to_latest_control,
        live_invocation_id=inv,
    )


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
    st.session_state.page = "Run Matrix"
if st.session_state.page == "Solvers":
    st.session_state.page = "Run Matrix"
if st.session_state.page == "Job History":
    st.session_state.page = "Job Activity"
if st.session_state.get("page_radio") == "Run Solvers":
    st.session_state.page_radio = "Run Matrix"
if st.session_state.get("page_radio") == "Solvers":
    st.session_state.page_radio = "Run Matrix"
if st.session_state.get("page_radio") == "Job History":
    st.session_state.page_radio = "Job Activity"
if st.session_state.page == "Run History":
    st.session_state.page = "Job Activity"
if st.session_state.get("page_radio") == "Run History":
    st.session_state.page_radio = "Job Activity"

if "test_result" not in st.session_state:
    st.session_state.test_result = None
if "run_job_results" not in st.session_state:
    st.session_state.run_job_results = None
if "page_change_requested" not in st.session_state:
    st.session_state.page_change_requested = False
if "page_radio" not in st.session_state:
    st.session_state.page_radio = st.session_state.page

# Persistent filter defaults (survive page navigation, reset on browser reload)
st.session_state.setdefault("history-solver", "(all)")
st.session_state.setdefault("history-system", "(all)")
st.session_state.setdefault("heatmap-mode", "All metrics for one solver/system")
st.session_state.setdefault("heatmap-color-mode", "Default (spec / min-max)")
st.session_state.setdefault("heatmap-color-mode-single", "Default (min-max)")

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
    /* ── Main content: wide usable width (Run Matrix, Long-Term Trends, tables) ── */
    .block-container {
        max-height: 95%;
        max-width: 95%;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    /* ── Job Activity / run rows: compact Baseline button on the right; shaded (primary) when set; clearer on hover ── */
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
PAGES = [
    "Home",
    "Run Matrix",
    "Job Activity",
    "Individual Trends",
    "Long-Term Trends",
    "Configs",
]

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
        - **Operate:** submit jobs from **Run Matrix**, watch **Job Activity** (live invocations and stored runs), and inspect stdout/stderr and metrics when they finish.
        - **Understand:** stored runs, **Job Activity** (stored runs), per-solver charts, and long-term trend views support baselines and drift detection.
        - **Configure:** solver, system, and resource definitions live under `configs/` (browse YAML from the sidebar or read `docs/ARCHITECTURE.md`).
        """
    )

    st.markdown(
        "Use the sidebar to navigate to **Run Matrix**, **Job Activity**, and **Trends**."
    )


def _matrix_cell_key(solver_name: str, system_name: str) -> str:
    """Stable session_state key for Run Matrix checkboxes."""
    return f"matrix-cell-{solver_name}-{system_name}".replace(" ", "_")


def _matrix_job_key(solver_name: str, system_name: str) -> str:
    """Harness job identity: solver@system."""
    return f"{solver_name}@{system_name}"


def _matrix_active_by_job_key(active_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Map solver@system -> first matching active invocation (queued/running from API)."""
    out: dict[str, dict[str, Any]] = {}
    for rec in active_rows:
        labels = rec.get("run_labels") or rec.get("job_names") or []
        for label in labels:
            if isinstance(label, str) and "@" in label:
                if label not in out:
                    out[label] = rec
    return out


def _matrix_toggle_row_selection(
    solver_name: str,
    allowed_systems: set[str],
    system_names: list[str],
) -> None:
    """If every allowed cell in the row is checked, clear the row; otherwise select all allowed."""
    keys = [(solver_name, sysn) for sysn in system_names if sysn in allowed_systems]
    if not keys:
        return
    all_on = all(st.session_state.get(_matrix_cell_key(sn, sy), False) for sn, sy in keys)
    new_val = not all_on
    for sn, sy in keys:
        st.session_state[_matrix_cell_key(sn, sy)] = new_val


def _matrix_toggle_column_selection(
    system_name: str,
    solver_names: list[str],
    solver_by_name: dict[str, Any],
) -> None:
    """If every allowed cell in the column is checked, clear the column; otherwise select all allowed."""
    keys: list[tuple[str, str]] = []
    for sn in solver_names:
        allowed = set(solver_by_name[sn].get("allowed_systems") or [])
        if system_name in allowed:
            keys.append((sn, system_name))
    if not keys:
        return
    all_on = all(st.session_state.get(_matrix_cell_key(sn, sy), False) for sn, sy in keys)
    new_val = not all_on
    for sn, sy in keys:
        st.session_state[_matrix_cell_key(sn, sy)] = new_val


def _matrix_cell_help(solver_name: str, system_name: str, inv: dict[str, Any] | None) -> str:
    """Tooltip for matrix checkbox: idle vs active invocation summary."""
    if not inv:
        return f"Run {solver_name} on {system_name}"
    status = (inv.get("status") or "").strip() or "unknown"
    iid = (inv.get("invocation_id") or "")[:12]
    ex = inv.get("execution") or {}
    backend = (ex.get("backend") or "local") if isinstance(ex, dict) else "local"
    lines = [
        f"Active: {status}",
        f"invocation: {iid}…" if iid else "invocation: (pending)",
        f"backend: {backend}",
    ]
    jt = inv.get("jobs_total")
    if jt is not None:
        jc = inv.get("jobs_completed")
        lines.append(f"progress: {jc}/{jt}")
    sj = inv.get("scheduler_job_ids") or []
    if sj:
        short = ", ".join(str(x) for x in sj[:4])
        if len(sj) > 4:
            short += "…"
        lines.append(f"scheduler ids: {short}")
    sess = (inv.get("session_label") or inv.get("batch_name") or "").strip()
    if sess:
        lines.append(f"session: {sess}")
    return "\n".join(lines)


def _run_matrix_preset_key(label: str) -> str:
    """Normalize session label for preset dict lookup (case-insensitive)."""
    return (label or "").strip().lower()


def _matrix_collect_specs_from_state(
    solver_names: list[str],
    system_names: list[str],
    solver_by_name: dict[str, Any],
) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for sn in solver_names:
        allowed = set(solver_by_name[sn].get("allowed_systems") or [])
        for sysn in system_names:
            if sysn in allowed and st.session_state.get(_matrix_cell_key(sn, sysn), False):
                specs.append({"name": sn, "system": sysn})
    return specs


def _apply_run_matrix_preset_pairs(
    pairs: set[tuple[str, str]],
    solver_names: list[str],
    system_names: list[str],
    solver_by_name: dict[str, Any],
) -> None:
    """Set each allowed matrix checkbox True iff (solver, system) is in pairs; else False."""
    for sn in solver_names:
        allowed = set(solver_by_name[sn].get("allowed_systems") or [])
        for sysn in system_names:
            if sysn not in allowed:
                continue
            st.session_state[_matrix_cell_key(sn, sysn)] = (sn, sysn) in pairs


def _matrix_preset_cells_to_pairs(cells: list[Any]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for item in cells:
        if isinstance(item, dict):
            n = (item.get("name") or "").strip()
            s = (item.get("system") or "").strip()
            if n and s:
                pairs.add((n, s))
    return pairs


def _fetch_matrix_presets_list() -> list[dict[str, Any]]:
    try:
        r = requests.get(API_URL + "/api/matrix_presets", timeout=15)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except requests.exceptions.RequestException:
        return []


def _get_matrix_preset_remote(label_key: str) -> dict[str, Any] | None:
    try:
        r = requests.get(
            API_URL + f"/api/matrix_presets/{quote(label_key, safe='')}",
            timeout=15,
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException:
        return None


def _put_matrix_preset_remote(label: str, cells: list[dict[str, Any]]) -> tuple[bool, str]:
    pk = _run_matrix_preset_key(label)
    if not pk:
        return False, "empty label"
    try:
        r = requests.put(
            API_URL + f"/api/matrix_presets/{quote(pk, safe='')}",
            json={"cells": cells},
            timeout=30,
        )
        if r.status_code == 422:
            detail = r.json()
            return False, str(detail.get("detail", r.text))
        r.raise_for_status()
        return True, ""
    except requests.exceptions.RequestException as e:
        return False, str(e)


def _delete_matrix_preset_remote(label: str) -> tuple[bool, str]:
    pk = _run_matrix_preset_key(label)
    if not pk:
        return False, "empty label"
    try:
        r = requests.delete(
            API_URL + f"/api/matrix_presets/{quote(pk, safe='')}",
            timeout=15,
        )
        if r.status_code == 404:
            return False, "not found"
        r.raise_for_status()
        return True, ""
    except requests.exceptions.RequestException as e:
        return False, str(e)


def _matrix_run_layout_effective() -> MatrixRunLayoutTuning:
    """Run Matrix layout: fixed defaults from :data:`DEFAULT_MATRIX_RUN_LAYOUT_TUNING`."""
    return DEFAULT_MATRIX_RUN_LAYOUT_TUNING


def page_run_matrix() -> None:
    """Solver × system grid: select cells and start one background run per cell (solver@system)."""
    _testid("page-run-matrix")
    st.header(
        "Run Matrix",
        help="Pick solver/system pairs. Each checked cell starts one background run (same as API: one job per solver@system).",
    )
    st.caption(
        "Use **Session label** to tag runs (`job_batch_name` / API `session_label`). "
        "Typing a name that matches a saved preset loads it; otherwise that name starts a new session. "
        "Presets persist via **GET/PUT/DELETE /api/matrix_presets** (case-insensitive)."
    )

    solvers: list[dict[str, Any]] = []
    systems: list[dict[str, Any]] = []
    try:
        r1 = requests.get(API_URL + "/api/systems", timeout=15)
        r1.raise_for_status()
        systems = r1.json()
        r2 = requests.get(API_URL + "/api/solvers", timeout=15)
        r2.raise_for_status()
        solvers = r2.json()
    except requests.exceptions.RequestException as e:
        st.error(
            "Cannot reach the HPC Regression API. Start it with `make api` from the project root, "
            "or set `HPC_API_URL` if the API runs elsewhere."
        )
        st.caption(str(e))
        return

    if not solvers or not systems:
        st.warning("Need at least one solver and one system in config.")
        return

    system_names = sorted(s["name"] for s in systems)
    solver_by_name = {s["name"]: s for s in solvers}
    solver_names = sorted(solver_by_name.keys())

    presets_rows = _fetch_matrix_presets_list()
    preset_opts = ["—"] + sorted(
        str(p["label"]).strip() for p in presets_rows if p.get("label")
    )
    # After Run or Save + PUT, we defer updating ``run-matrix-saved-pick`` (can't set after selectbox).
    # Apply here in the main script *before* validation/sync/widgets so ``preset_opts`` is from a fresh
    # list that includes the new preset; otherwise the Saved presets menu snaps back to "—".
    _defer_pk = st.session_state.pop("_run_matrix_defer_saved_pick", None)
    if _defer_pk is not None:
        st.session_state["run-matrix-saved-pick"] = _defer_pk
        st.session_state["_run_matrix_synced_pick"] = _defer_pk
        _row_defer = _get_matrix_preset_remote(_defer_pk)
        if _row_defer:
            st.session_state["run-matrix-session-label"] = str(_row_defer.get("label") or _defer_pk)

    st.session_state.setdefault("run-matrix-saved-pick", "—")
    _rp = st.session_state.get("run-matrix-saved-pick", "—")
    # Don't clear a valid selection when the list fetch failed (only "—" left) or labels are momentarily stale.
    if _rp != "—" and _rp not in preset_opts and len(preset_opts) > 1:
        st.session_state["run-matrix-saved-pick"] = "—"

    def _sync_run_matrix_from_saved_pick(current_pick: str) -> None:
        """Apply matrix + Session label from Saved presets when the dropdown value changes.

        Invoked from the main script and from ``@st.fragment`` (Saved presets is in the fragment;
        fragment-only reruns do not execute the main script, so both paths keep state aligned).
        """
        if current_pick == "—":
            _apply_run_matrix_preset_pairs(set(), solver_names, system_names, solver_by_name)
            st.session_state["run-matrix-session-label"] = ""
            return
        row = _get_matrix_preset_remote(current_pick)
        if row:
            st.session_state["run-matrix-session-label"] = str(row.get("label") or current_pick)
            pairs = _matrix_preset_cells_to_pairs(row.get("cells") or [])
            _apply_run_matrix_preset_pairs(pairs, solver_names, system_names, solver_by_name)
        else:
            st.session_state["run-matrix-session-label"] = current_pick

    current_pick = st.session_state.get("run-matrix-saved-pick", "—")
    if "_run_matrix_synced_pick" not in st.session_state:
        st.session_state["_run_matrix_synced_pick"] = current_pick
        if current_pick != "—":
            _sync_run_matrix_from_saved_pick(current_pick)
    elif current_pick != st.session_state["_run_matrix_synced_pick"]:
        st.session_state["_run_matrix_synced_pick"] = current_pick
        _sync_run_matrix_from_saved_pick(current_pick)

    def _on_session_label_change() -> None:
        raw = (st.session_state.get("run-matrix-session-label") or "").strip()
        pk = _run_matrix_preset_key(raw)
        if not pk:
            st.session_state["run-matrix-saved-pick"] = "—"
            st.session_state["_run_matrix_synced_pick"] = "—"
            return
        row = _get_matrix_preset_remote(pk)
        if row:
            pairs = _matrix_preset_cells_to_pairs(row.get("cells") or [])
            _apply_run_matrix_preset_pairs(pairs, solver_names, system_names, solver_by_name)
            label = str(row.get("label") or pk)
            st.session_state["run-matrix-saved-pick"] = label
            st.session_state["_run_matrix_synced_pick"] = label
        else:
            # GET can fail transiently; don't clear the Saved presets dropdown if it already matches this label.
            cur_sp = st.session_state.get("run-matrix-saved-pick", "—")
            if cur_sp != "—" and _run_matrix_preset_key(cur_sp) == pk:
                return
            st.session_state["run-matrix-saved-pick"] = "—"
            st.session_state["_run_matrix_synced_pick"] = "—"

    st.session_state.setdefault("run-matrix-session-label", "")

    _rm_label_w, _rm_btn_w = 0.72, 0.82
    r1, r2 = st.columns([_rm_label_w, _rm_btn_w])
    with r1:
        st.text_input(
            "Session label (optional)",
            key="run-matrix-session-label",
            on_change=_on_session_label_change,
            help="Matches saved presets by name (case-insensitive). Choosing a **Saved preset** fills this "
            "field so you can Save again, rename (Save as a copy), or edit the matrix and save under the same "
            "or a new label.",
            placeholder="e.g. nightly-smoke",
        )
    # Push column-2 buttons down so they line up with the labeled widget’s control (text field / select).
    _btn_align_labeled_control = '<div style="height:1.72rem" aria-hidden="true"></div>'
    _rm_preset_btn_px = 92
    with r2:
        st.markdown(_btn_align_labeled_control, unsafe_allow_html=True)
        # Skew + nudge Save right: equal columns leave a wide gap after a fixed-width Save.
        c_save, c_del = st.columns([0.34, 0.66], gap="xxsmall")
        with c_save:
            _, save_slot = st.columns([0.18, 0.82], gap="xxsmall")
            with save_slot:
                save_clicked = st.button(
                    "Save",
                    key="run-matrix-save-preset",
                    width=_rm_preset_btn_px,
                    help="Store the current checkbox selection under this session label (PUT /api/matrix_presets).",
                )
        with c_del:
            delete_clicked = st.button(
                "Delete",
                key="run-matrix-delete-preset",
                width=_rm_preset_btn_px,
                help="Remove this preset from the database (DELETE /api/matrix_presets).",
            )

    del_pend = st.session_state.get("run_matrix_preset_delete_pending")
    if del_pend:
        st.warning(f"Delete preset «{del_pend}» from the database?")
        dca, dcb = st.columns(2)
        with dca:
            if st.button("Yes, delete", type="primary", key="run-matrix-del-yes"):
                ok_del, err_del = _delete_matrix_preset_remote(del_pend)
                st.session_state.pop("run_matrix_preset_delete_pending", None)
                if ok_del:
                    if st.session_state.get("run-matrix-saved-pick") == del_pend:
                        st.session_state["run-matrix-saved-pick"] = "—"
                    st.toast(f"Deleted preset «{del_pend}».")
                    st.rerun()
                else:
                    st.error(err_del or "Delete failed.")
        with dcb:
            if st.button("Cancel", key="run-matrix-del-no"):
                st.session_state.pop("run_matrix_preset_delete_pending", None)
                st.rerun()

    if save_clicked:
        sl_in = (st.session_state.get("run-matrix-session-label") or "").strip()
        if not sl_in:
            st.warning("Enter a session label to save the current selection.")
        else:
            specs_cur = _matrix_collect_specs_from_state(
                solver_names, system_names, solver_by_name
            )
            if not specs_cur:
                st.warning("Select at least one cell in the matrix.")
            else:
                ok_sv, err_sv = _put_matrix_preset_remote(sl_in, specs_cur)
                if ok_sv:
                    pk = _run_matrix_preset_key(sl_in)
                    st.session_state["_run_matrix_defer_saved_pick"] = pk
                    st.toast(f"Saved {len(specs_cur)} cell(s) under «{pk}».")
                    st.rerun()
                else:
                    st.error(err_sv or "Save failed.")

    if delete_clicked:
        sl_in = (st.session_state.get("run-matrix-session-label") or "").strip()
        if not sl_in:
            st.warning("Enter a session label to identify which preset to delete.")
        elif not _get_matrix_preset_remote(_run_matrix_preset_key(sl_in)):
            st.warning(f"No saved preset for «{_run_matrix_preset_key(sl_in)}».")
        else:
            st.session_state["run_matrix_preset_delete_pending"] = _run_matrix_preset_key(
                sl_in
            )
            st.rerun()

    @st.fragment(run_every=timedelta(seconds=4))
    def _run_matrix_grid_fragment() -> None:
        active_rows = _fetch_active_invocations_safe()
        active_map = _matrix_active_by_job_key(active_rows)
        _testid("run-matrix-grid")

        st.subheader("Select runs")

        specs: list[dict[str, Any]] = _matrix_collect_specs_from_state(
            solver_names, system_names, solver_by_name
        )
        n_sel = len(specs)
        session_sl = (st.session_state.get("run-matrix-session-label") or "").strip()

        # Same column split as Session label | Save/Delete so the selectbox matches text input width.
        c_presets, c_run = st.columns([_rm_label_w, _rm_btn_w])
        with c_presets:
            st.selectbox(
                "Saved presets",
                options=preset_opts,
                key="run-matrix-saved-pick",
                help="Pick a saved label to load its cells. Choose «—» to clear all checkboxes and the session label.",
            )
        with c_run:
            st.markdown(_btn_align_labeled_control, unsafe_allow_html=True)
            run_go = st.button(
                f"Run selected ({n_sel})",
                type="primary",
                key="run-matrix-go",
                disabled=n_sel == 0,
            )

        # Run after the selectbox so ``run-matrix-saved-pick`` reflects this interaction. Fragment-only
        # reruns skip the main script; ``st.rerun()`` here (not in a widget callback) refreshes Session label.
        _pick = st.session_state.get("run-matrix-saved-pick", "—")
        if _pick != st.session_state.get("_run_matrix_synced_pick"):
            st.session_state["_run_matrix_synced_pick"] = _pick
            _sync_run_matrix_from_saved_pick(_pick)
            st.rerun()

        ml = _matrix_run_layout_effective()
        st.markdown(
            matrix_grid_control_css(DEFAULT_MATRIX_GRID_CONTROL_STYLE, layout=ml),
            unsafe_allow_html=True,
        )
        with st.container(key="run_matrix_tuning_shell"):
            # Column weights: see ``MatrixRunLayoutTuning`` in matrix_grid_style.
            col_weights = [ml.solver_col_weight] + [ml.system_col_weight] * len(system_names)
            # Two header rows: (1) system names only, (2) column ↕ only — same [0.28,0.72] + MATRIX_INNER_BAND
            # as body rows so Streamlit column widths match checkboxes/dashes (see matrix_grid_style).
            head_names = st.columns(col_weights)
            with head_names[0]:
                sp, lab = st.columns([0.42, 1.85])
                with sp:
                    st.markdown("")
                with lab:
                    st.caption("Solver")
            for i, sysn in enumerate(system_names):
                with head_names[i + 1]:
                    h_dot, h_chk = st.columns([0.28, 0.72])
                    with h_dot:
                        st.markdown("")
                    with h_chk:
                        st.markdown(
                            "<div class='matrix-header-system' style='text-align:center;font-size:0.85rem;line-height:1'>"
                            f"<b>{html.escape(sysn)}</b></div>",
                            unsafe_allow_html=True,
                        )
            head_toggles = st.columns(col_weights)
            with head_toggles[0]:
                cbtn, cname = st.columns([0.42, 1.85])
                with cbtn:
                    _, row_head_spacer, _ = st.columns(MATRIX_INNER_BAND)
                    with row_head_spacer:
                        st.markdown("")
                with cname:
                    st.markdown("")
            for i, sysn in enumerate(system_names):
                with head_toggles[i + 1]:
                    h_dot, h_chk = st.columns([0.28, 0.72])
                    with h_dot:
                        st.markdown("")
                    with h_chk:
                        _, col_btn, _ = st.columns(MATRIX_INNER_BAND)
                        with col_btn:
                            if st.button(
                                "↕",
                                key=f"matrix-col-toggle-{sysn}",
                                help=f"Toggle column {sysn}: select all allowed cells or clear",
                                width=DEFAULT_MATRIX_GRID_CONTROL_STYLE.toggle_width_px,
                            ):
                                _matrix_toggle_column_selection(sysn, solver_names, solver_by_name)
                                st.rerun()

            for sn in solver_names:
                allowed = set(solver_by_name[sn].get("allowed_systems") or [])
                row = st.columns(col_weights)
                with row[0]:
                    cbtn, cname = st.columns([0.42, 1.85])
                    with cbtn:
                        _, row_btn, _ = st.columns(MATRIX_INNER_BAND)
                        with row_btn:
                            if st.button(
                                "↔",
                                key=f"matrix-row-toggle-{sn}",
                                help="Toggle row: select all allowed systems for this solver or clear",
                                width=DEFAULT_MATRIX_GRID_CONTROL_STYLE.toggle_width_px,
                            ):
                                _matrix_toggle_row_selection(sn, allowed, system_names)
                                st.rerun()
                    with cname:
                        st.markdown(
                            f'<span class="matrix-solver-name"><code>{html.escape(sn)}</code></span>',
                            unsafe_allow_html=True,
                        )
                for i, sysn in enumerate(system_names):
                    with row[i + 1]:
                        if sysn not in allowed:
                            d_left, d_right = st.columns([0.28, 0.72])
                            with d_left:
                                st.markdown("")
                            with d_right:
                                pad_l, dash_mid, pad_r = st.columns(MATRIX_INNER_BAND)
                                with pad_l:
                                    st.markdown("")
                                with dash_mid:
                                    st.markdown(
                                        '<div class="matrix-dash-cell">—</div>',
                                        unsafe_allow_html=True,
                                    )
                                with pad_r:
                                    st.markdown("")
                        else:
                            jk = _matrix_job_key(sn, sysn)
                            inv = active_map.get(jk)
                            help_txt = _matrix_cell_help(sn, sysn, inv)
                            dot, chk = st.columns([0.28, 0.72])
                            with dot:
                                st.markdown("")
                            with chk:
                                pad_l, chk_mid, pad_r = st.columns(MATRIX_INNER_BAND)
                                with pad_l:
                                    st.markdown("")
                                with chk_mid:
                                    st.checkbox(
                                        "run",
                                        key=_matrix_cell_key(sn, sysn),
                                        label_visibility="collapsed",
                                        help=help_txt,
                                    )
                                with pad_r:
                                    if inv:
                                        st.markdown(
                                            '<span class="matrix-active-dot" title="Active run">●</span>',
                                            unsafe_allow_html=True,
                                        )
                                    else:
                                        st.markdown("")

            if run_go and specs:
                with st.spinner(f"Starting {len(specs)} background run(s)…"):
                    ok = _post_run_solvers(
                        specs,
                        session_sl,
                        success_note=(
                            f"Started {len(specs)} background run(s) (one per solver@system). "
                            "See **Job Activity** for live status and logs."
                        ),
                    )
                if ok:
                    if session_sl:
                        ok_pr, _ = _put_matrix_preset_remote(session_sl, specs)
                        if ok_pr:
                            st.session_state["_run_matrix_defer_saved_pick"] = _run_matrix_preset_key(
                                session_sl
                            )
                    st.rerun()

    _run_matrix_grid_fragment()


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
        st.info("No metrics data yet. Run solvers from **Run Matrix** or the CLI to collect metrics.")
        return

    options = [f"{dictionary['solver']} / {dictionary['metric']}" for dictionary in available]
    st.session_state.setdefault("home-metric-select", options[0])
    if st.session_state["home-metric-select"] not in options:
        st.session_state["home-metric-select"] = options[0]
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


def page_job_activity() -> None:
    _testid("page-job-activity")
    st.header("Job Activity")
    st.caption(
        "Choose one job below. **Live invocations** (⏳ queued · 🏃 running · …) are in-memory "
        "(tail when queued/running). **Stored runs** (✅ ❌ ⚠️) are from the database. "
        "**Filter by solver** and **Filter by system** apply to both."
    )

    st.caption(
        "The list reloads on each interaction (filters, **Job** selection). "
        "Submit new runs from **Run Matrix**."
    )

    inv_list: list[dict[str, Any]] = []
    try:
        inv_rows = requests.get(API_URL + "/api/invocations", timeout=30)
        inv_rows.raise_for_status()
        inv_list = inv_rows.json()
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not load invocations: {e}")

    runs_all: list[dict[str, Any]] = []
    try:
        runs_all = requests.get(API_URL + "/api/runs", timeout=30).json()
    except requests.exceptions.RequestException as e:
        st.error(f"API unavailable: {e}")
        return

    solver_names: set[str] = set()
    if runs_all:
        solver_names |= {r["solver_name"] for r in runs_all if r.get("solver_name")}
    for rec in inv_list:
        sn = (rec.get("solver_name") or "").strip()
        if sn:
            solver_names.add(sn)
    solvers = sorted(solver_names)

    system_names: set[str] = set()
    if runs_all:
        system_names |= {r.get("system_name") or "unknown" for r in runs_all}
    for rec in inv_list:
        system_names |= _jh_system_names_for_inv_option_list(rec)
    systems = sorted(system_names)

    _solver_opts = ["(all)"] + solvers
    _system_opts = ["(all)"] + systems
    if st.session_state.get("job-history-solver") not in _solver_opts:
        st.session_state["job-history-solver"] = "(all)"
    if st.session_state.get("job-history-system") not in _system_opts:
        st.session_state["job-history-system"] = "(all)"
    fc1, fc2 = st.columns(2)
    with fc1:
        solver_filter = st.selectbox("Filter by solver", _solver_opts, key="job-history-solver")
    with fc2:
        system_filter = st.selectbox("Filter by system", _system_opts, key="job-history-system")
    running_only = st.checkbox(
        "Running jobs only",
        key="job-history-running-only",
        help="Show only queued or running invocations. Stored (completed) runs are hidden.",
    )

    solver_arg = solver_filter if solver_filter != "(all)" else None
    system_arg = system_filter if system_filter != "(all)" else None
    params = {"solver": solver_arg, "system": system_arg}
    try:
        filtered = requests.get(API_URL + "/api/runs", params=params, timeout=30).json()
    except requests.exceptions.RequestException as e:
        st.error(f"API unavailable: {e}")
        return

    def _sort_key_ts(r: dict[str, Any]) -> str:
        return (r.get("timestamp") or "")[:32]

    inv_sorted = sorted(
        inv_list,
        key=lambda r: ((r.get("solver_name") or ""), r.get("invocation_id") or ""),
    )
    inv_filtered = [
        rec
        for rec in inv_sorted
        if _jh_invocation_matches_filters(rec, solver_filter=solver_filter, system_filter=system_filter)
    ]
    if running_only:
        inv_filtered = [
            rec
            for rec in inv_filtered
            if (rec.get("status") or "").strip().lower() in ("queued", "running")
        ]
    filtered_sorted = sorted(filtered, key=_sort_key_ts, reverse=True)
    runs_for_list = [] if running_only else filtered_sorted

    option_keys: list[str] = []
    labels: dict[str, str] = {}
    run_ids_in_filtered = {int(r["id"]) for r in runs_for_list if r.get("id") is not None}
    inv_shown = 0
    for rec in inv_filtered:
        iid = (rec.get("invocation_id") or "").strip()
        if not iid:
            continue
        st_ = (rec.get("status") or "").strip().lower()
        if st_ in ("completed", "failed", "cancelled"):
            match = _match_stored_run_for_invocation(rec, runs_all)
            if match is not None and match.get("id") is not None:
                if int(match["id"]) in run_ids_in_filtered:
                    # Same job is already listed as a stored run; omit duplicate inv: row.
                    continue
        k = f"inv:{iid}"
        option_keys.append(k)
        labels[k] = _jh_invocation_select_label(rec)
        inv_shown += 1
    for r in runs_for_list:
        rid = r.get("id")
        if rid is None:
            continue
        k = f"run:{int(rid)}"
        option_keys.append(k)
        labels[k] = _jh_stored_row_label(r)

    st.write(
        f"**Jobs (this filter):** {inv_shown} live invocation(s), "
        f"{len(runs_for_list)} stored run(s) (newest first)."
        + (" **Running only** — finished runs are hidden." if running_only else "")
    )

    _apply_jh_inv_to_stored_switch(runs_all)
    pr_pre = st.session_state.pop("jh_preselect_run_id", None)
    if pr_pre is not None:
        st.session_state["job-history-unified-pick"] = f"run:{int(pr_pre)}"

    _pick_defer = st.session_state.pop("jh_defer_job_history_pick", None)
    if _pick_defer == _JH_DEFER_PICK_CLEAR:
        st.session_state.pop("job-history-unified-pick", None)
    elif isinstance(_pick_defer, str):
        st.session_state["job-history-unified-pick"] = _pick_defer

    if not option_keys:
        st.session_state.pop("job-history-unified-pick", None)
        st.info(
            "No jobs to show: no invocations in memory, no stored runs (or none match the filters). "
            "Start a background run from **Run Matrix**, or widen filters."
        )
        return

    pick_cur = st.session_state.get("job-history-unified-pick")
    if pick_cur not in option_keys:
        st.session_state["job-history-unified-pick"] = option_keys[0]

    sel = st.selectbox(
        "Job",
        option_keys,
        format_func=lambda k: labels[k],
        key="job-history-unified-pick",
    )

    if sel.startswith("inv:"):
        iid = sel[4:].strip()
        if not iid:
            st.warning("Invalid invocation selection.")
            return

        st.session_state.pop("ja_pending_delete_run_id", None)

        try:
            detail = requests.get(API_URL + f"/api/invocations/{iid}", timeout=30)
            detail.raise_for_status()
            inv = detail.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Could not load invocation: {e}")
            return

        status = (inv.get("status") or "").strip()
        jc = inv.get("jobs_completed", 0)
        jt = inv.get("jobs_total", 0)

        if status in ("queued", "running"):
            _jh_invocation_completion_poller(iid, runs_all)
            st.markdown(f"**Status:** `{status}` · **Jobs:** {jc}/{jt}")
            err = inv.get("error")
            if err:
                st.warning(str(err))

            ex = inv.get("execution") or {}
            if isinstance(ex, dict) and ex.get("backend"):
                st.caption(f"Backend: `{ex.get('backend')}`")

            live_out = inv.get("live_stdout") or ""
            st.subheader("stdout")
            st.caption(_JOB_HISTORY_LOG_CAPTION)
            _render_live_log_viewer(
                iid,
                live_out if isinstance(live_out, str) else "",
                scope="job_history",
                jump_to_latest_control=True,
            )
            if st.button("Cancel invocation", key=f"job-history-cancel-{iid}", type="secondary"):
                try:
                    cresp = requests.post(API_URL + f"/api/invocations/{iid}/cancel", timeout=30)
                    st.json(cresp.json())
                except requests.exceptions.RequestException as ex:
                    st.error(str(ex))
        else:
            match = _match_stored_run_for_invocation(inv, runs_all)
            if match is not None and match.get("id") is not None:
                # Race: run row appeared after _apply_jh_inv_to_stored_switch; defer switch to next run (do not set job-history-unified-pick after selectbox).
                rid = int(match["id"])
                st.session_state["jh_pending_switch_to_stored"] = {"run_id": rid, "invocation_id": iid}
                st.rerun()
                return
            st.markdown(f"**Status:** `{status}` · **Jobs:** {jc}/{jt}")
            err = inv.get("error")
            if err:
                st.warning(str(err))

            ex = inv.get("execution") or {}
            if isinstance(ex, dict) and ex.get("backend"):
                st.caption(f"Backend: `{ex.get('backend')}`")

            live_out = inv.get("live_stdout") or ""
            st.caption("_Live subprocess output is cleared after the run finishes._")
            if inv.get("results") is not None:
                st.subheader("Results")
                st.json(inv.get("results"))
            elif live_out:
                st.subheader("stdout (snapshot)")
                st.caption(_JOB_HISTORY_LOG_CAPTION)
                _render_log_viewer(
                    live_out if isinstance(live_out, str) else str(live_out),
                    storage_key_suffix=f"inv{iid}_snapshot",
                    scope="job_history",
                    jump_to_latest_control=True,
                    live_invocation_id=None,
                )
    elif sel.startswith("run:"):
        pick_id = int(sel[4:])
        row = next((x for x in runs_all if int(x.get("id", -1)) == pick_id), None)
        if row is None:
            st.error(f"Run id {pick_id} not found.")
            return

        pend_del = st.session_state.get("ja_pending_delete_run_id")
        if pend_del is not None and pend_del != pick_id:
            st.session_state.pop("ja_pending_delete_run_id", None)

        col_run_title, col_run_baseline, col_run_delete = st.columns([4, 1, 1])
        with col_run_title:
            st.markdown(f"**Run id** `{pick_id}` · **{row.get('job_name')}** · {(row.get('timestamp') or '')[:19]}")
        rid_btn = row.get("id")
        with col_run_baseline:
            if rid_btn is not None:
                if row.get("is_baseline", False):
                    st.button(
                        "Baseline",
                        key=f"ja-baseline-current-{rid_btn}",
                        type="primary",
                        disabled=True,
                        help="This run is the current baseline",
                    )
                else:
                    if st.button(
                        "Baseline",
                        key=f"ja-baseline-set-{rid_btn}",
                        help="Set this run as the baseline for comparison",
                    ):
                        try:
                            resp = requests.post(API_URL + f"/api/runs/{rid_btn}/set_baseline")
                            if resp.status_code == 200:
                                st.success("Baseline set.")
                                st.rerun()
                            else:
                                st.error(resp.text or f"Error {resp.status_code}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Request failed: {e}")
        with col_run_delete:
            if rid_btn is not None:
                rid_int = int(rid_btn)
                if st.session_state.get("ja_pending_delete_run_id") == rid_int:
                    st.warning("Delete this run permanently from the database?")
                    dca, dcb = st.columns(2)
                    with dca:
                        if st.button("Yes, delete", type="primary", key=f"ja-delete-yes-{rid_int}"):
                            try:
                                dresp = requests.delete(
                                    API_URL + "/api/runs",
                                    json={"ids": [rid_int]},
                                    timeout=30,
                                )
                                if dresp.status_code == 200:
                                    st.success(
                                        f"Deleted {dresp.json().get('deleted', '?')} run(s)."
                                    )
                                    st.session_state.pop("ja_pending_delete_run_id", None)
                                    remain = [k for k in option_keys if k != f"run:{pick_id}"]
                                    if remain:
                                        st.session_state["jh_defer_job_history_pick"] = remain[0]
                                    else:
                                        st.session_state["jh_defer_job_history_pick"] = (
                                            _JH_DEFER_PICK_CLEAR
                                        )
                                    st.rerun()
                                else:
                                    st.error(dresp.text or str(dresp.status_code))
                            except requests.exceptions.RequestException as e:
                                st.error(f"Request failed: {e}")
                    with dcb:
                        if st.button("Cancel", key=f"ja-delete-no-{rid_int}"):
                            st.session_state.pop("ja_pending_delete_run_id", None)
                            st.rerun()
                else:
                    if st.button(
                        "Delete",
                        type="secondary",
                        key=f"ja-delete-req-{rid_int}",
                        help="Remove this stored run from the database",
                    ):
                        st.session_state["ja_pending_delete_run_id"] = rid_int
                        st.rerun()
        hh = st.session_state.pop("jh_log_key_handoff", None)
        stdout_key_suffix: str | None = None
        if isinstance(hh, dict) and int(hh.get("run_id", -1)) == pick_id:
            stdout_key_suffix = (hh.get("invocation_id") or "").strip() or None
        _render_run_record_detail_body(
            row,
            key_prefix="job-history-stored",
            show_session_meta=True,
            job_history_log_viewer=True,
            job_history_stdout_key_suffix=stdout_key_suffix,
        )


def _render_run_record_detail_body(
    r: dict[str, Any],
    *,
    key_prefix: str,
    show_session_meta: bool = False,
    code_height: int | None = None,
    job_history_log_viewer: bool = False,
    job_history_stdout_key_suffix: str | None = None,
) -> None:
    """Stdout, stderr, metrics, validation errors, optional SLURM refresh (Job Activity stored runs)."""
    run_id = r.get("id")
    if show_session_meta:
        bn = (r.get("job_batch_name") or "").strip()
        bu = (r.get("job_batch_uuid") or "").strip()
        if bn or bu:
            meta = []
            if bn:
                meta.append(f"Session label: `{bn}`")
            if bu:
                meta.append(f"Batch uuid: `{bu}`")
            st.caption(" · ".join(meta))
    st.write(
        f"**Solver:** {r['solver_name']} | **System:** {r['system_name']} | **Returncode:** {r.get('returncode')} "
        f"| **Runtime:** {r.get('runtime_seconds')}s"
    )
    if r.get("stdout"):
        st.subheader("stdout")
        if job_history_log_viewer and run_id is not None:
            st.caption(_JOB_HISTORY_LOG_CAPTION)
            out_key = job_history_stdout_key_suffix or f"run{run_id}_stdout"
            _render_log_viewer(
                r["stdout"] if isinstance(r["stdout"], str) else str(r["stdout"]),
                storage_key_suffix=out_key,
                scope="job_history",
                jump_to_latest_control=True,
                live_invocation_id=None,
                resume_job_history_session_scroll=bool(job_history_stdout_key_suffix),
            )
        elif code_height is not None:
            st.code(r["stdout"], language="text", height=code_height)
        else:
            st.code(r["stdout"], language="text")
    if r.get("stderr"):
        st.subheader("stderr")
        if job_history_log_viewer and run_id is not None:
            st.caption(_JOB_HISTORY_LOG_CAPTION)
            err_key = (
                f"{job_history_stdout_key_suffix}_stderr"
                if job_history_stdout_key_suffix
                else f"run{run_id}_stderr"
            )
            _render_log_viewer(
                r["stderr"] if isinstance(r["stderr"], str) else str(r["stderr"]),
                storage_key_suffix=err_key,
                scope="job_history",
                jump_to_latest_control=True,
                live_invocation_id=None,
            )
        elif code_height is not None:
            st.code(r["stderr"], language="text", height=code_height)
        else:
            st.code(r["stderr"], language="text")
    if r.get("metrics_json"):
        st.subheader("Metrics")
        raw_m = r["metrics_json"]
        try:
            metrics_text = json.dumps(
                json.loads(raw_m), indent=2, ensure_ascii=False
            )
        except (json.JSONDecodeError, TypeError):
            metrics_text = str(raw_m)
        if run_id is not None:
            if job_history_log_viewer:
                mkey = (
                    f"{job_history_stdout_key_suffix}_metrics"
                    if job_history_stdout_key_suffix
                    else f"run{run_id}_metrics"
                )
                _render_log_viewer(
                    metrics_text,
                    storage_key_suffix=mkey,
                    scope="job_history",
                    jump_to_latest_control=True,
                    live_invocation_id=None,
                )
            else:
                _render_log_viewer(
                    metrics_text,
                    storage_key_suffix=f"{key_prefix}_{run_id}_metrics",
                    scope="default",
                    jump_to_latest_control=True,
                    live_invocation_id=None,
                )
        else:
            st.text(metrics_text)
    raw_errors = r.get("validation_errors")
    if raw_errors and raw_errors != "[]":
        st.subheader("Validation Errors")
        if isinstance(raw_errors, str):
            try:
                val_text = json.dumps(
                    json.loads(raw_errors), indent=2, ensure_ascii=False
                )
            except json.JSONDecodeError:
                val_text = raw_errors
        else:
            val_text = json.dumps(raw_errors, indent=2, ensure_ascii=False)
        if run_id is not None:
            if job_history_log_viewer:
                vkey = (
                    f"{job_history_stdout_key_suffix}_validation"
                    if job_history_stdout_key_suffix
                    else f"run{run_id}_validation"
                )
                _render_log_viewer(
                    val_text,
                    storage_key_suffix=vkey,
                    scope="job_history",
                    jump_to_latest_control=True,
                    live_invocation_id=None,
                )
            else:
                _render_log_viewer(
                    val_text,
                    storage_key_suffix=f"{key_prefix}_{run_id}_validation",
                    scope="default",
                    jump_to_latest_control=True,
                    live_invocation_id=None,
                )
        else:
            st.text(val_text)
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
        snap_key = f"{key_prefix}_slurm_snap_{run_id}"
        if st.button("Refresh SLURM status", key=f"{key_prefix}-slurm-refresh-{run_id}"):
            try:
                sresp = requests.get(
                    API_URL + f"/api/runs/{run_id}/slurm_status",
                    timeout=120,
                )
                st.session_state[snap_key] = sresp.json()
            except requests.exceptions.RequestException as e:
                st.session_state[snap_key] = {"message": str(e)}
        snap = st.session_state.get(snap_key)
        if snap:
            st.code(json.dumps(snap, indent=2), language="json")

# ---------------------------------------------------------------------------
# POST /api/run_solvers (background) — used by Run Matrix
# ---------------------------------------------------------------------------

def _post_run_solvers(
    specs: list[dict[str, Any]],
    session_label_input: str,
    *,
    success_note: str | None = None,
) -> bool:
    """
    POST run_solvers with background=True (queued invocations). Returns True after session updates on 202.
    """
    payload: dict[str, Any] = {"solvers": specs, "background": True}
    sl = (session_label_input or "").strip()
    if sl:
        payload["session_label"] = sl
    endpoint = API_URL + "/api/run_solvers"
    try:
        response = requests.post(endpoint, json=payload, timeout=60)
        response.raise_for_status()
        if response.status_code != 202:
            st.error(f"Expected 202 from run_solvers with background; got {response.status_code}.")
            return False
        data = response.json()
        invs = data.get("invocations") or []
        inv_top = data.get("invocation_id") or (invs[0].get("invocation_id", "") if invs else "")
        n = len(invs)
        if success_note:
            st.success(success_note)
        elif n > 1:
            st.success(
                f"Started {n} background invocation(s). Open **Job Activity** to monitor and inspect results."
            )
        else:
            st.success(
                f"Background invocation started: `{inv_top}` — open **Job Activity** for live status and logs."
            )
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Run request failed: {e}")
        st.caption(f"API: `{API_URL}` — ensure the API is running and reachable.")
    except Exception as e:
        st.error(f"Unexpected error while running solvers: {e}")
    return False


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
def _global_run_notifier_fragment() -> None:
    """Polls active invocations on every page; fires toast notifications when runs finish."""
    rows = _fetch_active_invocations_safe()
    sig = _active_invocation_sig(rows)
    prev = st.session_state.get("_notifier_sig")
    prev_info: dict[str, dict] = st.session_state.get("_notifier_inv_info", {})

    curr_info: dict[str, dict] = {
        r["invocation_id"]: {
            "solver_name": (r.get("solver_name") or "(unknown)"),
            "batch_name": (r.get("batch_name") or "").strip(),
        }
        for r in rows
    }

    if prev is not None and prev != sig:
        finished_ids = set(prev) - set(sig)
        if finished_ids:
            still_active_batches = {
                info["batch_name"]
                for info in curr_info.values()
                if info["batch_name"]
            }
            pending: list[str] = st.session_state.setdefault("_pending_toasts", [])
            batches_finished: dict[str, list[str]] = {}
            for iid in finished_ids:
                info = prev_info.get(iid, {})
                bname = info.get("batch_name") or ""
                sname = info.get("solver_name") or "(unknown)"
                if bname:
                    batches_finished.setdefault(bname, []).append(sname)
                else:
                    pending.append(f"\u2705 **{sname}** finished \u2014 view results in Job Activity.")
            for bname in batches_finished:
                if bname not in still_active_batches:
                    pending.append(f"\u2705 Batch **{bname}** finished \u2014 view results in Job Activity.")
        st.session_state["_notifier_inv_info"] = curr_info
        st.session_state["_notifier_sig"] = sig
        st.rerun()

    st.session_state["_notifier_inv_info"] = curr_info
    st.session_state["_notifier_sig"] = sig


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

    _cat_opts = sorted(by_category.keys())
    st.session_state.setdefault("config-category", _cat_opts[0])
    if st.session_state["config-category"] not in _cat_opts:
        st.session_state["config-category"] = _cat_opts[0]
    category = st.selectbox(
        "Category",
        options=_cat_opts,
        key="config-category",
    )
    files_in_cat = by_category[category]
    if st.session_state.get("config-file") not in files_in_cat:
        st.session_state["config-file"] = files_in_cat[0] if files_in_cat else None
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

    df_all = get_trend_runs_data(str(DB_PATH))

    if df_all.empty:
        st.info("No run data available yet. Run solvers from **Run Matrix** or the CLI to collect data.")
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

    tab_heatmap, tab_metric_trends = st.tabs(["Heatmap", "Metric trends"])

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
                if st.session_state.get("heatmap-all-metrics-solver-pick") not in selected_solvers:
                    st.session_state["heatmap-all-metrics-solver-pick"] = selected_solvers[0]
                solver_pick = st.selectbox(
                    "Solver (for all-metrics heatmap)",
                    options=selected_solvers,
                    key="heatmap-all-metrics-solver-pick",
                )
            if len(selected_systems) > 1:
                if st.session_state.get("heatmap-all-metrics-system-pick") not in selected_systems:
                    st.session_state["heatmap-all-metrics-system-pick"] = selected_systems[0]
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
                        st.info("No baseline metrics available. Set a baseline in Job Activity or enter manual values above.")
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
                if st.session_state.get("heatmap-metric-select") not in available_metrics_hm:
                    st.session_state["heatmap-metric-select"] = available_metrics_hm[0]
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
                    metric_dictionary = {}
                elif selected_hm_metric == "runtime_seconds":
                    metric_dictionary = {
                        "python-solver": (0.0, 1.05),
                        "echo-solver": (0.0, 0.01),
                        "cpuinfo-solver": (0.0, 0.01),
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
                            "No baseline values available. Set baselines in Job Activity or enter manual values above."
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
    with tab_metric_trends:
        _testid("section-metric-trend")
        numeric_names = list_numeric_metric_names(df_filtered)
        if not numeric_names:
            st.info(
                "No numeric metrics in stored runs for the current filters. "
                "Charts only include int/float values from collected solver output "
                "(see each solver's parser_config)."
            )
        else:
            default_metric = (
                "runtime_seconds"
                if "runtime_seconds" in numeric_names
                else numeric_names[0]
            )
            selected_metric = st.selectbox(
                "Metric",
                options=numeric_names,
                index=numeric_names.index(default_metric),
                key="trend-metric-select",
                help="Options are derived from metrics present in runs (parser output).",
            )
            df_metric = build_metric_trend_frame(df_filtered, selected_metric)
            render_numeric_metric_trend(df_metric, selected_metric, st.session_state)


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


def _run_id_from_trend_chart_point(point: dict[str, Any]) -> int | None:
    """Map a Plotly chart selection (trends) to a stored run id for Job Activity preselection."""
    x = point.get("x")
    if x is None:
        return None
    s = str(x).strip()
    if "T" not in s and " " in s:
        s = s.replace(" ", "T", 1)
    target_prefix = s.split(".")[0][:19]
    try:
        rows = requests.get(API_URL + "/api/runs", params={"limit": 500}, timeout=30).json()
    except requests.exceptions.RequestException:
        return None
    candidates: list[tuple[int, dict[str, Any]]] = []
    for r in rows:
        rid = r.get("id")
        ts = r.get("timestamp") or ""
        if rid is None or not ts:
            continue
        ts_n = ts.replace(" ", "T", 1).split(".")[0][:19]
        if ts_n == target_prefix:
            candidates.append((int(rid), r))
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0][0]
    series_hint = (
        point.get("label")
        or point.get("text")
        or (point.get("fullData") or {}).get("name")
    )
    if series_hint:
        sh = str(series_hint).strip()
        for rid, r in candidates:
            jn = (r.get("job_name") or "").strip()
            if jn and (jn == sh or sh in jn):
                return rid
            combo = f"{r.get('solver_name', '')}@{r.get('system_name', '')}"
            if combo in sh or sh in combo:
                return rid
    return candidates[0][0]

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

# Global run-completion notifier — runs on every page so users are notified
# regardless of which page they are currently viewing.
_global_run_notifier_fragment()

# Drain any toast messages queued by the notifier fragment
_pending_toasts: list[str] = st.session_state.pop("_pending_toasts", [])
for _toast_msg in _pending_toasts:
    st.toast(_toast_msg)

if st.session_state.page == "Home":
    page_home()
elif st.session_state.page == "Run Matrix":
    page_run_matrix()
elif st.session_state.page == "Job Activity":
    if "clicked_point" in st.session_state:
        pt = st.session_state.pop("clicked_point")
        rid_go = _run_id_from_trend_chart_point(pt)
        if rid_go is not None:
            st.session_state["jh_preselect_run_id"] = rid_go
    page_job_activity()
elif st.session_state.page == "Individual Trends":
    page_individual_trends()
elif st.session_state.page == "Long-Term Trends":
    page_long_term_trends()
#elif st.session_state.page == "Tests":
#    page_tests()
elif st.session_state.page == "Configs":
    page_configs()
