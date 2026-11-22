# Trilha do anúncio: narração (já tratada, 44.1k) + música com ducking + efeitos sincronizados ao timing.js
import json, re, sys, wave, numpy as np
voice_path, timing_js, out = sys.argv[1:4]
TM=json.loads(re.search(r'window\.TIMING=(.*);',open(timing_js).read()).group(1)); L=TM['lines']; D=TM['dur']
SR=44100; N=int(D*SR); rng=np.random.default_rng(5)
w=wave.open(voice_path); vx=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32767
if w.getnchannels()==2: vx=vx.reshape(-1,2).mean(1)
voice=np.zeros(N); voice[:min(N,len(vx))]=vx[:N]
mus=np.zeros((N,2)); sfx=np.zeros((N,2))
def tt(d): return np.arange(int(d*SR))/SR
def put(buf,sig,t,g=1.,pan=0.):
    i=int(t*SR); 
    if i>=N or i<0: return
    j=min(N,i+len(sig)); s=sig[:j-i]*g; buf[i:j,0]+=s*(1-max(0,pan)); buf[i:j,1]+=s*(1+min(0,pan))
def band(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
W=lambda l,k:L[l]['words'][k]['t0']; LS=lambda l:L[l]['start']; LE=lambda l:L[l]['end']

# ---- música: pluck em Lá menor, 100 bpm ----
B=60/100
def pluck(f,d=.9):
    t=tt(d); ph=2*np.pi*f*t
    return (np.sin(ph)+.5*np.sin(2*ph)*np.exp(-t*9)+.25*np.sin(3*ph)*np.exp(-t*14))*np.exp(-t*5.5)*np.minimum(1,t/.004)
def padc(fs,d):
    t=tt(d); s=sum(np.sin(2*np.pi*f*t+rng.random()*6)*(1+.2*np.sin(2*np.pi*.25*t)) for f in fs)/len(fs)
    return s*np.minimum(1,t/.6)*np.minimum(1,(d-t)/.6)
prog=[(220,[220,261.63,329.63],[110,164.81]),(174.61,[174.61,220,261.63],[87.31,130.81]),
      (261.63,[196,261.63,329.63],[130.81,196]),(196,[196,246.94,293.66],[98,146.83])]
end_music=LS(7)-.15; t0=0; bar=0
while t0<end_music:
    root,ch,pd=prog[bar%4]
    put(mus,padc([x for x in ch],4*B+.4),t0,.10)
    arp=[ch[0],ch[1],ch[2],ch[1]*2,ch[2],ch[1],ch[0]*2,ch[2]]
    for k,f in enumerate(arp):
        tk=t0+k*B/2
        if tk<end_music: put(mus,pluck(f),tk,.11,(-.35,.35)[k%2])
    tb=tt(4*B); put(mus,np.sin(2*np.pi*pd[0]/2*tb)*np.minimum(1,tb/.03)*np.exp(-tb*.5),t0,.20)
    for k in range(4):
        tk=t0+k*B
        if tk>LS(1)-.3 and tk<end_music:
            t=tt(.3); put(mus,np.sin(2*np.pi*np.cumsum(50+70*np.exp(-t*35))/SR)*np.exp(-t*10),tk,.32)
            if k%2: t=tt(.18); put(mus,band(rng.standard_normal(len(t)),1200,7000)*np.exp(-t*28),tk,.07)
        t=tt(.05); put(mus,band(rng.standard_normal(len(t)),8000,15000)*np.exp(-t*80),tk+B/2,.035,.3)
    t0+=4*B; bar+=1
# acorde final da marca
t=tt(3.2); fin=sum(np.sin(2*np.pi*f*t)*np.exp(-t*1.1) for f in [220,277.18,329.63,440,554.37])/5
put(mus,fin,LS(7)-.1,.30)

# ---- ducking: música baixa quando a voz fala ----
hop=441; env=np.array([np.sqrt(np.mean(voice[k:k+hop]**2)) for k in range(0,N,hop)])
env=np.convolve(env,np.ones(15)/15,mode='same'); env=np.clip(env/(env.max()+1e-9)*3,0,1)
g=np.repeat(1-.62*env,hop)[:N]; mus*=g[:,None]

# ---- efeitos ----
def whoosh(d=.55,lo=500,hi=6000):
    t=tt(d); return band(rng.standard_normal(len(t)),lo,hi)*np.sin(np.pi*t/d)**2.2
def pop(f=900):
    t=tt(.35); return (np.sin(2*np.pi*f*t*(1+.6*np.exp(-t*40)))*np.exp(-t*18))
def tick():
    t=tt(.03); return band(rng.standard_normal(len(t)),2000,9000)*np.exp(-t*160)
for tw in [LS(1)-.32,LS(2)-.3,LS(6)-.45,LS(7)-.4]: put(sfx,whoosh(),tw,.16)
for k in range(15): put(sfx,tick(),W(1,0)+.55*(1-(1-k/15)**(1/3)),.12,(-.2,.2)[k%2])
t=tt(LE(2)-W(2,5)+.3); f=280+900*(t/t[-1])**2
put(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t/t[-1])*.6+band(rng.standard_normal(len(t)),3000,9000)*.15*(t/t[-1]),W(2,5)-.25,.08)
for (l,k),f in zip([(3,2),(4,0),(5,0)],[880,740,880]): put(sfx,pop(f),W(l,k)+.05,.22)
t=tt(.9); put(sfx,(np.sin(2*np.pi*1318.5*t)+.6*np.sin(2*np.pi*1975.5*t))*np.exp(-t*6),LE(5)+.42,.12)
t=tt(.25); put(sfx,np.sin(2*np.pi*np.cumsum(90+120*np.exp(-t*30))/SR)*np.exp(-t*14),LS(7)-.1,.35)

# ---- master ----
mix=mus+sfx+np.stack([voice,voice],1)*1.0
fade=np.ones(N); fo=int(.6*SR); fade[-fo:]=np.linspace(1,0,fo); mix*=fade[:,None]
mix=np.tanh(mix*1.2)/np.tanh(1.2); mix/=np.abs(mix).max()/.8
w=wave.open(out,'wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((mix*32767).astype('<i2').tobytes());w.close()
print('mix ok',round(D,2),'s')
