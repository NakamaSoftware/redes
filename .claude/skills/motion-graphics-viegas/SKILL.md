---
name: motion-graphics-viegas
description: >
  Crea motion graphics profesionales en código directamente desde Claude Code (2D y 3D real con three.js) y entrega un
  MP4 por animación, con la calidad de After Effects: curvas de velocidad exactas, rebote natural, desenfoque de
  movimiento, cámara que nunca se para, objetos 3D con luces y cámara real. Parte de una referencia (vídeo propio o
  enlace de Pinterest, Instagram, YouTube o TikTok) y mide sus curvas, ritmo, cámara y paleta para reproducirla; pregunta
  por logos, imágenes y vídeos y, si no los hay, los busca en la nube con su licencia. Comprueba primero que el equipo
  tiene todo (Node, ffmpeg, Playwright, Chrome, GPU…) y lo instala con permiso. Úsala cuando se pida una animación, un
  motion graphic, un intro, un logo animado, una escena 3D, «anima esto como en esta referencia», un lower third, una
  gráfica animada o «hazme las animaciones de mi vídeo», aunque no se nombre la skill. Para «pon mi interfaz / app / web
  en 3D» o «mi logo en 3D recorriendo la interfaz», mejor la skill interfaces-3d-viegas. Kit de Viegas Estudio.
---

# Motion Graphics Viegas · kit de animación en código

Cada animación es una página HTML que se pinta **fotograma a fotograma** con `window.seek(t)` y se fotografía con Chrome
sin ventana: el resultado es exacto y repetible, y se convierte en MP4 con ffmpeg. La misma idea que los carruseles y los
reels de Viegas, ahora para cualquier motion graphic: intros, logos, flujos, listas, gráficas, chats, 3D.

## Lo que hay en la skill

| Carpeta | Qué es |
|---|---|
| `motor/motor.js` | motor 2D: curvas (las de After Effects + rebote natural), `entra()` con desenfoque de movimiento, cámara, vídeos en tarjetas, texto por palabras/letras, líneas que se dibujan, contadores |
| `motor/motor3d.js` | 3D real con three.js: objetos (cajas redondeadas, esferas, toros, tarjetas con vídeo, modelos .glb), materiales (coral, oscuro, vidrio, metal, brillo), luces de estudio, sombras y **rigs de cámara** (órbita, dolly, grúa, recorrido, cámara en mano) |
| `motor/pantalla3d.js` · `motor/lente3d.js` · `motor/mascota3d.js` · `motor/svg3d.js` | **pantalla en 3D**: una interfaz real (HTML, web, clip de pantalla) como losa 3D, con recortes que salen hacia la cámara y planos de cámara para interfaces · **lente de cine**: desenfoque de profundidad y de movimiento para cualquier escena 3D · **la mascota de Claude Code** como personaje 3D (anda, salta, saluda) y logos SVG extruidos (`obj.mascotaClaude`, `obj.logoClaude`, `obj.svg`) |
| `motor/piezas3d.js` · `motor/logos/` · `motor/fuentes/` | **pack «3D con three.js»**: parámetros, formato 9:16/16:9, fondo transparente, coral de Claude fijo, logos reales como textura, placas, texto 3D extruido (Inter Tight) y bokeh. Ver «3D con three.js» más abajo |
| `motor/estilo.css` · `plantillas/estilo.json` | tokens de marca (colores, fuentes, radios). Para otra marca solo se cambian aquí |
| fondo vivo (`motor.js`) | además de `fondo: 'marca'`: `trama` (rejilla, líneas o puntos con tamaño e intensidad), `halo` (fuerza y posición; `MG.halo(x, y)` lo mueve) y `degradado` animado (`aurora`, `barrido`, `suave`, con fuerza y ciclo). Lo mueve el motor según t: render exacto. Detalle en `referencias/motor.md` |
| `motor/temas/` | **temas de color** listos (`claro`, `neon`, `lujo`, `pastel`): cada uno redefine los tokens de `estilo.css`. Se aplican al renderizar con `--tema <nombre>` sin tocar el HTML. Para un tema nuevo, copia uno y cambia los valores. Los ejemplos ya leen todos sus colores de los tokens (también el 3D: acento, fondo y niebla) |
| `scripts/preparar.py` | comprueba el equipo e instala lo que falte (con permiso) |
| `scripts/nuevo.py` | crea un proyecto (plantilla 2D, 3D o cualquier ejemplo) |
| `scripts/referencia.py` | **analiza una referencia** (archivo o enlace): planos, cámara, movimientos y su curva, escalonado, paleta |
| `scripts/recursos.py` | busca y descarga en la nube iconos, logos, fuentes, imágenes, vídeos y modelos 3D, y apunta la licencia |
| `scripts/render.mjs` | render a MP4 (una por animación): previa 1080p30 · hd 1080p60 · final 4K60 · transparente (ProRes 4444) · en paralelo · `pantalla`: una interfaz o una web en fotogramas para la pantalla en 3D |
| `scripts/recortar.py` | **recorta a la persona** de una toma sin halo (rembg + erosión + despill) → `-color.mp4` y `-mascara.mp4` para texto detrás de la cabeza |
| `scripts/revisar.py` | revisa cada MP4: formato, golpes, cámara quieta, curvas frente a la referencia, ritmo y color |
| `referencias/` | `metodo.md` (el proceso), `curvas.md` (cómo leer y elegir curvas), `estilo.md` (la guía de estilo Viegas), `tres-d.md` (3D y cámara), `pantalla-3d.md` (interfaz en 3D y lente de cine), `motor.md` (la API), **`reels.md` (zona segura de Instagram, subtítulos con jerarquía, texto detrás de la cabeza, montaje en el editor, variantes para Trial Reels)** |
| `ejemplos/escenas/` | 15 ejemplos editables: logo con barrido y arco 3D, flujo de nodos, lista escalonada, carrusel ovalado, cierre, rejilla de estilos, proceso paso a paso, chat de Claude, interruptor, y en 3D: logo 3D, tarjetas 3D, producto 3D, gráfica 3D, **pantalla 3D** y **pantalla 3D en Reel con la mascota de Claude Code en 3D** (con sus interfaces en `ejemplos/interfaces/`) |
| `ejemplos/mp4/` | el MP4 de cada ejemplo, para enseñar qué se puede hacer (en el kit están en `5-EJEMPLOS`; si faltan, se renderizan con `render.mjs`) |

## La primera vez: preparar el equipo
1. Ejecuta `python <skill>/scripts/preparar.py --json` (en Mac, `python3`).
2. Si `listo` es `false`, enséñale a la persona **la lista de lo que falta, en lenguaje claro**, y **pide permiso** antes de instalar. Con el sí: `preparar.py --instalar --prueba`.
3. **Nunca instales nada sin permiso.** Lo opcional (opencv, yt-dlp, GPU NVIDIA, fuente SF Compact) no bloquea: avisa de qué mejora.

## El proceso (cada paso termina en una prueba o en una parada)

1. **Pedido y referencia.** Pregunta solo lo que cambia el resultado (máx. 3 preguntas en un mensaje):
   - ¿Para qué es y en qué formato? 1920×1080 · 1080×1920 · 1080×1350 · 1080×1080. ¿Duración? ¿Va con voz? (si va con voz: los tiempos de las palabras).
   - ¿Hay **referencia**? Archivo o enlace de Pinterest, Instagram, YouTube o TikTok.
   - **¿Tienes recursos que añadir?** Logos, imágenes, vídeos, fuentes, colores de marca. Si no los tiene, dile que los buscas tú en la nube (paso 3).
2. **Analiza la referencia** (si la hay): `python scripts/referencia.py "<archivo o enlace>"`.
   - Lee `referencia/analisis.md` y mira `curvas.png` y `hoja.jpg`.
   - Apunta en el BRIEF: curvas por tipo de elemento, duración media de los movimientos, escalonado, si la cámara se para o no, cortes por segundo y paleta.
   - **Reprodúcelo con esas mismas curvas y tiempos**: es la diferencia entre «parecido» y «igual».
3. **Recursos.** Lo que la persona dé va a `recursos/`. Lo que falte se busca con `python scripts/recursos.py icono|logo|fuente|imagen|video|modelo3d "<búsqueda>"` (busca en inglés si no hay resultados). Revisa `recursos/LICENCIAS.md` y díselo a la persona: logos de marca, solo para referirse a la marca; CC BY, con atribución.
4. **Proyecto:** `python <skill>/scripts/nuevo.py "<carpeta>" --plantilla 2d|3d|<ejemplo> --ancho … --alto …`. Si un ejemplo encaja, **parte de él** (`ejemplos/escenas/`): ya trae la guía de estilo aplicada.
5. **BRIEF.md y STORYBOARD.md:** una línea por tiempo con qué entra, la curva, la duración, la dirección, la cámara y la palabra que lo dispara. **Parada: enséñalo y espera el OK** si el encargo es largo.
6. **Código** (`escenas/<nombre>.html`), siguiendo `referencias/estilo.md` y `referencias/motor.md`. En 3D, además, `referencias/tres-d.md`.
   - **Pantalla en 3D** (una interfaz, un panel o una web en 3D): lee `referencias/pantalla-3d.md`. Proyecto con `--plantilla pantalla-3d`.
     Primero, la interfaz en fotogramas: `node scripts/render.mjs pantalla <interfaz|web>`. Después, la escena con `obj.pantalla` y `planos.claves`.
7. **Vista previa:** `node scripts/render.mjs hoja <nombre>` y **mírala**. Corrige lo que se cruce, tape o aparezca de golpe. Luego `node scripts/render.mjs video todas --calidad previa` (1080p30, rápido).
8. **Revisión:** `python scripts/revisar.py`. Todo tiene que dar ≥ 8; corrige y repite. **Parada: enseña la vista previa y espera el OK.**
9. **Entrega:** con el OK, `node scripts/render.mjs video todas --calidad final` (4K60). También `--calidad hd` (1080p60) para redes y `--transparente` si va encima de otro vídeo. Entrega **un MP4 por animación** en `resultados/`, con su `.json` (duración, fps, tamaño).
   - **Otra paleta** sin tocar el HTML: `--tema claro|neon|lujo|pastel|<tuyo>` (la salida lleva `-<tema>` en el nombre). Para la marca de la persona, cambia los tokens de `motor/estilo.css` y `estilo.json`; nunca escribas colores fijos en las escenas: usa `var(--acento)`, `rgba(var(--halo), .5)`, `rgba(var(--claro), .1)`…

## Las reglas de estilo que no se rompen (detalle en `referencias/estilo.md`)
1. **Nada aparece de golpe:** todo entra escalonado (0,05–0,3 s), con **rebote natural** y **desenfoque de movimiento** según la velocidad.
2. **La cámara nunca se para:** zoom lineal suave de principio a fin (1,00 → 1,08–1,12) o una órbita o recorrido continuos.
3. **Nada se cruza** y **nada tapa** lo importante (caras, texto, botones). Zonas libres: subtítulos (los 180 px de abajo) y el suscríbete.
4. **Jerarquía:** etiqueta pequeña, título grande y la palabra clave en el color de acento. Una idea por escena.
5. **Si se habla de algo animado, se enseña animado:** tarjetas con vídeo, nunca capturas fijas.
6. **Sincronía:** si hay voz, cada elemento entra en la palabra que lo nombra, con 0,1–0,3 s de adelanto.
7. **Coherencia en la serie:** mismo formato, misma curva por tipo de elemento, mismo fondo y la misma paleta en todas las animaciones (lo comprueba `revisar.py`).
8. **Editable siempre:** se entrega el MP4 y se guarda el HTML, que es la plantilla para la próxima.

## Reels (vertical): lee `referencias/reels.md`
- **Zona segura:** lo importante entre y 260–1480 y x 60–940.
- **Subtítulos:** palabra clave SOLA en la línea de debajo, grande y en el acento; con «Claude», la mascota al lado.
- **Texto detrás de la cabeza:** recorte con `scripts/recortar.py`; la cabeza tapa ≈ 20 % de la palabra.
- **Cortes:** un zoom suave por tramo, sin rebotes ni destellos.

## 3D con three.js (pack de 8, en `ejemplos/escenas/3d-*.html`)
Cuando pidan una pieza 3D de estas («el asterisco de Claude en 3D», «la mascota saltando», «un teléfono 3D con mi reel», «una transición de cubo»…), **parte de la escena** y cambia solo los parámetros. Todas usan `motor/piezas3d.js` (encima de `motor3d.js`): bloque `<script id="params">` o la dirección (`?titular=Hola&acento=%23D97757`), formato `#9x16` (por defecto) · `#16x9` · `#1x1` · `#4x5`, fondo noche azul (`temas/noche-azul.css`) o `?fondo=transparente` + `render.mjs … --transparente` (ProRes 4444 con alfa). Llevan profundidad de campo y desenfoque de movimiento reales (`lente3d.js`), cámara que nunca se para y salida inversa (`"salida": false` para que se quede). **El logo de Claude y la mascota van siempre en coral #D97757** (aunque el tema cambie el acento); los logos de marcas son los reales de svgl en `motor/logos/` (claude, claude-code, youtube, instagram, tiktok, gmail) o la ruta a tu SVG/PNG.

| Escena | Qué hace | Parámetros propios | Pídeselo así |
|---|---|---|---|
| `3d-asterisco` | el asterisco de Claude extruido llega en 12 piezas, se arma y gira con barrido de luz | `titular`, `subtitulo`, `piezas`, `metal` | «Usa motion-graphics-viegas con 3d-asterisco: el asterisco de Claude en 3D que se arma en piezas, titular "[texto]", 9:16» |
| `3d-mascota-salto` | la mascota de Claude Code cae a una plataforma, salta 3 veces (aplasta, estira, rebota) y saluda | `titular`, `subtitulo`, `saltos`, `altura` | «…con 3d-mascota-salto: la mascota saltando sobre la plataforma, titular "[texto]"» |
| `3d-abanico` | pila de ventanas de app que se abre en abanico con bokeh; la del centro sale a cámara | `titular`, `ventanas` [{titulo, tipo: chat·grafica·lista·codigo·timeline, imagen}], `destacada` | «…con 3d-abanico: mis 5 pantallas [capturas] en abanico 3D, titular "[texto]"» |
| `3d-barras` | columnas de cristal que se llenan con rebote, cifras contando, grúa + órbita | `titular`, `datos` [{valor, etiqueta}], `sufijo`, `acento` | «…con 3d-barras: gráfica 3D con [datos], titular "[texto]"» |
| `3d-red-globo` | globo de puntos, Claude en el centro y logos reales conectados con arcos de luz y pulsos | `titular`, `centro`, `logos` | «…con 3d-red-globo: Claude conectado a [YouTube, Instagram, TikTok, Gmail], titular "[texto]"» |
| `3d-titular` | titular 3D extruido (Inter Tight) letra a letra desde detrás de la cámara, con desenfoque de movimiento | `titular` (líneas con `\n` o `|`), `clave`, `subtitulo`, `acento` | «…con 3d-titular: el titular "[línea 1|línea 2]" en 3D, la palabra "[clave]" en coral» |
| `3d-telefono` | teléfono 3D que gira hacia cámara con tu reel en pantalla + CTA y píldora con tu usuario | `video`, `titular`, `usuario`, `red`, `marco` | «…con 3d-telefono: mi reel [ruta.mp4] en un teléfono 3D, CTA "[texto]" y @[usuario]» |
| `3d-cubo-transicion` | transición de reel: cada escena es una cara de un prisma que gira 90° con zoom a través | `caras` (2–4: video · imagen · etiqueta/titulo · logo), `giro` | «…con 3d-cubo-transicion: pasa de [clip A] a [tarjeta "texto"] con el cubo 3D» |

Render igual que el resto: `python <skill>/scripts/nuevo.py <carpeta> --plantilla 3d-telefono` → `node scripts/render.mjs hoja 3d-telefono` → `node scripts/render.mjs video 3d-telefono --calidad previa` (y `final` con el OK). Los vídeos de las escenas (`vid/…`) van junto a la escena: copia tu clip a `escenas/vid/` o pon su ruta en el parámetro. Para 16:9 añade la escena a `escenas.json` con `"hash": "#16x9"`.

## Si algo falla
- **Pantalla negra o escena que no carga:** `node scripts/render.mjs frame <nombre> 1 prueba.png` y mira la consola (los errores salen como «error en la página»).
- **Render lento:** baja `--hilos` si hay poca RAM; con NVIDIA, NVENC se usa solo. Las escenas con 20 vídeos o más tardan más en cargar (es normal).
- **Instagram no descarga:** hace falta la sesión del navegador. `referencia.py` lo reintenta solo con Chrome, Edge o Firefox. Si aun así falla, pide el archivo.

## Plantillas por nicho (26, en `plantillas/nichos/`)
Para negocios reales: coach, abogado/asesor, inmobiliaria, restaurante, fitness, tienda online, fotógrafo, cursos, eventos/negocio local y genéricas (encuesta, «guarda este post», lower third, intro con logo). Catálogo con sector, parámetros y la frase para pedirla en `plantillas/nichos/nichos.json`.
Cuando pidan «la plantilla <id> para mi <negocio>» (o algo que encaje con una), **parte de ella y cambia solo los parámetros** (bloque `params`):
1. `python <skill>/scripts/nuevo.py "<carpeta>" --plantilla 2d --escenas 0` y copia en `escenas/` el `<id>.html` y las carpetas `_nichos/` y `fotos/` de `plantillas/nichos/`.
2. Edita el bloque `params`: textos (`*palabra*` = color de acento), cifras, `marca`, `logo` (ruta al logo de la persona; vacío = inicial), fotos (las suyas, en `escenas/`), `paleta` (`noche` = noche azul de Viegas, por defecto, o `claro`), `acento` (#hex) y `formato` (`9x16` por defecto; `4x5` y `16x9` donde lo indica la cabecera).
3. `node scripts/render.mjs hoja <id>` → míralo → `video <id> --calidad previa` → con el OK, `--calidad final`. `gen-lower-third` y `gen-guarda` admiten `"transparente": true` (render con `--transparente`).
Reglas: datos legales, reseñas y testimonios **reales** (pídelos); logos de marcas solo los oficiales de `_nichos/` (Google, Google Maps, WhatsApp, de svgl.app) o los que dé la persona; fotos de ejemplo CC0 (`fotos/LICENCIAS.md`), cámbialas por las suyas. Muestras en el Laboratorio: `lab/nichos.html`.
