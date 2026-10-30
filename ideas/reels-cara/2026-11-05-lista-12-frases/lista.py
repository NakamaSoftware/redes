# P1 · «12 frases para pegarle a ChatGPT»: gancho sobre la cara (0–2,6 s) y la lista en papel (2,6–10 s).
# Uso: python3 lista.py <carpeta> <cara.png>   → gancho.png, lista.png, cuadros/ para el armado
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SP, CARA = sys.argv[1], sys.argv[2]
F = '/home/user/redes/marca/fuentes/'
NOCHE, CREMA, BLANCO, ROJO, GRIS = (20,24,22), (245,241,232), (255,255,255), (168,64,44), (95,99,104)
def inter(px, w): f = ImageFont.truetype(F+'Inter.ttf', px); f.set_variation_by_axes([w]); return f
def mono(px, w=600): f = ImageFont.truetype(F+'JetBrainsMono.ttf', px); f.set_variation_by_axes([w]); return f
SER, SERI = (lambda px: ImageFont.truetype(F+'InstrumentSerif-Regular.ttf', px)), (lambda px: ImageFont.truetype(F+'InstrumentSerif-Italic.ttf', px))
def capa(im): return Image.new('RGBA', im.size, (0,0,0,0))
def sombra(im, ly, r=18, a=150, dy=0):
    s = Image.new('RGBA', im.size, (0,0,0,0)); m = ly.split()[3].filter(ImageFilter.GaussianBlur(r)).point(lambda p: p*a//255)
    s.putalpha(m); im.alpha_composite(s, (0, dy)); im.alpha_composite(ly)
def ficha_logo(lado=84):
    t = Image.new('RGBA', (lado, lado), (0,0,0,0)); g = ImageDraw.Draw(t); g.rounded_rectangle([0,0,lado-1,lado-1], 16, fill=CREMA)
    S = (lado-20)/24
    for x,y,w,h in ((0,0,14.1,8.1),(15.9,0,8.1,14.1),(9.9,15.9,14.1,8.1),(0,9.9,8.1,14.1)):
        g.rectangle([10+x*S, 10+y*S, 10+(x+w)*S-1, 10+(y+h)*S-1], fill=BLANCO, outline=(214,204,186), width=2)
    g.rectangle([10+10.3*S, 10+10.3*S, 10+13.7*S-1, 10+13.7*S-1], fill=ROJO)
    return t
def ponlogo(im):
    ly = capa(im); ly.alpha_composite(ficha_logo(), (860, 232)); sombra(im, ly, 14, 110, 4)
def vidrio(im, caja, r=36):
    x0, y0, x1, y1 = caja; zona = im.crop(caja).filter(ImageFilter.GaussianBlur(30))
    zona = Image.alpha_composite(zona, Image.new('RGBA', zona.size, BLANCO+(205,)))
    m = Image.new('L', zona.size, 0); ImageDraw.Draw(m).rounded_rectangle([0,0,zona.width-1,zona.height-1], r, fill=255)
    sh = capa(im); ImageDraw.Draw(sh).rounded_rectangle(caja, r, fill=(0,0,0,255))
    s = sh.split()[3].filter(ImageFilter.GaussianBlur(28)).point(lambda p: p*90//255); so = Image.new('RGBA', im.size, (0,0,0,0)); so.putalpha(s); im.alpha_composite(so, (0, 14))
    im.paste(zona, (x0, y0), m); ImageDraw.Draw(im).rounded_rectangle(caja, r, outline=BLANCO+(255,), width=3)

FRASES = [
    'Respondeme en 3 líneas.',
    'Si no sabés, decime que no sabés.',
    'Dame 3 opciones bien distintas.',
    'Decime los 3 puntos más débiles.',
    'Antes de contestar, haceme 3 preguntas.',
    'Explicámelo como si tuviera 12 años.',
    'Haceme 5 preguntas para ver si entendí.',
    'Es para ___, para ___, en ___ líneas.',
    '¿Qué ves en esta foto?',
    'Dame una amable, una firme y una corta.',
    'Pasalo a una tabla con estas columnas.',
    '¿Cuál elegirías vos y por qué?',
]

# 1 · gancho: la tarjeta de vidrio arriba de la cabeza (compacta, para no tapar el pelo)
def gancho():
    im = Image.open(CARA).convert('RGBA'); vidrio(im, (150, 236, 840, 450)); g = ImageDraw.Draw(im)
    g.rectangle([192, 280, 208, 296], fill=ROJO); g.text((224, 298), 'SACALE CAPTURA', font=mono(28), fill=NOCHE+(170,), anchor='ls')
    f = inter(56, 750); g.text((192, 376), '12 frases para', font=f, fill=NOCHE, anchor='ls')
    g.text((192, 430), 'pegarle a ', font=f, fill=NOCHE, anchor='ls')
    g.text((192 + f.getlength('pegarle a '), 434), 'ChatGPT', font=SERI(78), fill=ROJO, anchor='ls')
    ponlogo(im); return im.convert('RGB')

# 2 · la lista: papel crema, todo dentro de la zona segura (y 240–1480, 140 px libres a la derecha)
def papel():
    im = Image.new('RGB', (1080, 1920), CREMA); g = ImageDraw.Draw(im)
    for x in range(0, 1080, 40): g.line([(x, 0), (x, 1920)], fill=(236, 230, 218))
    for y in range(0, 1920, 40): g.line([(0, y), (1080, y)], fill=(236, 230, 218))
    return im
X0, XMAX, Y0, PASO = 110, 1080 - 110, 520, 78
def fuente_lista():
    for px in range(42, 28, -1):
        f = inter(px, 650)
        if all(X0 + 74 + f.getlength(t) <= XMAX for t in FRASES): return f
    raise SystemExit('la lista no entra')
FL = fuente_lista()
def lista(n=12):
    im = papel(); g = ImageDraw.Draw(im)
    g.rectangle([X0, 286, X0 + 16, 302], fill=ROJO); g.text((X0 + 32, 304), 'SACALE CAPTURA', font=mono(30), fill=GRIS, anchor='ls')
    g.text((X0, 410), 'Pegale esto a', font=SER(96), fill=NOCHE, anchor='ls')
    g.text((X0 + SER(96).getlength('Pegale esto a '), 410), 'ChatGPT', font=SERI(96), fill=ROJO, anchor='ls')
    for i, t in enumerate(FRASES[:n]):
        y = Y0 + i * PASO
        g.text((X0, y), f'{i+1:02d}', font=mono(34, 700), fill=ROJO, anchor='ls')
        g.text((X0 + 74, y), t, font=FL, fill=NOCHE, anchor='ls')
        if i < 11: g.line([(X0, y + 26), (XMAX, y + 26)], fill=(226, 218, 204), width=2)
    g.text((X0, 1490), '@pvmr.dev', font=inter(30, 700), fill=GRIS, anchor='ls')
    return im

os.makedirs(f'{SP}/cuadros', exist_ok=True)
gancho().save(f'{SP}/gancho.png'); lista().save(f'{SP}/lista.png')
for n in range(1, 13): lista(n).save(f'{SP}/cuadros/lista-{n:02d}.png')
print('fuente de la lista:', FL.size, 'px')
