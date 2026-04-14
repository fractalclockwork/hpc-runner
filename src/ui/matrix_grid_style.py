"""
Streamlit matrix grid: layout + CSS helpers for compact toggles aligned with checkboxes.

**Pattern (repeat on other pages)** — Streamlit 1.55+:

1. **Widget keys** become ``st-key-{sanitized-key}`` on the element container (not on the
   ``<button>``). Match with ``[class*="st-key-{your-prefix}"]`` (prefix must be unique).

2. **``st.button(..., width=px)``** sizes the ``[data-testid="stButton"]`` shell; set the inner
   ``button`` to ``width: 100%`` and fixed height so the glyph box matches checkboxes.

3. **Do not** scope global ``<style>`` with ``section[data-testid="stMainBlockContainer"]``
   if the grid lives in ``@st.fragment`` — fragment output may sit outside that section and
   rules will not match.

4. **Column headers vs body**: Put **system names** and **column ↕** in **separate** ``st.columns``
   rows so each row uses the same ``[0.28, 0.72]`` + inner ``[2, 1, 2]`` band as data cells;
   stacking name + toggle in one cell skews Streamlit’s column math.

5. **Transforms**: Use separate X/Y shifts for column vs row toggles; optional inner
   ``translateX`` on ``button > *`` for Unicode arrow metrics.

6. **Cells**: Checkbox keys use prefix ``matrix-cell``; dashes use HTML class
   ``matrix-dash-cell`` (see :func:`matrix_grid_control_css` ``dash_cell_class``).

7. **Active run**: HTML class ``matrix-active-dot`` on a ``●`` in the **right** slot of
   ``MATRIX_INNER_BAND`` (same row as the checkbox, to the right of it). Optional
   ``active_dot_shift_*`` nudges the glyph (negative X pulls toward the checkbox).
"""

from __future__ import annotations

from dataclasses import dataclass

# Middle band inside the 0.72 slice (and solver-column row-toggle slot): toggle / checkbox / dash.
MATRIX_INNER_BAND: list[int] = [2, 1, 2]


@dataclass(frozen=True)
class MatrixGridControlStyle:
    """Pixel tuning for matrix toggles, checkboxes, dash placeholders, and active-run dot."""

    toggle_height_px: int
    toggle_width_px: int
    row_toggle_shift_x_px: int
    col_toggle_shift_x_px: int
    cell_shift_x_px: int
    row_toggle_shift_y_px: int
    glyph_shift_x_px: int
    active_dot_shift_x_px: int
    active_dot_shift_y_px: int


DEFAULT_MATRIX_GRID_CONTROL_STYLE = MatrixGridControlStyle(
    toggle_height_px=18,
    toggle_width_px=(18 * 4) // 3,
    row_toggle_shift_x_px=8,
    col_toggle_shift_x_px=4,
    cell_shift_x_px=0,
    row_toggle_shift_y_px=3,
    glyph_shift_x_px=2,
    active_dot_shift_x_px=-10,
    active_dot_shift_y_px=2,
)


def _st_key_contains(prefix: str) -> str:
    return f'[class*="st-key-{prefix}"]'


def matrix_grid_control_css(
    style: MatrixGridControlStyle | None = None,
    *,
    col_toggle_key_prefix: str = "matrix-col-toggle",
    row_toggle_key_prefix: str = "matrix-row-toggle",
    cell_key_prefix: str = "matrix-cell",
    dash_cell_class: str = "matrix-dash-cell",
    active_dot_class: str = "matrix-active-dot",
) -> str:
    """
    Return a ``<style>...</style>`` block for Run Matrix–style controls.

    Copy this module and adjust :class:`MatrixGridControlStyle` / key prefixes / ``active_dot_class``
    when adding another solver×system grid.
    """
    s = style or DEFAULT_MATRIX_GRID_CONTROL_STYLE
    col_sel = _st_key_contains(col_toggle_key_prefix)
    row_sel = _st_key_contains(row_toggle_key_prefix)
    cell_sel = _st_key_contains(cell_key_prefix)
    h = s.toggle_height_px
    ad = active_dot_class

    return f"""
        <style>
        {col_sel} [data-testid="stButton"],
        {row_sel} [data-testid="stButton"] {{
            width: {s.toggle_width_px}px !important;
            min-width: {s.toggle_width_px}px !important;
            max-width: {s.toggle_width_px}px !important;
            box-sizing: border-box !important;
            margin-left: 0 !important;
            margin-right: auto !important;
        }}
        {col_sel} [data-testid="stButton"] {{
            transform: translateX(-{s.col_toggle_shift_x_px}px) !important;
        }}
        {row_sel} [data-testid="stButton"] {{
            transform: translate(-{s.row_toggle_shift_x_px}px, {s.row_toggle_shift_y_px}px) !important;
        }}
        {col_sel} [data-testid="stButton"] button,
        {row_sel} [data-testid="stButton"] button {{
            box-sizing: border-box !important;
            width: 100% !important;
            min-width: 0 !important;
            height: {h}px !important;
            min-height: {h}px !important;
            max-height: {h}px !important;
            padding: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            line-height: 1 !important;
            font-size: 0.7rem !important;
        }}
        {col_sel} [data-testid="stButton"] button *,
        {row_sel} [data-testid="stButton"] button * {{
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1 !important;
            text-align: left !important;
        }}
        {col_sel} [data-testid="stButton"] button > *,
        {row_sel} [data-testid="stButton"] button > * {{
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            width: 100% !important;
            min-width: 0 !important;
            transform: translateX(-{s.glyph_shift_x_px}px) !important;
        }}
        {cell_sel} [data-testid="stCheckbox"] {{
            margin-left: 0 !important;
            margin-right: auto !important;
            width: fit-content !important;
            max-width: 100% !important;
            padding-left: {s.cell_shift_x_px}px !important;
        }}
        .{dash_cell_class} {{
            margin: 0 !important;
            padding: 0 !important;
            padding-left: {s.cell_shift_x_px}px !important;
            text-align: left !important;
            line-height: {h}px !important;
            height: {h}px !important;
            display: flex !important;
            align-items: center !important;
        }}
        .{ad} {{
            color: #16a34a !important;
            display: inline-block !important;
            transform: translate({s.active_dot_shift_x_px}px, {s.active_dot_shift_y_px}px) !important;
            vertical-align: middle !important;
        }}
        </style>
        """
