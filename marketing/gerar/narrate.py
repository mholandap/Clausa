# Narração: sintetiza frase a frase (Kokoro pt-br), monta a linha do tempo e estima o tempo das palavras
import json, sys, re, subprocess, numpy as np
from kokoro_pt import synth, save
cfg=json.load(open(sys.argv[1])); SR=24000
track=np.zeros(int(60*SR),dtype=np.float32); lines=[]; prev_end=0.0
def plen(w):
    ps=subprocess.run(['espeak-ng','-q','-v','pt-br','--ipa',re.sub(r'[^\wÀ-ú%]','',w)],capture_output=True,text=True).stdout
    return max(1,len(re.sub(r'[ˈˌ\s‍]','',ps)))
def trim(x):
    a=np.where(np.abs(x)>0.008)[0]; return x[max(0,a[0]-120):a[-1]+360] if len(a) else x
for line,gap in zip(cfg['lines'],cfg['gaps']):
    st=round(prev_end+gap,3)
    sents=[s for s in re.split(r'(?<=[.?!])\s+',line.strip()) if s]
    t=st; words=[]
    for si,s in enumerate(sents):
        x,ps,unk=synth(s,cfg['voice'],cfg.get('speed',1.0),cfg['model']); x=trim(x)
        if unk: print('  aviso, fonemas ignorados:',unk)
        a=int(t*SR); track[a:a+len(x)]+=x[:max(0,len(track)-a)]
        d=len(x)/SR; ws=s.split(); L=[plen(w)+(2 if re.search(r'[,;]$',w) else 0) for w in ws]; tot=sum(L); c=0
        for w,l in zip(ws,L):
            words.append({'w':w,'t0':round(t+d*c/tot,3),'t1':round(t+d*(c+l)/tot,3)}); c+=l
        t+=d+(cfg.get('pause',.22) if si<len(sents)-1 else 0)
    lines.append({'start':st,'end':round(t,3),'words':words}); prev_end=t
    print(f"{st:5.2f}-{t:5.2f}", ' '.join(f"{w['w']}@{w['t0']}" for w in words))
for a,b in zip(lines,lines[1:]):
    if a['end']>b['start']-0.12: print('  ATENÇÃO: sobreposição entre', a['words'][0]['w'], 'e', b['words'][0]['w'])
cfg['dur']=round(prev_end+cfg.get('tail',1.3),2); track=track[:int(cfg['dur']*SR)]
track=track/np.abs(track).max()*.95; save(cfg['out_wav'],track); print('duração total:',cfg['dur'])
open(cfg['out_js'],'w').write('window.TIMING='+json.dumps({'dur':cfg['dur'],'lines':lines},ensure_ascii=False)+';\n')
