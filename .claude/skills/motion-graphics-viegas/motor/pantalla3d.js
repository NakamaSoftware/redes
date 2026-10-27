// pantalla3d.js · Motion Graphics Viegas · «pantalla en 3D»
// Una interfaz de verdad (una escena HTML animada, una web, una captura o una grabación de pantalla) convertida en un objeto
// 3D: una losa con canto, esquinas redondeadas y sombra, que la cámara sobrevuela con enfoque de cine. Partes de la interfaz
// pueden salir hacia la cámara (recortes) y la cámara se mueve con planos pensados para interfaces.
// Lo instala escena3d: ctx.obj.pantalla(...) y ctx.planos.*  (detalle y ejemplos en referencias/pantalla-3d.md)
//
//   const ui = obj.pantalla('../pantallas/mi-panel', { ancho: 8 });        // carpeta de `render.mjs pantalla`, .mp4/.webm o .png/.jpg
//   ui.rotation.x = -1.3; scene.add(ui);
//   const chat = ui.recorte(1520, 56, 400, 600);                            // en px de la interfaz
//   return (t) => { planos.revelado(t, ui); chat.levantar(t, 3.5, { altura: 0.5 }); };
import * as THREE from 'three';

const EXT_VIDEO = ['mp4', 'webm', 'mov', 'm4v'], EXT_IMAGEN = ['png', 'jpg', 'jpeg', 'webp', 'avif', 'gif'];
const ext = (s) => ((s.split('?')[0].match(/\.([a-z0-9]+)$/i) || [])[1] || '').toLowerCase();
const carga = (src) => new Promise((ok, mal) => { const im = new Image(); im.onload = () => im.decode().then(() => ok(im), () => ok(im)); im.onerror = () => mal(new Error('No se pudo cargar ' + src)); im.src = src; });
const rad = (g) => (g * Math.PI) / 180;

// rectángulo con esquinas redondeadas, centrado en el origen
function forma(w, h, r) {
  const s = new THREE.Shape(), x = -w / 2, y = -h / 2; r = Math.min(r, w / 2, h / 2);
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + h - r);
  s.quadraticCurveTo(x + w, y + h, x + w - r, y + h); s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y); return s;
}
// cara plana con las UV de una ventana de la textura [u0, v0, u1, v1]
function cara(w, h, r, [u0, v0, u1, v1] = [0, 0, 1, 1]) {
  const g = new THREE.ShapeGeometry(forma(w, h, r), 24), uv = g.attributes.uv, pos = g.attributes.position;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, u0 + ((pos.getX(i) + w / 2) / w) * (u1 - u0), v0 + ((pos.getY(i) + h / 2) / h) * (v1 - v0));
  return g;
}
// sombra suave (textura de lienzo): un rectángulo redondeado muy desenfocado, para debajo de lo que se levanta
let texSombra = null;
function sombraSuave() {
  if (texSombra) return texSombra;
  const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');   // alphaMap lee el verde: blanco = sombra
  g.fillStyle = '#000'; g.fillRect(0, 0, 256, 256);
  g.filter = 'blur(22px)'; g.fillStyle = '#fff'; g.beginPath(); g.roundRect(48, 48, 160, 160, 18); g.fill();
  texSombra = new THREE.CanvasTexture(c); return texSombra;
}

export function instalarPantallas(ctx) {
  const { MG, renderer, camara, mat, lente, cfg } = ctx;
  const ANISO = renderer.capabilities.getMaxAnisotropy();
  const esperar = (p) => { (MG._listos ||= []).push(p.catch((e) => console.error(e.message))); return p; };
  const nitida = (tx) => { tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = ANISO; tx.minFilter = THREE.LinearMipmapLinearFilter;
    tx.magFilter = THREE.LinearFilter; tx.generateMipmaps = true; tx.needsUpdate = true; return tx; };

  // ---------------------------------------------------------------- la pantalla
  // o: ancho (unidades 3D, 6) · grosor (0,018 × ancho) · radio (px de la interfaz, 18) · marco (px de borde oscuro, 0)
  //    t0 / desde / bucle (cuándo empieza la interfaz y desde qué segundo suyo) · cuerpo (material del canto)
  //    brillo (0–1, 1) · desplaza { t0, t1, desde: 0, hasta: 1, curva } para una captura de página entera (web larga)
  //    aspecto (ancho/alto de la ventana visible, si la captura es más alta que la pantalla)
  function pantalla(fuente, o = {}) {
    const g = new THREE.Group(), W = o.ancho ?? 6, pend = [];
    g.ui = { ancho: 1920, alto: 1080 }; g.ancho = W; g.alto = W * 9 / 16; g.listo = false;
    let tex = null, cuadros = null, base = '', actual = -1, vid = null, ventana = 1, zCara = 0;

    const montar = () => {
      const r0 = o.radio ?? 18, k = W / g.ui.ancho, marco = (o.marco ?? 0) * k, grosor = o.grosor ?? W * 0.018, bisel = grosor * 0.3;
      g.alto = (W * g.ui.alto) / g.ui.ancho; g.escala = k;
      const cuerpo = new THREE.Mesh(new THREE.ExtrudeGeometry(forma(W + 2 * marco, g.alto + 2 * marco, r0 * k + marco),
        { depth: grosor, bevelEnabled: true, bevelSize: bisel, bevelThickness: bisel, bevelSegments: 4, curveSegments: 16 }),
        o.cuerpo || new THREE.MeshPhysicalMaterial({ color: 0x0E0D11, roughness: 0.55, metalness: 0.2, clearcoat: 0.15, clearcoatRoughness: 0.5, envMapIntensity: 0.35 }));
      cuerpo.position.z = -(grosor + bisel); cuerpo.castShadow = cuerpo.receiveShadow = true;
      zCara = W * 0.0008;
      const m = new THREE.MeshBasicMaterial({ map: tex, toneMapped: false, color: new THREE.Color(o.brillo ?? 1, o.brillo ?? 1, o.brillo ?? 1) });
      const c = new THREE.Mesh(cara(W, g.alto, r0 * k), m); c.position.z = zCara;
      g.add(cuerpo, c); g.cuerpo = cuerpo; g.cara = c; g.listo = true; pend.forEach((f) => f());
    };

    esperar((async () => {
      const e = ext(fuente);
      if (EXT_VIDEO.includes(e)) {                         // grabación de pantalla (p. ej. de extractos-pantalla)
        vid = MG.video(fuente, o.t0 ?? 0, { desde: o.desde ?? 0, bucle: o.bucle ?? false });
        await new Promise((ok) => (vid.readyState >= 1 ? ok() : vid.addEventListener('loadedmetadata', ok, { once: true })));
        g.ui = { ancho: o.ui?.[0] ?? vid.videoWidth, alto: o.ui?.[1] ?? vid.videoHeight };
        tex = nitida(new THREE.VideoTexture(vid));
      } else {
        let img, info = null;
        if (EXT_IMAGEN.includes(e)) img = await carga(fuente);
        else {                                             // carpeta hecha con `render.mjs pantalla`
          base = fuente.replace(/\/$/, ''); info = await (await fetch(base + '/info.json')).json();
          img = await carga(info.tipo === 'imagen' ? `${base}/${info.archivo}` : `${base}/${nombre(info, 0)}`);
          if (info.tipo !== 'imagen') { cuadros = info; actual = 0; }
        }
        const esc = info?.escala ?? o.escala ?? 1;
        g.ui = { ancho: o.ui?.[0] ?? (info?.ancho ?? img.naturalWidth / esc), alto: o.ui?.[1] ?? (info?.alto ?? img.naturalHeight / esc) };
        tex = nitida(new THREE.Texture(img));
        if (o.aspecto && g.ui.ancho / o.aspecto < g.ui.alto) {   // página más alta que la pantalla: se ve una ventana y se desplaza
          g.ui.pagina = g.ui.alto; g.ui.alto = g.ui.ancho / o.aspecto; ventana = g.ui.alto / g.ui.pagina;
          tex.repeat.set(1, ventana); tex.offset.set(0, 1 - ventana);
        }
      }
      montar();
    })());

    const nombre = (info, i) => `f${String(i).padStart(6, '0')}.${info.ext}`;
    const cuadro = (t) => {
      const x = (t - (o.t0 ?? 0) + (o.desde ?? 0)) * cuadros.fps, n = cuadros.n;
      const i = Math.floor(x + 1e-4); return (o.bucle ? ((i % n) + n) % n : Math.min(n - 1, Math.max(0, i)));
    };
    // antes de pintar el 3D: la interfaz en su fotograma exacto
    MG.despues(async (t) => {
      if (!tex) return;
      if (cuadros) { const i = cuadro(t); if (i !== actual) { tex.image = await carga(`${base}/${nombre(cuadros, i)}`); tex.needsUpdate = true; actual = i; } }
      else if (vid) tex.needsUpdate = true;
      if (o.desplaza && ventana < 1) { const d = o.desplaza, p = (MG.curvas[d.curva || 'afterEffects'])(MG.k(t, d.t0 ?? 0, d.t1 ?? cfg.duracion));
        tex.offset.y = (1 - ventana) * (1 - MG.lerp(d.desde ?? 0, d.hasta ?? 1, p)); }
    });

    // un punto de la interfaz (px, como en el HTML) en coordenadas 3D: para enfocar, apuntar la cámara o colocar cosas encima
    const local = (x, y, z = 0) => new THREE.Vector3((x / g.ui.ancho - 0.5) * W, (0.5 - y / g.ui.alto) * g.alto, z);
    g.local = local;
    g.punto = (x, y, z = 0) => { g.updateMatrixWorld(true); return g.localToWorld(local(x, y, z)); };

    // sombra suave sobre la interfaz (la cara de la pantalla no recibe sombras reales): para lo que se mueve por encima
    // const s = ui.sombra(120); s.poner(x, y, { altura, opacidad }) · más alto = más grande y más clara
    g.sombra = (tamPx = 120) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ color: 0, alphaMap: sombraSuave(), transparent: true, opacity: 0, depthWrite: false, toneMapped: false }));
      m.renderOrder = 3; const pon = () => { if (!m.parent && g.listo) g.add(m); };
      m.poner = (x, y, o4 = {}) => { pon(); const a = o4.altura ?? 0, k = g.escala ?? W / g.ui.ancho, tam = tamPx * k * 1.6 * (1 + a * 0.9);
        const c = local(x, y, zCara + W * 0.00035); m.position.copy(c); m.scale.set(tam, tam * (o4.alargada ?? 0.7), 1);
        m.material.opacity = (o4.opacidad ?? 0.7) / (1 + a * 2.5); return m; };
      return m;
    };
    // recorte: un trozo de la interfaz (x, y, ancho, alto en px) que se levanta hacia la cámara como una tarjeta
    // o: radio (px, 14) · grosor (unidades) · sombra (true)
    g.recorte = (x, y, w, h, o2 = {}) => {
      const rc = new THREE.Group(); rc.visible = false; let sombra = null, hueco = null, z0 = 0;
      const crear = () => {
        const k = g.escala, ww = w * k, hh = h * k, r = (o2.radio ?? 14) * k, gro = o2.grosor ?? W * 0.008;
        const uv = [x / g.ui.ancho, 1 - (y + h) / g.ui.alto, (x + w) / g.ui.ancho, 1 - y / g.ui.alto];
        const c = new THREE.Mesh(cara(ww, hh, r, uv), g.cara.material); c.position.z = 0.0006 * W;
        const cuerpo = new THREE.Mesh(new THREE.ExtrudeGeometry(forma(ww, hh, r), { depth: gro, bevelEnabled: true, bevelSize: gro * 0.3, bevelThickness: gro * 0.3, bevelSegments: 3 }), g.cuerpo.material);
        cuerpo.position.z = -gro - gro * 0.3; cuerpo.castShadow = true;
        rc.add(cuerpo, c);
        const cen = local(x + w / 2, y + h / 2); z0 = zCara + gro * 1.6 + W * 0.0004; rc.position.set(cen.x, cen.y, z0);
        if (o2.hueco !== false) {                          // el sitio vacío que deja (o2.hueco: color, por defecto el fondo #0B0A0D)
          hueco = new THREE.Mesh(cara(ww, hh, r), new THREE.MeshBasicMaterial({ color: o2.hueco ?? 0x0B0A0D, transparent: true, opacity: 0, depthWrite: false, toneMapped: false }));
          hueco.position.set(cen.x, cen.y, zCara + W * 0.0002); hueco.renderOrder = 1; g.add(hueco);
        }
        if (o2.sombra !== false) {
          sombra = new THREE.Mesh(new THREE.PlaneGeometry(ww * 1.6, hh * 1.6), new THREE.MeshBasicMaterial({ color: 0, alphaMap: sombraSuave(), transparent: true, opacity: 0, depthWrite: false, toneMapped: false }));
          sombra.position.set(cen.x, cen.y, zCara + W * 0.0003); sombra.renderOrder = 2; g.add(sombra);
        }
        g.add(rc);
      };
      g.listo ? crear() : pend.push(crear);
      // levantar(t, t0, { altura (unidades, 0,06 × ancho), d (s), curva ('rebote'), escala (1,04), inclina (°), vuelta (s, opcional) })
      rc.levantar = (t, t0, o3 = {}) => {
        const cv = MG.curvas[o3.curva || 'rebote'], d = o3.d ?? 0.9, P = (a) => cv(MG.k(t, a, a + d * (String(o3.curva || 'rebote').startsWith('rebote') ? 1.5 : 1)));
        const p = P(t0) - (o3.vuelta != null ? P(o3.vuelta) : 0);
        rc.position.z = z0 + p * (o3.altura ?? W * 0.06); rc.scale.setScalar(1 + p * ((o3.escala ?? 1.04) - 1)); rc.rotation.x = rad(o3.inclina ?? 0) * p;
        rc.visible = p > 0.001;
        const q = Math.min(1, Math.max(0, p));
        if (hueco) hueco.material.opacity = 0.94 * q;
        if (sombra) { sombra.material.opacity = 0.75 * q; sombra.scale.setScalar(1 + 0.25 * q); }
        return p;
      };
      return rc;
    };
    return g;
  }

  // ---------------------------------------------------------------- planos de cámara para interfaces
  // Un «brazo» de cámara que apunta a un punto de la pantalla:
  //   objetivo [x, y] (px de la interfaz) · inclinacion (°: 90 = de frente, 8–15 = rasante) · giro (°: 0 = desde el borde
  //   de abajo, + hacia la derecha) · distancia (en anchos de pantalla) · balanceo (°, cámara ladeada) · enfoque [x, y] (px; si
  //   no, el objetivo; [x, y, z] para enfocar algo levantado z unidades). Con `claves` la cámara pasa por varios brazos sin pararse (curva suave con velocidad continua).
  const V = { mundo: new THREE.Vector3(0, 1, 0), a: new THREE.Vector3(), b: new THREE.Vector3(), c: new THREE.Vector3() };
  const perp = (v, d) => v.sub(d.clone().multiplyScalar(v.dot(d)));
  function brazo(p, s) {
    const [ox, oy] = s.objetivo ?? [p.ui.ancho / 2, p.ui.alto / 2], e = rad(s.inclinacion ?? 40), a = rad(s.giro ?? 0), R = (s.distancia ?? 0.8) * p.ancho;
    const tl = p.local(ox, oy), dl = new THREE.Vector3(Math.sin(a) * Math.cos(e), -Math.cos(a) * Math.cos(e), Math.sin(e));
    p.updateMatrixWorld(true);
    const pos = p.localToWorld(tl.clone().add(dl.multiplyScalar(R))), obj = p.localToWorld(tl.clone());
    const arribaUI = p.localToWorld(tl.clone().add(new THREE.Vector3(0, 1, 0))).sub(obj).normalize();
    const vista = obj.clone().sub(pos).normalize();
    // «arriba» de la cámara: el del mundo; si se mira casi en vertical, el de la interfaz (sin saltos entre uno y otro)
    const w = THREE.MathUtils.smoothstep(Math.abs(vista.dot(V.mundo)), 0.8, 0.98);
    const up = perp(V.mundo.clone(), vista).multiplyScalar(1 - w).add(perp(arribaUI.clone(), vista).multiplyScalar(w));
    camara.position.copy(pos); camara.up.copy(up.lengthSq() > 1e-8 ? up.normalize() : arribaUI); camara.lookAt(obj);
    if (s.balanceo) camara.rotateZ(rad(s.balanceo));
    camara.updateMatrixWorld();
    if (s.enfoca !== false) lente.enfocar(s.enfoque ? p.punto(s.enfoque[0], s.enfoque[1], s.enfoque[2] ?? 0) : obj);
    return { posicion: pos, objetivo: obj };
  }
  // claves: [{ t, objetivo, inclinacion, giro, distancia, balanceo, enfoque }, …] · interpolación de Hermite con
  // pendientes por tiempo (Catmull-Rom): la cámara pasa por cada clave sin frenar; solo se para si tú lo pides.
  const CAMPOS = [['objetivo', 0], ['objetivo', 1], ['inclinacion'], ['giro'], ['distancia'], ['balanceo'], ['enfoque', 0], ['enfoque', 1], ['enfoque', 2]];
  function claves(t, p, lista, o = {}) {
    const def = { objetivo: [p.ui.ancho / 2, p.ui.alto / 2], inclinacion: 40, giro: 0, distancia: 0.8, balanceo: 0 };
    const ks = lista.map((k) => { const c = { ...def, ...k }; const f = k.enfoque ?? c.objetivo; c.enfoque = [f[0], f[1], f[2] ?? 0]; return c; }).sort((x, y) => x.t - y.t);
    const val = (k, [n, i]) => (i === undefined ? k[n] : k[n][i]);
    if (o.curva) { const a = ks[0].t, b = ks[ks.length - 1].t; t = a + (MG.curvas[o.curva])(MG.k(t, a, b)) * (b - a); }
    let i = 0; while (i < ks.length - 2 && t > ks[i + 1].t) i++;
    const k0 = ks[i], k1 = ks[Math.min(i + 1, ks.length - 1)], dt = Math.max(1e-6, k1.t - k0.t), u = Math.min(1, Math.max(0, (t - k0.t) / dt));
    const pend = (j, c) => { const a = ks[Math.max(0, j - 1)], b = ks[Math.min(ks.length - 1, j + 1)]; return (val(b, c) - val(a, c)) / Math.max(1e-6, b.t - a.t); };
    const h00 = 2 * u ** 3 - 3 * u ** 2 + 1, h10 = u ** 3 - 2 * u ** 2 + u, h01 = -2 * u ** 3 + 3 * u ** 2, h11 = u ** 3 - u ** 2;
    const s = { objetivo: [0, 0], enfoque: [0, 0, 0] };
    for (const c of CAMPOS) {
      const v = ks.length < 2 ? val(k0, c) : h00 * val(k0, c) + h10 * dt * pend(i, c) + h01 * val(k1, c) + h11 * dt * pend(i + 1, c);
      if (c[1] === undefined) s[c[0]] = v; else s[c[0]][c[1]] = v;
    }
    if (o.enfoca === false) s.enfoca = false;
    return brazo(p, s);
  }
  // planos hechos (de t0 a t1; por defecto, toda la escena). Todos aceptan los mismos campos que las claves para cambiarlos.
  const tramo = (o) => [o.t0 ?? 0, o.t1 ?? cfg.duracion];
  const planos = {
    brazo, claves,
    // de rasante (casi pegada a la interfaz) a casi de frente, alejándose: «presenta» la interfaz entera
    revelado: (t, p, o = {}) => { const [a, b] = tramo(o), W = p.ui.ancho, H = p.ui.alto;
      return claves(t, p, [{ t: a, objetivo: [W * 0.42, H * 0.72], inclinacion: 7, giro: -26, distancia: 0.34, ...o.desde },
        { t: b, objetivo: [W * 0.5, H * 0.5], inclinacion: 58, giro: 0, distancia: 1.05, ...o.hasta }], o); },
    // vuelo bajo de lado a lado sobre la interfaz, con el foco recorriéndola
    sobrevuelo: (t, p, o = {}) => { const [a, b] = tramo(o), W = p.ui.ancho, H = p.ui.alto;
      return claves(t, p, [{ t: a, objetivo: [W * 0.2, H * 0.62], inclinacion: 13, giro: -32, distancia: 0.42, ...o.desde },
        { t: (a + b) / 2, objetivo: [W * 0.5, H * 0.56], inclinacion: 16, giro: -6, distancia: 0.46 },
        { t: b, objetivo: [W * 0.8, H * 0.5], inclinacion: 20, giro: 20, distancia: 0.5, ...o.hasta }], o); },
    // empuje a un detalle (o.objetivo [x, y]): de lejos y en ángulo a cerca y casi de frente
    empuje: (t, p, o = {}) => { const [a, b] = tramo(o), W = p.ui.ancho, H = p.ui.alto, obj = o.objetivo ?? [W / 2, H / 2];
      return claves(t, p, [{ t: a, objetivo: [W / 2, H / 2], inclinacion: 52, giro: -10, distancia: 1.0, ...o.desde },
        { t: b, objetivo: obj, inclinacion: 78, giro: 0, distancia: 0.34, ...o.hasta }], o); },
    // órbita lenta alrededor de la interfaz (o de un punto suyo)
    orbita: (t, p, o = {}) => { const [a, b] = tramo(o), c = o.objetivo ?? [p.ui.ancho / 2, p.ui.alto / 2];
      return claves(t, p, [{ t: a, objetivo: c, inclinacion: 32, giro: -40, distancia: 0.95, ...o.desde },
        { t: b, objetivo: c, inclinacion: 38, giro: 40, distancia: 0.9, ...o.hasta }], o); },
  };
  return { pantalla, planos };
}
