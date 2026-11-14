"""Desenha contrib-heatmap.svg a partir de data/contributions.json.

Janela de terminal com o calendário de contribuições (53 semanas x 7 dias).
As células entram em diagonal uma única vez (CSS keyframes) e congelam.
STATIC=1 gera um quadro sem animação, útil para pré-visualizar.
"""

import json
import os
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
STATIC = bool(os.environ.get("STATIC"))

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP = 12, 3
STEP = CELL + GAP
PAD, LEFT_LABEL_W, TOP_LABEL_H, TITLEBAR_H = 22, 30, 20, 30

BG, BG2, FRAME = "#0a0e14", "#0d1420", "#1f6feb"
MUTED, ACCENT, GREEN, GOLD = "#7d8590", "#22d3ee", "#39d353", "#f2cc60"
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
COL_T, ROW_T, CELL_DUR = 0.018, 0.045, 0.42


def fmt(n):
    return f"{n:,}".replace(",", ".")


def dias(n):
    return f"{n} dia" if n == 1 else f"{n} dias"


def br(iso):
    d = date.fromisoformat(iso)
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    origin = first - timedelta(days=(first.weekday() + 1) % 7)  # domingo da 1ª semana
    n_cols = (date.fromisoformat(days[-1]["date"]) - origin).days // 7 + 1

    w = PAD + LEFT_LABEL_W + n_cols * STEP + PAD
    h = TITLEBAR_H + TOP_LABEL_H + 7 * STEP + 88 + PAD
    grid_top, grid_left = TITLEBAR_H + TOP_LABEL_H, PAD + LEFT_LABEL_W

    css = "" if STATIC else (
        "<style>@keyframes cell{0%{opacity:0;transform:translateY(-6px)}100%{opacity:1;transform:translateY(0)}}"
        f".c{{opacity:0;animation:cell {CELL_DUR}s cubic-bezier(.2,.8,.2,1) both}}"
        "@media (prefers-reduced-motion:reduce){.c{animation:none;opacity:1}}</style>"
    )
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        css,
        f'<defs><linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/>'
        f'<stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{w}" height="{h}" rx="12" fill="url(#hbg)"/>',
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.55"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{w}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>',
    ]
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{c}"/>')
    p.append(f'<text x="{w / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">'
             f'pedro@github: ~/contributions --graph</text>')

    for row, name in ((1, "seg"), (3, "qua"), (5, "sex")):
        p.append(f'<text x="{PAD}" y="{grid_top + row * STEP + CELL * 0.78:.1f}" fill="{MUTED}" font-size="9">{name}</text>')

    seen = set()
    for d in days:
        dt = date.fromisoformat(d["date"])
        col, row = (dt - origin).days // 7, (dt.weekday() + 1) % 7
        x, y = grid_left + col * STEP, grid_top + row * STEP
        key = (dt.year, dt.month)
        if key not in seen and dt.day <= 7:
            seen.add(key)
            p.append(f'<text x="{x}" y="{TITLEBAR_H + 14}" fill="{MUTED}" font-size="10">{MONTHS[dt.month - 1]}</text>')
        style = "" if STATIC else f' style="animation-delay:{col * COL_T + row * ROW_T:.3f}s"'
        p.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                 f'fill="{PALETTE[min(d["level"], 5)]}"{style}><title>{br(d["date"])}: {d["count"]}</title></rect>')

    leg_y = grid_top + 7 * STEP + 6
    leg_x = w - PAD - (len(PALETTE) * (CELL - 1) + 70)
    p.append(f'<text x="{leg_x}" y="{leg_y + CELL * 0.8:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">menos</text>')
    lx = leg_x + 8
    for c in PALETTE:
        p.append(f'<rect x="{lx}" y="{leg_y}" width="{CELL - 1}" height="{CELL - 1}" rx="2.2" fill="{c}"/>')
        lx += CELL
    p.append(f'<text x="{lx + 4}" y="{leg_y + CELL * 0.8:.1f}" fill="{MUTED}" font-size="10">mais</text>')

    sep_y = leg_y + CELL + 14
    p.append(f'<line x1="0" y1="{sep_y}" x2="{w}" y2="{sep_y}" stroke="{FRAME}" stroke-opacity="0.25"/>')

    best = data["best_day"]
    ly = sep_y + 24
    p.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{GREEN}"><tspan font-weight="700">{fmt(data["total"])}</tspan>'
             f'<tspan fill="{MUTED}"> contribuições no último ano</tspan></text>')
    p.append(f'<text x="{w - PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">'
             f'{br(days[0]["date"])} &#8594; {br(days[-1]["date"])}</text>')
    ly += 24
    p.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{MUTED}" xml:space="preserve">sequência atual '
             f'<tspan fill="{ACCENT}" font-weight="700">{dias(data["current_streak"])}</tspan>   &#183;   maior '
             f'<tspan fill="{ACCENT}" font-weight="700">{dias(data["longest_streak"])}</tspan></text>')
    p.append(f'<text x="{w - PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">melhor dia '
             f'<tspan fill="{GOLD}" font-weight="700">{best["count"]}</tspan> em {br(best["date"])}</text>')
    p.append("</svg>")

    OUT.write_text("".join(p), encoding="utf-8")
    print(f"-> {OUT} ({w}x{h})")


if __name__ == "__main__":
    main()
