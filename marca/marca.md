# Marca de los reels · @pvmr.dev

Look elegido: **C · Tarjeta de vidrio, versión clara** (28/10/2026). Sale de dos reels de referencia: la tarjeta de vidrio flotando arriba de la cabeza y la línea punteada (referencia 2), y la etiqueta en mono con un cuadradito de color (referencia 1). Se tomó el estilo, nunca la marca de otro.

Muestra aprobada: `marca/muestras/look-c-claro.jpg` y `marca/muestras/muestra-final.jpg`. El código que las dibuja está en `marca/muestras/` y sirve de referencia exacta de medidas.

## Colores
| Uso | Hex |
|---|---|
| Rojo del logo (acento, cajas de palabra clave, cuadradito de la etiqueta) | `#A8402C` |
| Crema (ficha del logo, fondos claros) | `#F5F1E8` |
| Blanco (texto sobre video, vidrio, piezas del logo) | `#FFFFFF` |
| Noche (texto dentro de la tarjeta de vidrio) | `#141816` |
| Borde de las piezas del logo en la ficha | `#D6CCBA` |

Nada de coral de Claude (`#D97757`), azul ni verde lima. El terracota viejo (`#C9583F`) queda solo para los carruseles.

## Letras (en `marca/fuentes/`, todas libres, OFL)
- **Inter** (`marca/fuentes/Inter.ttf`, variable): títulos, subtítulos y textos de las tarjetas. Grosor 750–900.
- **Instrument Serif Italic** (`marca/fuentes/InstrumentSerif-Italic.ttf`): una sola palabra o frase destacada dentro de la tarjeta (por ejemplo «3 preguntas»). Nunca en subtítulos.
- **JetBrains Mono** (`marca/fuentes/JetBrainsMono.ttf`, variable, grosor 600): la etiqueta de la tarjeta, en MAYÚSCULAS («PROMPT», «SIRVE PARA»).

Como Inter es variable, los textos se dibujan con Pillow (o HTML) y se ponen encima: ni drawtext ni ASS.

## Gancho (0–3 s)
- Una **tarjeta de vidrio blanca** arriba de la cabeza: caja x 150–930, y 250–504 (en 1080×1920), esquinas de 36 px, fondo desenfocado (gaussiano 30) + blanco al 80 %, borde blanco de 3 px y sombra suave abajo.
- Dentro: cuadradito rojo de 16 px + etiqueta en mono 28 px (noche al 67 %); debajo el texto en Inter 56 px grosor 750, color noche, como mucho 2 líneas; la palabra clave en Instrument Serif Italic 78 px roja.
- Una **línea punteada blanca** baja desde la tarjeta por el costado (x ≈ 900) y termina en un punto rojo. Nunca cruza la cara.
- En los 3 primeros segundos es el único texto grande. Sin subtítulos encima.

## Subtítulos
- A la altura del pecho, centrados en x = 540, entre y ≈ 1270 y 1490.
- Línea normal: Inter 66 px grosor 800, blanca, con sombra suave (desenfoque 20, 65 % de opacidad, 6 px abajo). Trozos de 3 a 6 palabras.
- **Palabra clave: sola, en MAYÚSCULAS, Inter 112 px grosor 900, blanca, dentro de una caja roja `#A8402C`** con esquinas de 22 px y 30 px de aire a cada lado. Una por frase: el sustantivo, la cifra o el verbo que importa.
- Mientras hay una tarjeta en pantalla, los subtítulos siguen abajo (no se ocultan); la tarjeta y los subtítulos nunca se pisan.

## Tarjetas a mitad del video
- Mismo vidrio blanco que el gancho, arriba de la cabeza, sin tocar el logo (x 100–840).
- Etiqueta en mono + hasta 3 renglones en Inter 52 px con un tilde blanco en un cuadrado rojo de 36 px.
- Una idea por tarjeta, entra en la palabra que la nombra.

## Logo
- **Versión clara**: ficha crema `#F5F1E8` de 84 px con esquinas de 16 px, las piezas en blanco con borde `#D6CCBA` de 2 px y el cuadradito rojo. Arriba a la derecha: x 860, y 232. Sombra suave.
- Ninguna letra pisa el logo.

## Transiciones
- Un corte en cada salto de la toma, con un zoom suave constante en cada plano (100 → 108 %, alternando acercar y alejar). Nada de golpes, destellos ni barridos.
- Las tarjetas entran subiendo con un desenfoque que se aclara en 0,3–0,5 s y salen al revés. Las cajas rojas de palabra clave entran con un rebote corto.
- Efectos de efectos-reels solo si se piden, y como mucho uno o dos por reel.

## Sonido
- Voz limpia a −14 LUFS, pico por debajo de −1,5 dB.
- Sin música salvo que se pida.
- Efectos suaves solo en las acciones (entra una tarjeta, se marca un tilde): un clic o un chime bajito. Nunca un golpe encima de una palabra.

## Reglas fijas
1. Nada tapa la cara, ni un fotograma.
2. Las letras no pisan el logo.
3. En los 3 primeros segundos, un solo texto grande.
4. Zona segura de Instagram: nada importante en los 220 px de arriba, los 380 px de abajo ni los 140 px de la derecha (por debajo de y 1480).
5. Voseo y textos sin faltas; «ChatGPT», «Claude» y los nombres propios se corrigen a mano en la transcripción.
6. Reels con cara: tips de IA en general, nunca sobre el negocio, Nakama ni Kumi.

## Correcciones apuntadas
- (vacío: lo que corrijas en los próximos reels se apunta acá para que no se repita)
