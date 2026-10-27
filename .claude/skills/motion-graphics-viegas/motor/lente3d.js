// lente3d.js · Motion Graphics Viegas · la «lente de cine» del 3D
// Desenfoque de profundidad (enfoque real, con bokeh redondo) y desenfoque de movimiento (obturador: varios subfotogramas
// por fotograma, promediados). escena3d la activa cuando la escena lleva `profundidad` o `movimiento` en la configuración;
// si no lleva ninguno, el 3D se pinta directo como siempre (las escenas de antes salen idénticas).
//
//   escena3d({ duracion: 8, profundidad: { apertura: 14, max: 22 }, movimiento: { muestras: 8, obturador: 0.5 } }, ({ lente }) => {
//     return (t) => { ...colocar la cámara...; lente.enfocar(punto); };     // o lente.foco = 7.5 (distancia a la cámara)
//   });
//
// apertura: px de desenfoque (a 1080p) de lo que está muy lejos del foco · max: tope en px (a 1080p) · foco: distancia (unidades
// de la escena) a la que está lo nítido · muestras: subfotogramas por fotograma · obturador: 0,5 = 180° (lo de cine).
// En la vista previa con ?ver no hay subfotogramas (va en tiempo real); el render sí los hace.
import * as THREE from 'three';

const VERT = 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }';

// desenfoque en un solo paso (espiral áurea, idea de Dennis Gustafsson): cada muestra suma si su círculo de desenfoque
// llega hasta este píxel; lo que está detrás no se «come» lo que está delante. Se mezcla en luz lineal (premultiplicada).
const DOF = `
uniform sampler2D tColor; uniform sampler2D tDepth; uniform vec2 texel;
uniform float cerca, lejos, foco, apertura, maxR, paso, peso;
varying vec2 vUv;
float prof(vec2 uv) { float d = texture2D(tDepth, uv).x; return cerca * lejos / (lejos - d * (lejos - cerca)); }
float coc(float z) { return min(maxR, apertura * abs(1.0 - foco / z)); }
vec4 lin(vec4 c) { if (c.a <= 0.0001) return vec4(0.0); vec3 u = pow(max(c.rgb / c.a, 0.0), vec3(2.2)); return vec4(u * c.a, c.a); }
void main() {
  float zc = prof(vUv), cc = coc(zc);
  vec4 col = lin(texture2D(tColor, vUv));
  float tot = 1.0, r = paso, ang = 0.0;
  for (int i = 0; i < 1500; i++) {
    if (r >= maxR) break;
    ang += 2.39996323;
    vec2 uv = vUv + vec2(cos(ang), sin(ang)) * texel * r;
    float zs = prof(uv), cs = coc(zs);
    if (zs > zc) cs = clamp(cs, 0.0, cc * 2.0);
    float m = smoothstep(r - paso, r + paso, cs);
    col += mix(col / tot, lin(texture2D(tColor, uv)), m);
    tot += 1.0; r += paso / r;
  }
  gl_FragColor = col / tot * peso;
}`;
// salida: de luz lineal premultiplicada a sRGB premultiplicado (lo que espera el lienzo con alfa)
const COPIA = `
uniform sampler2D tAcum; varying vec2 vUv;
void main() {
  vec4 c = texture2D(tAcum, vUv); float a = clamp(c.a, 0.0, 1.0);
  if (a <= 0.0001) { gl_FragColor = vec4(0.0); return; }
  gl_FragColor = vec4(pow(clamp(c.rgb / c.a, 0.0, 1.0), vec3(1.0 / 2.2)) * a, a);
}`;

export function crearLente(renderer, scene, camara, cfg) {
  const prof = cfg.profundidad, mov = cfg.movimiento, dir = new THREE.Vector3(), tmp = new THREE.Vector3();
  const lente = {
    activa: !!(prof || mov),
    foco: prof?.foco ?? 10, apertura: prof ? (prof.apertura ?? 14) : 0, max: prof?.max ?? 22,
    // enfoca un punto (Vector3 o [x, y, z]): la distancia que cuenta es la de profundidad, a lo largo de la mirada
    enfocar(p) {
      const v = Array.isArray(p) ? tmp.set(...p) : tmp.copy(p);
      camara.updateMatrixWorld(); camara.getWorldDirection(dir);
      lente.foco = Math.max(0.05, v.sub(camara.position).dot(dir)); return lente.foco;
    },
  };
  if (!lente.activa) return { lente, pintar: (t, pinta, antes) => { antes(); renderer.render(scene, camara); } };

  const orto = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), plano = new THREE.PlaneGeometry(2, 2);
  const capa = (material) => { const s = new THREE.Scene(), m = new THREE.Mesh(plano, material); m.frustumCulled = false; s.add(m); return s; };
  const uDof = { tColor: { value: null }, tDepth: { value: null }, texel: { value: new THREE.Vector2() }, cerca: { value: 0.1 }, lejos: { value: 200 },
    foco: { value: 10 }, apertura: { value: 0 }, maxR: { value: 0 }, paso: { value: 0.5 }, peso: { value: 1 } };
  const sumar = { blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
    blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor, depthTest: false, depthWrite: false, toneMapped: false };
  const capaDof = capa(new THREE.ShaderMaterial({ uniforms: uDof, vertexShader: VERT, fragmentShader: DOF, ...sumar }));
  const uCopia = { tAcum: { value: null } };
  const capaCopia = capa(new THREE.ShaderMaterial({ uniforms: uCopia, vertexShader: VERT, fragmentShader: COPIA, depthTest: false, depthWrite: false, toneMapped: false, blending: THREE.NoBlending }));

  let rtEsc = null, rtAcum = null, W = 0, H = 0;
  const tam = new THREE.Vector2();
  function ajustar() {
    renderer.getDrawingBufferSize(tam); if (tam.x === W && tam.y === H) return;
    W = tam.x; H = tam.y; rtEsc?.dispose(); rtAcum?.dispose();
    // la escena se pinta como en pantalla (tone mapping y sRGB incluidos) en una textura con profundidad y antialiasing.
    // three r170 solo aplica tone mapping y sRGB al pintar en pantalla o en un destino «XR»: por eso se marca así.
    rtEsc = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4, depthTexture: new THREE.DepthTexture(W, H) });
    rtEsc.isXRRenderTarget = true; rtEsc.texture.colorSpace = THREE.SRGBColorSpace;
    rtAcum = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, depthBuffer: false });
    uDof.tColor.value = rtEsc.texture; uDof.tDepth.value = rtEsc.depthTexture; uDof.texel.value.set(1 / W, 1 / H); uCopia.tAcum.value = rtAcum.texture;
  }

  async function pintar(t, pinta, antes) {
    ajustar();
    const vista = location.search.includes('ver');
    const n = mov && !vista ? Math.max(1, Math.round(mov.muestras ?? 8)) : 1;
    const obt = (mov?.obturador ?? 0.5) / (window.__fps || 60), escala = H / 1080, auto = renderer.autoClear;
    renderer.autoClear = false;                              // los subfotogramas se suman en rtAcum: se limpia a mano
    renderer.setRenderTarget(rtAcum); renderer.clear();
    for (let i = 0; i < n; i++) {
      if (n > 1) pinta(t + obt * ((i + 0.5) / n - 0.5));    // obturador centrado en t
      antes();
      renderer.setRenderTarget(rtEsc); renderer.clear(); renderer.render(scene, camara);
      uDof.cerca.value = camara.near; uDof.lejos.value = camara.far; uDof.foco.value = lente.foco; uDof.apertura.value = lente.apertura * escala; uDof.maxR.value = lente.apertura > 0 ? lente.max * escala : 0;
      uDof.paso.value = 0.6 * Math.max(1, escala); uDof.peso.value = 1 / n;
      // por franjas: en 4K el desenfoque de un fotograma entero en una sola pasada puede tardar tanto que Windows
      // reinicia la tarjeta (TDR) y se caen Chrome y NVENC. En franjas de ~270 px cada pasada es corta; el resultado es igual.
      const franjas = uDof.maxR.value > 0 ? Math.max(1, Math.ceil(H / 270)) : 1, alto = Math.ceil(H / franjas), gl = renderer.getContext();
      rtAcum.scissorTest = franjas > 1;
      for (let f = 0; f < franjas; f++) {
        rtAcum.scissor.set(0, f * alto, W, alto); renderer.setRenderTarget(rtAcum); renderer.render(capaDof, orto);
        if (franjas > 1) gl.flush();
      }
      rtAcum.scissorTest = false;
    }
    if (n > 1) pinta(t);                                    // deja la escena (y la capa 2D) en el instante exacto
    renderer.setRenderTarget(null); renderer.clear(); renderer.render(capaCopia, orto);
    renderer.autoClear = auto;
  }
  return { lente, pintar };
}
