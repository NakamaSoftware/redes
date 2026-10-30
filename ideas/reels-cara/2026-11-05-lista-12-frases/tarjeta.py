# Gancho de P1 en look C: tarjeta de vidrio compacta (una línea) arriba de la cabeza, sacada de un cuadro de la toma.
# Uso: python3 tarjeta.py <cuadro.png> <salida.png>   → capa RGBA con la tarjeta y el logo, para ponerla encima del video
import sys
from PIL import Image, ImageDraw, ImageChops, ImageFilter
CUADRO, SAL = sys.argv[1], sys.argv[2]
sys.argv = sys.argv[:1] + ['/tmp', '/dev/null']
exec(open(__file__.replace('tarjeta.py', 'lista.py')).read().split('FRASES = [')[0])
base = Image.open(CUADRO).convert('RGBA'); im = base.copy()
X0, Y0, X1, Y1 = 110, 232, 836, 392
vidrio(im, (X0, Y0, X1, Y1)); g = ImageDraw.Draw(im)
g.rectangle([X0 + 42, Y0 + 40, X0 + 58, Y0 + 56], fill=ROJO); g.text((X0 + 74, Y0 + 58), 'SACALE CAPTURA', font=mono(28), fill=NOCHE+(170,), anchor='ls')
for px in range(60, 40, -2):
    f, s = inter(px, 780), SERI(round(px * 1.4))
    if X0 + 42 + f.getlength('12 frases para ') + s.getlength('ChatGPT') <= X1 - 36: break
g.text((X0 + 42, Y0 + 128), '12 frases para ', font=f, fill=NOCHE, anchor='ls')
g.text((X0 + 42 + f.getlength('12 frases para '), Y0 + 132), 'ChatGPT', font=s, fill=ROJO, anchor='ls')
ponlogo(im)
m = ImageChops.difference(im.convert('RGB'), base.convert('RGB')).convert('L').point(lambda p: 255 if p > 2 else 0).filter(ImageFilter.MaxFilter(9))
im.putalpha(m); im.save(SAL)
