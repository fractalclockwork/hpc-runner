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
