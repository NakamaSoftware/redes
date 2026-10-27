# Curvas de velocidad · cómo leerlas y cómo elegirlas

La curva es lo que separa una animación «de plantilla» de una profesional. Todas están en `MG.curvas` (motor.js) con el mismo
nombre que devuelve `referencia.py`, así lo que se mide en la referencia se escribe tal cual en la escena.

## Catálogo

| Nombre (motor.js) | Equivalente en After Effects | Cómo se siente | Úsala para |
|---|---|---|---|
| `lineal` | sin suavizado | mecánico, constante | **cámaras** (zoom lento, órbitas), cintas que corren, contadores de tiempo |
| `suave` | Easy Ease 33 % | correcto, neutro | transiciones discretas |
| `salidaCubica` | Easy Ease Out | arranca rápido y se posa | entradas de texto, UI |
| `salidaQuint` | Ease Out fuerte (~80 %) | muy rápido y frena largo («premium») | entradas de tarjetas, logos, cifras |
| `salidaExpo` | Expo Out | casi instantáneo y se desliza | flashes, golpes de ritmo |
| `entradaCubica` | Easy Ease In | acelera y se va | **salidas** (lo que se va de pantalla) |
| `entradaSalidaQuint` | Easy Ease 75–90 % (curva «Apple») | lento-rápido-lento | movimientos de A a B que ya están en pantalla, cámaras que se reencuadran |
| `atras` | Back Out | se pasa una vez y vuelve | botones, iconos, pop de elementos pequeños |
| **`rebote`** | muelle / Overshoot natural | se pasa ~10 % y se asienta | **la curva de la marca para todo lo que entra** |
| `reboteSuave` | muelle amortiguado | se pasa poco, elegante | cámaras que siguen un flujo, elementos grandes |
| `reboteFuerte` | muelle con oscilaciones | juguetón | ilustraciones, mascotas, iconos con carácter |
| `bezier(x1,y1,x2,y2)` | gráfico de velocidad de AE / cubic-bezier CSS | cualquiera | copiar exactamente una curva de AE o de una web |
| `muelle(amort, frec)` | Elastic / expresión de rebote | a medida | ajustar el rebote a la referencia |

Fórmula del rebote de la marca: `1 − e^(−5,5·x) · cos(2π · 1,15 · x)`. Necesita ~1,5× la duración de una entrada normal
para asentarse (`entra()` ya lo tiene en cuenta).

## Cómo leer `referencia/analisis.md`
- **Pico de velocidad** (en qué punto del movimiento va más rápido):
  - 0–25 % → ease out (`salidaCubica` / `salidaQuint` / `salidaExpo`);
  - 40–60 % → ease in-out (`entradaSalidaQuint`, `suave`);
  - 75–100 % → ease in (`entradaCubica`).
- **Se pasa > 3 %** → hay rebote o «back»: `rebote` si oscila y se asienta; `atras` si se pasa una sola vez.
- **Error < 0,05** → la curva es casi exacta. **0,05–0,12** → la familia es correcta, prueba también la alternativa. **> 0,12** → mira `curvas.png` (la línea blanca es la referencia; la coral, la curva elegida).
- **Duración** de cada movimiento y **escalonado típico**: cópialos tal cual en `entra(el, t, t0, { d })` y en los `t0` de los elementos hermanos.
- **Cámara quieta X %**: si la referencia nunca se para (0–5 %), la tuya tampoco. Si se para mucho, es un estilo de cortes secos: respétalo.

## Precisión medida (prueba con curvas conocidas)
En la prueba de `referencia.py` con 5 movimientos de curva conocida (lineal, salidaQuint, entradaSalidaQuint, rebote y entradaCubica):
- detectó los **5 movimientos**, con su inicio y su duración reales (±1 fotograma a 30 fps);
- acertó la **familia** de curva en los **5**;
- en 2 acertó también la variante exacta; en los otros 3 eligió la vecina más cercana: `salidaCubica` en lugar de `salidaQuint`, y `reboteSuave` en lugar de `rebote`.

Con OpenCV instalado mide con flujo óptico denso, más fino en vídeos con varios elementos a la vez.
