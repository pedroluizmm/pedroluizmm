"""Desenha os cartões do README como SVGs animados em cards/.

Design "papel e tinta" inspirado no perfil de AVIVASHISHTA29: cartões claros,
Instrument Serif + Geist + Geist Mono e uma cor por bloco (azul, vermelho, amarelo).

Cada cartão é um SVG independente exibido via <img>, então só usa o que o GitHub
permite ali: animações CSS inline, SMIL e fontes embutidas como data URI (sem JS,
sem requisições externas). As fontes são subconjuntos WOFF em fonts/ (SIL OFL).

Os números vêm de data/contributions.json (fetch_contributions.py) e o retrato
de data/portrait.txt (make_portrait.py). Os textos ficam nas constantes abaixo.
Só usa a biblioteca padrão. STATIC=1 gera os cartões no estado final, sem animação.
"""

import base64
import json
import os
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
PORTRAIT = ROOT / "data" / "portrait.txt"
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
PAPER, PAPER_DEEP = "#f3f3f1", "#e2e2de"
INK, INK_SOFT, MUTED, RULE = "#111111", "#3a3a3c", "#6e6e73", "#dcdcd7"
BLUE, RED, YELLOW = "#2f55ff", "#ef3b2d", "#ffc81a"
COLORS = [(BLUE, "#ffffff"), (RED, "#ffffff"), (YELLOW, INK)]  # (fundo, texto)
RAMP = [PAPER_DEEP, "#c8d3ff", "#94a8ff", "#6280ff", BLUE]
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
def hero():
    h = 420
    rows = PORTRAIT.read_text(encoding="utf-8").split("\n") if PORTRAIT.exists() else []
    if rows and not rows[-1]:
        rows.pop()  # quebra de linha final
    cols = max((len(r) for r in rows), default=1)
    # desenhado num espaço de 800px e reduzido por transform (fontes minúsculas renderizam mal)
    art, size, px, py = 800, 328, 520, 46
    ch = art / max(len(rows), 1)  # retrato quadrado
    portrait = "".join(
        f'<text class="f" style="animation-delay:{0.25 + i * 0.018:.3f}s;animation-duration:.35s" '
        f'xml:space="preserve" x="0" y="{(i + 0.74) * ch:.1f}" textLength="{art}" '
        f'lengthAdjust="spacing">{escape(r.ljust(cols))}</text>'
        for i, r in enumerate(rows) if r.strip()
    )
    body = f"""
<defs>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">
    <stop offset="0" stop-color="{INK}"/><stop offset=".42" stop-color="{INK}"/>
    <stop offset=".5" stop-color="{BLUE}"/><stop offset=".58" stop-color="{INK}"/>
    <stop offset="1" stop-color="{INK}"/>
    {'' if STATIC else '<animateTransform attributeName="gradientTransform" type="translate" values="-600 0;600 0;600 0" keyTimes="0;.45;1" dur="7s" begin="1.6s" repeatCount="indefinite"/>'}
  </linearGradient>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<g class="f" {d(0)}>
  <rect class="live" x="48" y="49" width="8" height="8" rx="2" fill="{BLUE}"/>
  <text x="66" y="57" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">{escape(ROLE)}</text>
</g>
<text class="r" {d(0.15)} x="44" y="190" font-family="{SERIF}" font-size="116" letter-spacing="-2.5" fill="{INK}">{escape(FIRST)}</text>
<text class="r" {d(0.3)} x="44" y="290" font-family="{SERIF}" font-style="italic" font-size="116" letter-spacing="-2.5" fill="url(#shine)">{escape(LAST)}</text>
<g class="r" {d(0.55)}>
  {text_lines(48, 338, TAGLINE, 27, f'font-family="{SANS}" font-size="18" fill="{INK_SOFT}"')}
</g>
<g class="f" {d(0.8)}>
  <text x="48" y="396" font-family="{MONO}" font-size="13" fill="{INK}" xml:space="preserve">{escape(FOOT)}</text>
  <text class="nu" x="{48 + (len(FOOT) + 1) * 7.8:.0f}" y="396" font-family="{MONO}" font-size="13" fill="{BLUE}">&#8599;</text>
</g>
<g transform="translate({px} {py}) scale({size / art})" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{ch * 0.86:.1f}" fill="{INK}">{portrait}</g>
"""
    write("hero.svg", W, h, body, ALL_FONTS, HERO_LABEL)


# ---- 2 · gráfico de contribuições azul ----------------------------------------------
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
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<text class="r" {d(0.8)} x="42" y="62" font-family="{SERIF}" font-size="34" fill="{INK}">Dia a dia, <tspan font-style="italic" fill="{BLUE}">em azul</tspan></text>
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
        fill = BLUE if is_best else ("#c9c9c4" if total == 0 else INK)
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
                        f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{BLUE}">{fmt(total)}</text>')

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
        (f'{active}<tspan fill="#8e8e93"> / {len(data["days"])}</tspan>', "dias com contribuição"),
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
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<text class="f" {d(1.9)} x="40" y="58" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">OS ÚLTIMOS 12 MESES NO GITHUB</text>
<text class="r" {d(2.0)} x="38" y="114" font-family="{SERIF}" font-size="52" fill="{INK}">{fmt(data["total"])} <tspan font-style="italic">{word}</tspan></text>
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
<rect width="{JOB_W:.3f}" height="{JOB_H}" rx="14" fill="{PAPER}"/>
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
    fg = "#e6edf3" if theme == "dark" else INK
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
