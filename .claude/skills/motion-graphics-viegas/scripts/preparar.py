"""preparar.py · Motion Graphics Viegas
Comprueba si este equipo tiene todo lo necesario para crear motion graphics con Claude Code y, si se le pide,
instala lo que falte. Claude Code lo ejecuta la primera vez (y cada vez que algo falla). Se puede repetir sin miedo.

  python preparar.py                       solo comprueba y dice qué falta (no instala nada)
  python preparar.py --instalar            instala lo que falte (winget en Windows, Homebrew en Mac, pip y npm)
  python preparar.py --instalar --prueba   … y al final renderiza una animación de prueba de 2 s
  python preparar.py --json                el resultado en JSON (para Claude Code)
  --trabajo "D:/Mis animaciones"           otra carpeta de trabajo (por defecto Documentos/Motion Graphics)

Comprueba: Node.js · ffmpeg y ffprobe (con H.264, ProRes y NVENC si hay tarjeta NVIDIA) · Python 3.9+ con numpy,
pillow (y opencv, opcional: mejora el análisis de referencias) · Playwright · Google Chrome · tarjeta gráfica ·
fuentes de la marca · conexión a internet (para buscar recursos en la nube) · la skill en ~/.claude/skills.
Nunca instala Claude Code: si lo ejecutas desde Claude Code, ya lo tienes.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

WIN = sys.platform.startswith('win')
MAC = sys.platform == 'darwin'
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = 'python' if WIN else 'python3'
CHROMES = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
           os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/Application/chrome.exe'),
           '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium']


def documentos():
    if WIN:
        try:
            import ctypes
            import ctypes.wintypes
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
            if buf.value:
                return buf.value
        except Exception:
            pass
    return os.path.join(os.path.expanduser('~'), 'Documents')


def refrescar_path():
    if WIN:
        try:
            import winreg
            partes = []
            for raiz, sub in [(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'),
                              (winreg.HKEY_CURRENT_USER, 'Environment')]:
                with winreg.OpenKey(raiz, sub) as k:
                    partes.append(os.path.expandvars(winreg.QueryValueEx(k, 'Path')[0]))
            os.environ['PATH'] = ';'.join(partes + [os.environ.get('PATH', '')])
        except Exception:
            pass
    else:
        os.environ['PATH'] = ':'.join(['/opt/homebrew/bin', '/usr/local/bin', os.path.expanduser('~/.local/bin'), os.environ.get('PATH', '')])


def correr(cmd, cwd=None, timeout=1800):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=WIN and isinstance(cmd, str), timeout=timeout,
                           encoding='utf-8', errors='replace')
        return r.returncode == 0, (r.stdout or '') + (r.stderr or '')
    except Exception as e:
        return False, str(e)


def version(cmd):
    exe = shutil.which(cmd[0])
    if not exe:
        return None
    ok, out = correr([exe] + cmd[1:], timeout=60)
    return out.strip().splitlines()[0] if ok and out.strip() else None


def instalar_programa(nombre, winget_id, brew):
    if WIN and shutil.which('winget'):
        ok, out = correr(['winget', 'install', '-e', '--id', winget_id, '--silent', '--accept-source-agreements', '--accept-package-agreements'])
    elif MAC and shutil.which('brew'):
        ok, out = correr(['brew', 'install', brew])
    else:
        return False, f'no hay winget (Windows) ni Homebrew (Mac) para instalar {nombre}'
    refrescar_path()
    return ok, out[-600:]


def ffmpeg_capacidades():
    """Qué sabe hacer el ffmpeg de este equipo: H.264 (obligatorio), ProRes 4444 (vídeo con transparencia), NVENC (GPU)."""
    cap = {'h264': False, 'prores': False, 'nvenc': False}
    if not shutil.which('ffmpeg'):
        return cap
    ok, out = correr(['ffmpeg', '-hide_banner', '-encoders'], timeout=60)
    cap['h264'] = 'libx264' in out or 'h264_nvenc' in out
    cap['prores'] = 'prores_ks' in out
    if 'h264_nvenc' in out:  # que esté compilado no basta: hay que probar que la tarjeta responde
        ok2, _ = correr(['ffmpeg', '-hide_banner', '-v', 'error', '-f', 'lavfi', '-i', 'color=black:s=256x256:d=0.1',
                         '-c:v', 'h264_nvenc', '-f', 'null', '-'], timeout=60)
        cap['nvenc'] = ok2
    return cap


def gpu():
    if shutil.which('nvidia-smi'):
        ok, out = correr(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'], timeout=30)
        if ok and out.strip():
            return out.strip().splitlines()[0]
    if MAC:
        return 'Apple (Metal)'
    return None


def fuente_marca():
    rutas = [os.path.expandvars(r'%WINDIR%\Fonts'), os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts'),
             '/Library/Fonts', os.path.expanduser('~/Library/Fonts'), '/System/Library/Fonts']
    for r in rutas:
        if os.path.isdir(r) and any('sf-compact' in f.lower() or 'sfcompact' in f.lower() for f in os.listdir(r)):
            return True
    return False


def internet():
    try:
        urllib.request.urlopen(urllib.request.Request('https://api.iconify.design/collections?prefix=mdi',
                               headers={'User-Agent': 'Mozilla/5.0 (motion-graphics-viegas)'}), timeout=6)
        return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--instalar', action='store_true')
    ap.add_argument('--prueba', action='store_true')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--trabajo')
    a = ap.parse_args()
    trabajo = os.path.abspath(a.trabajo or os.path.join(documentos(), 'Motion Graphics'))
    refrescar_path()
    estado, hechos = [], []

    def linea(clave, ok, que, arreglo='', opcional=False):
        estado.append({'clave': clave, 'ok': bool(ok), 'que': que, 'arreglo': arreglo, 'opcional': opcional})

    # 1. Programas
    for clave, cmd, nombre, wid, brew, arreglo in [
        ('node', ['node', '-v'], 'Node.js', 'OpenJS.NodeJS.LTS', 'node', 'Windows: winget install OpenJS.NodeJS.LTS · Mac: brew install node · o nodejs.org (LTS)'),
        ('ffmpeg', ['ffmpeg', '-version'], 'ffmpeg', 'Gyan.FFmpeg', 'ffmpeg', 'Windows: winget install Gyan.FFmpeg · Mac: brew install ffmpeg'),
    ]:
        v = version(cmd)
        if not v and a.instalar:
            ok, out = instalar_programa(nombre, wid, brew)
            hechos.append(f'instalar {nombre}: {"ok" if ok else out}')
            v = version(cmd)
        txt = v.split()[2] if clave == 'ffmpeg' and v and len(v.split()) > 2 else (v or '')
        linea(clave, v, f'{nombre} {txt}'.strip(), arreglo)
    linea('ffprobe', shutil.which('ffprobe'), 'ffprobe (lee duración, fps y tamaño de los vídeos)', 'viene con ffmpeg: reinstala ffmpeg')
    cap = ffmpeg_capacidades()
    linea('h264', cap['h264'], 'ffmpeg con H.264 (MP4 para redes y editores)', 'instala una versión completa: winget install Gyan.FFmpeg')
    linea('prores', cap['prores'], 'ffmpeg con ProRes 4444 (vídeos con fondo transparente)', 'instala una versión completa de ffmpeg', opcional=True)
    g = gpu()
    linea('gpu', g, f'tarjeta gráfica: {g}' if g else 'sin tarjeta NVIDIA: se renderiza con el procesador (más lento, misma calidad)', opcional=True)
    linea('nvenc', cap['nvenc'], 'codificación por GPU (NVENC): exporta varias veces más rápido' if cap['nvenc'] else 'sin NVENC: se codifica con x264', opcional=True)

    # 2. Python y librerías (opencv es opcional: afina el análisis de movimiento de las referencias)
    falta, falta_opc = [], []
    for mod, pkg in [('numpy', 'numpy'), ('PIL', 'pillow')]:
        try:
            __import__(mod)
        except ImportError:
            falta.append(pkg)
    try:
        __import__('cv2')
    except ImportError:
        falta_opc.append('opencv-python-headless')
    try:
        __import__('yt_dlp')
    except ImportError:
        if not shutil.which('yt-dlp'):
            falta_opc.append('yt-dlp')
    if (falta or falta_opc) and a.instalar:
        base = [sys.executable, '-m', 'pip', 'install', '--quiet', '--disable-pip-version-check']
        ok, out = correr(base + falta + falta_opc)
        if not ok:
            ok, out = correr(base + ['--user', '--break-system-packages'] + falta + falta_opc)
        hechos.append(f'pip install {" ".join(falta + falta_opc)}: {"ok" if ok else out[-300:]}')
        import importlib
        importlib.invalidate_caches()
        if ok:
            falta, falta_opc = [], []
    linea('python', sys.version_info >= (3, 9) and not falta, f'Python {sys.version.split()[0]} · numpy · pillow' + (f' (faltan: {", ".join(falta)})' if falta else ''),
          f'{PY} -m pip install {" ".join(falta) or "numpy pillow"}')
    linea('ytdlp', 'yt-dlp' not in falta_opc, 'yt-dlp (descargar referencias de Pinterest, Instagram, YouTube, TikTok…)', f'{PY} -m pip install yt-dlp', opcional=True)
    linea('opencv', 'opencv-python-headless' not in falta_opc, 'OpenCV (análisis de movimiento más preciso)', f'{PY} -m pip install opencv-python-headless', opcional=True)

    # 3. Skill, carpeta de trabajo y Playwright (una sola instalación para todos los proyectos)
    linea('skill', os.path.isfile(os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'motion-graphics-viegas', 'SKILL.md')),
          'skill motion-graphics-viegas en ~/.claude/skills', 'copia la carpeta motion-graphics-viegas en ~/.claude/skills')
    pw = os.path.isdir(os.path.join(trabajo, 'node_modules', 'playwright'))
    if a.instalar:
        os.makedirs(trabajo, exist_ok=True)
        pkg = os.path.join(trabajo, 'package.json')
        if not os.path.exists(pkg):
            with open(pkg, 'w', encoding='ascii') as f:
                f.write('{ "name": "motion-graphics", "private": true, "type": "module" }\n')
        cm = os.path.join(trabajo, 'CLAUDE.md')
        if not os.path.exists(cm):
            shutil.copy(os.path.join(SKILL, 'plantillas', 'CLAUDE-carpeta-de-trabajo.md'), cm)
        if not pw and shutil.which('npm'):
            ok, out = correr('npm install --no-audit --no-fund --silent playwright' if WIN else ['npm', 'install', '--no-audit', '--no-fund', '--silent', 'playwright'], cwd=trabajo)
            hechos.append(f'npm install playwright: {"ok" if ok else out[-300:]}')
            pw = os.path.isdir(os.path.join(trabajo, 'node_modules', 'playwright'))
        if pw and not next((c for c in CHROMES if os.path.exists(c)), None):
            ok, out = correr('npx --yes playwright install chromium' if WIN else ['npx', '--yes', 'playwright', 'install', 'chromium'], cwd=trabajo)
            hechos.append(f'navegador de Playwright: {"ok" if ok else out[-300:]}')
    linea('carpeta', os.path.isfile(os.path.join(trabajo, 'CLAUDE.md')), f'carpeta de trabajo {trabajo}', f'{PY} "{os.path.abspath(__file__)}" --instalar')
    linea('playwright', pw, 'Playwright (la cámara que fotografía cada fotograma)', f'en {trabajo}: npm install playwright')
    ch = next((c for c in CHROMES if os.path.exists(c)), None)
    linea('chrome', True, 'Google Chrome' if ch else 'sin Google Chrome: se usa el navegador de Playwright', opcional=True)
    linea('fuente', fuente_marca(), 'fuente de la marca (SF Compact Display)' if fuente_marca() else 'sin SF Compact Display: se usa Inter o la del sistema', opcional=True)
    linea('internet', internet(), 'internet para buscar recursos (iconos, logos, fuentes, imágenes)', 'sin conexión: solo recursos locales', opcional=True)

    # 4. Prueba real: una animación de 2 s
    if a.prueba and all(e['ok'] for e in estado if not e['opcional']):
        dst = os.path.join(trabajo, 'prueba-del-kit')
        shutil.rmtree(dst, ignore_errors=True)
        ok, out = correr([sys.executable, os.path.join(SKILL, 'scripts', 'nuevo.py'), dst, '--plantilla', 'prueba'])
        if ok:
            ok, out = correr('node scripts/render.mjs video todas --calidad previa' if WIN else ['node', 'scripts/render.mjs', 'video', 'todas', '--calidad', 'previa'], cwd=dst, timeout=600)
        mp4 = os.path.join(dst, 'resultados', 'prueba-previa.mp4')
        linea('prueba', os.path.isfile(mp4), f'prueba real: {mp4}', out.strip()[-400:])

    listo = all(e['ok'] for e in estado if not e['opcional'])
    if a.json:
        print(json.dumps({'listo': listo, 'trabajo': trabajo, 'estado': estado, 'hecho': hechos}, ensure_ascii=False, indent=1))
        sys.exit(0 if listo else 1)
    print('\nMotion Graphics Viegas · preparar el equipo\n')
    for h in hechos:
        print('  · ' + h)
    for e in estado:
        marca = '✓' if e['ok'] else ('·' if e['opcional'] else '✗')
        print(f'  {marca} ' + e['que'] + ('' if e['ok'] or not e['arreglo'] else f"\n      → {e['arreglo']}"))
    print()
    if listo:
        print('✓ Todo listo. Abre Claude Code en tu carpeta de trabajo y pide tu animación:')
        print(f'  {trabajo}')
    else:
        n = sum(not e['ok'] and not e['opcional'] for e in estado)
        print(f'Falta arreglar {n} cosa(s).' + ('' if a.instalar else f' Para instalarlo solo: {PY} "{os.path.abspath(__file__)}" --instalar'))
        print('Atajo: abre Claude Code y pégale esta lista con «arregla esto en mi computadora».')
    sys.exit(0 if listo else 1)


if __name__ == '__main__':
    main()
