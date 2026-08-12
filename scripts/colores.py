#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CU-COLORES v1 — paleta azul neon para la landing mobile.

La plantilla original es verde neon (#3cff91 y familia). Esta landing usa
AZUL neon para diferenciarse de la landing PC. Se reemplazan los colores en
index.html Y en los CSS de assets/ (el tema trae colores en los dos lados).

Mapa (verde -> azul, conservando luminosidad para no romper contrastes):

    #3cff91  ->  #3cd7ff      neon principal
    #00ff82  ->  #00c6ff      neon secundario
    #7dffb0  ->  #7dd9ff      neon claro (textos)
    #1db954  ->  #1976e6      verde "Spotify" (checks, badges)

Las imagenes (cubo verde, logos) NO se pueden recolorear aqui: siguen
verdes. Es aceptable — el producto principal es el pack mobile (celulares).

Corre al FINAL de post.py (despues de que todos los demas pasos ya
inyectaron su CSS/JS con colores verdes). Es idempotente: los colores
viejos ya no existen en la segunda corrida.
"""
import io
import os
import sys

PARES = [
    # hex (minusculas y MAYUSCULAS)
    ('3cff91', '3cd7ff'), ('3CFF91', '3CD7FF'),
    ('00ff82', '00c6ff'), ('00FF82', '00C6FF'),
    ('7dffb0', '7dd9ff'), ('7DFFB0', '7DD9FF'),
    ('1db954', '1976e6'), ('1DB954', '1976E6'),
    # rgb()/rgba() con y sin espacios
    ('rgba(60,255,145', 'rgba(60,215,255'), ('rgba(60, 255, 145', 'rgba(60, 215, 255'),
    ('rgb(60,255,145',  'rgb(60,215,255'),  ('rgb(60, 255, 145',  'rgb(60, 215, 255'),
    ('rgba(0,255,130',  'rgba(0,198,255'),  ('rgba(0, 255, 130',  'rgba(0, 198, 255'),
    ('rgba(29,185,84',  'rgba(25,118,230'), ('rgba(29, 185, 84',  'rgba(25, 118, 230'),
    ('rgb(29,185,84',   'rgb(25,118,230'),  ('rgb(29, 185, 84',   'rgb(25, 118, 230'),
    ('rgba(125,255,176', 'rgba(125,217,255'), ('rgba(125, 255, 176', 'rgba(125, 217, 255'),
]


def pintar(ruta):
    s = io.open(ruta, encoding='utf-8', errors='ignore').read()
    n0 = len(s)
    total = 0
    for viejo, nuevo in PARES:
        n = s.count(viejo)
        if n:
            s = s.replace(viejo, nuevo)
            total += n
    if total:
        io.open(ruta, 'w', encoding='utf-8').write(s)
    print('%-40s %4d reemplazos (%d bytes)' % (ruta, total, n0))
    return total


def main():
    archivo = os.environ.get('CU_INDEX', 'index.html')
    if not os.path.exists(archivo):
        sys.exit('no existe ' + archivo)

    total = pintar(archivo)

    if os.path.isdir('assets'):
        for f in sorted(os.listdir('assets')):
            if f.endswith('.css'):
                total += pintar(os.path.join('assets', f))

    if total == 0:
        sys.exit('ERROR colores.py: 0 reemplazos — ¿la plantilla cambio de paleta?')

    # ninguna huella verde puede quedar
    s = io.open(archivo, encoding='utf-8', errors='ignore').read()
    for viejo, _ in PARES:
        if viejo in s:
            sys.exit('ERROR colores.py: quedo el color viejo %s en %s' % (viejo, archivo))
    print('paleta azul neon aplicada (%d reemplazos)' % total)


if __name__ == '__main__':
    main()
