import ast
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Polygon
from reportlab.graphics import renderPDF
from reportlab.platypus import Table, TableStyle, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import ParagraphStyle


COLORS_UK = {
    "червоний": "#E53935", "синій": "#1565C0", "жовтий": "#FDD835",
    "зелений": "#43A047", "помаранчевий": "#FB8C00", "фіолетовий": "#8E24AA",
    "рожевий": "#EC407A", "коричневий": "#795548", "блакитний": "#29B6F6", "сірий": "#9E9E9E",
}
COLORS_RU = {
    "красный": "#E53935", "синий": "#1565C0", "жёлтый": "#FDD835",
    "зеленый": "#43A047", "оранжевый": "#FB8C00", "фиолетовый": "#8E24AA",
    "розовый": "#EC407A", "коричневый": "#795548", "голубой": "#29B6F6", "серый": "#9E9E9E",
}
COLORS_EN = {
    "red": "#E53935", "blue": "#1565C0", "yellow": "#FDD835",
    "green": "#43A047", "orange": "#FB8C00", "purple": "#8E24AA",
    "pink": "#EC407A", "brown": "#795548", "light blue": "#29B6F6", "grey": "#9E9E9E",
}


def _parse_visual(task: dict) -> dict:
    raw = task.get("visual_aid", "")
    if not raw:
        return {}
    try:
        return ast.literal_eval(raw)
    except Exception:
        return {}


def _color_map(lang: str) -> dict:
    if lang.startswith("uk"):
        return COLORS_UK
    if lang.startswith("en"):
        return COLORS_EN
    return COLORS_RU


_VISUAL_RENDERERS = {}


def render_visual(task: dict, lang: str, accent: str, content_width: float) -> Drawing:
    raw = task.get("visual_aid", "")
    if not raw:
        return _placeholder_drawing("No Visual", content_width)
    data = _parse_visual(task)
    vtype = data.get("type", "") if data else task.get("type", "")
    if vtype == "color_by_number":
        return render_color_by_number(task, lang, accent, content_width)
    if vtype == "sudoku":
        return render_sudoku(task, lang, accent, content_width)
    if vtype == "connect_dots":
        return render_connect_dots(task, lang, accent, content_width)
    if vtype == "graphic_dictation":
        return render_graphic_dictation(task, lang, accent, content_width)
    if vtype == "find_differences":
        return render_find_differences(task, lang, accent, content_width)
    if vtype == "maze":
        return render_maze(task, lang, accent, content_width)
    if vtype == "crossword":
        return render_crossword(task, lang, accent, content_width)
    return _placeholder_drawing(f"Visual:{vtype}", content_width)


def render_color_by_number(task: dict, lang: str, accent: str, content_width: float) -> Drawing:
    data = _parse_visual(task)
    if not data or data.get("type") != "color_by_number":
        return _placeholder_drawing("Color-by-Number", content_width)

    grid = data.get("grid", [])
    size = data.get("size", len(grid))
    legend = data.get("legend", [])
    cmap = _color_map(lang)

    cell_px = min(int(content_width / (size + 4.5)), 32)
    d_w = size * cell_px + 10
    d_h = size * cell_px + 16 * len(legend) + 30
    d = Drawing(d_w, d_h)

    for r in range(size):
        for c in range(size):
            val = grid[r][c]
            d.add(Rect(c * cell_px + 5, d_h - (r + 1) * cell_px - 20,
                        cell_px - 2, cell_px - 2,
                        strokeColor=black, strokeWidth=0.5, fillColor=None))
            d.add(String(c * cell_px + 5 + cell_px * 0.3,
                          d_h - (r + 1) * cell_px - 20 + cell_px * 0.2,
                          str(val), fontSize=cell_px * 0.5, fillColor=black))

    ly = 5
    for entry in legend:
        nm = entry.get("number", 0)
        color_name = entry.get("color", "")
        hex_c = cmap.get(color_name, "#FFFFFF")
        d.add(Rect(size * cell_px + 15, ly, 12, 10,
                    fillColor=HexColor(hex_c), strokeColor=black, strokeWidth=0.3))
        d.add(String(size * cell_px + 32, ly + 1,
                      f"{nm} = {color_name}", fontSize=8, fillColor=black))
        ly += 13
    return d


def render_sudoku(task: dict, lang: str, accent: str, content_width: float) -> Drawing:
    data = _parse_visual(task)
    if not data or data.get("type") != "sudoku":
        return _placeholder_drawing("Sudoku", content_width)

    grid = data.get("grid", [])
    sz = data.get("size", 4)
    box_sz = data.get("box_size", 2)

    cell_px = min(int(content_width / (sz + 1.5)), 48)
    d_w = sz * cell_px + 20
    d_h = sz * cell_px + 20
    d = Drawing(d_w, d_h)

    for r in range(sz + 1):
        sw = 2.0 if r % box_sz == 0 else 0.5
        d.add(Line(5, r * cell_px + 5, sz * cell_px + 5, r * cell_px + 5,
                    strokeColor=black, strokeWidth=sw))
    for c in range(sz + 1):
        sw = 2.0 if c % box_sz == 0 else 0.5
        d.add(Line(c * cell_px + 5, 5, c * cell_px + 5, sz * cell_px + 5,
                    strokeColor=black, strokeWidth=sw))
    for r in range(sz):
        for c in range(sz):
            val = grid[r][c]
            if val != 0:
                d.add(String(c * cell_px + 5 + cell_px * 0.3,
                              r * cell_px + 5 + cell_px * 0.25,
                              str(val), fontSize=cell_px * 0.55,
                              fillColor=black, fontName="Helvetica-Bold"))
    return d


def render_connect_dots(task: dict, lang: str, accent: str, content_width: float) -> Drawing:
    data = _parse_visual(task)
    if not data or data.get("type") != "connect_dots":
        return _placeholder_drawing("Connect Dots", content_width)

    points = data.get("points", [])
    if not points:
        return _placeholder_drawing("Connect Dots", content_width)

    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1)
    span_y = max(max_y - min_y, 1)

    d_size = min(content_width, 200)
    d = Drawing(d_size, d_size)

    def scale(p):
        x = ((p["x"] - min_x) / span_x) * (d_size - 40) + 20
        y = ((p["y"] - min_y) / span_y) * (d_size - 40) + 20
        return x, y

    for i in range(len(points)):
        nxt = (i + 1) % len(points)
        x1, y1 = scale(points[i])
        x2, y2 = scale(points[nxt])
        d.add(Line(x1, y1, x2, y2, strokeColor=HexColor("#CCCCCC"),
                    strokeWidth=0.5, strokeDashArray=[2, 3]))

    for p in points:
        x, y = scale(p)
        d.add(Circle(x, y, 3, fillColor=accent, strokeColor=None))
        d.add(String(x + 4, y + 2, str(p["num"]), fontSize=8, fillColor=black))
    return d


def render_graphic_dictation(task: dict, lang: str, accent: str, content_width: float) -> Drawing:
    data = _parse_visual(task)
    if not data or data.get("type") != "graphic_dictation":
        return _placeholder_drawing("Graphic Dictation", content_width)

    steps = data.get("steps", [])
    steps_text = data.get("steps_text", [])
    if not steps:
        return _placeholder_drawing("Graphic Dictation", content_width)

    cell_px = 14
    d_w = content_width
    line_h = 12
    d_h = len(steps) * line_h + 30 + 80

    x, y = 5, d_h - 15
    grid_points = [(x, y)]
    for dx, dy in steps:
        x += dx * cell_px
        y += dy * cell_px
        grid_points.append((x, y))

    gp_xs = [p[0] for p in grid_points]
    gp_ys = [p[1] for p in grid_points]
    min_gx, max_gx = min(gp_xs), max(gp_xs)
    min_gy, max_gy = min(gp_ys), max(gp_ys)

    d = Drawing(d_w, d_h)

    gx_span = max(max_gx - min_gx, 1)
    gy_span = max(max_gy - min_gy, 1)
    fig_w = min(120, content_width * 0.4)
    fig_h = min(80, content_width * 0.3)
    offset_x = 15
    offset_y = d_h - max_gy + min_gy - fig_h + 20

    def gscale(pt):
        return (
            offset_x + (pt[0] - min_gx) / gx_span * fig_w,
            offset_y + (pt[1] - min_gy) / gy_span * fig_h,
        )

    for i in range(len(grid_points) - 1):
        x1, y1 = gscale(grid_points[i])
        x2, y2 = gscale(grid_points[i + 1])
        d.add(Line(x1, y1, x2, y2, strokeColor=HexColor("#E0E0E0"),
                    strokeWidth=0.5, strokeDashArray=[2, 2]))

    sx, sy = gscale(grid_points[0])
    d.add(Circle(sx, sy, 3, fillColor=accent, strokeColor=None))

    text_x = fig_w + offset_x + 30
    for i, st in enumerate(steps_text):
        ly = d_h - 20 - i * line_h
        d.add(String(text_x, ly, f"{i + 1}. {st}", fontSize=8, fillColor=black))
    return d


def render_find_differences(task: dict, lang: str, accent: str, content_width: float) -> Drawing:
    data = _parse_visual(task)
    if not data or data.get("type") != "find_differences":
        return _placeholder_drawing("Find Differences", content_width)

    grid_a = data.get("grid_a", [])
    grid_b = data.get("grid_b", [])
    rows = data.get("rows", len(grid_a))
    cols = data.get("cols", len(grid_a[0]) if grid_a else 4)

    cell_px = min(int((content_width - 10) / (cols * 2 + 1)), 26)
    gap = 16
    d_w = cols * cell_px * 2 + gap + 20
    d_h = rows * cell_px + 30
    d = Drawing(d_w, d_h)

    cmap = _color_map(lang) if callable(_color_map) else COLORS_UK

    for g_idx, grid in enumerate([grid_a, grid_b]):
        offset_x = 5 + g_idx * (cols * cell_px + gap)
        d.add(String(offset_x, d_h - 10, "A" if g_idx == 0 else "B",
                      fontSize=10, fillColor=black))
        for r in range(rows):
            for c in range(cols):
                cell = grid[r][c]
                shape = cell.get("shape", "")
                color_name = cell.get("color", "")
                hex_c = cmap.get(color_name, "#DDDDDD")
                x = offset_x + c * cell_px
                y = d_h - 20 - (r + 1) * cell_px
                d.add(Rect(x, y, cell_px - 2, cell_px - 2,
                            strokeColor=black, strokeWidth=0.4, fillColor=None))
                if shape and color_name not in ("empty", ""):
                    cx = x + cell_px * 0.5 - 1
                    cy = y + cell_px * 0.5
                    radius = cell_px * 0.28
                    d.add(Circle(cx, cy, radius, fillColor=HexColor(hex_c), strokeColor=None))

    return d


def render_maze(task: dict, lang: str, accent: str, content_width: float) -> Drawing:
    data = _parse_visual(task)
    if not data or data.get("type") != "maze":
        return _placeholder_drawing("Maze", content_width)

    grid = data.get("grid", [])
    if not grid:
        return _placeholder_drawing("Maze", content_width)

    rows = len(grid)
    cols = len(grid[0])
    cell_px = min(int(content_width / (cols + 1)), 10)
    d_w = cols * cell_px + 20
    d_h = rows * cell_px + 25
    d = Drawing(d_w, d_h)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                d.add(Rect(c * cell_px + 5, d_h - (r + 1) * cell_px - 5,
                            cell_px, cell_px,
                            fillColor=black, strokeColor=None))
            else:
                d.add(Rect(c * cell_px + 5, d_h - (r + 1) * cell_px - 5,
                            cell_px, cell_px,
                            fillColor=None, strokeColor=HexColor("#CCCCCC"), strokeWidth=0.2))
    return d


def render_crossword(task: dict, lang: str, accent: str, content_width: float) -> Drawing:
    data = _parse_visual(task)
    if not data or data.get("type") != "crossword":
        return _placeholder_drawing("Crossword", content_width)

    grid = data.get("grid", [])
    if not grid:
        return _placeholder_drawing("Crossword", content_width)

    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    cell_px = min(int(content_width / (cols + 1)), 18)
    numbers = data.get("numbers", {})

    d_w = cols * cell_px + 20
    d_h = rows * cell_px + 25
    d = Drawing(d_w, d_h)

    row_off = data.get("row_offset", 0)
    col_off = data.get("col_offset", 0)

    for r in range(rows):
        for c in range(cols):
            x = c * cell_px + 5
            y = d_h - (r + 1) * cell_px - 5
            abs_r = r + row_off
            abs_c = c + col_off
            key = f"{abs_r},{abs_c}"
            if grid[r][c] == "":
                continue
            d.add(Rect(x, y, cell_px, cell_px,
                        fillColor=None, strokeColor=black, strokeWidth=0.8))
            num = numbers.get(key)
            if num:
                d.add(String(x + 1, y + cell_px - 7, str(num),
                              fontSize=5, fillColor=black))
    return d


def _placeholder_drawing(label: str, w: float) -> Drawing:
    d = Drawing(w, 30)
    d.add(String(5, 10, f"[{label}]", fontSize=10, fillColor=black))
    return d
