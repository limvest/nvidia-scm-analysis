# NVIDIA Rubin / Feynman 공급망 리스크 분석

NVIDIA 차세대 AI 가속기(Vera Rubin, Feynman)의 공급망을 187개 노드와 922개 공급 관계로 정리하고, 특정 지역이나 기업이 멈췄을 때 충격이 어디까지 번지는지 계산하는 시뮬레이터를 만든 분석 프로젝트입니다.

**[라이브 데모](https://nvidia-scm-analysis.vercel.app)** · [투자 리서치 페이지](https://nvidia-scm-analysis.vercel.app/research.html) · [리서치 문서](docs/)

[2026년 11월 후속 조사 · NVIDIA 출하에서 고객과 실제 가동까지](docs/NVIDIA_DOWNSTREAM.md)

![공급망 지도와 리스크 시뮬레이터](docs/img/supply-chain-map.png)

## 한눈에 보기

| 항목 | 내용 |
| --- | --- |
| 기간 | 2026년 4월 기초 조사 · 5~6월 프로젝트 · 11월 자료 수정 및 고객·가동 현황 후속 조사 |
| 주제 | 반도체 공급망 구조와 지정학 리스크 |
| 한 일 | 공개 자료 조사, 공급망 데이터 모델링, 리스크 시뮬레이터 구현, 리서치 문서 작성 |
| 도구 | Python(데이터 생성·빌드), JavaScript(시뮬레이터·시각화), Web Worker |
| 규모 | 웹 지도 노드 187개, 공급 흐름 922개, 충격 시나리오 6개, 상장사 84곳 스크리닝 |

## 어떤 질문에서 시작했나

AI 가속기 한 대가 나오려면 소재, 장비, 파운드리, 메모리, 패키징, 광부품 회사가 순서대로 맞물려야 합니다. 뉴스는 "대만 리스크"처럼 한 단어로 말하지만, 실제로 어느 회사가 멈추면 어디까지 영향이 가는지는 공급 관계를 따라가 봐야 알 수 있습니다. 그래서 다음 세 가지를 직접 확인해 보려고 했습니다.

1. 공급망의 어느 지점이 대체하기 어려운 단일 실패 지점인가
2. 대만해협 분쟁이나 수출 통제 같은 사건이 나면 NVIDIA 출하에 얼마나, 얼마나 빨리 영향이 가는가
3. 미국의 보조금·관세·수출통제가 공급망 기업들의 위치를 어떻게 바꾸는가

## 한 일

### 1. 공급망 지도

소재 → 장비 → 웨이퍼·파운드리 → 메모리(HBM) → 패키징(CoWoS) → 광인터커넥트(CPO) → 시스템 순서로, 기업을 노드로 공급 관계를 흐름으로 정리했습니다. 노드마다 국가, 시장 점유율, 대체 공급처 전환에 걸리는 기간, 초크포인트 등급을 붙였습니다. 일부 지표에는 추정치와 결측값이 포함됩니다. 현재 세대(Rubin, 2026)와 다음 세대(Feynman, 2028~)를 나눠 볼 수 있습니다.

### 2. 리스크 전파 시뮬레이터

노드 하나나 지역 전체를 차단하면 공급 관계를 따라 하류 노드의 공급 손실을 계산합니다.

- 상류에서 하류 순서로 손실을 전파합니다. 서로 순환하는 노드 사이에서는 전주의 공급 상태를 사용합니다.
- 대체 공급처 비중과 재고를 반영합니다. 각 시나리오의 지정 기간이 지나면 직접 충격이 종료됩니다.
- 몬테카를로로 여러 번 돌려 결과 분포를 히스토그램으로 보여 줍니다. 5년 이내 발생확률을 가정해 시나리오를 뽑고, 뽑힌 사건들이 같은 주에 시작한다고 가정해 선택한 주차의 영향을 비교합니다. 상관 옵션을 켜면 가우시안 코풀라를 사용합니다.
- 몬테카를로 계산은 Web Worker에서 돌려 화면이 멈추지 않습니다. 사용자 브라우저에서 결과를 계산합니다.

### 3. 충격 시나리오 6개

| 시나리오 | 내용 |
| --- | --- |
| 대만해협 분쟁 | TSMC 가동 중단, 첨단 로직 공급 차단 |
| 중국 인듐 수출 금지 | 인듐 공급의 약 70% 차단, InP 기판 체인 마비 |
| 중국 적린 수출 통제 | 적린 공급의 약 80% 차단, InP 합성 중단 |
| AIXTRON 단일공급 충격 | MOCVD 장비 한 곳에 광부품 3사가 동시에 의존 |
| 일본 소재·장비 수출 통제 | ABF, EUV 포토레지스트, 실리콘 웨이퍼 동시 차질 |
| 남중국해 봉쇄 | 대만·일본·한국 부품 운송 차질 |

### 4. 단일 실패 지점 순위

각 공급자를 하나씩 차단해 26주 안에 NVIDIA가 처음 다운되는 주를 계산합니다. 대체 가능성과 하류 노드 수, 마지막 주의 매출 영향 가정값을 함께 사용해 순위를 매깁니다.

### 5. 상장사 스크리닝과 리서치 문서

공급망에 속한 상장사 84곳을 초크포인트 등급(독점 정도), 영업이익률, NVIDIA 매출 의존도, 공급사 전환에 걸리는 기간, 밸류에이션(EV/EBITDA)으로 점수화했습니다. 이어서 미국의 통제력이 미치는 정도(US Control Score)를 기준으로 기업을 다시 분류했습니다.

![상장사 스크리닝](docs/img/research-screening.png)

| 문서 | 내용 |
| --- | --- |
| [docs/INVEST_DEEPDIVE.md](docs/INVEST_DEEPDIVE.md) | 스크리닝 방법, 상위 30곳, 테마별 분류, 4개 종목 상세 |
| [docs/GEO_RESHORE_ANALYSIS.md](docs/GEO_RESHORE_ANALYSIS.md) | 미국 중심 공급망 재편과 기업별 위치 |
| [docs/US_CONTROL_SCM_ANALYSIS.md](docs/US_CONTROL_SCM_ANALYSIS.md) | 보조금·관세·수출통제가 만드는 레버리지 |

## 직접 실행

저장소 루트에서 로컬 정적 서버를 실행한 뒤 [공급망 지도](http://127.0.0.1:8000/)를 엽니다. 시뮬레이터가 같은 주소에서 JSON과 Web Worker를 로드합니다.

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

```bash
node tests/test_risk_sim.js
```

## 파일 구성

| 파일 | 역할 |
| --- | --- |
| `index.html` | 공급망 분석 리포트와 리스크 시뮬레이터 |
| `scm_full.html` | 전체 공급망 지도 |
| `research.html` | 상장사 스크리닝·투자 리서치 페이지 |
| `risk_sim.js`, `risk_worker.js` | 리스크 전파 엔진과 몬테카를로 Web Worker |
| `scm_nodes.json`, `nodes_full.json`, `flows.js`, `layout.json` | 이전 138개 노드·52개 흐름 지도와 차트 작업용 자료 |
| `risk_data.json`, `marketcaps.json` | 시나리오 입력값, 공개 시가총액 |
| `scm_data.py`, `gen_*.py`, `build_data.py`, `patch_html.py` | 데이터 동기화, 리포트 빌드, 이전 차트 생성 도구 |
| `tests/test_risk_sim.js` | 시뮬레이터 단위 테스트 |

웹 지도와 테스트는 `index.html`의 `DATA`를 사용합니다. `gen_risk_data.py`는 기존 시나리오와 개별 추정치를 보존하고 지도에서 이름·시총 등을 동기화합니다. 개별 입력이 없는 노드에는 대체 비중 0.5와 재고 4주를 적용합니다.

`build_data.py`는 원본 리서치 마크다운을 읽어 HTML을 다시 만듭니다. 원본 위치는 `SCM_SOURCE_DIR` 환경변수로 지정하며, 원본 마크다운은 이 저장소에 없습니다.

## 배운 점과 한계

- **구조를 그려야 보이는 것이 있었습니다.** 표면에서는 한 줄인 공급 관계가, 따라가 보면 원료·기판·장비·전구체 가스까지 여러 층으로 깊어집니다. 병목은 유명한 대기업보다 그 아래 층의 작은 회사에 있는 경우가 많았습니다.
- **수치는 2026년 5월 공개 자료 기준입니다.** 기업 공시, 업계 보고서, 언론 보도를 썼고 자료별 기준일과 추정 여부는 리서치 문서에 표시했습니다.
- **시뮬레이션 입력은 가정입니다.** 대체 공급 비중, 재고 버퍼, 지역 간 상관계수는 공개 자료로 추정한 값이라, 결과는 정확한 예측이 아니라 상대적인 크기 비교로 봐야 합니다.
- **투자 리서치 문서는 공급망 분석의 연장선에서 정리한 개인 연구 기록입니다.** 화면에는 2026년 5월 조사 대상 중 상위 30개를 표시합니다.

## 주요 정정의 1차 자료

- SK하이닉스 인디애나 투자 계획은 38.7억 달러이며 CHIPS 직접지원 한도는 4.58억 달러입니다. 삼성전자의 최종 직접지원 한도는 47.45억 달러입니다. [NIST SK하이닉스](https://www.nist.gov/chips/sk-hynix-indiana-west-lafayette) · [미 상무부 삼성전자 발표](https://www.nist.gov/news-events/news/2024/12/biden-harris-administration-announces-chips-incentives-award-samsung)
- 2026년 3월 Ayar Labs의 5억 달러는 Series E 전체 조달액입니다. NVIDIA의 개별 출자액은 발표에 기재되지 않았습니다. Coherent는 NVIDIA에 주당 256.80달러로 7,788,161주를 발행했습니다. [Ayar Labs 발표](https://ayarlabs.com/news/ayar-labs-closes-500m-series-e-accelerates-volume-production-of-co-packaged-optics/) · [Coherent SEC 8-K](https://www.sec.gov/Archives/edgar/data/820318/000119312526084366/d42735d8k.htm)
- FY2026 NVIDIA 연결 매출은 2,159.38억 달러, GAAP 영업이익률은 60.4%입니다. TSMC의 2025년 연결 영업이익률은 50.8%입니다. [NVIDIA 연간 실적](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026/) · [TSMC 연차보고서](https://investor.tsmc.com/static/annualReports/2025/english/index.html)
- 2026년 3월 Vera Rubin 발표에는 Groq 3 LPU를 포함한 칩 7종이 등장합니다. Feynman의 커스텀 HBM과 NVLink 8 CPO는 공식 로드맵에 있으며, GPU 파운드리 공정과 광칩렛 공급사 배정은 이 분석의 가정입니다. [NVIDIA Vera Rubin 발표](https://nvidianews.nvidia.com/news/nvidia-vera-rubin-platform) · [GTC 2026 로드맵](https://images.nvidia.com/nvimages/gtc/pdf/GTC26_SanJose_Highlights_Final.pdf)
