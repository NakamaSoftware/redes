# Marca de los reels · @pvmr.dev

Look elegido: **C · Tarjeta de vidrio, versión clara** (28/10/2026). **Fijado: Pablo dijo «me gusta» el 28/10/2026.** Sale de dos reels de referencia: la tarjeta de vidrio flotando arriba de la cabeza y la línea punteada (referencia 2), y la etiqueta en mono con un cuadradito de color (referencia 1). Se tomó el estilo, nunca la marca de otro.

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
- **Cortinilla** (idea de la guía de Trescendit, 30/10): una pantalla roja `#A8402C` a pantalla completa, 0,4–0,6 s, que tapa el cambio de toma. Sirve para esconder un corte feo (la mano que va al celular, un salto de cámara) y, en los reels por pasos, para anunciar cada paso. Lleva «PASO 02» en JetBrains Mono y el número grande en Instrument Serif blanca. Detrás de la cortinilla cambia la toma; la voz sigue sonando. Suena un `whoosh` a −8 dB de la voz.

## Sonido
- Voz limpia a −14 LUFS, pico por debajo de −1,5 dB.
- **Música de fondo: sí** (elegido el 29/10). Synthwave sin derechos generado con `synthflow_render.mjs music synthwave`, a −13 dB (≈ 16 dB por debajo de la voz), con bajada automática cuando habla (`sidechaincompress` threshold 0.04, ratio 4) y fundido de entrada y salida.
- Efectos suaves solo en las acciones (entra una tarjeta, se marca un tilde): un clic o un chime bajito. Nunca un golpe encima de una palabra.
- **Volúmenes, contra la voz** (referencia de la guía de Trescendit, 30/10). Se miden en dB por debajo de la voz, no en volumen absoluto:

  | Sonido | Contra la voz | Cuándo |
  |---|---|---|
  | Golpe grave (`impact-bass`) | −4 dB | solo al arrancar o en el momento más grande; nunca sobre una palabra |
  | Whoosh | −8 dB | cuando entra un panel o una cortinilla |
  | Notificación | −8 dB | cuando «llega» un mensaje |
  | Pop | −9 dB | cuando aparece algo (tilde, chip, etiqueta) |
  | Clic | −10 dB | botones, enviar |
  | Teclas (`typing`) | −12 dB | mientras se escribe un texto, cortado al largo del texto |
  | Música | −10 a −16 dB | −16 con mucho eco en la voz (la tapa menos); −10 si la voz está limpia |

## Variantes según el tipo de reel
El look C (tarjeta de vidrio clara) es el de siempre. Para dos tipos de video hay variantes con los mismos colores y letras. Muestras: `marca/muestras/variantes.jpg`.

### Variante «Pasos» (para «cómo hacer X en N pasos»)
- Se turnan dos tomas: **CARA** (el video con las tarjetas de vidrio del look C) y **PAPEL** (pantalla completa sobre papel; la voz sigue sonando).
- Papel: crema `#F5F1E8` con una cuadrícula muy tenue cada 40 px (`#ECE6DA`).
- Título del paso en Instrument Serif 120 px, color noche, con la idea clave en cursiva roja («Contalo en *una línea*»). Arriba, etiqueta «PASO 02» en JetBrains Mono gris con el cuadradito rojo.
- Ventanas blancas estilo macOS (semáforo, título centrado, esquinas de 28 px, sombra suave) donde el texto se escribe letra por letra.
- Al empezar cada paso, **cortinilla** roja con el número (ver Transiciones); detrás cambia la toma.
- Subtítulos en el papel: de 1 a 3 palabras, Inter 800 de 62 px color noche, la palabra clave en rojo y en mayúsculas.

### Variante «Pantalla partida» (para comparaciones, datos o una historia)
- Arriba, de y 0 a y 740: un pizarrón crema `#EDE7DB` con una línea noche de 4 px abajo. Abajo: el video a todo lo ancho, bajado para que la cabeza quede debajo de la línea.
- Un pizarrón por idea: no se desliza, cambia con un fundido de 0,2 s. Cada idea lleva algo que la explique (barras, una línea de tiempo, un antes y después), no una foto sola. Título corto en Inter 800 de 48 px.
- Lo que todavía no se nombró va en gris `#A9AEA9`; lo importante en rojo, con un **círculo rojo que se dibuja** alrededor en 0,5 s.
- Subtítulos: una palabra a la vez, blanca, Inter 800 de 66 px con sombra, justo debajo de la línea, arriba de la cabeza.
- Pantalla completa solo una vez, para esconder un corte feo.

## Reglas fijas
1. Nada tapa la cara, ni un fotograma.
2. Las letras no pisan el logo.
3. En los 3 primeros segundos, un solo texto grande.
4. Zona segura de Instagram: nada importante en los 220 px de arriba, los 380 px de abajo ni los 140 px de la derecha (por debajo de y 1480).
5. Voseo y textos sin faltas; «ChatGPT», «Claude» y los nombres propios se corrigen a mano en la transcripción.
6. Reels con cara: tips de IA en general, nunca sobre el negocio, Nakama ni Kumi.
7. Referencias: si te pasan un link de un reel, se baja con `yt-dlp` y se analiza cuadro por cuadro. Se copia la forma de editar, nunca logos, caras, música ni textos de otro.

## Correcciones apuntadas
- **29/10 · La mano que arranca o corta la grabación nunca se ve.** Revisar cuadro por cuadro el primer y el último segundo de cada toma (la mano entra por abajo, a veces por el centro y no por la esquina). Si aparece cuando ya no habla, se recorta; si aparece mientras habla, se congela el cuadro limpio más cercano o se tapa con una pantalla completa.
- **29/10 · Menos eco en la voz, sin que suene robótica.** Antes de la cadena de voz: `dereverb.py` con T60 0,5 y piso 0,22 (más fuerte suena metálico). Después: `afftdn` nf −32, puerta con mirada adelante de 12 ms (`sidechaingate` threshold 0.04, ratio 3.5, range 0.16, release 110), −4 dB en 280 Hz, +1,5 dB en 4 kHz y compresión suave (ratio 1,6). La música de fondo ayuda a tapar el eco que queda. No subir la voz con compresión fuerte: levanta el eco.
- **29/10 · `afftdn` atrasa la voz 25 ms:** compensar con `atrim=start=0.025` para que vaya con la boca.
- **29/10 · Ningún efecto de sonido encima de la primera sílaba de una frase** (un clic tapó la «P» de «Pasa»).
- **29/10 · Las tomas se pasan a espejo** (como se ven en el celular al grabar).
