# Post «un mes de reels con Claude»: texto grande en Instrument Serif, centrado, encima de un video tranquilo (sin cara).
# Uso: python3 texto.py <salida.png>   → capa RGBA 1080×1920 con el texto y su sombra
#      después: python3 texto.py capa.png && ffmpeg -i broll.mov -i capa.png -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=-0.06[v];[v][1:v]overlay" -t 8 post.mp4
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = '/home/user/redes/marca/fuentes/'
SER, SERI = ImageFont.truetype(F + 'InstrumentSerif-Regular.ttf', 92), ImageFont.truetype(F + 'InstrumentSerif-Italic.ttf', 92)
# cada línea es una lista de (texto, cursiva)
LINEAS = [[('Le pedí a Claude', False)], [('que me armara ', False), ('un mes', True)], [('de reels', True), ('. Estos son', False)],
          [('los 7 pedidos', False)], [('que le hice', False)]]
capa = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); g = ImageDraw.Draw(capa)
ALTO = 104; y0 = 960 - ALTO * len(LINEAS) // 2 + 60
for i, linea in enumerate(LINEAS):
    ancho = sum((SERI if c else SER).getlength(t) for t, c in linea); x = 540 - ancho / 2
    for t, c in linea:
        f = SERI if c else SER; g.text((x, y0 + i * ALTO), t, font=f, fill=(255, 255, 255, 255) if not c else (245, 214, 190, 255), anchor='ls'); x += f.getlength(t)
sombra = Image.new('RGBA', capa.size, (0, 0, 0, 0)); sombra.putalpha(capa.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda p: p * 150 // 255))
fin = Image.new('RGBA', capa.size, (0, 0, 0, 0)); fin.alpha_composite(sombra, (0, 4)); fin.alpha_composite(capa)
fin.save(sys.argv[1])
