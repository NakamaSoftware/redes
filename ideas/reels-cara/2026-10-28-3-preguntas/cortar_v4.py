# Cortes de la versión 4: sin la mano que va al celular. Planos en espejo; en dos planos se congela el último cuadro limpio.
import json, os, subprocess
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trabajo'); os.chdir(T)
# (parte, desde, hasta, congelar desde · segundos dentro del plano o None)
CORTES = [(1, .95, 5.30, None), (2, .70, 7.55, None), (3, .15, 1.30, None), (3, 1.70, 4.95, None),
          (3, 5.65, 8.75, 2.80), (4, .75, 6.28, None), (5, .30, 3.80, 3.24), (6, .85, 3.30, None)]
def run(*c): subprocess.run(c, check=True)
ini, t = [], 0.0
for n, (p, a, b, h) in enumerate(CORTES):
    d = b - a
    vf = 'fps=30,hflip,setsar=1,format=yuv420p'
    if h is not None: vf = f'fps=30,hflip,trim=0:{h:.3f},tpad=stop_mode=clone:stop_duration={d-h+0.1:.3f},trim=0:{d:.3f},setsar=1,format=yuv420p'
    run('ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-t', f'{d:.3f}', '-i', f'parte{p}.mov', '-map_metadata', '-1', '-vf', vf,
        '-af', f'afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast',
        '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '1', '-t', f'{d:.3f}', f'v4/{n}.mov')
    ini.append(round(t, 4)); t += d
open('v4/lista.txt', 'w').write(''.join(f"file '{n}.mov'\n" for n in range(len(CORTES))))
run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'v4/lista.txt', '-c', 'copy', 'v4/base.mov')
run('ffmpeg', '-v', 'error', '-y', '-i', 'v4/base.mov', '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', 'v4/base-video.mp4')
json.dump({'cortes': CORTES, 'ini': ini, 'duracion': t}, open('v4/cortes.json', 'w'), indent=1)
print(f'✓ base v4 · {t:.2f} s · inicios {ini}')
