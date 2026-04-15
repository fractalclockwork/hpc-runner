"""
Streamlit matrix grid: layout + CSS helpers for compact toggles aligned with checkboxes.

**Pattern (repeat on other pages)** — Streamlit 1.55+:

1. **Widget keys** become ``st-key-{sanitized-key}`` on the element container (not on the
   ``<button>``). Match with ``[class*="st-key-{your-prefix}"]`` (prefix must be unique).

2. **``st.button(..., width=px)``** sizes the ``[data-testid="stButton"]`` shell; set the inner
   ``button`` to ``width: 100%`` and fixed height (see ``toggle_height_px``) so the glyph box matches checkboxes.

3. **Do not** scope global ``<style>`` with ``section[data-testid="stMainBlockContainer"]``
   if the grid lives in ``@st.fragment`` — fragment output may sit outside that section and
   rules will not match.

4. **Column headers vs body**: Put **system names** and **column ↕** in **separate** ``st.columns``
   rows so each row uses the same ``[0.28, 0.72]`` + inner ``[2, 1, 2]`` band as data cells;
   stacking name + toggle in one cell skews Streamlit’s column math.

5. **Transforms**: Outer ``translate`` on ``[data-testid="stButton"]`` aligns the control with
   the checkbox band; inner ``translateX`` on ``button > *`` uses ``col_glyph_shift_x_px`` /
   ``row_glyph_shift_x_px`` for Unicode arrow optical centering.

6. **Cells**: Checkbox keys use prefix ``matrix-cell``; dashes use HTML class
   ``matrix-dash-cell`` (see :func:`matrix_grid_control_css` ``dash_cell_class``).

7. **Active run**: HTML class ``matrix-active-dot`` on a ``●`` in the **right** slot of
   ``MATRIX_INNER_BAND`` (same row as the checkbox, to the right of it). Optional
   ``active_dot_shift_*`` nudges the glyph (negative X pulls toward the checkbox).

8. **Row alignment**: Use the **same** ``pad_l | mid | pad_r`` ``st.columns(MATRIX_INNER_BAND)``
   for dash rows as for checkbox rows (only ``mid`` has content for dashes). Use
   ``cell_row_min_height_px`` so dash em-dash and checkboxes share one vertical band with the
   solver name (``matrix-solver-name``).

9. **Run Matrix layout**: Use :class:`MatrixRunLayoutTuning` for solver/system column weights,
   uniform data-row spacing (``data_row_margin_block_rem`` on all data rows), and optional whole-grid
   shift.
"""

from __future__ import annotations

from dataclasses import dataclass

# Middle band inside the 0.72 slice (and solver-column row-toggle slot): toggle / checkbox / dash.
MATRIX_INNER_BAND: list[int] = [2, 1, 2]


@dataclass(frozen=True)
class MatrixRunLayoutTuning:
    """Tune Run Matrix column weights, row gaps, and whole-grid shift.

    **Horizontal / vertical:** ``grid_shift_x_px`` / ``grid_shift_y_px`` move the whole matrix
    (``st.container(key=\"run_matrix_tuning_shell\")``) in screen pixels (+X right, +Y down).
    """

    solver_col_weight: float = 0.52
    system_col_weight: float = 0.44
    #: Same margin for *every* data row (rem).
    data_row_margin_block_rem: float = -0.79
    grid_shift_x_px: int = -9
    grid_shift_y_px: int = -13


DEFAULT_MATRIX_RUN_LAYOUT_TUNING = MatrixRunLayoutTuning()

# Back-compat for imports that expect module-level weights (defaults only).
MATRIX_SOLVER_COL_WEIGHT: float = DEFAULT_MATRIX_RUN_LAYOUT_TUNING.solver_col_weight
MATRIX_SYSTEM_COL_WEIGHT: float = DEFAULT_MATRIX_RUN_LAYOUT_TUNING.system_col_weight


@dataclass(frozen=True)
class MatrixGridControlStyle:
    """Pixel tuning for matrix toggles, checkboxes, dash placeholders, and active-run dot.

    ``mid_cell_nudge_x_px`` / ``checkbox_cell_translate_y_px``: applied on the keyed checkbox
    root (``cell_sel``), so both axes actually move the widget. ``dash_mid_cell_nudge_x_px`` is
    separate so the em-dash can sit slightly right of the checkbox column if desired.
    """

    toggle_height_px: int
    toggle_width_px: int
    row_toggle_shift_x_px: int
    col_toggle_shift_x_px: int
    cell_shift_x_px: int
    mid_cell_nudge_x_px: int
    checkbox_cell_translate_y_px: int
    dash_mid_cell_nudge_x_px: int
    row_toggle_shift_y_px: int
    col_glyph_shift_x_px: int
    row_glyph_shift_x_px: int
    active_dot_shift_x_px: int
    active_dot_shift_y_px: int
    cell_row_min_height_px: int


DEFAULT_MATRIX_GRID_CONTROL_STYLE = MatrixGridControlStyle(
    toggle_height_px=14,
    toggle_width_px=(14 * 4) // 3,
    row_toggle_shift_x_px=9,
    col_toggle_shift_x_px=5,
    cell_shift_x_px=0,
    mid_cell_nudge_x_px=4,
    checkbox_cell_translate_y_px=6,
    dash_mid_cell_nudge_x_px=3,
    row_toggle_shift_y_px=-8,
    col_glyph_shift_x_px=5,
    row_glyph_shift_x_px=4,
    active_dot_shift_x_px=-10,
    active_dot_shift_y_px=-5,
    cell_row_min_height_px=22,
)


def _st_key_contains(prefix: str) -> str:
    return f'[class*="st-key-{prefix}"]'


def matrix_grid_control_css(
    style: MatrixGridControlStyle | None = None,
    *,
    layout: MatrixRunLayoutTuning | None = None,
    col_toggle_key_prefix: str = "matrix-col-toggle",
    row_toggle_key_prefix: str = "matrix-row-toggle",
    cell_key_prefix: str = "matrix-cell",
    dash_cell_class: str = "matrix-dash-cell",
    active_dot_class: str = "matrix-active-dot",
) -> str:
    """
    Return a ``<style>...</style>`` block for Run Matrix–style controls.

    Pass :class:`MatrixRunLayoutTuning` via ``layout`` for column weights, data-row gaps, and shell
    shift. Defaults: :data:`DEFAULT_MATRIX_RUN_LAYOUT_TUNING`.
    """
    s = style or DEFAULT_MATRIX_GRID_CONTROL_STYLE
    lt = layout or DEFAULT_MATRIX_RUN_LAYOUT_TUNING
    col_sel = _st_key_contains(col_toggle_key_prefix)
    row_sel = _st_key_contains(row_toggle_key_prefix)
    cell_sel = _st_key_contains(cell_key_prefix)
    h = s.toggle_height_px
    ad = active_dot_class
    rh = s.cell_row_min_height_px
    m = lt.data_row_margin_block_rem

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
        {col_sel} {{
            min-height: {rh}px !important;
            margin-block: 0 !important;
            padding-block: 0 !important;
        }}
        {row_sel} {{
            display: flex !important;
            align-items: center !important;
            min-height: {rh}px !important;
            margin-block: 0 !important;
            padding-block: 0 !important;
        }}
        {row_sel} [data-testid="stButton"] {{
            transform: translate(-{s.row_toggle_shift_x_px}px, calc({s.row_toggle_shift_y_px}px + 2mm)) !important;
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
            justify-content: center !important;
            line-height: 1 !important;
            font-size: 0.7rem !important;
        }}
        {col_sel} [data-testid="stButton"] button *,
        {row_sel} [data-testid="stButton"] button * {{
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1 !important;
            text-align: center !important;
        }}
        {col_sel} [data-testid="stButton"] button > * {{
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            min-width: 0 !important;
            transform: translateX(-{s.col_glyph_shift_x_px}px) !important;
        }}
        {row_sel} [data-testid="stButton"] button > * {{
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            min-width: 0 !important;
            transform: translateX(-{s.row_glyph_shift_x_px}px) !important;
        }}
        {cell_sel} {{
            display: flex !important;
            align-items: center !important;
            min-height: {rh}px !important;
            margin-block: 0 !important;
            padding-block: 0 !important;
            transform: translate(-{s.mid_cell_nudge_x_px}px, -{s.checkbox_cell_translate_y_px}px) !important;
        }}
        {cell_sel} [data-testid="stCheckbox"] {{
            margin: 0 auto 0 0 !important;
            width: fit-content !important;
            max-width: 100% !important;
            padding: 0 0 0 {s.cell_shift_x_px}px !important;
            align-self: center !important;
        }}
        .{dash_cell_class} {{
            margin: 0 !important;
            padding: 0 !important;
            padding-left: {s.cell_shift_x_px}px !important;
            text-align: left !important;
            min-height: {rh}px !important;
            line-height: 1 !important;
            display: flex !important;
            align-items: center !important;
            box-sizing: border-box !important;
            transform: translateX(-{s.dash_mid_cell_nudge_x_px}px) !important;
        }}
        .matrix-solver-name {{
            display: inline-flex !important;
            align-items: center !important;
            min-height: {rh}px !important;
            line-height: 1.05 !important;
            box-sizing: border-box !important;
            transform: translateY(-1mm) !important;
        }}
        .{ad} {{
            color: #16a34a !important;
            display: inline-block !important;
            transform: translate({s.active_dot_shift_x_px}px, {s.active_dot_shift_y_px}px) !important;
            vertical-align: middle !important;
        }}
        /*
         * Tighter vertical gap between *data* rows only. Same margin for every data row.
         */
        [data-testid="stHorizontalBlock"]:has(.matrix-solver-name):has([class*="st-key-matrix-cell"]) {{
            margin-block: {m}rem !important;
        }}
        [class*="st-key-run_matrix_tuning_shell"] {{
            transform: translate({lt.grid_shift_x_px}px, {lt.grid_shift_y_px}px) !important;
        }}
        </style>
        """