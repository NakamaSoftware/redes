# Reels · zona segura, subtítulos, texto detrás de la cabeza y variantes

Aprendido editando el reel «Motion graphics con Claude» (octubre de 2026) con las correcciones de Diego. Aplica a todo vertical 1080×1920.

## 1. Zona segura de Instagram Reels
| Zona | Qué la tapa | Regla |
|---|---|---|
| y < 260 | cabecera (Reels, cámara) | nada importante. **Ojo:** «AL MES» encima del precio no se vio en el reel publicado |
| y > 1480 | usuario, texto del post, audio | ni subtítulos ni CTA por debajo |
| x > 940 | botones (me gusta, comentar, compartir) | nada importante a la derecha |
- Lo importante va entre **y 260–1480** y **x 60–940**. Excepción: palabras gigantes detrás de la cabeza pueden salirse un poco.
- Etiquetas o tarjetas «arriba» (precio, plan): mejor **a un lado de la cara** (x 50–320, y 450–760) que encima de la cabeza.

## 2. Subtítulos con jerarquía
- **La palabra clave siempre sola en la línea de debajo**, grande (≈ 2× la línea de arriba), en el acento; arriba, las palabras normales pequeñas en Semibold. Nunca la clave en la misma línea que el resto.
- Fuente: SF Compact Display (Semibold arriba, Heavy/Black la clave). Entradas **suaves y naturales**: 0,3–0,45 s de desenfoque + subida, sin rebote. La clave entra en el instante en que se dice.
- Si la clave es **«Claude»**, la mascota de Claude Code (`claude-code-logo.svg`) va a su lado, con un salto de entrada y un balanceo leve.
- Precios pegados: «17$», sin espacio.
- Oculta el subtítulo cuando un gráfico ya dice lo mismo o hay una escena a pantalla completa.
- Hazlos con una escena del kit (`ejemplos` de reel: `subtitulos.html`); los generadores de los editores no dejan la clave en su línea.

## 3. Texto detrás de la cabeza
- La cabeza debe tapar **≈ 20 %** de la palabra: súbela o baja un poco el encuadre mientras dure.
- Recorte: `python scripts/recortar.py toma.mp4` (rembg, máscara erosionada 2 px y despill). Sin eso queda **halo** (un borde del color del fondo alrededor de la silueta) y el pelo se transparenta.
- Lo que va **delante** de la persona (CTA, comentarios, chips) en otra capa encima del recorte.

## 4. Montaje en el editor
- Render de capas con `--transparente` (ProRes 4444). Si el editor ignora el alfa, sepáralo en **color + máscara** y une con **mate de luminancia**:
  `ffmpeg -i capa.mov -filter_complex "[0]format=rgba,split[a][b];[a]format=yuv420p[c];[b]alphaextract,format=yuv420p[m]" -map "[c]" capa-color.mp4 -map "[m]" capa-mascara.mp4`
- En los cortes: **un solo zoom suave** (in u out, alternando) con curva suave. Nada de rebotes de escala, destellos ni parpadeos en cada corte.
- Escenas a pantalla completa: entra con zoom + fundido de 0,4 s y vuelve a cámara con zoom de salida; nunca la persona en miniatura dentro de la escena.

## 5. Variantes para Trial Reels
- Reordena **frases completas** de la toma (que el audio tenga sentido): gancho distinto en cada una (el 3D, el precio, el CTA, el texto cinético…).
- Cambia estilo de subtítulo, tema (`--tema`), gráficos e inserciones; mantén la zona segura y las reglas de arriba en todas.
- Ejemplo completo: proyecto `reel-claude` (`scripts/construir_variantes.py` + `escenas/variante.html`): una receta por variante → placa, máscara y audio cortados + configuración → MP4 con su audio.

## 6. Logos
- Usa el logo **de Claude** (isotipo coral, `obj.logoClaude`) salvo que pidan otro. Para extruir un SVG con huecos que salga relleno (p. ej. la «A» de Anthropic): `obj.svg(d, mat, { antihorario: true })`.
