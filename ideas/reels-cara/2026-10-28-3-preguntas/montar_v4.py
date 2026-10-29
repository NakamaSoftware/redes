# Montaje v4 del reel «ChatGPT te puede hacer preguntas a vos»: look C claro de marca.md + efectos del reel de ejemplo
# (contador arriba, palabra detrás de la cabeza, prompt que se escribe, pantalla completa «al revés», zoom de golpe,
# pastillas en arco alrededor de la cabeza, íconos de mail y avión, cierre con el logo). Sin la mano que va al celular.
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W0 = os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(W0, 'trabajo', 'v4'))
F = '/home/user/redes/marca/fuentes/'
SFX = '/root/.claude/skills/media-use/audio/assets/sfx/'
NOCHE, CREMA, BLANCO, ROJO = (20, 24, 22), (245, 241, 232), (255, 255, 255), (168, 64, 44)
FPS, GANANCIA = 30, float(sys.argv[1]) if len(sys.argv) > 1 else 19.0
SOLO = sys.argv[2] if len(sys.argv) > 2 else ''
MUSICA = os.environ.get('MUSICA', '')                       # archivo de música de fondo (opcional)          # «fotos»: solo fotogramas de control, sin exportar
C = json.load(open('cortes.json')); ini, DUR = C['ini'], C['duracion']
COLA = 1.3; TOTAL = DUR + COLA                            # el cierre se queda 1,3 s después de la última palabra

BLOQUES_TXT = [
    ['·ChatGPT te puede hacer preguntas a vos.', 'Eso casi *nadie*', 'lo usa.'],
    ['Pasa siempre que te escribís', '10 cosas en *10 líneas,*', 'te olvidaste de un solo *dato*', 'y ya *inventa*', 'ese dato y te responde', '*cualquier cosa.*'],
    ['·Probá al revés.'],
    ['Contale lo que querés', 'en una sola *línea*', 'y al terminar decile:'],
    ['Preguntame *tres cosas*', 'de lo que te quedó *duda.*'],
    ['Te pregunta lo que', 'capaz que pasaste por *alto*', 'o te olvidaste de *preguntar,*', 'y *listo.*', 'Le contestás', 'en base a eso.'],
    ['Sirve para un *mail*', 'difícil o para un *viaje*', 'de cuatro días.'],
    ['*Guardalo*', 'y probá hoy con *ChatGPT.*'],
]

# ---------- tiempos de palabras: se reparten sobre los tramos con voz de cada plano
def voz_activa(n):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{n}.mov', '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768; w = 160
    k = len(x) // w; db = 20 * np.log10(np.sqrt((x[:k*w].reshape(k, w) ** 2).mean(1)) + 1e-9)
    return db > np.percentile(db, 10) + 9
bloques = []
for n, bl in enumerate(BLOQUES_TXT):
    act = voz_activa(n); cum = np.cumsum(act) * 0.01
    toks = [(i, w) for i, s in enumerate(bl) for w in s.lstrip('·').split()]
    peso = np.array([len(w.strip('*.,:«»')) + 2 for _, w in toks], float); acum = np.concatenate([[0], np.cumsum(peso)]) / peso.sum() * cum[-1]
    primeros = {}
    for j, (i, w) in enumerate(toks): primeros.setdefault(i, ini[n] + np.searchsorted(cum, acum[j] + 1e-6) * 0.01)
    for i, s in enumerate(bl):
        partes = s.lstrip('·').split('*'); linea = (partes[0] + (partes[2] if len(partes) > 2 else '')).strip()
        clave = partes[1].strip('.,:').upper() if len(partes) > 1 else ''
        bloques.append([max(ini[n], primeros[i] - 0.06), None, linea, clave, s.startswith('·'), n])
fin_plano = lambda n: ini[n + 1] if n + 1 < len(ini) else DUR
for k, bq in enumerate(bloques):
    sig = bloques[k + 1] if k + 1 < len(bloques) else None
    bq[1] = sig[0] if sig and sig[5] == bq[5] else fin_plano(bq[5])
def t_de(txt): return next(b[0] for b in bloques if txt.lower() in (b[2] + ' ' + b[3]).lower())

# ---------- letras y utilidades
def inter(px, w): f = ImageFont.truetype(F + 'Inter.ttf', px); f.set_variation_by_axes([w]); return f
def mono(px, w=600): f = ImageFont.truetype(F + 'JetBrainsMono.ttf', px); f.set_variation_by_axes([w]); return f
LIN, MONO, MONO_S = inter(66, 800), mono(28), mono(24)
lim = lambda x: min(max(x, 0.0), 1.0)
sale = lambda x: 1 - (1 - lim(x)) ** 3
def rebote(x):
    x = lim(x); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def capa(): return Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
def con_sombra(ly, r=20, a=170, dy=6):
    s = ly.split()[3].filter(ImageFilter.GaussianBlur(r)).point(lambda p: p * a // 255); sh = Image.new('RGBA', ly.size, (0, 0, 0, 0)); sh.putalpha(s)
    o = Image.new('RGBA', ly.size, (0, 0, 0, 0)); o.alpha_composite(sh, (0, dy)); o.alpha_composite(ly); return o
def opacidad(im, a):
    if a >= 1: return im
    im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a))); return im
def ficha_logo(lado=84, sombra=True):
    t = Image.new('RGBA', (lado, lado), (0, 0, 0, 0)); g = ImageDraw.Draw(t); g.rounded_rectangle([0, 0, lado-1, lado-1], int(lado * .19), fill=CREMA); S = (lado * .76) / 24; m = lado * .12
    for x, y, w, h in ((0, 0, 14.1, 8.1), (15.9, 0, 8.1, 14.1), (9.9, 15.9, 14.1, 8.1), (0, 9.9, 8.1, 14.1)):
        g.rectangle([m+x*S, m+y*S, m+(x+w)*S-1, m+(y+h)*S-1], fill=BLANCO, outline=(214, 204, 186), width=max(2, lado // 42))
    g.rectangle([m+10.3*S, m+10.3*S, m+13.7*S-1, m+13.7*S-1], fill=ROJO)
    c = Image.new('RGBA', (lado + 40, lado + 40), (0, 0, 0, 0)); c.alpha_composite(t, (20, 20)); return con_sombra(c, 10, 100, 4) if sombra else c
LOGO, LOGO_G = ficha_logo(84), ficha_logo(220)
def vidrio(fr, caja, op, r=36):
    x0, y0, x1, y1 = [int(v) for v in caja]; zona = fr.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(30)).convert('RGBA')
    zona = Image.alpha_composite(zona, Image.new('RGBA', zona.size, BLANCO + (205,)))
    m = Image.new('L', zona.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, zona.width-1, zona.height-1], r, fill=int(255*op))
    sh = Image.new('L', fr.size, 0); ImageDraw.Draw(sh).rounded_rectangle([x0, y0+14, x1, y1+14], r, fill=int(90*op)); sh = sh.filter(ImageFilter.GaussianBlur(28))
    fr.paste(Image.new('RGBA', fr.size, (0, 0, 0, 255)), (0, 0), sh); fr.paste(zona, (x0, y0), m)
    ly = capa(); ImageDraw.Draw(ly).rounded_rectangle([x0, y0, x1, y1], r, outline=BLANCO + (int(255*op),), width=3); fr.alpha_composite(ly)
def tilde(g, x, y, lado, p, op=1.0):   # cuadradito rojo con tilde blanco, entra con rebote
    if p <= 0: return
    s = lado * min(p, 1.08); a = int(255 * op)
    g.rounded_rectangle([x - s/2, y - s/2, x + s/2, y + s/2], s * .25, fill=ROJO + (a,))
    if p > .6: k = s / 32; g.line([(x - 9*k, y), (x - 3*k, y + 7*k), (x + 9*k, y - 7*k)], fill=BLANCO + (a,), width=max(3, int(5*k)), joint='curve')

# ---------- subtítulos (marca.md)
cache = {}
def capa_sub(linea, clave):
    if (linea, clave) in cache: return cache[(linea, clave)]
    L = Image.new('RGBA', (1080, 330), (0, 0, 0, 0)); K = Image.new('RGBA', (1080, 330), (0, 0, 0, 0))
    if linea: ImageDraw.Draw(L).text((540, 110), linea, font=LIN, fill=BLANCO, anchor='ms')
    if clave:
        px = 112
        while inter(px, 900).getlength(clave) > 820: px -= 4
        k = inter(px, 900); w = k.getlength(clave); y1 = 142 if linea else 60; g = ImageDraw.Draw(K)
        g.rounded_rectangle([540-w/2-30, y1, 540+w/2+30, y1+128], 22, fill=ROJO); g.text((540, y1+104), clave, font=k, fill=BLANCO, anchor='ms')
    cache[(linea, clave)] = (con_sombra(L), con_sombra(K)); return cache[(linea, clave)]
def subtitulo(fr, t):
    for d0, d1, linea, clave, oculto, n in bloques:
        if oculto or not (d0 <= t < d1): continue
        L, K = capa_sub(linea, clave); y = 1220; e = sale((t - d0) / 0.25)
        fr.alpha_composite(opacidad(L, e), (0, int(y + (1 - e) * 18)))
        if clave:
            p = rebote((t - d0 - 0.04) / 0.3)
            if 0 < p < 1 or p > 1:
                w2, h2 = max(1, int(1080 * (0.86 + 0.14 * p))), max(1, int(330 * (0.86 + 0.14 * p)))
                fr.alpha_composite(opacidad(K.resize((w2, h2)), min(1, p)), (int(540 - w2/2), int(y + 165 - h2/2)))
            elif p == 1: fr.alpha_composite(K, (0, y))

# ---------- momentos
T_CHECK = [t_de('cualquier'), t_de('Preguntame'), t_de('listo')]
P3, P4, P5, P6, P7, P8 = ini[2], ini[3], ini[4], ini[5], ini[6], ini[7]
T_FIN = DUR - 0.35                                        # empieza el cierre
T_G = t_de('Eso casi') - 0.05                             # el gancho se va cuando arranca el primer subtítulo
PILLS = [('¿Para quién es?', t_de('Te pregunta')), ('¿Qué tono?', t_de('alto')), ('¿Para cuándo?', t_de('preguntar'))]
PROMPT_A = ['Necesito un mail para un cliente', 'que se atrasó con el pago.', 'Que suene amable pero firme,', 'que mencione la factura,',
            'que le ponga una fecha límite,', 'que no parezca un reclamo,', 'con un asunto corto,', 'que cierre con mi firma,', 'que sea breve', 'y que lo pueda mandar hoy.']
def pantalla_completa(t): return P3 <= t < P4 or P7 <= t < P7 + 0.95

# contador arriba: «EL TRUCO» con 3 círculos que se tildan
def contador(fr, t):
    if not (ini[1] - 0.2 <= t < T_FIN) or pantalla_completa(t): return
    op = sale((t - ini[1] + 0.2) / 0.4); ly = capa(); g = ImageDraw.Draw(ly)
    g.text((96, 186), 'EL TRUCO', font=MONO_S, fill=BLANCO + (int(220 * op),), anchor='ls')
    for i, tc in enumerate(T_CHECK):
        x = 262 + i * 44; y = 178
        g.ellipse([x - 15, y - 15, x + 15, y + 15], outline=BLANCO + (int(200 * op),), width=3)
        p = rebote((t - tc) / 0.35) if t >= tc else 0
        if p > 0: tilde(g, x, y, 30, p, op)
    fr.alpha_composite(con_sombra(ly, 8, 150, 2))

# gancho: «ChatGPT te puede hacer» arriba y PREGUNTAS gigante detrás de la cabeza
PAL = 'PREGUNTAS'; _px = 196
while inter(_px, 900).getlength(PAL) > 960: _px -= 2
FPAL = inter(_px, 900)
def gancho_detras(fr, t):
    if t >= T_G: return
    s = sale((T_G - t) / 0.3); ly = capa(); x = 540 - FPAL.getlength(PAL) / 2; g = ImageDraw.Draw(ly)
    for i, l in enumerate(PAL):
        e = sale((t - 0.15 - i * 0.045) / 0.4); a = int(255 * min(e, s))
        g.text((x, 600 + (1 - e) * 60), l, font=FPAL, fill=BLANCO + (a,), anchor='ls'); x += FPAL.getlength(l)
    fr.alpha_composite(con_sombra(ly, 26, 140, 8))
def gancho_delante(fr, t):
    if t >= T_G: return
    e, s = sale(t / 0.3), sale((T_G - t) / 0.3); op = min(e, s); txt = 'ChatGPT te puede hacer'
    f = inter(46, 800); w = f.getlength(txt); ly = capa(); g = ImageDraw.Draw(ly); y = 300 + (1 - e) * 24
    g.rounded_rectangle([540 - w/2 - 26, y, 540 + w/2 + 26, y + 70], 18, fill=ROJO + (int(255*op),)); g.text((540, y + 50), txt, font=f, fill=BLANCO + (int(255*op),), anchor='ms')
    fr.alpha_composite(con_sombra(ly, 14, 140, 4))

# plano 2: el prompt larguísimo que se escribe solo, y el dato que falta
def prompt_largo(fr, t):
    d0, d1 = ini[1], ini[2] - 0.05
    if not (d0 <= t < d1): return
    e, s = sale((t - d0) / 0.4), sale((d1 - t) / 0.3); op = min(e, s); dy = (1 - e) * 40
    x0, y0, x1, y1 = 100, 232 + dy, 790, 442 + dy; vidrio(fr, (x0, y0, x1, y1), op)
    ly = capa(); g = ImageDraw.Draw(ly); a = int(255 * op)
    t_esc0, t_esc1 = d0 + 0.3, t_de('olvidaste')                      # se escribe mientras habla de las 10 líneas
    car = sum(len(l) for l in PROMPT_A); n = int(car * lim((t - t_esc0) / (t_esc1 - t_esc0)))
    lineas, resto = [], n
    for l in PROMPT_A:
        if resto <= 0: break
        lineas.append(l[:resto]); resto -= len(l)
    g.rectangle([144, y0 + 34, 158, y0 + 48], fill=ROJO + (a,)); g.text((172, y0 + 50), 'PROMPT', font=MONO, fill=NOCHE + (int(170*op),), anchor='ls')
    g.text((746, y0 + 50), f'{max(1, len(lineas))}/10 líneas', font=MONO_S, fill=NOCHE + (int(140*op),), anchor='rs')
    f = inter(32, 600); vis = lineas[-3:] or ['']
    for i, l in enumerate(vis):
        g.text((146, y0 + 104 + i * 44), l + ('|' if i == len(vis) - 1 and int(t * 3) % 2 == 0 else ''), font=f, fill=NOCHE + (int(a * (0.55 + 0.15 * i)),), anchor='ls')
    for txt, tc in (('FALTA EL MONTO', t_de('un solo')), ('LO INVENTA', t_de('inventa'))):
        if t >= tc and (txt == 'LO INVENTA' or t < t_de('inventa')):
            p = rebote((t - tc) / 0.35); fp = inter(30, 900); w = fp.getlength(txt) + 40
            cx, cy = 746 - w / 2, y1 + 8
            g.rounded_rectangle([cx - w/2*p, cy - 24*p, cx + w/2*p, cy + 24*p], 14, fill=ROJO + (a,))
            if p > .7: g.text((cx, cy + 11), txt, font=fp, fill=BLANCO + (a,), anchor='ms')
    fr.alpha_composite(ly)

# plano 3: pantalla completa «Probá al REVÉS», la palabra gira de cabeza a derecha
FREV = inter(250, 900)
REV = Image.new('RGBA', (1080, 330), (0, 0, 0, 0)); ImageDraw.Draw(REV).text((540, 250), 'REVÉS', font=FREV, fill=ROJO, anchor='ms')
def reves(fr, t):
    if not (P3 <= t < P4): return
    u = t - P3; fondo = Image.new('RGBA', (1080, 1920), CREMA + (255,)); g = ImageDraw.Draw(fondo)
    g.rectangle([96, 640, 112, 656], fill=ROJO); g.text((128, 658), 'EL TRUCO', font=MONO, fill=NOCHE + (170,), anchor='ls')
    e = sale(u / 0.3); g.text((540, 830 - (1 - e) * 30), 'Probá al', font=inter(96, 800), fill=NOCHE + (int(255*e),), anchor='ms')
    giro = 180 * (1 - rebote((u - 0.4) / 0.55)); r = REV.rotate(giro, resample=Image.BICUBIC, center=(540, 165))
    fondo.alpha_composite(r, (0, 880))
    fr.paste(fondo, (0, 0))

# planos 4-5: el prompt corto que se escribe en vivo
def prompt_corto(fr, t):
    d0, d1 = P4, P6 - 0.05
    if not (d0 <= t < d1): return
    e, s = sale((t - d0) / 0.4), sale((d1 - t) / 0.3); op = min(e, s); dy = (1 - e) * 40
    L1, L2, L3 = 'Un mail para cobrar una factura.', 'Preguntame 3 cosas', 'de lo que te quede duda.'
    t1a, t1b = t_de('Contale') + 0.2, t_de('en una sola') + 0.7
    t2a = t_de('Preguntame'); t2b = t_de('de lo que') + 0.8
    h = 92 + 44 * (3 if t >= t2a else 1)
    x0, y0 = 100, 232 + dy; vidrio(fr, (x0, y0, 790, y0 + h), op); ly = capa(); g = ImageDraw.Draw(ly); a = int(255 * op)
    g.rectangle([144, y0 + 34, 158, y0 + 48], fill=ROJO + (a,)); g.text((172, y0 + 50), 'PROMPT', font=MONO, fill=NOCHE + (int(170*op),), anchor='ls')
    f, fr2 = inter(34, 650), inter(34, 850)
    def escribe(txt, ta, tb): return txt[:int(len(txt) * lim((t - ta) / (tb - ta)))]
    c1 = escribe(L1, t1a, t1b); cursor = '|' if int(t * 3) % 2 == 0 else ''
    if t < t2a: g.text((146, y0 + 104), c1 + cursor, font=f, fill=NOCHE + (a,), anchor='ls')
    else:
        g.text((146, y0 + 104), L1, font=f, fill=NOCHE + (int(a * .55),), anchor='ls')
        todo = L2 + '\n' + L3; c = escribe(todo, t2a, t2b); l2, _, l3 = c.partition('\n')
        g.text((146, y0 + 148), l2 + ('' if l3 else cursor), font=fr2, fill=ROJO + (a,), anchor='ls')
        if l3 or '\n' in c: g.text((146, y0 + 192), l3 + cursor, font=fr2, fill=ROJO + (a,), anchor='ls')
    fr.alpha_composite(ly)
T_TIPEO = [(t_de('Contale') + 0.2, t_de('en una sola') + 0.7), (t_de('Preguntame'), t_de('de lo que') + 0.8), (ini[1] + 0.3, t_de('olvidaste'))]

# plano 6: pastillas en arco sobre la cabeza (por detrás de la persona: nunca tapan la cara)
FPILL = inter(36, 750)
def arco(fr, t, cabeza):
    d0, d1 = P6, P7 - 0.05
    if not (d0 <= t < d1) or cabeza is None: return
    hx, ht = cabeza; cx, cy, R = 540, ht + 190, 360; op = min(sale((t - d0) / 0.4), sale((d1 - t) / 0.3))
    ly = capa(); g = ImageDraw.Draw(ly)
    for k in range(48):                                              # arco punteado que gira despacio
        a0 = np.radians(192 + k * 3.25 + (t * 12) % 3.25)
        if k % 2 == 0: g.arc([cx - R, cy - R, cx + R, cy + R], np.degrees(a0), np.degrees(a0) + 1.6, fill=BLANCO + (int(170*op),), width=4)
    for i, (txt, tc) in enumerate(PILLS):
        if t < tc: continue
        p = rebote((t - tc) / 0.4); ang = np.radians([215, 270, 325][i] + 3 * np.sin(t * 1.3 + i))
        px, py = cx + R * np.cos(ang), cy + R * np.sin(ang); w = FPILL.getlength(txt) + 54
        px = min(max(px, 60 + w/2), 1000 - w/2); py = max(py, 236)
        g.rounded_rectangle([px - w/2*p, py - 34*p, px + w/2*p, py + 34*p], 34, fill=BLANCO + (int(240*op),), outline=ROJO + (int(255*op),), width=3)
        if p > .7: g.text((px, py + 13), txt, font=FPILL, fill=NOCHE + (int(255*op),), anchor='ms')
    fr.alpha_composite(con_sombra(ly, 14, 120, 6))

# plano 7: apertura a pantalla completa con los íconos, después la tarjeta con tildes
def icono_mail(g, x, y, s, a):
    g.rounded_rectangle([x - s, y - s*.68, x + s, y + s*.68], s*.14, fill=BLANCO + (a,), outline=NOCHE + (a,), width=8)
    g.line([(x - s + 10, y - s*.6), (x, y + s*.08), (x + s - 10, y - s*.6)], fill=ROJO + (a,), width=10, joint='curve')
def icono_avion(g, x, y, s, a):
    g.polygon([(x - s, y + s*.1), (x + s, y - s*.7), (x - s*.15, y + s*.75), (x - s*.25, y + s*.25)], fill=ROJO + (a,))
    g.polygon([(x - s*.25, y + s*.25), (x + s, y - s*.7), (x - s*.05, y + s*.4)], fill=(120, 44, 30, a))
def apertura_sirve(fr, t):
    if not (P7 <= t < P7 + 0.95): return
    u = t - P7; salida = sale((u - 0.7) / 0.25); fondo = Image.new('RGBA', (1080, 1920), CREMA + (255,)); g = ImageDraw.Draw(fondo)
    g.rectangle([96, 560, 112, 576], fill=ROJO); g.text((128, 578), 'SIRVE PARA', font=MONO, fill=NOCHE + (170,), anchor='ls')
    for i, (dibu, txt) in enumerate(((icono_mail, 'Un mail difícil'), (icono_avion, 'Un viaje de 4 días'))):
        p = rebote((u - 0.05 - i * 0.15) / 0.4); x = 300 + i * 480; y = 900 - 10 * np.sin(u * 6 + i)
        if p > 0: dibu(g, x, y, 130 * min(p, 1.08), 255)
        if p > .5: g.text((x, 1130), txt, font=inter(46, 800), fill=NOCHE, anchor='ms')
    fr.paste(fondo, (0, int(-1920 * salida)))
def lista_sirve(fr, t):
    d0, d1 = P7 + 0.8, P8 - 0.05
    if not (d0 <= t < d1): return
    e, s = sale((t - d0) / 0.35), sale((d1 - t) / 0.3); op = min(e, s); dy = (1 - e) * 30
    items = [('Un mail difícil', t_de('Sirve para')), ('Un viaje de 4 días', t_de('difícil o para'))]
    y0 = 232 + dy; vidrio(fr, (100, y0, 780, y0 + 92 + 56 * 2), op); ly = capa(); g = ImageDraw.Draw(ly); a = int(255 * op)
    g.rectangle([144, y0 + 34, 158, y0 + 48], fill=ROJO + (a,)); g.text((172, y0 + 50), 'SIRVE PARA', font=MONO, fill=NOCHE + (int(170*op),), anchor='ls')
    for i, (txt, ti) in enumerate(items):
        ti = max(ti, d0); p = rebote((t - ti) / 0.35) if t >= ti else 0
        if p <= 0: continue
        y = y0 + 112 + i * 56; tilde(g, 160, y - 16, 32, p, op); g.text((192, y), txt, font=inter(44, 750), fill=NOCHE + (int(a * min(p, 1)),), anchor='ls')
    fr.alpha_composite(ly)

# cierre: el video se desenfoca y aparece el logo con «Guardalo y seguí a @pvmr.dev»
def cierre(fr, t):
    if t < T_FIN: return fr
    u = t - T_FIN; b = sale(u / 0.5)
    fr = fr.filter(ImageFilter.GaussianBlur(22 * b)); fr = Image.blend(fr, Image.new('RGBA', fr.size, NOCHE + (255,)), 0.55 * b)
    ly = capa(); p = rebote((u - 0.15) / 0.5)
    if p > 0:
        s = max(1, int(LOGO_G.width * min(p, 1.06))); ly.alpha_composite(LOGO_G.resize((s, s)), (int(540 - s/2), int(700 - s/2)))
    g = ImageDraw.Draw(ly); e = sale((u - 0.35) / 0.35)
    if e > 0:
        g.text((540, 930 + (1-e)*20), 'Guardalo y seguí a', font=inter(54, 800), fill=BLANCO + (int(255*e),), anchor='ms')
        f = inter(58, 900); w = f.getlength('@pvmr.dev')
        g.rounded_rectangle([540 - w/2 - 34, 968 + (1-e)*20, 540 + w/2 + 34, 1056 + (1-e)*20], 44, fill=CREMA + (int(255*e),))
        g.text((540, 1033 + (1-e)*20), '@pvmr.dev', font=f, fill=ROJO + (int(255*e),), anchor='ms')
        ya = 1110 + 14 * abs(np.sin(u * 5)); g.line([(540, ya), (540, ya + 60)], fill=BLANCO + (int(255*e),), width=6)
        g.line([(516, ya + 38), (540, ya + 62), (564, ya + 38)], fill=BLANCO + (int(255*e),), width=6, joint='curve')
    fr.alpha_composite(ly); return fr

# ---------- cabeza a partir del recorte (arriba del pelo y centro), suavizada
cab_prev = [None]
def cabeza_de(alpha):
    a = np.asarray(alpha.resize((270, 480)))
    filas = np.nonzero((a > 128).sum(1) > 12)[0]
    if not len(filas): return cab_prev[0]
    top = filas[0]; banda = a[top:top + 40] > 128; xs = np.nonzero(banda.any(0))[0]
    hx, ht = xs.mean() * 4, top * 4
    if cab_prev[0]: hx, ht = cab_prev[0][0] * .85 + hx * .15, cab_prev[0][1] * .85 + ht * .15
    cab_prev[0] = (hx, ht); return cab_prev[0]

# ---------- sonido: voz limpia + efectos suaves en las acciones (nunca un golpe encima de una palabra)
def audio():
    # voz-sin-eco.wav sale de dereverb.py (resta espectral de la cola de eco, T60 0,6 s); después puerta firme, menos «caja» en 280 Hz y algo de presencia
    voz = (f'highpass=f=90,afftdn=nf=-32,volume=14dB,agate=threshold=0.04:ratio=3.5:range=0.16:attack=3:release=110:knee=2,'
           f'equalizer=f=280:t=q:w=1.2:g=-4,equalizer=f=4000:t=q:w=1:g=1.5,acompressor=threshold=0.1:ratio=1.6:attack=10:release=150,volume={GANANCIA}dB,alimiter=limit=0.8:level=disabled')
    ef = [(0.1, 'whoosh-short', -20), (ini[1] - 0.3, 'click-soft', -18), (P3 - 0.02, 'whoosh', -16), (P4, 'whoosh-short', -20), (P7 - 0.02, 'whoosh', -16),
          (P7 + 0.7, 'whoosh-short', -22), (T_FIN + 0.15, 'chime', -16)]
    ef += [(tc, 'pop', -18) for tc in T_CHECK] + [(tc, 'pop', -20) for _, tc in PILLS]
    ef += [(t_de('Sirve para'), 'click-soft', -18), (t_de('difícil o para'), 'click-soft', -18)]
    # puerta con «mirada adelante» de 12 ms: decide con la señal sin demorar y deja pasar la demorada, así no se come la primera consonante
    pre, post = voz.split(',agate=')[0], voz.split(',agate=')[1].split(',', 1)
    ins, fc, labels = ['-i', 'voz-sin-eco-media.wav'], [f'[0:a]{pre},atrim=start=0.025,asetpts=PTS-STARTPTS,asplit[vm][vs];[vm]adelay=12[vd];[vd][vs]sidechaingate={post[0]}[vg];'
                                                   f'[vg]atrim=start=0.012,asetpts=PTS-STARTPTS,{post[1]},aformat=channel_layouts=stereo,apad=whole_dur={TOTAL:.3f},asplit[voz][llave]'], ['[voz]']
    for i, (tt, nom, db) in enumerate(ef, 1):
        ins += ['-i', SFX + nom + '.mp3']; ms = int(max(0, tt) * 1000)
        fc.append(f'[{i}:a]aformat=channel_layouts=stereo,aresample=48000,volume={db}dB,adelay={ms}|{ms}[e{i}]'); labels.append(f'[e{i}]')
    for j, (ta, tb) in enumerate(T_TIPEO, len(ef) + 1):                # tecleo bajito mientras se escribe el prompt
        ins += ['-stream_loop', '-1', '-i', SFX + 'typing.mp3']; ms = int(ta * 1000)
        fc.append(f'[{j}:a]aformat=channel_layouts=stereo,aresample=48000,atrim=0:{tb-ta:.3f},afade=t=out:st={max(0,tb-ta-0.15):.3f}:d=0.15,volume=-26dB,adelay={ms}|{ms}[e{j}]'); labels.append(f'[e{j}]')
    if MUSICA:   # música bajita (−13 dB) que se aparta otro poco cuando habla; entra y sale con fundido
        j = sum(1 for x in ins if x == '-i')
        ins += ['-i', MUSICA]
        fc.append(f'[{j}:a]aformat=channel_layouts=stereo,aresample=48000,atrim=0:{TOTAL:.3f},volume=-13dB,afade=t=in:d=0.6,afade=t=out:st={TOTAL-1.6:.3f}:d=1.6[mus]')
        fc.append('[mus][llave]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=350:makeup=1[musd]'); labels.append('[musd]')
    else: fc.append('[llave]anullsink')
    fc.append(''.join(labels) + f'amix=inputs={len(labels)}:duration=first:normalize=0,alimiter=limit=0.8:level=disabled[a]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[a]', '-t', f'{TOTAL:.3f}', '-ar', '48000', 'mezcla.wav'], check=True)

# ---------- fotograma a fotograma
def fotograma(fr, rec, t):
    n = max(i for i, s in enumerate(ini) if s <= min(t, DUR - 1e-3) + 1e-6)
    d = fin_plano(n) - ini[n]; u = lim((t - ini[n]) / d); z = 1 + 0.08 * (u if n % 2 == 0 else 1 - u)
    if P4 <= t < P4 + 0.4: z += 0.14 * (1 - sale((t - P4) / 0.4))      # zoom de golpe al salir de «al revés»
    if z > 1.0005:
        w, h = 1080 / z, 1920 / z; x0 = (1080 - w) / 2; y0 = (1920 - h) * 0.36; box = (x0, y0, x0 + w, y0 + h)
        fr = fr.resize((1080, 1920), Image.BILINEAR, box=box); rec = rec.resize((1080, 1920), Image.BILINEAR, box=box)
    fr = fr.convert('RGBA'); cab = cabeza_de(rec.split()[3])
    # detrás de la persona
    gancho_detras(fr, t); arco(fr, t, cab)
    fr.alpha_composite(rec)
    # delante
    prompt_largo(fr, t); prompt_corto(fr, t); lista_sirve(fr, t); gancho_delante(fr, t)
    reves(fr, t); apertura_sirve(fr, t)
    if not pantalla_completa(t) and t < T_FIN + 0.1: subtitulo(fr, t)
    contador(fr, t)
    if t < T_FIN + 0.2: fr.alpha_composite(opacidad(LOGO, 1 - sale((t - T_FIN) / 0.2)), (840, 212))
    return cierre(fr, t)

if SOLO == 'fotos':
    ts = [float(x) for x in sys.argv[3].split(',')]
    for t in ts:
        f = int(round(min(t, DUR - 0.04) * FPS))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'base-video.mp4', '-vf', f'select=eq(n\\,{f})', '-frames:v', '1', '_f.png'], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-c:v', 'libvpx-vp9', '-i', 'recorte.webm', '-vf', f'select=eq(n\\,{f})', '-frames:v', '1', '-pix_fmt', 'rgba', '_r.png'], check=True)
        fr, rec = Image.open('_f.png').convert('RGB'), Image.open('_r.png').convert('RGBA')
        cab_prev[0] = None   # sin suavizado entre fotos sueltas
        fotograma(fr, rec, t).convert('RGB').save(f'control-{t:05.2f}.jpg', quality=90)
    print('✓ fotos'); sys.exit()

audio()
if SOLO == 'audio': print('✓ audio'); sys.exit()
lee = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', 'base-video.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
lr = subprocess.Popen(['ffmpeg', '-v', 'error', '-c:v', 'libvpx-vp9', '-i', 'recorte.webm', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '1080x1920', '-'], stdout=subprocess.PIPE)
esc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(FPS), '-i', '-', '-i', 'mezcla.wav',
                        '-map', '0:v', '-map', '1:a', '-map_metadata', '-1', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', '../../FINAL v4 - 3 preguntas.mp4'], stdin=subprocess.PIPE)
def cuadros():   # (video, recorte) de cada fotograma; al terminarse, repite el último (la cola del cierre)
    fr = rec = None
    while True:
        b1 = lee.stdout.read(1080 * 1920 * 3); b2 = lr.stdout.read(1080 * 1920 * 4)
        if len(b1) == 1080 * 1920 * 3: fr = Image.frombytes('RGB', (1080, 1920), b1)
        if len(b2) == 1080 * 1920 * 4: rec = Image.frombytes('RGBA', (1080, 1920), b2)
        yield fr, rec
# la mano que va al celular o vuelve de él: (primer cuadro, último cuadro, cuadro limpio que los reemplaza)
P1_FIN = (int(3.95 * FPS) + 1, int(round(ini[1] * FPS)) - 1, int(3.95 * FPS))      # fin del plano 1: queda el último cuadro limpio
P2_INI = (int(round(ini[1] * FPS)), int(round(ini[1] * FPS)) + 3, int(round(ini[1] * FPS)) + 4)   # arranque del plano 2: el primero limpio
fuente, k, guardado = cuadros(), 0, {}
adelante = []
while k < int(round(TOTAL * FPS)):
    if k == P2_INI[0]:                                   # se adelanta la lectura hasta el cuadro limpio
        adelante = [next(fuente) for _ in range(P2_INI[2] - P2_INI[0] + 1)]
        guardado[P2_INI[2]] = adelante[-1]
    par = adelante.pop(0) if adelante else next(fuente)
    if k == P1_FIN[2]: guardado[k] = par
    if P1_FIN[0] <= k <= P1_FIN[1]: par = guardado[P1_FIN[2]]
    if P2_INI[0] <= k <= P2_INI[1]: par = guardado[P2_INI[2]]
    fr, rec = par
    esc.stdin.write(fotograma(fr.copy(), rec.copy(), k / FPS).convert('RGB').tobytes()); k += 1
esc.stdin.close(); esc.wait()
print(f'✓ FINAL v4 · {TOTAL:.2f} s · {k} fotogramas')
