"""recursos.py · Motion Graphics Viegas
Busca y descarga recursos para las animaciones cuando la persona no los tiene. Todo queda en recursos/ con su licencia
apuntada en recursos/LICENCIAS.md (fuente, autor, licencia y enlace), para poder usarlo con tranquilidad.

  python recursos.py icono "rocket"            [--n 6] [--color D97757]   iconos SVG (Iconify: +200 000, libres)
  python recursos.py logo "figma"              [--color original]          logo oficial de una marca (Simple Icons / Logos de Iconify)
  python recursos.py fuente "Inter"            [--pesos 400,700,800]       fuente de Google Fonts (woff2) + @font-face listo
  python recursos.py imagen "abstract gradient" [--n 6]                    imágenes con licencia abierta (Openverse: CC0 / CC BY)
  python recursos.py video "ocean waves"       [--n 4]                     vídeos libres (Pexels o Pixabay si hay clave; si no, Wikimedia Commons)
  python recursos.py modelo3d "chair"          [--n 4]                     modelos 3D .glb libres (Poly Haven)
  --carpeta recursos                                                       dónde guardarlos (por defecto ./recursos)

Claves opcionales (variables de entorno): PEXELS_API_KEY, PIXABAY_API_KEY (más y mejores vídeos y fotos).
Los logos de marcas son marcas registradas: úsalos solo para referirte a esa marca (no como si fueran tuyos).
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

UA = {'User-Agent': 'Mozilla/5.0 (motion-graphics-viegas; +https://viegasestudio.com)'}


def get(url, headers=None, binario=False, timeout=30):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binario else data.decode('utf-8', 'replace')


def guarda(carpeta, nombre, data):
    os.makedirs(carpeta, exist_ok=True)
    p = os.path.join(carpeta, re.sub(r'[^\w.\-]+', '-', nombre).strip('-'))
    with open(p, 'wb') as f:
        f.write(data if isinstance(data, bytes) else data.encode('utf-8'))
    return p


def licencia(carpeta, archivo, fuente, autor, lic, enlace):
    p = os.path.join(carpeta, 'LICENCIAS.md')
    nuevo = not os.path.exists(p)
    with open(p, 'a', encoding='utf-8') as f:
        if nuevo:
            f.write('# Recursos y licencias\n\n| Archivo | Fuente | Autor | Licencia | Enlace |\n|---|---|---|---|---|\n')
        f.write(f'| {os.path.basename(archivo)} | {fuente} | {autor} | {lic} | {enlace} |\n')


def icono(q, n, color, carpeta):
    r = json.loads(get(f'https://api.iconify.design/search?query={urllib.parse.quote(q)}&limit={max(n * 3, 12)}'))
    out = []
    # preferimos colecciones con licencias abiertas y estilo limpio
    pref = ['lucide', 'tabler', 'ph', 'mdi', 'material-symbols', 'solar', 'iconoir', 'heroicons', 'fluent']
    iconos = sorted(r.get('icons', []), key=lambda x: pref.index(x.split(':')[0]) if x.split(':')[0] in pref else 99)[:n]
    for ic in iconos:
        pre, nom = ic.split(':')
        svg = get(f'https://api.iconify.design/{pre}/{nom}.svg' + (f'?color=%23{color}' if color else ''))
        p = guarda(carpeta, f'icono-{pre}-{nom}.svg', svg)
        lic = (r.get('collections', {}).get(pre, {}) or {}).get('license', {})
        licencia(carpeta, p, f'Iconify · {pre}', (r.get('collections', {}).get(pre, {}) or {}).get('author', {}).get('name', pre), lic.get('title', 'ver colección'), f'https://icon-sets.iconify.design/{pre}/{nom}/')
        out.append(p)
    return out


def logo(q, color, carpeta):
    out = []
    for pre in ('logos', 'simple-icons', 'devicon'):
        r = json.loads(get(f'https://api.iconify.design/search?query={urllib.parse.quote(q)}&prefix={pre}&limit=4'))
        for ic in r.get('icons', [])[:2]:
            p_, nom = ic.split(':')
            url = f'https://api.iconify.design/{p_}/{nom}.svg' + (f'?color=%23{color}' if color and color != 'original' and p_ == 'simple-icons' else '')
            p = guarda(carpeta, f'logo-{nom}-{p_}.svg', get(url))
            licencia(carpeta, p, f'Iconify · {p_}', 'la marca', 'marca registrada (solo para referirse a ella)', f'https://icon-sets.iconify.design/{p_}/{nom}/')
            out.append(p)
        if out:
            break
    return out


def fuente(familia, pesos, carpeta):
    url = f'https://fonts.googleapis.com/css2?family={urllib.parse.quote(familia)}:wght@{";".join(pesos.split(","))}&display=swap'
    css = get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'})
    out, nuevo = [], []
    for bloque in re.findall(r'/\*\s*latin\s*\*/\s*(@font-face\s*{[^}]+})', css):
        w = re.search(r'font-weight:\s*(\d+)', bloque).group(1)
        src = re.search(r'url\((https://[^)]+\.woff2)\)', bloque).group(1)
        p = guarda(carpeta, f'{familia.replace(" ", "")}-{w}.woff2', get(src, binario=True))
        nuevo.append(f"@font-face {{ font-family: '{familia}'; font-weight: {w}; src: url('{os.path.basename(p)}') format('woff2'); font-display: block; }}")
        out.append(p)
    if out:
        guarda(carpeta, f'{familia.replace(" ", "")}.css', '\n'.join(nuevo) + '\n')
        licencia(carpeta, f'{familia}.woff2', 'Google Fonts', familia, 'SIL Open Font License', f'https://fonts.google.com/specimen/{familia.replace(" ", "+")}')
    return out


def imagen(q, n, carpeta):
    r = json.loads(get(f'https://api.openverse.org/v1/images/?q={urllib.parse.quote(q)}&license_type=commercial&page_size={n}&mature=false'))
    out = []
    for it in r.get('results', [])[:n]:
        try:
            ext = os.path.splitext(urllib.parse.urlparse(it['url']).path)[1] or '.jpg'
            p = guarda(carpeta, f'imagen-{it["id"][:8]}{ext}', get(it['url'], binario=True))
            licencia(carpeta, p, f'Openverse · {it.get("source")}', it.get('creator') or '—', f'{it.get("license", "").upper()} {it.get("license_version", "")}', it.get('foreign_landing_url', ''))
            out.append(p)
        except Exception as e:
            print('  · no se pudo bajar una imagen:', e)
    return out


def video(q, n, carpeta):
    out = []
    kp, kx = os.environ.get('PEXELS_API_KEY'), os.environ.get('PIXABAY_API_KEY')
    if kp:
        r = json.loads(get(f'https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page={n}', headers={'Authorization': kp}))
        for v in r.get('videos', [])[:n]:
            f = sorted(v['video_files'], key=lambda x: abs((x.get('width') or 0) - 1920))[0]
            p = guarda(carpeta, f'video-pexels-{v["id"]}.mp4', get(f['link'], binario=True, timeout=120))
            licencia(carpeta, p, 'Pexels', v.get('user', {}).get('name', '—'), 'Licencia Pexels (uso libre)', v.get('url', '')); out.append(p)
    elif kx:
        r = json.loads(get(f'https://pixabay.com/api/videos/?key={kx}&q={urllib.parse.quote(q)}&per_page={max(3, n)}'))
        for v in r.get('hits', [])[:n]:
            f = v['videos'].get('large') or v['videos'].get('medium')
            p = guarda(carpeta, f'video-pixabay-{v["id"]}.mp4', get(f['url'], binario=True, timeout=120))
            licencia(carpeta, p, 'Pixabay', v.get('user', '—'), 'Licencia Pixabay (uso libre)', v.get('pageURL', '')); out.append(p)
    else:
        api = ('https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=' + str(n * 3) +
               '&gsrsearch=' + urllib.parse.quote(f'{q} filetype:video') + '&prop=imageinfo&iiprop=url|extmetadata|mime')
        r = json.loads(get(api))
        for pg in list((r.get('query') or {}).get('pages', {}).values())[: n * 3]:
            ii = (pg.get('imageinfo') or [{}])[0]
            if not ii.get('mime', '').startswith('video') or len(out) >= n:
                continue
            md = ii.get('extmetadata', {})
            ext = os.path.splitext(urllib.parse.urlparse(ii['url']).path)[1] or '.webm'
            p = guarda(carpeta, f'video-commons-{pg["pageid"]}{ext}', get(ii['url'], binario=True, timeout=180))
            licencia(carpeta, p, 'Wikimedia Commons', re.sub('<[^>]+>', '', md.get('Artist', {}).get('value', '—'))[:60], md.get('LicenseShortName', {}).get('value', '—'), ii.get('descriptionurl', '')); out.append(p)
        if not out:
            print('  · Sin resultados en Wikimedia. Para más vídeos de stock pon una clave gratuita de Pexels en PEXELS_API_KEY.')
    return out


def modelo3d(q, n, carpeta):
    lista = json.loads(get('https://api.polyhaven.com/assets?t=models'))
    nombres = [k for k, v in lista.items() if q.lower() in (k + ' ' + ' '.join(v.get('tags', [])) + ' ' + v.get('name', '')).lower()][:n]
    out = []
    for k in nombres:
        f = json.loads(get(f'https://api.polyhaven.com/files/{k}'))
        g = (f.get('gltf') or {}).get('1k', {}).get('gltf')
        if not g:
            continue
        sub = os.path.join(carpeta, f'modelo-{k}'); p = guarda(sub, f'{k}.gltf', get(g['url'], binario=True))
        for rel, inc in (g.get('include') or {}).items():
            guarda(os.path.join(sub, os.path.dirname(rel)), os.path.basename(rel), get(inc['url'], binario=True, timeout=120))
        licencia(carpeta, p, 'Poly Haven', 'Poly Haven', 'CC0', f'https://polyhaven.com/a/{k}'); out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tipo', choices=['icono', 'logo', 'fuente', 'imagen', 'video', 'modelo3d'])
    ap.add_argument('busqueda')
    ap.add_argument('--n', type=int, default=4)
    ap.add_argument('--color', default='')
    ap.add_argument('--pesos', default='400,600,800')
    ap.add_argument('--carpeta', default='recursos')
    a = ap.parse_args()
    try:
        f = {'icono': lambda: icono(a.busqueda, a.n, a.color, a.carpeta), 'logo': lambda: logo(a.busqueda, a.color, a.carpeta),
             'fuente': lambda: fuente(a.busqueda, a.pesos, a.carpeta), 'imagen': lambda: imagen(a.busqueda, a.n, a.carpeta),
             'video': lambda: video(a.busqueda, a.n, a.carpeta), 'modelo3d': lambda: modelo3d(a.busqueda, a.n, a.carpeta)}[a.tipo]
        out = f()
    except Exception as e:
        sys.exit(f'No pude buscar en la nube ({e}). ¿Hay internet? Prueba otra búsqueda o pásame el archivo.')
    for p in out:
        print('✓', p)
    if not out:
        print('Sin resultados: prueba con otras palabras (en inglés suele haber más).')
    else:
        print(f'Licencias apuntadas en {os.path.join(a.carpeta, "LICENCIAS.md")}')


if __name__ == '__main__':
    main()
