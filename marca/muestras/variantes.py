import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SP, F = sys.argv[1], '/home/user/redes/marca/fuentes/'
NOCHE, CREMA, CREMA2, BLANCO, ROJO, GRIS = (20,24,22), (245,241,232), (237,231,219), (255,255,255), (168,64,44), (95,99,104)
def inter(px, w): f = ImageFont.truetype(F+'Inter.ttf', px); f.set_variation_by_axes([w]); return f
def mono(px, w=600): f = ImageFont.truetype(F+'JetBrainsMono.ttf', px); f.set_variation_by_axes([w]); return f
SER, SERI = (lambda px: ImageFont.truetype(F+'InstrumentSerif-Regular.ttf', px)), (lambda px: ImageFont.truetype(F+'InstrumentSerif-Italic.ttf', px))
def papel():
    im = Image.new('RGB', (1080, 1920), CREMA); g = ImageDraw.Draw(im)
    for x in range(0, 1080, 40): g.line([(x, 0), (x, 1920)], fill=(236, 230, 218))
    for y in range(0, 1920, 40): g.line([(0, y), (1080, y)], fill=(236, 230, 218))
    return im
def sombra_caja(im, caja, r=28):
    s = Image.new('L', im.size, 0); ImageDraw.Draw(s).rounded_rectangle([caja[0], caja[1]+16, caja[2], caja[3]+16], r, fill=60); s = s.filter(ImageFilter.GaussianBlur(26))
    im.paste((180, 170, 150), (0, 0), s); ImageDraw.Draw(im).rounded_rectangle(caja, r, fill=BLANCO)
# 1 · cortinilla de paso: tapa el corte entre tomas
c = Image.new('RGB', (1080, 1920), ROJO); g = ImageDraw.Draw(c)
g.text((540, 820), 'PASO 02', font=mono(40), fill=(245, 225, 215), anchor='ms')
g.text((540, 1180), '02', font=SER(420), fill=BLANCO, anchor='ms')
# 2 · pantalla de papel: título serif con una palabra en cursiva + la ventana donde se escribe
p = papel(); g = ImageDraw.Draw(p)
g.rectangle([130, 470, 146, 486], fill=ROJO); g.text((162, 488), 'PASO 02', font=mono(30), fill=GRIS, anchor='ls')
f1, f2 = SER(120), SERI(120); x = 130
g.text((x, 640), 'Contalo en', font=f1, fill=NOCHE, anchor='ls'); g.text((130, 770), 'una línea', font=f2, fill=ROJO, anchor='ls')
sombra_caja(p, (130, 900, 950, 1180)); g = ImageDraw.Draw(p)
for i, col in enumerate(((236, 106, 94), (245, 190, 79), (98, 197, 84))): g.ellipse([160 + i*34, 928, 182 + i*34, 950], fill=col)
g.text((540, 948), 'ChatGPT', font=inter(26, 600), fill=GRIS, anchor='ms')
g.text((170, 1050), 'Un mail para cobrar una factura.', font=inter(36, 600), fill=NOCHE, anchor='ls')
g.text((170, 1110), 'Preguntame 3 cosas antes|', font=inter(36, 800), fill=ROJO, anchor='ls')
g.text((540, 1400), 'una', font=inter(62, 800), fill=NOCHE, anchor='ms'); g.text((540, 1480), 'LÍNEA', font=inter(62, 800), fill=ROJO, anchor='ms')
# 3 · pantalla partida: pizarrón arriba (y 0–740) y vos abajo
v = Image.new('RGB', (1080, 1920), CREMA2); cara = Image.open(f'{SP}/cara.png').convert('RGB')
v.paste(cara.crop((0, 280, 1080, 1460)).resize((1080, 1180)), (0, 740)); g = ImageDraw.Draw(v)
g.rectangle([0, 0, 1080, 740], fill=CREMA2); g.line([(0, 740), (1080, 740)], fill=NOCHE, width=4)
g.text((130, 300), 'Pedido largo vs. 3 preguntas', font=inter(48, 800), fill=NOCHE, anchor='ls')
for i, (txt, w, col) in enumerate((('10 líneas, falta un dato', 760, (169, 174, 169)), ('1 línea + «preguntame 3 cosas»', 520, ROJO))):
    y = 400 + i * 190; g.rounded_rectangle([130, y, 130 + w, y + 70], 16, fill=col)
    g.text((130, y - 34), txt, font=inter(34, 700), fill=NOCHE, anchor='ls')
g.ellipse([88, 568, 702, 682], outline=ROJO, width=6)
sub = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); ImageDraw.Draw(sub).text((540, 860), 'ADIVINA', font=inter(66, 800), fill=BLANCO, anchor='ms')
s2 = sub.split()[3].filter(ImageFilter.GaussianBlur(10)); sh = Image.new('RGBA', sub.size, (0, 0, 0, 0)); sh.putalpha(s2.point(lambda a: a * 170 // 255))
v = v.convert('RGBA'); v.alpha_composite(sh, (0, 5)); v.alpha_composite(sub); v = v.convert('RGB')
W, H = 360, 640; hoja = Image.new('RGB', (3*W + 4*24, H + 130), CREMA); gh = ImageDraw.Draw(hoja)
for i, (nom, im) in enumerate((('Pasos · cortinilla', c), ('Pasos · pantalla de papel', p), ('Pantalla partida', v))):
    x = 24 + i * (W + 24); gh.text((x, 40), nom, font=inter(30, 750), fill=NOCHE); hoja.paste(im.resize((W, H)), (x, 100)); im.save(f'{SP}/{i}.jpg', quality=90)
hoja.save(f'{SP}/variantes.jpg', quality=92)
