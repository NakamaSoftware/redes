# 3D real con three.js (motor3d.js)

Úsalo cuando la idea pide **volumen, luz o una cámara de verdad**: logos en 3D, productos, objetos que orbitan, tarjetas en
el espacio, gráficas con profundidad. Para tarjetas planas con perspectiva basta con el 3D de CSS de `motor.js` (más ligero).

## Plantilla
`nuevo.py <carpeta> --plantilla 3d` (o un ejemplo 3D). El HTML necesita el `importmap` de la plantilla y `type="module"`.

```js
import { escena3d } from '../motor/motor3d.js';
escena3d({ duracion: 6, fondo: 'marca' }, ({ THREE, MG, scene, camara, obj, mat, rig, entra3d, luces }) => {
  const caja = obj.cajaRedonda(1.6, 1.6, 1.6, mat.coral()); scene.add(caja);
  return (t) => { rig.orbita(t, { radio: 10, desde: -25, hasta: 20 }); entra3d(caja, t, 0.3); };
});
```

## Objetos (`obj`)
- `cajaRedonda(w, h, d, mat, radio)`, `esfera(r, mat)`, `toro(r, tubo, mat)`, `cilindro(r, h, mat)`.
- `tarjeta(src, w, h, t0, {desde})`: una tarjeta con esquinas redondeadas, canto y **un vídeo** que se coloca fotograma a fotograma.
- `modelo(url)`: un .glb o .gltf; busca modelos libres con `recursos.py modelo3d "…"`.
- `suelo()`: solo recoge las sombras, así se sigue viendo el fondo de la marca. `suelo(mat.oscuro())` da un suelo visible.

## Materiales (`mat`)
- `coral()`: el acento, con barniz.
- `oscuro()`: las tarjetas y los cuerpos.
- `vidrio()`: transmisión real.
- `metal()`.
- `brillo(color, intensidad)`: emisivo.
- `video(v)` e `imagen(url)`.

## Luces
Ya montadas en `luces`:
- una clave cálida desde arriba a la derecha, con sombras suaves;
- un relleno frío;
- un contraluz coral, para recortar las siluetas.

Hay un entorno de estudio (`RoomEnvironment`) que da reflejos realistas al metal y al cristal. Para un barrido de luz, mueve una `PointLight` a lo largo del objeto (lo hace el ejemplo `logo-3d`).

## Cámara (`rig`) · nunca se para
| Rig | Qué hace | Curva por defecto |
|---|---|---|
| `orbita(t, {radio, desde, hasta, altura, centro})` | gira alrededor del centro de «desde» a «hasta» grados, en toda la escena | `lineal` |
| `dolly(t, {desde, hasta, t0, t1})` | se acerca o se aleja en línea recta | `lineal` |
| `grua(t, {desde, hasta, z, centro})` | sube o baja mientras mira al centro | `salidaQuint` |
| `recorrido(t, puntos, {curva, mirarA})` | viaja por una curva suave que pasa por los puntos (Catmull-Rom) | `entradaSalidaQuint` |
| `temblor(t, f)` | cámara en mano sutil y determinista | — |
| `mirar(p)` | apunta a un punto | — |

Combínalos. Por ejemplo, `orbita` con un radio que va bajando (dolly + órbita), y `temblor` al final. Las entradas de objetos van con `entra3d(objeto, t, t0, {d, subida, escala})`: escala y subida con rebote.

## Lente de cine y pantalla en 3D
- `profundidad: { apertura, max }` y `movimiento: { muestras, obturador }` en la configuración dan desenfoque de profundidad real (con `lente.enfocar(punto)`) y desenfoque de movimiento por obturador a cualquier escena 3D.
- `obj.pantalla(...)` pone una interfaz real en 3D y `planos.*` la recorre.
- `obj.mascotaClaude()` es la mascota de Claude Code como personaje (anda, parpadea, saluda); `obj.logoClaude()` y `obj.svg(d)` son logos SVG extruidos con bisel.
- Todo esto está en `pantalla-3d.md`.

## Rendimiento
- 4K a 60 fps con sombras: unos 2–4 min por cada 6 s en la GPU. Sombras de 2048 px y antialiasing ya están ajustados.
- Muchas tarjetas con vídeo: cada una es un `<video>` que se coloca en cada fotograma. Hasta ~15 va bien; con más, usa vídeos cortos y pequeños (320×400, `-g 1`).
- Si no hay GPU (o el navegador sin ventana no la usa), three.js pinta con SwiftShader: va más lento, pero sale igual.
