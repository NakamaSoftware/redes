"""nuevo.py · Motion Graphics Viegas
Crea la carpeta de un proyecto de motion graphics lista para trabajar.

  python nuevo.py <carpeta> [--plantilla 2d|3d|prueba|<ejemplo>] [--escenas 3] [--ancho 1920 --alto 1080]

Deja: motor/ (motor.js, motor3d.js, three.js, estilo.css) · escenas/escena-01.html … · recursos/ · referencia/ ·
resultados/ · BRIEF.md · STORYBOARD.md · estilo.json · escenas.json (opcional, para varias escenas en un HTML).
<ejemplo> = cualquier escena de ejemplos/ (logo-barrido, arco-3d, flujo-nodos, …): se copia como punto de partida.
Con --plantilla pantalla-3d también deja interfaces/ con la interfaz de muestra (editor-viegas.html): la pantalla en 3D.
Formatos: 1920×1080 (YouTube), 1080×1920 (Reel/Short), 1080×1350 (carrusel), 1080×1080 (cuadrado).
"""
import argparse
import os
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('carpeta')
    ap.add_argument('--plantilla', default='2d')
    ap.add_argument('--escenas', type=int, default=1)
    ap.add_argument('--ancho', type=int, default=1920)
    ap.add_argument('--alto', type=int, default=1080)
    a = ap.parse_args()
    dst = os.path.abspath(a.carpeta)
    os.makedirs(dst, exist_ok=True)
    for d in ('escenas', 'interfaces', 'recursos', 'referencia', 'resultados'):
        os.makedirs(os.path.join(dst, d), exist_ok=True)
    shutil.copytree(os.path.join(SKILL, 'motor'), os.path.join(dst, 'motor'), dirs_exist_ok=True)
    shutil.copytree(os.path.join(SKILL, 'scripts'), os.path.join(dst, 'scripts'), dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__'))
    for f in ('BRIEF.md', 'STORYBOARD.md', 'estilo.json'):
        if not os.path.exists(os.path.join(dst, f)):
            shutil.copy(os.path.join(SKILL, 'plantillas', f), os.path.join(dst, f))
    ejemplos = os.path.join(SKILL, 'ejemplos', 'escenas')
    origen = {'2d': os.path.join(SKILL, 'plantillas', 'escena-2d.html'), '3d': os.path.join(SKILL, 'plantillas', 'escena-3d.html'),
              'prueba': os.path.join(SKILL, 'plantillas', 'prueba.html')}.get(a.plantilla) or os.path.join(ejemplos, a.plantilla + '.html')
    if not os.path.exists(origen):
        sys.exit(f'No existe la plantilla «{a.plantilla}». Opciones: 2d, 3d, prueba o un ejemplo de {ejemplos}')
    html = open(origen, encoding='utf-8').read().replace('ancho: 1920', f'ancho: {a.ancho}').replace('alto: 1080', f'alto: {a.alto}')
    if a.plantilla == 'prueba':
        open(os.path.join(dst, 'escenas', 'prueba.html'), 'w', encoding='utf-8').write(html)
    else:
        for i in range(1, a.escenas + 1):
            p = os.path.join(dst, 'escenas', f'escena-{i:02d}.html' if a.plantilla in ('2d', '3d') else f'{a.plantilla}.html' if a.escenas == 1 else f'{a.plantilla}-{i:02d}.html')
            if not os.path.exists(p):
                open(p, 'w', encoding='utf-8').write(html)
    # pantalla en 3D: las interfaces de muestra (HTML animado que luego se pone en 3D con obj.pantalla)
    interfaces = os.path.join(SKILL, 'ejemplos', 'interfaces')
    if a.plantilla.startswith('pantalla-3d') and os.path.isdir(interfaces):
        for f in os.listdir(interfaces):
            if not os.path.exists(os.path.join(dst, 'interfaces', f)):
                shutil.copy(os.path.join(interfaces, f), os.path.join(dst, 'interfaces', f))
    # vídeos de muestra para las tarjetas de los ejemplos (pequeños, en bucle)
    muestras = os.path.join(SKILL, 'ejemplos', 'escenas', 'vid')
    if os.path.isdir(muestras):
        shutil.copytree(muestras, os.path.join(dst, 'escenas', 'vid'), dirs_exist_ok=True)
    for f in ('claude.svg', 'claude-code-logo.svg', 'claude-logo.svg', 'ejemplos.css'):
        s = os.path.join(SKILL, 'ejemplos', 'escenas', f)
        if os.path.exists(s):
            shutil.copy(s, os.path.join(dst, 'escenas', f))
    print(f'✓ Proyecto en {dst}\n  escenas/  → edita el .html de cada animación (vista previa: ábrelo con ?ver)\n'
          f'  render    → node scripts/render.mjs video todas --calidad previa   (y --calidad final al aprobar)'
          + ('\n  pantalla  → primero node scripts/render.mjs pantalla editor-viegas (la interfaz en fotogramas)' if a.plantilla.startswith('pantalla-3d') else ''))


if __name__ == '__main__':
    main()
