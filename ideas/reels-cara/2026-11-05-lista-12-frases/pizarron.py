# Pizarrón del gancho de P1 (pantalla partida): crema de y 0 a 740, línea noche abajo, logo claro arriba a la derecha.
import sys
from PIL import Image, ImageDraw, ImageFont
sys.argv, SAL = sys.argv[:1] + ['/tmp', '/dev/null'], sys.argv[1]
exec(open(__file__.replace('pizarron.py', 'lista.py')).read().split('FRASES = [')[0])
im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
g.rectangle([0, 0, 1080, 740], fill=(237, 231, 219, 255)); g.line([(0, 740), (1080, 740)], fill=NOCHE, width=4)
for x in range(0, 1080, 40): g.line([(x, 0), (x, 738)], fill=(230, 223, 210, 255))
for y in range(0, 738, 40): g.line([(0, y), (1080, y)], fill=(230, 223, 210, 255))
g.rectangle([110, 330, 126, 346], fill=ROJO); g.text((142, 348), 'SACALE CAPTURA', font=mono(30), fill=GRIS, anchor='ls')
g.text((110, 480), '12 frases para', font=SER(110), fill=NOCHE, anchor='ls')
g.text((110, 600), 'pegarle a ', font=SER(110), fill=NOCHE, anchor='ls')
g.text((110 + SER(110).getlength('pegarle a '), 600), 'ChatGPT', font=SERI(110), fill=ROJO, anchor='ls')
ponlogo(im); im.save(SAL)
