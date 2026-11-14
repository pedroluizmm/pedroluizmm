"""Converte uma foto/avatar em retrato ASCII: grava data/portrait.txt,
que o render_readme_cards.py desenha no cartão principal.

Uso (local, requer Pillow e numpy):
    python scripts/make_portrait.py foto.png          # foto com fundo claro/liso
    python scripts/make_portrait.py avatar.png --ink  # ilustração com fundo colorido

Padrão: tons de cinza -> glifos (escuro = denso, claro = vazio).
--ink: mantém só o "traço" escuro ligado ao personagem (cabelo, barba, óculos,
roupa) e apaga o resto, o que funciona bem em avatares ilustrados.
--erase=x0,y0,x1,y1 (frações de 0 a 1, repetível): apaga à mão um retângulo
do fundo que tenha sobrado. --debug salva a imagem recortada ao lado do .txt.
"""

import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

OUT = Path(__file__).resolve().parent.parent / "data" / "portrait.txt"
COLS = 140
ROWS = round(COLS * 8 / 15)  # célula ~8x15 -> retrato quadrado
RAMP = " .`:-=+*cs#%@"  # claro (esparso) -> escuro (denso)
WHITE_FLOOR = 0.82
N = 230  # resolução de trabalho da máscara
MIN_BLOB = 260  # área mínima (em px da máscara) para uma mancha escura ser mantida


def ink_mask(rgb, erase=()):
    a = np.asarray(rgb.resize((N, N), Image.LANCZOS)).astype(int)
    r, b, mx = a[..., 0], a[..., 2], a.max(axis=2)
    cand = (mx < 78) & ~((b >= 28) & (b >= r - 5))  # escuro, mas não azulado/roxo (céu)

    # mantém só as manchas grandes (cabelo, óculos, barba, roupa); descarta respingos do fundo
    for x0, y0, x1, y1 in erase:
        cand[int(y0 * N):int(y1 * N), int(x0 * N):int(x1 * N)] = False

    lab = np.zeros((N, N), int)
    keep, small, cur = [], [], 0
    for y in range(N):
        for x in range(N):
            if not cand[y, x] or lab[y, x]:
                continue
            cur += 1
            lab[y, x] = cur
            q, n, sy, sx = deque([(y, x)]), 0, 0, 0
            while q:
                cy, cx = q.popleft()
                n, sy, sx = n + 1, sy + cy, sx + cx
                for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                    if 0 <= ny < N and 0 <= nx < N and cand[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = cur
                        q.append((ny, nx))
            if n >= MIN_BLOB:
                keep.append(cur)
            elif n >= 4:
                small.append((cur, sy / n, sx / n))
    # detalhes pequenos (olhos, sobrancelhas) entram se estiverem dentro da área do personagem
    ys, xs = np.nonzero(np.isin(lab, keep))
    if len(ys):
        keep += [c for c, my, mx_ in small if ys.min() <= my <= ys.max() and xs.min() <= mx_ <= xs.max()]
    mask =Image.fromarray((np.isin(lab, keep) * 255).astype("uint8"))
    return mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)).resize(rgb.size, Image.LANCZOS)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    rgb = Image.open(args[0]).convert("RGB")
    gray = ImageOps.autocontrast(ImageOps.grayscale(rgb), cutoff=1)
    if "--ink" in sys.argv:
        gray = gray.point(lambda v: min(150, int(v * 1.2)))  # traço sempre denso, com leve textura
        erase = [tuple(float(v) for v in a.split("=", 1)[1].split(","))
                 for a in sys.argv if a.startswith("--erase=")]
        gray = Image.composite(gray, Image.new("L", rgb.size, 255), ink_mask(rgb, erase))
        if "--debug" in sys.argv:
            gray.save(OUT.with_suffix(".debug.png"))
    px = gray.resize((COLS, ROWS), Image.LANCZOS).load()

    lines = []
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            lum = px[x, y] / 255
            row += " " if lum >= WHITE_FLOOR else RAMP[round((1 - lum) * (len(RAMP) - 1))]
        lines.append(row)  # largura fixa: o renderizador conta com COLS colunas
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{COLS}x{ROWS} -> {OUT}")


if __name__ == "__main__":
    main()
