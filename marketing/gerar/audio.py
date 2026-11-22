# Trilha lo-fi + sons de papel/caneta, sintetizados (sem samples de terceiros)
import numpy as np, wave, sys
SR=44100; D=17.0; N=int(SR*D)
rng=np.random.default_rng(3)
mix=np.zeros((N,2))
def add(sig,start,gain=1.0,pan=0.0):
    i=int(start*SR)
    if i>=N: return
    j=min(N,i+len(sig)); s=sig[:j-i]*gain
    mix[i:j,0]+=s*(1-max(0,pan)); mix[i:j,1]+=s*(1+min(0,pan))
def band(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
def tt(d): return np.arange(int(d*SR))/SR

# ---- música ----
BPM=86; B=60/BPM
def ep(freq,dur):            # piano elétrico com "wow" de vinil
    t=tt(dur); wob=1+.0035*np.sin(2*np.pi*.55*t)
    ph=2*np.pi*freq*np.cumsum(wob)/SR
    s=np.sin(ph)+.35*np.sin(2*ph)*np.exp(-t*3)+.12*np.sin(3*ph)*np.exp(-t*5)
    e=np.minimum(1,t/.012)*np.exp(-t*.55)*(1+.12*np.sin(2*np.pi*4.2*t))
    return s*e
chords=[[174.61,220,261.63,329.63],[164.81,196,246.94,293.66],[146.83,174.61,220,261.63],[130.81,164.81,196,246.94]]
bass=[87.31,82.41,73.42,65.41]
t0=0.0; k=0
while t0<13.4:
    for n,f in enumerate(chords[k%4]): add(ep(f,4*B+1.5),t0+n*.018,.10,(-.3,.3,-.15,.15)[n])
    tb=tt(4*B); add(np.sin(2*np.pi*bass[k%4]*tb)*np.minimum(1,tb/.02)*np.exp(-tb*.9),t0,.22)
    t0+=4*B; k+=1
# acorde final que fica soando
for n,f in enumerate([174.61,220,261.63,329.63,392]): add(ep(f,3.6),13.45+n*.03,.12,(-.3,.3,-.15,.15,0)[n])
def kick():
    t=tt(.35); return np.sin(2*np.pi*np.cumsum(48+90*np.exp(-t*30))/SR)*np.exp(-t*9)
def snare():
    t=tt(.25); return band(rng.standard_normal(len(t)),900,6000)*np.exp(-t*22)+.3*np.sin(2*np.pi*190*t)*np.exp(-t*30)
def hat():
    t=tt(.06); return band(rng.standard_normal(len(t)),7000,14000)*np.exp(-t*70)
beat=0; t=B*1  # bateria entra no 2º tempo
while t<12.9:
    pos=beat%4
    if pos in (0,): add(kick(),t,.42)
    if pos==2: add(kick(),t+B*.5,.32)
    if pos in (1,3): add(snare(),t,.12)
    add(hat(),t,.05,.25); add(hat(),t+B*.58,.035,-.25)   # swing
    t+=B; beat+=1
# chiado de vinil
crk=band(rng.standard_normal(N),2000,9000)*.004
pops=np.zeros(N); idx=rng.integers(0,N,90); pops[idx]=rng.uniform(.05,.18,90)*rng.choice([-1,1],90)
mix[:,0]+=crk+band(pops,800,8000)*.5; mix[:,1]+=crk+band(pops,800,8000)*.5

# ---- sons de papel e caneta ----
def rustle(dur,seed):
    r=np.random.default_rng(seed); t=tt(dur); env=np.zeros(len(t))
    for _ in range(int(dur*40)):
        c=r.uniform(0,dur); w=r.uniform(.005,.03); env+=r.uniform(.3,1)*np.exp(-((t-c)/w)**2)
    return band(r.standard_normal(len(t)),900,7500)*env*np.sin(np.pi*t/dur)
def marker(dur,seed):
    r=np.random.default_rng(seed); t=tt(dur)
    am=.6+.4*np.sin(2*np.pi*23*t+r.uniform(0,6))*np.sin(2*np.pi*3.1*t)
    return band(r.standard_normal(len(t)),1800,4800)*am*np.sin(np.pi*t/dur)**.6
def pen(dur,seed):
    r=np.random.default_rng(seed); t=tt(dur); g=np.zeros(len(t))
    for _ in range(int(dur*55)):
        c=r.uniform(0,dur); w=r.uniform(.008,.04); g+=np.exp(-((t-c)/w)**2)
    return band(r.standard_normal(len(t)),3000,9000)*g*np.sin(np.pi*t/dur)**.4
add(rustle(.7,1),.05,.22)
add(rustle(.6,2),3.3,.30,-.2); add(rustle(.6,4),4.3,.30,.2)
add(marker(.55,5),6.15,.16); add(marker(.55,6),7.75,.16)
add(pen(.75,7),6.7,.10,.3); add(pen(.75,8),8.3,.10,.3); add(pen(.65,9),9.35,.12,-.1); add(pen(.75,10),10.0,.10,.3)
th=tt(.25); add(np.sin(2*np.pi*120*th)*np.exp(-th*25)+band(rng.standard_normal(len(th)),1500,6000)*np.exp(-th*60)*.5,10.95,.35)
add(pen(1.0,11),11.2,.07,.2)
add(rustle(.7,12),12.75,.35)

# ---- master ----
fade=np.ones(N); fi=int(.08*SR); fo=int(1.0*SR); fade[:fi]=np.linspace(0,1,fi); fade[-fo:]=np.linspace(1,0,fo)
mix*=fade[:,None]; mix=np.tanh(mix*1.6)/np.tanh(1.6)
mix/=np.max(np.abs(mix))/.79
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix*32767).astype('<i2').tobytes()); w.close(); print('audio ok')
