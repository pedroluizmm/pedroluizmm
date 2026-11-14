"""Converte uma foto em retrato ASCII monocromático animado: ascii.svg.

Uso (local, requer Pillow):  python scripts/make_ascii_svg.py foto.png [--green]

Uma cor só, fundo apagado. Cada linha é revelada da esquerda para a direita
com um cursor (SMIL), de cima para baixo; imprime uma vez e congela.
STATIC=1 gera um quadro parado.

Padrão: foto com fundo branco/removido (escuro -> glifo denso, claro -> vazio).
--green: usa o canal verde invertido, que isola tons de pele e apaga fundos
vermelhos/roxos saturados (bom para avatares ilustrados).
"""

import html
import os
import sys
from pathlib import Path

from PIL import Image, ImageOps

OUT = Path(__file__).resolve().parent.parent / "ascii.svg"
STATIC = bool(os.environ.get("STATIC"))

COLS = int(os.environ.get("COLS", 120))
CELL_W = 800 / COLS
CELL_H = CELL_W * 15 / 8
ROWS = round(COLS * 8 / 15)
RAMP = " .`:-=+*cs#%@"  # claro (esparso) -> escuro (denso)
GAMMA = 1.18
WHITE_FLOOR = 0.80  # luminância acima disso vira espaço

PAD, TITLEBAR_H, STATUS_H = 20, 30, 30
ART_W, ART_H = COLS * CELL_W, ROWS * CELL_H
W, H = ART_W + PAD * 2, TITLEBAR_H + ART_H + STATUS_H + PAD

BG, BG2, FRAME = "#0d1117", "#111722", "#30363d"
MUTED, INK = "#7d8590", "#c9d1d9"
ROW_DUR = 5.8 / ROWS  # retrato inteiro em ~6s; um único cursor descendo
NAME = "Pedro Luiz Mariano"
PROMPT = "pedro@github:~$ whoami "


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    rgb = Image.open(args[0]).convert("RGB")
    if "--green" in sys.argv:
        im = ImageOps.invert(ImageOps.autocontrast(rgb.getchannel("G"), cutoff=2))
    else:
        im = ImageOps.autocontrast(ImageOps.grayscale(rgb), cutoff=1)
    px = im.resize((COLS, ROWS), Image.LANCZOS).load()

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/>'
        f'<stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{W:.0f}" height="{H:.0f}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1:.0f}" height="{H - 1:.0f}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W:.0f}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{c}"/>')
    p.append(f'<text x="{W / 2:.0f}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="18" '
             f'text-anchor="middle">pedro@github: ~$ ./portrait.sh</text>')

    top = TITLEBAR_H + PAD * 0.35
    for r in range(ROWS):
        chars = []
        for c in range(COLS):
            lum = (px[c, r] / 255) ** GAMMA
            chars.append(" " if lum >= WHITE_FLOOR else RAMP[round((1 - lum) * (len(RAMP) - 1))])
        row_y = top + r * CELL_H
        text = (f'<text xml:space="preserve" x="{PAD}" y="{row_y + CELL_H * 0.74:.1f}" fill="{INK}" '
                f'font-size="{CELL_H * 0.86:.1f}" textLength="{ART_W:.0f}" lengthAdjust="spacing">'
                f'{html.escape("".join(chars))}</text>')
        if STATIC:
            p.append(text)
            continue
        d = r * ROW_DUR
        p.append(
            f'<clipPath id="r{r}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{ART_W:.0f}" begin="{d:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            f'</rect></clipPath><g clip-path="url(#r{r})">{text}</g>'
            f'<rect y="{row_y + 1:.1f}" width="{CELL_W:.1f}" height="{CELL_H - 2:.1f}" fill="{INK}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + ART_W:.0f}" begin="{d:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{d:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{d + ROW_DUR:.3f}s"/></rect>'
        )

    # barra de status com cursor piscando
    line_y = TITLEBAR_H + ART_H + PAD * 0.35
    sy, fs = line_y + 27, 20
    p.append(f'<line x1="0" y1="{line_y:.1f}" x2="{W:.0f}" y2="{line_y:.1f}" stroke="{FRAME}"/>')
    p.append(f'<text x="{PAD}" y="{sy:.1f}" fill="{MUTED}" font-size="{fs}" xml:space="preserve">{PROMPT}'
             f'<tspan fill="{INK}">{NAME}</tspan></text>')
    cx = PAD + (len(PROMPT) + len(NAME)) * fs * 0.6 + 6
    p.append(f'<rect x="{cx:.1f}" y="{sy - 17:.1f}" width="12" height="21" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')
    p.append("</svg>")

    OUT.write_text("".join(p), encoding="utf-8")
    print(f"-> {OUT} ({W:.0f}x{H:.0f})")


if __name__ == "__main__":
    main()
