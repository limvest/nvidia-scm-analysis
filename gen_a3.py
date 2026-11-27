#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A-3: InP 체인 드릴다운 — 원료→합성→기판→전구체→MOCVD→에피→레이저→정렬→CPO광엔진"""
import math

W = 680
NODE_W = 120
NODE_H = 32
PERROW = 4
TOP = 60
STAGE_GAP = 110

COLORS = {
    'Critical': '#E24B4A',
    'High':     '#EF9F27',
    'Medium':   '#378ADD',
    '':         '#9C9A92',
}

def esc(t):
    return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ── 노드 정의 ──────────────────────────────────────────────
# usd: 숫자(B단위) or None(비상장/공정)
# g: Critical/High/Medium/''
# priv: 비상장 → 점선 테두리
# alt: 대안공급 → 파란 점선 + 연한색
# sub: 2행 보조텍스트 (시총 대신 표시)
# badge: (텍스트, 색) 경고 뱃지
NODES = {
    # Stage 0: 원료 (중국 집중)
    '인듐': {
        'n':'중국 인듐 (70%)','usd':None,'g':'Critical','priv':False,'alt':False,
        'sub':'원자재·중국','badge':('집중도 위험','#E24B4A')},
    '적린': {
        'n':'중국 적린 (80%)','usd':None,'g':'Critical','priv':False,'alt':False,
        'sub':'원자재·중국','badge':('집중도 위험','#E24B4A')},
    # Stage 1: 합성공정
    'InP합성': {
        'n':'InP 합성공정','usd':None,'g':'High','priv':True,'alt':False,
        'sub':'공정·中업체의존','badge':None},
    # Stage 2: 기판
    'Sumitomo': {
        'n':'Sumitomo Elec.','usd':52.6,'g':'High','priv':False,'alt':False,
        'sub':'$53B · 45~60%','badge':('라이선스2029','#EF9F27')},
    'AXT': {
        'n':'AXT / Tongmei','usd':7.9,'g':'High','priv':False,'alt':False,
        'sub':'$7.9B · 35%','badge':('⚠ 수출통제中','#E24B4A')},
    'JX Metals': {
        'n':'JX Metals','usd':None,'g':'Medium','priv':True,'alt':True,
        'sub':'비상장 · 5~10%','badge':None},
    # Stage 3: 전구체 가스
    'Merck': {
        'n':'Merck (TMIn)','usd':None,'g':'','priv':True,'alt':False,
        'sub':'비상장·독일','badge':None},
    'Tosoh': {
        'n':'Tosoh (TMIn)','usd':5.1,'g':'','priv':False,'alt':False,
        'sub':'$5B·일본','badge':None},
    'Air Liquide': {
        'n':'Air Liquide','usd':120.5,'g':'','priv':False,'alt':False,
        'sub':'$121B·TBP공급','badge':None},
    'Linde': {
        'n':'Linde (PH₃)','usd':237.9,'g':'','priv':False,'alt':False,
        'sub':'$238B','badge':None},
    # Stage 4: MOCVD 장비 (공유 SPoF)
    'AIXTRON': {
        'n':'AIXTRON G10-AsP','usd':6.9,'g':'Critical','priv':False,'alt':False,
        'sub':'$6.9B · 70~90%','badge':('공유SPoF·18~24mo','#E24B4A')},
    'Veeco': {
        'n':'Veeco Lumina','usd':3.5,'g':'Medium','priv':False,'alt':True,
        'sub':'$3.5B · 대안10~30%','badge':None},
    # Stage 5: 에피웨이퍼
    'IQE': {
        'n':'IQE plc','usd':0.5,'g':'','priv':False,'alt':False,
        'sub':'$0.5B · 독립공급40~60%','badge':None},
    'Coherent에피': {
        'n':'Coherent 내재화','usd':74.0,'g':'High','priv':False,'alt':False,
        'sub':'$74B · 자체 에피','badge':None},
    # Stage 6: 레이저 + 아이솔레이터
    'Coherent': {
        'n':'Coherent','usd':74.0,'g':'High','priv':False,'alt':False,
        'sub':'$74B · InP CW 레이저','badge':None},
    'Lumentum': {
        'n':'Lumentum','usd':75.0,'g':'High','priv':False,'alt':False,
        'sub':'$75B · InP CW 레이저','badge':None},
    'TDK': {
        'n':'TDK (YIG)','usd':37.5,'g':'Medium','priv':False,'alt':False,
        'sub':'$38B · 이트륨 중국80%','badge':('이트륨 CN80%','#EF9F27')},
    'Murata': {
        'n':'Murata (YIG)','usd':77.0,'g':'','priv':False,'alt':False,
        'sub':'$77B · YIG결정공급','badge':None},
    # Stage 7: 정렬 패키징
    'ficonTEC': {
        'n':'ficonTEC','usd':None,'g':'High','priv':True,'alt':False,
        'sub':'비상장·독일 준독점','badge':('±100nm 6-DOF','#EF9F27')},
    # Stage 8: CPO 광엔진 (NVIDIA)
    'NVIDIA': {
        'n':'NVIDIA Spectrum-6','usd':5316.6,'g':'','priv':False,'alt':False,
        'sub':'$5.32T','badge':None},
}

STAGE_NAMES = [
    "1. 원료 (중국 집중 — 인듐 70% · 적린 80%)",
    "2. InP 폴리크리스탈 합성",
    "3. InP 기판 공급  (공급갭 70% · 수요 200만 vs 공급 60만 wafer/yr)",
    "4. 전구체 가스  (TMIn · TBP · PH₃)",
    "5. MOCVD 장비  (공유 SPoF: Coherent·Lumentum·IQE 3사 동시 의존)",
    "6. InP 에피웨이퍼",
    "7. InP 레이저 다이 + YIG 아이솔레이터",
    "8. 정렬 패키징  (±100nm 6-DOF, 비상장 준독점)",
    "9. CPO 광엔진 → NVIDIA Spectrum-6",
]

STAGE_NODES = [
    ['인듐', '적린'],
    ['InP합성'],
    ['Sumitomo', 'AXT', 'JX Metals'],
    ['Merck', 'Tosoh', 'Air Liquide', 'Linde'],
    ['AIXTRON', 'Veeco'],
    ['IQE', 'Coherent에피'],
    ['Coherent', 'Lumentum', 'TDK', 'Murata'],
    ['ficonTEC'],
    ['NVIDIA'],
]

# (from, to, label, alt)
FLOWS = [
    # 원료 → 합성
    ('인듐',   'InP합성', '인듐원료 70%', False),
    ('적린',   'InP합성', '적린원료 80%', False),
    # 합성 → 기판
    ('InP합성','Sumitomo',  '합성원료',      False),
    ('InP합성','AXT',       '합성원료',      False),
    ('InP합성','JX Metals', '합성원료(소량)',  True),
    # 기판 → 에피 (단계 스킵: S2→S5)
    ('Sumitomo','IQE',          'InP기판 45~60%', False),
    ('AXT',     'IQE',          'InP기판 35%',    False),
    ('JX Metals','IQE',         'InP기판 5~10%',   True),
    ('Sumitomo','Coherent에피', 'InP기판',         False),
    ('AXT',     'Coherent에피', 'InP기판',         False),
    # 전구체 → MOCVD
    ('Merck',      'AIXTRON', 'TMIn 전구체',  False),
    ('Tosoh',      'AIXTRON', 'TMIn 전구체',  False),
    ('Air Liquide','AIXTRON', 'TBP 전구체',   False),
    ('Linde',      'AIXTRON', 'PH₃ 전구체',   False),
    # MOCVD → 에피
    ('AIXTRON','IQE',          'MOCVD 70~90%', False),
    ('AIXTRON','Coherent에피', 'MOCVD 70~90%', False),
    ('Veeco',  'IQE',          'MOCVD 대안',    True),
    ('Veeco',  'Coherent에피', 'MOCVD 대안',    True),
    # 에피 → 레이저
    ('IQE',         'Coherent', 'InP에피 40~60%', False),
    ('IQE',         'Lumentum', 'InP에피웨이퍼',   False),
    ('Coherent에피','Coherent', '내재화 에피',     False),
    # 레이저+ISO → 정렬
    ('Coherent', 'ficonTEC', 'InP 레이저다이', False),
    ('Lumentum', 'ficonTEC', 'InP 레이저다이', False),
    ('TDK',      'ficonTEC', 'YIG 아이솔레이터', False),
    ('Murata',   'ficonTEC', 'YIG 아이솔레이터', False),
    # 정렬 → NVIDIA
    ('ficonTEC','NVIDIA', 'CPO 광엔진 완성', False),
]

MONEY = [
    ('NVIDIA', 'Coherent', '$20억'),
    ('NVIDIA', 'Lumentum', '$20억'),
]

# ── 레이아웃 계산 ──────────────────────────────────────────
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
            tw = ncols * NODE_W + (ncols - 1) * 16
            x0 = (W - tw) / 2
            x = x0 + c * (NODE_W + 16)
            ny = y + r * (NODE_H + 12)
            node_xy[nm] = (x + NODE_W / 2, ny + NODE_H / 2, x, ny)
        stage_meta.append((STAGE_NAMES[sidx], y - 22, rows * (NODE_H + 12) + 24))
        y += rows * (NODE_H + 12) + STAGE_GAP
    H = y + 30
    return node_xy, stage_meta, int(H)

def curve(x1, y1, x2, y2):
    my = (y1 + y2) / 2
    return f'M{x1:.0f} {y1:.0f} C {x1:.0f} {my:.0f} {x2:.0f} {my:.0f} {x2:.0f} {y2:.0f}'

# ── SVG 생성 ───────────────────────────────────────────────
def build():
    node_xy, stage_meta, H = compute_layout()

    s = []
    s.append(f'<svg width="100%" viewBox="0 0 {W} {H}" role="img" style="font-family:sans-serif">')
    s.append('<title>InP 체인 드릴다운 (CPO 광학 공급망 Tier 3)</title>')
    s.append('<desc>원료→합성→기판→전구체→MOCVD→에피→레이저+아이솔레이터→정렬→CPO광엔진</desc>')
    s.append('<defs>')
    s.append('<marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
             '<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.4" stroke-linecap="round"/></marker>')
    s.append('<marker id="ad" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
             '<path d="M2 1L8 5L2 9" fill="none" stroke="#378ADD" stroke-width="1.2" stroke-linecap="round"/></marker>')
    s.append('<marker id="am" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
             '<path d="M2 1L8 5L2 9" fill="none" stroke="#1D9E75" stroke-width="1.8" stroke-linecap="round"/></marker>')
    s.append('</defs>')

    # 단계 배경 띠
    for sname, yt, hh in stage_meta:
        s.append(f'<rect x="6" y="{yt:.0f}" width="{W-12}" height="{hh:.0f}" rx="8" fill="#00000004" stroke="#0000000a" stroke-width="0.5"/>')
        s.append(f'<text x="14" y="{yt-4:.0f}" style="font-size:10.5px;font-weight:500" fill="#888780">{esc(sname)}</text>')

    # 자재 흐름 선
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
        if alt:
            s.append(f'<path d="{curve(fx,y1,tx,y2)}" fill="none" stroke="#378ADD" '
                     f'stroke-width="0.8" stroke-dasharray="5 3" opacity="0.45" marker-end="url(#ad)"/>')
        else:
            s.append(f'<path d="{curve(fx,y1,tx,y2)}" fill="none" stroke="#9C9A92" '
                     f'stroke-width="0.9" opacity="0.5" marker-end="url(#a)"/>')
        lx = fx + (tx - fx) * 0.25
        ly = y1 + (y2 - y1) * 0.25
        labels.append((lx, ly, lab, alt))

    # 라벨 필 (나중에 그려야 선 위에 올라옴)
    for lx, ly, lab, alt in labels:
        w = len(lab) * 5.0 + 8
        tc = '#4A6FA5' if alt else '#5F5E5A'
        s.append(f'<rect x="{lx-w/2:.0f}" y="{ly-7:.0f}" width="{w:.0f}" height="13" rx="3" fill="#EFEEE8" opacity="0.95"/>')
        s.append(f'<text x="{lx:.0f}" y="{ly+3:.0f}" text-anchor="middle" style="font-size:7.5px" fill="{tc}">{esc(lab)}</text>')

    # 머니플로우 (NVIDIA→Coherent, NVIDIA→Lumentum)
    for k, (fr, to, amt) in enumerate(MONEY):
        if fr not in node_xy or to not in node_xy:
            continue
        fx, fy, _, _ = node_xy[fr]
        tx, ty, _, _ = node_xy[to]
        y1 = fy - NODE_H / 2
        y2 = ty + NODE_H / 2
        bend = W - 24 - k * 6
        mid = (y1 + y2) / 2
        s.append(f'<path d="M{fx:.0f} {y1:.0f} C {bend:.0f} {mid-80:.0f} {bend:.0f} {mid+80:.0f} {tx:.0f} {y2:.0f}" '
                 f'fill="none" stroke="#1D9E75" stroke-width="2" stroke-dasharray="6 4" opacity="0.8" marker-end="url(#am)"/>')
        s.append(f'<rect x="{bend-46:.0f}" y="{mid-8:.0f}" width="62" height="16" rx="4" fill="#1D9E75"/>')
        s.append(f'<text x="{bend-15:.0f}" y="{mid+4:.0f}" text-anchor="middle" style="font-size:9px;font-weight:500" fill="#fff">투자 {amt}</text>')

    # 노드
    for nm, (cx, cy, left, top) in node_xy.items():
        info = NODES.get(nm, {'n': nm, 'usd': None, 'g': '', 'priv': False, 'alt': False, 'sub': '', 'badge': None})
        col = COLORS.get(info['g'], '#9C9A92')
        alt = info.get('alt', False)
        priv = info.get('priv', False)

        if alt:
            dash = ' stroke-dasharray="4 2"'
            fo = '0.08'
            sw = '1.0'
        elif priv:
            dash = ' stroke-dasharray="4 2"'
            fo = '0.16'
            sw = '1.2'
        else:
            dash = ''
            fo = '0.16'
            sw = '1.2'

        # NVIDIA와 AIXTRON은 강조 테두리
        if nm in ('NVIDIA', 'AIXTRON'):
            fo = '0.24'
            sw = '1.8'

        # 노드 사각형
        s.append(f'<g style="cursor:pointer" onclick="D(\'{esc(nm)}\',\'{esc(info["g"] or "일반")}\',\'{esc(info.get("sub",""))}\')">')
        s.append(f'<rect x="{left:.0f}" y="{top:.0f}" width="{NODE_W}" height="{NODE_H}" '
                 f'rx="6" fill="{col}" fill-opacity="{fo}" stroke="{col}" stroke-width="{sw}"{dash}/>')
        # 노드명
        dn = info['n']
        if len(dn) > 14:
            dn = dn[:13] + '…'
        s.append(f'<text x="{cx:.0f}" y="{cy-3:.0f}" text-anchor="middle" '
                 f'style="font-size:10px;font-weight:500" fill="{col}">{esc(dn)}</text>')
        # 보조텍스트
        sub = info.get('sub', '')
        if len(sub) > 20:
            sub = sub[:19] + '…'
        s.append(f'<text x="{cx:.0f}" y="{cy+9:.0f}" text-anchor="middle" '
                 f'style="font-size:7px" fill="#888780">{esc(sub)}</text>')
        s.append('</g>')

        # 경고 뱃지
        badge = info.get('badge')
        if badge:
            btxt, bcol = badge
            bw = len(btxt) * 5.2 + 8
            bx = cx - bw / 2
            by = top - 14
            s.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="12" rx="3" fill="{bcol}" opacity="0.85"/>')
            s.append(f'<text x="{cx:.0f}" y="{by+8.5:.0f}" text-anchor="middle" '
                     f'style="font-size:7px;font-weight:600" fill="#fff">{esc(btxt)}</text>')

    s.append('</svg>')
    return '\n'.join(s)

svg = build()
with open('chart_a3.txt', 'w', encoding='utf-8') as f:
    f.write(svg)
_, _, H = compute_layout()
print(f"A-3 생성 완료: {len(svg):,} chars, viewBox height={H}")
