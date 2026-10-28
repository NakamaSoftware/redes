import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SP, F = sys.argv[1], '/home/user/redes/marca/fuentes/'
NOCHE, CREMA, BLANCO, ROJO = (20,24,22), (245,241,232), (255,255,255), (168,64,44)
def inter(px, w): f = ImageFont.truetype(F+'Inter.ttf', px); f.set_variation_by_axes([w]); return f
def mono(px, w=600): f = ImageFont.truetype(F+'JetBrainsMono.ttf', px); f.set_variation_by_axes([w]); return f
def serif(px): return ImageFont.truetype(F+'InstrumentSerif-Italic.ttf', px)
def base(n): return Image.open(f'{SP}/f{n}.png').convert('RGBA')
def capa(im): return Image.new('RGBA', im.size, (0,0,0,0))
def sombra(im, ly, r=18, a=150, dy=0):
    s = Image.new('RGBA', im.size, (0,0,0,0)); m = ly.split()[3].filter(ImageFilter.GaussianBlur(r)).point(lambda p: p*a//255)
    s.putalpha(m); im.alpha_composite(s, (0, dy)); im.alpha_composite(ly)
# logo claro: la versión crema del isotipo, en una ficha redondeada
def ficha_logo(lado=84):
    t = Image.new('RGBA', (lado, lado), (0,0,0,0)); g = ImageDraw.Draw(t); g.rounded_rectangle([0,0,lado-1,lado-1], 16, fill=CREMA)
    S = (lado-20)/24
    for x,y,w,h in ((0,0,14.1,8.1),(15.9,0,8.1,14.1),(9.9,15.9,14.1,8.1),(0,9.9,8.1,14.1)):
        g.rectangle([10+x*S, 10+y*S, 10+(x+w)*S-1, 10+(y+h)*S-1], fill=BLANCO, outline=(214,204,186), width=2)
    g.rectangle([10+10.3*S, 10+10.3*S, 10+13.7*S-1, 10+13.7*S-1], fill=ROJO)
    return t
LOGO = ficha_logo()
def ponlogo(im):
    ly = capa(im); ly.alpha_composite(LOGO, (860, 232)); sombra(im, ly, 14, 110, 4)
def vidrio(im, caja, r=36):
    x0, y0, x1, y1 = caja; zona = im.crop(caja).filter(ImageFilter.GaussianBlur(30))
    zona = Image.alpha_composite(zona, Image.new('RGBA', zona.size, BLANCO+(205,)))
    m = Image.new('L', zona.size, 0); ImageDraw.Draw(m).rounded_rectangle([0,0,zona.width-1,zona.height-1], r, fill=255)
    sh = capa(im); ImageDraw.Draw(sh).rounded_rectangle(caja, r, fill=(0,0,0,255)); sombra(im, capa(im)); 
    s = sh.split()[3].filter(ImageFilter.GaussianBlur(28)).point(lambda p: p*90//255); so = Image.new('RGBA', im.size, (0,0,0,0)); so.putalpha(s); im.alpha_composite(so, (0, 14))
    im.paste(zona, (x0, y0), m); ImageDraw.Draw(im).rounded_rectangle(caja, r, outline=BLANCO+(255,), width=3)

def gancho():
    im = base(1); vidrio(im, (150, 250, 930, 504)); g = ImageDraw.Draw(im)
    g.rectangle([196, 298, 212, 314], fill=ROJO); g.text((228, 316), 'PROMPT', font=mono(28), fill=NOCHE+(170,), anchor='ls')
    f = inter(56, 750); g.text((196, 398), '«Antes de responder,', font=f, fill=NOCHE, anchor='ls')
    g.text((196, 466), 'haceme ', font=f, fill=NOCHE, anchor='ls')
    x = 196 + f.getlength('haceme '); s = serif(78)
    g.text((x, 470), '3 preguntas»', font=s, fill=ROJO, anchor='ls')
    for i in range(13): y = 532 + i*26; g.line([(900, y), (900, y+12)], fill=BLANCO+(230,), width=5)
    g.ellipse([892, 532+13*26, 908, 548+13*26], fill=ROJO)
    ponlogo(im); return im
def sub_1():  # palabra clave en blanco sobre caja roja
    im = base(2); ly = capa(im); g = ImageDraw.Draw(ly)
    g.text((540, 1330), 'te responde', font=inter(66, 800), fill=BLANCO, anchor='ms')
    k = inter(112, 900); w = k.getlength('ADIVINANDO')
    g.rounded_rectangle([540-w/2-30, 1362, 540+w/2+30, 1490], 22, fill=ROJO)
    g.text((540, 1466), 'ADIVINANDO', font=k, fill=BLANCO, anchor='ms')
    sombra(im, ly, 20, 170, 6); ponlogo(im); return im
def sub_2():  # todo en una píldora blanca de vidrio, palabra clave en rojo
    im = base(2); f1, k = inter(64, 800), inter(64, 900)
    w = f1.getlength('te responde ') + k.getlength('ADIVINANDO'); x0 = 540 - w/2
    vidrio(im, (int(x0-40), 1318, int(x0+w+40), 1428), 30); g = ImageDraw.Draw(im)
    g.text((x0, 1396), 'te responde ', font=f1, fill=NOCHE, anchor='ls'); g.text((x0 + f1.getlength('te responde '), 1396), 'ADIVINANDO', font=k, fill=ROJO, anchor='ls')
    ponlogo(im); return im

ims = [('gancho (0–3 s)', gancho()), ('subtítulo · opción 1', sub_1()), ('subtítulo · opción 2', sub_2())]
W, H, pad = 400, 711, 24
hoja = Image.new('RGB', (3*W+4*pad, H+150), CREMA); g = ImageDraw.Draw(hoja)
g.text((pad, 26), 'C · Tarjeta de vidrio · versión clara', font=inter(40, 750), fill=NOCHE)
for i, (nom, im) in enumerate(ims):
    x = pad + i*(W+pad); g.text((x, 84), nom, font=mono(22, 500), fill=(110,110,100))
    hoja.paste(im.convert('RGB').resize((W, H)), (x, 120)); im.convert('RGB').save(f'{SP}/C-claro-{i}.jpg', quality=92)
hoja.save(f'{SP}/look-c-claro.jpg', quality=92)
