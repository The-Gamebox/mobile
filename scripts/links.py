#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Links de pago de la LANDING MOBILE, en un solo lugar. Checkout = STRIPE
(Payment Links), cuenta "The Gamebox" acct_1U1cFpEIkdT1ZKlo.

construir.py trae los links embebidos en el HTML (los viejos de Hotmart).
Este script los reescribe sobre el HTML ya generado.

Cada clave es la combinacion que arma el carrito DE ESTA LANDING:
    principal                      PACK SUPREMO MOBILE          $9.99
    principal+gold-pc              + Ultimate Leyenda          $19.98
    principal+gold-mob             + Multiconsola PC           $19.98
    principal+gold-pc+gold-mob     los tres                    $25.99

⚠️ OJO: aqui "principal" es el pack MOBILE y "gold-mob" es la MULTICONSOLA
PC (la tarjeta se rebautiza en scripts/mobilizar.py). Por eso
principal+gold-mob usa el MISMO Payment Link kc06 que en la landing PC usa
"multiconsola + supremo": el contenido del combo es identico.

Los Payment Links presentan el precio EN LA MONEDA LOCAL del comprador:
cada Price tiene currency_options fijos en 14 monedas de LATAM, los MISMOS
numeros que muestra la landing (scripts/moneda.py compartido con la landing
PC — el precio no se calcula, se copia).

Productos Stripe de esta landing:
    prod_V3l61cNJnk7jC6  PACK SUPREMO MOBILE                    ($9.99)
    prod_V3l6h6AQSNzJWt  PACK SUPREMO MOBILE + ULTIMATE LEYENDA ($19.98)
    prod_V1foRduqk71z6b  multiconsola + supremo (kc06, $19.98)
    prod_V1fonN8D2qKFGk  todo (kc07, $25.99)

Es idempotente.
"""
import io
import os
import re
import sys

ARCHIVO = os.environ.get('CU_INDEX', 'index.html')

LINKS = {
    # PACK SUPREMO MOBILE — $9.99
    'principal': 'https://buy.stripe.com/cNi3cv6HY0AQ7budGj7kc08',
    # + ULTIMATE LEYENDA — $19.98
    'principal+gold-pc': 'https://buy.stripe.com/eVq14n9Ua97mgM48lZ7kc09',
    # + MULTICONSOLA PC — $19.98 (mismo combo que "multi+supremo" de la landing PC)
    'principal+gold-mob': 'https://buy.stripe.com/8x200j7M2cjygM4au77kc06',
    # LOS TRES — $25.99 (mismo link "todo" de la landing PC)
    'principal+gold-pc+gold-mob': 'https://buy.stripe.com/3cI6oHaYe83i67q6dR7kc07',
}


def main():
    if not os.path.exists(ARCHIVO):
        sys.exit('no existe ' + ARCHIVO)
    s = io.open(ARCHIVO, encoding='utf-8').read()
    n0 = len(s)

    cambiados, faltantes = [], []
    for clave, url in LINKS.items():
        # clave entre comillas ("principal+gold-pc": "...") o sin comillas (principal: "...")
        patrones = [
            re.compile(r'("%s":\s*)"[^"]*"' % re.escape(clave)),
            re.compile(r'(\b%s:\s*)"[^"]*"' % re.escape(clave)),
        ]
        total = 0
        for patron in patrones:
            s, n = patron.subn(lambda m: m.group(1) + '"' + url + '"', s)
            total += n
        if total == 0:
            faltantes.append(clave)
            continue
        cambiados.append('%s  ->  %s  (x%d)' % (clave, url, total))

    for c in cambiados:
        print('   ' + c)
    if faltantes:
        sys.exit('ERROR links.py: no se encontraron en el HTML: ' + ', '.join(faltantes))

    io.open(ARCHIVO, 'w', encoding='utf-8').write(s)
    print('%s: %d -> %d bytes' % (ARCHIVO, n0, len(s)))

    for clave, url in LINKS.items():
        if url not in s:
            sys.exit('ERROR links.py: %s no quedo aplicado' % clave)
    print('validaciones OK')


if __name__ == '__main__':
    main()

# 2026-08-12: nace la landing mobile (PACK SUPREMO MOBILE como principal,
#             Leyenda y Multiconsola PC como order bumps, paleta azul neon).
#             Payment Links kc08/kc09 nuevos; kc06/kc07 compartidos con la
#             landing PC porque los combos son identicos.
