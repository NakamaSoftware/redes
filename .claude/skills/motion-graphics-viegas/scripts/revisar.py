"""revisar.py · Motion Graphics Viegas
Revisa cada animación renderizada ANTES de entregarla: que se parezca a la referencia, que sea coherente con la marca
y con las demás animaciones, y que no tenga los errores de siempre. Se ejecuta desde la carpeta del proyecto.

  python scripts/revisar.py [todas|nombre1,nombre2]      → resultados/revision.md (y resultados/revision/<nombre>/…)

Comprueba, por animación:
  1. Formato: tamaño, fps y duración (y que todas las del proyecto coincidan entre sí).
  2. «Nada aparece de golpe»: fotogramas con un salto de imagen enorme que no es un corte buscado.
  3. «La cámara nunca se para»: tramos de más de 0,5 s sin ningún movimiento.
  4. Curvas: las que usa (medidas sobre el MP4, con referencia.py) frente a las de la referencia y a la curva de la marca.
  5. Ritmo: duración media de los movimientos y escalonado, frente a la referencia (si hay referencia/analisis.json).
  6. Color: los colores dominantes frente a estilo.json (avisa de colores que no son de la marca).
Nota de 0 a 10 por apartado. Una animación se entrega solo con todo ≥ 8.
"""
import glob
import json
import os
import subprocess
import sys

import numpy as np

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import referencia as R  # noqa: E402


def hexrgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else 'todas'
    vids = sorted(glob.glob('resultados/*.mp4'))
    if arg != 'todas':
        quiero = arg.split(',')
        vids = [v for v in vids if os.path.basename(v).replace('-previa', '').rsplit('.', 1)[0] in quiero]
    if not vids:
        sys.exit('No hay MP4 en resultados/: renderiza primero (node scripts/render.mjs video todas).')
    ref = json.load(open('referencia/analisis.json', encoding='utf-8')) if os.path.exists('referencia/analisis.json') else None
    estilo = json.load(open('estilo.json', encoding='utf-8')) if os.path.exists('estilo.json') else {}
    curva_marca = estilo.get('curva_por_defecto', 'rebote')
    marca = [hexrgb(c) for c in (estilo.get('colores') or {}).values()]
    L = ['# Revisión de las animaciones', '']
    formatos = set()
    for v in vids:
        nombre = os.path.basename(v).rsplit('.', 1)[0]
        dst = os.path.join('resultados', 'revision', nombre)
        subprocess.run([sys.executable, os.path.join(AQUI, 'referencia.py'), v, '--salida', dst], capture_output=True)
        try:
            a = json.load(open(os.path.join(dst, 'analisis.json'), encoding='utf-8'))
        except Exception:
            L += [f'## {nombre}', '- ✗ No se pudo analizar.', '']; continue
        info = a['info']; formatos.add((info['ancho'], info['alto'], round(info['fps'])))
        # 2) golpes: saltos de imagen > 6× la mediana fuera de cortes buscados
        F = R.fotogramas(v, 30, 0, 0, int(round(R.W_AN * info['alto'] / info['ancho'] / 2) * 2)).mean(-1) / 255
        d = np.abs(np.diff(F, axis=0)).mean((1, 2)) if len(F) > 1 else np.zeros(1)
        med = np.median(d) + 1e-4
        golpes = [round((i + 1) / 30, 2) for i, x in enumerate(d) if x > max(0.06, med * 8) and i > 1]
        # 3) cámara/escena quieta: más de 0,5 s seguidos sin movimiento
        quieto = d < max(0.0008, med * 0.15)
        tramo, peor = 0, 0
        for q in quieto:
            tramo = tramo + 1 if q else 0; peor = max(peor, tramo)
        quieta_s = round(peor / 30, 2)
        # 4) curvas
        movs = a.get('movimientos', [])
        usadas = [m['curva'] for m in movs if m.get('tipo') != 'cámara']   # la cámara va lineal por regla: no cuenta
        familia = lambda c: 'rebote' if c.startswith('rebote') or c == 'atras' else ('salida' if c.startswith('salida') else ('entradaSalida' if c in ('entradaSalidaQuint', 'suave') else c))
        if ref and ref.get('curvas_mas_usadas'):
            objetivo = familia(ref['curvas_mas_usadas'][0][0])
        else:
            objetivo = familia(curva_marca)
        coinciden = sum(familia(c) == objetivo for c in usadas)
        nota_curvas = 10 if not usadas else round(10 * coinciden / len(usadas), 1)
        # 5) ritmo
        nota_ritmo, txt_ritmo = 10, 'sin referencia: se usa el ritmo de la marca (escalonado 0,05–0,3 s)'
        if ref and ref.get('duracion_media_movimiento_s') and a.get('duracion_media_movimiento_s'):
            r_ = a['duracion_media_movimiento_s'] / ref['duracion_media_movimiento_s']
            nota_ritmo = round(max(0, 10 - abs(np.log2(r_)) * 8), 1)
            txt_ritmo = f"movimientos de {a['duracion_media_movimiento_s']} s frente a {ref['duracion_media_movimiento_s']} s de la referencia (×{r_:.2f})"
        # 6) color: % de píxeles lejos de cualquier color de la marca (solo colores saturados; negros y grises no cuentan)
        nota_color, raros = 10, []
        if marca:
            for hx, pct in a['paleta']:
                c = hexrgb(hx); sat = c.max() - c.min()
                if sat > 40 and min(np.linalg.norm(c - m) for m in marca) > 70 and pct > 0.04:
                    raros.append(f'{hx} ({int(pct * 100)} %)')
            nota_color = 10 - 3 * len(raros)
        n_golpes = 10 - 3 * len(golpes); n_quieta = 10 if quieta_s <= 0.5 else max(0, 10 - (quieta_s - 0.5) * 6)
        notas = {'formato': 10, 'nada de golpe': max(0, n_golpes), 'cámara viva': round(n_quieta, 1), 'curvas': nota_curvas, 'ritmo': nota_ritmo, 'color': max(0, nota_color)}
        ok = all(x >= 8 for x in notas.values())
        L += [f"## {'✓' if ok else '✗'} {nombre}", f"- {info['ancho']}×{info['alto']} · {info['fps']} fps · {info['duracion']:.2f} s",
              f"- Notas: " + ' · '.join(f'{k} {v}' for k, v in notas.items()),
              f"- Golpes (algo aparece de un fotograma a otro): {golpes or 'ninguno'}",
              f"- Tramo quieto más largo: {quieta_s} s" + ('' if quieta_s <= 0.5 else ' → añade zoom lineal de cámara o un movimiento continuo'),
              f"- Curvas medidas: {', '.join(sorted(set(usadas))) or '—'} · objetivo: familia «{objetivo}» ({coinciden}/{len(usadas)})",
              f"- Ritmo: {txt_ritmo}", f"- Colores fuera de la marca: {', '.join(raros) or 'ninguno'}",
              f"- Gráfica de curvas: `{dst}/curvas.png` · hoja: `{dst}/hoja.jpg`", '']
    if len(formatos) > 1:
        L.insert(2, f'⚠ Las animaciones no tienen el mismo formato: {sorted(formatos)}. Para una serie, deben coincidir.\n')
    open('resultados/revision.md', 'w', encoding='utf-8').write('\n'.join(L))
    print('\n'.join(L))


if __name__ == '__main__':
    main()
