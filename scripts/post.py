#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post-proceso de index.html (LANDING MOBILE).

El workflow llama a ESTE archivo y a ninguno mas. Para agregar un paso nuevo
al build basta con sumarlo a la lista PASOS de abajo.

Los pasos corren EN ORDEN sobre el mismo index.html que dejo construir.py.
Si alguno falla, el build se detiene: es preferible romper el deploy a
publicar la pagina con los precios o la medicion rotos.

moneda.py, carrito.py e imagenes.py NO viven en este repo: el workflow los
baja de estebanninoc/consola-ultimate en cada build (unica fuente de verdad
de la tabla de precios por moneda).
"""
import os
import subprocess
import sys

PASOS = [
    'scripts/precios.py',    # precios reales (mobile 9.99 / bumps / trio 25.99)
    'scripts/links.py',      # Payment Links de Stripe (kc08 kc09 kc06 kc07)
    'scripts/imagenes.py',   # PNG pesados -> WebP, srcset real, lazy loading
    'scripts/moneda.py',     # precios en moneda local, instantaneos
    'scripts/carrito.py',    # el TOTAL del carrito tambien en moneda local
    'scripts/meta.py',       # Meta Pixel + atribucion (prefijo MB-)
    'scripts/mobilizar.py',  # identidad mobile: titulo, principal, tarjeta PC
    'scripts/colores.py',    # paleta azul neon (al final, pinta todo lo anterior)
]


def main():
    if not os.path.exists('index.html'):
        sys.exit('post.py: no existe index.html — ¿corrio construir.py?')

    for paso in PASOS:
        if not os.path.exists(paso):
            print('── %s (no existe, se omite)' % paso)
            continue
        print('── %s' % paso)
        r = subprocess.run([sys.executable, paso])
        if r.returncode != 0:
            sys.exit('post.py: fallo %s (codigo %d)' % (paso, r.returncode))

    print('post-proceso completo')


if __name__ == '__main__':
    main()
