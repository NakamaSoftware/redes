"""Recorta a la persona de un vídeo (para texto detrás de la cabeza) SIN halo.

Fotograma a fotograma con rembg (u2net_human_seg, ~0,2 s/fotograma), máscara erosionada 2 px y despill del color de fondo
(por defecto azul: las luces del estudio dejan un borde azulado). Salida, en la carpeta del vídeo:
  <nombre>-color.mp4    la toma con el despill (va DEBAJO de la máscara)
  <nombre>-mascara.mp4  blanco = persona (mate de luminancia)
Muchos editores (Viegas Editor, algunos Premiere) ignoran el alfa de ProRes 4444: por eso se entrega como pareja color + máscara.
Uso: python recortar.py toma.mp4 [--fps 30] [--despill blue|green|none]
Requiere: pip install rembg onnxruntime pillow · ffmpeg
"""
import argparse, os, subprocess, tempfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video'); ap.add_argument('--fps', type=int, default=30); ap.add_argument('--despill', default='blue')
    a = ap.parse_args()
    from rembg import remove, new_session
    from PIL import Image
    base = os.path.splitext(os.path.abspath(a.video))[0]
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(f'{tmp}/in'); os.makedirs(f'{tmp}/m')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.video, '-vf', f'fps={a.fps}', f'{tmp}/in/%05d.png'], check=True)
        s = new_session('u2net_human_seg'); fs = sorted(os.listdir(f'{tmp}/in'))
        for i, f in enumerate(fs):
            remove(Image.open(f'{tmp}/in/{f}'), session=s, only_mask=True).save(f'{tmp}/m/{f}')
            if i % 100 == 0: print(f'{i}/{len(fs)}', flush=True)
        # máscara: más contraste en el pelo (que no transparente), 2 px hacia dentro (sin borde de fondo) y borde suave
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(a.fps), '-i', f'{tmp}/m/%05d.png', '-vf',
                        "format=gray,lutyuv=y='clip((val-30)*1.6,0,255)',erosion,erosion,gblur=sigma=0.7,format=yuv420p",
                        '-c:v', 'libx264', '-crf', '14', f'{base}-mascara.mp4'], check=True)
    vf = f'fps={a.fps}' + (f',despill=type={a.despill}:mix=0.6:expand=0.1' if a.despill != 'none' else '')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.video, '-vf', vf, '-an', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', f'{base}-color.mp4'], check=True)
    print(f'✓ {base}-color.mp4 y {base}-mascara.mp4')


if __name__ == '__main__':
    main()
