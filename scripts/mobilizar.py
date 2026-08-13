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



# ═════════════════════════════════════════════════════════════
#  CONTENIDO 100% MOBILE (v2) — el cuerpo de la plantilla venia
#  hablando de Windows/PC; aqui se reescribe TODO a Android con
#  los numeros reales de los packs (sacados de sus propias
#  descripciones: 150 MB por app, 45+ consolas, +90.000 juegos).
#  Tambien: en el carrito la MULTICONSOLA va ARRIBA y ULTIMATE
#  LEYENDA abajo con "(PARA PC)".
#  Cada reemplazo es tolerante a re-corridas: si el texto viejo no
#  esta pero el nuevo si, se salta; si no esta ninguno, falla.
# ═════════════════════════════════════════════════════════════

def _bloque_div(s, ancla):
    """(ini, fin) del <div ...> balanceado que contiene el ancla."""
    j = s.find(ancla)
    if j == -1:
        return None
    ini = s.rfind('<div', 0, j)
    pat = re.compile(r'<div\b|</div>')
    d = 0
    k = ini
    while True:
        m = pat.search(s, k)
        if not m:
            return None
        d += 1 if m.group(0) == '<div' else -1
        k = m.end()
        if d == 0:
            return (ini, k)


def _cambiar(s, viejo, nuevo, fallos, critico=True):
    if viejo in s:
        return s.replace(viejo, nuevo)
    if nuevo in s:
        return s
    (fallos.append if critico else print)('sin ancla: ' + viejo[:60])
    return s


def _cuerpo_faq(s, titulo_viejo, titulo_nuevo, marca_inner, cuerpo_nuevo, fallos):
    """Reemplaza el cuerpo del FAQ (anclado al titulo) y renombra el titulo."""
    ancla = titulo_viejo if titulo_viejo in s else (titulo_nuevo if titulo_nuevo in s else None)
    if ancla is None:
        fallos.append('faq no encontrado: ' + titulo_viejo[:50])
        return s
    i = s.find(ancla)
    j = s.find(marca_inner, i)
    if j == -1:
        fallos.append('faq sin cuerpo: ' + titulo_viejo[:50])
        return s
    j += len(marca_inner)
    k = s.find('</div>', j)
    s = s[:j] + '\n            ' + cuerpo_nuevo + '\n          ' + s[k:]
    if titulo_viejo in s:
        s = s.replace(titulo_viejo, titulo_nuevo)
    return s


def movilizar_contenido(s, fallos):
    # ── fila de stats ──────────────────────────────────────────
    s = _cambiar(s, '<span class="cu-s2-tag">50 consolas</span>',
                    '<span class="cu-s2-tag">45+ consolas</span>', fallos)
    s = _cambiar(s, '<span class="cu-s2-tag">22.000 juegos</span>',
                    '<span class="cu-s2-tag">+90.000 juegos</span>', fallos)
    s = _cambiar(s, '<span class="cu-s2-tag">Solo Windows</span>',
                    '<span class="cu-s2-tag">Solo Android</span>', fallos)

    # ── FAQs de arriba (faq-) ──────────────────────────────────
    s = _cambiar(s, 'faq-emoji">💻</span>', 'faq-emoji">📱</span>', fallos, critico=False)
    s = _cuerpo_faq(s, '¿CUÁNTO ESPACIO NECESITO EN LA PC?', '¿CUÁNTO ESPACIO OCUPA EN MI CELULAR?',
        '<div class="faq-body-inner">',
        'Casi nada: <span class="hl">cada app pesa ~150 MB</span>. Los juegos se descargan adentro, '
        '<span class="hl">uno por uno, solo los que vas a jugar</span> — nada de ocupar espacio de más. '
        '<strong>Sin instalar nada extra, sin configurar nada.</strong>', fallos)
    s = _cuerpo_faq(s, '¿FUNCIONA CON MI JOYSTICK?', '¿FUNCIONA CON MI CONTROL?',
        '<div class="faq-body-inner">',
        'Sí. <span class="hl">Los controles táctiles vienen en la pantalla</span> — no necesitás nada más. '
        'Y si querés, <span class="hl">podés conectar cualquier mando Bluetooth</span>: PS4, PS5, Xbox, Switch. '
        'Todos funcionan. <strong>Conectás, abrís y jugás.</strong>', fallos)
    s = _cambiar(s, 'faq-emoji">🖥️</span>', 'faq-emoji">📱</span>', fallos, critico=False)
    s = _cuerpo_faq(s, '¿FUNCIONA EN MI PC? ¿Y SI NO ES PARA MÍ?', '¿FUNCIONA EN MI CELULAR? ¿Y SI NO ES PARA MÍ?',
        '<div class="faq-body-inner">',
        'Solo Android. Si tu celular corre apps normales, <span class="hl">corre los juegos sin problema</span>. '
        'No necesitás un teléfono de gama alta. Y si por cualquier motivo no estás conforme, tenés '
        '<strong>7 días de garantía total</strong> — te devolvemos el 100% de tu plata sin preguntas.', fallos)

    # ── requisitos ─────────────────────────────────────────────
    s = _cambiar(s, 'Lo que necesita tu PC para correr la Consola Ultimate Retro™ sin problemas.',
                    'Lo que necesita tu celular para correr el Pack Supremo Mobile™ sin problemas.', fallos)
    s = _cambiar(s, '🖥️ Consola Ultimate Retro™', '📱 Pack Supremo Mobile™', fallos)
    s = _cambiar(s, 'Windows 10 o Windows 11', 'Android — celular o tablet', fallos)
    s = _cambiar(s, 'Intel i3 / i5 / i7 o AMD FX / Ryzen',
                    'Cualquier procesador actual — no necesitás gama alta', fallos)
    s = _cambiar(s, '20 GB libres para la instalación inicial — los juegos se descargan automáticamente dentro del sistema según lo que elegís',
                    'Cada app pesa ~150 MB — los juegos se descargan adentro según lo que elegís', fallos)
    s = _cambiar(s, '<strong>Memoria RAM</strong><br/>', '<strong>Memoria RAM</strong><br/>', fallos, critico=False)
    s = _cambiar(s, '8 GB o más', 'Funciona en gama media y baja — no necesitás un teléfono último modelo', fallos)
    s = _cambiar(s, '<strong>Placa de Video</strong>', '<strong>Gráficos</strong>', fallos)
    s = _cambiar(s, 'GPU integrada Intel i3 / AMD Ryzen 3 actual o superior',
                    'No hace falta — todo está optimizado para Android', fallos)

    # ── seccion de consolas (numeros reales del pack) ──────────
    s = _cambiar(s, '🎮 50 consolas incluidas', '🎮 45+ consolas incluidas', fallos)
    s = _cambiar(s, '✦ 22.000 juegos · Todo en un solo archivo', '✦ +90.000 juegos · Todo en tu celular', fallos)
    s = _cambiar(s, '<span class="cu-ix-total-num"><span>50</span> consolas</span>',
                    '<span class="cu-ix-total-num"><span>45+</span> consolas</span>', fallos)
    if '22.000 juegos</span> te esperan adentro' in s:
        s = s.replace('22.000 juegos</span> te esperan adentro', '+90.000 juegos</span> te esperan adentro')
    elif '22.000 juegos</strong> te esperan adentro' in s:
        s = s.replace('22.000 juegos</strong> te esperan adentro', '+90.000 juegos</strong> te esperan adentro')

    # ── testimonios ────────────────────────────────────────────
    s = _cambiar(s, 'Lo que dicen quienes ya tienen la MultiConsola Ultimate Retro™',
                    'Lo que dicen quienes ya compran en The Game Box', fallos)

    # ── garantia ───────────────────────────────────────────────
    s = _cambiar(s, 'el sistema no funciona en tu PC, te devolvemos el',
                    'el sistema no funciona en tu celular, te devolvemos el', fallos)

    # ── Preguntas Frecuentes (cu-faq) ──────────────────────────
    s = _cuerpo_faq(s, '¿Qué consolas y cuántos juegos incluye la Consola Ultimate Retro?',
        '¿Qué incluye exactamente el Pack Supremo Mobile?',
        '<div class="cu-faq-answer-inner">',
        '<strong>RETRO GAMING MOBILE:</strong> 15 consolas · +60.000 juegos (NES, SNES, PSX, PSP, N64, NDS, MAME y más).<br/>'
        '<strong>ULTRA RETRO MOBILE:</strong> 30 consolas · +50.000 juegos (NES, GBA, PSP, PS, N64, Arcade, Wii, Dreamcast y más).<br/>'
        '<strong>PS2 MOBILE:</strong> +2.000 juegos de PS2 (God of War, GTA, DBZ, PES, MGS, GT4, Tekken 5).<br/><br/>'
        '3 APKs listas — todo en tu celular.', fallos)
    s = _cuerpo_faq(s, '¿Cómo funciona el sistema?', '¿Cómo funciona el sistema?',
        '<div class="cu-faq-answer-inner">',
        'Instalás las 3 APKs con su guía paso a paso. Después <strong>seleccionás el juego, se descarga y se abre</strong> '
        'para que empieces a jugar. Queda guardado en tu celular.<br/><br/>'
        '<strong>No necesitás internet para jugar</strong> los juegos ya descargados.', fallos)
    s = _cuerpo_faq(s, '¿Cuáles son las consolas con sistema de descarga directa?',
        '¿Cómo descargo los juegos?',
        '<div class="cu-faq-answer-inner">',
        'Dentro de cada app el catálogo está organizado por consola: <strong>elegís el juego, se descarga y listo</strong>. '
        'Solo descargás los que querés jugar.', fallos)
    s = _cuerpo_faq(s, '¿Necesito instalar algo?', '¿Necesito instalar algo?',
        '<div class="cu-faq-answer-inner">',
        'Solo las 3 APKs — te llegan con su guía paso a paso. De resto, <strong>descargar y jugar</strong>.', fallos)
    s = _cuerpo_faq(s, '¿Puedo instalar y ejecutar Consola Ultimate Retro en un disco externo?',
        '¿Puedo jugar sin internet?',
        '<div class="cu-faq-answer-inner">',
        'Sí. Una vez descargado un juego, <strong>podés jugarlo sin conexión</strong> cuando quieras.', fallos)
    s = _cuerpo_faq(s, '¿Funciona en MAC OS, Android o Linux?', '¿Funciona en iPhone (iOS) o en PC?',
        '<div class="cu-faq-answer-inner">',
        'El pack es <strong>para Android</strong> (celulares y tablets) — no funciona en iPhone. '
        '¿Querés jugar también en tu PC? Agregá la <strong>Multiconsola Ultimate Retro™</strong> en el carrito.', fallos)
    s = _cuerpo_faq(s, '¿Qué versiones permiten crear partidas online y cómo funciona?',
        '¿Puedo jugar partidas online?',
        '<div class="cu-faq-answer-inner">',
        'El pack mobile es para jugar en tu celular. Las partidas online multijugador son una función de la '
        '<strong>Multiconsola de PC</strong> (la podés agregar en el carrito).', fallos)

    # ── listas de video de PS4/PS5/Xbox (catalogo del pack PC) ──
    if 'cu-movil-css' not in s:
        css = ('<style id="cu-movil-css">.vps4,.vps5,.vxbox,.vxbs{display:none!important}</style>')
        j = s.rfind('</body>')
        if j != -1:
            s = s[:j] + css + '\n' + s[j:]

    return s


def reordenar_carrito(s, fallos):
    """MULTICONSOLA arriba, ULTIMATE LEYENDA (PARA PC) abajo."""
    s = _cambiar(s, '<p class="cu-bump-title cu-leyenda-title">⚡ ULTIMATE LEYENDA</p>',
                    '<p class="cu-bump-title cu-leyenda-title">⚡ ULTIMATE LEYENDA (PARA PC)</p>', fallos)
    s = _cambiar(s, '📱 LLEVA TODO EL GAMING EN TU BOLSILLO!',
                    '🖥️ ¿TENÉS PC? LLEVATE ESTOS TAMBIÉN', fallos)
    i_pc = s.find('id="cu-b-gold-pc"')
    i_mob = s.find('id="cu-b-gold-mob"')
    if i_pc == -1 or i_mob == -1:
        fallos.append('no encontre las tarjetas gold para reordenar')
        return s
    if i_mob < i_pc:
        return s  # ya reordenado (idempotente)
    a = _bloque_div(s, 'id="cu-b-gold-pc"')
    b = _bloque_div(s, 'id="cu-b-gold-mob"')
    if not a or not b or not (a[1] < b[0]):
        fallos.append('bloques gold no delimitables para el swap')
        return s
    s = s[:a[0]] + s[b[0]:b[1]] + s[a[1]:b[0]] + s[a[0]:a[1]] + s[b[1]:]
    return s

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

    # ── 7. contenido 100%% mobile + carrito reordenado ──────────
    s = movilizar_contenido(s, fallos)
    s = reordenar_carrito(s, fallos)
    print('contenido mobilizado + carrito reordenado')

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
    if 'Solo Windows' in s or 'Windows 10 o Windows 11' in s:
        fallos.append('quedo texto de Windows sin mobilizar')
    if s.find('id="cu-b-gold-mob"') > s.find('id="cu-b-gold-pc"'):
        fallos.append('el carrito no quedo reordenado (multiconsola debe ir arriba)')
    if '(PARA PC)' not in s:
        fallos.append('falta el (PARA PC) en Ultimate Leyenda')
    if GOLDMOB_TITULO_NUEVO not in s:
        fallos.append('la tarjeta PC no quedo rebautizada')
    if fallos:
        sys.exit('ERROR mobilizar.py:\n  - ' + '\n  - '.join(fallos))
    print('validaciones OK')


if __name__ == '__main__':
    main()
