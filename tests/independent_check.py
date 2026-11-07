# 도구(JS)와 별개로 원 문헌 식에서 직접 작성한 독립 검산 코드
import math, json, subprocess
mm=1e-3
# ---- 공통 조건 (논문 기반) ----
Q=42.5; Lc=Wc=5*mm; L=W=12*mm; Tin=70.0; eta_p=0.5; kb=390; tb=2*mm
stack=[(0.18,118),(0.08,50),(0.30,390),(0.38,170),(0.30,390),(0.30,50)]
# ---- 유체 데이터시트 값 ----
F={
 'amp110':dict(rho=(15.6,820,7e-4),nu=((40,8.11),(100,2.22)),cp=((40,2212.1),(100,2439.0)),k=((40,.1359),(100,.1325))),
 'amp122':dict(rho=(15.6,790,7e-4),nu=((40,5.02),(100,1.70)),cp=((40,2212.1),(100,2439.0)),k=((40,.1359),(100,.1325))),
 'amp120':dict(rho=(15.6,820,7e-4),nu=((40,16.0),(100,3.60)),cp=((40,2206.0),(100,2428.8)),k=((40,.1459),(100,.1430))),
 'valde1':dict(rho=(40,811.5,(811.5-773.4)/811.5/60),nu=((40,8.01),(100,2.40)),cp=((40,2001.1),(100,2222.2)),k=((40,.1304),(100,.1196))),
 'castrol':dict(rho=(15.6,797,7e-4),nu=((40,5.12),(100,1.71)),cp=((20,2030),(21,2030*(1+.0018))),k=((20,.139),(21,.139*(1-.0007)))),
 'fuchs':dict(rho=(25,792,7e-4),nu=((40,5.1),(100,1.8)),cp=((25,2035),(26,2035*1.0018)),k=((25,.138),(26,.138*(1-.0007)))),
 'hxl9119':dict(rho=(20,830,7e-4),nu=((40,4.7),(100,1.4)),cp=((20,2240),(21,2240*1.0018)),k=((20,.138),(21,.138*(1-.0007)))),
 'e565':dict(rho=(20,918,7.5e-4),nu=((40,8.0),(100,2.0)),cp=((20,1948),(21,1948*1.0018)),k=((20,.133),(21,.133*(1-.0006)))),
 'repsol':dict(rho=(20,969,7.5e-4),nu=((-20,1196),(40,27.4)),cp=((25,1997),(26,1997*1.0018)),k=((25,.148),(26,.148*(1-.0006)))),
}
def props(f,T):
    (T1,n1),(T2,n2)=f['nu']; B=math.log(n1/n2)/(1/(T1+273.15)-1/(T2+273.15)); nu=n1*math.exp(B*(1/(T+273.15)-1/(T1+273.15)))*1e-6
    Tr,rr,b=f['rho']; rho=rr*(1-b*(T-Tr))
    li=lambda p:p[0][1]+(p[1][1]-p[0][1])*(T-p[0][0])/(p[1][0]-p[0][0])
    cp=li(f['cp']); k=li(f['k']); mu=nu*rho
    return rho,cp,k,mu,nu,mu*cp/k
# ---- 패키지: 45도 확산 + Lee-Song-Au-Moran ----
def pkg():
    a,b_=Lc,Wc; R=0
    for t,k in stack:
        t*=mm; A1=a*b_; a2=min(a+2*t,L); b2=min(b_+2*t,W); R+=t/(k*math.sqrt(A1*a2*b2)); a,b_=a2,b2
    return R,a*b_
Rpkg,Asrc=pkg()
def base(heff):
    A=L*W; a=math.sqrt(Asrc/math.pi); b=math.sqrt(A/math.pi); e=a/b; tau=tb/b; Bi=heff*b/kb
    lam=math.pi+1/(math.sqrt(math.pi)*e); th=math.tanh(lam*tau); Phi=(th+lam/Bi)/(1+lam/Bi*th)
    return tb/(kb*A),(1-e)*Phi/(math.pi*kb*a),1/(heff*A)
# ---- A: Zukauskas(엇갈림) + 핀효율 + Gaddis-Gnielinski ----
def coolA(V,p,Prs=None):
    rho,cp,k,mu,nu,Pr=p; Prs=Prs or Pr; D,H,ST,SL=.5*mm,1*mm,1*mm,1*mm
    NL=int(L/SL+1e-9); NT=int(W/ST+1e-9); N=NT*NL-NL//2
    uin=V/(W*H); SD=math.hypot(SL,ST/2); umax=uin*ST/(2*(SD-D)) if SD<(ST+D)/2 else uin*ST/(ST-D)
    Re=umax*D/nu
    if Re<500: Nu=1.04*Re**.4
    elif Re<1000: Nu=.71*Re**.5
    else: Nu=.35*(ST/SL)**.2*Re**.6
    Nu*=Pr**.36*(Pr/Prs)**0.25
    # Cengel Table 7-3 엇갈림: Re<1000 행(10:0.98, 13:0.99), Re>=1000 행(10:0.97, 13:0.98)
    lo,hi=(0.98,0.99) if Re<1000 else (0.97,0.98)
    C2=lo+(hi-lo)*(NL-10)/3
    Nu*=C2; h=Nu*k/D
    m=math.sqrt(4*h/(kb*D)); eta=math.tanh(m*H)/(m*H)
    A=L*W; heff=h*((A-N*math.pi*D*D/4)+eta*N*math.pi*D*H)/A
    a=ST/D; b=SL/D; c=a if b>=0.5*math.sqrt(2*a+1) else math.sqrt(a*a/4+b*b)
    fl=280*math.pi*((b**.5-.6)**2+.75)/((4*a*b-math.pi)*c**1.6)
    ft=2.5+1.2/(a-.85)**1.08+.4*(b/a-1)**3-.01*(a/b-1)**3
    xi=fl/Re+ft/Re**.25*(1-math.exp(-(Re+1000)/2000))
    uh=V/(W*3*mm)
    dp=xi*NL*rho*umax**2/2+1.5*rho*uin**2/2+rho*uh**2/2
    return heff,dp,(0.5+0.5*Lc/L),dict(Re=Re,Nu=Nu,h=h,eta=eta,ar=((A-N*math.pi*D*D/4)+N*math.pi*D*H)/A)
# ---- B: Martin(1977) 원형노즐 배열 ----
def martin(Re,Pr,d,S,Hg):
    f=math.pi*d*d/(4*S*S); s=math.sqrt(f); Hd=Hg/d
    K=(1+(Hd/(0.6/s))**6)**-0.05; G=2*s*(1-2.2*s)/(1+0.2*(Hd-6)*s)
    return K*G*0.5*Re**(2/3)*Pr**0.42
KIN={'sharp':0.5,'chamfer':0.25,'round':0.05}
def shah_fapp(Re,Ld):
    xp=Ld/Re; sx=math.sqrt(xp)
    return (3.44/sx+(1.25/(4*xp)+16-3.44/sx)/(1+0.00021/xp**2))/Re
def haaland(Re,rr):
    return (-1.8*math.log10((rr/3.7)**1.11+6.9/Re))**-2
def jet(V,p,d,S,ln,Hp,inlet='sharp',rough=2e-6):
    rho,cp,k,mu,nu,Pr=p; n=int(L/S+1e-9); N=n*int(W/S+1e-9)
    vj=V/(N*math.pi*d*d/4); Re=vj*d/nu; q=rho*vj**2/2; Ld=ln/d
    lam=4*shah_fapp(Re,Ld)*Ld if Re<2300 else 4*shah_fapp(2300,Ld)*Ld*2300/Re
    tur=haaland(max(Re,2300),rough/d)*Ld+0.1
    w=0 if Re<=2300 else 1 if Re>=4000 else (Re-2300)/1700
    dpn=(KIN[inlet]+1.0)*q+((1-w)*lam+w*tur)*q
    up=V/(W*Hp); dpp=rho*up**2/2
    return N,vj,Re,dpn,dpp
def coolB(V,p):
    rho,cp,k,mu,nu,Pr=p; d,S,Hj=.5*mm,2.5*mm,1.5*mm
    N,vj,Re,dpn,dpp=jet(V,p,d,S,1*mm,3*mm); Nu=martin(Re,Pr,d,S,Hj); h=Nu*k/d
    return h,dpn+dpp+0.25*rho*vj**2/2,0.1,dict(Re=Re,Nu=Nu,h=h,eta=1,ar=1)
def coolC(V,p,chi=1.0):
    rho,cp,k,mu,nu,Pr=p; d,S,Hj,Dp,Hp,Sp=.5*mm,2.5*mm,1.5*mm,.4*mm,.8*mm,.8*mm
    N,vj,Re,dpn,dpp=jet(V,p,d,S,1*mm,3*mm)
    s=max(Hj-Hp,d); Nu=martin(Re,Pr,d,S,s); h=Nu*k/d*chi
    Np0=int(L/Sp+1e-9)*int(W/Sp+1e-9); Np=Np0-N*max(1,round(math.pi*d*d/(4*Sp*Sp)))
    Lc=Hp+Dp/4; m=math.sqrt(4*h/(kb*Dp)); eta=math.tanh(m*Lc)/(m*Lc)
    A=L*W; heff=h*((A-Np*math.pi*Dp**2/4)+eta*Np*math.pi*Dp*Lc)/A; info_ar=((A-Np*math.pi*Dp**2/4)+Np*math.pi*Dp*Lc)/A
    ur=(V/N)/(2*math.pi*(S/4)*Hp); um=ur*Sp/(Sp-Dp); Rep=um*Dp/nu; a=Sp/Dp
    fl=280*math.pi*((a**.5-.6)**2+.75)/((4*a*a-math.pi)*a**1.6)
    ft=(.22+1.2*(1-.94/a)**.6/(a-.85)**1.3)*10**(.47*(1-1.5))+.03*(a-1)**2
    xi=fl/Rep+ft/Rep**(0.1)*(1-math.exp(-(Rep+1000)/2000)); Nr=max(1,round(S/(2*Sp)))
    dpin=xi*Nr*rho*um**2/2
    return heff,dpn+dpp+dpin+0.25*rho*vj**2/2,0.1,dict(Re=Re,Nu=Nu,h=h,eta=eta,ar=info_ar)
def evalc(fn,f,V):
    T=Tin; Prs=None
    p=props(f,T)
    for _ in range(5):
        heff,dp,rf,info=fn(V,p,Prs) if fn is coolA else fn(V,p)
        dT=Q/(p[0]*V*p[1]); T=Tin+min(dT,150)/2
        Ts=T+min(Q/(info['h']*L*W*info['ar']),200)
        p=props(f,T); Prs=props(f,Ts)[5]
    r1,rsp,rc=base(heff); Rcal=rf/(p[0]*V*p[1])
    R=Rpkg+r1+rsp+rc+Rcal; return dict(V=V,dp=dp,W=dp*V/eta_p,Tj=Tin+Q*R,R=R,heff=heff,**info)
def solveW(fn,f,Wt):
    lo,hi=math.log(1e-8),math.log(2e-3)
    for _ in range(80):
        m=(lo+hi)/2
        if evalc(fn,f,math.exp(m))['W']>Wt: hi=m
        else: lo=m
    return evalc(fn,f,math.exp((lo+hi)/2))
out={}
for fk,f in F.items():
    for cn,fn in (('A',coolA),('B',coolB),('C',coolC)):
        out[f'{fk}|{cn}']=solveW(fn,f,0.0133)
import os; json.dump(out,open(os.path.join(os.path.dirname(__file__),'py.json'),'w')); print('py.json 저장 완료')
