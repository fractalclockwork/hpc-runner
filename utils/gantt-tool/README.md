# Gantt Chart Generator (XKCD Style)

A lightweight, readable, XKCD‑style Gantt chart generator built with Python, Pandas, and Matplotlib.  
This tool produces sketch‑style project timelines with clear owner‑specific colors, hatching patterns, milestones, deliverables, and phase shading.  
It is designed for GitHub/GitLab wikis, class projects, and lightweight planning workflows.

---

## Features

- XKCD sketch‑style rendering  
- Owner‑specific colors and hatching  
- Task names on the left, owner names on the right  
- Phase shading for high‑level structure  
- Milestones (red diamonds)  
- Deliverables (blue dashed lines)  
- Alternating row shading for readability  
- SVG output for wiki‑friendly embedding  
- Simple CLI interface using `uv`  

---

## Installation

Install dependencies using `uv`:

```bash
uv sync
```

---

## Usage

Generate a Gantt chart from a CSV file:

```bash
uv run generate_gantt.py project.csv --out gantt.svg
```

- `project.csv` — input project definition  
- `--out gantt.svg` — output SVG file (default: `gantt.svg`)  

The resulting SVG can be embedded directly into wikis or documents.

---

## Input Format

The tool expects a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `Type` | One of: `task`, `phase`, `milestone`, `deliverable` |
| `Name` | Human‑readable name |
| `Owner` | Person or team responsible (for tasks) |
| `Start` | Start date (YYYY‑MM‑DD) |
| `End` | End date (YYYY‑MM‑DD) |
| `Date` | Single date (YYYY‑MM‑DD) for milestones/deliverables |

### Example

```csv
Type,Name,Owner,Start,End,Date
phase,Phase 1,,,2026-01-08,2026-02-15
task,Prototype Solver,Brent,2026-01-10,2026-01-20,
task,UI Mockups,Kayleen,2026-01-12,2026-01-22,
milestone,Prototype Complete,,, ,2026-01-23
deliverable,Report Draft,,, ,2026-02-01
```

---

## Directory Structure

```text
gantt-tool/
├── generate_gantt.py      # Main script
├── project.csv            # Example input
├── gantt.svg              # Example output
├── pyproject.toml         # Project config (deps)
└── README.md              # This file
```

---

## Development

### Formatting & Linting (Ruff)

Format all code:

```bash
uv run ruff format .
```

Lint the project:

```bash
uv run ruff check .
```

---

## License

MIT License

