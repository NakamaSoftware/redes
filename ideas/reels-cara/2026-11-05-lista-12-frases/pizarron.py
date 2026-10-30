# Uso: python3 pizarron.py <salida.png> [etiqueta línea1 línea2 [alto]]
# Pizarrón del gancho de P1 (pantalla partida): crema de y 0 a 740, línea noche abajo, logo claro arriba a la derecha.
import sys
from PIL import Image, ImageDraw, ImageFont
SAL = sys.argv[1]; ETIQ, L1, L2, ALTO = (sys.argv[2:5] + [740])[:4] if len(sys.argv) > 4 else ('SACALE CAPTURA', '12 frases para', 'pegarle a ', 740); ALTO = int(sys.argv[5]) if len(sys.argv) > 5 else 740; sys.argv = sys.argv[:1] + ['/tmp', '/dev/null']
exec(open(__file__.replace('pizarron.py', 'lista.py')).read().split('FRASES = [')[0])
im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
g.rectangle([0, 0, 1080, ALTO], fill=(237, 231, 219, 255)); g.line([(0, ALTO), (1080, ALTO)], fill=NOCHE, width=4)
for x in range(0, 1080, 40): g.line([(x, 0), (x, ALTO - 2)], fill=(230, 223, 210, 255))
for y in range(0, ALTO - 2, 40): g.line([(0, y), (1080, y)], fill=(230, 223, 210, 255))
dy = ALTO - 740; g.rectangle([110, 330 + dy, 126, 346 + dy], fill=ROJO); g.text((142, 348 + dy), ETIQ, font=mono(30), fill=GRIS, anchor='ls')
g.text((110, 480 + dy), L1, font=SER(110), fill=NOCHE, anchor='ls')
g.text((110, 600 + dy), L2, font=SER(110), fill=NOCHE, anchor='ls')
g.text((110 + SER(110).getlength(L2), 600 + dy), 'ChatGPT', font=SERI(110), fill=ROJO, anchor='ls')
ponlogo(im); im.save(SAL)
