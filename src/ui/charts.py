"""Chart rendering functions for the Streamlit UI."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
import json
import numpy as np
import requests
import plotly.graph_objects as go
from typing import Any

API_URL = "http://localhost:8000"


def render_manual_baseline_overrides(
    *,
    item_labels: list[str],
    defaults: dict[str, float],
    key_prefix: str,
    caption_text: str,
    input_help: str,
) -> dict[str, float]:
    """
    Render manual baseline inputs and return positive numeric overrides.
    Keys are persisted in Streamlit session state via key_prefix.
    """
    with st.expander("Manual baseline overrides (optional)", expanded=False):
        st.caption(caption_text)
        for label in item_labels:
            default = defaults.get(label, 0.0)
            st.number_input(
                label,
                value=default,
                min_value=0.0,
                format="%g",
                key=f"{key_prefix}_{label}",
                help=input_help.format(label=label),
            )
    overrides = {
        label: st.session_state.get(
            f"{key_prefix}_{label}",
            defaults.get(label, 0.0),
        )
        for label in item_labels
    }
    return {
        k: float(v)
        for k, v in overrides.items()
        if isinstance(v, (int, float)) and float(v) > 0
    }


def render_single_solver_runs_vs_baseline(
    *,
    solver_name: str,
    baseline_metrics: dict[str, float],
    baseline_comparison_data: list[dict[str, Any]],
) -> None:
    """Render comparison table for one solver heatmap baseline mode."""
    with st.expander("Runs vs baseline", expanded=False):
        entry = next(
            (e for e in baseline_comparison_data if e.get("solver_name") == solver_name),
            None,
        )
        if not entry:
            st.caption("No comparison data for this solver.")
            return

        comparisons_list = entry.get("comparisons") or []
        if not comparisons_list:
            st.caption("No other runs to compare for this solver.")
            return

        metric_options = sorted({
            k for c in comparisons_list for k in (c.get("vs_baseline") or {}).keys()
        })
        metric_options = [m for m in metric_options if m in baseline_metrics]
        if not metric_options:
            st.caption("No comparable metrics found for this solver.")
            return

        selected_metric = st.selectbox(
            "Metric",
            options=metric_options,
            key=f"comparison_metric_single_{solver_name}",
        )

        rows = []
        for comp in comparisons_list:
            row = {
                "Run ID": comp.get("run_id"),
                "Job": comp.get("job_name"),
                "Timestamp": comp.get("timestamp", ""),
            }
            v = (comp.get("vs_baseline") or {}).get(selected_metric)
            if v is not None:
                base_val = v.get("baseline")
                cur_val = v.get("value")
                row["baseline"] = base_val
                row["value"] = cur_val
                if (
                    isinstance(base_val, (int, float))
                    and base_val != 0
                    and isinstance(cur_val, (int, float))
                ):
                    row["× baseline"] = f"{(float(cur_val) / float(base_val)):.2f}×"
                else:
                    row["× baseline"] = ""
                row["Δ"] = v.get("delta")
                pct = v.get("delta_pct")
                row["Δ%"] = f"{pct:.1f}%" if pct is not None else ""
            else:
                row["baseline"] = ""
                row["value"] = ""
                row["× baseline"] = ""
                row["Δ"] = ""
                row["Δ%"] = ""
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_multi_solver_runs_vs_baseline(
    *,
    metric_name: str,
    baseline_values: dict[str, float],
    baseline_comparison_data: list[dict[str, Any]],
) -> None:
    """Render comparison table for multi-solver heatmap baseline mode."""
    with st.expander("Runs vs baseline", expanded=False):
        valid_entries = [
            e for e in baseline_comparison_data
            if e.get("solver_name") in baseline_values
            and e.get("baseline_run")
            and (e.get("comparisons") or [])
        ]
        solver_options = sorted([e["solver_name"] for e in valid_entries])
        if not solver_options:
            st.caption("No comparison data for current baselines.")
            return

        selected_solver = st.selectbox(
            "Solver",
            options=solver_options,
            key=f"comparison_solver_{metric_name}",
        )
        entry = next((e for e in valid_entries if e["solver_name"] == selected_solver), None)
        if not entry:
            st.caption("No comparison data for selected solver.")
            return

        comparisons_list = entry.get("comparisons") or []
        rows = []
        for comp in comparisons_list:
            row = {
                "Run ID": comp.get("run_id"),
                "Job": comp.get("job_name"),
                "Timestamp": comp.get("timestamp", ""),
            }
            v = (comp.get("vs_baseline") or {}).get(metric_name)
            if v is not None:
                base_val = v.get("baseline")
                cur_val = v.get("value")
                row[f"{metric_name} (baseline)"] = base_val
                row[f"{metric_name} (value)"] = cur_val
                if (
                    isinstance(base_val, (int, float))
                    and base_val != 0
                    and isinstance(cur_val, (int, float))
                ):
                    ratio = float(cur_val) / float(base_val)
                    row[f"{metric_name} (× baseline)"] = f"{ratio:.2f}×"
                else:
                    row[f"{metric_name} (× baseline)"] = ""
                row[f"{metric_name} (Δ)"] = v.get("delta")
                pct = v.get("delta_pct")
                row[f"{metric_name} (Δ%)"] = f"{pct:.1f}%" if pct is not None else ""
            else:
                row[f"{metric_name} (baseline)"] = ""
                row[f"{metric_name} (value)"] = ""
                row[f"{metric_name} (× baseline)"] = ""
                row[f"{metric_name} (Δ)"] = ""
                row[f"{metric_name} (Δ%)"] = ""
            rows.append(row)
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

def render_runtime_trend(df: pd.DataFrame, session_state) -> None:
    """Render a Plotly line chart of runtime_seconds over time, one line per series.

    Expects df to have columns: timestamp, runtime_seconds, series
    (where series = solver_name + " / " + system_name).
    Handles empty/null states inline.
    """
    if df is None or df.empty:
        st.info("No run data available yet. Run jobs via Run Jobs or the CLI to collect data.")
        return

    if "timestamp" not in df.columns or "runtime_seconds" not in df.columns:
        st.warning("Unexpected data format — missing required columns.")
        return

    if df["runtime_seconds"].isna().all():
        st.info("No runtime data recorded for the selected filters.")
        return

    fig = px.line(
        df,
        x="timestamp",
        y="runtime_seconds",
        color="series",
        markers=True,
        labels={
            "timestamp": "Date",
            "runtime_seconds": "Runtime (seconds)",
            "series": "Solver / System",
        },
        title="Runtime Trend — Wall-Clock Time per Run",
    )

    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Date: %{x}<br>Runtime: %{y:.3f}s<extra></extra>"
    )
    fig.update_layout(
        legend_title_text="Solver / System",
        hovermode="closest",
        xaxis_title="Date",
        yaxis_title="Runtime (seconds)",
    )

    event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    if event.selection.points:
        point = event.selection.points[0]
        session_state['clicked_point'] = point
        print(f"point is {st.session_state['clicked_point']}")
        session_state.page = "Run History"
        st.session_state.page_change_requested = True


def render_mlups_trend(df: pd.DataFrame, session_state) -> None:
    """Render a Plotly line chart of mlups over time, one line per series.

    Expects df to have columns: timestamp, mlups, series
    (where series = solver_name + " / " + system_name).
    Handles empty/null states inline.
    """
    if df is None or df.empty:
        st.info("No MLUPS data available for the selected filters. Only runs from solvers that report 'mlups' will appear here.")
        return

    if df["mlups"].isna().all():
        st.info("No MLUPS values recorded for the selected filters.")
        return

    fig = px.line(
        df,
        x="timestamp",
        y="mlups",
        color="series",
        markers=True,
        labels={
            "timestamp": "Date",
            "mlups": "Throughput (MLUPS)",
            "series": "Solver / System",
        },
        title="Throughput Trend — MLUPS per Run",
    )

    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Date: %{x}<br>MLUPS: %{y:.3f}<extra></extra>"
    )
    fig.update_layout(
        legend_title_text="Solver / System",
        hovermode="closest",
        xaxis_title="Date",
        yaxis_title="Throughput (MLUPS)",
    )


    event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    if event.selection.points:
        point = event.selection.points[0]
        session_state['clicked_point'] = point
        print(f"point is {session_state['clicked_point']}")
        session_state.page = "Run History"
        st.session_state.page_change_requested = True

def single_solver_heatmap(filtered, solver_name: str = ""):
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
    normalized = (numeric_df - numeric_df.min()) / (numeric_df.max() - numeric_df.min())
    normalized = normalized.fillna(0)
    normalized= normalized.transpose()
    fig = go.Figure(data=go.Heatmap(
        customdata=numeric_df.transpose(),
        z=normalized,
        x=normalized.columns,
        y=normalized.index,
        colorscale='Viridis',
        xgap=2,  # Makes vertical gridlines
        ygap=2,  # Makes horizontal gridlines
        hovertemplate='Non-Normalized Value: %{customdata:.4f}<extra></extra>',
    ))
    fig.update_layout(
        xaxis=dict(
            type="category"
        )
    )
    st.header(f"Single Metric Heatmap",help="Heatmap compares numeric metrics for a single solver using per metric normalized values. You can hover over to see the non-normalized value for reference.  The raw data table shows non normalized values for each metric.")
    # Display in Streamlit
    event = st.plotly_chart(fig, on_select='rerun', key='heatmap', selection_mode="box")
    print("Should have rerun")
    print(event)
    if event.selection.points:
        point = event.selection.points[0]
        st.session_state['clicked_point'] = point
        print(f"point is {st.session_state['clicked_point']}")
    with st.expander("View heatmap data"):
        st.dataframe(numeric_df, width='stretch')

def multi_solver_heatmap(metric_name: str, filtered, min_max_dictionary: dict[str, tuple[float, float]]):
    def norm(value, min_value, max_value):
        return (value - min_value) / (max_value - min_value)
    def normalize_row(row):
        print(min_max_dictionary)
        print(row)
        if row.name in min_max_dictionary:
            min_value, max_value = min_max_dictionary[row.name]   # row.name is the index label
        else:
            st.warning(f"Supplied min_max dictionary does not have entry for {row.name}, will use observed max/min to set ranges")
            min_value, max_value = 0, 1
        return (row - min_value) / (max_value - min_value)
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
    # normalize value based on the min and max range in the dictionary,
    # this may want to be refactored to pull from the filtered input
    # directly
    normalized = pivot.apply(normalize_row, axis = 1)
    # pivot = (pivot - min_value / (max_value - min_value))
    fig = go.Figure(data=go.Heatmap(
        customdata=pivot,
        z=normalized,
        x=normalized.columns,
        y=normalized.index,
        zmin = 0.0,
        zmax = 1.0,
        colorscale=[
                [0,  'green'],
                [0.5,  'yellow'],
                [1.0,  'red'],
            ],
        colorbar=dict(
            tickvals=np.arange(0.0, 1.0, 1.0 / 3.0),       # center ticks in each band
            ticktext=[f"Within Spec", f"Near Average", f"Out of Spec "],
            ticks='outside',
        ),
        hovertemplate='Non-Normalized Value: %{customdata:.4f}<extra></extra>',
        xgap=2,  # Makes vertical gridlines
        ygap=2,  # Makes horizontal gridlines
    ))

    fig.update_layout(
        xaxis=dict(
            type="category"
        )
    )
    st.header(f"{metric_name} Heatmap",help=f"Heatmap shows whether {metric_name} is within a specified per solver normalized range over the time seires if a range was properly supplied, otherwise reverts to showing the normalized min max range. The raw data table shows daily metrics information for the shared metric across solvers. You can hover over heatmap values to see the non normalized value of the metric.")
    def handle_click(event):
        print("called go_to_metric_page")
    # Display in Streamlit
    st.plotly_chart(fig, on_select=handle_click, key="chart")
    with st.expander(f"View heatmap data"):
        st.dataframe(df, width='stretch')
    with st.expander(f"Specification Ranges"):
        st.dataframe(pd.DataFrame(min_max_dictionary).rename(index={0: "Lower Spec Range", 1: "Upper Spec Range"}).transpose(), width='stretch')
