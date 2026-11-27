# 지정학적 리스크 시뮬레이터 (Geopolitical Risk Simulator)

**작성일:** 2026-05-24
**대상 산출물:** `index.html` 내장 인터랙티브 시뮬레이터 + 사전계산 데이터 JSON
**기준 품질:** Goldman Sachs senior급 SCM 충격 모델
**브레인스토밍 산출:** 6개 시나리오, 시간축 BFS 전파, Substitution score, Monte Carlo, Reshoring Optionality, Cross-correlation

---

## 1. 목표와 비목표

### 목표
1. 6개 지정학 시나리오를 단일 또는 다중 토글로 켜고 끄며, 실시간으로 SCM 차트(138노드, 52흐름) 위에 충격 전파를 시각화한다.
2. 시간축(W1~W52)을 따라 어떤 노드가 언제 무너지는지 보여준다.
3. 재고 버퍼와 substitution score를 반영한 **연쇄 전파 모델**을 구현한다.
4. Monte Carlo로 P50/P90 NVIDIA 매출 영향 분포를 제공한다.
5. CHIPS Act reshoring 진행도에 따른 충격 완화를 카운터팩추얼 분석으로 보여준다.
6. 시나리오 간 상관관계를 6×6 매트릭스로 모델링한다.
7. Critical Path Centrality 랭킹으로 "어느 노드가 가장 위험한가"를 정량화한다.

### 비목표
- 새 차트 페이지를 만들지 않는다. `index.html`을 확장한다.
- 노드 데이터(138개)·흐름 데이터(52개)를 새로 만들지 않는다. 기존 `scm_nodes.json` + `index.html` 내장 DATA를 그대로 사용한다.
- 가격(commodity price) 영향, 재고 일변동, 환율, 정책 시차 모델링은 Phase 3로 미룬다.
- 결과를 외부 시스템(Bloomberg/FactSet)으로 내보내지 않는다.

---

## 2. 사용자 흐름

### 진입
사용자는 기존처럼 `index.html`을 연다. 우측 패널 탭 옆에 **"지정학"** 탭이 새로 추가된다(기존 overview/risk/feynman 탭과 동렬).

### 시뮬레이터 ON
"지정학" 탭 클릭 → 우측 패널이 시뮬레이터 UI로 전환되고, 상단 컨트롤 바에 시뮬레이션 모드 배너가 표시된다.

### 시나리오 토글
시뮬레이터 패널의 시나리오 6개를 체크박스로 ON/OFF 한다. 토글 즉시 `render()`가 재호출되어 차트 위 노드/흐름이 다시 칠해진다.

### 시간 슬라이더
패널 상단의 슬라이더로 W0(충격 직전)~W52(1년 후)를 이동한다. 각 시점의 노드 상태가 즉시 갱신된다.

### CHIPS Act 슬라이더
"Reshoring 진행도" 슬라이더: `current(2026)` / `2028` / `2030` / `accelerated` / `delayed` 5단계. 단계마다 미국 팹 노드의 substitution score가 변하여 충격 완화 정도가 달라진다.

### Monte Carlo 보기
"확률 분석" 토글 → 우측 패널에 P50/P90 NVIDIA 매출 분포 막대그래프가 표시된다. WebWorker 백그라운드 1000회.

### 노드 클릭
충격 상태에서도 노드 클릭은 기존처럼 작동한다. 추가로 클릭 노드의 "충격 분해" 미니 패널이 떠서 "이 노드가 깨진 이유: input X가 W12에 끊김, substitution=0.85"를 보여준다.

---

## 3. 4-Layer 충격 전파 모델

### Layer 1: Shock Origin

각 시나리오 = (초기 충격 노드 집합, 초기 충격 흐름 집합, 강도 0~1, 지속 기간, 발생 확률)

```js
SCENARIOS = {
  S1_taiwan_strait: {
    name: '대만해협 분쟁',
    shock_nodes: { tsmc: 1.0, tsmc_coupe: 1.0 },
    shock_flows: {},
    duration_weeks: 52,        // 무기한, 차트 범위 끝
    probability_5y: 0.20,      // 15~25% 중간값
    correlation_trigger: { S5_japan_export: 0.7, S6_scs_blockade: 0.5 }
  },
  S2_china_indium: {
    name: '중국 인듐 수출 금지',
    shock_nodes: {},
    shock_flows: { 'cn_in→axt': 0.7, 'cn_in→sum_elec_inp': 0.7 },
    duration_weeks: 36,
    probability_5y: 0.35,
    correlation_trigger: { S3_china_phos: 0.6 }
  },
  S3_china_phos: {
    name: '중국 적린 수출 통제',
    shock_nodes: {},
    shock_flows: { 'cn_phos→axt': 0.8, 'cn_phos→sum_elec_inp': 0.8 },
    duration_weeks: 36,
    probability_5y: 0.30,
    correlation_trigger: { S2_china_indium: 0.6 }
  },
  S4_aixtron_shock: {
    name: 'AIXTRON 단일공급 충격',
    shock_nodes: { aixtron: 1.0 },
    shock_flows: {},
    duration_weeks: 78,        // 재가동 12~24mo
    probability_5y: 0.15,
    correlation_trigger: {}
  },
  S5_japan_export: {
    name: '일본 소재·장비 수출 통제',
    shock_nodes: {},
    shock_flows: {
      'ajinomoto→ibiden': 0.5, 'jsr→tsmc': 0.5, 'tok→tsmc': 0.5,
      'shinetsu_si→tsmc': 0.4, 'sumco→tsmc': 0.4
    },
    duration_weeks: 26,
    probability_5y: 0.25,
    correlation_trigger: { S1_taiwan_strait: 0.4 }
  },
  S6_scs_blockade: {
    name: '남중국해 봉쇄/물류 차단',
    shock_nodes: {},
    shock_flows: {
      // 대만/일본/한국 → 다운스트림 모든 흐름에 0.6 cut
      'tsmc→nvidia': 0.6, 'skhynix→tsmc': 0.6, 'samsung_m→tsmc': 0.6,
      'disco→skhynix': 0.6, 'ajinomoto→ibiden': 0.6,
      'shinetsu_si→tsmc': 0.6, 'sumco→tsmc': 0.6,
      'aixtron→iqe': 0.6, 'aixtron→coherent': 0.6, 'aixtron→lumentum': 0.6
    },
    duration_weeks: 24,
    probability_5y: 0.18,
    correlation_trigger: { S1_taiwan_strait: 0.5 }
  }
};
```

### Layer 2: Propagation (시간축 BFS)

각 노드는 `inventory_weeks`(재고 버퍼)를 가진다. 흐름이 끊기면 즉시 다운이 아니라 버퍼 소진 후 다운.

```
buffer = {
  tsmc: 6, asml: 12, ajinomoto: 24, ibiden: 8,
  coherent: 8, lumentum: 8, iqe: 4, axt: 4, sum_elec_inp: 4,
  nvidia: 2, foxconn: 1,
  // 명시 안 된 노드: 4주 디폴트 (보수적 추정)
}

for t in [0..52]:
  for n in topo_order:
    cut_score = aggregate(incoming(n))  // 가중평균
    if cut_score > 0.5:
      n.buffer[t] = n.buffer[t-1] - 1
      if n.buffer[t] <= 0:
        n.status[t] = 'DOWN'
        for f in outgoing(n):
          f.cut = max(f.cut, cut_score * (1 - n.substitution))
    elif cut_score > 0.2:
      n.status[t] = 'IMPAIRED'
    else:
      n.status[t] = 'NORMAL'
      n.buffer[t] = min(n.buffer_max, n.buffer[t-1] + 0.5)  // 회복
```

### Layer 3: Substitution Score (0~1, 1=대체 불가)

```
substitution(n) = 0.4 * (mkt_shr/100)
                + 0.3 * (grade_to_score[grade])  // Critical=1, High=0.7, Medium=0.4
                + 0.2 * keyword_score(note)       // "유일"/"독점"/"100%" → 1
                + 0.1 * tier_score(tier)          // tier 0-2 (원자재/장비): 높음
```

수동 오버라이드 가능 (`SUBSTITUTION_OVERRIDE` 객체):
```
SUBSTITUTION_OVERRIDE = {
  asml: 1.0,        // EUV 유일
  carl_zeiss: 1.0,  // EUV 광학계 유일
  trumpf: 1.0,      // CO2 레이저 유일
  ajinomoto: 0.85,  // ABF필름 95%이지만 자체 재고 24주
  cn_in: 0.7,       // 페루·캐나다 30% 우회 가능
  cn_phos: 0.85,    // 중국 80%, 대체 어려움
  aixtron: 0.75,    // Veeco 25% 대체 가능
  ...
}
```

### Layer 4: Financial Impact

```
nvidia_revenue_impact(t) =
  if nvidia.status[t] == 'DOWN': -100%
  elif tsmc.status[t] == 'DOWN': -100%
  elif tsmc.status[t] == 'IMPAIRED': -50%
  elif (cpo_chain_down): -15%  // CPO만 영향, 기존 NVLink fallback
  elif (hbm.status == 'IMPAIRED'): -30%
  else: 0%

affected_marketcap(t) =
  sum(node.usd_b for node in DOWN/IMPAIRED nodes)

upstream_supplier_damage(t) =
  sum(node.usd_b * node.nv_exp/100 for node in IMPAIRED)
```

---

## 4. Monte Carlo (WebWorker)

### 구조
- `risk_worker.js` 별도 파일 (Web Worker)
- 1000회 시뮬레이션, 각 회마다:
  1. 시나리오별 발생 여부 추첨 (확률 + 상관)
  2. 활성 시나리오로 Layer 1-4 전파
  3. NVIDIA 매출 영향 기록
- 결과: 분포(히스토그램), P5/P50/P95, 평균
- 메인 스레드는 `postMessage`로 진행률만 받음 (0~100%)

### 상관관계 적용 (Layer 1 확장)
```
6×6 correlation matrix:
       S1   S2   S3   S4   S5   S6
S1   [ 1   0   0  0  0.7  0.5]
S2   [ 0   1  0.6 0  0    0  ]
S3   [ 0  0.6  1  0  0    0  ]
S4   [ 0   0   0  1  0    0  ]
S5   [0.7  0   0  0  1    0.3]
S6   [0.5  0   0  0  0.3  1  ]

샘플링 알고리즘: Gaussian copula
- 6차원 표준정규 z 추출 (Cholesky 분해된 corr matrix)
- u = Φ(z) (각각 0~1로 변환)
- if u[i] < probability_5y[i]: 시나리오 i 활성화
```

---

## 5. CHIPS Act Reshoring Optionality

5단계 슬라이더가 substitution score를 자동 조정:

| 단계 | 적용 시점 | 영향 |
|------|---------|------|
| `current_2026` | 현재 (디폴트) | substitution 그대로 |
| `2028_micron_idaho` | 2028 시나리오 | MU substitution 0.05↓, TSMC AZ substitution 0.10↓ |
| `2030_full_chips` | 2030 시나리오 | 추가 0.10↓ (Micron NY, Samsung Austin 가동) |
| `accelerated` | 2027.5 가속 시 | TSMC AZ N2 양산 → 대만 의존도 -20% |
| `delayed` | TSMC AZ 지연 | 모든 reshoring 효과 -50% |

```
effective_substitution(node, reshoring_stage) =
  base_substitution(node) * RESHORING_FACTOR[node][reshoring_stage]
```

---

## 6. Critical Path Centrality 랭킹

각 노드를 단독 충격 origin으로 두고 W26 시점 NVIDIA 영향을 계산 → 노드별 점수 매긴 후 패널 하단에 Top 10 표시:

```
centrality(n) = ∫ (nvidia_impact_at_t × decay(t)) dt for t in [0..52]
              when n is the only shock node

Top 10 예상:
1. asml             (EUV 단일공급, mkt_shr 100%, sub 1.0)
2. tsmc             (TSMC 단일 첨단공정)
3. carl_zeiss       (EUV 광학계 100%)
4. trumpf           (CO2 레이저 100%)
5. ajinomoto        (ABF필름 95%, 일본 단일생산)
6. cymer            (ArF 레이저 100%)
7. hamamatsu        (PMT 80-90%, SD 레이저)
8. tsmc_coupe       (CPO NVLink 스위치 100%)
9. aixtron          (MOCVD 90%)
10. iqe             (InP 에피 40~60%)
```

---

## 7. UI 컴포넌트 명세

### 우측 패널 새 탭 "지정학"
```
┌────────────────────────────────┐
│ 🌐 지정학 리스크 시뮬레이터       │
│ ┌──────────────────────────┐  │
│ │ 시간 [W0 ━●━━━━━ W52]    │  │
│ │ Reshoring [현재▼]         │  │
│ │ [□] 확률가중 Monte Carlo  │  │
│ └──────────────────────────┘  │
│                                │
│ ◇ 활성 시나리오                 │
│  ☐ S1 대만해협 (p=20%)         │
│  ☐ S2 中 인듐금지 (p=35%)      │
│  ☐ S3 中 적린통제 (p=30%)      │
│  ☐ S4 AIXTRON 충격 (p=15%)    │
│  ☐ S5 일본 수출통제 (p=25%)    │
│  ☐ S6 SCS 봉쇄 (p=18%)        │
│  [+ 상관 자동 적용]             │
│                                │
│ ━━ Impact @ W12 ━━            │
│ Direct hits:     3 ($85B)     │
│ Cascaded down:  12 ($340B)    │
│ Impaired:        8 ($210B)    │
│ NVIDIA Rubin:   -45%          │
│ TSMC output:    -100%         │
│ CPO chain:      -85%          │
│ Expected loss:  $XB           │
│                                │
│ ━━ Critical Path ━━           │
│ cn_in → axt → iqe →           │
│ coherent → nvidia              │
│                                │
│ ━━ Monte Carlo ━━             │
│ NVIDIA Revenue Distribution    │
│ [P5: -82%] [P50: -25%]        │
│ [P95: +0%] [Mean: -28%]       │
│ [히스토그램 막대]               │
│                                │
│ ━━ Centrality Top 10 ━━       │
│ 1. ASML        score 92       │
│ 2. TSMC        score 88       │
│ ...                            │
└────────────────────────────────┘
```

### 메인 차트 변화 (Render 확장)

시뮬레이터 활성 시 (`riskSim.active == true`):
- **노드 상태별 표시**:
  - `DOWN`: 빨간 X자 오버레이 (SVG path 두 선) + 노드 fill 빨강 30%
  - `IMPAIRED`: 주황 점선 테두리 (`stroke-dasharray:4 2`) + fill 주황 15%
  - `AT_RISK`: 노란 점 표시 (input 끊겼으나 버퍼 살아있음)
  - `NORMAL`: 기존 렌더
- **흐름 상태별 표시**:
  - `cut=1.0`: 빨간 점선 + 중앙에 X 마커
  - `cut=0.3~0.8`: 주황 가는선
  - `cut=0`: 기존 회색
- **하단 status bar**: 현재 시점·활성 시나리오·집계 텍스트 한 줄

### 컨트롤 바 (상단)
기존 `country-bar`/`extra-bar` 아래에 신규 `risk-bar` 추가:
```
🌐 시뮬: [OFF/ON] | W [●━━━━] 12 | Reshoring [현재▼] | 시나리오: 2개 활성 | Impact: -45%
```

---

## 8. 데이터 파일 구조

### 신규 파일: `risk_data.json`
```json
{
  "scenarios": { ... Layer 1 정의 ... },
  "inventory_buffer": { "tsmc": 6, "asml": 12, ... },
  "substitution_override": { ... },
  "reshoring_factor": { ... },
  "correlation_matrix": [[1,0,0,0,0.7,0.5], ...],
  "version": "1.0",
  "generated_at": "2026-05-24"
}
```

### 신규 파일: `gen_risk_data.py`
- `scm_nodes.json` + 인수인계서·INVEST_DEEPDIVE·GEO_RESHORE_ANALYSIS 정량 수치 → `risk_data.json` 생성
- 138노드 전체에 substitution score 자동 계산 + 수동 오버라이드 머지
- 명시 안 된 노드의 inventory_buffer 4주 디폴트
- 검증: 모든 노드에 빠짐없이 파라미터 채워졌는지 assert

### 신규 파일: `risk_worker.js`
- WebWorker로 동작하는 Monte Carlo 엔진
- 입력: `{scenarios, params, n_runs}`
- 출력: 진행률(`{progress: 0~100}`) + 최종 분포(`{p5, p50, p95, mean, histogram}`)

### 신규 파일: `risk_sim.js`
- 메인 스레드 시뮬레이션 엔진 (Layer 1-4 단일 실행)
- 입력: 활성 시나리오 셋 + 시간 t + reshoring 단계
- 출력: 노드별 상태 맵 + 흐름별 cut score 맵 + 집계
- `index.html`의 `render()`가 이걸 호출

### `index.html` 변경
- `<script src="risk_sim.js">`, `<script>let riskWorker = new Worker('risk_worker.js')</script>`, fetch `risk_data.json`
- 시뮬레이터 UI 마크업 추가 (우측 패널 탭)
- `render()` 확장: `riskSim.active` 분기로 상태별 노드/흐름 표시
- 컨트롤 바 마크업 추가

---

## 9. 구현 단위 (10개 task)

| # | Task | 산출물 |
|---|------|--------|
| 1 | 데이터 모델 정의 & 추출 | `gen_risk_data.py`, `risk_data.json` |
| 2 | 시뮬레이션 엔진 코어 (Layer 1-2-3-4) | `risk_sim.js` |
| 3 | UI 마크업 추가 (탭, 컨트롤, 패널) | `index.html` |
| 4 | `render()` 확장: 노드/흐름 상태 시각화 | `index.html` |
| 5 | 시간 슬라이더 + 시나리오 토글 wiring | `index.html` |
| 6 | Reshoring slider + 효과 적용 | `index.html`, `risk_sim.js` |
| 7 | Monte Carlo WebWorker | `risk_worker.js`, `index.html` |
| 8 | Cross-correlation (Gaussian copula) | `risk_worker.js` |
| 9 | Critical Path Centrality Top 10 | `risk_sim.js`, `index.html` |
| 10 | Polish & 검증 (브라우저 테스트) | 전체 |

---

## 10. 테스트 전략

### 정합성 테스트 (수동)
1. **시나리오 S1 단독 활성 → W12** 시점에 TSMC = DOWN, NVIDIA = DOWN 확인
2. **S2 단독 → W12** 시점에 AXT = IMPAIRED 또는 DOWN, IQE = IMPAIRED, NVIDIA = -15% 미만 확인 (CPO만 영향)
3. **S4 단독 → W26** AIXTRON DOWN, IQE·Coherent·Lumentum IMPAIRED 확인
4. **S1+S5 동시 (상관 적용)** Monte Carlo 시 S1만일 때보다 NVIDIA 영향 분포가 더 왼쪽으로 이동 확인
5. **Reshoring=accelerated** S1 활성 시 NVIDIA 영향이 `current_2026` 대비 -20% 정도 완화 확인

### 시각 회귀 (수동)
- 시뮬레이터 OFF 상태에서 기존 `index.html`과 픽셀-동일하게 보이는지
- 시나리오 ON 시 노드 X자가 SVG에 그려지는지
- 시간 슬라이더 이동 시 60fps 렌더되는지 (138노드는 충분히 가능)

### 단위 (Node.js 빠른 검증)
- `risk_sim.js`를 Node에서 require해서 단일 시나리오 propagation 결과를 hardcoded expected와 비교

---

## 11. 명시적 가정과 한계

### 가정
- 인벤토리 버퍼는 일부 노드만 근거 있고 나머지는 4주 디폴트 추정값이다.
- substitution score는 mkt_shr·grade에서 계산한 휴리스틱이며 수동 오버라이드로 보정한다.
- 상관계수 매트릭스는 GEO_RESHORE_ANALYSIS의 시나리오 의존성 서술에서 도출한 정성적 값이다.
- NVIDIA 매출 영향은 단순화된 if-elif 룰베이스이며, 실제 매출 mix(데이터센터 80%, 게이밍 16%, ...)는 무시한다.

### 한계
- 가격 영향(commodity price)은 모델링하지 않는다. 인듐 가격 15-20% 상승은 충격이 아니라 마진 압축이므로 별도 차원이다.
- 수요측 충격(하이퍼스케일러 capex 삭감)은 다루지 않는다. 공급측만이다.
- 재가동 시간(recovery dynamics)은 시나리오별 duration_weeks 하나로 단순화한다. 실제는 점진적 회복이다.
- 모든 가정값은 UI에서 노출되고 출처가 라벨링된다. 사용자가 "이 가정 의심스러운데"라고 했을 때 클릭 한 번에 출처 표시.

---

## 12. 완료 정의 (Definition of Done)

1. `index.html`을 브라우저에서 열고 "지정학" 탭으로 전환 가능
2. 6개 시나리오 각각 단독 토글 시, 노드 상태가 시각적으로 변하고 우측 패널에 영향 수치 표시
3. 시간 슬라이더 W0~W52 이동 시 노드 상태가 실시간 갱신
4. Reshoring 슬라이더 5단계가 시나리오 결과를 변화시킴
5. Monte Carlo "확률가중" 토글 시 WebWorker가 1000회 돌고 P5/P50/P95 표시
6. 상관 자동 적용 ON 시 단일 시나리오라도 연관 시나리오가 확률적으로 동반
7. Critical Path Centrality Top 10이 의미 있는 순서로 표시 (asml/tsmc/carl_zeiss 상위)
8. 시뮬레이터 OFF 상태에서 기존 차트가 깨지지 않음
9. 모든 추정치 파라미터에 출처/근거 tooltip 또는 라벨이 있음

---

## 13. Out of Scope (Phase 3 후속)
- 가격 시뮬레이션(인듐·헬륨 등 commodity)
- 수요측 충격 모델
- 시계열 매크로 변수(금리, 환율, GDP)
- 대안 시나리오 자동 생성(LLM 기반)
- PDF/Excel 리포트 익스포트
- 사용자 정의 시나리오 작성 UI
- 다국어 (한국어 외)
