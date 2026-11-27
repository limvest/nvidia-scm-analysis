#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chart B: Feynman 시대 공급망 전환 (2028+) — M/E/T/X/N 운명 추적"""
import math

W = 680
NODE_W = 124
NODE_H = 38  # 3행 텍스트 공간
PERROW = 4
TOP = 65
STAGE_GAP = 100

COLORS = {
    'Critical': '#E24B4A',
    'High':     '#EF9F27',
    'Medium':   '#378ADD',
    '':         '#9C9A92',
}

FATE_COLORS = {
    'M': '#4CAF50',   # 초록 — 유지
    'E': '#2196F3',   # 파랑 — 진화
    'T': '#FF9800',   # 주황 — 전환
    'X': '#757575',   # 회색 — 소멸
    'N': '#9C27B0',   # 보라 — 신생
}
FATE_LABELS = {'M': '유지(M)', 'E': '진화(E)', 'T': '전환(T)', 'X': '소멸(X)', 'N': '신생(N)'}

def esc(t):
    return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ── 노드 정의 ─────────────────────────────────────────────
# fate: M/E/T/X/N
# risk: Critical/High/Medium/''
# sub1: 첫번째 보조줄 (변화 내용)
# sub2: 두번째 보조줄 (시총 또는 리스크 점수)
NODES = {
    # ─ Stage 0: 소멸 예정 (X) ─
    '3M Novec': {
        'n':'3M Novec','fate':'X','risk':'','priv':False,
        'sub1':'2025.12.31 EOL','sub2':'대체 유체 미확보'},
    'AIXTRONX': {
        'n':'AIXTRON G10-AsP','fate':'X','risk':'','priv':False,
        'sub1':'QD전환 후 수요소멸','sub2':'$6.9B · 장기'},
    '적린의존': {
        'n':'적린 의존(P)','fate':'X','risk':'','priv':False,
        'sub1':'QD-on-Si 전환 후','sub2':'중국 80% → 소멸'},
    # ─ Stage 1: 광학·레이저 (변화) ─
    'TSMC COUPE': {
        'n':'TSMC COUPE','fate':'N','risk':'Critical','priv':False,
        'sub1':'TeraPHY SiPho+CMOS','sub2':'Critical 400 · 대안없음'},
    'Soitec진화': {
        'n':'Soitec SOI','fate':'E','risk':'High','priv':False,
        'sub1':'OIO 수요 급증','sub2':'$7B · High 300'},
    'InP유지': {
        'n':'InP/인듐 의존','fate':'M','risk':'High','priv':False,
        'sub1':'OIO ELS도 InP','sub2':'High 256 · 구조 동일'},
    # ─ Stage 2: OIO 칩렛 ─
    'Ayar Labs': {
        'n':'Ayar Labs','fate':'N','risk':'High','priv':True,
        'sub1':'TeraPHY Gen3 OIO','sub2':'High 320 · $3.75B 밸류'},
    'Sivers ELS': {
        'n':'Sivers Semi.','fate':'N','risk':'Medium','priv':False,
        'sub1':'ELS InP DFB 레이저','sub2':'$1.9B · OIO 광원'},
    # ─ Stage 3: GPU 제조 ─
    'TSMC A16': {
        'n':'TSMC A16','fate':'T','risk':'Critical','priv':False,
        'sub1':'N3P→A16 (BSPDN최초)','sub2':'Critical · ~$45K/wfr'},
    'RuMo': {
        'n':'JX/Tanaka Ru·Mo','fate':'N','risk':'Medium','priv':False,
        'sub1':'A16 BSPDN 메탈화','sub2':'Medium 150 · 일본집중'},
    # ─ Stage 4: 메모리 (이중집중) ─
    'TSMC3nm': {
        'n':'TSMC 3nm 로직','fate':'N','risk':'Critical','priv':False,
        'sub1':'C-HBM4E 로직다이','sub2':'Critical · 대만 이중집중'},
    'SKHynix진화': {
        'n':'SK Hynix','fate':'E','risk':'High','priv':False,
        'sub1':'HBM4→C-HBM4E','sub2':'$916B · 인디애나2028'},
    'Micron유지': {
        'n':'Micron','fate':'M','risk':'Medium','priv':False,
        'sub1':'C-HBM4E 공급 유지','sub2':'$859B'},
    # ─ Stage 5: 패키징 ─
    'CoWoSR': {
        'n':'CoWoS-R 14×','fate':'E','risk':'High','priv':False,
        'sub1':'5.5→14리티클,12020mm²','sub2':'High 380 · 캐파재제약'},
    'SoIC': {
        'n':'SoIC 3D 스택','fate':'N','risk':'Medium','priv':False,
        'sub1':'20 컴퓨트다이 3D','sub2':'TSMC CoW 신규'},
    # ─ Stage 6: 전력·냉각 ─
    'Infineon': {
        'n':'Infineon SiC','fate':'N','risk':'Medium','priv':False,
        'sub1':'800V SiC 핫스왑','sub2':'Medium 160 · 유럽단일'},
    'Navitas': {
        'n':'Navitas GaN','fate':'N','risk':'','priv':False,
        'sub1':'GPU 보드 DC-DC','sub2':'Low 90 · 대안존재'},
    'PFAS냉각': {
        'n':'PFAS-프리 냉각','fate':'N','risk':'High','priv':False,
        'sub1':'Novec EOL→대체 미확보','sub2':'High 200 · 2028겹침'},
    # ─ Stage 7: 유지 핵심 직렬체인 ─
    'ASML유지': {
        'n':'ASML Low-NA','fate':'M','risk':'Critical','priv':False,
        'sub1':'A16에도 Low-NA 유지','sub2':'$614B · Critical 직렬'},
    'Zeiss유지': {
        'n':'Carl Zeiss SMT','fate':'M','risk':'High','priv':True,
        'sub1':'간접압박↑(Intel 14A)','sub2':'비상장 · High 250'},
    'ABF': {
        'n':'Ajinomoto ABF','fate':'X','risk':'','priv':False,
        'sub1':'단기 유지→SoW로 쇠퇴','sub2':'$31B · 장기 수요감소'},
    # ─ Stage 8: NVIDIA 통합 ─
    'NVIDIA': {
        'n':'NVIDIA Feynman','fate':'','risk':'','priv':False,
        'sub1':'TSMC A16 · 2028 출하','sub2':'$5.32T · Hub'},
}

STAGE_NAMES = [
    "소멸 예정 (X) — Feynman 전환으로 수요 소멸",
    "광학·레이저 — InP 의존 유지, SiPho 집중 신생",
    "OIO 칩렛 (Ayar Labs TeraPHY) — 신생 단일점",
    "GPU 제조 전환 — TSMC N3P → A16 (BSPDN 최초)",
    "메모리 — C-HBM4E, TSMC 대만 이중집중 신생",
    "패키징 — CoWoS-R 14×, SoIC 3D 스택",
    "전력·냉각 — 800VDC 신규 의존, Novec EOL",
    "유지 핵심 — ASML·Zeiss 직렬체인 + ABF 장기쇠퇴",
    "NVIDIA Feynman 통합 (2028 출하 목표)",
]

STAGE_NODES = [
    ['3M Novec', 'AIXTRONX', '적린의존'],
    ['TSMC COUPE', 'Soitec진화', 'InP유지'],
    ['Ayar Labs', 'Sivers ELS'],
    ['TSMC A16', 'RuMo'],
    ['TSMC3nm', 'SKHynix진화', 'Micron유지'],
    ['CoWoSR', 'SoIC'],
    ['Infineon', 'Navitas', 'PFAS냉각'],
    ['ASML유지', 'Zeiss유지', 'ABF'],
    ['NVIDIA'],
]

FLOWS = [
    ('TSMC COUPE','Ayar Labs','TeraPHY 제조', False),
    ('Soitec진화','TSMC COUPE','SOI 웨이퍼', False),
    ('InP유지','Sivers ELS','InP DFB 레이저', False),
    ('Sivers ELS','Ayar Labs','ELS 광원', False),
    ('Ayar Labs','NVIDIA','OIO TeraPHY', False),
    ('TSMC A16','NVIDIA','Feynman GPU 다이', False),
    ('TSMC3nm','NVIDIA','C-HBM4E 로직다이', False),
    ('SKHynix진화','NVIDIA','C-HBM4E 공급', False),
    ('Micron유지','NVIDIA','C-HBM4E 공급', False),
    ('CoWoSR','NVIDIA','14× 패키징', False),
    ('Infineon','NVIDIA','800V 전력', False),
    ('ASML유지','TSMC A16','EUV 노광', False),
    ('Zeiss유지','ASML유지','EUV 광학계', False),
]

MONEY = [
    ('NVIDIA','Ayar Labs','Series E 참여'),
]

# ── 레이아웃 계산 ─────────────────────────────────────────
def compute_layout():
    node_xy = {}
    stage_meta = []
    y = TOP
    for sidx, names in enumerate(STAGE_NODES):
        rows = math.ceil(len(names) / PERROW)
        for i, nm in enumerate(names):
            r = i // PERROW
            c = i % PERROW
            ncols = min(PERROW, len(names) - r * PERROW)
            tw = ncols * NODE_W + (ncols - 1) * 14
            x0 = (W - tw) / 2
            x = x0 + c * (NODE_W + 14)
            ny = y + r * (NODE_H + 10)
            node_xy[nm] = (x + NODE_W / 2, ny + NODE_H / 2, x, ny)
        stage_meta.append((STAGE_NAMES[sidx], y - 24, rows * (NODE_H + 10) + 28))
        y += rows * (NODE_H + 10) + STAGE_GAP
    return node_xy, stage_meta, int(y + 30)

def curve(x1, y1, x2, y2):
    my = (y1 + y2) / 2
    return f'M{x1:.0f} {y1:.0f} C {x1:.0f} {my:.0f} {x2:.0f} {my:.0f} {x2:.0f} {y2:.0f}'

def build():
    node_xy, stage_meta, H = compute_layout()
    s = []
    s.append(f'<svg width="100%" viewBox="0 0 {W} {H}" role="img" style="font-family:sans-serif">')
    s.append('<title>Feynman 시대 공급망 전환 (2028+) — 운명 추적</title>')
    s.append('<desc>Rubin→Feynman 전환: M(유지)·E(진화)·T(전환)·X(소멸)·N(신생) 노드 운명 지도</desc>')

    # 범례
    legend_x = 10
    legend_y = 12
    s.append(f'<text x="{legend_x}" y="{legend_y+8}" style="font-size:9px;font-weight:600" fill="#555">운명 기호:</text>')
    for i, (fate, fc) in enumerate(FATE_COLORS.items()):
        lx = legend_x + 80 + i * 78
        s.append(f'<rect x="{lx}" y="{legend_y}" width="14" height="12" rx="3" fill="{fc}"/>')
        s.append(f'<text x="{lx+17}" y="{legend_y+9}" style="font-size:8.5px" fill="#555">{FATE_LABELS[fate]}</text>')

    s.append('<defs>')
    s.append('<marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
             '<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.4" stroke-linecap="round"/></marker>')
    s.append('<marker id="am" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
             '<path d="M2 1L8 5L2 9" fill="none" stroke="#1D9E75" stroke-width="1.8" stroke-linecap="round"/></marker>')
    s.append('</defs>')

    # 단계 배경 띠
    for sname, yt, hh in stage_meta:
        s.append(f'<rect x="6" y="{yt:.0f}" width="{W-12}" height="{hh:.0f}" rx="8" fill="#00000004" stroke="#0000000a" stroke-width="0.5"/>')
        s.append(f'<text x="14" y="{yt-5:.0f}" style="font-size:10px;font-weight:500" fill="#888780">{esc(sname)}</text>')

    # 소멸 스테이지(0)에 사선 배경
    if stage_meta:
        yt0, hh0 = stage_meta[0][1], stage_meta[0][2]
        s.append(f'<rect x="6" y="{yt0:.0f}" width="{W-12}" height="{hh0:.0f}" rx="8" '
                 f'fill="none" stroke="#75757540" stroke-width="1" stroke-dasharray="4 4"/>')

    # 흐름 선
    labels = []
    for fr, to, lab, alt in FLOWS:
        if fr not in node_xy or to not in node_xy:
            continue
        fx, fy, _, _ = node_xy[fr]
        tx, ty, _, _ = node_xy[to]
        y1 = fy + NODE_H / 2
        y2 = ty - NODE_H / 2
        if y2 < y1:
            y1, y2 = fy - NODE_H / 2, ty + NODE_H / 2
        s.append(f'<path d="{curve(fx,y1,tx,y2)}" fill="none" stroke="#9C9A92" '
                 f'stroke-width="0.9" opacity="0.5" marker-end="url(#a)"/>')
        lx = fx + (tx - fx) * 0.25
        ly = y1 + (y2 - y1) * 0.25
        labels.append((lx, ly, lab))

    for lx, ly, lab in labels:
        w = len(lab) * 5.0 + 8
        s.append(f'<rect x="{lx-w/2:.0f}" y="{ly-7:.0f}" width="{w:.0f}" height="13" rx="3" fill="#EFEEE8" opacity="0.95"/>')
        s.append(f'<text x="{lx:.0f}" y="{ly+3:.0f}" text-anchor="middle" style="font-size:7.5px" fill="#5F5E5A">{esc(lab)}</text>')

    # 머니플로우
    for k, (fr, to, amt) in enumerate(MONEY):
        if fr not in node_xy or to not in node_xy:
            continue
        fx, fy, _, _ = node_xy[fr]
        tx, ty, _, _ = node_xy[to]
        y1 = fy - NODE_H / 2
        y2 = ty + NODE_H / 2
        bend = W - 24 - k * 6
        mid = (y1 + y2) / 2
        s.append(f'<path d="M{fx:.0f} {y1:.0f} C {bend:.0f} {mid-60:.0f} {bend:.0f} {mid+60:.0f} {tx:.0f} {y2:.0f}" '
                 f'fill="none" stroke="#1D9E75" stroke-width="2" stroke-dasharray="6 4" opacity="0.8" marker-end="url(#am)"/>')
        s.append(f'<rect x="{bend-52:.0f}" y="{mid-8:.0f}" width="70" height="16" rx="4" fill="#1D9E75"/>')
        s.append(f'<text x="{bend-17:.0f}" y="{mid+4:.0f}" text-anchor="middle" style="font-size:9px;font-weight:500" fill="#fff">투자 {esc(amt)}</text>')

    # 노드 그리기
    for nm, (cx, cy, left, top_y) in node_xy.items():
        info = NODES.get(nm, {'n': nm, 'fate': '', 'risk': '', 'priv': False, 'sub1': '', 'sub2': ''})
        fate = info.get('fate', '')
        risk = info.get('risk', '')
        priv = info.get('priv', False)
        col = COLORS.get(risk, '#9C9A92')
        fc = FATE_COLORS.get(fate, '#9C9A92')

        # 소멸(X) 노드: 회색 처리
        if fate == 'X':
            col = '#888'
            fo = '0.10'
            sw = '1.0'
            dash = ' stroke-dasharray="5 3"'
        elif priv:
            fo = '0.14'
            sw = '1.1'
            dash = ' stroke-dasharray="4 2"'
        else:
            fo = '0.15'
            sw = '1.2'
            dash = ''

        if nm == 'NVIDIA':
            fo = '0.24'
            sw = '2.0'

        s.append(f'<g style="cursor:pointer" onclick="D(\'{esc(nm)}\',\'{esc(fate)}\',\'{esc(risk)}\')">')
        s.append(f'<rect x="{left:.0f}" y="{top_y:.0f}" width="{NODE_W}" height="{NODE_H}" '
                 f'rx="6" fill="{col}" fill-opacity="{fo}" stroke="{col}" stroke-width="{sw}"{dash}/>')

        # 운명 뱃지 (노드 상단 좌측)
        if fate:
            s.append(f'<rect x="{left:.0f}" y="{top_y:.0f}" width="22" height="13" rx="3" fill="{fc}" opacity="0.9"/>')
            s.append(f'<text x="{left+11:.0f}" y="{top_y+9:.0f}" text-anchor="middle" '
                     f'style="font-size:7.5px;font-weight:700" fill="#fff">{fate}</text>')

        # 노드명 (중앙 상단)
        dn = info['n']
        if len(dn) > 15:
            dn = dn[:14] + '…'
        text_x = cx
        text_y_name = top_y + 16
        s.append(f'<text x="{text_x:.0f}" y="{text_y_name:.0f}" text-anchor="middle" '
                 f'style="font-size:9.5px;font-weight:500" fill="{col}">{esc(dn)}</text>')

        # sub1
        sub1 = info.get('sub1', '')
        if len(sub1) > 22:
            sub1 = sub1[:21] + '…'
        s.append(f'<text x="{text_x:.0f}" y="{top_y+26:.0f}" text-anchor="middle" '
                 f'style="font-size:7px" fill="#888780">{esc(sub1)}</text>')

        # sub2
        sub2 = info.get('sub2', '')
        if len(sub2) > 22:
            sub2 = sub2[:21] + '…'
        s.append(f'<text x="{text_x:.0f}" y="{top_y+35:.0f}" text-anchor="middle" '
                 f'style="font-size:6.5px" fill="#aaa">{esc(sub2)}</text>')

        s.append('</g>')

    s.append('</svg>')
    return '\n'.join(s)

svg = build()
with open('chart_b.txt', 'w', encoding='utf-8') as f:
    f.write(svg)
_, _, H = compute_layout()
print(f"Chart B 생성 완료: {len(svg):,} chars, height={H}")
