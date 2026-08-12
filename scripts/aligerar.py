#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CU-ALIGERAR v1 — compresion agresiva de las imagenes de assets/.

La pagina pesa ~2.1 MB y ~85%% son imagenes: la plantilla trae webp ENORMES
(testimoniales de 689 KB, tarjetas de 250-330 KB) que se muestran a menos de
500px de ancho. Este paso las recomprime EN EL BUILD, antes de publicar:

  - ancho maximo 1400px (mas que suficiente para retina en movil)
  - webp calidad 68 / jpg calidad 70 (indistinguible a ojo en fotos)
  - png se convierte a webp SOLO si no pierde el nombre (no: se queda igual,
    los png de la plantilla son logos chicos y los toca procesar.py)
  - solo se sobreescribe si el resultado ahorra >10%%

Corre como paso del workflow DESPUES de descargar.py/procesar.py y ANTES de
construir.py + post.py (imagenes.py generara los srcset a partir de las
versiones ya comprimidas). Idempotente: una imagen ya comprimida no baja
del umbral de ahorro y se deja quieta.
"""
import os
import sys

from PIL import Image

UMBRAL = 120 * 1024      # solo tocar archivos de mas de 120 KB
MAX_ANCHO = 1400
CALIDAD_WEBP = 68
CALIDAD_JPG = 70


def comprimir(ruta):
    peso0 = os.path.getsize(ruta)
    ext = ruta.rsplit('.', 1)[-1].lower()
    if ext not in ('webp', 'jpg', 'jpeg'):
        return 0
    try:
        im = Image.open(ruta)
        im.load()
    except Exception as e:
        print('   %s: no se pudo abrir (%s)' % (ruta, e))
        return 0

    if im.width > MAX_ANCHO:
        alto = round(im.height * MAX_ANCHO / im.width)
        im = im.resize((MAX_ANCHO, alto), Image.LANCZOS)

    tmp = ruta + '.cu_tmp'
    try:
        if ext == 'webp':
            im.save(tmp, 'WEBP', quality=CALIDAD_WEBP, method=6)
        else:
            if im.mode not in ('RGB', 'L'):
                im = im.convert('RGB')
            im.save(tmp, 'JPEG', quality=CALIDAD_JPG, optimize=True, progressive=True)
    except Exception as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        print('   %s: fallo al comprimir (%s)' % (ruta, e))
        return 0

    peso1 = os.path.getsize(tmp)
    if peso1 < peso0 * 0.9:
        os.replace(tmp, ruta)
        print('   %-70s %4d KB -> %4d KB' % (os.path.basename(ruta), peso0 // 1024, peso1 // 1024))
        return peso0 - peso1
    os.remove(tmp)
    return 0


def main():
    if not os.path.isdir('assets'):
        sys.exit('aligerar.py: no existe assets/ — ¿corrio descargar.py?')
    total = 0
    candidatos = 0
    for f in sorted(os.listdir('assets')):
        ruta = os.path.join('assets', f)
        if not os.path.isfile(ruta) or os.path.getsize(ruta) < UMBRAL:
            continue
        candidatos += 1
        total += comprimir(ruta)
    print('aligerar: %d candidatos, ahorro total %.2f MB' % (candidatos, total / 1048576.0))


if __name__ == '__main__':
    main()
