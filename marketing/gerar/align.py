# Alinha uma locução gravada (frases separadas por pausas) ao roteiro -> voz.wav + timing.js
import json, sys, re, subprocess, wave, numpy as np
src, out_wav, out_js, cfgp = sys.argv[1:5]
cfg=json.load(open(cfgp))
w=wave.open(src); SR=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32767
hop=SR//100; e=np.array([np.sqrt(np.mean(x[k:k+hop]**2)) for k in range(0,len(x)-hop,hop)])
th=max(.01,np.percentile(e,95)*.08); v=e>th; segs=[]; k=0
while k<len(v):
    if v[k]:
        j=k
        while j<len(v) and (v[j] or (j+12<len(v) and v[j:j+12].any())): j+=1
        segs.append([k/100,j/100]); k=j
    else: k+=1
sents=[s for line in cfg['lines'] for s in re.split(r'(?<=[.?!])\s+',line.strip()) if s]
assert len(segs)==len(sents), f'{len(segs)} trechos de fala para {len(sents)} frases'
# insere silêncio depois de certas frases (índice da frase -> segundos)
ins={int(k):v for k,v in cfg.get('insert_after',{}).items()}
pieces=[]; cur=0; shift=0; S=[]
for i,(a,b) in enumerate(segs):
    S.append((a+shift,b+shift))
    if i in ins:
        cut=int(((b+segs[i+1][0])/2)*SR); pieces.append(x[cur:cut]); pieces.append(np.zeros(int(ins[i]*SR))); cur=cut; shift+=ins[i]
pieces.append(x[cur:]); y=np.concatenate(pieces)
lead=cfg.get('lead',0.3); y=np.concatenate([np.zeros(int(lead*SR)),y]); S=[(a+lead,b+lead) for a,b in S]
def plen(word):
    ps=subprocess.run(['espeak-ng','-q','-v','pt-br','--ipa',re.sub(r'[^\wÀ-ú%]','',word)],capture_output=True,text=True).stdout
    return max(1,len(re.sub(r'[ˈˌ\s‍]','',ps)))
lines=[]; si=0
for line in cfg['lines']:
    ss=[s for s in re.split(r'(?<=[.?!])\s+',line.strip()) if s]; words=[]
    for s in ss:
        a,b=S[si]; si+=1; ws=s.split(); L=[plen(t)+(2 if re.search(r'[,;]$',t) else 0) for t in ws]; tot=sum(L); c=0
        for t,l in zip(ws,L): words.append({'w':t,'t0':round(a+(b-a)*c/tot,3),'t1':round(a+(b-a)*(c+l)/tot,3)}); c+=l
    lines.append({'start':words[0]['t0'],'end':words[-1]['t1'],'words':words})
dur=round(lines[-1]['end']+cfg.get('tail',1.3),2); y=y[:int(dur*SR)]
if len(y)<int(dur*SR): y=np.concatenate([y,np.zeros(int(dur*SR)-len(y))])
o=wave.open(out_wav,'wb');o.setnchannels(1);o.setsampwidth(2);o.setframerate(SR);o.writeframes((np.clip(y,-1,1)*32767).astype('<i2').tobytes());o.close()
open(out_js,'w').write('window.TIMING='+json.dumps({'dur':dur,'lines':lines},ensure_ascii=False)+';\n')
for l in lines: print(f"{l['start']:6.2f}-{l['end']:6.2f}",' '.join(f"{t['w']}@{t['t0']}" for t in l['words']))
print('duração total:',dur)
