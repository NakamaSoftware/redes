// motor3d.js · Motion Graphics Viegas · 3D real con three.js (objetos, materiales, luces y cámara de verdad)
// Se apoya en motor.js (tiempo, curvas, vídeos y capa 2D encima) y renderiza la escena 3D en cada window.seek(t),
// así el MP4 sale idéntico fotograma a fotograma. Uso (en escena.html, con el importmap de la plantilla):
//
//   import { escena3d } from '../motor/motor3d.js';
//   escena3d({ duracion: 6, fondo: 'marca' }, ({ THREE, MG, scene, camara, mat, obj, rig }) => {
//     const cubo = obj.cajaRedonda(2, 2, 2, mat.coral());          // objetos y materiales de marca
//     return (t) => { rig.orbita(t, { radio: 9, desde: -30, hasta: 30, altura: 2 }); cubo.rotation.y = t; };
//   });
//
// Cámara («rig»): orbita · dolly (acercar/alejar) · grua (subir/bajar mirando a un punto) · recorrido (por puntos con curva)
// · temblor (cámara en mano sutil). Todos usan las curvas de MG.curvas y nunca se paran (regla de la marca).
// Lente de cine: `profundidad: { apertura, max }` y `movimiento: { muestras, obturador }` en la configuración (lente3d.js).
// Pantalla en 3D: obj.pantalla(fuente) + planos.revelado / sobrevuelo / empuje / orbita / claves (pantalla3d.js).
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { crearLente } from './lente3d.js';
import { instalarPantallas } from './pantalla3d.js';
import { extruir, CLAUDE } from './svg3d.js';
import { crearMascota } from './mascota3d.js';

// colores de la marca: se leen de estilo.css (o del tema de motor/temas/) al crear la escena
const tok = (n, d) => { const v = getComputedStyle(document.documentElement).getPropertyValue('--' + n).trim(); const m = /^#([0-9a-f]{6})$/i.exec(v) || /^#([0-9a-f]{3})$/i.exec(v);
  if (!m) return d; const h = m[1].length === 3 ? m[1].replace(/./g, (c) => c + c) : m[1]; return parseInt(h, 16); };
const oscurece = (c, k) => (Math.round(((c >> 16) & 255) * k) << 16) | (Math.round(((c >> 8) & 255) * k) << 8) | Math.round((c & 255) * k);
let CORAL = 0xD97757, CORAL2 = 0xE78F72, OSCURO = 0x141217, TEXTO = 0xF4F2EE, FONDO = 0x0D0C0F;
const leerMarca = () => { CORAL = tok('acento', CORAL); CORAL2 = tok('acento2', CORAL2); OSCURO = tok('tarjeta2', OSCURO); TEXTO = tok('texto', TEXTO); FONDO = tok('fondo', FONDO); };

export function escena3d(cfg, crear) {
  window.escena(cfg, (MG) => {
    leerMarca();
    const W = MG.ANCHO, H = MG.ALTO;
    // lienzo 3D entre el fondo de la marca y la capa 2D (textos, píldoras): transparente para ver el fondo
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
    renderer.setPixelRatio(window.devicePixelRatio || 1); renderer.setSize(W, H);
    renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = cfg.exposicion ?? 1.05;
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    // tamaño explícito: sin él, en 4K (pixelRatio 2) el lienzo se ve al doble y solo sale su esquina de arriba a la izquierda
    renderer.domElement.style.cssText = 'position:absolute;inset:0;width:100%;height:100%'; MG.vista.insertBefore(renderer.domElement, MG.mundo);
    const scene = new THREE.Scene();
    const pmrem = new THREE.PMREMGenerator(renderer); scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    if (cfg.niebla !== false) scene.fog = new THREE.Fog(FONDO, cfg.nieblaCerca ?? 14, cfg.nieblaLejos ?? 40);
    const camara = new THREE.PerspectiveCamera(cfg.fov ?? 35, W / H, 0.1, 200); camara.position.set(0, 1.5, 10);
    // luces: clave cálida coral desde arriba-derecha, relleno frío, contra para recortar siluetas
    const clave = new THREE.DirectionalLight(0xffe7dc, 2.4); clave.position.set(5, 8, 6); clave.castShadow = true; clave.shadow.mapSize.set(2048, 2048);
    Object.assign(clave.shadow.camera, { left: -12, right: 12, top: 12, bottom: -12 }); scene.add(clave);
    const relleno = new THREE.DirectionalLight(0x9fb4ff, 0.5); relleno.position.set(-6, 3, 4); scene.add(relleno);
    const contra = new THREE.PointLight(CORAL, 40, 30); contra.position.set(0, 3, -6); scene.add(contra);
    scene.add(new THREE.AmbientLight(0xffffff, 0.15));
    // lente de cine (desenfoque de profundidad y de movimiento) si la escena lleva `profundidad` o `movimiento` (lente3d.js)
    const { lente, pintar } = crearLente(renderer, scene, camara, cfg);

    const texVideo = [];
    // ---------------- materiales de marca
    const mat = {
      coral: (o = {}) => new THREE.MeshPhysicalMaterial({ color: oscurece(CORAL, 0.86), roughness: 0.38,   // más saturado: el tone mapping ACES lo aclara hasta el coral de la marca
        metalness: 0.0, clearcoat: 0.6, clearcoatRoughness: 0.25, ...o }),
      oscuro: (o = {}) => new THREE.MeshPhysicalMaterial({ color: OSCURO, roughness: 0.5, metalness: 0.1, clearcoat: 0.3, ...o }),
      vidrio: (o = {}) => new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.08, transmission: 1, thickness: 0.6, ior: 1.4, transparent: true, ...o }),
      metal: (o = {}) => new THREE.MeshStandardMaterial({ color: 0xd9d4cc, roughness: 0.2, metalness: 1, ...o }),
      brillo: (color = CORAL, intensidad = 2) => new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: intensidad }),
      // textura de vídeo: el vídeo está en pausa y se coloca fotograma a fotograma, así que hay que refrescarla a mano en cada render
      video: (v) => { const tx = new THREE.VideoTexture(v); tx.colorSpace = THREE.SRGBColorSpace; texVideo.push(tx); return new THREE.MeshBasicMaterial({ map: tx, toneMapped: false }); },
      imagen: (url) => { const tx = new THREE.TextureLoader().load(url); tx.colorSpace = THREE.SRGBColorSpace; return new THREE.MeshBasicMaterial({ map: tx, toneMapped: false, transparent: true }); },
    };
    // ---------------- objetos
    const sombras = (m) => { m.castShadow = true; m.receiveShadow = true; return m; };
    const obj = {
      cajaRedonda: (w = 1, h = 1, d = 1, m = mat.coral(), r = 0.12) => sombras(new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 6, r), m)),
      esfera: (r = 1, m = mat.coral()) => sombras(new THREE.Mesh(new THREE.SphereGeometry(r, 64, 64), m)),
      toro: (r = 1, tubo = 0.3, m = mat.coral()) => sombras(new THREE.Mesh(new THREE.TorusGeometry(r, tubo, 48, 160), m)),
      cilindro: (r = 0.5, h = 1, m = mat.coral()) => sombras(new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, 64), m)),
      // suelo que solo recoge sombras (se ve el fondo de la marca); suelo(mat.oscuro()) para un suelo visible
      suelo: (m = new THREE.ShadowMaterial({ opacity: 0.45 })) => { const s = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), m); s.rotation.x = -Math.PI / 2; s.receiveShadow = true; return s; },
      // tarjeta 3D con un vídeo (un slide de carrusel, una pantalla): plano con esquinas redondeadas y canto
      tarjeta: (src, w = 1.6, h = 2, t0 = 0, o = {}) => {
        const v = MG.video(src, t0, o), g = new THREE.Group();
        const forma = new THREE.Shape(), r = Math.min(w, h) * 0.06, x = -w / 2, y = -h / 2;
        forma.moveTo(x + r, y); forma.lineTo(x + w - r, y); forma.quadraticCurveTo(x + w, y, x + w, y + r); forma.lineTo(x + w, y + h - r);
        forma.quadraticCurveTo(x + w, y + h, x + w - r, y + h); forma.lineTo(x + r, y + h); forma.quadraticCurveTo(x, y + h, x, y + h - r);
        forma.lineTo(x, y + r); forma.quadraticCurveTo(x, y, x + r, y);
        const geo = new THREE.ShapeGeometry(forma, 24); const uv = geo.attributes.uv; const pos = geo.attributes.position;
        for (let i = 0; i < uv.count; i++) uv.setXY(i, (pos.getX(i) - x) / w, (pos.getY(i) - y) / h);
        const cara = new THREE.Mesh(geo, mat.video(v)); cara.position.z = 0.046;   // por delante del canto (que llega a z = 0.03)
        const canto = sombras(new THREE.Mesh(new THREE.ExtrudeGeometry(forma, { depth: 0.04, bevelEnabled: true, bevelSize: 0.01, bevelThickness: 0.01, bevelSegments: 3 }), mat.oscuro()));
        canto.position.z = -0.02; g.add(canto, cara); g.video = v; return g;
      },
      // logos e iconos de verdad: el «d» de un <path> SVG extruido con bisel, de pie (base en y = 0) · svg3d.js
      svg: (d, m = mat.coral(), o = {}) => extruir(d, m, o),
      logoClaude: (o = {}) => extruir(CLAUDE, o.mat || mat.coral(), o),
      // la mascota de Claude Code como personaje 3D (anda, parpadea, saluda) · mascota3d.js
      mascotaClaude: (o = {}) => crearMascota(mat, o),
      modelo: (url) => new Promise((ok) => new GLTFLoader().load(url, (g) => { g.scene.traverse((m) => { if (m.isMesh) sombras(m); }); ok(g.scene); })),
    };
    // ---------------- cámara real: rigs con curva, que nunca se quedan quietos
    const v3 = (a) => new THREE.Vector3(...a), mira = new THREE.Vector3();
    const rig = {
      mirar: (p) => { mira.copy(Array.isArray(p) ? v3(p) : p); camara.up.set(0, 1, 0); camara.lookAt(mira); },
      // orbita alrededor de un punto: ángulo de «desde» a «hasta» (grados) a lo largo de toda la escena
      orbita: (t, o = {}) => { const x = MG.lerp(o.desde ?? -25, o.hasta ?? 25, (MG.curvas[o.curva || 'lineal'])(t / (o.dur ?? cfg.duracion))) * Math.PI / 180, R = o.radio ?? 10;
        const c = o.centro ? v3(o.centro) : new THREE.Vector3(); camara.position.set(c.x + Math.sin(x) * R, c.y + (o.altura ?? 1.5), c.z + Math.cos(x) * R); rig.mirar(c); },
      // dolly: acercar o alejar en línea recta (z) mirando al centro
      dolly: (t, o = {}) => { const p = (MG.curvas[o.curva || 'lineal'])(MG.k(t, o.t0 ?? 0, o.t1 ?? cfg.duracion));
        camara.position.set(o.x ?? 0, o.altura ?? 1.5, MG.lerp(o.desde ?? 12, o.hasta ?? 8, p)); rig.mirar(o.centro || [0, 0, 0]); },
      // grúa: sube o baja (y) mientras mira al centro
      grua: (t, o = {}) => { const p = (MG.curvas[o.curva || 'salidaQuint'])(MG.k(t, o.t0 ?? 0, o.t1 ?? cfg.duracion));
        camara.position.set(o.x ?? 0, MG.lerp(o.desde ?? 6, o.hasta ?? 1.2, p), o.z ?? 10); rig.mirar(o.centro || [0, 0, 0]); },
      // recorrido por puntos (curva Catmull-Rom) con su propia curva de velocidad; «mirarA» puede ser fijo o seguir otra curva
      recorrido: (t, puntos, o = {}) => { const c = new THREE.CatmullRomCurve3(puntos.map(v3)); const p = (MG.curvas[o.curva || 'entradaSalidaQuint'])(MG.k(t, o.t0 ?? 0, o.t1 ?? cfg.duracion));
        camara.position.copy(c.getPoint(p)); rig.mirar(o.mirarA || [0, 0, 0]); },
      // cámara en mano sutil (determinista: senos, no aleatorio)
      temblor: (t, f = 0.04) => { camara.position.x += Math.sin(t * 1.7) * f; camara.position.y += Math.sin(t * 2.3 + 1) * f * 0.7; camara.rotation.z += Math.sin(t * 1.1) * f * 0.05; },
    };
    // entrada con rebote de un objeto 3D (escala + subida), escalonable
    const entra3d = (o3, t, t0, o = {}) => { const p = (MG.curvas[o.curva || 'rebote'])(MG.k(t, t0, t0 + (o.d ?? 1.0)));
      const s = Math.max(0.0001, p) * (o.escala ?? 1); o3.scale.setScalar(s); o3.position.y = (o.y ?? 0) + (1 - Math.min(1, p)) * (o.subida ?? -1.2); o3.visible = p > 0.001; return p; };

    const ctx = { THREE, MG, cfg, scene, camara, renderer, mat, obj, rig, entra3d, lente, luces: { clave, relleno, contra } };
    // pantalla en 3D: una interfaz real como objeto (obj.pantalla) y planos de cámara para interfaces (planos.*) · pantalla3d.js
    const { pantalla, planos } = instalarPantallas(ctx); obj.pantalla = pantalla; ctx.planos = planos;
    const pinta = crear(ctx) || (() => {});
    MG.despues((t) => pintar(t, pinta, () => { for (const tx of texVideo) tx.needsUpdate = true; }));
    return (t) => { pinta(t); };
  });
}
export { THREE };
