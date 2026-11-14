"""Desenha assets/terminal/contrib-heatmap.svg a partir de data/contributions.json.

As células entram em diagonal (CSS keyframes dentro do SVG) e congelam.
STATIC=1 gera um quadro sem animação, útil para pré-visualizar.
"""

import json
import os
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "assets" / "terminal" / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

W, H = 860, 218
CELL, GAP = 12, 3
STEP = CELL + GAP
X0, Y0 = 46, 46
RAMP = ["#1F1A33", "#3B2A78", "#5B3FC0", "#8B6CF0", "#C4B0FF"]
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def fmt(n):
    return f"{n:,}".replace(",", ".")


def plural(n, one, many):
    return f"{fmt(n)} {one if n == 1 else many}"


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    origin = first - timedelta(days=(first.weekday() + 1) % 7)  # domingo da 1ª semana

    cells, labels, seen_month = [], [], None
    for d in days:
        dt = date.fromisoformat(d["date"])
        col = (dt - origin).days // 7
        row = (dt.weekday() + 1) % 7
        x, y = X0 + col * STEP, Y0 + row * STEP
        style = "" if STATIC else f' style="animation-delay:{(col + row) * 14}ms"'
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{RAMP[min(d["level"], 4)]}"{style}>'
            f'<title>{d["date"]}: {d["count"]}</title></rect>'
        )
        if row == 0 and dt.month != seen_month:
            # evita rótulo espremido na borda esquerda/direita
            if seen_month is not None or dt.day <= 7:
                labels.append(f'<text class="l" x="{x}" y="{Y0 - 10}">{MONTHS[dt.month - 1]}</text>')
            seen_month = dt.month

    for row, name in ((1, "seg"), (3, "qua"), (5, "sex")):
        labels.append(f'<text class="l" x="{X0 - 30}" y="{Y0 + row * STEP + 10}">{name}</text>')

    ly = Y0 + 7 * STEP + 12
    lx = W - 28 - 5 * STEP - 44
    legend = [f'<text class="l" x="{lx - 44}" y="{ly + 10}">menos</text>']
    legend += [
        f'<rect x="{lx + i * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
        for i, c in enumerate(RAMP)
    ]
    legend.append(f'<text class="l" x="{lx + 5 * STEP + 4}" y="{ly + 10}">mais</text>')

    best = data["best_day"]
    bd = date.fromisoformat(best["date"])
    stats = (
        f'<tspan class="hi">{plural(data["total"], "contribuição", "contribuições")}</tspan> no último ano'
        f'  ·  sequência atual <tspan class="hi">{plural(data["current_streak"], "dia", "dias")}</tspan>'
        f'  ·  maior sequência <tspan class="hi">{plural(data["longest_streak"], "dia", "dias")}</tspan>'
        f'  ·  melhor dia <tspan class="hi">{best["count"]}</tspan> ({bd.day:02d}/{bd.month:02d})'
    )

    anim = "" if STATIC else """
.c{opacity:0;animation:drop .45s cubic-bezier(.2,.8,.2,1) both}
.f{opacity:0;animation:fade .6s ease-out 1.1s both}
@keyframes drop{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
@keyframes fade{to{opacity:1}}
@media (prefers-reduced-motion:reduce){.c,.f{animation:none;opacity:1}}"""

    label = f'{plural(data["total"], "contribuição", "contribuições")} no último ano'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Gráfico de contribuições no GitHub: {label}.">
<style>
text{{font-family:{MONO};font-size:11px}}
.l{{fill:#A6A0C4}} .s{{fill:#A6A0C4;font-size:12px}} .hi{{fill:#CDBFFD;font-weight:600}}{anim}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="#14111F" stroke="#2B2448" stroke-width="1.2"/>
{"".join(labels)}
{"".join(cells)}
<g class="f">{"".join(legend)}
<text class="s" x="{X0 - 30}" y="{H - 18}" xml:space="preserve">{stats}</text></g>
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
