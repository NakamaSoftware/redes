"""referencia.py · Motion Graphics Viegas
Analiza un vídeo de referencia y saca lo que hace falta para reproducir su movimiento con precisión:

  python referencia.py <video|url> [--salida referencia/] [--fps 30] [--desde 0 --hasta 0]

Qué mide (sin abrir el vídeo a mano):
  · planos y cortes (ritmo: cortes por segundo, duración de cada plano)
  · cámara: desplazamiento global (correlación de fase), zoom (escala entre fotogramas) y si se para en algún momento
  · cada MOVIMIENTO dentro de un plano (cuando algo arranca y se detiene) y su CURVA DE VELOCIDAD:
      lineal · entradaCubica · salidaCubica · salidaQuint · entradaSalidaQuint · salidaExpo · atras (se pasa una vez) ·
      rebote (muelle: se pasa y se asienta) · suave — con duración, pico de velocidad y error del ajuste
  · escalonado: arranques de movimientos que se suceden (stagger típico)
  · paleta (6 colores dominantes) y luminosidad
Deja en <salida>: analisis.json (todo), analisis.md (listo para el BRIEF), curvas.png (velocidad + curva ajustada de cada
movimiento) y hoja.jpg (un fotograma por plano). Con OpenCV instalado (opcional) usa flujo óptico denso, más preciso.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
try:
    import cv2  # opcional
except Exception:
    cv2 = None
from PIL import Image, ImageDraw, ImageFont

W_AN = 320  # ancho de análisis (rápido y suficiente para medir movimiento)


# ---------------------------------------------------------------- curvas candidatas (mismas que motor.js)
def muelle(a, f):
    return lambda x: np.where(x >= 1, 1.0, 1 - np.exp(-a * x) * np.cos(2 * np.pi * f * x))


CURVAS = {
    'lineal': lambda x: x,
    'suave': lambda x: x * x * (3 - 2 * x),
    'entradaCubica': lambda x: x ** 3,
    'salidaCubica': lambda x: 1 - (1 - x) ** 3,
    'salidaQuint': lambda x: 1 - (1 - x) ** 5,
    'entradaSalidaQuint': lambda x: np.where(x < .5, 16 * x ** 5, 1 - (-2 * x + 2) ** 5 / 2),
    'salidaExpo': lambda x: np.where(x >= 1, 1, 1 - 2 ** (-10 * x)),
    'atras': lambda x: 1 + 2.4 * (x - 1) ** 3 + 1.4 * (x - 1) ** 2,
    'rebote': muelle(5.5, 1.15),
    'reboteSuave': muelle(6.5, 0.95),
    'reboteFuerte': muelle(4.2, 1.6),
}
EQUIV_AE = {'lineal': 'Lineal (sin suavizado)', 'suave': 'Easy Ease 33 %', 'entradaCubica': 'Easy Ease In', 'salidaCubica': 'Easy Ease Out',
            'salidaQuint': 'Ease Out fuerte (influencia ~80 %)', 'entradaSalidaQuint': 'Easy Ease 75–90 % (curva «Apple»)', 'salidaExpo': 'Expo Out',
            'atras': 'Back Out (se pasa una vez)', 'rebote': 'Rebote natural / muelle (se pasa ~10 % y se asienta)',
            'reboteSuave': 'Muelle suave (cámara)', 'reboteFuerte': 'Muelle marcado (varias oscilaciones)'}


def ffprobe(v):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,nb_frames:format=duration',
                        '-of', 'json', v], capture_output=True, text=True)
    d = json.loads(r.stdout or '{}')
    s = (d.get('streams') or [{}])[0]
    num, den = (s.get('r_frame_rate', '30/1').split('/') + ['1'])[:2]
    return {'ancho': s.get('width'), 'alto': s.get('height'), 'fps': round(float(num) / float(den or 1), 3), 'duracion': float(d.get('format', {}).get('duration', 0))}


def fotogramas(v, fps, desde, hasta, alto):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(desde)] + (['-to', str(hasta)] if hasta else []) + ['-i', v, '-vf', f'fps={fps},scale={W_AN}:{alto}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (W_AN * alto * 3)
    return np.frombuffer(raw[:n * W_AN * alto * 3], np.uint8).reshape(n, alto, W_AN, 3)


def fase(a, b):
    """desplazamiento (dx, dy) entre dos fotogramas grises por correlación de fase, con precisión subpíxel"""
    win = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    A, B = np.fft.fft2(a * win), np.fft.fft2(b * win)
    R = A * np.conj(B); R /= np.abs(R) + 1e-9
    c = np.fft.ifft2(R).real
    y, x = np.unravel_index(np.argmax(c), c.shape)
    def sub(c0, cm, cp):
        d = cm - 2 * c0 + cp
        return 0.0 if abs(d) < 1e-9 else 0.5 * (cm - cp) / d
    h, w = c.shape
    dy = y + sub(c[y, x], c[(y - 1) % h, x], c[(y + 1) % h, x]); dx = x + sub(c[y, x], c[y, (x - 1) % w], c[y, (x + 1) % w])
    if dy > h / 2: dy -= h
    if dx > w / 2: dx -= w
    return -dx, -dy, float(c.max())


def escala(a, b):
    """zoom entre fotogramas: correlación de fase en coordenadas log-polares del espectro (Fourier-Mellin simplificado)"""
    def lp(img):
        F = np.abs(np.fft.fftshift(np.fft.fft2(img)))
        h, w = F.shape; cy, cx = h / 2, w / 2; R = min(cy, cx)
        n_r, n_t = 64, 90
        rs = np.exp(np.linspace(0, np.log(R), n_r)); ts = np.linspace(0, np.pi, n_t, endpoint=False)
        yy = (cy + rs[:, None] * np.sin(ts)[None, :]).astype(int).clip(0, h - 1); xx = (cx + rs[:, None] * np.cos(ts)[None, :]).astype(int).clip(0, w - 1)
        return np.log1p(F[yy, xx]), np.log(R) / (n_r - 1)
    la, paso = lp(a); lb, _ = lp(b)
    dx, dy, _ = fase(la, lb)
    return float(np.exp(-dx * paso)) if False else float(np.exp(dy * paso))  # eje radial = filas


def suaviza(x, n=5):
    if len(x) < n:
        return np.asarray(x, float)
    k = np.ones(n) / n
    return np.convolve(np.pad(x, (n // 2, n // 2), mode='edge'), k, mode='valid')


def ajusta(desplaz):
    """desplaz: desplazamiento acumulado normalizado (0→1, puede pasarse de 1). Devuelve la curva que mejor encaja."""
    n = len(desplaz); x = np.linspace(0, 1, n)
    res = []
    for nombre, f in CURVAS.items():
        y = np.asarray(f(x), float)
        res.append((float(np.sqrt(np.mean((y - desplaz) ** 2))), nombre))
    res.sort()
    return res


def kmeans(px, k=6, it=12):
    rng = np.random.default_rng(0); c = px[rng.choice(len(px), k, replace=False)].astype(float)
    for _ in range(it):
        d = ((px[:, None, :] - c[None, :, :]) ** 2).sum(-1); l = d.argmin(1)
        for j in range(k):
            if (l == j).any():
                c[j] = px[l == j].mean(0)
    cuenta = np.bincount(l, minlength=k)
    orden = np.argsort(-cuenta)
    return [('#%02X%02X%02X' % tuple(int(v) for v in c[j]), round(float(cuenta[j] / len(px)), 3)) for j in orden]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--salida', default='referencia')
    ap.add_argument('--fps', type=float, default=30)
    ap.add_argument('--desde', type=float, default=0)
    ap.add_argument('--hasta', type=float, default=0)
    a = ap.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    v = a.video
    if v.startswith('http'):
        # Pinterest, Instagram (reels y posts), YouTube, TikTok, Vimeo, X… con yt-dlp. Instagram a veces pide sesión:
        # se reintenta con las cookies de Chrome / Edge / Firefox del propio usuario (nunca se guardan).
        ytdlp = shutil.which('yt-dlp') or (None if not shutil.which(sys.executable) else 'py-yt-dlp')
        dst = os.path.join(a.salida, 'referencia.%(ext)s')
        base = ([sys.executable, '-m', 'yt_dlp'] if ytdlp == 'py-yt-dlp' else [ytdlp]) + ['-f', 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b', '--merge-output-format', 'mp4', '-o', dst, '--no-playlist']
        ok = subprocess.run(base + [v]).returncode == 0
        for nav in ([] if ok else ['chrome', 'edge', 'firefox']):
            print(f'· Reintentando con la sesión de {nav} (Instagram y Pinterest privados la piden)…')
            if subprocess.run(base + ['--cookies-from-browser', nav, v]).returncode == 0:
                ok = True; break
        if not ok:
            sys.exit('No pude descargar el vídeo. Instala yt-dlp (python -m pip install yt-dlp) o descárgalo y pásame el archivo.')
        v = os.path.join(a.salida, 'referencia.mp4')
    info = ffprobe(v)
    alto = int(round(W_AN * info['alto'] / info['ancho'] / 2) * 2)
    F = fotogramas(v, a.fps, a.desde, a.hasta, alto)
    if len(F) < 3:
        sys.exit('No pude leer fotogramas del vídeo.')
    gris = F.mean(-1).astype(np.float32) / 255
    dt = 1 / a.fps
    n = len(gris)

    # 1) cortes: diferencia de histograma y de imagen muy por encima de lo normal
    hist = np.array([np.histogram(g, 32, (0, 1))[0] for g in gris], float)
    dh = np.r_[0, np.abs(np.diff(hist, axis=0)).sum(1) / hist[0].sum()]
    dimg = np.r_[0, np.abs(np.diff(gris, axis=0)).mean((1, 2))]
    umbral = max(0.35, np.median(dh) + 6 * np.std(dh))
    cortes = [i for i in range(1, n) if dh[i] > umbral and dimg[i] > max(0.08, np.median(dimg) * 5)]
    limites = [0] + cortes + [n]
    planos = [(limites[i], limites[i + 1]) for i in range(len(limites) - 1) if limites[i + 1] - limites[i] >= 3]

    # 2) movimiento por plano: cámara global (fase + zoom) y movimiento local (energía tras compensar)
    vx, vy, zoom, local = np.zeros(n), np.zeros(n), np.ones(n), np.zeros(n)
    for (i0, i1) in planos:
        for i in range(i0 + 1, i1):
            if cv2 is not None:
                fl = cv2.calcOpticalFlowFarneback((gris[i - 1] * 255).astype(np.uint8), (gris[i] * 255).astype(np.uint8), None, 0.5, 3, 15, 3, 5, 1.2, 0)
                vx[i], vy[i] = np.median(fl[..., 0]), np.median(fl[..., 1])
                gx = np.gradient(fl[..., 0], axis=1); gy = np.gradient(fl[..., 1], axis=0)
                zoom[i] = 1 + float(np.median(gx + gy)) / 2
                local[i] = float(np.percentile(np.hypot(fl[..., 0] - vx[i], fl[..., 1] - vy[i]), 95))
            else:
                dx, dy, _ = fase(gris[i - 1], gris[i]); vx[i], vy[i] = dx, dy
                try:
                    zoom[i] = escala(gris[i - 1], gris[i])
                except Exception:
                    zoom[i] = 1
                sh = np.roll(np.roll(gris[i - 1], int(round(dy)), 0), int(round(dx)), 1)
                local[i] = float(np.percentile(np.abs(gris[i] - sh), 99)) * 40
    esc = info['ancho'] / W_AN  # px del vídeo original por px de análisis
    vel_cam = np.hypot(vx, vy) * esc / dt                     # px/s en el tamaño original
    vel_zoom = np.abs(np.log(np.clip(zoom, 0.5, 2))) / dt       # «velocidad» de zoom
    quieto = (vel_cam < 3) & (vel_zoom < 0.01)
    for c in cortes:
        quieto[c] = False

    # 3) movimientos. Por plano se elige el modo:
    #    · «cámara» si todo el fotograma se desplaza (correlación de fase global)
    #    · «elemento» si el fondo está quieto: se separa el fondo (mediana del plano) y se sigue el centro y el tamaño de lo que se mueve
    #    Cada movimiento se toma con histéresis: núcleo por encima del 25 % de su pico y se extiende mientras la velocidad > 3 % del pico,
    #    uniendo huecos de < 0,15 s. Así un ease in-out (lento al principio y al final) sale entero y no partido.
    movs = []
    def tramos(vel):
        out = []; n_ = len(vel); pico_g = vel.max() if n_ else 0
        if pico_g <= 0: return out
        nucleo = vel > 0.25 * pico_g; j = 0
        while j < n_:
            if nucleo[j]:
                k = j
                while k < n_ and nucleo[k]: k += 1
                pk = vel[j:k].max(); a0, a1 = j, k
                while a0 > 0 and vel[a0 - 1] > 0.01 * pk: a0 -= 1
                # el final es cuando el elemento se ASIENTA: en los 0,3 s siguientes la velocidad no vuelve a pasar del 2 % del pico
                # (así un rebote, que se para un instante en el punto de giro, no se corta)
                ven = max(2, int(0.3 / dt))
                while a1 < n_ and vel[a1:a1 + ven].max() > 0.02 * pk: a1 += 1
                if out and a0 - out[-1][1] <= max(1, int(0.15 / dt)): out[-1] = (out[-1][0], max(out[-1][1], a1))
                else: out.append((a0, a1))
                j = max(k, a1)
            else: j += 1
        return [(x0, x1) for x0, x1 in out if x1 - x0 >= 3]
    for pi, (i0, i1) in enumerate(planos, 1):
        g = gris[i0:i1]
        cam_px = np.hypot(vx[i0:i1], vy[i0:i1])
        modo = 'cámara' if np.median(cam_px[1:]) > 0.35 else 'elemento'
        if modo == 'elemento':
            fondo = np.median(g, axis=0)
            m = np.abs(g - fondo) > 0.08
            yy, xx = np.mgrid[0:g.shape[1], 0:g.shape[2]]
            area = m.sum((1, 2)).astype(float)
            cx = np.where(area > 0, (m * xx).sum((1, 2)) / np.maximum(area, 1), np.nan); cy = np.where(area > 0, (m * yy).sum((1, 2)) / np.maximum(area, 1), np.nan)
            cx = np.nan_to_num(cx, nan=np.nanmean(cx) if np.isfinite(cx).any() else 0); cy = np.nan_to_num(cy, nan=np.nanmean(cy) if np.isfinite(cy).any() else 0)
            px_, py_ = cx * esc, cy * esc                       # posición del elemento en px del vídeo original
            tam = np.sqrt(np.maximum(area, 1)) * esc            # tamaño (para entradas por escala)
            vxe, vye = np.r_[0, np.diff(px_)], np.r_[0, np.diff(py_)]
            vtam = np.r_[0, np.diff(tam)]
            vel = suaviza(np.hypot(vxe, vye) + np.abs(vtam) * 0.5, 3) / dt
            pos = np.stack([px_, py_, tam], 1)
        else:
            vxe, vye = vx[i0:i1] * esc, vy[i0:i1] * esc
            vel = suaviza(np.hypot(vxe, vye), 3) / dt + np.abs(np.log(np.clip(zoom[i0:i1], .5, 2))) / dt * 400
            pos = np.stack([np.cumsum(vxe), np.cumsum(vye), np.cumsum(np.log(np.clip(zoom[i0:i1], .5, 2))) * 400], 1)
        for a0, a1 in tramos(vel):
            b0 = max(0, a0 - 1); b1 = min(len(vel) - 1, a1)
            # se toma el final cuando el elemento ya se ha asentado (incluye el rebote)
            p0, pf = pos[b0], pos[b1]
            dvec = pf - p0; L_ = np.linalg.norm(dvec[:2]) if np.linalg.norm(dvec[:2]) > 1 else np.linalg.norm(dvec)
            if L_ < 1: continue
            u = dvec / np.linalg.norm(dvec)
            desplaz = ((pos[b0:b1 + 1] - p0) @ u) / np.linalg.norm(dvec)
            ranking = ajusta(desplaz)
            seg_v = vel[b0:b1 + 1]
            movs.append({'plano': pi, 'inicio_s': round((i0 + b0) * dt + a.desde, 3), 'fin_s': round((i0 + b1) * dt + a.desde, 3),
                         'duracion_s': round((b1 - b0) * dt, 3), 'tipo': modo, 'curva': ranking[0][1], 'equivalente_ae': EQUIV_AE[ranking[0][1]],
                         'error': round(ranking[0][0], 3), 'alternativas': [r[1] for r in ranking[1:3]],
                         'pico_velocidad_en': round(int(np.argmax(seg_v)) / max(1, len(seg_v) - 1), 2),
                         'se_pasa_pct': round(max(0.0, float(desplaz.max() - 1)) * 100, 1), 'velocidad_max_px_s': round(float(seg_v.max()), 1),
                         'recorrido_px': round(float(np.linalg.norm(dvec[:2])), 1),
                         '_v': [round(float(x), 3) for x in seg_v], '_d': [round(float(x), 4) for x in desplaz]})

    # 4) escalonado: separación entre arranques de movimientos cercanos del mismo plano
    stag = []
    for p in set(m['plano'] for m in movs):
        ini = sorted(m['inicio_s'] for m in movs if m['plano'] == p)
        stag += [round(b - a_, 3) for a_, b in zip(ini, ini[1:]) if 0.02 < b - a_ < 0.6]

    # 5) paleta y luminosidad
    muestra = F[:: max(1, n // 24)].reshape(-1, 3)[:: 7]
    paleta = kmeans(muestra.astype(float), 6)
    lum = float(gris.mean())

    # 6) resumen
    from collections import Counter
    cnt = Counter(m['curva'] for m in movs)
    dur_planos = [round((b - a_) * dt, 2) for a_, b in planos]
    res = {
        'video': os.path.abspath(v), 'info': info, 'analizado_fps': a.fps, 'metodo': 'flujo óptico (OpenCV)' if cv2 is not None else 'correlación de fase (numpy)',
        'planos': len(planos), 'cortes_s': [round(c * dt + a.desde, 3) for c in cortes], 'duracion_planos_s': dur_planos,
        'ritmo_cortes_por_s': round(len(cortes) / max(0.1, n * dt), 3),
        'camara': {'tiempo_quieta_pct': round(100 * float(quieto[1:].mean()), 1), 'velocidad_media_px_s': round(float(vel_cam[1:].mean()), 1),
                   'zoom_total_pct': round(100 * (float(np.prod(np.clip(zoom[1:], .8, 1.25))) - 1), 1)},
        'movimientos': [{k_: v_ for k_, v_ in m.items() if not k_.startswith('_')} for m in movs],
        'curvas_mas_usadas': cnt.most_common(),
        'duracion_media_movimiento_s': round(float(np.mean([m['duracion_s'] for m in movs])), 3) if movs else None,
        'escalonado_tipico_s': round(float(np.median(stag)), 3) if stag else None,
        'paleta': paleta, 'luminosidad_media': round(lum, 3),
    }
    json.dump(res, open(os.path.join(a.salida, 'analisis.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # curvas.png: velocidad (gris) y desplazamiento real (blanco) vs curva ajustada (coral) de cada movimiento
    if movs:
        cols = 4; filas = math.ceil(min(len(movs), 16) / cols); cw, chh = 360, 220
        img = Image.new('RGB', (cols * cw, filas * chh), (13, 12, 15)); dr = ImageDraw.Draw(img)
        try:
            fnt = ImageFont.truetype('arial.ttf', 15)
        except Exception:
            fnt = ImageFont.load_default()
        for idx, m in enumerate(movs[:16]):
            ox, oy = (idx % cols) * cw, (idx // cols) * chh; x0, y0, w, h = ox + 20, oy + 40, cw - 40, chh - 70
            dr.rectangle([x0, y0, x0 + w, y0 + h], outline=(40, 38, 44))
            d = np.array(m['_d']); vv = np.array(m['_v']); xs = np.linspace(0, 1, len(d))
            ymax = max(1.15, d.max() + .05)
            pt = lambda xx, yy: (x0 + xx * w, y0 + h - (yy / ymax) * h)
            if vv.max() > 0:
                dr.line([pt(xx, yy / vv.max()) for xx, yy in zip(xs, vv)], fill=(110, 105, 100), width=1)
            fy = np.asarray(CURVAS[m['curva']](np.linspace(0, 1, 60)), float)
            dr.line([pt(xx, yy) for xx, yy in zip(np.linspace(0, 1, 60), fy)], fill=(217, 119, 87), width=3)
            dr.line([pt(xx, yy) for xx, yy in zip(xs, d)], fill=(244, 242, 238), width=2)
            dr.line([pt(0, 1), pt(1, 1)], fill=(60, 56, 62))
            dr.text((ox + 20, oy + 10), f"#{idx + 1} {m['inicio_s']}s · {m['duracion_s']}s · {m['curva']}", fill=(244, 242, 238), font=fnt)
        img.save(os.path.join(a.salida, 'curvas.png'))
    # hoja.jpg: un fotograma del centro de cada plano
    tiles = [Image.fromarray(F[(p0 + p1) // 2]) for p0, p1 in planos[:16]] or [Image.fromarray(F[n // 2])]
    cols = min(4, len(tiles)); hoja = Image.new('RGB', (cols * W_AN, math.ceil(len(tiles) / cols) * alto), (0, 0, 0))
    for i, t in enumerate(tiles):
        hoja.paste(t, ((i % cols) * W_AN, (i // cols) * alto))
    hoja.save(os.path.join(a.salida, 'hoja.jpg'), quality=88)

    # analisis.md
    L = [f"# Análisis de la referencia · {os.path.basename(v)}", '',
         f"- {info['ancho']}×{info['alto']} · {info['fps']} fps · {info['duracion']:.2f} s · método: {res['metodo']}",
         f"- **Planos:** {len(planos)} · cortes por segundo: {res['ritmo_cortes_por_s']} · duración de los planos: {dur_planos}",
         f"- **Cámara:** quieta el {res['camara']['tiempo_quieta_pct']} % del tiempo · velocidad media {res['camara']['velocidad_media_px_s']} px/s · zoom total {res['camara']['zoom_total_pct']} %",
         f"- **Movimientos detectados:** {len(movs)} · duración media {res['duracion_media_movimiento_s']} s · escalonado típico {res['escalonado_tipico_s']} s",
         f"- **Curvas más usadas:** " + ', '.join(f'{c} ({k_})' for c, k_ in cnt.most_common()),
         f"- **Paleta:** " + ' '.join(f'`{c}` {int(p * 100)} %' for c, p in paleta), '',
         '| # | Plano | Inicio | Duración | Tipo | Curva (motor.js) | Equivalente en After Effects | Pico de velocidad | Se pasa | Error |', '|---|---|---|---|---|---|---|---|---|---|']
    for i, m in enumerate(movs, 1):
        L.append(f"| {i} | {m['plano']} | {m['inicio_s']} s | {m['duracion_s']} s | {m['tipo']} | `{m['curva']}` | {m['equivalente_ae']} | {int(m['pico_velocidad_en'] * 100)} % | {m['se_pasa_pct']} % | {m['error']} |")
    L += ['', 'Cómo leerlo: «pico de velocidad» cerca de 0 % = arranca de golpe y frena (ease out); en el 50 % = ease in-out; cerca del 100 % = acelera (ease in).',
          '«Se pasa» > 3 % = hay rebote o «back»: úsalo igual en la animación. Error < 0,05 = ajuste muy fiable; > 0,12 = mira la gráfica (curvas.png).']
    open(os.path.join(a.salida, 'analisis.md'), 'w', encoding='utf-8').write('\n'.join(L))
    print('\n'.join(L[:8]))
    print(f'\n✓ {a.salida}/analisis.md · analisis.json · curvas.png · hoja.jpg')


if __name__ == '__main__':
    main()
