# -*- coding: utf-8 -*-
"""
Мини-библиотека оформления ЕСКД: лист с примитивами в миллиметрах,
вывод в PDF (matplotlib) и DXF (ezdxf), рамка, основные надписи
формы 1 и 2 (ГОСТ 2.104), бланк спецификации формы 1 (ГОСТ 2.106).
"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Polygon, Arc

S, T = 0.7, 0.35          # толщина основной (S) и тонкой (S/2) линий, мм
from matplotlib.font_manager import FontProperties, findSystemFonts
from matplotlib.textpath import TextPath

def _font():
    for f in findSystemFonts():
        if f.endswith("DejaVuSansCondensed-Oblique.ttf"):
            return FontProperties(fname=f)
    return FontProperties(family="DejaVu Sans", style="italic")

FP = _font()
FP_B = FP.copy(); FP_B.set_weight("bold")
_PT = 72 / 25.4


def fsize(h):
    """Кегль (pt) для высоты прописных h мм."""
    return h * _PT / 0.73


def text_w(s, h):
    """Ширина строки в мм при высоте шрифта h."""
    if not s:
        return 0.0
    tp = TextPath((0, 0), s, size=fsize(h), prop=FP)
    return tp.get_extents().width / _PT


class Sheet:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.items = []

    # --- примитивы
    def line(self, x1, y1, x2, y2, lw=T, ls="-"):
        self.items.append(("line", x1, y1, x2, y2, lw, ls))

    def poly(self, pts, lw=T, ls="-", closed=False, fill=None):
        self.items.append(("poly", list(pts), lw, ls, closed, fill))

    def rect(self, x, y, w, h, lw=T, ls="-", fill=None):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], lw, ls, True, fill)

    def circle(self, x, y, r, lw=T, fill=None):
        self.items.append(("circle", x, y, r, lw, fill))

    def text(self, x, y, s, h=3.5, ha="left", va="baseline", rot=0, bold=False, maxw=None):
        s = str(s)
        if maxw:
            while h > 1.8 and text_w(s, h) > maxw:
                h -= 0.25
        self.items.append(("text", x, y, s, h, ha, va, rot, bold))

    def hatch(self, x, y, w, h, step=1.5, lw=0.18):
        """Штриховка прямоугольника под 45°."""
        n = int((w + h) / step) + 1
        for i in range(n):
            c = i * step
            # линия x - y = const, ограниченная прямоугольником
            x1, y1 = x + c, y
            x2, y2 = x, y + c
            if x1 > x + w:
                y1 += x1 - (x + w); x1 = x + w
            if y2 > y + h:
                x2 += y2 - (y + h); y2 = y + h
            if y1 <= y + h and x2 <= x + w:
                self.line(x1, y1, x2, y2, lw)

    # --- составные
    def arrow(self, x1, y1, x2, y2, lw=T, size=2.5):
        """Стрелка в точке (x2,y2)."""
        a = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - size * math.cos(a - 0.17), y2 - size * math.sin(a - 0.17))
        p2 = (x2 - size * math.cos(a + 0.17), y2 - size * math.sin(a + 0.17))
        self.poly([(x2, y2), p1, p2], lw=0.1, closed=True, fill="k")

    def dim_h(self, x1, x2, y, ybase1, ybase2, txt, h=3.5, ext=2):
        """Горизонтальный размер: выносные от ybase до y, размерная на y."""
        self.line(x1, ybase1, x1, y + (ext if y > ybase1 else -ext))
        self.line(x2, ybase2, x2, y + (ext if y > ybase2 else -ext))
        self.line(x1, y, x2, y)
        self.arrow(x2, y, x1, y); self.arrow(x1, y, x2, y)
        self.text((x1 + x2) / 2, y + 1, txt, h, ha="center")

    def dim_v(self, x, y1, y2, xbase, txt, h=3.5, ext=2):
        self.line(xbase, y1, x + (ext if x > xbase else -ext), y1)
        self.line(xbase, y2, x + (ext if x > xbase else -ext), y2)
        self.line(x, y1, x, y2)
        self.arrow(x, y2, x, y1); self.arrow(x, y1, x, y2)
        self.text(x - 1, (y1 + y2) / 2, txt, h, ha="center", va="bottom", rot=90)

    def leader(self, x0, y0, x1, y1, txt, h=5, shelf=None):
        """Линия-выноска с полкой и номером позиции (ГОСТ 2.316)."""
        self.circle(x0, y0, 0.6, fill="k")
        self.line(x0, y0, x1, y1)
        shelf = shelf or max(6, len(str(txt)) * h * 0.6)
        self.line(x1, y1, x1 + shelf, y1)
        self.text(x1 + shelf / 2, y1 + 0.8, txt, h, ha="center")

    def note_leader(self, x0, y0, x1, y1, txt, h=3.5, left=False):
        self.circle(x0, y0, 0.5, fill="k")
        self.line(x0, y0, x1, y1)
        wdt = len(txt) * h * 0.55
        if left:
            self.line(x1, y1, x1 - wdt, y1); self.text(x1 - wdt, y1 + 0.8, txt, h)
        else:
            self.line(x1, y1, x1 + wdt, y1); self.text(x1, y1 + 0.8, txt, h)

    def para(self, x, y, lines, h=3.5, width=180, lead=1.6):
        """Абзацы с переносом по ширине; возвращает y после последней строки."""
        for ln in lines:
            words, cur = ln.split(" "), ""
            out = []
            for wd in words:
                if cur and text_w(cur + " " + wd, h) > width:
                    out.append(cur); cur = wd
                else:
                    cur = (cur + " " + wd).strip()
            out.append(cur)
            for o in out:
                self.text(x, y, o, h); y -= h * lead
        return y

    def table(self, x, ytop, widths, rows, rh=7, h=3.5, header_rows=1, lw_head=S):
        """Таблица: rows — списки строк; возвращает y низа."""
        W = sum(widths); y = ytop
        for i, r in enumerate(rows):
            self.line(x, y, x + W, y, lw=lw_head if i <= header_rows else T)
            cx = x
            for wdt, c in zip(widths, r):
                if c not in (None, ""):
                    self.text(cx + 1.2, y - rh / 2 - h * 0.35, c, h, maxw=wdt - 2)
                cx += wdt
            y -= rh
        self.line(x, y, x + W, y, lw=lw_head)
        cx = x
        for wdt in [0] + widths:
            cx += wdt
            self.line(cx, ytop, cx, y, lw=lw_head)
        return y

    # --- вывод
    def render_mpl(self, pdf):
        fig = plt.figure(figsize=(self.w / 25.4, self.h / 25.4))
        ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, self.w); ax.set_ylim(0, self.h)
        ax.set_aspect("equal"); ax.axis("off")
        pt = 72 / 25.4
        for it in self.items:
            k = it[0]
            if k == "line":
                _, x1, y1, x2, y2, lw, ls = it
                ax.plot([x1, x2], [y1, y2], color="k", lw=lw * pt, ls=_ls(ls), solid_capstyle="butt")
            elif k == "poly":
                _, pts, lw, ls, closed, fill = it
                ax.add_patch(Polygon(pts, closed=closed, fill=fill is not None, fc=fill or "none",
                                     ec="k", lw=lw * pt, ls=_ls(ls)))
            elif k == "circle":
                _, x, y, r, lw, fill = it
                ax.add_patch(Circle((x, y), r, fill=fill is not None, fc=fill or "none", ec="k", lw=lw * pt))
            elif k == "text":
                _, x, y, s, h, ha, va, rot, bold = it
                ax.text(x, y, s, fontsize=fsize(h), ha=ha, va=va, rotation=rot,
                        rotation_mode="anchor", fontproperties=FP_B if bold else FP)
        pdf.savefig(fig); plt.close(fig)

    def render_dxf(self, path):
        import ezdxf
        doc = ezdxf.new("R2010", setup=True); msp = doc.modelspace()
        doc.layers.add("ОСНОВНАЯ", lineweight=70); doc.layers.add("ТОНКАЯ", lineweight=35)
        doc.styles.add("ГОСТ", font="isocpeur.ttf")
        lt = {"-": "CONTINUOUS", "--": "DASHED", "-.": "DASHDOT"}
        for it in self.items:
            k = it[0]
            if k == "line":
                _, x1, y1, x2, y2, lw, ls = it
                msp.add_line((x1, y1), (x2, y2), dxfattribs=dict(layer=_lay(lw), linetype=lt.get(ls, "CONTINUOUS")))
            elif k == "poly":
                _, pts, lw, ls, closed, fill = it
                p = msp.add_lwpolyline(pts, close=closed, dxfattribs=dict(layer=_lay(lw), linetype=lt.get(ls, "CONTINUOUS")))
                if fill:
                    hh = msp.add_hatch(color=7); hh.paths.add_polyline_path(pts, is_closed=True)
            elif k == "circle":
                _, x, y, r, lw, fill = it
                msp.add_circle((x, y), r, dxfattribs=dict(layer=_lay(lw)))
            elif k == "text":
                _, x, y, s, h, ha, va, rot, bold = it
                al = {("left", "baseline"): "LEFT", ("center", "baseline"): "CENTER",
                      ("right", "baseline"): "RIGHT", ("center", "center"): "MIDDLE_CENTER",
                      ("left", "center"): "MIDDLE_LEFT", ("center", "bottom"): "BOTTOM_CENTER",
                      ("left", "bottom"): "BOTTOM_LEFT"}.get((ha, va), "LEFT")
                t = msp.add_text(s, height=h, rotation=rot, dxfattribs=dict(style="ГОСТ", layer="ТОНКАЯ", width=0.8, oblique=15))
                t.set_placement((x, y), align=ezdxf.enums.TextEntityAlignment[al])
        doc.saveas(path)


def _ls(ls):
    return {"-": "-", "--": (0, (6, 3)), "-.": (0, (12, 3, 1.5, 3))}.get(ls, "-")


def _lay(lw):
    return "ОСНОВНАЯ" if lw >= 0.5 else "ТОНКАЯ"


# ====================================================================== формы
def frame(sh, fmt, first=True, designation="", g26=True):
    w, h = sh.w, sh.h
    sh.rect(20, 5, w - 25, h - 10, lw=S)
    sh.text(w - 60, 1.5, "Копировал", 3.5)
    sh.text(w - 30, 1.5, f"Формат  {fmt}", 3.5)
    # дополнительные графы (ГОСТ 2.104, форма 4/5)
    x0, x1, x2 = 8, 13, 20
    ys = [5, 30, 65, 90, 115, 150]
    names = ["Инв. № подл.", "Подп. и дата", "Взам. инв. №", "Инв. № дубл.", "Подп. и дата"]
    sh.line(x0, 5, x0, 150, lw=S); sh.line(x1, 5, x1, 150, lw=S)
    for i, y in enumerate(ys):
        sh.line(x0, y, x2, y, lw=S)
        if i < 5:
            sh.text(x1 - 1.3, (y + ys[i + 1]) / 2, names[i], 2.5, ha="center", va="baseline", rot=90)
    if first:
        sh.line(x0, h - 125, x0, h - 5, lw=S); sh.line(x1, h - 125, x1, h - 5, lw=S)
        for y in (h - 125, h - 65, h - 5):
            sh.line(x0, y, x2, y, lw=S)
        sh.text(x1 - 1.3, h - 35, "Перв. примен.", 2.5, ha="center", rot=90)
        sh.text(x1 - 1.3, h - 95, "Справ. №", 2.5, ha="center", rot=90)
        # графа 26 — обозначение, повёрнутое на 180°
    if first and g26:
        sh.rect(20, h - 19, 70, 14, lw=S)
        sh.text(55, h - 10, designation, 5, ha="center", rot=180)


def stamp1(sh, d, name, lit="", mass="", scale="", sheet=1, sheets=1, material="", org="", people=None):
    """Основная надпись формы 1 (185×55) — первый лист чертежа."""
    x0 = sh.w - 5 - 185; y0 = 5
    sh.rect(x0, y0, 185, 55, lw=S)
    # левый блок
    for dx in (7, 17, 40, 55, 65):
        sh.line(x0 + dx, y0, x0 + dx, y0 + 55, lw=S)
    for k in range(1, 11):
        sh.line(x0, y0 + 5 * k, x0 + 65, y0 + 5 * k, lw=S if k in (6, 7) else T)
    hdr = ["Изм.", "Лист", "№ докум.", "Подп.", "Дата"]; xs = [0, 7, 17, 40, 55]
    for t, xx in zip(hdr, xs):
        sh.text(x0 + xx + 0.8, y0 + 31.2, t, 2.5)
    roles = ["Разраб.", "Пров.", "Т.контр.", "", "Н.контр.", "Утв."]
    people = people or {}
    for i, r in enumerate(roles):
        yy = y0 + 25 - 5 * i + 1.2
        sh.text(x0 + 0.8, yy, r, 2.5)
        if people.get(r):
            sh.text(x0 + 17.8, yy, people[r], 2.5)
    # правый блок
    sh.line(x0 + 65, y0 + 40, x0 + 185, y0 + 40, lw=S)
    sh.line(x0 + 65, y0 + 15, x0 + 185, y0 + 15, lw=S)
    sh.line(x0 + 135, y0, x0 + 135, y0 + 40, lw=S)
    sh.line(x0 + 135, y0 + 35, x0 + 185, y0 + 35, lw=S)
    sh.line(x0 + 135, y0 + 20, x0 + 185, y0 + 20, lw=S)
    for dx in (150, 167):
        sh.line(x0 + dx, y0 + 20, x0 + dx, y0 + 40, lw=S)
    for dx in (140, 145):
        sh.line(x0 + dx, y0 + 20, x0 + dx, y0 + 35, lw=T)
    sh.line(x0 + 155, y0 + 15, x0 + 155, y0 + 20, lw=S)
    sh.text(x0 + 142.5, y0 + 36.2, "Лит.", 2.5, ha="center")
    sh.text(x0 + 158.5, y0 + 36.2, "Масса", 2.5, ha="center")
    sh.text(x0 + 176, y0 + 36.2, "Масштаб", 2.5, ha="center")
    sh.text(x0 + 137.5, y0 + 26, lit, 3.5, ha="center")
    sh.text(x0 + 158.5, y0 + 26, mass, 3.5, ha="center")
    sh.text(x0 + 176, y0 + 26, scale, 3.5, ha="center")
    sh.text(x0 + 136, y0 + 16.2, f"Лист  {sheet}", 2.5)
    sh.text(x0 + 157, y0 + 16.2, f"Листов  {sheets}", 2.5)
    sh.text(x0 + 125, y0 + 45.5, d, 7, ha="center")
    ny = y0 + 27.5 + 2.5 * (len(name) - 1)
    for ln in name:
        sh.text(x0 + 100, ny, ln, 5 if ln == name[0] else 3.5, ha="center", maxw=66); ny -= 6.5
    sh.text(x0 + 100, y0 + 6, material, 3.5, ha="center")
    sh.text(x0 + 160, y0 + 6, org, 5, ha="center")


def stamp2a(sh, d, sheet):
    """Основная надпись формы 2а (185×15) — последующие листы."""
    x0 = sh.w - 5 - 185; y0 = 5
    sh.rect(x0, y0, 185, 15, lw=S)
    for dx in (7, 17, 40, 55, 65, 175):
        sh.line(x0 + dx, y0, x0 + dx, y0 + 15, lw=S)
    for k in (5, 10):
        sh.line(x0, y0 + k, x0 + 65, y0 + k, lw=T if k == 10 else S)
    sh.line(x0 + 175, y0 + 8, x0 + 185, y0 + 8, lw=S)
    for t, xx in zip(["Изм.", "Лист", "№ докум.", "Подп.", "Дата"], [0, 7, 17, 40, 55]):
        sh.text(x0 + xx + 0.8, y0 + 1.2, t, 2.5)
    sh.text(x0 + 180, y0 + 9.5, "Лист", 2.5, ha="center")
    sh.text(x0 + 180, y0 + 2, str(sheet), 3.5, ha="center")
    sh.text(x0 + 120, y0 + 5, d, 7, ha="center")


def stamp2(sh, d, name, sheet=1, sheets=1, lit="", org="", people=None):
    """Основная надпись формы 2 (185×40) — первый лист текстового документа."""
    x0 = sh.w - 5 - 185; y0 = 5
    sh.rect(x0, y0, 185, 40, lw=S)
    for dx in (7, 17, 40, 55, 65):
        sh.line(x0 + dx, y0, x0 + dx, y0 + 40, lw=S)
    for k in range(1, 8):
        sh.line(x0, y0 + 5 * k, x0 + 65, y0 + 5 * k, lw=S if k in (5, 6) else T)
    for t, xx in zip(["Изм.", "Лист", "№ докум.", "Подп.", "Дата"], [0, 7, 17, 40, 55]):
        sh.text(x0 + xx + 0.8, y0 + 26.2, t, 2.5)
    people = people or {}
    for i, r in enumerate(["Разраб.", "Пров.", "", "Н.контр.", "Утв."]):
        sh.text(x0 + 0.8, y0 + 21.2 - 5 * i, r, 2.5)
        if people.get(r):
            sh.text(x0 + 17.8, y0 + 21.2 - 5 * i, people[r], 2.5)
    sh.line(x0 + 65, y0 + 25, x0 + 185, y0 + 25, lw=S)
    sh.line(x0 + 135, y0, x0 + 135, y0 + 25, lw=S)
    sh.line(x0 + 135, y0 + 20, x0 + 185, y0 + 20, lw=S)
    sh.line(x0 + 135, y0 + 15, x0 + 185, y0 + 15, lw=S)
    for dx in (150, 165):
        sh.line(x0 + dx, y0 + 15, x0 + dx, y0 + 25, lw=S)
    for dx in (140, 145):
        sh.line(x0 + dx, y0 + 15, x0 + dx, y0 + 20, lw=T)
    sh.text(x0 + 142.5, y0 + 21.2, "Лит.", 2.5, ha="center")
    sh.text(x0 + 157.5, y0 + 21.2, "Лист", 2.5, ha="center")
    sh.text(x0 + 175, y0 + 21.2, "Листов", 2.5, ha="center")
    sh.text(x0 + 137.5, y0 + 16.2, lit, 3.5, ha="center")
    sh.text(x0 + 157.5, y0 + 16.2, str(sheet), 3.5, ha="center")
    sh.text(x0 + 175, y0 + 16.2, str(sheets), 3.5, ha="center")
    sh.text(x0 + 125, y0 + 30.5, d, 7, ha="center")
    ny = y0 + 14 + 3 * (len(name) - 1)
    for ln in name:
        sh.text(x0 + 100, ny, ln, 5 if ln == name[0] else 3.5, ha="center", maxw=66); ny -= 6.5
    sh.text(x0 + 160, y0 + 6, org, 5, ha="center")


SPEC_W = [6, 6, 8, 70, 63, 10, 22]
SPEC_HDR = ["Формат", "Зона", "Поз.", "Обозначение", "Наименование", "Кол.", "Приме-\nчание"]


def spec_pages(designation, name, sections, org="", people=None):
    """Спецификация ГОСТ 2.106 форма 1/1а на листах А4. Возвращает список Sheet."""
    def wrap(txt, width, h):
        out = []
        for part in str(txt).split("\n"):
            cur = ""
            for wd in part.split(" "):
                if cur and text_w(cur + " " + wd, h) > width:
                    out.append(cur); cur = wd
                else:
                    cur = (cur + " " + wd).strip()
            out.append(cur)
        return out
    rows = []
    for title, items in sections:
        rows.append(("", "", "", "", "", "", ""))
        rows.append(("SECTION", title))
        rows.append(("", "", "", "", "", "", ""))
        for it in items:
            fmt, pos, oboz, nm, q, pr = it
            nl = wrap(nm, 60, 3.5); pl = wrap(pr, 20, 2.5) if pr else [""]
            for j in range(max(len(nl), len(pl))):
                rows.append((fmt if j == 0 else "", "", pos if j == 0 else "", oboz if j == 0 else "",
                             nl[j] if j < len(nl) else "", q if j == 0 else "", pl[j] if j < len(pl) else ""))
    pages, i = [], 0
    first_n, next_n = 29, 32
    chunks = [rows[:first_n]]
    rest = rows[first_n:]
    while rest:
        chunks.append(rest[:next_n]); rest = rest[next_n:]
    for pi, ch in enumerate(chunks):
        sh = Sheet(210, 297)
        frame(sh, "A4", first=(pi == 0), designation=designation, g26=False)
        x = 20; ytop = 292
        # шапка
        sh.line(x, ytop - 15, x + 185, ytop - 15, lw=S)
        cx = x
        for wdt, hd in zip(SPEC_W, SPEC_HDR):
            lines = hd.split("\n")
            if wdt <= 8:
                sh.text(cx + wdt / 2 + 1.2, ytop - 7.5, hd.replace("\n", ""), 2.5, ha="center", va="center", rot=90)
            else:
                for li, ln in enumerate(lines):
                    sh.text(cx + wdt / 2, ytop - 8.5 - 3.5 * li + 1.75 * (len(lines) - 1), ln, 3.5, ha="center")
            cx += wdt
        ybot = 45 if pi == 0 else 20
        y = ytop - 15
        for r in ch:
            y -= 8
            sh.line(x, y, x + 185, y, lw=T)
            if r[0] == "SECTION":
                sh.text(x + 20 + 70 + 31.5, y + 2.5, r[1], 3.5, ha="center")
                sh.line(x + 20 + 70 + 31.5 - len(r[1]) * 0.95, y + 1.8, x + 20 + 70 + 31.5 + len(r[1]) * 0.95, y + 1.8, lw=T)
                continue
            cx = x
            for wdt, c in zip(SPEC_W, r):
                if c:
                    hh = 3.5 if wdt > 10 or len(c) < 3 else 2.5
                    ha = "center" if wdt <= 10 else "left"
                    sh.text(cx + (wdt / 2 if ha == "center" else 1.5), y + 2.5, c, hh if wdt != 22 else 2.5, ha=ha,
                            maxw=wdt - 2)
                cx += wdt
        while y - 8 >= ybot - 0.01:
            y -= 8; sh.line(x, y, x + 185, y, lw=T)
        cx = x
        for wdt in [0] + SPEC_W:
            cx += wdt
            sh.line(cx, ytop, cx, ybot, lw=S)
        if pi == 0:
            stamp2(sh, designation, name, sheet=1, sheets=len(chunks), org=org, people=people)
        else:
            stamp2a(sh, designation, pi + 1)
        pages.append(sh)
    return pages


def save_pdf(sheets, path):
    with PdfPages(path) as pdf:
        for s in sheets:
            s.render_mpl(pdf)
