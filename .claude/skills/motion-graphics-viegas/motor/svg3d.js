// svg3d.js · Motion Graphics Viegas · un trazado SVG (el atributo d de un <path>) convertido en un objeto 3D extruido,
// con bisel y su base en el suelo: logos e iconos de verdad, no aproximaciones. Lo usa motor3d: obj.svg(d, …) y obj.logoClaude().
// Entiende M L H V C S Q T Z (en mayúscula o minúscula). Los arcos (A) no: exporta el SVG con «convertir arcos en curvas».
import * as THREE from 'three';

// isotipo de Claude (claude.svg, caja de 100 × 100)
export const CLAUDE = 'm19.6 66.5 19.7-11 .3-1-.3-.5h-1l-3.3-.2-11.2-.3L14 53l-9.5-.5-2.4-.5L0 49l.2-1.5 2-1.3 2.9.2 6.3.5 9.5.6 6.9.4L38 49.1h1.6l.2-.7-.5-.4-.4-.4L29 41l-10.6-7-5.6-4.1-3-2-1.5-2-.6-4.2 2.7-3 3.7.3.9.2 3.7 2.9 8 6.1L37 36l1.5 1.2.6-.4.1-.3-.7-1.1L33 25l-6-10.4-2.7-4.3-.7-2.6c-.3-1-.4-2-.4-3l3-4.2L28 0l4.2.6L33.8 2l2.6 6 4.1 9.3L47 29.9l2 3.8 1 3.4.3 1h.7v-.5l.5-7.2 1-8.7 1-11.2.3-3.2 1.6-3.8 3-2L61 2.6l2 2.9-.3 1.8-1.1 7.7L59 27.1l-1.5 8.2h.9l1-1.1 4.1-5.4 6.9-8.6 3-3.5L77 13l2.3-1.8h4.3l3.1 4.7-1.4 4.9-4.4 5.6-3.7 4.7-5.3 7.1-3.2 5.7.3.4h.7l12-2.6 6.4-1.1 7.6-1.3 3.5 1.6.4 1.6-1.4 3.4-8.2 2-9.6 2-14.3 3.3-.2.1.2.3 6.4.6 2.8.2h6.8l12.6 1 3.3 2 1.9 2.7-.3 2-5.1 2.6-6.8-1.6-16-3.8-5.4-1.3h-.8v.4l4.6 4.5 8.3 7.5L89 80.1l.5 2.4-1.3 2-1.4-.2-9.2-7-3.6-3-8-6.8h-.5v.7l1.8 2.7 9.8 14.7.5 4.5-.7 1.4-2.6 1-2.7-.6-5.8-8-6-9-4.7-8.2-.5.4-2.9 30.2-1.3 1.5-3 1.2-2.5-2-1.4-3 1.4-6.2 1.6-8 1.3-6.4 1.2-7.9.7-2.6v-.2H49L43 72l-9 12.3-7.2 7.6-1.7.7-3-1.5.3-2.8L24 86l10-12.8 6-7.9 4-4.6-.1-.5h-.3L17.2 77.4l-4.7.6-2-2 .2-3 1-1 8-5.5Z';

// d → THREE.ShapePath (con el eje y hacia arriba, como en 3D)
export function trazado(d) {
  const sp = new THREE.ShapePath(), tok = d.match(/[a-df-z]|-?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?/gi) || [];
  let i = 0, cmd = '', x = 0, y = 0, x0 = 0, y0 = 0, cx = 0, cy = 0, prev = '';
  const num = () => parseFloat(tok[i++]), hay = () => i < tok.length && !/^[a-z]$/i.test(tok[i]);
  const P = (a, b) => [a, -b];                              // SVG va con y hacia abajo
  while (i < tok.length) {
    if (/^[a-z]$/i.test(tok[i])) cmd = tok[i++]; else if (!cmd) break;
    const rel = cmd === cmd.toLowerCase(), C = cmd.toUpperCase();
    if (C === 'Z') { sp.currentPath?.closePath?.(); x = x0; y = y0; prev = C; continue; }
    do {
      if (C === 'M') { const a = num() + (rel ? x : 0), b = num() + (rel ? y : 0); sp.moveTo(...P(a, b)); x = x0 = a; y = y0 = b; cmd = rel ? 'l' : 'L'; prev = 'M'; break; }
      if (C === 'L') { x = num() + (rel ? x : 0); y = num() + (rel ? y : 0); sp.lineTo(...P(x, y)); }
      else if (C === 'H') { x = num() + (rel ? x : 0); sp.lineTo(...P(x, y)); }
      else if (C === 'V') { y = num() + (rel ? y : 0); sp.lineTo(...P(x, y)); }
      else if (C === 'C' || C === 'S') {
        let a, b; if (C === 'C') { a = num() + (rel ? x : 0); b = num() + (rel ? y : 0); } else { [a, b] = 'CS'.includes(prev) ? [2 * x - cx, 2 * y - cy] : [x, y]; }
        const c = num() + (rel ? x : 0), e = num() + (rel ? y : 0), f = num() + (rel ? x : 0), g = num() + (rel ? y : 0);
        sp.bezierCurveTo(...P(a, b), ...P(c, e), ...P(f, g)); cx = c; cy = e; x = f; y = g;
      } else if (C === 'Q' || C === 'T') {
        let a, b; if (C === 'Q') { a = num() + (rel ? x : 0); b = num() + (rel ? y : 0); } else { [a, b] = 'QT'.includes(prev) ? [2 * x - cx, 2 * y - cy] : [x, y]; }
        const f = num() + (rel ? x : 0), g = num() + (rel ? y : 0); sp.quadraticCurveTo(...P(a, b), ...P(f, g)); cx = a; cy = b; x = f; y = g;
      } else { i++; }                                       // arcos u órdenes que no se entienden: se saltan
      prev = C;
    } while (hay());
  }
  return sp;
}

// objeto 3D: ancho «tam», grosor «fondo» (fracción del ancho), bisel; centrado en x/z y con la base en y = 0 (de pie)
export function extruir(d, material, o = {}) {
  const formas = trazado(d).toShapes(o.antihorario ?? false), tam = o.tam ?? 1;   // antihorario: true si el SVG dibuja los huecos al revés (p. ej. la A de Anthropic)
  const caja = new THREE.Box2(); formas.forEach((f) => f.getPoints(8).forEach((p) => caja.expandByPoint(p)));
  const s = tam / (caja.max.x - caja.min.x), fondo = (o.fondo ?? 0.14) / s * tam, bisel = (o.bisel ?? 0.035) / s * tam;   // en unidades del SVG
  const geo = new THREE.ExtrudeGeometry(formas, { depth: fondo, bevelEnabled: true, bevelSize: bisel * 0.7, bevelThickness: bisel, bevelSegments: o.segmentos ?? 5, curveSegments: 10 });
  geo.translate(-(caja.min.x + caja.max.x) / 2, -caja.min.y + bisel * 0.7, -fondo / 2); geo.scale(s, s, s); geo.computeVertexNormals();
  const m = new THREE.Mesh(geo, material); m.castShadow = true; m.receiveShadow = true; return m;
}
