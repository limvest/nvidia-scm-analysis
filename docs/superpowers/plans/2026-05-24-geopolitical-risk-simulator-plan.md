# 지정학적 리스크 시뮬레이터 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `index.html`에 6개 지정학 시나리오·시간축·Monte Carlo·Reshoring·Centrality를 갖춘 Goldman Sachs senior급 SCM 충격 시뮬레이터를 내장한다.

**Architecture:** 단일 페이지 (`index.html`) + 분리된 ES 모듈 3개 (`risk_sim.js`, `risk_worker.js`, `risk_data.json`). 메인 스레드는 단일 시점 propagation을 즉시 렌더, WebWorker는 1000회 Monte Carlo를 백그라운드 실행. Layer 1-4 모델: Shock Origin → 시간축 BFS Propagation → Substitution Score → Financial Impact.

**Tech Stack:** Vanilla JS (ES2020), SVG (기존 패턴), WebWorker, Python 3 (데이터 생성 스크립트). 외부 라이브러리 없음.

**Spec:** `docs/superpowers/specs/2026-05-24-geopolitical-risk-simulator-design.md`

---

## File Structure

**신규 파일**
- `gen_risk_data.py` — risk_data.json 생성 (138노드 substitution + buffer + scenarios)
- `risk_data.json` — Layer 1-3 정량 파라미터 (시나리오·버퍼·substitution·reshoring·correlation)
- `risk_sim.js` — 단일 시점 propagation 엔진 (Layer 1-4) + Centrality
- `risk_worker.js` — Monte Carlo WebWorker (1000회 + Gaussian copula)
- `tests/test_risk_sim.html` — 브라우저 기반 시각화 회귀 + 단위 검증
- `tests/test_risk_sim.js` — Node.js 단위 테스트 (risk_sim.js를 require)

**수정 파일**
- `index.html` — 우측 패널 "지정학" 탭 마크업, 컨트롤 바, `render()` 확장, 시뮬레이터 wiring

**책임 경계**
- `gen_risk_data.py`: scm_nodes.json + 인수인계서 정량값 → JSON 직렬화
- `risk_data.json`: 순수 데이터, 로직 없음
- `risk_sim.js`: 단일 propagation 1회 (deterministic) — Node·브라우저 양쪽 require 가능
- `risk_worker.js`: 확률 샘플링·반복 시뮬레이션·집계 — risk_sim.js를 importScripts
- `index.html`: UI·이벤트·SVG 렌더만. 시뮬레이션 로직은 risk_sim.js 위임

---

## Task 1: 데이터 모델 & risk_data.json 생성

**Files:**
- Create: `gen_risk_data.py`
- Create: `risk_data.json` (스크립트 실행 결과)

- [ ] **Step 1: gen_risk_data.py 작성**

```python
#!/usr/bin/env python3
"""
risk_data.json 생성:
- scm_nodes.json 138노드 전체에 substitution score + inventory_weeks 산출
- 6개 시나리오 정의
- reshoring factor 매핑
- 6x6 correlation matrix
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
nodes_data = json.loads((ROOT / "scm_nodes.json").read_text())
nodes = nodes_data["nodes"]
flows = nodes_data["flows"]

GRADE_SCORE = {"Critical": 1.0, "High": 0.7, "Medium": 0.4, "": 0.2, None: 0.2}

def keyword_score(note: str | None) -> float:
    if not note:
        return 0.0
    s = 0.0
    for kw in ("유일", "독점", "100%", "단독", "single source"):
        if kw in note:
            s += 0.4
    return min(s, 1.0)

def tier_score(tier: int) -> float:
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

# 6x6 correlation matrix (S1..S6)
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

CRITICAL_FLOWS = {f"{f['from']}→{f['to']}": f for f in flows}

# Assertions
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
    "generated_at": "2026-05-24"
}
(ROOT / "risk_data.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(f"✅ risk_data.json 생성 완료: {len(result_nodes)} 노드, {len(SCENARIOS)} 시나리오")
```

- [ ] **Step 2: 스크립트 실행**

Run: `python3 gen_risk_data.py`
Expected: `✅ risk_data.json 생성 완료: 138 노드, 6 시나리오`

- [ ] **Step 3: risk_data.json 정합성 수동 확인**

Run: `python3 -c "import json; d=json.load(open('risk_data.json')); assert len(d['nodes'])==138; assert len(d['scenarios'])==6; assert d['nodes']['tsmc']['substitution']==0.95; assert d['nodes']['asml']['substitution']==1.0; assert d['nodes']['tsmc']['inventory_weeks']==6; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add gen_risk_data.py risk_data.json
git commit -m "feat(risk-sim): risk_data.json 생성 스크립트 + 138노드 substitution/buffer 파라미터"
```

---

## Task 2: risk_sim.js 코어 propagation 엔진

**Files:**
- Create: `risk_sim.js`
- Create: `tests/test_risk_sim.js`

- [ ] **Step 1: Node 호환 risk_sim.js 작성 (Layer 1-4 단일 시점)**

```javascript
// risk_sim.js — 단일 시점 propagation 엔진 (Node + browser 양립)
// 사용:
//   브라우저: window.RiskSim = RiskSim
//   Node:    module.exports = RiskSim
//   Worker:  importScripts('risk_sim.js'); 그 후 RiskSim 사용

(function(root, factory){
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.RiskSim = factory();
}(typeof self !== 'undefined' ? self : this, function(){

  function buildFlowIndex(flows){
    const incoming = {}, outgoing = {};
    for (const f of flows){
      (incoming[f.to] = incoming[f.to] || []).push(f);
      (outgoing[f.from] = outgoing[f.from] || []).push(f);
    }
    return {incoming, outgoing};
  }

  function topoOrder(nodeKeys, flows){
    const indeg = {}, adj = {};
    nodeKeys.forEach(k => { indeg[k] = 0; adj[k] = []; });
    for (const f of flows){
      if (indeg[f.to] !== undefined){ indeg[f.to]++; adj[f.from] && adj[f.from].push(f.to); }
    }
    const q = nodeKeys.filter(k => indeg[k] === 0);
    const order = [];
    while (q.length){
      const k = q.shift();
      order.push(k);
      for (const nb of (adj[k]||[])){
        if (--indeg[nb] === 0) q.push(nb);
      }
    }
    // cycles fall through; append leftover
    for (const k of nodeKeys) if (!order.includes(k)) order.push(k);
    return order;
  }

  // Single-shot propagation up to time T weeks.
  // Returns: { nodeStatus: {key: {status, buffer, cut_in}}, flowCut: {key: cut}, summary }
  function simulate(opts){
    const {
      flows, nodeKeys, riskData,
      activeScenarios,           // array of scenario IDs
      reshoringStage='current_2026',
      t = 12
    } = opts;

    const reshoreFactor = riskData.reshoring_factor[reshoringStage] || {};
    const subOf = k => {
      const base = riskData.nodes[k]?.substitution ?? 0.5;
      const f = reshoreFactor[k];
      return f !== undefined ? base * f : base;
    };
    const bufOf = k => riskData.nodes[k]?.inventory_weeks ?? riskData.default_buffer;

    // 초기 cut 적용
    const flowCut = {};       // "from→to" -> cut [0..1]
    const initialNodeShock = {};

    for (const sid of activeScenarios){
      const s = riskData.scenarios[sid];
      if (!s) continue;
      for (const [nk, v] of Object.entries(s.shock_nodes||{})){
        initialNodeShock[nk] = Math.max(initialNodeShock[nk]||0, v);
      }
      for (const [fk, v] of Object.entries(s.shock_flows||{})){
        flowCut[fk] = Math.max(flowCut[fk]||0, v);
      }
    }

    const {incoming, outgoing} = buildFlowIndex(flows);
    const order = topoOrder(nodeKeys, flows);

    // 시간축 시뮬레이션: t=0..T
    // 노드 상태: NORMAL=0, AT_RISK=1, IMPAIRED=2, DOWN=3
    const buffer = {};
    nodeKeys.forEach(k => { buffer[k] = bufOf(k); });

    const nodeStatusFinal = {};
    for (let week = 1; week <= t; week++){
      for (const k of order){
        // 직접 충격 노드
        const directShock = initialNodeShock[k] || 0;
        // 들어오는 흐름의 가중 cut score
        const incs = incoming[k] || [];
        let cutScore = directShock;
        if (incs.length > 0){
          let total = 0, weighted = 0;
          for (const f of incs){
            const fk = `${f.from}→${f.to}`;
            const c = flowCut[fk] || 0;
            // 상류 노드가 DOWN/IMPAIRED면 해당 흐름도 cut
            const upState = nodeStatusFinal[f.from]?.status;
            let upCut = c;
            if (upState === 'DOWN') upCut = Math.max(upCut, 1.0 * (1 - subOf(f.from)));
            else if (upState === 'IMPAIRED') upCut = Math.max(upCut, 0.5 * (1 - subOf(f.from)));
            flowCut[fk] = upCut;
            weighted += upCut;
            total += 1;
          }
          const inflowCut = total ? weighted / total : 0;
          cutScore = Math.max(cutScore, inflowCut);
        }

        // 버퍼 소진/회복
        if (cutScore > 0.5){
          buffer[k] = (buffer[k] ?? bufOf(k)) - 1;
        } else if (cutScore < 0.1){
          buffer[k] = Math.min(bufOf(k), (buffer[k] ?? bufOf(k)) + 0.5);
        }

        let status;
        if (cutScore > 0.5 && buffer[k] <= 0) status = 'DOWN';
        else if (cutScore > 0.5) status = 'AT_RISK';
        else if (cutScore > 0.2) status = 'IMPAIRED';
        else status = 'NORMAL';

        nodeStatusFinal[k] = { status, buffer: buffer[k], cutScore };

        // outgoing flow propagation
        if (status === 'DOWN' || status === 'IMPAIRED'){
          for (const f of outgoing[k] || []){
            const fk = `${f.from}→${f.to}`;
            const propagate = (status === 'DOWN' ? 1.0 : 0.5) * (1 - subOf(k));
            flowCut[fk] = Math.max(flowCut[fk] || 0, propagate);
          }
        }
      }
    }

    // 집계
    const summary = aggregate(nodeStatusFinal, riskData);
    return { nodeStatus: nodeStatusFinal, flowCut, summary };
  }

  function aggregate(nodeStatus, riskData){
    let direct=0, cascaded=0, impaired=0;
    let mcDown=0, mcImpaired=0;
    for (const [k, s] of Object.entries(nodeStatus)){
      const info = riskData.nodes[k] || {};
      const mc = info.usd_b || 0;
      if (s.status === 'DOWN'){
        if (s.cutScore >= 0.95) { direct++; mcDown += mc; }
        else { cascaded++; mcDown += mc; }
      } else if (s.status === 'IMPAIRED'){
        impaired++; mcImpaired += mc;
      }
    }
    // NVIDIA revenue impact rule
    const nv = nodeStatus['nvidia']?.status;
    const tsmc = nodeStatus['tsmc']?.status;
    const cohState = nodeStatus['coherent']?.status;
    const lumState = nodeStatus['lumentum']?.status;
    let revImpact = 0;
    if (nv === 'DOWN' || tsmc === 'DOWN') revImpact = -100;
    else if (tsmc === 'IMPAIRED') revImpact = -50;
    else if (cohState === 'DOWN' || lumState === 'DOWN') revImpact = -15;
    else if (cohState === 'IMPAIRED' || lumState === 'IMPAIRED') revImpact = -8;
    return {
      direct, cascaded, impaired,
      marketcap_down_b: Math.round(mcDown*10)/10,
      marketcap_impaired_b: Math.round(mcImpaired*10)/10,
      nvidia_revenue_pct: revImpact
    };
  }

  // Critical Path Centrality: 각 노드를 단독 origin으로 시뮬해서 NVIDIA 영향 합산
  function centrality(opts){
    const { flows, nodeKeys, riskData, t=26 } = opts;
    const scores = [];
    for (const k of nodeKeys){
      // 임시 시나리오 만들기
      const tmpScenarios = { _tmp: { name:'tmp', shock_nodes:{[k]:1.0}, shock_flows:{}, duration_weeks:t, probability_5y:1 } };
      const rdClone = { ...riskData, scenarios: { ...riskData.scenarios, ...tmpScenarios } };
      const res = simulate({flows, nodeKeys, riskData: rdClone, activeScenarios:['_tmp'], t});
      scores.push({ key:k, name: riskData.nodes[k]?.name || k, score: Math.abs(res.summary.nvidia_revenue_pct) });
    }
    scores.sort((a,b)=>b.score-a.score);
    return scores.slice(0,10);
  }

  return { simulate, centrality, buildFlowIndex, topoOrder };
}));
```

- [ ] **Step 2: tests/test_risk_sim.js 작성**

```javascript
// Run with: node tests/test_risk_sim.js
const fs = require('fs');
const path = require('path');
const RiskSim = require('../risk_sim.js');

const scmData = JSON.parse(fs.readFileSync(path.join(__dirname,'../scm_nodes.json'),'utf8'));
const riskData = JSON.parse(fs.readFileSync(path.join(__dirname,'../risk_data.json'),'utf8'));

const flows = scmData.flows;
const nodeKeys = scmData.nodes.map(n=>n.key);

let pass = 0, fail = 0;
function assert(cond, msg){
  if (cond){ pass++; console.log('✅', msg); }
  else { fail++; console.log('❌', msg); }
}

// Test 1: 시나리오 비활성 → 모든 노드 NORMAL
{
  const r = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:[], t:12});
  const allNormal = Object.values(r.nodeStatus).every(s=>s.status==='NORMAL');
  assert(allNormal, 'T1: 시나리오 0개 → 전부 NORMAL');
}

// Test 2: S1 대만봉쇄 → W12 TSMC=DOWN
{
  const r = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S1_taiwan_strait'], t:12});
  assert(r.nodeStatus['tsmc'].status === 'DOWN', 'T2: S1@W12 → TSMC=DOWN');
  assert(r.nodeStatus['nvidia'].status === 'DOWN' || r.summary.nvidia_revenue_pct <= -50,
    'T2b: S1@W12 → NVIDIA major impact');
}

// Test 3: S2 인듐금지 → W12 AXT impaired/down
{
  const r = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S2_china_indium'], t:12});
  const axt = r.nodeStatus['axt'].status;
  assert(axt === 'IMPAIRED' || axt === 'DOWN' || axt === 'AT_RISK',
    `T3: S2@W12 → AXT degraded (got ${axt})`);
}

// Test 4: S4 AIXTRON → W26 IQE impacted
{
  const r = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S4_aixtron_shock'], t:26});
  assert(r.nodeStatus['aixtron'].status === 'DOWN', 'T4: S4@W26 → AIXTRON=DOWN');
  const iqe = r.nodeStatus['iqe'].status;
  assert(iqe !== 'NORMAL', `T4b: S4@W26 → IQE impacted (got ${iqe})`);
}

// Test 5: Reshoring accelerated → S1 영향이 current보다 약함 (NVIDIA rev 더 큼 (덜 음수))
{
  const cur = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S1_taiwan_strait'], t:12, reshoringStage:'current_2026'});
  const acc = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S1_taiwan_strait'], t:12, reshoringStage:'accelerated'});
  assert(acc.summary.nvidia_revenue_pct >= cur.summary.nvidia_revenue_pct,
    `T5: accelerated reshoring 완화 (cur=${cur.summary.nvidia_revenue_pct} acc=${acc.summary.nvidia_revenue_pct})`);
}

// Test 6: Centrality Top 10에 asml/tsmc/carl_zeiss 포함
{
  const top = RiskSim.centrality({flows, nodeKeys, riskData, t:26});
  const keys = top.map(x=>x.key);
  assert(keys.includes('asml') || keys.includes('tsmc'),
    `T6: Centrality Top 10에 asml/tsmc 포함 (${keys.join(',')})`);
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail > 0 ? 1 : 0);
```

- [ ] **Step 3: 테스트 실행**

Run: `node tests/test_risk_sim.js`
Expected: 모든 테스트 PASS, exit 0

- [ ] **Step 4: 실패 시 조정**

Test가 실패하면 substitution/buffer 값 또는 propagation 로직을 조정. 특히:
- T2가 실패하면 TSMC buffer를 줄이거나 shock_nodes 적용 로직 확인
- T3가 NORMAL이면 cn_in→axt cut score 전파 점검
- T5가 실패하면 reshoring factor 적용 확인

조정 후 다시 `node tests/test_risk_sim.js` 실행하여 PASS 확인.

- [ ] **Step 5: Commit**

```bash
git add risk_sim.js tests/test_risk_sim.js
git commit -m "feat(risk-sim): Layer 1-4 propagation 엔진 + 단위테스트 6개"
```

---

## Task 3: index.html UI 마크업 추가 (탭/패널/컨트롤바)

**Files:**
- Modify: `index.html`

- [ ] **Step 1: country-bar 아래에 risk-bar 추가**

`index.html`의 `<div id="extra-bar">` 다음 줄에 다음 div를 삽입:

```html
<div id="risk-bar" style="display:flex;align-items:center;gap:8px;padding:4px 12px;background:#0c0c0a;border-bottom:1px solid #2a2a28;font-size:10px;color:#ccc">
  <span style="font-weight:700;color:#ef4444">🌐 지정학 시뮬</span>
  <button id="risk-toggle" onclick="riskToggle()" style="padding:3px 10px;border:1px solid #555;background:#1a1a18;color:#ccc;border-radius:4px;cursor:pointer;font-size:10px">OFF</button>
  <span style="opacity:0.6">|</span>
  <span>주차 <span id="risk-week-label">12</span></span>
  <input type="range" id="risk-week" min="0" max="52" value="12" step="1" oninput="riskSetWeek(this.value)" style="width:140px;accent-color:#ef4444" disabled>
  <span style="opacity:0.6">|</span>
  <span>Reshoring</span>
  <select id="risk-reshoring" onchange="riskSetReshoring(this.value)" style="background:#1a1a18;color:#ccc;border:1px solid #555;border-radius:4px;padding:2px 4px;font-size:10px" disabled>
    <option value="current_2026">현재(2026)</option>
    <option value="2028_phase1">2028 Phase1</option>
    <option value="2030_full">2030 Full</option>
    <option value="accelerated">가속</option>
    <option value="delayed">지연</option>
  </select>
  <span style="opacity:0.6">|</span>
  <span id="risk-summary" style="color:#f97316;font-weight:600">시뮬 OFF</span>
</div>
```

- [ ] **Step 2: 우측 패널 탭에 "지정학" 탭 추가**

기존 탭 버튼들 (`ptab-overview`, `ptab-risk`, `ptab-feynman` 근처) 라인을 찾아 옆에 추가:

기존:
```html
<button class="ptab"    id="ptab-risk"     onclick="switchPanelTab('risk')">리스크</button>
```

다음 줄에 추가:
```html
<button class="ptab"    id="ptab-geosim"   onclick="switchPanelTab('geosim')">🌐 지정학</button>
```

- [ ] **Step 3: 우측 패널 컨텐츠 div 추가**

기존 `<div id="panel-content">` 안의 다른 탭 컨텐츠 옆에 다음 div 추가 (다른 탭들 마지막):

```html
<div id="ptab-content-geosim" style="display:none;flex-direction:column;gap:8px;padding:8px;overflow-y:auto;font-size:10px;color:#ddd">
  <div style="font-size:11px;font-weight:700;color:#ef4444;border-bottom:1px solid #2a2a28;padding-bottom:4px">🌐 지정학 리스크 시뮬레이터</div>

  <div style="background:#0d0d0b;padding:6px;border-radius:4px;border:1px solid #2a2a28">
    <div style="font-weight:700;margin-bottom:4px;color:#fbbf24">◇ 활성 시나리오</div>
    <div id="risk-scenario-list"></div>
    <label style="display:flex;align-items:center;gap:4px;margin-top:4px;font-size:9px;color:#aaa">
      <input type="checkbox" id="risk-correlation" onchange="riskRender()" style="accent-color:#ef4444">
      상관관계 자동 적용
    </label>
  </div>

  <div style="background:#0d0d0b;padding:6px;border-radius:4px;border:1px solid #2a2a28">
    <div style="font-weight:700;margin-bottom:4px;color:#fbbf24">━━ Impact @ W<span id="risk-impact-week">12</span> ━━</div>
    <div id="risk-impact-body" style="line-height:1.6;font-family:monospace;font-size:9.5px"></div>
  </div>

  <div style="background:#0d0d0b;padding:6px;border-radius:4px;border:1px solid #2a2a28">
    <div style="font-weight:700;margin-bottom:4px;color:#fbbf24">━━ Monte Carlo ━━</div>
    <button id="risk-mc-run" onclick="riskRunMonteCarlo()" style="padding:3px 8px;border:1px solid #555;background:#1a1a18;color:#ccc;border-radius:4px;cursor:pointer;font-size:10px;width:100%">1000회 시뮬 실행</button>
    <div id="risk-mc-progress" style="margin-top:4px;font-size:9px;color:#aaa"></div>
    <div id="risk-mc-result" style="margin-top:4px;font-family:monospace;font-size:9.5px"></div>
  </div>

  <div style="background:#0d0d0b;padding:6px;border-radius:4px;border:1px solid #2a2a28">
    <div style="font-weight:700;margin-bottom:4px;color:#fbbf24">━━ Centrality Top 10 ━━</div>
    <div id="risk-centrality-list" style="font-family:monospace;font-size:9.5px"></div>
  </div>

  <div style="background:#0d0d0b;padding:6px;border-radius:4px;border:1px solid #2a2a28;color:#888;font-size:9px;line-height:1.5">
    <div style="font-weight:700;color:#aaa">⚠ 가정·한계</div>
    <div>• Inventory buffer: 명시값 외 4주 디폴트 추정</div>
    <div>• Substitution score: mkt_shr·grade·키워드에서 계산 + 수동 보정</div>
    <div>• 상관계수: GEO_RESHORE_ANALYSIS 정성적 도출</div>
    <div>• 가격 영향·수요충격 미모델링 (Phase 3)</div>
  </div>
</div>
```

- [ ] **Step 4: switchPanelTab() 함수 수정 (geosim 탭 처리 추가)**

`switchPanelTab` 함수 찾아서 (line 4019 근처) 다음 코드 패턴:

기존:
```javascript
['overview','risk','feynman'].forEach(t =>
  document.getElementById('ptab-'+t).classList.toggle('on', t===tab));
```

수정:
```javascript
['overview','risk','feynman','geosim'].forEach(t => {
  const btn=document.getElementById('ptab-'+t);
  if (btn) btn.classList.toggle('on', t===tab);
  const cnt=document.getElementById('ptab-content-'+t);
  if (cnt) cnt.style.display = (t===tab) ? 'flex' : 'none';
});
if (tab === 'geosim') { riskInitPanel(); return; }
```

- [ ] **Step 5: 브라우저로 열어 마크업만 정상 표시 확인**

Run: `open index.html`
브라우저에서 확인:
- 상단 risk-bar가 표시되고 "🌐 지정학 시뮬 [OFF]" 보임
- 우측 패널 탭에 "🌐 지정학" 추가됨
- 탭 클릭 시 마크업 표시 (값은 비어있음, 다음 task에서 채움)

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat(risk-sim): UI 마크업 (risk-bar, 지정학 탭, 빈 컨테이너)"
```

---

## Task 4: index.html에 risk_sim.js 로드 + state 초기화

**Files:**
- Modify: `index.html`

- [ ] **Step 1: risk_sim.js 스크립트 태그 추가**

`<script>` 블록 시작 직전(`const DATA = {...}` 위)에 추가:

```html
<script src="risk_sim.js"></script>
```

- [ ] **Step 2: risk_data.json 로드 + 시뮬레이션 상태 변수 추가**

기존 전역 변수들 (`let currentNodeKey=null` 근처)에 다음 추가:

```javascript
let riskData = null;
let riskState = {
  active: false,
  week: 12,
  reshoring: 'current_2026',
  scenarios: new Set(),
  correlation: false,
  lastResult: null,   // {nodeStatus, flowCut, summary}
  mcResult: null,     // {p5, p50, p95, mean, histogram}
};
let riskWorker = null;

async function riskLoadData(){
  if (riskData) return riskData;
  try {
    const r = await fetch('risk_data.json');
    riskData = await r.json();
    return riskData;
  } catch(e){
    console.error('risk_data.json 로드 실패:', e);
    return null;
  }
}
```

- [ ] **Step 3: 시나리오 토글/주차/Reshoring 핸들러 함수 추가**

스크립트 영역 끝(`</script>` 직전)에 추가:

```javascript
function riskToggle(){
  riskState.active = !riskState.active;
  const btn = document.getElementById('risk-toggle');
  btn.textContent = riskState.active ? 'ON' : 'OFF';
  btn.style.background = riskState.active ? '#7f1d1d' : '#1a1a18';
  btn.style.color = riskState.active ? '#fff' : '#ccc';
  document.getElementById('risk-week').disabled = !riskState.active;
  document.getElementById('risk-reshoring').disabled = !riskState.active;
  if (riskState.active){
    riskLoadData().then(() => {
      riskInitPanel();
      riskRender();
    });
  } else {
    document.getElementById('risk-summary').textContent = '시뮬 OFF';
    render();
  }
}

function riskSetWeek(v){
  riskState.week = parseInt(v,10);
  document.getElementById('risk-week-label').textContent = v;
  document.getElementById('risk-impact-week').textContent = v;
  riskRender();
}

function riskSetReshoring(v){
  riskState.reshoring = v;
  riskRender();
}

function riskToggleScenario(sid){
  if (riskState.scenarios.has(sid)) riskState.scenarios.delete(sid);
  else riskState.scenarios.add(sid);
  riskRender();
}

function riskInitPanel(){
  if (!riskData) return;
  const list = document.getElementById('risk-scenario-list');
  if (!list) return;
  if (list.children.length > 0) return; // already initialized
  const order = riskData.scenario_order;
  for (const sid of order){
    const s = riskData.scenarios[sid];
    const lbl = document.createElement('label');
    lbl.style.cssText = 'display:flex;align-items:center;gap:4px;font-size:9.5px;padding:2px 0;cursor:pointer';
    lbl.innerHTML = `
      <input type="checkbox" data-sid="${sid}" onchange="riskToggleScenario('${sid}')" style="accent-color:#ef4444">
      <span>${s.icon} ${s.name}</span>
      <span style="opacity:0.55;margin-left:auto">p=${Math.round(s.probability_5y*100)}%</span>
    `;
    lbl.title = s.description;
    list.appendChild(lbl);
  }
}

// 상관 적용: 활성 시나리오에서 파생되는 추가 활성 시나리오 ID 셋 반환
function riskCorrelatedScenarios(active){
  if (!riskState.correlation || !riskData) return new Set(active);
  const result = new Set(active);
  const order = riskData.scenario_order;
  const idxOf = sid => order.indexOf(sid);
  for (const sid of active){
    const i = idxOf(sid);
    if (i<0) continue;
    for (let j=0;j<order.length;j++){
      if (i===j) continue;
      const corr = riskData.correlation[i][j];
      if (corr >= 0.5) result.add(order[j]);
    }
  }
  return result;
}

function riskRender(){
  if (!riskState.active || !riskData){
    document.getElementById('risk-summary').textContent = '시뮬 OFF';
    render();
    return;
  }
  const flows = DATA.flows;
  const nodeKeys = DATA.nodes.map(n=>n.key);
  const active = [...riskCorrelatedScenarios(riskState.scenarios)];
  const res = RiskSim.simulate({
    flows, nodeKeys, riskData,
    activeScenarios: active,
    reshoringStage: riskState.reshoring,
    t: riskState.week
  });
  riskState.lastResult = res;

  // 상단 요약
  const s = res.summary;
  document.getElementById('risk-summary').textContent =
    `시나리오 ${riskState.scenarios.size}개 활성 | NVIDIA ${s.nvidia_revenue_pct}% | 다운 ${s.direct + s.cascaded}개`;

  // Impact 패널
  const body = document.getElementById('risk-impact-body');
  if (body){
    body.innerHTML = `
      Direct hits:     ${s.direct} <span style="color:#888">nodes</span>
      Cascaded down:   ${s.cascaded} <span style="color:#888">($${s.marketcap_down_b}B)</span>
      Impaired:        ${s.impaired} <span style="color:#888">($${s.marketcap_impaired_b}B)</span>
      <br>
      <span style="color:#ef4444;font-weight:700">NVIDIA Rubin: ${s.nvidia_revenue_pct}%</span>
    `.replace(/\n/g,'<br>');
  }

  // Centrality (한 번만 계산해서 캐싱)
  if (!riskState.centrality){
    riskState.centrality = RiskSim.centrality({flows, nodeKeys, riskData, t:26});
    const cl = document.getElementById('risk-centrality-list');
    if (cl){
      cl.innerHTML = riskState.centrality.map((x,i) =>
        `${(i+1).toString().padStart(2)}. <span style="color:#fbbf24">${x.name.slice(0,18)}</span> <span style="opacity:0.6;float:right">score ${x.score}</span>`
      ).join('<br>');
    }
  }

  // 메인 차트 재렌더
  render();
}
```

- [ ] **Step 4: 브라우저로 검증**

Run: `open index.html`
- "🌐 지정학 시뮬" ON 클릭 → 우측 "🌐 지정학" 탭 자동 활성, 시나리오 체크박스 6개 표시
- S1 체크 → 우측 패널에 "Direct hits, Cascaded down, NVIDIA Rubin" 수치 표시
- 주차 슬라이더 이동 → Impact 패널 수치 변화

이 시점에서 차트 자체는 아직 노드 색이 안 변함 (다음 Task 5에서 render 확장).

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat(risk-sim): risk_sim.js 로드 + state · 이벤트 핸들러 · Impact 패널 wiring"
```

---

## Task 5: render() 확장하여 노드/흐름 상태별 시각화

**Files:**
- Modify: `index.html`

- [ ] **Step 1: 노드 렌더 코드에 상태 오버레이 추가**

기존 `render()` 함수 안 `for(const n of vis){...}` 노드 렌더 루프를 찾는다. `g.appendChild(se('rect',ra));` 직후 (`const textC=hl?sc:'#3a3a38';` 직전)에 다음 코드를 삽입:

```javascript
// Risk simulator: 상태별 오버레이
if (riskState.active && riskState.lastResult){
  const rs = riskState.lastResult.nodeStatus[n.key];
  if (rs){
    if (rs.status === 'DOWN'){
      // 빨간 X자 + 빨간 fill 오버레이
      g.appendChild(se('rect',{x:p.x,y:p.y,width:NW,height:NH,rx:'5',
        fill:'#dc2626','fill-opacity':'0.30',stroke:'#ef4444','stroke-width':'1.5'}));
      g.appendChild(se('line',{x1:p.x+4,y1:p.y+4,x2:p.x+NW-4,y2:p.y+NH-4,
        stroke:'#ef4444','stroke-width':'2','stroke-linecap':'round'}));
      g.appendChild(se('line',{x1:p.x+NW-4,y1:p.y+4,x2:p.x+4,y2:p.y+NH-4,
        stroke:'#ef4444','stroke-width':'2','stroke-linecap':'round'}));
    } else if (rs.status === 'IMPAIRED'){
      g.appendChild(se('rect',{x:p.x,y:p.y,width:NW,height:NH,rx:'5',
        fill:'#f97316','fill-opacity':'0.18',stroke:'#fb923c','stroke-width':'1.5',
        'stroke-dasharray':'4 2'}));
    } else if (rs.status === 'AT_RISK'){
      g.appendChild(se('circle',{cx:p.x+NW-6,cy:p.y+6,r:'3',fill:'#facc15',
        stroke:'#eab308','stroke-width':'1'}));
    }
  }
}
```

- [ ] **Step 2: 흐름 렌더 코드에 상태별 색 적용**

`render()` 함수 안 흐름 렌더 루프(`for(const f of DATA.flows){...}` 안 `svgContent.appendChild(se('path', ... 'marker-end':flowMarker(act)}));` 라인 직전)에 다음 분기 추가 (`else if(countryFilter...)` 분기 다음, `}else if(mode!=='all')` 분기 직전):

```javascript
// Risk simulator override
if (riskState.active && riskState.lastResult){
  const fkey = `${f.from}→${f.to}`;
  const cut = riskState.lastResult.flowCut[fkey] || 0;
  if (cut >= 0.8){
    fc = '#ef4444'; sw = '1.8'; op = '0.85';
  } else if (cut >= 0.4){
    fc = '#fb923c'; sw = '1.2'; op = '0.7';
  } else if (cut >= 0.1){
    fc = '#fbbf24'; sw = '0.7'; op = '0.5';
  }
}
```

흐름 렌더 path 추가 후, 끊긴 흐름에는 X 마커도 그리기:
```javascript
// (위 path append 직후에 추가)
if (riskState.active && riskState.lastResult){
  const fkey = `${f.from}→${f.to}`;
  const cut = riskState.lastResult.flowCut[fkey] || 0;
  if (cut >= 0.8){
    const mx = (x1+x2)/2, mmy = (y1+y2)/2;
    svgContent.appendChild(se('line',{x1:mx-4,y1:mmy-4,x2:mx+4,y2:mmy+4,stroke:'#ef4444','stroke-width':'1.8','stroke-linecap':'round'}));
    svgContent.appendChild(se('line',{x1:mx+4,y1:mmy-4,x2:mx-4,y2:mmy+4,stroke:'#ef4444','stroke-width':'1.8','stroke-linecap':'round'}));
  }
}
```

- [ ] **Step 3: 브라우저 시각 검증**

Run: `open index.html`
- 시뮬 ON, S1 (대만봉쇄) 체크, 주차=12
- 차트: TSMC·TSMC COUPE에 빨간 X자, NVIDIA·foxconn·wistron·quanta·marvell·broadcom 등에 빨간 X 또는 주황 점선
- S1 OFF → 차트 정상 복귀

- [ ] **Step 4: 회귀 — 시뮬 OFF 시 기존 차트 픽셀-동일**

시뮬 OFF 상태에서 country filter, grade filter, mode 변경이 모두 기존대로 작동하는지 확인.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat(risk-sim): render() 확장 — 노드 상태 X자/점선/노란점, 흐름 cut 색상"
```

---

## Task 6: risk_worker.js — Monte Carlo + Gaussian Copula

**Files:**
- Create: `risk_worker.js`
- Modify: `index.html`

- [ ] **Step 1: risk_worker.js 작성**

```javascript
// risk_worker.js — Monte Carlo 시뮬레이션 (Web Worker)
importScripts('risk_sim.js');

// Box-Muller로 표준정규 z 1개 추출
function gauss(){
  let u=0,v=0;
  while(u===0)u=Math.random();
  while(v===0)v=Math.random();
  return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);
}

// Cholesky decomposition (6x6, symmetric positive)
function cholesky(A){
  const n = A.length;
  const L = Array.from({length:n},()=>Array(n).fill(0));
  for (let i=0;i<n;i++){
    for (let j=0;j<=i;j++){
      let s=0;
      for (let k=0;k<j;k++) s += L[i][k]*L[j][k];
      if (i===j) L[i][j] = Math.sqrt(Math.max(A[i][i]-s, 0));
      else L[i][j] = L[j][j] === 0 ? 0 : (A[i][j]-s)/L[j][j];
    }
  }
  return L;
}

// 표준정규 CDF (Abramowitz & Stegun 근사)
function normalCdf(x){
  const a1=0.254829592,a2=-0.284496736,a3=1.421413741,a4=-1.453152027,a5=1.061405429,p=0.3275911;
  const sign = x<0?-1:1;
  const ax = Math.abs(x)/Math.sqrt(2);
  const t = 1.0/(1.0 + p*ax);
  const y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*Math.exp(-ax*ax);
  return 0.5*(1.0 + sign*y);
}

// 다변량 정규 샘플 (correlation L = Cholesky)
function correlatedSample(L){
  const n = L.length;
  const z = Array.from({length:n},()=>gauss());
  const x = Array(n).fill(0);
  for (let i=0;i<n;i++){
    let s=0;
    for (let j=0;j<=i;j++) s += L[i][j]*z[j];
    x[i] = s;
  }
  // Convert to uniform via CDF (Gaussian copula)
  return x.map(normalCdf);
}

let RUNNING = false;

self.onmessage = async (e) => {
  const {cmd, payload} = e.data;
  if (cmd === 'run'){
    RUNNING = true;
    const {flows, nodeKeys, riskData, reshoring, week, useCorrelation, nRuns} = payload;
    const order = riskData.scenario_order;
    const L = useCorrelation ? cholesky(riskData.correlation) : null;
    const probs = order.map(sid => riskData.scenarios[sid].probability_5y);

    const results = [];
    const histBins = 21; // -100% to 0% in 5% buckets
    const histogram = Array(histBins).fill(0);

    for (let i=0;i<nRuns;i++){
      if (!RUNNING) break;
      // 시나리오 추첨
      let uniforms;
      if (L) uniforms = correlatedSample(L);
      else uniforms = order.map(()=>Math.random());

      const active = [];
      for (let s=0;s<order.length;s++){
        if (uniforms[s] < probs[s]) active.push(order[s]);
      }

      const res = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios: active, reshoringStage: reshoring, t: week});
      const imp = res.summary.nvidia_revenue_pct;
      results.push(imp);
      const binIdx = Math.min(histBins-1, Math.max(0, Math.floor((-imp)/5)));
      histogram[binIdx]++;

      if (i%50 === 0){
        self.postMessage({type:'progress', value: Math.round(i/nRuns*100)});
      }
    }

    results.sort((a,b)=>a-b);
    const pct = q => results[Math.floor(results.length*q)];
    const mean = results.reduce((a,b)=>a+b,0)/results.length;

    self.postMessage({
      type: 'done',
      result: {
        p5: pct(0.05), p50: pct(0.50), p95: pct(0.95),
        mean: Math.round(mean*100)/100,
        histogram,
        n: results.length
      }
    });
    RUNNING = false;
  } else if (cmd === 'stop'){
    RUNNING = false;
  }
};
```

- [ ] **Step 2: index.html에 Monte Carlo 실행 함수 추가**

스크립트 영역 (`riskRender` 함수 다음)에 추가:

```javascript
function riskRunMonteCarlo(){
  if (!riskData) return;
  if (!riskWorker){
    riskWorker = new Worker('risk_worker.js');
    riskWorker.onmessage = (e) => {
      const {type, value, result} = e.data;
      const prog = document.getElementById('risk-mc-progress');
      const out = document.getElementById('risk-mc-result');
      if (type === 'progress'){
        if (prog) prog.textContent = `진행: ${value}%`;
      } else if (type === 'done'){
        if (prog) prog.textContent = `완료 (n=${result.n})`;
        if (out){
          const fmt = v => `${Math.round(v)}%`;
          const histMax = Math.max(...result.histogram);
          const histBars = result.histogram.map((c,i) => {
            const h = Math.round(c/histMax*30);
            const label = -i*5;
            return `<div style="display:flex;align-items:center;gap:2px"><span style="width:24px;font-size:8px;color:#888">${label}%</span><div style="background:#ef4444;height:5px;width:${c/histMax*100}%"></div><span style="font-size:8px;color:#888">${c}</span></div>`;
          }).join('');
          out.innerHTML = `
            <div style="color:#fbbf24;font-weight:700">NVIDIA Revenue Distribution</div>
            <div>P5:   <span style="color:#ef4444">${fmt(result.p5)}</span></div>
            <div>P50:  <span style="color:#fb923c">${fmt(result.p50)}</span></div>
            <div>P95:  <span style="color:#84cc16">${fmt(result.p95)}</span></div>
            <div>Mean: <span style="color:#facc15">${fmt(result.mean)}</span></div>
            <div style="margin-top:4px">${histBars}</div>
          `;
        }
        riskState.mcResult = result;
      }
    };
  }
  const flows = DATA.flows;
  const nodeKeys = DATA.nodes.map(n=>n.key);
  riskWorker.postMessage({
    cmd: 'run',
    payload: {
      flows, nodeKeys, riskData,
      reshoring: riskState.reshoring,
      week: riskState.week,
      useCorrelation: document.getElementById('risk-correlation').checked,
      nRuns: 1000
    }
  });
  document.getElementById('risk-mc-progress').textContent = '시작 중...';
}
```

- [ ] **Step 3: 브라우저 검증**

Run: `open index.html`
- 시뮬 ON → 지정학 탭 → "1000회 시뮬 실행" 클릭
- 진행률 0~100% 표시
- 완료 후 P5/P50/P95/Mean + 히스토그램 막대 표시
- "상관관계 자동 적용" 체크 후 재실행 → 상관 적용 결과는 P5가 더 왼쪽(더 음수)에 위치

- [ ] **Step 4: Commit**

```bash
git add risk_worker.js index.html
git commit -m "feat(risk-sim): Monte Carlo WebWorker + Gaussian copula 상관 샘플링 + 히스토그램"
```

---

## Task 7: 노드 클릭 시 충격 분해 정보 추가

**Files:**
- Modify: `index.html`

- [ ] **Step 1: 노드 클릭 시 충격 정보 패널에 추가 정보 표시**

기존 `selectNode()` 함수를 찾는다 (검색: `function selectNode`). 함수 본문 끝(또는 panel render 직전)에 다음 코드 추가:

```javascript
// Risk shock breakdown
if (riskState.active && riskState.lastResult){
  const rs = riskState.lastResult.nodeStatus[key];
  if (rs){
    const info = riskData.nodes[key] || {};
    const breakdown = document.createElement('div');
    breakdown.id = 'risk-node-breakdown';
    breakdown.style.cssText = 'background:#1a0a0a;padding:6px;margin-top:6px;border:1px solid #7f1d1d;border-radius:4px;font-size:9.5px;color:#ddd;font-family:monospace';
    const statusColor = rs.status==='DOWN'?'#ef4444':rs.status==='IMPAIRED'?'#fb923c':rs.status==='AT_RISK'?'#facc15':'#84cc16';
    breakdown.innerHTML = `
      <div style="color:#ef4444;font-weight:700">⚠ 충격 분해 @ W${riskState.week}</div>
      <div>Status: <span style="color:${statusColor};font-weight:700">${rs.status}</span></div>
      <div>Buffer 잔여: ${Math.max(0,Math.round(rs.buffer*10)/10)} weeks</div>
      <div>Cut score: ${Math.round((rs.cutScore||0)*100)}%</div>
      <div>Substitution: ${info.substitution}</div>
      <div>Initial buffer: ${info.inventory_weeks} weeks</div>
    `;
    // panel-content 안 currently visible tab에 append
    const panel = document.getElementById('ptab-content-overview') || document.getElementById('panel-content');
    const existing = document.getElementById('risk-node-breakdown');
    if (existing) existing.remove();
    if (panel) panel.appendChild(breakdown);
  }
}
```

- [ ] **Step 2: 브라우저 검증**

- 시뮬 ON, S1 활성, 주차=12
- 차트에서 TSMC 노드 클릭 → 우측 패널(overview 탭)에 "⚠ 충격 분해 @ W12 / Status: DOWN / Buffer 잔여: 0 / ..." 표시

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat(risk-sim): 노드 클릭 시 충격 분해 패널 (status·buffer·cut·substitution)"
```

---

## Task 8: 최종 통합 검증 (end-to-end)

**Files:**
- Run: `tests/test_risk_sim.js`

- [ ] **Step 1: 단위 테스트 전체 재실행**

Run: `node tests/test_risk_sim.js`
Expected: 6/6 pass

- [ ] **Step 2: 브라우저 종합 검증 체크리스트**

`open index.html` 후 다음을 모두 확인:

1. ✅ 시뮬 OFF 상태: 기존 차트가 깨지지 않음, country/grade/mode 필터 정상
2. ✅ 시뮬 ON: risk-bar의 OFF→ON 토글, 슬라이더·셀렉트 활성화
3. ✅ S1 대만봉쇄 단독: TSMC·TSMC COUPE에 빨간 X, NVIDIA major 영향
4. ✅ S2 인듐금지 단독: AXT·Sumitomo InP·IQE 등 빨간/주황
5. ✅ S4 AIXTRON 단독 W26: AIXTRON DOWN, IQE/Coherent/Lumentum 영향
6. ✅ 시간 슬라이더 W0→W52 부드럽게 작동 (60fps 체감)
7. ✅ Reshoring `accelerated` 선택 시 같은 시나리오에서 NVIDIA 영향 완화
8. ✅ 상관 자동 적용 체크 시 S1만 활성해도 S5/S6 효과 동반
9. ✅ Monte Carlo 1000회 5초 내 완료, P5/P50/P95 + 히스토그램 표시
10. ✅ Centrality Top 10에 asml/tsmc/carl_zeiss/trumpf 등 합리적 노드 상위
11. ✅ TSMC 클릭 시 충격 분해 패널 표시

- [ ] **Step 3: 발견된 버그 수정**

체크리스트 중 실패 항목이 있으면 해당 Task로 돌아가 수정 후 다시 검증.

- [ ] **Step 4: 최종 commit (변경 없으면 스킵)**

```bash
git status
# 변경 있으면:
git add -A
git commit -m "fix(risk-sim): 통합 검증 후 버그 수정"
```

---

## Self-Review Notes

스펙 13개 섹션 → 8개 task 매핑:
- 섹션 3 (4-Layer 모델) → Task 1, 2
- 섹션 4 (Monte Carlo) → Task 6
- 섹션 5 (Reshoring) → Task 1, 2 (factor), Task 4 (UI)
- 섹션 6 (Centrality) → Task 2, 4
- 섹션 7 (UI) → Task 3, 4, 5, 7
- 섹션 8 (데이터 파일) → Task 1
- 섹션 9 (구현단위 10개) → 본 plan은 8개로 통합 (단위 6, 8, 9, 10이 task 2/4/5/8에 흡수)
- 섹션 10 (테스트) → Task 2 (단위), Task 8 (E2E)
- 섹션 12 (완료정의 9개) → Task 8 체크리스트
