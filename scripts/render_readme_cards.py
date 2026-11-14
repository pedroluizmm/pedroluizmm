"""Desenha os cartões do README como SVGs animados em cards/.

Layout inspirado no perfil de AVIVASHISHTA29, com paleta "pôr do sol" tirada do avatar:
cartões em degradê roxo, Instrument Serif + Geist + Geist Mono e laranja/magenta/violeta.

Cada cartão é um SVG independente exibido via <img>, então só usa o que o GitHub
permite ali: animações CSS inline, SMIL e fontes embutidas como data URI (sem JS,
sem requisições externas). As fontes são subconjuntos WOFF em fonts/ (SIL OFL).

Os números vêm de data/contributions.json (fetch_contributions.py) e
a moeda com o P é desenhada aqui mesmo. Os textos ficam nas constantes abaixo.
Só usa a biblioteca padrão. STATIC=1 gera os cartões no estado final, sem animação.
"""

import base64
import json
import math
import os
import random
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "cards"
FONTS = ROOT / "fonts"
STATIC = bool(os.environ.get("STATIC"))

# ---- conteúdo ------------------------------------------------------------------
ROLE = "DESENVOLVEDOR FULL STACK JÚNIOR"
FIRST, LAST = "Pedro", "Mariano"
TAGLINE = ["Construo aplicações web do front ao back-end,", "de interfaces a integrações de APIs."]
FOOT = "Fortaleza, Brasil  ·  LinkedIn"
HERO_LABEL = ("Pedro Luiz Mariano. Desenvolvedor Full Stack Júnior em Fortaleza, Brasil. "
              "Construo aplicações web do front ao back-end, de interfaces a integrações de APIs.")

# (arquivo, rótulo, grande, grande em itálico, texto)
TILES = [
    ("front", "FRONT-END", "React", "& Next.js",
     "TypeScript, JavaScript, Tailwind CSS, Sass/SCSS e styled-components."),
    ("back", "BACK-END", "Node", "& NestJS",
     "APIs REST, BFF, MongoDB e MySQL."),
    ("tools", "FERRAMENTAS", "Docker", "& Git",
     "Figma, Postman, Storybook e AWS Amplify."),
]

# (arquivo, nome, descrição, cargo)
JOBS = [
    ("webstore", "WebStore",
     "E-commerce, painel administrativo e PDV com Next.js, React e TypeScript.",
     "Estágio → Dev Júnior (PJ)"),
    ("spaceodyssey", "SpaceOdyssey",
     "TerraBrasilis: plataforma de gestão de eventos com Next.js, NestJS e MongoDB.",
     "Desenvolvedor Full Stack"),
    ("healthdev", "HealthDEV",
     "SaúdeHD: interfaces de aplicação web com React, TypeScript e Tailwind CSS.",
     "Desenvolvedor Front-end"),
]

# ---- tokens ---------------------------------------------------------------------
# paleta "pôr do sol" tirada do avatar: roxo profundo, magenta e laranja
NIGHT, DUSK, PLUM = "#1d0b2f", "#3b1033", "#2c0e45"  # fundo dos cartões (degradê)
INK, INK_SOFT, MUTED, RULE = "#fff6ec", "#ead9e8", "#c5aecb", "#5b3768"  # textos claros
ORANGE, AMBER, PINK, MAGENTA, VIOLET = "#ff8a1f", "#ffb347", "#ff4f8b", "#d633a8", "#7b2fd0"
BAR, EMPTY = "#6b2a8a", "#3a1a4c"
COLORS = [(ORANGE, NIGHT), (MAGENTA, "#ffffff"), (VIOLET, "#ffffff")]  # (fundo, texto)
RAMP = [EMPTY, "#a02c93", PINK, ORANGE, AMBER]
W = 880  # largura total: a coluna do README do GitHub a 100%
GAP = 12  # respiro entre cartões, embutido nos SVGs

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}
ALL_FONTS = ["serif", "serif-i", "sans", "mono"]

ANIMATED = ".r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro"
BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes nudgeup{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
@keyframes tilein{0%{opacity:0;transform:translateY(90px) scale(.6) rotate(-9deg)}55%{opacity:1;transform:translateY(-10px) scale(1.05) rotate(2deg)}75%{transform:translateY(3px) scale(.98) rotate(-.8deg)}90%{transform:translateY(-1px) scale(1.01) rotate(.2deg)}100%{opacity:1;transform:none}}
@keyframes slidein{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes arrowin{0%{opacity:0;transform:translateX(-30px)}60%{opacity:1;transform:translateX(6px)}100%{opacity:1;transform:none}}
@keyframes roll{from{transform:translateY(60px)}to{transform:none}}
@keyframes sheen{0%{transform:translateX(-260px) skewX(-20deg)}22%,100%{transform:translateX(420px) skewX(-20deg)}}
@keyframes ring{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.4)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudgeup 1.8s ease-in-out infinite}
.ti{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:tilein 1.1s cubic-bezier(.2,.8,.2,1) both}
.sl{opacity:0;transform-box:fill-box;animation:slidein .6s cubic-bezier(.2,.7,.2,1) both}
.ai{opacity:0;transform-box:fill-box;animation:arrowin .7s cubic-bezier(.2,.7,.2,1) both}
.ro{transform-box:fill-box;animation:roll .8s cubic-bezier(.15,.8,.2,1) both}
.sh{animation:sheen 5s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1s ease-out both}
"""
FROZEN = ANIMATED + "{animation:none!important;opacity:1!important;transform:none!important}.sh,.rg{display:none}"
BASE_CSS += "@media (prefers-reduced-motion: reduce){" + FROZEN + "}"


def card(w, h, wave=True, flip=False):
    """Fundo do cartão: degradê roxo, borda laranja->magenta e ondas no canto."""
    a = min(130, h * 0.42)
    waves = (
        f'<g clip-path="url(#cclip)">'
        f'<path d="M{w * .42:.0f} {h} C{w * .62:.0f} {h - a * .1:.0f},{w * .78:.0f} {h - a * .95:.0f},{w} {h - a:.0f} L{w} {h} Z" fill="{MAGENTA}" opacity=".30"/>'
        f'<path d="M{w * .60:.0f} {h} C{w * .76:.0f} {h - a * .05:.0f},{w * .86:.0f} {h - a * .6:.0f},{w} {h - a * .62:.0f} L{w} {h} Z" fill="url(#cwave)" opacity=".85"/>'
        f'</g>' if wave else "")
    if wave and flip:  # onda no canto inferior esquerdo
        waves = waves.replace('<g clip-path="url(#cclip)">', f'<g clip-path="url(#cclip)"><g transform="translate({w} 0) scale(-1 1)">', 1).replace('</g>', '</g></g>', 1)
    return (
        f'<defs><linearGradient id="cbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{DUSK}"/>'
        f'<stop offset=".55" stop-color="{NIGHT}"/><stop offset="1" stop-color="{PLUM}"/></linearGradient>'
        f'<linearGradient id="cbd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ORANGE}"/>'
        f'<stop offset=".5" stop-color="{MAGENTA}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
        f'<linearGradient id="cwave" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{MAGENTA}"/>'
        f'<stop offset="1" stop-color="{ORANGE}"/></linearGradient>'
        f'<clipPath id="cclip"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>'
        f'<rect width="{w}" height="{h}" rx="14" fill="url(#cbg)"/>{waves}'
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="13.25" fill="none" stroke="url(#cbd)" stroke-width="1.5"/>'
    )


def font_face(keys):
    out = []
    for k in keys:
        fam, style, weight, fn = FONT_FILES[k]
        b64 = base64.b64encode((FONTS / fn).read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                   f"src:url(data:font/woff;base64,{b64}) format('woff')}}")
    return "".join(out)


def write(name, w, h, body, fonts, label, left=0, right=0, bottom=GAP):
    """Cartão w x h desenhado em x=left num canvas transparente, com respiro para as linhas encaixarem."""
    if left:
        body = f'<g transform="translate({left} 0)">{body}</g>'
    w, h = w + left + right, h + bottom
    css = font_face(fonts) + BASE_CSS + (FROZEN if STATIC else "")
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}" '
        f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
        f"<style>{css}</style>{body}</svg>",
        encoding="utf-8",
    )
    print(f"cards/{name}")


def d(s):
    return f'style="animation-delay:{s:.2f}s"'


def wrap(text, n):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > n:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line] if line else lines


def text_lines(x, y, lines, lh, attrs):
    return "".join(f'<text x="{x}" y="{y + i * lh}" {attrs}>{escape(l)}</text>' for i, l in enumerate(lines))


def fmt(n):
    return f"{n:,}".replace(",", ".")


# ---- 1 · hero ---------------------------------------------------------------------
def p_coin(cx, cy, r=118, thick=18, dur=11, layers=16, samples=72):
    """Moeda dourada minimalista com um "P". Gira 360° em falso 3D: cada camada da borda
    é um círculo achatado (escala X = cos θ) e deslocado (x = z·sen θ), o que dá corpo à
    moeda. Frente e verso trocam no meio do giro; o verso é desenhado espelhado para o P
    sempre aparecer legível. Tudo em SMIL, funciona dentro do <img> do GitHub."""
    thetas = [2 * math.pi * i / samples for i in range(samples + 1)]

    def spin(z):
        """Animações de escala + deslocamento para uma camada na profundidade z."""
        if STATIC:
            return "", ""
        tr = ";".join(f"{z * math.sin(t):.2f} 0" for t in thetas)
        sc = ";".join(f"{math.cos(t):.3f} 1" for t in thetas)
        return (f'<animateTransform attributeName="transform" type="translate" values="{tr}" dur="{dur}s" repeatCount="indefinite"/>',
                f'<animateTransform attributeName="transform" type="scale" values="{sc}" dur="{dur}s" repeatCount="indefinite"/>')

    def show(front):
        if STATIC:
            return ""
        vals = "1;0;1" if front else "0;1;0"
        return (f'<animate attributeName="opacity" values="{vals}" keyTimes="0;.25;.75" calcMode="discrete" '
                f'dur="{dur}s" repeatCount="indefinite"/>')

    # borda: camadas do fundo para a frente, um pouco mais claras perto das faces
    edge = []
    for i in range(layers):
        z = -thick / 2 + thick * i / (layers - 1)
        shade = 1 - abs(z) / (thick / 2)
        col = "#8a4600" if i % 2 else "#9c5300"
        col = "#b8650c" if shade > .7 else col
        tr, sc = spin(z)
        edge.append(f'<g>{tr}<circle r="{r}" fill="{col}">{sc}</circle></g>')

    def face(mirror):
        flip = ' transform="scale(-1 1)"' if mirror else ""
        return f"""
<circle r="{r}" fill="url(#gold)"/>
<circle r="{r - 10}" fill="url(#face)" stroke="#ffe08a" stroke-width="1.6"/>
<circle r="{r - 17}" fill="none" stroke="{AMBER}" stroke-width="1" stroke-opacity=".55"/>
<g{flip}>
  <g stroke="#ffd36b" stroke-width="6" stroke-linecap="round">
    <line x1="-12" y1="-74" x2="-12" y2="-56"/><line x1="8" y1="-74" x2="8" y2="-56"/>
    <line x1="-12" y1="48" x2="-12" y2="66"/><line x1="8" y1="48" x2="8" y2="66"/>
  </g>
  <g font-family="{SERIF}" font-size="168" text-anchor="middle">
    <text x="4" y="58" fill="#3a1a06">P</text>
    <text x="0" y="54" fill="url(#gold)" stroke="#fff1c2" stroke-width="1.2">P</text>
  </g>
</g>
<ellipse cx="-38" cy="-58" rx="62" ry="22" transform="rotate(-35 -38 -58)" fill="#fff" opacity=".10"/>"""

    ftr, fsc = spin(thick / 2)
    btr, bsc = spin(-thick / 2)
    pulse = "" if STATIC else '<animate attributeName="opacity" values="1;.55;1" dur="4s" repeatCount="indefinite"/>'
    return f"""
<defs>
  <radialGradient id="gold" cx=".35" cy=".3" r=".8">
    <stop offset="0" stop-color="#fff0b0"/><stop offset=".45" stop-color="{AMBER}"/>
    <stop offset=".8" stop-color="{ORANGE}"/><stop offset="1" stop-color="#a14d00"/>
  </radialGradient>
  <radialGradient id="face" cx=".4" cy=".35" r=".9">
    <stop offset="0" stop-color="#6b3a12"/><stop offset=".7" stop-color="#3f1d0c"/><stop offset="1" stop-color="#2a1208"/>
  </radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="{ORANGE}" stop-opacity=".45"/>
    <stop offset=".6" stop-color="{MAGENTA}" stop-opacity=".12"/><stop offset="1" stop-color="{MAGENTA}" stop-opacity="0"/></radialGradient>
</defs>
<g class="f" {d(0.4)}><g transform="translate({cx} {cy})">
  <circle r="{r * 1.5:.0f}" fill="url(#halo)">{pulse}</circle>
  {''.join(edge)}
  <g opacity="0">{btr}<g>{bsc}{face(True)}</g>{show(False)}</g>
  <g>{ftr}<g>{fsc}{face(False)}</g>{show(True)}</g>
</g></g>
"""


def hero():
    h = 420
    body = f"""
<defs>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">
    <stop offset="0" stop-color="{ORANGE}"/><stop offset=".42" stop-color="{ORANGE}"/>
    <stop offset=".5" stop-color="#ffe2a8"/><stop offset=".58" stop-color="{ORANGE}"/>
    <stop offset="1" stop-color="{ORANGE}"/>
    {'' if STATIC else '<animateTransform attributeName="gradientTransform" type="translate" values="-600 0;600 0;600 0" keyTimes="0;.45;1" dur="7s" begin="1.6s" repeatCount="indefinite"/>'}
  </linearGradient>
</defs>
{card(W, h)}
<g class="f" {d(0)}>
  <rect class="live" x="48" y="49" width="8" height="8" rx="2" fill="{ORANGE}"/>
  <text x="66" y="57" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">{escape(ROLE)}</text>
</g>
<text class="r" {d(0.15)} x="44" y="190" font-family="{SERIF}" font-size="116" letter-spacing="-2.5" fill="{INK}">{escape(FIRST)}</text>
<text class="r" {d(0.3)} x="44" y="290" font-family="{SERIF}" font-style="italic" font-size="116" letter-spacing="-2.5" fill="url(#shine)">{escape(LAST)}</text>
<g class="r" {d(0.55)}>
  {text_lines(48, 338, TAGLINE, 27, f'font-family="{SANS}" font-size="18" fill="{INK_SOFT}"')}
</g>
<g class="f" {d(0.8)}>
  <text x="48" y="396" font-family="{MONO}" font-size="13" fill="{INK}" xml:space="preserve">{escape(FOOT[:-8])}<tspan fill="{ORANGE}" font-weight="700">{escape(FOOT[-8:])}</tspan></text>
  <text class="nu" x="{48 + (len(FOOT) + 1) * 7.8:.0f}" y="396" font-family="{MONO}" font-size="13" fill="{ORANGE}">&#8599;</text>
</g>
{p_coin(690, 208)}
"""
    write("hero.svg", W, h, body, ALL_FONTS, HERO_LABEL)


# ---- 2 · gráfico de contribuições ----------------------------------------------
def heatmap(data):
    days = data["days"]
    lead = (date.fromisoformat(days[0]["date"]).weekday() + 1) % 7  # domingo = 0
    cell, step, gx, gy = 12, 15, 44, 96
    cells, months, seen = [], [], set()
    for i, day in enumerate(days):
        col, row = divmod(i + lead, 7)
        dt = date.fromisoformat(day["date"])
        if dt.day <= 7 and (dt.year, dt.month) not in seen and row == 0:
            seen.add((dt.year, dt.month))
            months.append((col, MONTHS[dt.month - 1]))
        cells.append(
            f'<rect class="p" style="animation-delay:{1.0 + col * 0.03 + row * 0.02:.2f}s" x="{gx + col * step}" '
            f'y="{gy + row * step}" width="{cell}" height="{cell}" rx="3" fill="{RAMP[min(day["level"], 4)]}">'
            f'<title>{dt.day:02d}/{dt.month:02d}/{dt.year}: {day["count"]}</title></rect>'
        )
    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    ly = gy + 7 * step
    labels = "".join(
        f'<text x="{gx + col * step}" y="{ly + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">{m}</text>'
        for col, m in months if col < ncols - 12
    )
    legend_x = right - len(RAMP) * 14 - 34
    legend = "".join(
        f'<rect x="{legend_x + i * 14}" y="{ly + 6}" width="11" height="11" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(RAMP)
    )
    h = ly + 44
    body = f"""
{card(W, h, wave=False)}
<text class="r" {d(0.8)} x="42" y="62" font-family="{SERIF}" font-size="34" fill="{INK}">Dia a dia, <tspan font-style="italic" fill="{PINK}">no código</tspan></text>
<text class="f" {d(0.8)} x="{right}" y="60" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">ATUALIZADO DIARIAMENTE</text>
{''.join(cells)}
<g class="f" {d(2.4)}>{labels}
<text x="{legend_x - 8}" y="{ly + 16}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">menos</text>
{legend}
<text x="{legend_x + len(RAMP) * 14 + 2}" y="{ly + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">mais</text></g>
"""
    write("heatmap.svg", W, h, body, ["serif", "serif-i", "mono"],
          f'Gráfico de contribuições: {fmt(data["total"])} contribuições no último ano')


# ---- 3 · atividade (barras por mês) ---------------------------------------------------
def activity(data):
    h = 340
    totals = {}
    for day in data["days"]:
        totals[day["date"][:7]] = totals.get(day["date"][:7], 0) + day["count"]
    monthly = sorted(totals.items())[-12:]
    top = max(t for _, t in monthly) or 1
    best_i = max(range(len(monthly)), key=lambda i: monthly[i][1])
    x0, x1, base, maxh, gap = 40, 600, 292, 140, 10
    bw = (x1 - x0 - gap * (len(monthly) - 1)) / len(monthly)
    bars = []
    for i, (month, total) in enumerate(monthly):
        bh = max(4, round(total / top * maxh))
        x = x0 + i * (bw + gap)
        is_best = i == best_i and total > 0
        fill = ORANGE if is_best else (EMPTY if total == 0 else BAR)
        label = MONTHS[int(month[5:]) - 1]
        delay = 2.2 + i * 0.07
        bars.append(
            f'<rect class="g" style="animation-delay:{delay:.2f}s" x="{x:.1f}" y="{base - bh}" width="{bw:.1f}" '
            f'height="{bh}" rx="4" fill="{fill}"><title>{label}: {fmt(total)}</title></rect>'
            f'<text class="f" style="animation-delay:{delay:.2f}s" x="{x + bw / 2:.1f}" y="{base + 22}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{label}</text>'
        )
        if is_best:
            bars.append(f'<text class="p" style="animation-delay:3.2s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" '
                        f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{ORANGE}">{fmt(total)}</text>')

    cs, ls = data["current_streak"], data["longest_streak"]
    if cs and cs >= ls:
        streak, note = cs, "de sequência atual, a maior"
    elif cs:
        streak, note = cs, f"de sequência atual, maior {ls}"
    else:
        streak, note = ls, "na maior sequência"
    active = sum(1 for day in data["days"] if day["count"])
    stats = [
        (f'{streak} <tspan font-style="italic">{"dia" if streak == 1 else "dias"}</tspan>', note),
        (f'{active}<tspan fill="{MUTED}"> / {len(data["days"])}</tspan>', "dias com contribuição"),
        (f'{data["best_day"]["count"]}', "no dia mais ativo"),
    ]
    side = []
    for i, (big, small) in enumerate(stats):
        y = 104 + i * 92
        side.append(f'<g class="r" {d(2.6 + i * 0.15)}>'
                    f'<text x="650" y="{y}" font-family="{SERIF}" font-size="40" fill="{INK}">{big}</text>'
                    f'<text x="650" y="{y + 24}" font-family="{SANS}" font-size="13" fill="{MUTED}">{small}</text></g>')
        if i < 2:
            side.append(f'<rect class="f" {d(2.6)} x="650" y="{y + 44}" width="190" height="1" fill="{RULE}"/>')
    word = "contribuição" if data["total"] == 1 else "contribuições"
    body = f"""
{card(W, h, flip=True)}
<text class="f" {d(1.9)} x="40" y="58" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">OS ÚLTIMOS 12 MESES NO GITHUB</text>
<text class="r" {d(2.0)} x="38" y="114" font-family="{SERIF}" font-size="52" fill="{INK}">{fmt(data["total"])} <tspan font-style="italic" fill="{ORANGE}">{word}</tspan></text>
{''.join(bars)}
{''.join(side)}
"""
    write("activity.svg", W, h, body, ALL_FONTS, f'{fmt(data["total"])} {word} no último ano, por mês')


# ---- 4 · blocos de stack ------------------------------------------------------------------
TILE_W, TILE_H = W / 3 - 8, 210  # dois respiros de 12px ao longo da linha


def tile(pos, name, label, big, italic, blurb):
    color, on = COLORS[pos]
    delay = 3.1 + pos * 0.25
    blurb_svg = "".join(
        f'<text class="r" {d(delay + 0.75 + i * 0.1)} x="24" y="{150 + i * 20}" font-family="{SANS}" '
        f'font-size="14" fill="{on}" opacity=".92">{escape(l)}</text>'
        for i, l in enumerate(wrap(blurb, 34))
    )
    body = f"""
<defs>
  <clipPath id="card"><rect width="{TILE_W:.3f}" height="{TILE_H}" rx="14"/></clipPath>
  <clipPath id="slot"><rect x="0" y="62" width="{TILE_W:.3f}" height="62"/></clipPath>
  <linearGradient id="gl" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g class="ti" {d(delay)}>
  <g clip-path="url(#card)">
    <rect width="{TILE_W:.3f}" height="{TILE_H}" fill="{color}"/>
    <circle class="rg" {d(delay + 0.5)} cx="{TILE_W - 40:.1f}" cy="{TILE_H - 40}" r="60" fill="none" stroke="{on}" stroke-opacity=".5" stroke-width="2"/>
    <rect class="sh" style="animation-delay:{delay + 1.4:.2f}s" x="0" y="-20" width="90" height="{TILE_H + 40}" fill="url(#gl)" transform="translate(-260 0)"/>
  </g>
  <text class="sl" {d(delay + 0.35)} x="24" y="38" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{on}">{escape(label)}</text>
  <g clip-path="url(#slot)"><g class="ro" {d(delay + 0.45)}>
    <text x="22" y="112" font-family="{SERIF}" font-size="42" fill="{on}">{escape(big)} <tspan font-style="italic">{escape(italic)}</tspan></text>
  </g></g>
  {blurb_svg}
</g>
"""
    write(f"{name}.svg", TILE_W, TILE_H, body, ALL_FONTS, f"{label}: {big} {italic}. {blurb}",
          left=4 * pos, right=8 - 4 * pos)


# ---- 5 · experiência ------------------------------------------------------------------------
JOB_W, JOB_H = W / 3 - 8, 176


def job_card(pos, name, title, desc, role):
    body = f"""
{card(round(JOB_W, 3), JOB_H, wave=False)}
<g class="r" {d(4.6 + pos * 0.12)}>
  <rect x="24" y="30" width="8" height="8" rx="2" fill="{COLORS[pos][0]}"/>
  <text x="40" y="39" font-family="{SANS}" font-weight="600" font-size="18" fill="{INK}">{escape(title)}</text>
  {text_lines(24, 72, wrap(desc, 34), 21, f'font-family="{SANS}" font-size="14" fill="{INK_SOFT}"')}
  <text x="24" y="{JOB_H - 24}" font-family="{MONO}" font-size="12" fill="{MUTED}">{escape(role)}</text>
</g>
"""
    write(f"exp-{name}.svg", JOB_W, JOB_H, body, ["sans", "sans-b", "mono"], f"{title}: {desc} {role}.",
          left=4 * pos, right=8 - 4 * pos)


def section_title(name, text, italic, theme):
    fg = "#e6edf3" if theme == "dark" else "#111111"
    body = (f'<text class="r" {d(4.4)} x="2" y="46" font-family="{SERIF}" font-size="34" fill="{fg}">{escape(text)} '
            f'<tspan font-style="italic">{escape(italic)}</tspan></text>')
    write(f"title-{name}-{theme}.svg", W, 64, body, ["serif", "serif-i"], f"{text} {italic}", bottom=0)


if __name__ == "__main__":
    data = json.loads(DATA.read_text(encoding="utf-8"))
    hero()
    heatmap(data)
    activity(data)
    for i, t in enumerate(TILES):
        tile(i, *t)
    for theme in ("dark", "light"):
        section_title("exp", "Onde", "trabalhei", theme)
    for i, j in enumerate(JOBS):
        job_card(i, *j)
