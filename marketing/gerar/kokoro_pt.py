# Kokoro-82M (ONNX) + espeak-ng pt-br -> WAV 24 kHz
import re, subprocess, sys, json, wave, numpy as np, onnxruntime as ort
from vocab import V
E2M=sorted({'a^ɪ':'I','a^ʊ':'W','d^z':'ʣ','d^ʒ':'ʤ','e^ɪ':'A','o^ʊ':'O','ə^ʊ':'Q','s^s':'S','t^s':'ʦ','t^ʃ':'ʧ','ɔ^ɪ':'Y'}.items())
def esp(txt):
    out=subprocess.run(['espeak-ng','-q','-v','pt-br','--ipa','--tie=^',txt],capture_output=True,text=True).stdout
    return ' '.join(out.split())
def phonemize(text):
    parts=re.split(r'([,.!?;:…—])',text); ps=''
    for p in parts:
        if not p.strip(): continue
        if re.fullmatch(r'[,.!?;:…—]',p): ps=ps.rstrip()+p+' '
        else: ps+=esp(p.strip())+' '
    for a,b in E2M: ps=ps.replace(a,b)
    ps=ps.replace('^','').replace('‍','')
    # maiúsculas especiais (I,W,A,O,Q,S,Y) só existem nos ids deslocados do v1.0
    return ps.strip()
UP={'A':24,'I':25,'O':31,'Q':33,'S':35,'W':39,'Y':41}
def tokens(ps):
    ids=[];unk=set()
    for c in ps:
        if c in V: ids.append(V[c])
        elif c in UP: ids.append(UP[c])
        else: unk.add(c)
    return ids,unk
SESS=None
def synth(text,voice,speed=1.0,model=None):
    global SESS
    if SESS is None: SESS=ort.InferenceSession(model)
    ps=phonemize(text); ids,unk=tokens(ps)
    v=np.fromfile(voice,dtype=np.float32).reshape(-1,1,256)
    st=v[min(len(ids),len(v)-1)]
    wav=SESS.run(None,{'input_ids':np.array([[0]+ids+[0]],dtype=np.int64),'style':st.astype(np.float32),'speed':np.array([speed],dtype=np.float32)})[0][0]
    return wav,ps,unk
def save(path,wav,sr=24000):
    w=wave.open(path,'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
    w.writeframes((np.clip(wav,-1,1)*32767).astype('<i2').tobytes());w.close()
if __name__=='__main__':
    cfg=json.load(open(sys.argv[1])); out={}
    for i,line in enumerate(cfg['lines']):
        wav,ps,unk=synth(line,cfg['voice'],cfg.get('speed',1.0),cfg['model'])
        # corta silêncio das pontas
        a=np.where(np.abs(wav)>0.01)[0]; wav=wav[max(0,a[0]-240):a[-1]+1200] if len(a) else wav
        p=f"{cfg['out']}_{i}.wav"; save(p,wav); out[i]={'text':line,'ps':ps,'unk':''.join(unk),'dur':round(len(wav)/24000,3),'peak':round(float(np.abs(wav).max()),3)}
    json.dump(out,open(cfg['out']+'.json','w'),ensure_ascii=False,indent=1)
    for k,v in out.items(): print(k,v['dur'],'s |',v['text'],'|',v['ps'],('| UNK:'+v['unk']) if v['unk'] else '')
