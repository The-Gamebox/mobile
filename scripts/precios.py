#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Precios de la LANDING MOBILE, en un solo lugar.

construir.py se baja la pagina de Shopify (bundle mobile — misma plantilla que
la landing PC, mismos numeros de origen), asi que los precios que trae son los
de Shopify. Este script los reescribe sobre el HTML ya generado.

Tabla actual (debe coincidir con los Prices de Stripe):

    PACK SUPREMO MOBILE (principal)   9.99   antes  36.00   -72%
    Ultimate Leyenda    (gold-pc)     9.99   antes  35.00   -71%
    Multiconsola PC     (gold-mob)    9.99   antes  33.00   -70%

    principal + leyenda              19.98
    principal + multiconsola         19.98
    los tres juntos                  25.99   (suma 29.97, descuento extra 3.98)

⚠️ En esta landing la tarjeta "gold-mob" es la MULTICONSOLA PC (la rebautiza
scripts/mobilizar.py): los anclajes del HTML de origen son los mismos de
siempre ($35.20 / 88.00), pero el destino es el precio de la multiconsola.

Es idempotente.
"""
import io
import os
import sys

ARCHIVO = os.environ.get('CU_INDEX', 'index.html')
MARCA = 'CU-PRECIOS v1'

PRINCIPAL, PRINCIPAL_ANTES, PRINCIPAL_PCT = 9.99, 36.00, 72   # PACK SUPREMO MOBILE
LEYENDA,   LEYENDA_ANTES,   LEYENDA_PCT   = 9.99, 35.00, 71   # ULTIMATE LEYENDA (gold-pc)
MULTI,     MULTI_ANTES,     MULTI_PCT     = 9.99, 33.00, 70   # MULTICONSOLA PC (gold-mob)
TODO = 25.99                      # los tres juntos, con descuento extra
TODO_ANTES = PRINCIPAL_ANTES + LEYENDA_ANTES + MULTI_ANTES

# lo que trae Shopify -> lo que debe decir
TEXTOS = [
    ('<span class="cu-main-price">$39.99</span>',   '<span class="cu-main-price">$%.2f</span>' % PRINCIPAL),
    ('<span class="cu-main-compare">$117.64</span>', '<span class="cu-main-compare">$%.2f</span>' % PRINCIPAL_ANTES),
    ('<span class="cu-main-pct">-66%</span>',        '<span class="cu-main-pct">-%d%%</span>' % PRINCIPAL_PCT),
    ('<span class="cu-bump-price cu-leyenda-price">$34.00</span>',
     '<span class="cu-bump-price cu-leyenda-price">$%.2f</span>' % LEYENDA),
    ('<span class="cu-bump-price cu-leyenda-price">$35.20</span>',
     '<span class="cu-bump-price cu-leyenda-price">$%.2f</span>' % MULTI),
    ('data-compare="85.00" data-price="34.00"', 'data-compare="%.2f" data-price="%.2f"' % (LEYENDA_ANTES, LEYENDA)),
    ('data-compare="88.00" data-price="35.20"', 'data-compare="%.2f" data-price="%.2f"' % (MULTI_ANTES, MULTI)),
    ('var MAIN_PRICE   = 39.99;',   'var MAIN_PRICE   = %.2f;' % PRINCIPAL),
    ('var MAIN_COMPARE = 117.64;',  'var MAIN_COMPARE = %.2f;' % PRINCIPAL_ANTES),
]

BLOQUE = '''<script>
/* ══════════════════════════════════════════════════════════
   CU-PRECIOS v1 — el pack completo tiene descuento adicional

   Llevar los tres NO es la suma de los tres:
       %(pri).2f + %(ley).2f + %(mul).2f = %(suma).2f
       precio real del combo            = %(todo).2f
   El carrito suma por defecto, asi que hay que corregirlo cuando
   los dos packs estan marcados.
   ══════════════════════════════════════════════════════════ */
(function(){
  "use strict";
  var TODO = %(todo).2f, TODO_ANTES = %(antes).2f;

  function fmt(v){
    return (window.CU_FX && window.CU_FX.fmt) ? window.CU_FX.fmt(v) : "$" + v.toFixed(2);
  }
  function ambos(){
    var a = document.getElementById("cu-cb-gold-pc");
    var b = document.getElementById("cu-cb-gold-mob");
    return !!(a && b && a.checked && b.checked);
  }
  function nota(mostrar){
    var n = document.getElementById("cu-todo-nota");
    if(!mostrar){ if(n) n.style.display = "none"; return; }
    if(!n){
      var fila = document.querySelector(".cu-total-row");
      if(!fila || !fila.parentNode) return;
      n = document.createElement("div");
      n.id = "cu-todo-nota";
      n.style.cssText = "font-size:10.5px;font-weight:800;letter-spacing:.4px;color:#1db954;" +
                        "text-align:right;margin-top:3px;";
      n.textContent = "\\u2713 DESCUENTO EXTRA POR LLEVAR TODO";
      fila.parentNode.insertBefore(n, fila.nextSibling);
    }
    n.style.display = "";
  }

  var _upd = window.updateTotals;
  if(typeof _upd !== "function") return;

  window.updateTotals = function(){
    if(!ambos()){ nota(false); return _upd.apply(this, arguments); }
    var t = document.getElementById("cu-total");
    var s = document.getElementById("cu-savings");
    if(t) t.textContent = fmt(TODO);
    if(s) s.textContent = "-" + fmt(TODO_ANTES - TODO);
    nota(true);
  };
})();
</script>
''' % dict(pri=PRINCIPAL, ley=LEYENDA, mul=MULTI, suma=PRINCIPAL + LEYENDA + MULTI,
           todo=TODO, antes=TODO_ANTES)


def main():
    if not os.path.exists(ARCHIVO):
        sys.exit('no existe ' + ARCHIVO)
    s = io.open(ARCHIVO, encoding='utf-8').read()
    n0 = len(s)

    if MARCA in s:
        i = s.find(MARCA)
        ini = s.rfind('<script>', 0, i)
        fin = s.find('</script>', i)
        if ini != -1 and fin != -1:
            s = s[:ini] + s[fin + len('</script>\n'):]
            print('bloque anterior retirado (idempotente)')

    # ── textos exactos ──────────────────────────────────────────────
    hechos = 0
    for viejo, nuevo in TEXTOS:
        if viejo in s:
            s = s.replace(viejo, nuevo)
            hechos += 1
    print('reemplazos exactos: %d de %d' % (hechos, len(TEXTOS)))

    # ── el resto de apariciones sueltas ─────────────────────────
    sueltos = [
        ('$39.99',  '$%.2f' % PRINCIPAL),
        ('$117.64', '$%.2f' % PRINCIPAL_ANTES),
        ('"39.99"', '"%.2f"' % PRINCIPAL),
        ('-$77.65', '-$%.2f' % (PRINCIPAL_ANTES - PRINCIPAL)),
        ('68% OFF', '%d%% OFF' % PRINCIPAL_PCT),
        ('66% OFF', '%d%% OFF' % PRINCIPAL_PCT),
        # tachados de los packs: conservar el % de descuento tras la rebaja
        ('$85.00',  '$%.2f' % LEYENDA_ANTES),
        ('$88.00',  '$%.2f' % MULTI_ANTES),
        ('"85.00"', '"%.2f"' % LEYENDA_ANTES),
        ('"88.00"', '"%.2f"' % MULTI_ANTES),
    ]
    for viejo, nuevo in sueltos:
        n = s.count(viejo)
        if n:
            s = s.replace(viejo, nuevo)
            print('   %-10s x%d -> %s' % (viejo, n, nuevo))

    # ── comentarios de los links (la verdad de esta landing) ──
    comentarios = [
        ('/* ULTIMATE LEYENDA         — $34.00 */', '/* ULTIMATE LEYENDA         — $%.2f */' % LEYENDA),
        ('/* PACK SUPREMO MOBILE      — $35.20 */', '/* MULTICONSOLA PC          — $%.2f */' % MULTI),
    ]
    for viejo, nuevo in comentarios:
        if viejo in s:
            s = s.replace(viejo, nuevo)
    print('comentarios de los links actualizados')

    # ── los -60% de las dos tarjetas de pack ────────────────────
    for ancla, pct in (('id="cu-b-gold-pc"', LEYENDA_PCT), ('id="cu-b-gold-mob"', MULTI_PCT)):
        i = s.find(ancla)
        if i == -1:
            continue
        j = s.find('cu-bump-pct cu-leyenda-pct">', i)
        if j == -1:
            continue
        k = s.find('<', j)
        s = s[:j] + 'cu-bump-pct cu-leyenda-pct">-%d%%' % pct + s[k:]
    print('porcentajes de los packs: -%d%% y -%d%%' % (LEYENDA_PCT, MULTI_PCT))

    # ── la regla del combo completo ─────────────────────────────
    j = s.rfind('</body>')
    if j == -1:
        sys.exit('no se encontro </body>')
    s = s[:j] + BLOQUE + s[j:]

    io.open(ARCHIVO, 'w', encoding='utf-8').write(s)
    print('%s: %d -> %d bytes' % (ARCHIVO, n0, len(s)))

    # ── validaciones ────────────────────────────────────────────
    fallos = []
    if s.count(MARCA) != 1:
        fallos.append('el bloque del combo no quedo inyectado')
    for viejo in ('$39.99', '$117.64', '$34.00', '$35.20', '-$77.65', '$85.00', '$88.00'):
        if viejo in s:
            fallos.append('quedo un precio viejo sin cambiar: %s' % viejo)
    if '$%.2f' % PRINCIPAL not in s:
        fallos.append('no aparece el precio nuevo del principal')
    if fallos:
        sys.exit('ERROR precios.py:\n  - ' + '\n  - '.join(fallos))
    print('validaciones OK')


if __name__ == '__main__':
    main()
