# PACK SUPREMO MOBILE™ — landing

Landing mobile de The Game Box. Misma arquitectura que la landing PC
(`estebanninoc/consola-ultimate`), con el PACK SUPREMO MOBILE como producto
principal, Ultimate Leyenda y Multiconsola PC como order bumps, y paleta
**azul neón**.

⚠️ `index.html` se REGENERA en cada deploy — NUNCA editarlo a mano.

Pipeline del workflow (`desplegar.yml`):

1. Baja los módulos compartidos de `consola-ultimate` (moneda, carrito,
   imagenes, descargar, procesar + assets-manifest.txt) — única fuente de
   verdad de la tabla de precios por moneda.
2. `descargar.py` → `procesar.py` → `construir.py` (clona la página del
   bundle mobile de Shopify).
3. `post.py` corre en orden: `precios → links → imagenes → moneda →
   carrito → meta → mobilizar → colores`.

Propios de esta landing: `precios.py` (mobile 9.99/-72%), `links.py`
(kc08/kc09/kc06/kc07), `meta.py` (pixel con prefijo MB-), `mobilizar.py`
(identidad mobile) y `colores.py` (verde → azul neón).

El workflow solo se dispara con cambios en `scripts/**` o el propio workflow.
