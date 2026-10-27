// piezas3d.js · Motion Graphics Viegas · pack «3D con three.js» (las escenas 3d-*.html de ejemplos/escenas/)
// Ayudas comunes encima de motor3d.js: parámetros editables, formato 9:16 / 16:9 por la dirección, fondo transparente,
// el coral de Claude fijo, logos reales como textura, placas con imagen o vídeo, texto 3D extruido y encuadre automático.
//
//   <script id="params" type="application/json">{ "formato": "9x16", "titular": "…", "acento": "#D97757" }</script>
//   import { pieza3d } from '../motor/piezas3d.js';
//   pieza3d({ duracion: 6 }, ({ P, W, H, VERT, scene, mat, coral, encuadre, ... }) => (t) => { ... });
//
// Parámetros: bloque `params` de la escena · o en la dirección: `?titular=Hola&acento=%23D97757` · formato con `#16x9`
// (por defecto `#9x16`) · fondo transparente con `?fondo=transparente` (y render con --transparente → ProRes 4444 con alfa).
// El logo de Claude y la mascota van SIEMPRE en coral #D97757, aunque el tema cambie el acento.
import * as THREE from 'three';
import { escena3d } from './motor3d.js';
import { TTFLoader } from 'three/addons/loaders/TTFLoader.js';
import { Font } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

export const CORAL_CLAUDE = 0xD97757;
const BASE = new URL('./', import.meta.url).href;            // carpeta motor/ (logos, fuentes)

// ---------------- parámetros
const bloque = document.getElementById('params');
export const P = Object.assign(bloque ? JSON.parse(bloque.textContent) : {}, window.PARAMS || {});
const q = new URLSearchParams(location.search);
for (const [k, v] of q) {
  if (k === 'ver') continue;
  const d = P[k];
  if (typeof d === 'number') P[k] = parseFloat(v);
  else if (typeof d === 'boolean') P[k] = v !== 'false' && v !== '0';
  else if (Array.isArray(d) || (d && typeof d === 'object')) { try { P[k] = JSON.parse(v); } catch { P[k] = v.split(','); } }
  else P[k] = v;
}
export const FMT = (location.hash.match(/(16x9|9x16|1x1|4x5)/) || [0, P.formato || '9x16'])[1];
export const [W, H] = ({ '16x9': [1920, 1080], '9x16': [1080, 1920], '1x1': [1080, 1080], '4x5': [1080, 1350] })[FMT];
export const VERT = H > W, U = Math.min(W, H) / 1080;
export const TRANSPARENTE = P.fondo === 'transparente';
const hex = (c, d) => { if (typeof c === 'number') return c; const m = /^#?([0-9a-f]{6})$/i.exec(String(c || '').trim()); return m ? parseInt(m[1], 16) : d; };
const oscurece = (c, k) => (Math.round(((c >> 16) & 255) * k) << 16) | (Math.round(((c >> 8) & 255) * k) << 8) | Math.round((c & 255) * k);

// logos reales (svgl, colores oficiales): claude, claude-code, youtube, instagram, tiktok, gmail · o la ruta a tu SVG/PNG
export const LOGOS = { claude: 'logos/claude.svg', 'claude-code': 'logos/claude-code.svg', youtube: 'logos/youtube.svg', instagram: 'logos/instagram.svg', tiktok: 'logos/tiktok.svg', gmail: 'logos/gmail.svg' };
const rutaLogo = (n) => (LOGOS[n] ? BASE + LOGOS[n] : new URL(n, location.href).href);

let fuentePromesa = null;
export function fuente(url = BASE + 'fuentes/InterTight-700.ttf') {
  if (!fuentePromesa) fuentePromesa = new Promise((ok, ko) => new TTFLoader().load(url, (j) => ok(new Font(j)), undefined, ko));
  return fuentePromesa;
}

export function pieza3d(cfg, crear) {
  const dur = P.duracion ?? cfg.duracion ?? 6;
  escena3d({ ...cfg, duracion: dur, ancho: W, alto: H, fondo: TRANSPARENTE ? 'transparente' : (cfg.fondo || 'marca') }, (ctx) => {
    const { MG, renderer, camara, mat } = ctx;
    renderer.localClippingEnabled = true;
    renderer.shadowMap.type = THREE.VSMShadowMap;                // sombras suaves de verdad (nada de bordes «cuadriculados»)
    ctx.luces.clave.shadow.radius = 10; ctx.luces.clave.shadow.blurSamples = 16; ctx.luces.clave.shadow.bias = -0.0004;
    MG._listos = MG._listos || [];
    const espera = (p) => { MG._listos.push(p.catch((e) => console.error(e))); return p; };
    const ACENTO = hex(P.acento, CORAL_CLAUDE);
    // el coral de Claude (fijo) y el acento editable; más saturados porque el tone mapping ACES los aclara
    const coral = (o = {}) => new THREE.MeshPhysicalMaterial({ color: oscurece(CORAL_CLAUDE, 0.8), roughness: 0.4, metalness: 0, clearcoat: 0.35, clearcoatRoughness: 0.5, envMapIntensity: 0.6, ...o });
    const acento = (o = {}) => new THREE.MeshPhysicalMaterial({ color: oscurece(ACENTO, 0.8), roughness: 0.4, clearcoat: 0.35, clearcoatRoughness: 0.5, envMapIntensity: 0.6, ...o });
    const brilloAcento = (k = 2) => new THREE.MeshStandardMaterial({ color: ACENTO, emissive: ACENTO, emissiveIntensity: k });

    // distancia de cámara para que una caja de ancho × alto (unidades) quepa con margen en este formato
    const encuadre = (ancho, alto, margen = 1.12) => {
      const tv = Math.tan((camara.fov * Math.PI) / 360);
      return Math.max(alto / (2 * tv), ancho / (2 * tv * camara.aspect)) * margen;
    };

    // ---- texturas
    const lienzo = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
    const texDe = (c) => { const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = renderer.capabilities.getMaxAnisotropy(); return tx; };
    // logo real → textura (cuadrada, con margen y fondo opcional)
    const texLogo = (nombre, o = {}) => {
      const s = o.tam || 1024, c = lienzo(s, s), tx = texDe(c);
      espera(new Promise((ok) => { const im = new Image(); im.onload = () => {
        const g = c.getContext('2d'), m = s * (o.margen ?? 0.2), a = im.naturalWidth || 1, b = im.naturalHeight || 1, k = Math.min((s - 2 * m) / a, (s - 2 * m) / b);
        if (o.fondo) { g.fillStyle = o.fondo; g.fillRect(0, 0, s, s); }
        g.drawImage(im, (s - a * k) / 2, (s - b * k) / 2, a * k, b * k); tx.needsUpdate = true; ok(); };
        im.onerror = () => { console.error('No carga el logo', nombre); ok(); }; im.src = rutaLogo(nombre); }));
      return tx;
    };
    // textura dibujada con canvas (cuando las fuentes ya están cargadas): dibuja(g, w, h)
    const texDibujo = (w, h, dibuja) => {
      const c = lienzo(w, h), tx = texDe(c);
      espera(document.fonts.ready.then(() => Promise.all(['600 40px "Inter Tight"', '400 40px "Geist Mono"', 'italic 400 40px "Instrument Serif"'].map((f) => document.fonts.load(f).catch(() => {}))))
        .then(() => { dibuja(c.getContext('2d'), w, h); tx.needsUpdate = true; }));
      return tx;
    };
    // forma de rectángulo redondeado (centrada)
    const rect = (w, h, r) => { const s = new THREE.Shape(), x = -w / 2, y = -h / 2;
      s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + h - r);
      s.quadraticCurveTo(x + w, y + h, x + w - r, y + h); s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
      s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y); return s; };
    // placa: tarjeta con esquinas redondeadas, canto con bisel y una textura (imagen, dibujo o vídeo) en la cara
    const placa = (tex, w, h, o = {}) => {
      const g = new THREE.Group(), r = o.radio ?? Math.min(w, h) * 0.07, forma = rect(w, h, r), grosor = o.grosor ?? 0.06;
      const geo = new THREE.ShapeGeometry(forma, 24), uv = geo.attributes.uv, pos = geo.attributes.position;
      for (let i = 0; i < uv.count; i++) uv.setXY(i, (pos.getX(i) + w / 2) / w, (pos.getY(i) + h / 2) / h);
      const cara = new THREE.Mesh(geo, o.material || new THREE.MeshBasicMaterial({ map: tex, toneMapped: false, transparent: true }));
      cara.position.z = grosor / 2 + 0.012;
      const canto = new THREE.Mesh(new THREE.ExtrudeGeometry(forma, { depth: grosor, bevelEnabled: true, bevelSize: 0.012, bevelThickness: 0.012, bevelSegments: 3, curveSegments: 16 }), o.canto || mat.oscuro({ roughness: 0.35, metalness: 0.4 }));
      canto.position.z = -grosor / 2; canto.castShadow = canto.receiveShadow = true;
      g.add(canto, cara); g.cara = cara; g.canto = canto; return g;
    };
    // vídeo como textura (se coloca fotograma a fotograma, como las tarjetas del motor)
    const texVideo = (src, t0 = 0, o = {}) => { const v = MG.video(src, t0, o); const m = mat.video(v); return m.map; };

    // ---- texto 3D extruido, por letras (cada letra es un objeto: se puede animar por separado)
    // texto3d(texto, { tam, fondo, bisel, mats: [materialNormal, materialClave], clave: ['palabra'], interlinea }) → Promise<Group>
    // grupo.letras = [{ m, linea, i, clave }] centrado en x, la base de la última línea en y = 0
    const texto3d = (txt, o = {}) => espera(fuente(o.fuente).then((f) => {
      const tam = o.tam ?? 1, gr = new THREE.Group(), lineas = String(txt).split(/\n|\\n|\|/), esc = tam / f.data.resolution, letras = [];
      const claves = (o.clave || []).map((x) => x.toLowerCase());
      lineas.forEach((ln, li) => {
        const pal = ln.split(' '); let x = 0; const fila = [];
        pal.forEach((p, pi) => {
          const esClave = claves.some((c) => c.split(' ').includes(p.toLowerCase().replace(/[.,!?¡¿]/g, '')));
          for (const ch of p) {
            const gl = f.data.glyphs[ch] || f.data.glyphs['?']; const adv = gl.ha * esc;
            if (ch.trim()) {
              const geo = new TextGeometry(ch, { font: f, size: tam, depth: o.fondo ?? tam * 0.28, curveSegments: 10, bevelEnabled: true, bevelThickness: o.bisel ?? tam * 0.035, bevelSize: (o.bisel ?? tam * 0.035) * 0.7, bevelSegments: 5 });
              geo.computeBoundingBox(); const bb = geo.boundingBox, cx = (bb.min.x + bb.max.x) / 2;
              geo.translate(-cx, 0, -(o.fondo ?? tam * 0.28) / 2);   // pivote en el centro de la letra (gira bien)
              const m = new THREE.Mesh(geo, (o.mats || [])[esClave ? 1 : 0] || coral()); m.castShadow = m.receiveShadow = true;
              m.userData.x = x + cx; fila.push(m); letras.push({ m, linea: li, i: letras.length, clave: esClave });
              gr.add(m);
            }
            x += adv;
          }
          if (pi < pal.length - 1) x += (f.data.glyphs[' ']?.ha ?? f.data.resolution * 0.25) * esc;
        });
        const y = (lineas.length - 1 - li) * tam * (o.interlinea ?? 1.18);
        fila.forEach((m) => { m.position.set(m.userData.x - x / 2, y, 0); m.userData.base = m.position.clone(); });
      });
      gr.letras = letras; gr.ancho = Math.max(...letras.map((l) => Math.abs(l.m.position.x))) * 2 + tam; gr.alto = lineas.length * tam * (o.interlinea ?? 1.18);
      return gr;
    }));

    // bokeh: puntos de luz lejos del foco; con `profundidad` en la configuración salen como círculos suaves de lente
    const bokeh = (n = 24, o = {}) => {
      const g = new THREE.Group(); let s = o.semilla ?? 7; const az = () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
      const cols = o.colores || [0x60A5FA, 0x93C5FD, CORAL_CLAUDE];
      for (let i = 0; i < n; i++) {
        const c = cols[i % cols.length], m = new THREE.Mesh(new THREE.SphereGeometry((o.tam ?? 0.06) * (0.6 + az()), 16, 12), new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: 0.55 + az() * 0.45, toneMapped: false, fog: false }));
        const a = az() * Math.PI * 2, r = (o.radio ?? 6) * (0.45 + az() * 0.55);
        m.position.set(Math.cos(a) * r, (az() - 0.5) * (o.alto ?? 8), (o.z ?? -6) + (az() - 0.5) * (o.fondo ?? 8)); m.userData.f = az() * 6; m.userData.y0 = m.position.y; g.add(m);
      }
      g.flota = (t) => g.children.forEach((m) => { m.position.y = m.userData.y0 + Math.sin(t * 0.7 + m.userData.f) * 0.25; });   // determinista: solo depende de t
      return g;
    };

    return crear({ ...ctx, P, W, H, VERT, U, FMT, TRANSPARENTE, ACENTO, espera, coral, acento, brilloAcento, encuadre, texLogo, texDibujo, texVideo, placa, rect, texto3d, bokeh });
  });
}
export { THREE };
