# Trilha lo-fi sintetizada (sem samples de terceiros) + whoosh nos cortes + "pop" no final
import sys, json, wave, numpy as np
dur=float(sys.argv[1]); cuts=json.loads(sys.argv[2]); pop_at=float(sys.argv[3]); out=sys.argv[4]
SR=44100; N=int(dur*SR); rng=np.random.default_rng(11); mix=np.zeros((N,2))
def tt(d): return np.arange(int(d*SR))/SR
def put(sig,t,g=1.,pan=0.):
    i=int(t*SR)
    if i>=N: return
    j=min(N,i+len(sig)); s=sig[:j-i]*g; mix[i:j,0]+=s*(1-max(0,pan)); mix[i:j,1]+=s*(1+min(0,pan))
def band(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
B=60/88
def ep(f,d):
    t=tt(d); ph=2*np.pi*f*np.cumsum(1+.003*np.sin(2*np.pi*.5*t))/SR
    return (np.sin(ph)+.3*np.sin(2*ph)*np.exp(-t*3))*np.minimum(1,t/.012)*np.exp(-t*.6)*(1+.1*np.sin(2*np.pi*4*t))
chords=[[220,261.63,329.63,392],[174.61,220,261.63,329.63],[261.63,329.63,392,493.88],[196,246.94,293.66,349.23]]
bass=[110,87.31,130.81,98]
t0=0;k=0
while t0<dur:
    for n,f in enumerate(chords[k%4]): put(ep(f,4*B+1.2),t0+n*.02,.085,(-.3,.3,-.15,.15)[n])
    tb=tt(4*B); put(np.sin(2*np.pi*bass[k%4]*tb)*np.minimum(1,tb/.02)*np.exp(-tb*.8),t0,.2)
    for q in range(4):
        tq=t0+q*B
        tk=tt(.3); put(np.sin(2*np.pi*np.cumsum(48+80*np.exp(-tk*30))/SR)*np.exp(-tk*9),tq,.38 if q in (0,2) else 0)
        if q in (1,3): ts=tt(.22); put(band(rng.standard_normal(len(ts)),900,6000)*np.exp(-ts*22),tq,.10)
        th=tt(.05); put(band(rng.standard_normal(len(th)),7000,14000)*np.exp(-th*70),tq+B*.5,.04,.25)
    t0+=4*B;k+=1
crk=band(rng.standard_normal(N),2000,9000)*.003; mix[:,0]+=crk; mix[:,1]+=crk
for c in cuts:
    d=.5; t=tt(d); put(band(rng.standard_normal(len(t)),500,6000)*np.sin(np.pi*t/d)**2.2,c-.25,.12)
t=tt(.35); put(np.sin(2*np.pi*880*t*(1+.5*np.exp(-t*40)))*np.exp(-t*16),pop_at,.18)
fade=np.ones(N); fi=int(.3*SR); fo=int(1.6*SR); fade[:fi]=np.linspace(0,1,fi); fade[-fo:]=np.linspace(1,0,fo)
mix*=fade[:,None]; mix=np.tanh(mix*1.4)/np.tanh(1.4); mix/=np.abs(mix).max()/.8
w=wave.open(out,'wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((mix*32767).astype('<i2').tobytes());w.close()
print('trilha ok')
