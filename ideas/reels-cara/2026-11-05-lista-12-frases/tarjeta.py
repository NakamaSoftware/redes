# Gancho de P1 en look C: tarjeta de vidrio compacta (una línea) arriba de la cabeza, sacada de un cuadro de la toma.
# Uso: python3 tarjeta.py <cuadro.png> <salida.png> [etiqueta texto palabra-en-serif]
#   → capa RGBA con la tarjeta y el logo, para ponerla encima del video. Si el texto no entra en una línea, usa dos.
import sys
from PIL import Image, ImageDraw, ImageChops, ImageFilter
CUADRO, SAL = sys.argv[1], sys.argv[2]
ETIQ, TXT, SERIF = sys.argv[3:6] if len(sys.argv) > 5 else ('SACALE CAPTURA', '12 frases para ', 'ChatGPT')
sys.argv = sys.argv[:1] + ['/tmp', '/dev/null']
exec(open(__file__.replace('tarjeta.py', 'lista.py')).read().split('FRASES = [')[0])
base = Image.open(CUADRO).convert('RGBA'); im = base.copy()
X0, Y0, X1 = 110, 232, 836
f, s = inter(56, 780), SERI(78)
una = X0 + 42 + f.getlength(TXT) + s.getlength(SERIF) <= X1 - 36
if una:  # achica hasta 42 px antes de pasar a dos líneas
    for px in range(60, 40, -2):
        f, s = inter(px, 780), SERI(round(px * 1.4))
        if X0 + 42 + f.getlength(TXT) + s.getlength(SERIF) <= X1 - 36: break
Y1 = Y0 + 160 if una else Y0 + 236
vidrio(im, (X0, Y0, X1, Y1)); g = ImageDraw.Draw(im)
g.rectangle([X0 + 42, Y0 + 40, X0 + 58, Y0 + 56], fill=ROJO); g.text((X0 + 74, Y0 + 58), ETIQ, font=mono(28), fill=NOCHE+(170,), anchor='ls')
if una:
    g.text((X0 + 42, Y0 + 128), TXT, font=f, fill=NOCHE, anchor='ls')
    g.text((X0 + 42 + f.getlength(TXT), Y0 + 132), SERIF, font=s, fill=ROJO, anchor='ls')
else:  # corta el texto en la palabra que mejor equilibra las dos líneas; la serif va al final de la segunda
    pal = TXT.split(); k = min(range(1, len(pal)), key=lambda i: abs(f.getlength(' '.join(pal[:i])) - f.getlength(' '.join(pal[i:]) + ' ') - s.getlength(SERIF)))
    l1, l2 = ' '.join(pal[:k]), ' '.join(pal[k:]) + ' '
    g.text((X0 + 42, Y0 + 132), l1, font=f, fill=NOCHE, anchor='ls'); g.text((X0 + 42, Y0 + 204), l2, font=f, fill=NOCHE, anchor='ls')
    g.text((X0 + 42 + f.getlength(l2), Y0 + 208), SERIF, font=s, fill=ROJO, anchor='ls')
ponlogo(im)
m = ImageChops.difference(im.convert('RGB'), base.convert('RGB')).convert('L').point(lambda p: 255 if p > 2 else 0).filter(ImageFilter.MaxFilter(9))
im.putalpha(m); im.save(SAL)
