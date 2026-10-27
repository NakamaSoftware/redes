# Método · de la idea (o la referencia) al MP4

## 1. El pedido en una frase
«Animación de 6 s para la intro de mi vídeo sobre X, en 1920×1080, con el estilo de esta referencia».
Si falta algo que cambia el resultado (formato, duración, si va con voz), pregúntalo: máximo 3 preguntas en un mensaje.

## 2. Recursos: preguntar siempre
«¿Tienes logos, imágenes, vídeos, fuentes o colores de marca que quieras usar?»
- **Sí** → a `recursos/`, y se usan tal cual.
- **No** → los buscas con `recursos.py`:
  - logos: oficiales, de Iconify;
  - iconos: de Lucide, Tabler o Phosphor;
  - fuentes: de Google Fonts;
  - imágenes: de Openverse (CC);
  - vídeos: de Pexels o Pixabay si hay clave; si no, de Wikimedia;
  - modelos 3D: de Poly Haven (CC0).
- Siempre: revisa `LICENCIAS.md` y díselo a la persona.

## 3. La referencia manda
1. `referencia.py` sobre el archivo o el enlace (Pinterest, Instagram, YouTube, TikTok, Vimeo, X).
2. Copia al BRIEF: curvas por tipo de elemento, duraciones, escalonado, comportamiento de la cámara, cortes y paleta.
3. Lo que no se mide (tipografía, composición, estilo de las formas) se toma mirando `hoja.jpg`.
4. Al terminar, `revisar.py` compara tu render con la referencia: curvas y ritmo tienen que salir ≥ 8.

## 4. Storyboard antes que código
Una línea por tiempo:

| t | elemento | entra o sale | curva y duración | dirección y desenfoque | cámara | palabra |
|---|---|---|---|---|---|---|

Si hay voz, los tiempos salen de las palabras (de su transcripción con tiempos). Si no, del ritmo de la referencia (escalonado típico).

## 5. Código
- Parte de un ejemplo si encaja; si no, de la plantilla 2D o 3D.
- Una escena = una animación = un MP4.
- La función de pintar depende **solo de t**.
- Coloca los elementos en una rejilla mental (márgenes de 150 px en 1920) y deja libres las zonas de subtítulos y botones.

## 6. Previa, revisión y entrega
1. `render.mjs hoja <nombre>`: miras 12 fotogramas repartidos.
2. `render.mjs video todas --calidad previa`: 1080p30, rápido.
3. `revisar.py`: notas ≥ 8.
4. Parada: la persona aprueba.
5. `render.mjs video todas --calidad final`: 4K60. Además `--calidad hd` (1080p60) y `--transparente` si lo va a montar encima de otro vídeo.
6. Entrega: la lista de MP4 con su duración, y la ruta del HTML editable para reutilizarlo.
