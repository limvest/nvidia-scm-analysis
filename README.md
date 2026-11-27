# NVIDIA Rubin / Feynman 공급망(SCM) 리스크 분석

NVIDIA의 차세대 AI 가속기(Vera Rubin, Feynman) 공급망을 노드-흐름 그래프로 모델링하고, 특정 지역·기업이 멈췄을 때 충격이 어디까지 번지는지 시뮬레이션하는 분석 프로젝트입니다.

## 무엇을 했나

- **공급망 지도**: 소재 → 장비 → 웨이퍼·파운드리 → 메모리(HBM) → 패키징(CoWoS) → 광인터커넥트(CPO) → 시스템까지, 공급망 기업을 노드로, 공급 관계를 흐름(edge)으로 정리했습니다 (`scm_nodes.json`, `flows.js`).
- **리스크 전파 시뮬레이터**: 노드 하나 또는 지역(대만·일본·한국·중국 등)을 차단하면 위상 정렬 순서로 하류 노드의 공급 손실을 계산합니다. 대체 공급처 비중을 반영하고, 몬테카를로로 여러 시나리오를 돌립니다 (`risk_sim.js`, `risk_worker.js`).
- **단일 실패 지점(SPoF) 탐지**: 중심성(centrality)과 대체 불가능성을 함께 보고, 차단 시 영향이 큰 병목 노드를 순위로 뽑습니다.
- **지정학 분석**: 미국의 보조금(CHIPS Act)·관세·수출통제가 공급망 기업별로 어떤 레버리지를 만드는지 정리했습니다 (`docs/US_CONTROL_SCM_ANALYSIS.md`).

## 보는 법

브라우저에서 `index.html` 을 열면 됩니다 (서버 불필요).

- `index.html`: 공급망 분석 리포트 + 인터랙티브 리스크 시뮬레이터
- `scm_full.html`: 전체 공급망 지도
- `research.html`: 공급망 상장사 스크리닝·투자 리서치 페이지
- `docs/INVEST_DEEPDIVE.md`, `docs/GEO_RESHORE_ANALYSIS.md`: 투자 딥다이브, 리쇼어링 분석 문서

## 테스트

```bash
node tests/test_risk_sim.js
```

## 파일 구성

| 파일 | 역할 |
|---|---|
| `risk_sim.js` | 리스크 전파 엔진 (Node·브라우저 공용) |
| `risk_worker.js` | 몬테카를로 시뮬레이션용 Web Worker |
| `scm_nodes.json`, `nodes_full.json`, `flows.js`, `layout.json` | 공급망 노드·흐름·배치 데이터 |
| `risk_data.json`, `marketcaps.json` | 시뮬레이션 입력값, 공개 시가총액 데이터 |
| `scm_data.py`, `gen_*.py`, `build_data.py`, `patch_html.py` | 데이터 생성·HTML 빌드 스크립트 |
| `tests/test_risk_sim.js` | 시뮬레이터 단위 테스트 |

`build_data.py` 는 원본 리서치 마크다운을 읽어 HTML을 다시 만듭니다. 원본 위치는 `SCM_SOURCE_DIR` 환경변수로 지정합니다 (원본 마크다운은 이 저장소에 포함하지 않았습니다).

## 참고

- 수치는 2026년 5월 기준 공개 자료(기업 공시, 업계 보고서, 언론 보도)로 정리했으며, 각 수치 옆에 출처 등급(1차/2차)을 표기했습니다.
- 투자 리서치 문서는 공급망 분석의 연장선에서 정리한 개인 연구 기록이며, 특정 종목의 매수·매도 권유가 아닙니다.
