"""Gera info-card.svg: painel estilo neofetch que fica à direita do retrato ASCII.

Conteúdo escrito à mão em ROWS. As linhas entram com fade + slide escalonado
e congelam. STATIC=1 gera um quadro sem animação.
"""

import html
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = bool(os.environ.get("STATIC"))

W, H = 480, 400
PAD, TITLEBAR_H = 20, 30
KEY_X, VAL_X = PAD, PAD + 104
LINE_H = 19

BG, BG2, FRAME = "#0d1117", "#111722", "#30363d"
MUTED, INK = "#7d8590", "#c9d1d9"
KEY, SECTION, GREEN, ACCENT = "#ffa657", "#58a6ff", "#3fb950", "#22d3ee"

# ("host",) cabeçalho · ("kv", chave, valor) · ("sec", título) · ("bul", texto) · ("gap",)
ROWS = [
    ("host",),
    ("kv", "Nome", "Pedro Luiz Mariano"),
    ("kv", "Cargo", "Desenvolvedor Full Stack Júnior"),
    ("kv", "Local", "Fortaleza, Brasil"),
    ("kv", "Edu", "Ciência da Computação, Unifor '27.1"),
    ("gap",),
    ("sec", "Experiência"),
    ("kv", "WebStore", "E-commerce, painel admin e PDV"),
    ("kv", "SpaceOdyssey", "TerraBrasilis · gestão de eventos"),
    ("kv", "HealthDEV", "SaúdeHD · front-end em React"),
    ("gap",),
    ("sec", "Stack"),
    ("kv", "Frontend", "React, Next.js, TypeScript, Tailwind"),
    ("kv", "Backend", "Node.js, NestJS, MongoDB, MySQL"),
    ("kv", "Tools", "Docker, Git, Figma, AWS Amplify"),
    ("gap",),
    ("sec", "Em foco"),
    ("bul", "Arquitetura de software, testes e cloud"),
    ("bul", "Disponível para oportunidades júnior"),
]


def rise(inner, i):
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.06
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


def main():
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<defs><linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/>'
        f'<stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{c}"/>')
    p.append(f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">pedro@github: ~$ neofetch</text>')

    y = TITLEBAR_H + 30
    for i, row in enumerate(ROWS):
        kind = row[0]
        if kind == "gap":
            y += LINE_H * 0.5
            continue
        if kind == "host":
            inner = (f'<text x="{KEY_X}" y="{y:.1f}" font-size="14" font-weight="700"><tspan fill="{GREEN}">pedro</tspan>'
                     f'<tspan fill="{MUTED}">@</tspan><tspan fill="{ACCENT}">github</tspan></text>'
                     f'<line x1="{KEY_X + 112}" y1="{y - 4:.1f}" x2="{W - PAD}" y2="{y - 4:.1f}" stroke="{FRAME}" stroke-opacity="0.8"/>')
        elif kind == "sec":
            inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">&#8212; {html.escape(row[1])}</text>'
                     f'<line x1="{KEY_X + 24 + len(row[1]) * 8}" y1="{y - 4:.1f}" x2="{W - PAD}" y2="{y - 4:.1f}" stroke="{FRAME}" stroke-opacity="0.8"/>')
        elif kind == "kv":
            inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{html.escape(row[1])}</text>'
                     f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">{html.escape(row[2])}</text>')
        else:
            inner = (f'<circle cx="{KEY_X + 3}" cy="{y - 4:.1f}" r="2.5" fill="{GREEN}"/>'
                     f'<text x="{KEY_X + 14}" y="{y:.1f}" fill="{INK}" font-size="12.5">{html.escape(row[1])}</text>')
        p.append(rise(inner, i))
        y += LINE_H
    p.append("</svg>")

    OUT.write_text("".join(p), encoding="utf-8")
    print(f"-> {OUT} ({W}x{H}, conteúdo até y={round(y)})")


if __name__ == "__main__":
    main()
