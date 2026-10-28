import sys, runpy
SP = sys.argv[1]; sys.argv = ['x', SP]
L = runpy.run_path(f'{SP}/look-c-claro.py')   # reutiliza fuentes, colores, logo y vidrio
from PIL import Image, ImageDraw
inter, mono, serif, base, capa, sombra, ponlogo, vidrio = (L[k] for k in ('inter','mono','serif','base','capa','sombra','ponlogo','vidrio'))
NOCHE, BLANCO, ROJO = L['NOCHE'], L['BLANCO'], L['ROJO']
def subt(n, linea, clave):
    im = base(n); ly = capa(im); g = ImageDraw.Draw(ly)
    g.text((540, 1330), linea, font=inter(66, 800), fill=BLANCO, anchor='ms')
    k = inter(112, 900); w = k.getlength(clave)
    g.rounded_rectangle([540-w/2-30, 1362, 540+w/2+30, 1490], 22, fill=ROJO)
    g.text((540, 1466), clave, font=k, fill=BLANCO, anchor='ms')
    sombra(im, ly, 20, 170, 6); ponlogo(im); return im
a = subt(3, 'te pregunta lo que no', 'PENSASTE')
# tarjeta de vidrio a mitad del video: los casos de uso
b = base(4); vidrio(b, (100, 330, 840, 590)); g = ImageDraw.Draw(b)
g.rectangle([146, 378, 162, 394], fill=ROJO); g.text((178, 396), 'SIRVE PARA', font=mono(28), fill=NOCHE+(170,), anchor='ls')
f = inter(52, 750)
for i, t in enumerate(['Un mail difícil', 'Un viaje de cuatro días']):
    y = 478 + i*74; g.rounded_rectangle([146, y-40, 182, y-4], 9, fill=ROJO); g.line([(154, y-22), (161, y-14), (175, y-30)], fill=BLANCO, width=5, joint='curve'); g.text((202, y), t, font=f, fill=NOCHE, anchor='ls')
ly = capa(b); g2 = ImageDraw.Draw(ly)
g2.text((540, 1330), 'sirve para un', font=inter(66, 800), fill=BLANCO, anchor='ms')
k = inter(112, 900); w = k.getlength('MAIL'); g2.rounded_rectangle([540-w/2-30, 1362, 540+w/2+30, 1490], 22, fill=ROJO); g2.text((540, 1466), 'MAIL', font=k, fill=BLANCO, anchor='ms')
sombra(b, ly, 20, 170, 6); ponlogo(b)
W, H, pad = 450, 800, 24
hoja = Image.new('RGB', (2*W+3*pad, H+130), L['CREMA']); gh = ImageDraw.Draw(hoja)
gh.text((pad, 24), 'Muestra final · look C claro', font=inter(40, 750), fill=NOCHE)
gh.text((pad, 80), 'subtítulo', font=mono(22, 500), fill=(110,110,100)); gh.text((2*pad+W, 80), 'tarjeta + subtítulo', font=mono(22, 500), fill=(110,110,100))
hoja.paste(a.convert('RGB').resize((W, H)), (pad, 112)); hoja.paste(b.convert('RGB').resize((W, H)), (2*pad+W, 112))
hoja.save(f'{SP}/muestra-final.jpg', quality=92)
