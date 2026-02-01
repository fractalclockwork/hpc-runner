#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ------------------------------------------------------------
# PATTERN + COLOR MAPS
# ------------------------------------------------------------
OWNER_PATTERNS = {
    "Brent": "/",
    "Shree": "\\",
    "Shawn": "x",
    "Kayleen": ".",
    "Team": "+",
}

OWNER_COLORS = {
    "Brent": "#a2cffe",  # soft blue
    "Shree": "#ffb07c",  # peach
    "Shawn": "#c2eabd",  # mint
    "Kayleen": "#ff9cee",  # pink
    "Team": "#d5baff",  # lavender
}


# ------------------------------------------------------------
# LOAD CSV
# ------------------------------------------------------------
def load_csv(path):
    df = pd.read_csv(path)

    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    # Convert dates
    for col in ["Start", "End", "Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


# ------------------------------------------------------------
# DRAW GANTT CHART
# ------------------------------------------------------------
def generate_gantt(df, output_svg):
    tasks = df[df["Type"] == "task"].copy()
    milestones = df[df["Type"] == "milestone"].copy()
    deliverables = df[df["Type"] == "deliverable"].copy()
    phases = df[df["Type"] == "phase"].copy()

    # Sort tasks by start date for clean ordering
    tasks = tasks.sort_values("Start").reset_index(drop=True)

    # Assign y-positions
    tasks["y"] = range(len(tasks))

    # Convert durations
    tasks["duration"] = (tasks["End"] - tasks["Start"]).dt.days

    with plt.xkcd():
        fig, ax = plt.subplots(figsize=(22, 12))

        # ----------------------------------------------------
        # PHASE BACKGROUNDS
        # ----------------------------------------------------
        for _, row in phases.iterrows():
            ax.axvspan(row["Start"], row["End"], color="#f0f0f0", alpha=0.25, zorder=0)
            ax.text(
                row["Start"],
                len(tasks) + 1,
                row["Name"],
                fontsize=14,
                ha="left",
                va="bottom",
                fontweight="bold",
            )

        # ----------------------------------------------------
        # ALTERNATING ROW SHADING
        # ----------------------------------------------------
        for i in range(len(tasks)):
            if i % 2 == 0:
                ax.axhspan(i - 0.4, i + 0.4, color="#fafafa", zorder=0.5)

        # ----------------------------------------------------
        # TASK BARS (owner-specific colors + hatching)
        # ----------------------------------------------------
        for i, row in tasks.iterrows():
            owner = row["Owner"]
            pattern = OWNER_PATTERNS.get(owner, None)
            color = OWNER_COLORS.get(owner, "#cccccc")  # fallback gray

            # Draw the bar
            ax.barh(
                y=row["y"],
                width=row["duration"],
                left=row["Start"],
                height=0.8,
                color=color,
                edgecolor="black",
                hatch=pattern,
                linewidth=1.5,
            )

            # Owner label on the right side of the bar
            ax.text(
                row["Start"] + pd.Timedelta(days=row["duration"] + 0.2),
                row["y"],
                f"{owner}",
                va="center",
                ha="left",
                fontsize=10,
                fontweight="bold",
                color="black",
            )

        # ----------------------------------------------------
        # MILESTONES
        # ----------------------------------------------------
        for _, row in milestones.iterrows():
            ax.scatter(
                row["Date"],
                -1,
                marker="D",
                s=140,
                color="red",
                edgecolor="black",
                zorder=5,
            )
            ax.text(
                row["Date"],
                -1.5,
                row["Name"],
                ha="center",
                va="bottom",
                fontsize=10,
                color="red",
                rotation=45,
            )

        # ----------------------------------------------------
        # DELIVERABLES
        # ----------------------------------------------------
        for _, row in deliverables.iterrows():
            ax.axvline(row["Date"], color="blue", linestyle="--", linewidth=2)
            ax.text(
                row["Date"],
                len(tasks) + 0.5,
                row["Name"],
                ha="left",
                va="top",
                fontsize=10,
                color="blue",
                rotation=45,
            )

        # ----------------------------------------------------
        # AXIS FORMATTING
        # ----------------------------------------------------
        ax.set_yticks(tasks["y"])
        ax.set_yticklabels(tasks["Name"], fontsize=10)

        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

        plt.xticks(rotation=45, fontsize=10)

        ax.set_xlabel("Timeline", fontsize=14)
        ax.set_title("Project Gantt Chart (DOW-1-26)", fontsize=20)

        ax.grid(True, linestyle="--", linewidth=1, color="#cccccc")

        plt.tight_layout()
        fig.savefig(output_svg, format="svg")
        print(f"Gantt chart saved to {output_svg}")


# ------------------------------------------------------------
# CLI ENTRYPOINT
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Generate XKCD-style Gantt chart from CSV"
    )
    parser.add_argument("csv", help="Path to CSV project file")
    parser.add_argument("--out", default="gantt.svg", help="Output SVG file")
    args = parser.parse_args()

    df = load_csv(args.csv)
    generate_gantt(df, args.out)


if __name__ == "__main__":
    main()
