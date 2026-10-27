# API del motor (motor.js)

```html
<link rel="stylesheet" href="../motor/estilo.css">
<script src="../motor/motor.js"></script>
<script>
escena({ duracion: 5, ancho: 1920, alto: 1080, fondo: 'marca' }, (MG) => {
  // 1) crear los elementos (una sola vez)
  const t1 = MG.el(`<div class="mg-abs mg-titulo" style="font-size:110px">Hola <em>mundo</em></div>`);
  // 2) devolver la función que pinta el instante t (se llama en cada fotograma, en cualquier orden)
  return (t) => { MG.camara(t, 1, 1.08); const e = MG.entra(t1, t, 0.3, { dy: 120 }); MG.pon(t1, 300 + e.x, 400 + e.y, e.s); };
});
</script>
```

**Regla de oro:** la función de pintar depende **solo de `t`**. Nada de `Math.random()` sin semilla, de `Date.now()` ni de estado que dependa del fotograma anterior. Así cada fotograma es exacto y el render se puede hacer en paralelo.

| Función | Qué hace |
|---|---|
| `MG.el(html, padre?)` | crea un elemento dentro del mundo (`.mg-abs` = posición absoluta) |
| `MG.entra(el, t, t0, {d, dx, dy, escala0, curva, base, extra, desenfoque})` | fundido + desplazamiento + escala con curva + **desenfoque de movimiento**; devuelve `{x, y, s, p}` para `pon` |
| `MG.pon(el, x, y, s, extra)` | coloca el elemento (`translate` + `scale` + transformaciones extra) |
| `MG.camara(t, z0, z1, ox, oy)` | zoom lineal de toda la escena (la cámara nunca se para) |
| `MG.desenfoca(el, sx, sy)` | desenfoque direccional a mano (σ en px) |
| `MG.tarjeta(src, w, h, t0, {desde, bucle, fijo})` | tarjeta con un **vídeo** colocado fotograma a fotograma |
| `MG.video(src, t0, …)` · `MG.registrar(video, {...})` | vídeos sin tarjeta (texturas 3D, montajes propios) |
| `MG.texto(txt, clase, 'palabras'|'letras')` + `MG.animaTexto(el, t, t0, {paso, d, dy, curva})` | texto que entra por palabras o letras, escalonado |
| `MG.linea(d, color, ancho)` → `.dibuja(p)` | trazo SVG que se dibuja de 0 a 1 |
| `MG.contador(el, t, t0, t1, desde, hasta, {sufijo, prefijo, decimales, curva})` | número que cuenta |
| `MG.curvas.*` · `MG.k(t, a, b)` · `MG.lerp(a, b, x)` | curvas (ver curvas.md), progreso 0–1 entre a y b, interpolación |

Clases útiles (`estilo.css`): `.mg-titulo` (con `<em>` en el color de acento), `.mg-sub`, `.mg-chip`, `.mg-cristal`, `.mg-tarjeta`, `.mg-brillo`.
Fondos: `fondo: 'marca'` (rejilla y halo), `'transparente'` (para render con alfa) o ninguno.
Fondo configurable (opcional, se combina con `fondo: 'marca'`):
- `trama: { tipo: 'rejilla'|'lineas'|'puntos'|'nada', tamano: 70, intensidad: .5 }`: tamaño en px; intensidad 0–1 (1 = la de la marca). Puntos discretos: `tamano: 36, intensidad: .5`.
- `halo: .3` o `{ fuerza: .3, x: 50, y: 112 }`. `MG.halo(x, y)` lo mueve en cada fotograma (p. ej. siguiendo al elemento principal).
- `degradado: 'aurora'|'barrido'|'suave'` o `{ tipo, fuerza: .35, ciclo: 12 }`: degradado animado con el acento y el acento 2. Lo mueve el motor según t, así que el render es exacto; si `ciclo` divide la duración, el bucle cierra perfecto.
Vista previa en el navegador: abre el HTML con `?ver` al final de la dirección.
