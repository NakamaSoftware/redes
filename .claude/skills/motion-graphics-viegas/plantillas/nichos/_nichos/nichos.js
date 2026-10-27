// nichos.js · utilidades de las «Plantillas por nicho» (Viegas IA · Motion Lab)
// Va después de motor.js y estilos.js. Uso dentro de escena(): const N = NICHOS(MG);
//
//   Parámetros comunes (bloque <script id="params">): "paleta": "noche" (noche azul de Viegas, por defecto) | "claro"
//   "acento": "#hex" (vacío = el del tema) · "marca": nombre del negocio · "logo": ruta a tu logo (PNG/SVG; vacío = inicial)
//
//   N.es(el, t, t0, t1, o)  entra en t0 (rebote + desenfoque de movimiento) y sale en t1 con la curva inversa (acelera y se va).
//                           o: x, y (posición final), dx, dy (desde dónde llega), ox, oy (hacia dónde se va), d, dOut,
//                           curva (entrada), curvaSal (salida), s0 (escala inicial), s1 (escala al salir), rot (grados al llegar)
//   N.vivo(t)               cámara que nunca se para + manchas de luz suaves (desenfoque gaussiano) que derivan
//   N.foto(src, w, h)       tarjeta con foto (object-fit: cover) · N.kb(foto, t, s0, s1) zoom lento tipo Ken Burns
//   N.marca()               HTML del distintivo de marca (logo o inicial + nombre)
//   N.cx(el)                x para centrar un elemento · N.escribe(el, texto, t, a, b) máquina de escribir
//   N.estrella(llena)       SVG de estrella (0–1 de relleno) en el color de acento
(function () {
  const PALETAS = {
    claro: { '--fondo': '#F4F2EE', '--fondo-rgb': '244,242,238', '--texto': '#14161C', '--mute': '#5E6573', '--tarjeta': '#FFFFFF', '--tarjeta2': '#F7F6F3',
      '--superficie': '#E6E3DD', '--acento': '#2563EB', '--acento2': '#2563EB', '--brillo': '#2563EB', '--halo': '37,99,235', '--claro': '20,22,28', '--sombra': '30,35,60', '--tinta': '#FFFFFF' },
  };
  const rgb = (hex) => { const h = hex.replace('#', ''); const n = parseInt(h.length === 3 ? h.replace(/./g, '$&$&') : h, 16); return `${(n >> 16) & 255},${(n >> 8) & 255},${n & 255}`; };
  window.NICHOS = function (MG) {
    const { P, W, H } = EST, { k, lerp, curvas: C, DT, MB } = MG, raiz = document.documentElement.style;
    const pal = PALETAS[P.paleta];
    if (pal) { Object.entries(pal).forEach(([a, b]) => raiz.setProperty(a, b)); document.body.classList.add('n-claro'); }
    if (P.acento) { raiz.setProperty('--acento', P.acento); raiz.setProperty('--halo', rgb(P.acento)); raiz.setProperty('--brillo', P.acento); raiz.setProperty('--acento2', P.acento); }
    // manchas de luz: desenfoque gaussiano muy amplio (nunca cuadriculado), se mueven despacio con t
    const U = Math.min(W, H) / 1080;
    const blobs = [[.18, .22, 760, 'var(--acento)'], [.86, .7, 900, 'var(--brillo, var(--acento2))'], [.4, 1.02, 700, 'var(--acento)']].map(([x, y, r, c], i) => {
      const b = MG.el(`<div class="n-blob" style="width:${r * U}px;height:${r * U}px;background:radial-gradient(circle, ${c}, transparent 68%)"></div>`);
      b._b = { x: x * W - r * U / 2, y: y * H - r * U / 2, f: .23 + i * .07, a: 60 + i * 30 }; MG.mundo.prepend(b); return b;
    });
    const N = {
      P, W, H, U, C, k, lerp,
      vivo(t, z0 = 1, z1 = 1.07) {
        MG.camara(t, z0, z1);
        blobs.forEach((b, i) => { const o = b._b; MG.pon(b, o.x + Math.sin(t * o.f + i) * o.a, o.y + Math.cos(t * o.f * .8 + i * 2) * o.a * .7); });
      },
      es(el, t, t0, t1, o = {}) {
        let x = o.x || 0, y = o.y || 0, s = 1, rot = 0;
        if (t1 == null || t < t1) {
          const e = MG.entra(el, t, t0, { d: o.d ?? .7, dx: o.dx ?? 0, dy: o.dy ?? 140, escala0: o.s0 ?? .92, curva: o.curva || 'rebote', base: o.base ?? 4 });
          x += e.x; y += e.y; s = e.s; rot = (o.rot || 0) * (1 - Math.min(1, e.p));
        } else {
          const dO = o.dOut ?? .45, cv = C[o.curvaSal || 'entradaCubica'], p = cv(k(t, t1, t1 + dO)), q = cv(k(t - DT, t1, t1 + dO));
          const ox = o.ox ?? 0, oy = o.oy ?? -110;
          x += ox * p; y += oy * p; s = lerp(1, o.s1 ?? 1.06, p);
          el.style.opacity = 1 - p;
          MG.desenfoca(el, Math.abs(ox * (p - q) / DT) * MB + p * 8, Math.abs(oy * (p - q) / DT) * MB + p * 8);
        }
        MG.pon(el, x, y, s, rot ? `rotate(${rot}deg)` : ''); return { x, y, s };
      },
      foto(src, w, h, padre) {
        const f = MG.el(`<div class="n-foto" style="width:${w}px;height:${h}px"><img src="${src}" alt=""></div>`, padre); f._img = f.firstChild; return f;
      },
      kb(f, t, s0 = 1.12, s1 = 1.0, dx = 0) { f._img.style.transform = `scale(${lerp(s0, s1, t / P.duracion)}) translateX(${dx * t / P.duracion}px)`; },
      marca(tam = 1) {
        const ini = (P.marca || '·').trim()[0].toUpperCase();
        return `<div class="n-marca" style="font-size:${38 * tam}px"><span class="ic" style="width:${72 * tam}px;height:${72 * tam}px">${P.logo ? `<img src="${P.logo}" alt="">` : ini}</span>${P.marca || ''}</div>`;
      },
      cx: (el) => (W - el.offsetWidth) / 2,
      escribe(el, txt, t, a, b, cursor = true) { const n = Math.round(txt.length * k(t, a, b)); el.textContent = txt.slice(0, n) + (cursor && t > a - .3 && t < b + .8 && Math.floor(t * 3) % 2 ? '|' : ''); },
      estrella(llena = 1, id = 'e' + Math.random().toString(36).slice(2, 7)) {
        return `<svg viewBox="0 0 24 24"><defs><linearGradient id="${id}"><stop offset="${llena * 100}%" stop-color="var(--estrella, #FBBF24)"/><stop offset="${llena * 100}%" stop-color="rgba(var(--claro),.18)"/></linearGradient></defs><path fill="url(#${id})" d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.5L12 17.3l-5.9 3.2 1.3-6.5L2.5 9.4l6.6-.8z"/></svg>`;
      },
      // *palabras* → <em> palabra a palabra (para que MG.texto las anime por separado)
      md: (s) => String(s).replace(/\*([^*]+)\*/g, (_, g) => g.split(' ').map((w) => `<em>${w}</em>`).join(' ')),
      // texto por palabras centrado en un ancho fijo
      frase(s, clase, ancho = W - 160, modo = 'palabras') { const el = MG.texto(N.md(s), clase, modo); el.style.width = ancho + 'px'; return el; },
      // escala de "pop" con rebote (para iconos, precios, sellos)
      pop(t, t0, d = .6, curva = 'reboteFuerte') { return Math.max(0, C[curva](k(t, t0, t0 + d * 1.5))); },
    };
    return N;
  };
})();
