"""Converte uma foto em retrato ASCII animado: assets/terminal/ascii.svg.

Uso (local, requer Pillow):  python scripts/make_ascii_svg.py foto.png [--green]
Cada linha é "impressa" da esquerda para a direita com um cursor (SMIL),
de cima para baixo, e o resultado congela. STATIC=1 gera um quadro parado.
"""

import os
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

OUT = Path(__file__).resolve().parent.parent / "assets" / "terminal" / "ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

W, H = 370, 400
COLS = 68
RAMP = " .`:-=+*cox#%@"  # esparso -> denso
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
PAD_X, TOP = 14, 44
FONT = 8.0


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    inner_w = W - 2 * PAD_X
    inner_h = H - TOP - 12
    rows = 44
    lh = inner_h / rows

    rgb = Image.open(sys.argv[1]).convert("RGB")
    # --green usa só o canal verde: destaca tons de pele e apaga fundos
    # vermelhos/roxos saturados (bom para avatares ilustrados).
    img = rgb.getchannel("G") if "--green" in sys.argv else ImageOps.grayscale(rgb)
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.resize((COLS, rows), Image.LANCZOS)
    px = img.load()

    # O cartão é escuro: pixel claro -> glifo denso, pixel escuro -> vazio.
    out = []
    for r in range(rows):
        line = "".join(
            RAMP[min(len(RAMP) - 1, int((px[c, r] / 255) ** 1.25 * len(RAMP)))] for c in range(COLS)
        )
        y = TOP + r * lh
        text = (
            f'<text x="{PAD_X}" y="{y + lh * 0.8:.1f}" textLength="{inner_w}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{escape(line)}</text>'
        )
        if STATIC:
            out.append(text)
            continue
        begin, dur = 0.2 + r * 0.055, 0.5
        out.append(
            f'<clipPath id="r{r}"><rect x="{PAD_X}" y="{y:.1f}" width="0" height="{lh + 1:.1f}">'
            f'<animate attributeName="width" from="0" to="{inner_w}" begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>'
            f'</rect></clipPath><g clip-path="url(#r{r})">{text}</g>'
            f'<rect y="{y:.1f}" x="{PAD_X}" width="5" height="{lh:.1f}" fill="#A78BFA" opacity="0">'
            f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X + inner_w}" begin="{begin:.2f}s" dur="{dur}s"/>'
            f'<set attributeName="opacity" to="1" begin="{begin:.2f}s" dur="{dur}s"/></rect>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Retrato de Pedro Luiz Mariano em arte ASCII.">
<style>
text{{font-family:{MONO};font-size:{FONT}px;fill:#CDBFFD}}
.t{{fill:#A6A0C4;font-size:12px}}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="#14111F" stroke="#2B2448" stroke-width="1.2"/>
<path d="M1.6 32H{W - 1.6}" stroke="#2B2448" stroke-width="1.2"/>
<circle cx="22" cy="17" r="5.5" fill="#FF5F57"/><circle cx="40" cy="17" r="5.5" fill="#FEBC2E"/><circle cx="58" cy="17" r="5.5" fill="#28C840"/>
<text class="t" x="{W / 2}" y="21" text-anchor="middle">pedro.png</text>
{chr(10).join(out)}
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
