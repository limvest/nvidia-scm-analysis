#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""시점별 분리 차트: A-1(현재 Rubin) / A-2(CPO 2027~)"""
import json, math

L = json.load(open('layout.json'))
src_nodes = L['nodes']
# Sumitomo Electric 보강
NODE_INFO = dict(src_nodes)
NODE_INFO['Sumitomo']={'n':'Sumitomo Electric','usd':52.6,'g':'High','priv':False}
NODE_INFO['Carl Zeiss SMT']={'n':'Carl Zeiss SMT','usd':None,'g':'Critical','priv':True}
NODE_INFO['Trumpf']={'n':'Trumpf','usd':None,'g':'Critical','priv':True}
def gr(note):
    if 'Critical' in note:return'Critical'
    if 'High' in note:return'High'
    if 'Medium' in note:return'Medium'
    return''
for k,v in NODE_INFO.items():
    if 'g' not in v: v['g']=gr(v.get('note',''))
    if 'priv' not in v: v['priv']=False

COLORS={'Critical':'#E24B4A','High':'#EF9F27','Medium':'#378ADD','':'#9C9A92'}

def usdtxt(u):
    if u is None: return "비상장"
    if u>=1000: return f"${u/1000:.2f}T"
    if u>=1: return f"${u:.0f}B"
    return f"${u:.1f}B"

def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def build(stages, flows, money, title, subtitle):
    """stages: dict{stage_idx:(name,[node...])}, flows:[(from,to,label)], money:[(from,to,amt)]"""
    W=680; NODE_W=120; NODE_H=32; PERROW=4
    TOP=52; STAGE_GAP=120
    # 좌표
    node_xy={}
    stage_meta=[]
    y=TOP
    for sidx in sorted(stages):
        sname, names = stages[sidx]
        rows=math.ceil(len(names)/PERROW)
        for i,nm in enumerate(names):
            r=i//PERROW; c=i%PERROW
            ncols=min(PERROW,len(names)-r*PERROW)
            tw=ncols*NODE_W+(ncols-1)*16
            x0=(W-tw)/2
            x=x0+c*(NODE_W+16)
            ny=y+r*(NODE_H+12)
            node_xy[nm]=(x+NODE_W/2, ny+NODE_H/2, x, ny)
        stage_meta.append((sname,y-22,rows*(NODE_H+12)+24))
        y+=rows*(NODE_H+12)+STAGE_GAP
    H=y+20

    svg=[f'<svg width="100%" viewBox="0 0 {W} {int(H)}" role="img" style="font-family:sans-serif">']
    svg.append(f'<title>{esc(title)}</title><desc>{esc(subtitle)}</desc>')
    svg.append('<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.4" stroke-linecap="round"/></marker>'
               '<marker id="am" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M2 1L8 5L2 9" fill="none" stroke="#1D9E75" stroke-width="1.8" stroke-linecap="round"/></marker></defs>')
    # 단계 띠
    for sname,yt,hh in stage_meta:
        svg.append(f'<rect x="6" y="{yt:.0f}" width="{W-12}" height="{hh:.0f}" rx="10" fill="#00000004" stroke="#0000000a" stroke-width="0.5"/>')
        svg.append(f'<text x="14" y="{yt-5:.0f}" style="font-size:12px;font-weight:500" fill="#888780">{esc(sname)}</text>')
    # 자재 흐름
    def curve(x1,y1,x2,y2):
        my=(y1+y2)/2
        return f'M{x1:.0f} {y1:.0f} C {x1:.0f} {my:.0f} {x2:.0f} {my:.0f} {x2:.0f} {y2:.0f}'
    labels=[]
    for fr,to,lab in flows:
        if fr not in node_xy or to not in node_xy: continue
        fx,fy,_,_=node_xy[fr]; tx,ty,_,_=node_xy[to]
        y1=fy+NODE_H/2; y2=ty-NODE_H/2
        if y2<y1: y1=fy-NODE_H/2; y2=ty+NODE_H/2
        svg.append(f'<path d="{curve(fx,y1,tx,y2)}" fill="none" stroke="#9C9A92" stroke-width="0.9" opacity="0.5" marker-end="url(#a)"/>')
        lx=fx+(tx-fx)*0.25; ly=y1+(y2-y1)*0.25
        labels.append((lx,ly,lab))
    for lx,ly,lab in labels:
        w=len(lab)*5.8+8
        svg.append(f'<rect x="{lx-w/2:.0f}" y="{ly-7:.0f}" width="{w:.0f}" height="13" rx="3" fill="#EFEEE8" opacity="0.95"/>')
        svg.append(f'<text x="{lx:.0f}" y="{ly+3:.0f}" text-anchor="middle" style="font-size:8px" fill="#5F5E5A">{esc(lab)}</text>')
    # 머니플로우
    for k,(fr,to,amt) in enumerate(money):
        if fr not in node_xy or to not in node_xy: continue
        fx,fy,_,_=node_xy[fr]; tx,ty,_,_=node_xy[to]
        y1=fy-NODE_H/2; y2=ty+NODE_H/2
        bend=W-28-k*5
        svg.append(f'<path d="M{fx:.0f} {y1:.0f} C {bend:.0f} {(y1+y2)/2-70:.0f} {bend:.0f} {(y1+y2)/2+70:.0f} {tx:.0f} {y2:.0f}" fill="none" stroke="#1D9E75" stroke-width="2" stroke-dasharray="6 4" opacity="0.8" marker-end="url(#am)"/>')
        my=(y1+y2)/2
        svg.append(f'<rect x="{bend-46:.0f}" y="{my-8:.0f}" width="60" height="16" rx="4" fill="#1D9E75"/>')
        svg.append(f'<text x="{bend-16:.0f}" y="{my+4:.0f}" text-anchor="middle" style="font-size:9px;font-weight:500" fill="#fff">투자 {amt}</text>')
    # 노드
    for nm,(cx,cy,left,top) in node_xy.items():
        info=NODE_INFO.get(nm,{'n':nm,'usd':None,'g':'','priv':False})
        col=COLORS[info['g']]
        ut=usdtxt(info['usd'])
        dash=' stroke-dasharray="4 2"' if info.get('priv') else ''
        emph = nm in ('NVIDIA','TSMC')
        fo = 0.24 if emph else 0.16
        sw = 1.8 if emph else 1.2
        svg.append(f'<g style="cursor:pointer" onclick="D(\'{esc(nm)}\',\'{info["g"] or "일반"}\',\'{ut}\')">')
        svg.append(f'<rect x="{left:.0f}" y="{top:.0f}" width="{NODE_W}" height="{NODE_H}" rx="6" fill="{col}" fill-opacity="{fo}" stroke="{col}" stroke-width="{sw}"{dash}/>')
        dn=info['n'] if len(info['n'])<=13 else info['n'][:12]+'…'
        svg.append(f'<text x="{cx:.0f}" y="{cy-3:.0f}" text-anchor="middle" style="font-size:10px;font-weight:500" fill="{col}">{esc(dn)}</text>')
        svg.append(f'<text x="{cx:.0f}" y="{cy+9:.0f}" text-anchor="middle" style="font-size:7.5px" fill="#888780">{ut}</text>')
        svg.append('</g>')
    svg.append('</svg>')
    return '\n'.join(svg)

# ===== A-1 현재 (Rubin 본체 2026) =====
A1_STAGES = {
  0:("1. 소재·광학",["Carl Zeiss SMT","Trumpf","Ajinomoto","Resonac"]),
  1:("2. 웨이퍼·기판·노광·장비",["ASML","Shin-Etsu","SUMCO","Ibiden","Hamamatsu"]),
  2:("3. 후공정 장비",["Disco","Advantest","한미반도체"]),
  3:("4. 메모리",["SK Hynix","Samsung","Micron"]),
  4:("5. 제조 + EDA",["TSMC","Cadence","Synopsys"]),
  5:("6. 통합",["NVIDIA"]),
  6:("7. 조립",["Foxconn","Wistron","Quanta"]),
}
A1_FLOWS = [
  ("Carl Zeiss SMT","ASML","광학계 100%독점"),("Trumpf","ASML","CO₂레이저 100%독점"),
  ("Ajinomoto","Ibiden","ABF필름 95%+"),("Resonac","SK Hynix","NCF필름"),
  ("ASML","TSMC","EUV 100%독점"),("Shin-Etsu","TSMC","실리콘웨이퍼"),("SUMCO","TSMC","실리콘웨이퍼"),
  ("Ibiden","TSMC","ABF기판"),("Hamamatsu","Disco","SD엔진 단독"),
  ("Disco","SK Hynix","그라인딩"),("Advantest","SK Hynix","HBM테스트"),("한미반도체","SK Hynix","TC본더"),
  ("SK Hynix","TSMC","HBM4 주력"),("Samsung","TSMC","HBM4 2차"),("Micron","TSMC","HBM4 3차"),
  ("TSMC","NVIDIA","N3P+CoWoS-L"),("Cadence","NVIDIA","EDA"),("Synopsys","NVIDIA","EDA"),
  ("NVIDIA","Foxconn","NVL72조립"),("NVIDIA","Wistron","NVL72조립"),("NVIDIA","Quanta","NVL72조립"),
]
a1 = build(A1_STAGES, A1_FLOWS, [], "현재 Rubin 본체 공급망 (2026)", "구리 NVLink + 플러그인 광모듈 기반 양산 흐름")
open('chart_a1.txt','w').write(a1)

# ===== A-2 CPO 전환 (2027~) =====
A2_STAGES = {
  0:("1. 원료 (중국)",["Dowa"]),
  1:("2. InP기판·SOI·MOCVD",["Sumitomo","AXT","Soitec","AIXTRON"]),
  2:("3. 에피·파운드리",["IQE","Tower Semi"]),
  3:("4. 로직 (TSMC)",["TSMC"]),
  4:("5. CPO 광엔진·DSP",["Coherent","Lumentum","Marvell"]),
  5:("6. 통합",["NVIDIA"]),
}
A2_FLOWS = [
  ("Dowa","AXT","인듐원료"),
  ("AXT","IQE","InP기판 35%"),("Sumitomo","IQE","InP기판 45-60%"),("AIXTRON","IQE","MOCVD에피"),
  ("AIXTRON","Coherent","MOCVD 70-90%"),("AIXTRON","Lumentum","MOCVD 70-90%"),
  ("AXT","Coherent","InP기판"),("Sumitomo","Coherent","InP기판"),("IQE","Coherent","InP에피웨이퍼"),
  ("Soitec","Tower Semi","SOI웨이퍼 1:1"),("TSMC","Marvell","N3P(Ara DSP)"),
  ("Coherent","NVIDIA","CPO광엔진"),("Lumentum","NVIDIA","CPO광엔진"),
  ("Tower Semi","NVIDIA","SiPho PIC"),("Marvell","NVIDIA","광DSP"),
]
A2_MONEY = [("NVIDIA","Coherent","$20억"),("NVIDIA","Lumentum","$20억")]
# Ayar Labs는 OIO(Feynman)용이라 CPO차트엔 제외, Feynman 차트로
a2 = build(A2_STAGES, A2_FLOWS, A2_MONEY, "CPO 전환 공급망 (Spectrum-6, 2027~)", "InP·SiPho·DSP 3체인 합류 + NVIDIA 선제 투자")
open('chart_a2.txt','w').write(a2)

print("A-1 생성:", len(a1), "chars")
print("A-2 생성:", len(a2), "chars")
