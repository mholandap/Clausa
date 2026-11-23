"""Gera a máscara (matte) da pessoa em cada quadro de um vídeo, com o Robust Video Matting (RVM).

Uso:  python3 recortar_pessoa.py ENTRADA.mp4 SAIDA_mascara.mkv MODELO.onnx [downsample=0.25] [ate_quadro]
A máscara sai em tons de cinza (branco = pessoa), mesmo tamanho e fps da entrada, sem compressão com perda.
Serve para colocar texto "atrás" da pessoa: base + texto + (base recortada pela máscara) + texto da frente.

Modelo: rvm_mobilenetv3_fp32.onnx (github.com/PeterL1n/RobustVideoMatting, licença GPL-3.0 — usado só como
ferramenta, não é redistribuído neste repositório).
"""
import subprocess, sys, json, time
import numpy as np, onnxruntime as ort

src, dst, modelo = sys.argv[1:4]
ds = float(sys.argv[4]) if len(sys.argv) > 4 else 0.25
limite = int(sys.argv[5]) if len(sys.argv) > 5 else None
info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                                  '-of', 'json', src], capture_output=True, text=True).stdout)['streams'][0]
W, H, fps = info['width'], info['height'], info['r_frame_rate']
leitor = subprocess.Popen(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
escritor = subprocess.Popen(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{W}x{H}', '-r', fps,
                             '-i', '-', '-c:v', 'ffv1', dst], stdin=subprocess.PIPE)
s = ort.InferenceSession(modelo, providers=['CPUExecutionProvider'])
rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
n, t0 = 0, time.time()
while True:
    buf = leitor.stdout.read(W * H * 3)
    if len(buf) < W * H * 3 or (limite and n >= limite):
        break
    x = np.frombuffer(buf, np.uint8).reshape(H, W, 3).transpose(2, 0, 1)[None].astype(np.float32) / 255
    fgr, pha, *rec = s.run(None, {'src': x, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3],
                                 'downsample_ratio': np.array([ds], np.float32)})
    escritor.stdin.write((np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8).tobytes())
    n += 1
    if n % 60 == 0:
        print(f'{n} quadros, {n / (time.time() - t0):.1f} q/s', flush=True)
leitor.kill(); escritor.stdin.close(); escritor.wait()
print(f'pronto: {n} quadros em {time.time() - t0:.0f} s')
