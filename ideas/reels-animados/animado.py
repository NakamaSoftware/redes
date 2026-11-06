# Reels animados sin cara, con la marca de marca/marca.md (variante «Pasos»: papel crema, Instrument Serif, ventanas de chat).
# Uso: python3 animado.py <guion.py> <salida.mp4>
#   <guion.py> define ESCENAS (lista de dicts) y SONIDOS opcionales; ver guiones/*.py
# Escenas: gancho / frase (texto serif), pedido (ventana de chat con lo que escribís + leyenda), chat (pedido + respuesta),
#          cortinilla (rojo con el número del paso), cierre (texto + palabra en caja roja + @pvmr.dev)
import sys, math, subprocess, json, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = '/home/user/redes/marca/fuentes/'
NOCHE, CREMA, BLANCO, ROJO, GRIS, GRIS2 = (20, 24, 22), (245, 241, 232), (255, 255, 255), (168, 64, 44), (95, 99, 104), (238, 234, 226)
W, H, FPS = 1080, 1920, 30
def inter(px, w): f = ImageFont.truetype(F + 'Inter.ttf', px); f.set_variation_by_axes([w]); return f
def mono(px, w=600): f = ImageFont.truetype(F + 'JetBrainsMono.ttf', px); f.set_variation_by_axes([w]); return f
SER = lambda px: ImageFont.truetype(F + 'InstrumentSerif-Regular.ttf', px)
SERI = lambda px: ImageFont.truetype(F + 'InstrumentSerif-Italic.ttf', px)
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def eb(x):
    x = max(0., min(1., x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def papel():
    im = Image.new('RGB', (W, H), CREMA); g = ImageDraw.Draw(im)
    for x in range(0, W, 40): g.line([(x, 0), (x, H)], fill=(236, 230, 218))
    for y in range(0, H, 40): g.line([(0, y), (W, y)], fill=(236, 230, 218))
    return im.convert('RGBA')
def ficha_logo(lado=84):
    t = Image.new('RGBA', (lado, lado), (0, 0, 0, 0)); g = ImageDraw.Draw(t); g.rounded_rectangle([0, 0, lado - 1, lado - 1], 16, fill=CREMA)
    S = (lado - 20) / 24
    for x, y, w, h in ((0, 0, 14.1, 8.1), (15.9, 0, 8.1, 14.1), (9.9, 15.9, 14.1, 8.1), (0, 9.9, 8.1, 14.1)):
        g.rectangle([10 + x * S, 10 + y * S, 10 + (x + w) * S - 1, 10 + (y + h) * S - 1], fill=BLANCO, outline=(214, 204, 186), width=2)
    g.rectangle([10 + 10.3 * S, 10 + 10.3 * S, 10 + 13.7 * S - 1, 10 + 13.7 * S - 1], fill=ROJO)
    out = Image.new('RGBA', (lado + 40, lado + 40), (0, 0, 0, 0)); s = Image.new('RGBA', out.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([20, 24, 20 + lado, 24 + lado], 16, fill=(0, 0, 0, 70)); out.alpha_composite(s.filter(ImageFilter.GaussianBlur(8))); out.alpha_composite(t, (20, 20))
    return out
FONDO, LOGO = papel(), ficha_logo()

def sombra_caja(base, caja, r, a=70, dy=16, blur=26):
    s = Image.new('RGBA', base.size, (0, 0, 0, 0)); ImageDraw.Draw(s).rounded_rectangle([caja[0], caja[1] + dy, caja[2], caja[3] + dy], r, fill=(60, 50, 40, a))
    base.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))

# --- texto serif por palabras: «linea» es una lista de (texto, cursiva_roja)
def palabras(lineas, px, x0, y0, alto, centro=False):
    out = []
    for i, linea in enumerate(lineas):
        piezas = []  # (palabra, cursiva, va pegada a la anterior): la puntuación suelta («,» «?») no lleva espacio antes
        for txt, cur in linea:
            for k, w in enumerate(txt.split(' ')):
                if not w: continue
                piezas.append((w, cur, k == 0 and bool(piezas) and not txt.startswith(' ') and w[0] in ',.;:?!)»'))
        f = lambda c: SERI(px) if c else SER(px)
        esp = SER(px).getlength(' ')
        ancho = sum(f(c).getlength(w) for w, c, _ in piezas) + esp * sum(1 for _, _, p in piezas[1:] if not p)
        x = (W - ancho) / 2 if centro else x0
        for j, (w, c, pegada) in enumerate(piezas):
            if pegada: x -= esp
            fo = f(c); a = fo.getbbox(w); lw, lh = int(fo.getlength(w)) + 20, px + 60
            img = Image.new('RGBA', (lw, lh), (0, 0, 0, 0)); ImageDraw.Draw(img).text((10, px + 10), w, font=fo, fill=ROJO if c else NOCHE, anchor='ls')
            out.append((img, int(x) - 10, int(y0 + i * alto) - px - 10)); x += fo.getlength(w) + esp
    return out
def pone_palabras(im, pz, t, t0, paso=0.06, dur=0.45):
    for k, (img, x, y) in enumerate(pz):
        u = (t - t0 - k * paso) / dur
        if u <= 0: continue
        a = eo(u); c = img
        if a < 1:
            c = img.filter(ImageFilter.GaussianBlur(10 * (1 - a))); c.putalpha(c.split()[3].point(lambda p: int(p * a)))
        im.alpha_composite(c, (x, int(y + 34 * (1 - a))))

def envolver(texto, fo, ancho):
    out, l = [], ''
    for w in texto.split(' '):
        p = (l + ' ' + w).strip()
        if fo.getlength(p) > ancho and l: out.append(l); l = w
        else: l = p
    if l: out.append(l)
    return out

def etiqueta(im, txt, a=1.0):
    if not txt: return
    c = Image.new('RGBA', (W, 80), (0, 0, 0, 0)); g = ImageDraw.Draw(c)
    g.rectangle([110, 24, 126, 40], fill=ROJO); g.text((142, 42), txt, font=mono(30), fill=GRIS, anchor='ls')
    if a < 1: c.putalpha(c.split()[3].point(lambda p: int(p * a)))
    im.alpha_composite(c, (0, 262))

# --- ventana de chat: lo que escribís (burbuja roja que se escribe sola) y la respuesta
VX0, VX1 = 90, 930
def ventana(im, y0, alto, titulo='ChatGPT'):
    caja = (VX0, y0, VX1, y0 + alto); sombra_caja(im, caja, 30); g = ImageDraw.Draw(im)
    g.rounded_rectangle(caja, 30, fill=BLANCO)
    for i, col in enumerate(((236, 106, 94), (245, 190, 79), (98, 197, 84))): g.ellipse([VX0 + 30 + i * 32, y0 + 28, VX0 + 50 + i * 32, y0 + 48], fill=col)
    g.text(((VX0 + VX1) / 2, y0 + 48), titulo, font=inter(28, 600), fill=GRIS, anchor='ms'); g.line([(VX0, y0 + 76), (VX1, y0 + 76)], fill=(232, 228, 220), width=2)
def burbuja(im, lineas, fo, x, y, derecha, fondo, color, s=1.0, alto_l=54):
    w = max(fo.getlength(l) for l in lineas) + 64; h = alto_l * len(lineas) + 34
    b = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0)); g = ImageDraw.Draw(b); g.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=fondo)
    for i, l in enumerate(lineas): g.text((32, 54 + i * alto_l - 6), l, font=fo, fill=color, anchor='ls')
    if s < 1:
        b = b.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
    bx = x - b.width if derecha else x
    im.alpha_composite(b, (int(bx), int(y + h * (1 - s) / 2)))
    return h
def puntitos(im, x, y, t):
    g = ImageDraw.Draw(im); g.rounded_rectangle([x, y, x + 130, y + 70], 30, fill=GRIS2)
    for i in range(3):
        a = 0.5 + 0.5 * math.sin(t * 12 - i * 1.1); g.ellipse([x + 32 + i * 28, y + 27 - 6 * a, x + 48 + i * 28, y + 43 - 6 * a], fill=GRIS)

def leyenda(im, txt, clave, y, a):
    if a <= 0: return
    fo = inter(54, 800); c = Image.new('RGBA', (W, 240), (0, 0, 0, 0)); g = ImageDraw.Draw(c)
    lineas = envolver(txt, fo, 820)
    for i, l in enumerate(lineas):
        x = 110
        for w in l.split(' '):
            col = ROJO if clave and w.strip('.,:;').lower() in clave else NOCHE
            g.text((x, 60 + i * 66), w, font=fo, fill=col, anchor='ls'); x += fo.getlength(w + ' ')
    c.putalpha(c.split()[3].point(lambda p: int(p * a))); im.alpha_composite(c, (0, int(y + 20 * (1 - a))))

# --- respuestas dibujadas (sin inventar contenido): renglones grises, lista numerada o tabla
def resp_renglones(im, x, y, n, a, numerada=False):
    g = ImageDraw.Draw(im); w = 560; h = 40 + n * 56
    caja = Image.new('RGBA', (w, h), (0, 0, 0, 0)); gc = ImageDraw.Draw(caja); gc.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=GRIS2)
    for i in range(n):
        yy = 28 + i * 56; x0 = 32
        if numerada: gc.text((32, yy + 26), f'{i + 1}.', font=inter(34, 800), fill=ROJO, anchor='ls'); x0 = 80
        gc.rounded_rectangle([x0, yy + 6, w - 40 - (i * 37 % 120), yy + 28], 11, fill=(212, 206, 196))
    caja.putalpha(caja.split()[3].point(lambda p: int(p * a))); im.alpha_composite(caja, (x, int(y + 20 * (1 - a))))
def resp_tabla(im, x, y, a, cols=('Producto', 'Cant.', 'Precio'), filas=4):
    w, fh = 620, 62; h = fh * (filas + 1) + 30
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); g = ImageDraw.Draw(c); g.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=GRIS2)
    cx = [24, 300, 440]
    for j, col in enumerate(cols): g.text((cx[j] + 10, 15 + 42), col, font=inter(30, 800), fill=NOCHE, anchor='ls')
    for i in range(filas):
        yy = 15 + fh * (i + 1); g.line([(20, yy), (w - 20, yy)], fill=(214, 206, 194), width=2)
        if a > (i + 1) / (filas + 1):
            for j, ww in enumerate((200 - i * 23 % 70, 60, 100)): g.rounded_rectangle([cx[j] + 10, yy + 20, cx[j] + 10 + ww, yy + 42], 10, fill=(206, 198, 186))
    c.putalpha(c.split()[3].point(lambda p: int(p * min(1, a * 3)))); im.alpha_composite(c, (x, y))
def foto_papel(im, x, y, w, h, a=1.0, flash=0.0):
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); g = ImageDraw.Draw(c)
    g.rounded_rectangle([0, 0, w - 1, h - 1], 18, fill=(250, 247, 236), outline=(214, 206, 194), width=3)
    for i in range(7):
        yy = 40 + i * (h - 60) // 7; g.line([(20, yy), (w - 20, yy)], fill=(170, 190, 215), width=2)
        if i: g.line([(30, yy - 12), (30 + (w - 90) * (0.4 + 0.35 * math.sin(i * 2.3)), yy - 12)], fill=(70, 80, 120), width=4)
    if flash > 0: g.rectangle([0, 0, w, h], fill=(255, 255, 255, int(220 * flash)))
    c.putalpha(c.split()[3].point(lambda p: int(p * a))); im.alpha_composite(c, (x, y))

# ---------- escenas ----------
def escena_texto(e, im, t):
    etiqueta(im, e.get('etiqueta'), eo(t / 0.3))
    pone_palabras(im, e['_pz'], t, 0.15)
    if e.get('chico'):
        a = eo((t - e.get('chico_t', 1.0)) / 0.4)
        if a > 0:
            fo = inter(44, 700); ls = envolver(e['chico'], fo, 840); g = ImageDraw.Draw(im)
            c = Image.new('RGBA', (W, 70 * len(ls) + 20), (0, 0, 0, 0)); gc = ImageDraw.Draw(c)
            for i, l in enumerate(ls): gc.text((110, 54 + i * 62), l, font=fo, fill=GRIS, anchor='ls')
            c.putalpha(c.split()[3].point(lambda p: int(p * a))); im.alpha_composite(c, (0, int(e['_ychico'] + 16 * (1 - a))))
def prepara_texto(e):
    px = e.get('px', 110); alto = int(px * 1.08); n = len(e['lineas'])
    y0 = e.get('y', 880 - (n - 1) * alto // 2 + px // 2)
    e['_pz'] = palabras(e['lineas'], px, 110, y0, alto, e.get('centro', False)); e['_ychico'] = y0 + (n - 1) * alto + 50

def escena_chat(e, im, t):
    y0 = e.get('y', 600); alto = e.get('alto', 720)
    e['_t_envio'] = e.get('t_escribe', 0.5) + len(e['pedido']) / e.get('vel', 32)
    a = eo(t / 0.35)
    if a < 1:
        tmp = Image.new('RGBA', im.size, (0, 0, 0, 0)); ventana(tmp, y0, alto, e.get('titulo', 'ChatGPT'))
        tmp.putalpha(tmp.split()[3].point(lambda p: int(p * a))); im.alpha_composite(tmp, (0, int(60 * (1 - a))))
        etiqueta(im, e.get('etiqueta'), a); return
    ventana(im, y0, alto, e.get('titulo', 'ChatGPT')); etiqueta(im, e.get('etiqueta'))
    fo = inter(40, 650); yb = y0 + 110
    if e.get('foto'):  # la foto adjunta, a la derecha
        fa = eo((t - 0.4) / 0.35)
        if fa > 0: foto_papel(im, VX1 - 30 - 220, yb, 220, 280, fa, flash=max(0, 1 - (t - 0.4) / 0.3) if t > 0.4 else 0); 
        yb += 300
    t_esc = e.get('t_escribe', 0.5); vel = e.get('vel', 32)  # letras por segundo
    texto = e['pedido']; n = int(max(0, (t - t_esc)) * vel); parcial = texto[:n]
    if n > 0:
        cursor = '|' if n < len(texto) and int(t * 4) % 2 == 0 else ''
        ls = envolver(parcial + cursor, fo, 580) if parcial else ['|']
        h = burbuja(im, ls, fo, VX1 - 30, yb, True, ROJO, BLANCO)
        yb += h + 26
    t_fin = t_esc + len(texto) / vel; e['_t_envio'] = t_fin
    r = e.get('respuesta')
    if r is None: return
    tr = t_fin + 0.3
    if tr < t < tr + 0.7: puntitos(im, VX0 + 30, yb, t)
    elif t >= tr + 0.7:
        u = (t - tr - 0.7) / 0.35
        if r == 'renglones': resp_renglones(im, VX0 + 30, yb, e.get('n', 3), eo(u), e.get('numerada', False))
        elif r == 'tabla': resp_tabla(im, VX0 + 30, yb, eo((t - tr - 0.7) / 1.2))
        else: burbuja(im, envolver(r, fo, 580), fo, VX0 + 30, yb, False, GRIS2, NOCHE, s=eb(u))
    if e.get('sello') and t > tr + 1.4:  # un sello rojo en diagonal
        u = eb((t - tr - 1.4) / 0.3); fo = inter(54, 900); sw = int(fo.getlength(e['sello'])) + 80
        s = Image.new('RGBA', (sw, 140), (0, 0, 0, 0)); g = ImageDraw.Draw(s)
        g.rounded_rectangle([4, 4, sw - 5, 135], 18, outline=ROJO, width=8); g.text((sw // 2, 90), e['sello'], font=fo, fill=ROJO, anchor='ms')
        s = s.rotate(-6, expand=True, resample=Image.BICUBIC); s = s.resize((max(1, int(s.width * u)), max(1, int(s.height * u))))
        im.alpha_composite(s, (int(510 - s.width / 2), int(yb + 230 - s.height / 2)))
def escena_pedido(e, im, t):
    escena_chat(e, im, t)
    if e.get('leyenda'): leyenda(im, e['leyenda'], e.get('clave'), e.get('y', 600) + e.get('alto', 720) + 60, eo((t - e['_t_envio'] - 0.3) / 0.4))
def escena_cortinilla(e, im, t):
    im.paste(ROJO + (255,), (0, 0, W, H)); g = ImageDraw.Draw(im)
    g.text((540, 820), 'PASO ' + e['n'], font=mono(40), fill=(245, 225, 215), anchor='ms')
    a = eb(t / 0.35); fo = SER(int(420 * (0.8 + 0.2 * a))); g.text((540, 1180), e['n'], font=fo, fill=BLANCO, anchor='ms')
def escena_cierre(e, im, t):
    escena_texto(e, im, t)
    u = eb((t - e.get('caja_t', 1.2)) / 0.35)
    if u > 0:
        fo = inter(96, 900); w = fo.getlength(e['caja']) + 60
        c = Image.new('RGBA', (int(w), 150), (0, 0, 0, 0)); g = ImageDraw.Draw(c); g.rounded_rectangle([0, 0, w - 1, 149], 22, fill=ROJO); g.text((30, 112), e['caja'], font=fo, fill=BLANCO, anchor='ls')
        c = c.resize((max(1, int(c.width * u)), max(1, int(c.height * u))))
        im.alpha_composite(c, (int(110), int(e['_ychico'] + 40)))
    a = eo((t - e.get('caja_t', 1.2) - 0.3) / 0.4)
    if a > 0: ImageDraw.Draw(im).text((110, e['_ychico'] + 280), '@pvmr.dev', font=inter(40, 700), fill=GRIS + (int(255 * a),), anchor='ls')
TIPOS = {'gancho': escena_texto, 'frase': escena_texto, 'chat': escena_chat, 'pedido': escena_pedido, 'cortinilla': escena_cortinilla, 'cierre': escena_cierre}

def render(escenas, salida_video):
    for e in escenas:
        if 'lineas' in e: prepara_texto(e)
    total = sum(e['dur'] for e in escenas)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', salida_video], stdin=subprocess.PIPE)
    t0, eventos = 0.0, []
    for e in escenas:
        n = int(round(e['dur'] * FPS))
        for k in range(n):
            t = k / FPS; im = FONDO.copy(); TIPOS[e['tipo']](e, im, t)
            if e['tipo'] != 'cortinilla': im.alpha_composite(LOGO, (840, 212))
            fuera = e['dur'] - t
            if fuera < 0.2 and e['tipo'] != 'cortinilla':  # se aclara hacia el papel en los últimos 0,2 s
                im = Image.blend(im, FONDO, (0.2 - fuera) / 0.2 * 0.85)
            p.stdin.write(im.convert('RGB').tobytes())
        # sonidos de la escena
        if e['tipo'] == 'cortinilla': eventos.append(('whoosh-short', t0, -8))
        elif e['tipo'] in ('chat', 'pedido'):
            eventos.append(('whoosh-short', t0 + 0.05, -11))
            if e.get('foto'): eventos.append(('click', t0 + 0.4, -10))
            eventos.append(('click-soft', t0 + e['_t_envio'], -10))
            if e.get('respuesta') is not None: eventos.append(('pop', t0 + e['_t_envio'] + 1.0, -9))
            if e.get('sello'): eventos.append(('pop', t0 + e['_t_envio'] + 1.7, -7))
        elif e['tipo'] == 'cierre': eventos.append(('pop', t0 + e.get('caja_t', 1.2), -9))
        t0 += e['dur']
    p.stdin.close(); p.wait()
    return total, eventos

def mezcla(video, total, eventos, salida):
    X = '/root/.claude/skills/media-use/audio/assets/sfx/'; M = '/home/user/redes/2026-10/reel-3-preguntas/musica-synthwave.wav'
    ins = ['-i', video, '-i', M]; fc = [f'[1:a]atrim=0:{total},asetpts=PTS-STARTPTS,volume=-6dB,afade=in:d=0.4,afade=out:st={total - 1}:d=1[m]']; lb = '[m]'
    for i, (s, t, db) in enumerate(eventos):
        ins += ['-i', X + s + '.mp3']; fc.append(f'[{i + 2}:a]loudnorm=I=-16:TP=-1,aresample=48000,adelay={int(t * 1000)}:all=1,volume={db}dB[s{i}]'); lb += f'[s{i}]'
    fc.append(f'{lb}amix=inputs={len(eventos) + 1}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[a]', '-t', str(total), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', salida], check=True)

if __name__ == '__main__':
    g = {}; exec(open(sys.argv[1]).read(), g)
    tmp = sys.argv[2] + '.solo.mp4'; total, ev = render(g['ESCENAS'], tmp); mezcla(tmp, total, ev, sys.argv[2]); os.remove(tmp)
    print(f'{sys.argv[2]}: {total:.1f} s, {len(ev)} sonidos')
