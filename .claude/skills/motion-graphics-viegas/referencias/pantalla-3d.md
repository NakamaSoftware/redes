# Pantalla en 3D: una interfaz real como objeto 3D (pantalla3d.js + lente3d.js)

Una interfaz de verdad (tu panel, una web, una app, una grabación de pantalla) se pone **dentro de una losa 3D** con canto,
esquinas redondeadas y sombra. La cámara la sobrevuela con **enfoque de cine** (desenfoque de profundidad real) y
**desenfoque de movimiento** (obturador), y trozos de la interfaz pueden **salir hacia la cámara**. Es la técnica del vídeo
de GLEA que circuló en Threads en octubre de 2026 («HTML + 3D»), hecha solo con código: sin Blender y sin instalar nada.

Ejemplos completos:
- `ejemplos/escenas/pantalla-3d.html` (horizontal) con `ejemplos/interfaces/editor-viegas.html`.
- `ejemplos/escenas/pantalla-3d-reel.html` (Reel, con la mascota de Claude Code en 3D) con `ejemplos/interfaces/terminal-claude.html`.

MP4 de muestra en `ejemplos/mp4/`: `pantalla-3d-1080p.mp4` y `pantalla-3d-reel-1080p.mp4`. Plantillas: `--plantilla pantalla-3d` o `--plantilla pantalla-3d-reel`.

## Cuándo usarla
- Enseñar una herramienta, una función nueva o un flujo de trabajo: Claude Code, el panel, el grabador, una web.
- Intros de YouTube y ganchos de Reels con «la pantalla» como protagonista.
- Una slide de carrusel con la interfaz en 3D (render 1080×1350).

**No** sirve para que se lea un texto largo: una interfaz tumbada y desenfocada no se lee. Lo importante se enseña **de
frente y unos segundos** (como el panel de Claude del ejemplo). Es la crítica que más se repitió en el hilo de Threads: «todo
vuela y no se entiende nada». Pocas claves de cámara, una idea por tramo y siempre al ritmo de lo que pasa en la interfaz.

## Los 3 pasos
1. **La interfaz.** Puede ser cualquiera de estas cuatro:
   - un HTML animado con el motor (`interfaces/<nombre>.html`, igual que una escena 2D);
   - un HTML fijo o una web (`https://…`): se hace una captura, o con `--entera` la página entera, para desplazarla;
   - un clip de pantalla `.mp4` (por ejemplo de la skill extractos-pantalla, ya censurado);
   - una imagen `.png` o `.jpg`.
2. **Fotogramas de la interfaz** (solo si es HTML o web):
   `node scripts/render.mjs pantalla <nombre|archivo.html|https://…>` → `pantallas/<nombre>/`
   - Previa: 30 fps a ×2 (3840 px de ancho, para que se lea en los primeros planos).
   - Con `--calidad final`: 60 fps a ×3.
   - Otras opciones: `--fps`, `--escala`, `--entera`, `--nombre`, `--ancho` y `--alto` (de la página), `--png`.
   - Rehazlo cada vez que cambie la interfaz; la escena 3D no hace falta tocarla.
3. **La escena 3D** (`escenas/<nombre>.html`, plantilla `nuevo.py <carpeta> --plantilla pantalla-3d`) y su render, como siempre:
   `render.mjs hoja`, luego `video --calidad previa`, luego `revisar.py`, y `--calidad final` solo cuando se apruebe.

## La pantalla (`obj.pantalla`)
```js
escena3d({ duracion: 8, fondo: 'marca', fov: 32, niebla: false,
  profundidad: { apertura: 16, max: 22 }, movimiento: { muestras: 8, obturador: 0.5 } }, ({ scene, obj, planos, MG }) => {
  const ui = obj.pantalla('../pantallas/mi-panel', { ancho: 8, radio: 20 });   // o 'clip.mp4', o 'captura.png'
  ui.rotation.x = -1.25; scene.add(ui);                                         // tumbada, como un portátil abierto del todo
  const chat = ui.recorte(1516, 76, 392, 560);                                  // x, y, ancho, alto en px de la interfaz
  return (t) => { planos.revelado(t, ui); chat.levantar(t, 2.2, { altura: 0.6, vuelta: 6.2 }); };
});
```
| Opción | Qué hace | Por defecto |
|---|---|---|
| `ancho` | ancho en unidades 3D (el alto sale de la interfaz) | 6 |
| `radio` | esquinas, en px de la interfaz | 18 |
| `grosor` | grosor de la losa | 1,8 % del ancho |
| `marco` | borde oscuro alrededor, en px | 0 |
| `t0` · `desde` · `bucle` | cuándo arranca la interfaz y desde qué segundo suyo | 0 · 0 · no |
| `brillo` | 0–1, para oscurecerla | 1 |
| `aspecto` + `desplaza: { t0, t1, desde, hasta, curva }` | página más alta que la pantalla: se ve una ventana y se desplaza (web larga con `--entera`) | — |
| `cuerpo` | material del canto | negro mate |

- `ui.punto(x, y, z)`: un punto de la interfaz (en px) en 3D. Sirve para enfocar, apuntar o poner cosas encima (la mascota, un cursor 3D).
- `ui.recorte(x, y, w, h, { radio, grosor, sombra, hueco })` → `.levantar(t, t0, { altura, d, curva, escala, inclina, vuelta })`:
  ese trozo sale hacia la cámara con rebote, deja su hueco vacío y una sombra suave. Con `vuelta`, vuelve a su sitio.
- La interfaz se ve **tal cual** (sin luces ni tone mapping encima), con mipmaps y filtrado anisótropo: se lee bien aunque esté de canto.

## Los planos de cámara (`planos`)
Todos se miden **desde la pantalla**, así que funcionan esté como esté colocada. Los números de «inclinación» dan por hecho
que está **tumbada** (`rotation.x` ≈ −1,2); si está de pie, «de frente» es una inclinación de 90.

| Plano | Qué hace |
|---|---|
| `planos.revelado(t, ui, {t0, t1})` | de rasante, casi pegada a la interfaz, a casi de frente, alejándose: la presenta entera |
| `planos.sobrevuelo(t, ui, {t0, t1})` | vuelo bajo de lado a lado, con el foco recorriéndola |
| `planos.empuje(t, ui, {objetivo: [x, y]})` | de lejos y en ángulo a cerca y de frente, sobre un detalle |
| `planos.orbita(t, ui, {t0, t1})` | órbita lenta alrededor |
| `planos.claves(t, ui, [{ t, objetivo, inclinacion, giro, distancia, balanceo, enfoque }, …])` | **la buena**: varias claves y la cámara pasa por todas sin pararse (curva con velocidad continua) |

Qué significa cada campo:
- `objetivo`: a qué punto mira, en px de la interfaz.
- `inclinacion`: el ángulo sobre la pantalla (8–15 es rasante, 90 de frente).
- `giro`: 0 es desde el borde de abajo; los números positivos giran hacia la derecha.
- `distancia`: en anchos de pantalla.
- `balanceo`: cámara ladeada, en grados.
- `enfoque`: el punto que sale nítido. Por defecto, el objetivo. Con `[x, y, z]` enfoca algo levantado (un recorte).

Los planos hechos aceptan `desde` y `hasta` para cambiar sus claves (por ejemplo, `{ hasta: { distancia: 0.9 } }`).

**Cómo se monta una escena buena** (lo que hace el ejemplo):
1. Una clave por cada cosa que pasa en la interfaz, en el mismo segundo en que pasa.
2. Empieza rasante sobre algo con color, nunca sobre una zona negra.
3. Lo que se tiene que leer va de frente (inclinación de 50 o más) y cerca.
4. Acaba con la interfaz entera y el título en la zona libre de arriba.

## Personajes y logos que recorren la interfaz (como la mascota del vídeo de GLEA)
- `obj.mascotaClaude({ tam })`: la mascota de Claude Code como personaje 3D. Las proporciones salen del SVG oficial (`claude-code-logo.svg`). Lleva cuerpo, ojos brillantes, brazos y 4 patas, y se maneja así:
  - `m.andar(fase, fuerza)`: las patas por turnos y un bote suave;
  - `m.parpadear(p)`;
  - `m.saludar(p, t)`;
  - `m.brazosArriba(a)`: para los saltos.
- `obj.logoClaude({ tam, fondo, bisel })`: el isotipo de Claude extruido de su SVG real.
- `obj.svg(d, material, o)`: cualquier logo o icono a partir del `d` de un `<path>`.
- Ponlos **dentro de la pantalla** (`ui.add(grupo)`) y colócalos con `ui.local(x, y, altura)`: se mueven en px de la interfaz, sobre ella.
  - Para que estén de pie, mete el modelo en un grupo con `rotation.x = π/2`.
  - Para que miren a la cámara: `Math.atan2(cam.x, -cam.y)`, con `cam = ui.worldToLocal(camara.position)` relativo a su sitio.
- `ui.sombra(tamPx).poner(x, y, { altura, opacidad })`: sombra suave debajo, porque la cara de la pantalla no recibe sombras reales.
- Luz propia: dos `PointLight` que lo siguen (una clave cálida delante y un contraluz coral detrás). Cuando la cámara lo ve de frente, baja la clave y llévala de lado, o el personaje queda plano.
- La cámara puede seguirlo: mezcla el `objetivo` de las claves con la posición media del personaje (± 0,14 s).
  - En vertical (9:16) el plano es muy estrecho: lo que se siga tiene que ir a `distancia` ≥ 0,5, o se sale por los lados.
- Ejemplo completo: `ejemplos/escenas/pantalla-3d-reel.html` (Reel 1080×1920) con `ejemplos/interfaces/terminal-claude.html`.
  - La mascota anda detrás del texto mientras se escribe, salta de herramienta en herramienta, camina sobre la barra de render y al final saluda junto a la vista previa.
  - MP4: `ejemplos/mp4/pantalla-3d-reel-1080p.mp4`.

## La lente de cine (`lente3d.js`, para cualquier escena 3D, no solo pantallas)
- `profundidad: { apertura, max, foco }`:
  - `apertura` es lo que se desenfoca lo que está lejos del foco (px a 1080p; 10–18 queda de cine);
  - `max` es el tope;
  - el foco lo ponen los planos solos. A mano: `lente.enfocar(punto)` o `lente.foco = 7`. Puedes cambiarlo en cada fotograma: un *rack focus*.
- `movimiento: { muestras: 8, obturador: 0.5 }`: desenfoque de movimiento real. Cada fotograma son 8 subfotogramas dentro de un obturador de 180°, promediados. Todo lo que se mueve en 3D lo recibe; la capa 2D lleva el suyo (`MG.entra`).
- Sin `profundidad` ni `movimiento`, el 3D se pinta como siempre: las escenas de antes salen idénticas.
- Coste en la 5090:
  - el ejemplo (8 s) tarda unos 25 s en previa (1080p30) y unos 47 s en hd (1080p60), con 8 muestras;
  - en 4K, cuenta de 4 a 6 veces más;
  - si va lento, baja `muestras` a 4–6.
- En la vista previa del navegador (`?ver`) no hay subfotogramas, para que vaya en tiempo real.

## Límites
- La interfaz es una «película» de fotogramas: dentro del 3D no se puede pulsar ni hacer scroll. Lo que tenga que pasar, pasa en su HTML (con `window.seek`) o en el clip.
- Las webs con login, o las que cambian solas (anuncios, vídeos), salen como estén en ese momento. Mejor tu propio HTML o un clip limpio.
- Datos privados en pantalla: usa clips de extractos-pantalla (ya censurados) o censura en el HTML.
- Los fotogramas ocupan: a ×2, unos 0,7 MB cada uno (9 s a 60 fps ≈ 370 MB); a ×3, el doble largo (≈ 0,8 GB) en `pantallas/`. Se pueden borrar cuando el vídeo esté aprobado (pídelo antes).
