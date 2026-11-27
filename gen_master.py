#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""마스터 공급망 전체 지도 — Tier 0~9 전 계층 ~130개 노드"""
import math

COLORS = {'Critical':'#E24B4A','High':'#EF9F27','Medium':'#378ADD','':'#9C9A92'}

def usdtxt(u):
    if u is None: return ""
    if u >= 1000: return f"${u/1000:.1f}T"
    if u >= 1: return f"${u:.0f}B"
    return f"${u:.1f}B"

def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# (key, display_name, grade, market_cap_usd_B_or_None, is_private)
STAGES = [
  ("Tier 0 — 원자재·광물·원소", [
    ("dowa",         "Dowa",              "",        3.8,   False),
    ("sum_mining",   "Sumitomo Mining",   "",       14.2,   False),
    ("umicore",      "Umicore",           "",        3.4,   False),
    ("heraeus",      "Heraeus★",          "",        None,  True),
    ("tosoh",        "Tosoh",             "",        5.1,   False),
    ("mit_chem",     "Mitsubishi Chem",   "",       12.8,   False),
    ("basf",         "BASF (전자소재)",   "",        None,  False),
    ("albemarle",    "Albemarle",         "",        6.5,   False),
    ("covestro",     "Covestro",          "",        6.2,   False),
  ]),
  ("Tier 1 — 특수가스·세정화학·포토레지스트", [
    ("linde",        "Linde",             "",      237.9,  False),
    ("air_liq",      "Air Liquide",       "",      120.5,  False),
    ("air_prod",     "Air Products",      "",       64.6,  False),
    ("merck",        "Merck KGaA (전자)", "",       52.0,  False),
    ("jsr",          "JSR★",             "High",    None,  True),
    ("tok",          "Tokyo Ohka (TOK)", "High",    3.9,   False),
    ("entegris",     "Entegris",         "High",   13.2,   False),
    ("cabot",        "Cabot Micro",       "",        1.9,   False),
    ("daikin",       "Daikin (불소화학)", "",        None,  False),
    ("stella",       "Stella Chemifa",    "",        0.5,   False),
    ("showa_denko",  "Resonac (전자가스)","High",   19.7,  False),
  ]),
  ("Tier 2A — 필름·접착제·솔더·패시브", [
    ("ajinomoto",    "Ajinomoto (ABF)",  "Critical",31.2,  False),
    ("henkel",       "Henkel",            "",       32.0,  False),
    ("namics",       "Namics★",           "",        None,  True),
    ("indium_corp",  "Indium Corp★",      "",        None,  True),
    ("murata",       "Murata",            "",       77.0,  False),
    ("tdk",          "TDK",               "",       37.5,  False),
    ("sem",          "Samsung E-M",       "",        None,  False),
    ("yageo",        "Yageo",             "",        8.0,  False),
    ("kyocera",      "Kyocera",           "",       13.0,  False),
  ]),
  ("Tier 2B — 웨이퍼·기판소재·광섬유", [
    ("shinetsu",     "Shin-Etsu (Si/PR)","High",    80.1,  False),
    ("sumco",        "SUMCO (Si웨이퍼)", "High",     6.8,  False),
    ("siltronic",    "Siltronic (Si웨이퍼)","",      1.8,  False),
    ("sk_siltron",   "SK Siltron★",       "",        None,  True),
    ("soitec",       "Soitec (SOI)",     "High",     6.9,  False),
    ("axt",          "AXT (InP기판)",    "High",     0.5,  False),
    ("sum_elec",     "Sumitomo Elec",    "High",    52.6,  False),
    ("ibiden",       "Ibiden (ABF기판)", "",         31.4,  False),
    ("shinko",       "Shinko Elec (기판)","",         3.8,  False),
    ("ats",          "AT&S (기판)",       "",         1.0,  False),
    ("corning",      "Corning (광섬유)",  "",       165.1,  False),
    ("furukawa",     "Furukawa (광섬유)", "",         21.8,  False),
    ("prysmian",     "Prysmian (광케이블)","",        49.8,  False),
  ]),
  ("Tier 2C — 광학·레이저 소재 (ASML 전용)", [
    ("carl_zeiss",   "Carl Zeiss SMT★", "Critical",  None,  True),
    ("trumpf",       "Trumpf★",         "Critical",  None,  True),
    ("hamamatsu",    "Hamamatsu",       "Critical",   4.9,  False),
  ]),
  ("Tier 3 — 전공정·후공정·패키징 장비", [
    ("asml",         "ASML (EUV노광)",  "Critical", 613.6,  False),
    ("amat",         "Applied Materials","High",    162.0,  False),
    ("lam",          "Lam Research",    "High",      93.0,  False),
    ("kla",          "KLA",             "High",      96.0,  False),
    ("tel",          "Tokyo Electron",  "High",      64.0,  False),
    ("ucl",          "Ultra Clean Hldg","",           3.8,  False),
    ("mks",          "MKS Instruments", "",           3.2,  False),
    ("aixtron",      "AIXTRON (MOCVD)", "Critical",   6.9,  False),
    ("veeco",        "Veeco (MOCVD대안)","",           3.5,  False),
    ("disco",        "Disco (그라인딩/다이싱)","Critical",44.8,False),
    ("advantest",    "Advantest (HBM테스트)","High", 122.0,  False),
    ("teradyne",     "Teradyne",        "",           17.0,  False),
    ("hanmi",        "한미반도체 (TC본더)","Critical",  21.0,  False),
    ("asmpt",        "ASMPT",           "",            9.3,  False),
    ("besi",         "BESI (다이본더)", "",            24.9,  False),
    ("formfactor",   "FormFactor (프로브)","",         10.0,  False),
  ]),
  ("Tier 4 — EDA·설계IP·R&D", [
    ("cadence",      "Cadence",          "",          98.9,  False),
    ("synopsys",     "Synopsys",         "",          96.5,  False),
    ("siemens_eda",  "Siemens EDA★",     "",           None,  True),
    ("arm",          "Arm Holdings",     "",          160.0,  False),
    ("ansys",        "Ansys",            "",           35.0,  False),
    ("imec",         "IMEC★ (R&D)",      "",           None,  True),
    ("rambus",       "Rambus (메모리IP)","",            3.8,  False),
  ]),
  ("Tier 5 — 파운드리·메모리", [
    ("tsmc",         "TSMC (N3P+CoWoS)","Critical", 2111.7,  False),
    ("samsung_f",    "Samsung Foundry",  "",          None,  False),
    ("intel_f",      "Intel Foundry",    "",          595.6,  False),
    ("umc",          "UMC (대안파운드리)","",           24.0,  False),
    ("gf",           "GlobalFoundries",  "",           44.6,  False),
    ("tower",        "Tower Semi (SiPho)","",           33.2,  False),
    ("skhynix",      "SK Hynix (HBM4)", "Critical",  915.5,  False),
    ("micron",       "Micron (HBM4)",    "",          859.4,  False),
    ("samsung_mem",  "Samsung Memory",   "",           None,  False),
    ("kioxia",       "Kioxia (NAND)",    "",           None,  False),
  ]),
  ("Tier 6 — 칩·광엔진·IP·인터커넥트", [
    ("broadcom",     "Broadcom (PCIe/NIC)","",       1962.9,  False),
    ("marvell",      "Marvell (광DSP)",  "Medium",    167.0,  False),
    ("coherent",     "Coherent (CPO광엔진)","High",    74.0,  False),
    ("lumentum",     "Lumentum (CPO광엔진)","",         75.0,  False),
    ("iqe",          "IQE (InP에피)",   "Critical",    0.5,  False),
    ("sivers",       "Sivers (광모듈)",  "",             1.9,  False),
    ("credo",        "Credo (SerDes)",   "",            35.7,  False),
    ("ayar",         "Ayar Labs★ (OIO)", "High",        None,  True),
    ("amphenol",     "Amphenol (광커넥터)","",           80.0,  False),
    ("te_conn",      "TE Connectivity",  "",            55.0,  False),
    ("samtec",       "Samtec★ (고속커넥터)","",          None,  True),
    ("molex",        "Molex★",           "",            None,  True),
    ("lattice",      "Lattice Semi",     "",            10.0,  False),
  ]),
  ("Tier 7 — 시스템조립·전원·냉각·PCB", [
    ("foxconn",      "Foxconn (NVL72)", "High",       109.9,  False),
    ("wistron",      "Wistron",          "",            14.1,  False),
    ("quanta",       "Quanta",           "",            37.7,  False),
    ("celestica",    "Celestica",        "",             6.0,  False),
    ("jabil",        "Jabil",            "",            19.0,  False),
    ("flex",         "Flex (Flextronics)","",           10.5,  False),
    ("delta",        "Delta Electronics","",           167.3,  False),
    ("vertiv",       "Vertiv",           "",           124.2,  False),
    ("schneider",    "Schneider Electric","",          173.0,  False),
    ("eaton",        "Eaton (UPS·전원)", "",            90.0,  False),
    ("motivair",     "Motivair★ (CDU액냉)","",           None,  True),
    ("asetek",       "Asetek★ (액냉)",   "",            None,  False),
    ("ttm",          "TTM Tech (PCB)",   "",             2.0,  False),
    ("sanmina",      "Sanmina (PCB)",    "",             2.5,  False),
  ]),
  ("Tier 8 — NVIDIA (최종 통합)", [
    ("nvidia",       "NVIDIA",           "",          5316.6,  False),
  ]),
]

# 핵심 SPoF 흐름만 표시 (전체 연결 생략)
KEY_FLOWS = [
    ("carl_zeiss", "asml",    "광학계 독점"),
    ("trumpf",     "asml",    "CO₂레이저"),
    ("asml",       "tsmc",    "EUV 독점"),
    ("ajinomoto",  "ibiden",  "ABF필름 95%"),
    ("ibiden",     "tsmc",    "ABF기판"),
    ("hamamatsu",  "disco",   "SD엔진 독점"),
    ("disco",      "skhynix", "그라인딩"),
    ("aixtron",    "coherent","MOCVD 70%+"),
    ("aixtron",    "lumentum","MOCVD 70%+"),
    ("skhynix",    "tsmc",    "HBM4 주력"),
    ("micron",     "tsmc",    "HBM4 3차"),
    ("tsmc",       "nvidia",  "N3P+CoWoS"),
    ("coherent",   "nvidia",  "CPO광엔진"),
    ("lumentum",   "nvidia",  "CPO광엔진"),
    ("broadcom",   "nvidia",  "PCIe SW"),
    ("marvell",    "nvidia",  "광DSP"),
]

def build():
    W=1000; NODE_W=108; NODE_H=26; PERROW=8
    TOP=70; STAGE_GAP=60

    node_xy = {}
    stage_meta = []
    y = TOP
    for (sname, nodes) in STAGES:
        rows = math.ceil(len(nodes)/PERROW)
        for i,(key,disp,g,usd,priv) in enumerate(nodes):
            r=i//PERROW; c=i%PERROW
            ncols=min(PERROW,len(nodes)-r*PERROW)
            tw=ncols*NODE_W+(ncols-1)*10
            x0=(W-tw)/2
            nx=x0+c*(NODE_W+10)
            ny=y+r*(NODE_H+9)
            node_xy[key]=(nx+NODE_W/2, ny+NODE_H/2, nx, ny)
        hh=rows*(NODE_H+9)+10
        stage_meta.append((sname,y-20,hh+28))
        y+=hh+STAGE_GAP
    H=y+30

    total_nodes = sum(len(n) for _,n in STAGES)

    svg=[f'<svg width="100%" viewBox="0 0 {W} {int(H)}" role="img" style="font-family:sans-serif">']
    svg.append(f'<title>NVIDIA Vera Rubin 공급망 전체 지도 ({total_nodes}개 노드)</title>')
    svg.append('<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.4" stroke-linecap="round"/></marker></defs>')

    # 헤더
    svg.append(f'<text x="{W/2:.0f}" y="24" text-anchor="middle" style="font-size:15px;font-weight:700" fill="#1A1A18">NVIDIA Vera Rubin 공급망 전체 지도</text>')
    svg.append(f'<text x="{W/2:.0f}" y="42" text-anchor="middle" style="font-size:10px" fill="#888780">Tier 0~8 전 계층 · {total_nodes}개 노드 · 점선=비상장 · 화살표=SPoF 핵심 흐름만 표시</text>')

    # 리스크 범례
    legend_x = W - 340
    svg.append(f'<text x="{legend_x}" y="18" style="font-size:9px;font-weight:600" fill="#5F5E5A">리스크:</text>')
    for i,(g,label) in enumerate([("Critical","Critical"),("High","High"),("Medium","Medium"),("","일반")]):
        lx=legend_x+52+i*72
        svg.append(f'<rect x="{lx}" y="8" width="10" height="10" rx="2" fill="{COLORS[g]}" fill-opacity="0.7"/>')
        svg.append(f'<text x="{lx+13}" y="18" style="font-size:9px" fill="{COLORS[g]}">{label}</text>')

    # 단계 띠
    for sname,yt,hh in stage_meta:
        svg.append(f'<rect x="4" y="{yt:.0f}" width="{W-8}" height="{hh:.0f}" rx="8" fill="#00000003" stroke="#0000000a" stroke-width="0.5"/>')
        svg.append(f'<text x="12" y="{yt-5:.0f}" style="font-size:10px;font-weight:600" fill="#888780">{esc(sname)}</text>')

    # 핵심 흐름
    def curve(x1,y1,x2,y2):
        my=(y1+y2)/2
        return f'M{x1:.0f} {y1:.0f} C {x1:.0f} {my:.0f} {x2:.0f} {my:.0f} {x2:.0f} {y2:.0f}'

    for fr,to,lab in KEY_FLOWS:
        if fr not in node_xy or to not in node_xy: continue
        fx,fy,_,_=node_xy[fr]; tx,ty,_,_=node_xy[to]
        y1=fy+NODE_H/2; y2=ty-NODE_H/2
        if y2<y1: y1=fy-NODE_H/2; y2=ty+NODE_H/2
        svg.append(f'<path d="{curve(fx,y1,tx,y2)}" fill="none" stroke="#BABAB0" stroke-width="0.8" opacity="0.55" marker-end="url(#a)"/>')

    # 노드
    for sname,nodes in STAGES:
        for key,disp,g,usd,priv in nodes:
            if key not in node_xy: continue
            cx,cy,left,top=node_xy[key]
            col=COLORS[g]
            ut=usdtxt(usd)
            dash=' stroke-dasharray="4 2"' if priv else ''
            emph = key=='nvidia'
            fo=0.24 if emph else 0.12
            sw=2.2 if emph else (1.4 if g else 1.0)
            dn=disp if len(disp)<=16 else disp[:15]+'…'
            svg.append(f'<rect x="{left:.0f}" y="{top:.0f}" width="{NODE_W}" height="{NODE_H}" rx="5" fill="{col}" fill-opacity="{fo}" stroke="{col}" stroke-width="{sw}"{dash}/>')
            if ut:
                svg.append(f'<text x="{cx:.0f}" y="{cy-2:.0f}" text-anchor="middle" style="font-size:8.5px;font-weight:500" fill="{col}">{esc(dn)}</text>')
                svg.append(f'<text x="{cx:.0f}" y="{cy+8:.0f}" text-anchor="middle" style="font-size:7px" fill="#888780">{ut}</text>')
            else:
                svg.append(f'<text x="{cx:.0f}" y="{cy+4:.0f}" text-anchor="middle" style="font-size:8.5px;font-weight:500" fill="{col}">{esc(dn)}</text>')
    svg.append('</svg>')
    return '\n'.join(svg)

svg=build()
with open('chart_master.txt','w') as f: f.write(svg)
total=sum(len(n) for _,n in STAGES)
print(f"Master 생성: {total}개 노드, {len(svg)}chars")
