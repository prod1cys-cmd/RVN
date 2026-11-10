# -*- coding: utf-8 -*-
"""
Генератор КД на кабели К4, К5, К6, К10, К14 рабочего места АРБМ.468915.018:
  • сборочные чертежи СБ (А3) — PDF и DXF (для импорта в КОМПАС);
  • спецификации по ГОСТ 2.106 (А4) — PDF и CSV;
  • сводный текст КД_кабели.md (спецификации, таблицы соединений, ТТ).
Запуск:  python kd_cables.py [папка_вывода]
Требуется: matplotlib, ezdxf (pip install matplotlib ezdxf).
"""
import os, sys, csv
from eskd import Sheet, S, T, frame, stamp1, stamp2a, spec_pages, save_pdf
import kd_data as D

OUT = sys.argv[1] if len(sys.argv) > 1 else "КД_кабели"
PEOPLE = {}            # {"Разраб.": "Фамилия", ...} — при необходимости заполнить


# ====================================================================== элементы
def sma_plug(sh, x, y, flip=False):
    """Вилка SMA (условно, М 2:1): гайка 8 мм + корпус. x — торец гайки."""
    s = -1 if flip else 1
    nut = (x, x + s * 9); body = (x + s * 9, x + s * 21)
    sh.rect(min(nut), y - 5, 9, 10, lw=S)
    for k in (-2.5, 2.5):
        sh.line(min(nut), y + k, max(nut), y + k, lw=T)
    sh.rect(min(body), y - 3.5, 12, 7, lw=S)
    return x + s * 21


def cable_break(sh, x, y, half):
    """Обрыв (волнистая линия) по ГОСТ 2.303."""
    pts = [(x + 1.2 * ((-1) ** i), y - half - 2 + i * (2 * half + 4) / 6) for i in range(7)]
    sh.poly(pts, lw=T)


def label_tube(sh, x, y, w, txt, h=6):
    sh.rect(x, y - h / 2, w, h, lw=S, fill="white")
    sh.text(x + w / 2, y - 1.0, txt, 2.5, ha="center", maxw=w - 1.5)


# ====================================================================== К4–К6
def draw_rf(k):
    d = D.RF[k]; C = D.COAX; num = D.NUM[k]
    sh = Sheet(420, 297)
    frame(sh, "A3", True, num + "СБ")
    y = 245
    # --- общий вид (условно, с разрывом)
    x1 = sma_plug(sh, 32, y)                       # XW1
    r = 1.7
    sh.line(x1, y + r, 92, y + r, lw=S); sh.line(x1, y - r, 92, y - r, lw=S)
    cable_break(sh, 94, y, r); cable_break(sh, 98, y, r)
    sh.line(100, y + r, 150, y + r, lw=S); sh.line(100, y - r, 150, y - r, lw=S)
    x2 = sma_plug(sh, 171, y, flip=True)           # XW2 (гайка справа)
    # переход
    ax0 = 171
    sh.rect(ax0, y - 6, 8, 12, lw=S)                # розетка SMA перехода (гайка)
    if "BNC" in d["adapter"]:
        sh.rect(ax0 + 8, y - 5, 14, 10, lw=S); sh.rect(ax0 + 22, y - 6.5, 8, 13, lw=S)
        for yy in (y - 6.5, y + 6.5):
            sh.line(ax0 + 24, yy, ax0 + 28, yy - (1.5 if yy > y else -1.5), lw=T)
        xend = ax0 + 30
    else:
        sh.rect(ax0 + 8, y - 6, 10, 12, lw=S); sh.rect(ax0 + 18, y - 9, 12, 18, lw=S)
        for k2 in (-4, 0, 4):
            sh.line(ax0 + 18, y + k2, ax0 + 30, y + k2, lw=T)
        xend = ax0 + 30
    sh.line(25, y, xend + 6, y, lw=0.18, ls="-.")
    # бирки
    label_tube(sh, 58, y, 22, d["label"])
    label_tube(sh, 122, y, 22, d["label"])
    # обозначения
    sh.text(38, y + 9, "XW1", 3.5, ha="center")
    sh.text(160, y + 9, "XW2", 3.5, ha="center")
    sh.text(40, y - 13, "К плате ПОС", 2.5); sh.text(40, y - 16.5, d["board"], 2.5)
    sh.text(150, y - 13, "К прибору", 2.5); sh.text(150, y - 16.5, d["dev"].split(",")[0], 2.5)
    # размеры
    sh.dim_h(32, 171, y + 22, y + 5, y + 5, f"{C['L']}±{C['tol']}")
    sh.dim_h(53, 58, y - 26, y - 5, y - 3, "20…30*", h=2.5)
    sh.dim_h(58, 80, y + 13, y + 3, y + 3, "30*", h=2.5)
    # выноски
    sh.leader(110, y + r, 116, y + 12, "1")
    sh.leader(26 + 15, y - 5, 22, y - 30, "2")
    sh.leader(186, y + 6, 194, y + 16, "3")
    sh.leader(133, y - 3, 138, y - 30, "4")
    sh.line(32, y - 6, 32, y - 22, lw=T); sh.arrow(32, y - 22, 32, y - 7)
    sh.text(34, y - 21, "А", 5)
    sh.text(110, y - 40, "Изображение условное, с разрывом", 2.5, ha="center")

    # --- вид А: разделка (М 5:1)
    M = 5; cy = 150; xe = 150                    # торец кабеля по x = xe
    Rt, Rd, Rc = C["d_tube"] / 2 * M, C["d_diel"] / 2 * M, C["d_center"] / 2 * M
    xl = xe - 105                                 # начало изображённого участка
    # трубка (разрез, верх/низ)
    for sgn in (1, -1):
        sh.rect(xl, cy + sgn * Rd if sgn > 0 else cy - Rt, xe - xl, Rt - Rd, lw=S)
        sh.hatch(xl, cy + Rd if sgn > 0 else cy - Rt, xe - xl, Rt - Rd, step=1.4)
    # диэлектрик
    sh.line(xl, cy + Rd, xe, cy + Rd, lw=S); sh.line(xl, cy - Rd, xe, cy - Rd, lw=S)
    sh.line(xe, cy - Rt, xe, cy + Rt, lw=S)
    for yy in range(int(cy - Rd) + 1, int(cy + Rd), 2):
        if abs(yy - cy) > Rc + 0.4:
            sh.line(xl + 4, yy, xe - 2, yy, lw=0.13, ls="--")
    # центральная жила с конусом 90°
    A = C["strip_a"] * M
    sh.line(xl, cy + Rc, xe + A - Rc, cy + Rc, lw=S); sh.line(xl, cy - Rc, xe + A - Rc, cy - Rc, lw=S)
    sh.poly([(xe + A - Rc, cy + Rc), (xe + A, cy), (xe + A - Rc, cy - Rc)], lw=S)
    cable_break(sh, xl, cy, Rt)
    sh.line(xl - 6, cy, xe + A + 8, cy, lw=0.18, ls="-.")
    # зона зачистки Б
    B = C["clean_b"] * M
    sh.line(xe - B, cy + Rt, xe - B, cy + Rt + 4, lw=T)
    sh.dim_h(xe - B if xe - B > xl else xl + 2, xe, cy + Rt + 12, cy + Rt, cy + Rt,
             f"Б = {C['clean_b']:g} (зачистить, облудить)", h=3.5)
    sh.dim_h(xe, xe + A, cy - Rt - 10, cy - Rc, cy - Rc, f"А = {C['strip_a']:g}*".replace(".", ","), h=3.5)
    sh.dim_v(xe + A + 18, cy - Rt, cy + Rt, xe, f"⌀{C['d_tube']}*".replace(".", ","))
    sh.dim_v(xe + A + 30, cy - Rd, cy + Rd, xe, f"⌀{C['d_diel']}*".replace(".", ","))
    sh.text(xl + 2, cy + Rt + 24, "А (5:1)", 5)
    sh.text(xl + 2, cy + Rt + 18, "Разделка кабеля под вилку SMA-JB6 (оба конца)", 3.5)
    sh.note_leader(xe - 40, cy + Rt - 1, xe - 50, cy - Rt - 22, "Трубка медная (внешний проводник)", left=True)
    sh.note_leader(xe - 25, cy + Rd - 4, xe - 30, cy - Rt - 30, "Диэлектрик ПТФЭ — торец заподлицо с трубкой", left=True)
    sh.note_leader(xe + 6, cy, xe + 10, cy - Rt - 38, f"Жила ⌀{C['d_center']}* сталемедная посеребр., конус 90°".replace("0.9", "0,9"))

    # --- ТТ
    tt = D.tt_rf(k)
    yy = 287
    xt = 230
    for i, s in enumerate(tt, 1):
        yy = sh.para(xt, yy, [f"{i} {s}"], h=3.5, width=178) - 1
    # --- основная надпись
    stamp1(sh, num + "СБ", [d["title"], "Сборочный чертеж"], scale="1:1; 5:1", org=D.ORG, people=PEOPLE)
    return [sh]


# ====================================================================== К10
def db_hood(sh, x, y, w, h):
    sh.poly([(x, y - h / 2), (x + w, y - h / 2 + 2), (x + w, y + h / 2 - 2), (x, y + h / 2)], lw=S, closed=True)
    sh.rect(x - 3, y - h / 2 - 1.5, 3, h + 3, lw=S)          # фланец/винты


def draw_k10():
    K = D.K10; num = D.NUM["К10"]; q = D.k10_qty()
    sh = Sheet(420, 297); frame(sh, "A3", True, num + "СБ")
    yc = 200
    # X6
    db_hood(sh, 27, yc, 22, 30)
    sh.text(33, yc + 19, "X6", 3.5, ha="center")
    sh.text(24, yc - 24, "К плате ПОС", 2.5); sh.text(24, yc - 27.5, "(DB-25F)", 2.5)
    # ствол в оплётке
    tr0, tr1 = 49, 138; R = 3
    for s_ in (1, -1):
        sh.line(tr0, yc + s_ * R, 88, yc + s_ * R, lw=S); sh.line(94, yc + s_ * R, tr1, yc + s_ * R, lw=S)
    cable_break(sh, 89, yc, R); cable_break(sh, 93, yc, R)
    for xx in range(tr0 + 8, tr1 - 4, 4):
        if not 84 < xx < 96:
            sh.line(xx, yc - R, xx + 3, yc + R, lw=0.13); sh.line(xx + 3, yc - R, xx, yc + R, lw=0.13)
    sh.rect(tr0, yc - R - 0.8, 6, 2 * R + 1.6, lw=S)          # ТУТ на торце оплётки
    sh.rect(tr1 - 6, yc - R - 0.8, 6, 2 * R + 1.6, lw=S)
    label_tube(sh, 58, yc, 24, K["label_main"], h=8)
    # ветви
    ys = [yc + 66 - i * 22 for i in range(7)]
    xb = 170
    for (des, lab, kind, item), yb in zip(D.K10_BRANCHES, ys):
        sh.line(tr1, yc + (yb - yc) * 0.05, 152, yb, lw=S)
        sh.line(152, yb, xb, yb, lw=S)
        if kind == "DB-9F":
            db_hood(sh, xb + 12, yb, -12, 14)
            sh.text(xb + 16, yb + 1, des, 3.5); sh.text(xb + 16, yb - 3.5, lab.split(". ")[1], 2.5)
        else:
            sh.rect(xb, yb - 2.5, 10, 5, lw=S)                  # зона сростков (ТУТ поз. 13)
            sh.line(xb + 10, yb, xb + 22, yb, lw=S)
            cable_break(sh, xb + 23, yb, 2); cable_break(sh, xb + 26, yb, 2)
            sh.line(xb + 27, yb, xb + 30, yb, lw=S)
            sh.rect(xb + 30, yb - 3, 8, 6, lw=S)                 # USB-A
            sh.text(xb + 13, yb + 2.5, des, 3.5); sh.text(xb + 40, yb - 1.0, "USB-A", 2.5)
            sh.text(xb + 11, yb - 6, item.split(" (")[0], 2.2)
        label_tube(sh, 153, yb, 16, lab.split(". ")[1], h=5)
    # размеры
    sh.dim_h(27, xb, yc - 86, yc - 16, ys[-1] - 8, f"{K['L']}±{K['tol']}")
    sh.dim_h(27, tr1, yc - 52, yc - 16, yc - 4, f"{K['trunk']}*")
    sh.dim_h(tr1, xb, yc - 76, yc - 4, ys[-1] - 8, f"{K['branch']}*", h=2.5)
    # выноски
    sh.leader(38, yc + 13, 31, yc + 40, "3,4")
    sh.leader(110, yc + R, 106, yc + 26, "1,2")
    sh.leader(118, yc - R, 114, yc - 30, "14")
    sh.leader(tr1 - 3, yc + R + 0.8, 128, yc + 46, "13")
    sh.leader(xb + 4, ys[0] + 6, xb - 6, ys[0] + 14, "5,6", shelf=8)
    sh.leader(xb + 5, ys[2] + 2.5, xb + 14, ys[2] + 11, "7, 13", shelf=11)
    sh.leader(xb + 5, ys[3] + 2.5, xb + 14, ys[3] + 11, "8", shelf=6)
    sh.leader(xb + 5, ys[4] + 2.5, xb + 14, ys[4] + 11, "9", shelf=6)
    sh.leader(165, ys[5], 160, ys[5] - 11, "15", shelf=7)
    sh.leader(158, ys[6] + 2.5, 142, ys[6] - 12, "12", shelf=7)
    sh.text(90, yc - 96, "Изображение условное, с разрывом", 2.5, ha="center")
    # узел скрутки
    yt = 72; x0t = 40
    import math
    pts1 = [(x0t + t, yt + 2.2 * math.sin(t / 17.5 * 2 * math.pi)) for t in [i * 0.5 for i in range(141)]]
    pts2 = [(x0t + t, yt - 2.2 * math.sin(t / 17.5 * 2 * math.pi)) for t in [i * 0.5 for i in range(141)]]
    sh.poly(pts1, lw=S); sh.poly(pts2, lw=S)
    sh.dim_h(x0t, x0t + 17.5, yt + 9, yt + 2.5, yt + 2.5, "15…20", h=2.5)
    sh.text(x0t, yt + 20, "Скрутка пар П1–П2, П3–П4, П9–П10, П11–П12, П19–П20 (условно)", 3.5)
    # ТТ
    yy = 287
    for i, s in enumerate(D.tt_k10(), 1):
        yy = sh.para(230, yy, [f"{i} {s}"], h=3.5, width=178) - 1
    stamp1(sh, num + "СБ", [K["title"], "Сборочный чертеж"], sheet=1, sheets=2, scale="1:2", org=D.ORG, people=PEOPLE)

    # ---- лист 2: таблица соединений
    s2 = Sheet(420, 297); frame(s2, "A3", False)
    s2.text(30, 280, "Таблица соединений кабеля К10", 5)
    rows = [["Провод", "X6 (DB-25F), конт.", "Цепь", "Марка провода, бирка", "Куда", "Примечание"]]
    for w, pin, net, to, note in D.K10_WIRES:
        rows.append([w, str(pin) if pin else "X1.1:3", net, f"МГТФ 0,2; «{w}»", to, note])
    y = s2.table(25, 274, [16, 42, 32, 42, 82, 52], rows, rh=7.2, h=3.2)
    s2.text(30, y - 10, "Неиспользуемые провода кабелей FTDI (обрезать, изолировать по п. 8 ТТ)", 3.5)
    rows2 = [["Ветвь", "Изделие", "Провода"]]
    for br, wires in D.K10_UNUSED_FTDI.items():
        item = [b[3] for b in D.K10_BRANCHES if b[0] == br][0].split(" (")[0]
        rows2.append([br, item, ", ".join(wires)])
    y2 = s2.table(25, y - 14, [16, 60, 190], rows2, rh=7, h=3.2)
    s2.text(30, y2 - 10, "Розетки DB-9F X1.1, X1.2 — распиновка CiA 303-1: конт. 2 — CAN_L, 7 — CAN_H, 3 — CAN_GND. "
                       "X5 (IZP): конт. 1 — IZP_P, 2 — IZP_N.", 3.5)
    s2.text(30, y2 - 16, "Длина каждого провода П1–П20 — " + f"{q['Lw']} мм, П21 — {q['Lj']} мм (с припуском 5 %).", 3.5)
    stamp2a(s2, num + "СБ", 2)
    return [sh, s2]


# ====================================================================== К14
def draw_k14():
    K = D.K14; num = D.NUM["К14"]; q = D.k14_qty()
    sh = Sheet(420, 297); frame(sh, "A3", True, num + "СБ")
    yc = 215
    # X1, X2 (MTA-156)
    for des, net, yy in (("X1", "GND", yc + 18), ("X2", "+12VA", yc - 18)):
        sh.rect(30, yy - 5, 12, 10, lw=S); sh.line(36, yy - 5, 36, yy + 5, lw=T)
        sh.text(36, yy + 7, f"{des} «{net}»", 3.5, ha="center")
        for k2 in (-2, 2):
            sh.line(42, yy + k2, 60, yc + k2 * 0.6 + (2 if yy > yc else -2), lw=S)
    # ствол
    R = 2.5
    for s_ in (1, -1):
        sh.line(60, yc + s_ * R, 104, yc + s_ * R, lw=S); sh.line(110, yc + s_ * R, 160, yc + s_ * R, lw=S)
    cable_break(sh, 105, yc, R); cable_break(sh, 109, yc, R)
    for xx in range(66, 156, 4):
        if not 100 < xx < 112:
            sh.line(xx, yc - R, xx + 3, yc + R, lw=0.13); sh.line(xx + 3, yc - R, xx, yc + R, lw=0.13)
    sh.rect(60, yc - R - 0.8, 5, 2 * R + 1.6, lw=S); sh.rect(155, yc - R - 0.8, 5, 2 * R + 1.6, lw=S)
    label_tube(sh, 72, yc, 22, K["label"], h=7)
    # наконечники
    ends = [("XT3", "GND", yc + 21), ("XT4", "GND", yc + 7), ("XT5", "+12В", yc - 7), ("XT6", "+12В", yc - 21)]
    for des, net, yy in ends:
        sh.line(160, yc + (yy - yc) * 0.1, 176, yy, lw=S)
        sh.rect(176, yy - 2, 10, 4, lw=S, fill="0.75" if net == "GND" else "white")
        sh.circle(191, yy, 4.5, lw=S); sh.circle(191, yy, 2.1, lw=S)
        sh.text(197, yy - 1.2, f"{des} «{net}»", 3)
    label_tube(sh, 128, yc, 22, K["label"], h=7)
    # размеры
    sh.dim_h(30, 195.5, yc - 40, yc - 23, yc - 25, f"{K['L']}±{K['tol']}")
    # выноски
    sh.leader(36, yc + 23, 26, yc + 40, "2")
    sh.leader(90, yc + R, 87, yc + 22, "1")
    sh.leader(118, yc - R, 114, yc - 26, "8")
    sh.leader(157, yc + R + 0.8, 150, yc + 22, "7")
    sh.leader(181, yc + 21 + 2, 174, yc + 34, "3", shelf=6)
    sh.leader(181, yc - 21 - 2, 174, yc - 34, "4", shelf=6)
    sh.leader(138, yc - 3.5, 134, yc - 18, "6", shelf=6)
    sh.text(110, yc - 50, "Изображение условное, с разрывом", 2.5, ha="center")
    # схема запараллеливания
    sh.text(30, 150, "Схема соединений (запараллеливание цепей питания)", 3.5)
    for i, (w, frm, net, to, note) in enumerate(D.K14_WIRES):
        yy = 138 - i * 9
        sh.text(30, yy - 1.2, frm, 3.5); sh.line(45, yy, 120, yy, lw=S); sh.text(80, yy + 1, w, 3, ha="center")
        sh.text(123, yy - 1.2, to.split(" →")[0].split(" (")[0], 3.5)
    for a, b, lab in ((138, 129, "CH1−"), (120, 111, "CH1+")):
        sh.line(140, a, 150, a, lw=T); sh.line(140, b, 150, b, lw=T); sh.line(150, a, 150, b, lw=S)
        sh.line(150, (a + b) / 2, 158, (a + b) / 2, lw=S); sh.circle(160, (a + b) / 2, 2, lw=S)
        sh.text(164, (a + b) / 2 - 1.2, f"A8 {lab}", 3.5)
    # таблица соединений
    rows = [["Провод", "Откуда", "Цепь", "Марка, бирка", "Куда", "Примечание"]]
    for w, frm, net, to, note in D.K14_WIRES:
        rows.append([w, frm, net, f"МГТФ 0,5; «{w}»", to, note])
    sh.text(30, 92, "Таблица соединений", 3.5)
    sh.table(25, 88, [14, 16, 16, 30, 72, 26], rows, rh=7, h=3)
    yy = 287
    for i, s in enumerate(D.tt_k14(), 1):
        yy = sh.para(230, yy, [f"{i} {s}"], h=3.5, width=178) - 1
    stamp1(sh, num + "СБ", [K["title"], "Сборочный чертеж"], scale="1:2", org=D.ORG, people=PEOPLE)
    return [sh]


# ====================================================================== вывод
def write_csv(path, sections):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Раздел", "Формат", "Поз.", "Обозначение", "Наименование", "Кол.", "Примечание"])
        for title, items in sections:
            for fmt, pos, oboz, nm, qty, pr in items:
                w.writerow([title, fmt, pos, oboz, nm.replace("\n", " "), qty, pr])


def md_spec(sections):
    out = ["| Формат | Поз. | Обозначение | Наименование | Кол. | Примечание |", "|---|---|---|---|---|---|"]
    for title, items in sections:
        out.append(f"| | | | **{title}** | | |")
        for fmt, pos, oboz, nm, qty, pr in items:
            out.append(f"| {fmt} | {pos} | {oboz} | {nm.replace(chr(10), ' ')} | {qty} | {pr} |")
    return "\n".join(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for k in ("К4", "К5", "К6"):
        jobs.append((k, D.RF[k]["title"], draw_rf(k), D.spec_rf(k), D.tt_rf(k)))
    jobs.append(("К10", D.K10["title"], draw_k10(), D.spec_k10(), D.tt_k10()))
    jobs.append(("К14", D.K14["title"], draw_k14(), D.spec_k14(), D.tt_k14()))

    md = [f"# КД на кабели рабочего места {D.BASE}\n"]
    allpdf = []
    for k, title, sheets, spec, tt in jobs:
        num = D.NUM[k]
        save_pdf(sheets, os.path.join(OUT, f"{num}СБ {k}.pdf"))
        for i, s in enumerate(sheets, 1):
            s.render_dxf(os.path.join(OUT, f"{num}СБ {k} лист{i}.dxf"))
        sp = spec_pages(num, [title, ""][:1], spec, org=D.ORG, people=PEOPLE)
        save_pdf(sp, os.path.join(OUT, f"{num} {k} спецификация.pdf"))
        write_csv(os.path.join(OUT, f"{num} {k} спецификация.csv"), spec)
        allpdf += sp + sheets
        md.append(f"## {k} — {title} ({num})\n")
        md.append("### Спецификация\n\n" + md_spec(spec) + "\n")
        if k == "К10":
            md.append("### Таблица соединений\n\n| Провод | X6, конт. | Цепь | Провод, бирка | Куда | Примечание |\n|---|---|---|---|---|---|")
            for w, pin, net, to, note in D.K10_WIRES:
                md.append(f"| {w} | {pin if pin else 'X1.1:3'} | {net} | МГТФ 0,2, «{w}» | {to} | {note} |")
            md.append("")
        if k == "К14":
            md.append("### Таблица соединений\n\n| Провод | Откуда | Цепь | Провод, бирка | Куда | Примечание |\n|---|---|---|---|---|---|")
            for w, frm, net, to, note in D.K14_WIRES:
                md.append(f"| {w} | {frm} | {net} | МГТФ 0,5, «{w}» | {to} | {note} |")
            md.append("")
        md.append("### Технические требования\n")
        md += [f"{i}. {s}" for i, s in enumerate(tt, 1)]
        md.append("")
    save_pdf(allpdf, os.path.join(OUT, "Комплект КД кабели (все листы).pdf"))
    with open(os.path.join(OUT, "КД_кабели.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("Готово:", OUT)


if __name__ == "__main__":
    main()
