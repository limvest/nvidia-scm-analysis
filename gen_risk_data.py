#!/usr/bin/env python3
"""
risk_data.json 생성:
- scm_nodes.json 138노드 전체에 substitution score + inventory_weeks 산출
- 6개 시나리오 정의
- reshoring factor 매핑
- 6x6 correlation matrix
"""
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).parent
nodes_data = json.loads((ROOT / "scm_nodes.json").read_text())
nodes = nodes_data["nodes"]

GRADE_SCORE = {"Critical": 1.0, "High": 0.7, "Medium": 0.4, "": 0.2, None: 0.2}

def keyword_score(note):
    if not note:
        return 0.0
    s = 0.0
    for kw in ("유일", "독점", "100%", "단독", "single source"):
        if kw in note:
            s += 0.4
    return min(s, 1.0)

def tier_score(tier):
    return 1.0 if tier in (0, 1, 2) else 0.5 if tier in (3, 4) else 0.2

def base_substitution(n):
    mkt = (n.get("mkt_shr") or 0) / 100.0
    g = GRADE_SCORE.get(n.get("grade"), 0.2)
    k = keyword_score(n.get("note"))
    t = tier_score(n.get("tier", 0))
    return round(0.4*mkt + 0.3*g + 0.2*k + 0.1*t, 3)

SUBSTITUTION_OVERRIDE = {
    "asml": 1.0, "carl_zeiss": 1.0, "trumpf": 1.0, "cymer": 1.0,
    "tsmc": 0.95, "tsmc_coupe": 1.0,
    "ajinomoto": 0.85, "hamamatsu": 0.9,
    "cn_in": 0.7, "cn_phos": 0.85,
    "aixtron": 0.75, "iqe": 0.7, "sum_elec_inp": 0.6, "axt": 0.55,
    "coherent": 0.6, "lumentum": 0.6,
    "skhynix": 0.55, "micron": 0.5, "samsung_m": 0.6,
    "shinetsu_si": 0.55, "sumco": 0.45,
    "jsr": 0.6, "tok": 0.55, "tel": 0.7, "disco": 0.85,
    "advantest": 0.8, "hanmi": 0.7, "resonac": 0.55,
    "ibiden": 0.6, "ayar": 0.5, "soitec": 0.85, "gf": 0.5,
    "sivers": 0.9, "tower": 0.7, "marvell": 0.55, "broadcom": 0.5,
    "cadence": 0.85, "synopsys": 0.85, "arm": 0.9, "amphenol": 0.65,
    "nvidia": 1.0, "mellanox": 0.95,
    "foxconn": 0.3, "wistron": 0.3, "quanta": 0.3,
    "entegris": 0.5,
}

INVENTORY_BUFFER = {
    "tsmc": 6, "asml": 12, "ajinomoto": 24, "ibiden": 8,
    "coherent": 8, "lumentum": 8, "iqe": 4, "axt": 4, "sum_elec_inp": 4,
    "nvidia": 2, "foxconn": 1, "wistron": 1, "quanta": 1,
    "skhynix": 6, "micron": 6, "samsung_m": 6,
    "shinetsu_si": 8, "sumco": 8, "jsr": 6, "tok": 6,
    "aixtron": 12, "trumpf": 8, "carl_zeiss": 8, "cymer": 8,
    "hamamatsu": 6, "disco": 4, "tel": 8, "advantest": 6,
    "soitec": 12, "tower": 8, "gf": 6, "ayar": 4,
    "cn_in": 999, "cn_phos": 999, "dowa": 8,
    "marvell": 6, "broadcom": 6, "cadence": 999, "synopsys": 999, "arm": 999,
    "amphenol": 4, "mellanox": 6, "tsmc_coupe": 6,
    "sivers": 4, "resonac": 4, "hanmi": 4, "entegris": 6,
}
DEFAULT_BUFFER = 4

result_nodes = {}
for n in nodes:
    k = n["key"]
    sub = SUBSTITUTION_OVERRIDE.get(k, base_substitution(n))
    buf = INVENTORY_BUFFER.get(k, DEFAULT_BUFFER)
    result_nodes[k] = {
        "substitution": sub,
        "inventory_weeks": buf,
        "tier": n.get("tier", 0),
        "country": n.get("country", ""),
        "grade": n.get("grade", ""),
        "usd_b": n.get("usd"),
        "name": n["name"],
    }

SCENARIOS = {
    "S1_taiwan_strait": {
        "name": "대만해협 분쟁",
        "icon": "🇹🇼",
        "shock_nodes": {"tsmc": 1.0, "tsmc_coupe": 1.0},
        "shock_flows": {},
        "duration_weeks": 52,
        "probability_5y": 0.20,
        "description": "TSMC·TSMC COUPE 전면 가동 중단. 전 세계 첨단 로직 공급 차단."
    },
    "S2_china_indium": {
        "name": "중국 인듐 수출 금지",
        "icon": "🇨🇳",
        "shock_nodes": {},
        "shock_flows": {"cn_in→axt": 0.7, "cn_in→sum_elec_inp": 0.7},
        "duration_weeks": 36,
        "probability_5y": 0.35,
        "description": "인듐 글로벌 70% 공급 차단. InP 기판 체인 마비."
    },
    "S3_china_phos": {
        "name": "중국 적린 수출 통제",
        "icon": "🇨🇳",
        "shock_nodes": {},
        "shock_flows": {"cn_phos→axt": 0.8, "cn_phos→sum_elec_inp": 0.8},
        "duration_weeks": 36,
        "probability_5y": 0.30,
        "description": "적린 80% 차단. InP 합성 중단."
    },
    "S4_aixtron_shock": {
        "name": "AIXTRON 단일공급 충격",
        "icon": "⚡",
        "shock_nodes": {"aixtron": 1.0},
        "shock_flows": {},
        "duration_weeks": 78,
        "probability_5y": 0.15,
        "description": "MOCVD G10-AsP 70-90% 점유. Coherent·Lumentum·IQE 동시 노출."
    },
    "S5_japan_export": {
        "name": "일본 소재·장비 수출 통제",
        "icon": "🇯🇵",
        "shock_nodes": {},
        "shock_flows": {
            "ajinomoto→ibiden": 0.5, "jsr→tsmc": 0.5, "tok→tsmc": 0.5,
            "shinetsu_si→tsmc": 0.4, "sumco→tsmc": 0.4
        },
        "duration_weeks": 26,
        "probability_5y": 0.25,
        "description": "ABF·EUV PR·Si웨이퍼 동시 차질."
    },
    "S6_scs_blockade": {
        "name": "남중국해 봉쇄/물류 차단",
        "icon": "🌊",
        "shock_nodes": {},
        "shock_flows": {
            "tsmc→nvidia": 0.6, "skhynix→tsmc": 0.6, "samsung_m→tsmc": 0.6,
            "disco→skhynix": 0.6, "ajinomoto→ibiden": 0.6,
            "shinetsu_si→tsmc": 0.6, "sumco→tsmc": 0.6,
            "aixtron→iqe": 0.6, "aixtron→coherent": 0.6, "aixtron→lumentum": 0.6
        },
        "duration_weeks": 24,
        "probability_5y": 0.18,
        "description": "대만·일본·한국 부품 운송 60% 차질."
    }
}

CORRELATION = [
    [1.0, 0.0, 0.0, 0.0, 0.7, 0.5],
    [0.0, 1.0, 0.6, 0.0, 0.0, 0.0],
    [0.0, 0.6, 1.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    [0.7, 0.0, 0.0, 0.0, 1.0, 0.3],
    [0.5, 0.0, 0.0, 0.0, 0.3, 1.0]
]

RESHORING_FACTOR = {
    "current_2026": {},
    "2028_phase1": {
        "micron": 0.90, "tsmc": 0.85, "skhynix": 0.90, "samsung_m": 0.90,
    },
    "2030_full": {
        "micron": 0.75, "tsmc": 0.70, "skhynix": 0.80, "samsung_m": 0.80,
        "entegris": 0.85, "gf": 0.80
    },
    "accelerated": {
        "micron": 0.65, "tsmc": 0.55, "skhynix": 0.70, "samsung_m": 0.70,
        "entegris": 0.80, "gf": 0.70
    },
    "delayed": {
        "micron": 0.95, "tsmc": 0.92, "skhynix": 0.95, "samsung_m": 0.95,
    }
}

for n in nodes:
    assert n["key"] in result_nodes, f"{n['key']} missing"
    rn = result_nodes[n["key"]]
    assert 0.0 <= rn["substitution"] <= 1.0
    assert rn["inventory_weeks"] >= 1

out = {
    "nodes": result_nodes,
    "scenarios": SCENARIOS,
    "correlation": CORRELATION,
    "scenario_order": ["S1_taiwan_strait","S2_china_indium","S3_china_phos","S4_aixtron_shock","S5_japan_export","S6_scs_blockade"],
    "reshoring_factor": RESHORING_FACTOR,
    "default_buffer": DEFAULT_BUFFER,
    "version": "1.0",
    "generated_at": datetime.date.today().isoformat()
}
(ROOT / "risk_data.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(f"risk_data.json 생성 완료: {len(result_nodes)} 노드, {len(SCENARIOS)} 시나리오")
