// mascota3d.js · Motion Graphics Viegas · la mascota de Claude Code en 3D, como personaje
// Las proporciones salen del SVG oficial (claude-code-logo.svg, rejilla de 24): cuerpo 18 × 12, brazos 3 × 3,1 a los lados,
// 4 patas de 1,5 × 2,9 y dos ojos de 1,5 × 2,85. Aquí con volumen real (cajas redondeadas), ojos oscuros con brillo,
// patas que andan, parpadeo y saludo con el brazo. Lo usa motor3d: obj.mascotaClaude({ tam }).
//
//   const m = obj.mascotaClaude({ tam: 0.5 });     // tam = ancho total (con los brazos); de pie, base en y = 0, mira a +z
//   m.andar(fase, fuerza) · m.parpadear(p 0–1) · m.saludar(p 0–1, t) · m.partes { cuerpo, patas, brazos, ojos }
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export function crearMascota(mat, o = {}) {
  const g = (o.tam ?? 0.5) / 24, fondo = (o.fondo ?? 9) * g;            // 1 unidad de la rejilla del SVG
  const piel = o.mat || mat.coral({ clearcoat: 1, clearcoatRoughness: 0.12, roughness: 0.34 });
  const ojoMat = new THREE.MeshPhysicalMaterial({ color: 0x050405, roughness: 0.25, clearcoat: 1, clearcoatRoughness: 0.06, envMapIntensity: 0.25 });
  const caja = (w, h, d, m, r) => { const x = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 5, r), m); x.castShadow = x.receiveShadow = true; return x; };
  const raiz = new THREE.Group();
  const PATA = 2.92, cuerpoH = 12.08;
  // cuerpo (con un poco de bote al andar)
  const cuerpo = new THREE.Group(); raiz.add(cuerpo);
  const tronco = caja(18 * g, cuerpoH * g, fondo, piel, 1.3 * g); tronco.position.y = (PATA + cuerpoH / 2) * g; cuerpo.add(tronco);
  // ojos: en la cara de delante, un pelín salientes y muy brillantes
  const ojos = [-5.26, 5.25].map((x) => { const e = caja(1.5 * g, 2.85 * g, 0.5 * g, ojoMat, 0.35 * g);
    e.position.set(x * g, (20 - 10.47) * g, fondo / 2 + 0.05 * g); cuerpo.add(e); return e; });
  // brazos: girados desde el hombro (el saludo)
  const brazos = [-1, 1].map((s) => { const hombro = new THREE.Group(); hombro.position.set(s * 9 * g, 7.5 * g, 0);
    const b = caja(3 * g, 3.1 * g, 3.4 * g, piel, 0.8 * g); b.position.x = s * 1.5 * g; hombro.add(b); cuerpo.add(hombro); return hombro; });
  // patas: 4 en fila, como en el SVG; cada una sube y baja por turnos al andar
  const patas = [-6.76, -3.76, 3.76, 6.76].map((x) => { const p = caja(1.51 * g, PATA * g, 1.8 * g, piel, 0.45 * g);
    p.position.set(x * g, (PATA / 2) * g, 0); raiz.add(p); return p; });

  raiz.partes = { cuerpo, patas, brazos, ojos };
  // andar: fase en vueltas (1 = un paso de cada pata) · fuerza 0–1
  raiz.andar = (fase, fuerza = 1) => {
    patas.forEach((p, i) => { const s = Math.max(0, Math.sin((fase + (i % 2) * 0.5) * Math.PI * 2));
      p.position.y = (PATA / 2 + 1.1 * s * fuerza) * g; p.rotation.x = -0.25 * s * fuerza; });
    cuerpo.position.y = 0.45 * g * fuerza * Math.abs(Math.sin(fase * Math.PI * 2));
    cuerpo.rotation.z = 0.05 * fuerza * Math.sin(fase * Math.PI * 2);
  };
  raiz.parpadear = (p) => ojos.forEach((e) => { e.scale.y = Math.max(0.12, 1 - p); });
  // saludar: el brazo derecho sube y saluda (p 0–1 = cuánto está levantado; t para el vaivén)
  raiz.saludar = (p, t = 0) => { const h = brazos[1]; h.position.y = (7.5 + 5.2 * p) * g; h.rotation.z = p * (0.75 + 0.45 * Math.sin(t * 13)); brazos[0].rotation.z = -0.1 * p; };
  // brazos que acompañan al andar o al saltar (a = 0–1)
  raiz.brazosArriba = (a) => { brazos.forEach((h) => { h.position.y = 7.5 * g; }); brazos[0].rotation.z = -0.9 * a; brazos[1].rotation.z = 0.9 * a; };
  return raiz;
}
