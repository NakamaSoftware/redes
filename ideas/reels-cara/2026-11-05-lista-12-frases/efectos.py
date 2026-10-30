# Tres efectos para la parte de la cara de P1 (2,17 s): chat, bichito y órbita.
# Uso: python3 efectos.py <carpeta> <tarjeta.png> <version: chat|bichito|orbita> [c|partida]
#   c = look C (cabeza abajo, lugar en el pecho); partida = pantalla partida (cabeza grande: los efectos van a la izquierda)
#   <carpeta>/f/NNN.png = cuadros de la toma; <carpeta>/m/NNN.png = máscara de la persona (hyperframes remove-background)
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter
ARGS = sys.argv[1:4]; MODO = sys.argv[4] if len(sys.argv) > 4 else 'c'
sys.argv = sys.argv[:1] + ['/tmp', '/dev/null']
exec(open(__file__.replace('efectos.py', 'lista.py')).read().split('FRASES = [')[0])  # colores, letras, vidrio y logo
SP, TARJ, VER = ARGS
FPS = 30
def ease_out(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def ease_back(x):
    x = max(0, min(1, x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def pildora(w, h, r, fondo=BLANCO + (235,)):
    t = Image.new('RGBA', (w + 60, h + 60), (0, 0, 0, 0)); s = Image.new('RGBA', t.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([30, 40, 30 + w, 40 + h], r, fill=(0, 0, 0, 90)); s = s.filter(ImageFilter.GaussianBlur(14))
    t.alpha_composite(s); ImageDraw.Draw(t).rounded_rectangle([30, 30, 30 + w, 30 + h], r, fill=fondo); return t
def pegar(im, capa, cx, cy, escala=1.0, alfa=1.0):
    if escala <= 0.01 or alfa <= 0.01: return
    c = capa.resize((max(1, round(capa.width * escala)), max(1, round(capa.height * escala))), Image.LANCZOS)
    if alfa < 1: c.putalpha(c.split()[3].point(lambda p: int(p * alfa)))
    im.alpha_composite(c, (round(cx - c.width / 2), round(cy - c.height / 2)))

# --- 1 · chat: una ventanita de chat sube a la altura del pecho y responde
def ventana(t):
    W, H = (800, 300) if MODO == 'c' else (340, 380); v = pildora(W, H, 34); g = ImageDraw.Draw(v); o = 30
    for i, col in enumerate(((236, 106, 94), (245, 190, 79), (98, 197, 84))): g.ellipse([o + 28 + i * 30, o + 26, o + 46 + i * 30, o + 44], fill=col)
    if MODO == 'c': g.text((o + W / 2, o + 44), 'ChatGPT', font=inter(26, 600), fill=GRIS, anchor='ms')
    else: g.text((o + W - 24, o + 44), 'ChatGPT', font=inter(24, 600), fill=GRIS, anchor='rs'); g.line([(o, o + 66), (o + W, o + 66)], fill=(230, 226, 218), width=2)
    f = inter(38, 700) if MODO == 'c' else inter(28, 700)
    PED, RES = ('Dame 12 frases útiles', 'Acá van, guardalas') if MODO == 'c' else ('Dame 12 preguntas', '¡Acá van!')
    Y1, Y2, Y3 = (130, 196, 232) if MODO == 'c' else (150, 236, 300)
    if t > 0.5:  # mi pedido, burbuja roja a la derecha
        s = ease_back((t - 0.5) / 0.25); lin = PED.split('\n'); w = max(f.getlength(x) for x in lin) + 56; hb = 74 + 40 * (len(lin) - 1)
        b = Image.new('RGBA', (int(w), hb), (0, 0, 0, 0)); ImageDraw.Draw(b).rounded_rectangle([0, 0, w - 1, hb - 1], 30, fill=ROJO)
        for j, x in enumerate(lin): ImageDraw.Draw(b).text((28, 50 + 40 * j), x, font=f, fill=BLANCO, anchor='ls')
        pegar(v, b, o + W - 16 - w / 2, o + Y1, s)
    if 0.9 < t < 1.45:  # escribiendo…
        b = Image.new('RGBA', (130, 64), (0, 0, 0, 0)); gb = ImageDraw.Draw(b); gb.rounded_rectangle([0, 0, 129, 63], 28, fill=(238, 234, 226))
        for i in range(3):
            a = 0.5 + 0.5 * math.sin((t - 0.9) * 14 - i * 1.1); gb.ellipse([30 + i * 28, 24 - 5 * a, 46 + i * 28, 40 - 5 * a], fill=GRIS)
        v.alpha_composite(b, (o + 20, o + Y2))
    if t > 1.45:  # la respuesta
        s = ease_back((t - 1.45) / 0.25); txt = RES; w = f.getlength(txt) + 56
        b = Image.new('RGBA', (int(w), 74), (0, 0, 0, 0)); ImageDraw.Draw(b).rounded_rectangle([0, 0, w - 1, 73], 30, fill=(238, 234, 226)); ImageDraw.Draw(b).text((28, 50), txt, font=f, fill=NOCHE, anchor='ls')
        pegar(v, b, o + 20 + w / 2, o + Y3, s)
    return v
def chat(im, mask, t):
    if t < 0.3: return
    e = ease_out((t - 0.3) / 0.4); v = ventana(t)
    v.putalpha(v.split()[3].point(lambda p: int(p * e)))
    im.alpha_composite(v, (110, round(1150 + 80 * (1 - e))) if MODO == 'c' else (-26, round(760 + 80 * (1 - e))))

# --- 2 · bichito: un globito de chat con ojos asoma por detrás del hombro, saluda y se esconde
def bicho(t):
    B = Image.new('RGBA', (300, 300), (0, 0, 0, 0)); g = ImageDraw.Draw(B)
    g.rounded_rectangle([30, 30, 270, 220], 70, fill=CREMA, outline=(214, 204, 186), width=5)
    g.polygon([(80, 205), (70, 270), (140, 215)], fill=CREMA); g.line([(80, 214), (70, 270), (135, 220)], fill=(214, 204, 186), width=5)
    parpadeo = 1.05 < t < 1.17
    for x in (115, 185):
        if parpadeo: g.line([(x - 16, 120), (x + 16, 120)], fill=NOCHE, width=8)
        else: g.ellipse([x - 16, 100, x + 16, 140], fill=NOCHE); g.ellipse([x - 4, 106, x + 6, 116], fill=BLANCO)
    for x in (82, 218): g.ellipse([x - 16, 146, x + 16, 166], fill=(232, 150, 130))
    g.arc([125, 140, 175, 180], 20, 160, fill=NOCHE, width=6)
    return B
def bichito(im, mask, t):
    sube = ease_back((t - 0.25) / 0.45) - ease_out((t - 1.85) / 0.3)
    if sube <= 0.001: return
    capa = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ang = 8 * math.sin(max(0, t - 0.7) * 9) if t < 1.6 else 0
    b = bicho(t).rotate(ang, resample=Image.BICUBIC, center=(150, 200))
    if t > 1.85: b.putalpha(b.split()[3].point(lambda p: int(p * (1 - ease_out((t - 1.85) / 0.2)))))
    BX, BY, BD = (790, 1330, 470) if MODO == 'c' else (30, 1500, 420)
    capa.alpha_composite(b, (BX, round(BY - BD * sube)))
    if 0.7 < t < 1.85:  # su globito con el número
        s = ease_back((t - 0.7) / 0.25) * (1 - ease_out((t - 1.6) / 0.25)); gl = pildora(150, 84, 38, ROJO + (255,)); ImageDraw.Draw(gl).text((105, 92), '¡12!', font=inter(48, 900), fill=BLANCO, anchor='ms')
        pegar(capa, gl, BX + 170, round(BY - BD * sube) - 30, s)
    persona = Image.new('RGBA', im.size, (0, 0, 0, 0)); persona.paste(im, (0, 0), mask)
    im.alpha_composite(capa); im.alpha_composite(persona)

# --- 3 · órbita: tres frases de la lista giran alrededor tuyo a la altura del pecho (por detrás cuando pasan atrás)
CHIPS = ['Respondeme en 3 líneas', 'Dame 3 opciones', 'Si no sabés, decilo']
def chip(txt):
    f = inter(42, 750); w = int(f.getlength(txt)) + 100; c = pildora(w, 86, 43); g = ImageDraw.Draw(c)
    g.rectangle([30 + 30, 30 + 30, 30 + 46, 30 + 46], fill=ROJO); g.text((30 + 62, 30 + 57), txt, font=f, fill=NOCHE, anchor='ls'); return c
CH = [chip(t) for t in CHIPS]
def orbita(im, mask, t):
    e = ease_out(t / 0.5); atras, adelante = Image.new('RGBA', im.size, (0, 0, 0, 0)), Image.new('RGBA', im.size, (0, 0, 0, 0))
    for i, c in enumerate(CH):
        a = 2 * math.pi * (t / 2.6) + i * 2 * math.pi / 3 + 0.6
        x, y, z = (540 + 330 * math.cos(a), 1210 + 120 * math.sin(a), math.sin(a)) if MODO == 'c' else (560 + 320 * math.cos(a), 1530 + 70 * math.sin(a), math.sin(a))
        esc = (0.78 + 0.22 * z) * e
        pegar(adelante if z > 0 else atras, c, x, y, esc, 0.55 + 0.45 * (z + 1) / 2)
    persona = Image.new('RGBA', im.size, (0, 0, 0, 0)); persona.paste(im, (0, 0), mask)
    im.alpha_composite(atras); im.alpha_composite(persona); im.alpha_composite(adelante)

EFECTO = {'chat': chat, 'bichito': bichito, 'orbita': orbita}[VER]
tarj = Image.open(TARJ).convert('RGBA'); n = len(os.listdir(f'{SP}/f')); os.makedirs(f'{SP}/{VER}', exist_ok=True)
for k in range(1, n + 1):
    t = (k - 1) / FPS
    im = Image.open(f'{SP}/f/{k:03d}.png').convert('RGBA'); mask = Image.open(f'{SP}/m/{k:03d}.png').convert('L')
    EFECTO(im, mask, t)
    tt = tarj.copy()
    if MODO == 'c': tt.putalpha(tt.split()[3].point(lambda p: int(p * ease_out(t / 0.3))))
    im.alpha_composite(tt)
    im.convert('RGB').save(f'{SP}/{VER}/{k:03d}.png')
