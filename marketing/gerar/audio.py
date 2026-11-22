import numpy as np, wave, sys
SR=44100; D=18.0; N=int(SR*D); t=np.arange(N)/SR
rng=np.random.default_rng(7)
L=np.zeros(N); R=np.zeros(N)
def add(sig,start,gain=1.0,pan=0.0):
    i=int(start*SR); j=min(N,i+len(sig)); s=sig[:j-i]*gain
    L[i:j]+=s*(1-max(0,pan)); R[i:j]+=s*(1+min(0,pan))
def env(n,a,r):
    e=np.ones(n); A=int(a*SR); Rr=int(r*SR)
    if A: e[:A]=np.linspace(0,1,A)
    if Rr: e[-Rr:]*=np.linspace(1,0,Rr)
    return e
def lp(x,k):  # passa-baixa simples (média móvel)
    return np.convolve(x,np.ones(k)/k,mode='same')
# pad de fundo (Lá menor 9 -> Fá maior 7 no final)
def pad(freqs,dur):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for f in freqs:
        for h,g in [(1,1),(2,.25),(3,.08)]:
            s+=g*np.sin(2*np.pi*f*h*tt+rng.random()*6)*(1+.15*np.sin(2*np.pi*.2*tt+rng.random()*6))
    return s/len(freqs)
add(pad([110,164.81,220,246.94,261.63],15.4)*env(int(15.4*SR),2.5,1.2),0,.11)
add(pad([87.31,174.61,220,261.63,329.63],2.6)*env(int(2.6*SR),.6,1.6),15.4,.13)
# pulso grave suave (batida de tensão)
for k in np.arange(3.3,12.3,.5):
    n=int(.25*SR); tt=np.arange(n)/SR
    add(np.sin(2*np.pi*55*tt)*np.exp(-tt*18),k,.35)
# tique-taque da rolagem
for k in np.arange(3.9,6.5,.25):
    n=int(.04*SR); add(rng.standard_normal(n)*np.exp(-np.arange(n)/SR*120),k,.05,pan=.3 if int(k*4)%2 else -.3)
# whooshes
def whoosh(dur,up=True):
    n=int(dur*SR); x=lp(rng.standard_normal(n),12); e=np.sin(np.linspace(0,np.pi,n))**2
    return x*e
for k in [3.15,6.45,12.45,15.25]: add(whoosh(.6),k,.18)
# varredura (tom subindo)
n=int(1.4*SR); tt=np.arange(n)/SR; f=300+600*(tt/1.4)**2
add(np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.3,.25)*.5,6.9,.12)
# "plim" de alerta em cada cláusula
def plim(f0):
    n=int(.7*SR); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*f0*tt)+.4*np.sin(2*np.pi*f0*2.01*tt))*np.exp(-tt*7)
add(plim(880),8.5,.22,-.2); add(plim(988),9.4,.22,.2); add(plim(880),10.3,.22,-.2)
add(plim(1318.5)*.8+plim(1046.5)*.8,11.05,.2)
# acorde final (marca)
n=int(2.4*SR); tt=np.arange(n)/SR
ch=sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*1.6) for f in [349.23,440,523.25,659.25])/4
add(ch,15.45,.35)
# master
mx=np.stack([L,R],1); mx*=env(N,.05,.8)[:,None]
mx/=np.max(np.abs(mx))/.89
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mx*32767).astype('<i2').tobytes()); w.close(); print('audio ok')
