# Reducción de reverberación tardía (Lebart et al. 2001): resta espectral de la cola estimada a partir del T60 de la habitación.
import sys, subprocess, numpy as np
from scipy.signal import stft, istft
ent, sal, T60 = sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.45
sr = 48000
a = subprocess.run(['ffmpeg', '-v', 'error', '-i', ent, '-vn', '-f', 's16le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True, check=True).stdout
x = np.frombuffer(a, np.int16).astype(np.float64) / 32768
n, hop = 1024, 256
f, t, X = stft(x, sr, nperseg=n, noverlap=n - hop)
P = np.abs(X) ** 2
D = int(round(0.05 * sr / hop))                               # la cola tardía empieza ~50 ms después del sonido directo
alfa = np.exp(-2 * (3 * np.log(10) / T60) * D * hop / sr)     # cuánto decae la energía en ese tiempo
Ps = np.copy(P)
for i in range(1, P.shape[1]): Ps[:, i] = 0.6 * Ps[:, i - 1] + 0.4 * P[:, i]   # suavizado temporal
Pl = np.zeros_like(P); Pl[:, D:] = alfa * Ps[:, :-D]
G = np.maximum(1 - Pl / (P + 1e-12), 0.12)                    # piso de -18 dB para que no suene a robot
for i in range(1, G.shape[1]): G[:, i] = np.maximum(G[:, i], 0.7 * G[:, i - 1])   # sin «parpadeos»
_, y = istft(X * np.sqrt(G), sr, nperseg=n, noverlap=n - hop)
y = y[:len(x)]; y = np.clip(y, -1, 1)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(sr), '-ac', '1', '-i', '-', sal], input=(y * 32767).astype(np.int16).tobytes(), check=True)
