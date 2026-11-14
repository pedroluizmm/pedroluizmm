"""Gera assets/terminal/info-card.svg: cartão estilo neofetch com os dados do perfil.

Edite ROWS para mudar o conteúdo. Cada linha entra com fade + slide escalonado.
STATIC=1 gera um quadro sem animação.
"""

import os
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "terminal" / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

W, H = 490, 400
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

TITLE = "pedro@github: ~"
HEADER = ("pedro", "github")
# (chave, valor) — None insere uma linha em branco
ROWS = [
    ("Nome", "Pedro Luiz Mariano"),
    ("Cargo", "Desenvolvedor Full Stack Júnior"),
    ("Local", "Fortaleza, Brasil"),
    ("Formação", "Ciência da Computação · Unifor (2027.1)"),
    None,
    ("Agora", "Arquitetura, testes automatizados e cloud"),
    ("Antes", "WebStore · SpaceOdyssey · HealthDEV"),
    None,
    ("Front", "React, Next.js, TypeScript, Tailwind CSS"),
    ("Back", "Node.js, NestJS, MongoDB, MySQL"),
    ("Langs", "TypeScript, JavaScript, Python, Java"),
    ("Tools", "Docker, Git, Figma, Storybook, AWS Amplify"),
    None,
    ("Status", "Disponível para oportunidades júnior"),
]
SWATCHES = ["#3B2A78", "#5B3FC0", "#8B6CF0", "#A78BFA", "#C4B0FF", "#EEEBFA"]


def main():
    x, y, lh = 22, 62, 20.5
    lines = []

    def add(inner, yy):
        style = "" if STATIC else f' style="animation-delay:{250 + len(lines) * 90}ms"'
        lines.append(f'<g class="ln"{style}><text x="{x}" y="{yy:.1f}" xml:space="preserve">{inner}</text></g>')

    user, host = HEADER
    add(f'<tspan class="k">{user}</tspan><tspan class="d">@</tspan><tspan class="k">{host}</tspan>', y)
    y += lh
    add(f'<tspan class="d">{"-" * (len(user) + len(host) + 1)}</tspan>', y)
    y += lh
    for row in ROWS:
        if row:
            key, val = row
            add(f'<tspan class="k">{escape(key)}</tspan><tspan class="d">:</tspan>{" " * (9 - len(key))}'
                f'<tspan class="v">{escape(val)}</tspan>', y)
            y += lh
        else:
            y += lh * 0.45

    y += 2
    style = "" if STATIC else f' style="animation-delay:{250 + len(lines) * 90}ms"'
    sw = "".join(
        f'<rect x="{x + i * 26}" y="{y - 12:.1f}" width="26" height="16" fill="{c}"/>'
        for i, c in enumerate(SWATCHES)
    )
    lines.append(f'<g class="ln"{style}>{sw}</g>')

    anim = "" if STATIC else """
.ln{opacity:0;animation:in .4s ease-out both}
@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.ln{animation:none;opacity:1}}"""

    label = "; ".join(f"{r[0]}: {r[1]}" for r in ROWS if r)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(label)}">
<style>
text{{font-family:{MONO};font-size:13px}}
.k{{fill:#A78BFA;font-weight:600}} .v{{fill:#EEEBFA}} .d{{fill:#6F6890}} .t{{fill:#A6A0C4;font-size:12px}}{anim}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="#14111F" stroke="#2B2448" stroke-width="1.2"/>
<path d="M1.6 32H{W - 1.6}" stroke="#2B2448" stroke-width="1.2"/>
<circle cx="22" cy="17" r="5.5" fill="#FF5F57"/><circle cx="40" cy="17" r="5.5" fill="#FEBC2E"/><circle cx="58" cy="17" r="5.5" fill="#28C840"/>
<text class="t" x="{W / 2}" y="21" text-anchor="middle">{escape(TITLE)}</text>
{chr(10).join(lines)}
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
