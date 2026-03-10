"""Chart rendering functions for the Streamlit UI."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def render_runtime_trend(df: pd.DataFrame) -> None:
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

    st.plotly_chart(fig, use_container_width=True)


def render_mlups_trend(df: pd.DataFrame) -> None:
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

    st.plotly_chart(fig, use_container_width=True)


def render_metric_heatmap(
    pivot: pd.DataFrame,
    title: str,
    normalize_rows: bool = True,
) -> None:
    """Render a Plotly heatmap from a pre-pivoted DataFrame.

    pivot: rows = labels (metrics or solver/system series),
           columns = run labels (short timestamps),
           values = numeric.
    normalize_rows: normalize each row to [0,1] so metrics with different
    units are visually comparable. Raw values are always shown on hover.
    """
    import numpy as np

    if pivot is None or pivot.empty:
        st.info("No data for the selected heatmap configuration.")
        return

    raw = pivot.values.astype(float)

    if normalize_rows:
        row_min = np.nanmin(raw, axis=1, keepdims=True)
        row_max = np.nanmax(raw, axis=1, keepdims=True)
        denom = np.where((row_max - row_min) == 0, 1.0, row_max - row_min)
        display = (raw - row_min) / denom
    else:
        display = raw

    # Build hover text with raw values; show "—" for NaN
    hover = np.where(
        np.isnan(raw),
        "—",
        np.vectorize(lambda v: f"{v:.4g}")(raw),
    )

    fig = px.imshow(
        display,
        x=list(pivot.columns),
        y=list(pivot.index),
        color_continuous_scale="Blues",
        aspect="auto",
        title=title,
    )
    fig.update_traces(
        customdata=hover,
        hovertemplate="<b>%{y}</b> | %{x}<br>Value: %{customdata}<extra></extra>",
        text=None,
    )
    fig.update_layout(
        xaxis_title="Run",
        yaxis_title="",
        xaxis_tickangle=-45,
        coloraxis_showscale=normalize_rows,
    )
    if normalize_rows:
        fig.update_coloraxes(colorbar_title="Normalized")

    st.plotly_chart(fig, use_container_width=True)
    if normalize_rows:
        st.caption(
            "Color is normalized per row so metrics with different units are visually comparable. "
            "Hover over any cell for the raw value."
        )
