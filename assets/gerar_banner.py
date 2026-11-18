#!/usr/bin/env python3
"""Gera o banner do perfil do GitHub: céu azul do Cruzeiro com o Cruzeiro do Sul de verdade.

As cinco estrelas saem das coordenadas reais (J2000) e são projetadas como se vê do chão,
olhando para o céu: norte para cima, leste para a esquerda. As fontes vão embutidas no SVG,
porque o GitHub mostra o README como <img>, e imagem não busca fonte de fora.

Uso: python3 gerar_banner.py <pasta com archivo.woff2 e jetbrains-mono.woff2> assets/banner.svg
As duas fontes são livres (SIL Open Font License).
"""
import base64
import math
import random
import sys
from pathlib import Path

FONTES = Path(sys.argv[1])
SAIDA = Path(sys.argv[2])

L, A = 1280, 320

def b64(nome):
    return base64.b64encode((FONTES / nome).read_bytes()).decode()

# (nome popular no Brasil, designação, AR em horas, declinação em graus, magnitude, cor)
ESTRELAS = [
    ("Estrela de Magalhães", "α Cru", 12 + 26/60 + 35.9/3600, -(63 + 5/60 + 56/3600), 0.76, "#EAF1FF"),
    ("Mimosa",               "β Cru", 12 + 47/60 + 43.3/3600, -(59 + 41/60 + 19/3600), 1.25, "#E3ECFF"),
    ("Rubídea",              "γ Cru", 12 + 31/60 + 9.9/3600,  -(57 + 6/60 + 48/3600),  1.64, "#FFD7C2"),
    ("Pálida",               "δ Cru", 12 + 15/60 + 8.7/3600,  -(58 + 44/60 + 56/3600), 2.79, "#E6EEFF"),
    ("Intrometida",          "ε Cru", 12 + 21/60 + 21.6/3600, -(60 + 24/60 + 4/3600),  3.59, "#FFF3E0"),
]

CX, CY, ESCALA = 1010, 146, 35.0
ra0 = ESTRELAS[2][2] * 15          # Rubídea no eixo vertical
dec0 = -60.0

def projetar(ra_h, dec):
    x = -(ra_h * 15 - ra0) * math.cos(math.radians(dec))   # leste para a esquerda
    y = -(dec - dec0)                                      # norte para cima
    return x, y

pontos = [projetar(e[2], e[3]) for e in ESTRELAS]
meio_y = (min(p[1] for p in pontos) + max(p[1] for p in pontos)) / 2
pos = [(CX + x * ESCALA, CY + (y - meio_y) * ESCALA) for x, y in pontos]

def brilho(x, y, mag, cor, atraso):
    r = max(1.8, 6.3 - 1.25 * mag)
    raio = r * 4.2
    fino = r * 0.42
    estrela = (f"M{x:.1f},{y - raio:.1f} L{x + fino:.1f},{y - fino:.1f} L{x + raio:.1f},{y:.1f} "
               f"L{x + fino:.1f},{y + fino:.1f} L{x:.1f},{y + raio:.1f} L{x - fino:.1f},{y + fino:.1f} "
               f"L{x - raio:.1f},{y:.1f} L{x - fino:.1f},{y - fino:.1f} Z")
    return (f'<g class="cruz" style="animation-delay:{atraso:.1f}s;transform-origin:{x:.1f}px {y:.1f}px">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 6:.1f}" fill="url(#halo)"/>'
            f'<path d="{estrela}" fill="{cor}"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.9:.1f}" fill="#fff"/></g>')

# Rótulos: posição relativa à estrela e alinhamento
ROTULOS = {
    0: (14, 18, "start"),
    1: (-16, 4, "end"),
    2: (16, -2, "start"),
    3: (14, -8, "start"),
    4: (12, 14, "start"),
}

aleatorio = random.Random(1921)    # ano de fundação do clube, só como semente
fundo = []
for i in range(110):
    x = aleatorio.uniform(0, L)
    y = aleatorio.uniform(0, A)
    if 40 < x < 860 and 60 < y < 300 and aleatorio.random() < 0.65:
        continue                    # menos estrelas atrás do texto
    r = aleatorio.choice([0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5])
    op = aleatorio.uniform(0.25, 0.85)
    pisca = ' class="pisca" style="animation-delay:%.1fs;animation-duration:%.1fs"' % (
        aleatorio.uniform(0, 6), aleatorio.uniform(3, 7)) if aleatorio.random() < 0.3 else ""
    fundo.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" opacity="{op:.2f}"{pisca}/>')

linhas = []
for a, b in ((2, 0), (1, 3)):
    (x1, y1), (x2, y2) = pos[a], pos[b]
    comp = math.hypot(x2 - x1, y2 - y1)
    linhas.append(f'<line class="traco" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                  f'style="stroke-dasharray:{comp:.1f};stroke-dashoffset:{comp:.1f}"/>')

estrelas_svg = []
rotulos_svg = []
for i, (e, (x, y)) in enumerate(zip(ESTRELAS, pos)):
    estrelas_svg.append(brilho(x, y, e[4], e[5], i * 0.7))
    dx, dy, ancora = ROTULOS[i]
    rotulos_svg.append(f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{ancora}" class="rotulo">'
                       f'{e[0]}<tspan class="greg" dx="6">{e[1]}</tspan></text>')

coracao = ("M0,3.2 C0,1.2 1.6,0 3.1,0 C4.3,0 5.2,0.7 5.6,1.6 C6,0.7 6.9,0 8.1,0 "
           "C9.6,0 11.2,1.2 11.2,3.2 C11.2,6.4 7.4,8.6 5.6,10 C3.8,8.6 0,6.4 0,3.2 Z")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{L}" height="{A}" viewBox="0 0 {L} {A}" role="img" aria-labelledby="t d">
<title id="t">Ricardo dos Santos Pavanelli, Analista de TI</title>
<desc id="d">Céu noturno em azul e branco com a constelação do Cruzeiro do Sul nas posições reais das cinco estrelas.</desc>
<defs>
<style>
@font-face{{font-family:"Archivo";font-weight:100 900;src:url(data:font/woff2;base64,{b64("archivo.woff2")}) format("woff2")}}
@font-face{{font-family:"JetBrains Mono";font-weight:800;src:url(data:font/woff2;base64,{b64("jetbrains-mono.woff2")}) format("woff2")}}
.nome{{font:800 46px "Archivo",sans-serif;fill:#fff;letter-spacing:-.5px}}
.cargo{{font:500 20px "Archivo",sans-serif;fill:#CFDCFF}}
.linha{{font:400 15.5px "Archivo",sans-serif;fill:#9FB6EA}}
.prompt{{font:800 14px "JetBrains Mono",monospace;fill:#7FA6FF}}
.selo{{font:700 12.5px "Archivo",sans-serif;fill:#fff;letter-spacing:2.6px}}
.rotulo{{font:600 11.5px "Archivo",sans-serif;fill:#BFD0FF;letter-spacing:.6px;opacity:.78}}
.greg{{font-weight:400;fill:#7F98D6}}
.legenda{{font:700 11px "Archivo",sans-serif;fill:#8EA9EE;letter-spacing:4px}}
.marca{{font:900 172px "Archivo",sans-serif;fill:none;stroke:#fff;stroke-width:1.2;opacity:.07;letter-spacing:6px}}
.traco{{stroke:#DCE6FF;stroke-width:1.1;opacity:.38;animation:desenha 2.4s ease-out .4s forwards}}
.cruz{{animation:cintila 5.5s ease-in-out infinite}}
.pisca{{animation:pisca 5s ease-in-out infinite}}
.cursor{{animation:cursor 1.1s steps(1) infinite}}
.cadente{{animation:cadente 11s linear infinite 2s;opacity:0}}
@keyframes desenha{{to{{stroke-dashoffset:0}}}}
@keyframes cintila{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(.86);opacity:.82}}}}
@keyframes pisca{{0%,100%{{opacity:.15}}50%{{opacity:.95}}}}
@keyframes cursor{{50%{{opacity:0}}}}
@keyframes cadente{{0%{{transform:translate(0,0);opacity:0}}2%{{opacity:1}}9%{{transform:translate(420px,150px);opacity:0}}100%{{transform:translate(420px,150px);opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.traco{{stroke-dashoffset:0!important}}.cadente{{opacity:0}}}}
</style>
<linearGradient id="ceu" x1="0" y1="0" x2="1" y2="0.35">
<stop offset="0" stop-color="#020A22"/><stop offset=".5" stop-color="#05205F"/><stop offset="1" stop-color="#0A3AA6"/>
</linearGradient>
<radialGradient id="brilhoCruz" cx="{CX / L:.3f}" cy=".5" r=".42" gradientTransform="translate({CX / L:.3f} .5) scale(.55 1.9) translate(-{CX / L:.3f} -.5)">
<stop offset="0" stop-color="#2C64FF" stop-opacity=".55"/><stop offset="1" stop-color="#2C64FF" stop-opacity="0"/>
</radialGradient>
<radialGradient id="halo"><stop offset="0" stop-color="#BFD4FF" stop-opacity=".55"/><stop offset=".35" stop-color="#6E97FF" stop-opacity=".18"/><stop offset="1" stop-color="#6E97FF" stop-opacity="0"/></radialGradient>
<linearGradient id="rastro" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".9"/></linearGradient>
<linearGradient id="faixa" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".25" stop-color="#fff" stop-opacity=".55"/><stop offset=".75" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<rect width="{L}" height="{A}" fill="url(#ceu)"/>
<rect width="{L}" height="{A}" fill="url(#brilhoCruz)"/>
<text x="{L + 8}" y="{A - 18}" text-anchor="end" class="marca">CRUZEIRO</text>
<g>{"".join(fundo)}</g>
<g class="cadente"><line x1="250" y1="22" x2="330" y2="51" stroke="url(#rastro)" stroke-width="1.6" stroke-linecap="round"/></g>
<g>{"".join(linhas)}</g>
<g>{"".join(estrelas_svg)}</g>
<g>{"".join(rotulos_svg)}</g>
<text x="{CX}" y="{A - 16}" text-anchor="middle" class="legenda">CRUZEIRO DO SUL</text>

<text x="72" y="94" class="prompt">ricardo@curitiba:~$ whoami<tspan class="cursor"> _</tspan></text>
<text x="70" y="152" class="nome">Ricardo dos Santos Pavanelli</text>
<text x="72" y="190" class="cargo">Analista de TI · Segurança · Microsoft 365 · Sistemas internos</text>
<text x="72" y="220" class="linha">Tradestar Group  ·  Engenharia de Software  ·  Curitiba, PR</text>
<g transform="translate(72 248)">
<rect width="168" height="30" rx="15" fill="#fff" fill-opacity=".07" stroke="#fff" stroke-opacity=".38"/>
<path d="{coracao}" transform="translate(15 10)" fill="#4D84FF"/>
<text x="35" y="19.6" class="selo">CRUZEIRENSE</text>
</g>
<rect x="0" y="{A - 3}" width="{L}" height="3" fill="url(#faixa)" opacity=".5"/>
</svg>
'''

SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(svg, encoding="utf-8")
print(SAIDA, len(svg.encode()), "bytes")
for e, (x, y) in zip(ESTRELAS, pos):
    print(f"  {e[0]:<22} {x:7.1f} {y:7.1f}  mag {e[4]}")
