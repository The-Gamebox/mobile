#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CU-MOBILIZAR v1 — convierte la landing clonada en la landing del
PACK SUPREMO MOBILE.

La pagina de origen usa la MISMA plantilla que la landing PC (mismo drawer,
mismas tarjetas). Este script hace el "trasplante de identidad":

  1. <title> y og:title  ->  PACK SUPREMO MOBILE™
  2. El titular (h1)     ->  version mobile (+90.000 juegos · 45+ consolas,
                             los numeros reales del pack segun la tienda)
  3. Producto principal del carrito -> PACK SUPREMO MOBILE™ (nombre + imagen:
     toma la imagen de la tarjeta gold-mob, que ES el pack mobile)
  4. La tarjeta gold-mob se rebautiza como MULTICONSOLA ULTIMATE RETRO™ (PC)
     (el pack mobile ya es el principal, no puede ser tambien un bump):
     titulo, descripcion, imagen (el cubo verde del principal original) y
     se ocultan sus miniaturas .cu-incluye (eran las 3 APKs del mobile).

Corre DESPUES de construir.py, dentro de post.py. Es idempotente
(los reemplazos son de ida: el texto viejo ya no existe en la 2a corrida).
"""
import io
import os
import re
import sys

ARCHIVO = os.environ.get('CU_INDEX', 'index.html')

TITULO = 'PACK SUPREMO MOBILE™ : RETRO GAMING + ULTRA RETRO + PS2 MOBILE'

H1_VIEJO = 'En 5 minutos tenés 50 consolas y 22.000 juegos listos para jugar en tu PC.'
H1_NUEVO = 'En 5 minutos tenés 45+ consolas y +90.000 juegos listos para jugar en tu celular.'

GOLDMOB_TITULO_VIEJO = '🏆 PACK SUPREMO MOBILE'
GOLDMOB_TITULO_NUEVO = '🖥️ MULTICONSOLA ULTIMATE RETRO™ (PC)'
GOLDMOB_DESC_VIEJO = ('RETRO GAMING + ULTRA RETRO + PS2 MOBILE. +90.000 juegos · 45+ consolas · '
                      '3 APKs listas. Todo en tu celular.')
GOLDMOB_DESC_NUEVO = ('La legendaria multiconsola para PC: 50 consolas · +22.000 juegos · cero '
                      'configuración. Llevátela junto a tu pack mobile.')

CSS_EXTRA = ('<style id="cu-mobilizar-css">'
             '#cu-b-gold-mob .cu-incluye{display:none!important}'
             '#cu-b-gold-mob>.cu-bump-row .cu-bump-img{display:block!important}'
             '</style>')


def main():
    if not os.path.exists(ARCHIVO):
        sys.exit('no existe ' + ARCHIVO)
    s = io.open(ARCHIVO, encoding='utf-8').read()
    n0 = len(s)
    fallos = []

    # ── 1. <title> y og:title ───────────────────────────────────
    s, n = re.subn(r'<title>[^<]*</title>', '<title>%s</title>' % TITULO, s, count=1)
    if not n:
        fallos.append('no se encontro <title>')
    s = re.sub(r'(<meta property="og:title" content=")[^"]*(")', r'\g<1>' + TITULO + r'\g<2>', s, count=1)
    s = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', r'\g<1>' + TITULO + r'\g<2>', s, count=1)
    print('titulo: %s' % TITULO)

    # ── 2. titular ──────────────────────────────────────────────
    if H1_VIEJO in s:
        s = s.replace(H1_VIEJO, H1_NUEVO)
        print('h1 mobilizado')
    elif H1_NUEVO not in s:
        fallos.append('no se encontro el h1 de la plantilla')

    # ── 3. imagenes: se intercambian las ETIQUETAS COMPLETAS ────
    #    (imagenes.py puede haber agregado srcset; un swap solo del src
    #     dejaria al navegador eligiendo la imagen vieja por el srcset)
    m_main = re.search(r'<img[^>]*class="cu-main-img"[^>]*>', s)
    i_gold = s.find('id="cu-b-gold-mob"')
    m_bump = re.search(r'<img[^>]*class="cu-bump-img"[^>]*>', s[i_gold:]) if i_gold != -1 else None

    def src_de(tag):
        m = re.search(r'\bsrc="([^"]+)"', tag)
        return m.group(1) if m else None

    img_cubo = src_de(m_main.group(0)) if m_main else None
    img_mobile = src_de(m_bump.group(0)) if m_bump else None

    # ── 4. producto principal del carrito -> PACK SUPREMO MOBILE ──
    viejo = '<p class="cu-main-name">MULTICONSOLA ULTIMATE RETRO™</p>'
    nuevo = '<p class="cu-main-name">PACK SUPREMO MOBILE™</p>'
    if viejo in s:
        s = s.replace(viejo, nuevo)
        print('nombre del principal: PACK SUPREMO MOBILE™')
    elif nuevo not in s:
        fallos.append('no se encontro cu-main-name')

    ya_mobilizado = 'cu-mobilizar-css' in s   # 2a corrida: no volver a intercambiar
    if ya_mobilizado:
        print('imagenes ya intercambiadas (idempotente)')
    elif img_mobile and img_cubo and m_main and m_bump:
        tag_main = ('<img class="cu-main-img" src="%s" alt="Pack Supremo Mobile™" '
                    'loading="lazy">' % img_mobile)
        tag_bump = ('<img class="cu-bump-img" src="%s" alt="Multiconsola Ultimate Retro™ (PC)" '
                    'loading="lazy">' % img_cubo)
        s = s.replace(m_main.group(0), tag_main, 1)
        # la tarjeta gold-mob: solo su primera cu-bump-img
        i_gold = s.find('id="cu-b-gold-mob"')
        seg = s[i_gold:]
        seg = seg.replace(m_bump.group(0), tag_bump, 1)
        s = s[:i_gold] + seg
        print('imagenes intercambiadas: principal=%s · tarjeta PC=%s' % (img_mobile, img_cubo))
    else:
        fallos.append('no pude intercambiar las imagenes (mobile=%s cubo=%s)'
                      % (img_mobile, img_cubo))

    # ── 5. la tarjeta gold-mob pasa a ser la MULTICONSOLA PC ────
    if GOLDMOB_TITULO_VIEJO in s:
        s = s.replace(GOLDMOB_TITULO_VIEJO, GOLDMOB_TITULO_NUEVO)
        print('tarjeta gold-mob rebautizada: MULTICONSOLA PC')
    elif GOLDMOB_TITULO_NUEVO not in s:
        fallos.append('no se encontro el titulo de la tarjeta gold-mob')
    if GOLDMOB_DESC_VIEJO in s:
        s = s.replace(GOLDMOB_DESC_VIEJO, GOLDMOB_DESC_NUEVO)

    # etiquetas iniciales del toggle (el tema las trae en data-label/texto;
    # el JS de construir.py solo las cambia al hacer clic)
    s = s.replace('+ AGREGAR PACK SUPREMO MOBILE', '+ AGREGAR MULTICONSOLA PC')
    s = s.replace('\u2713 PACK SUPREMO MOBILE AGREGADO', '\u2713 MULTICONSOLA PC AGREGADA')

    # ── 6. CSS: sin miniaturas APK en la tarjeta PC, con su imagen ──
    if 'cu-mobilizar-css' not in s:
        j = s.rfind('</body>')
        if j == -1:
            sys.exit('no se encontro </body>')
        s = s[:j] + CSS_EXTRA + '\n' + s[j:]

    io.open(ARCHIVO, 'w', encoding='utf-8').write(s)
    print('%s: %d -> %d bytes' % (ARCHIVO, n0, len(s)))

    # ── validaciones ────────────────────────────────────────────
    if TITULO not in s:
        fallos.append('el titulo nuevo no quedo')
    if '<p class="cu-main-name">PACK SUPREMO MOBILE™</p>' not in s:
        fallos.append('el principal no quedo rebautizado')
    if GOLDMOB_TITULO_NUEVO not in s:
        fallos.append('la tarjeta PC no quedo rebautizada')
    if fallos:
        sys.exit('ERROR mobilizar.py:\n  - ' + '\n  - '.join(fallos))
    print('validaciones OK')


if __name__ == '__main__':
    main()
