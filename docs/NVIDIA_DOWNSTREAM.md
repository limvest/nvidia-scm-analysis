# NVIDIA에서 고객까지 · 출하와 실제 가동

**조사 기준일 2026년 11월 28일** · 데이터센터용 AI 가속기를 대상으로 한다. 4월 공급망 조사에 이어 NVIDIA가 출하한 장비를 누가 운영하고 누가 연산을 사용하는지 추적했다. [고객별 원문과 계산이 담긴 엑셀](NVIDIA-downstream-2026-11.xlsx)

## NVIDIA는 얼마나 출하했고, 어디로 팔았나

NVIDIA가 2025년 10월 GTC에서 밝힌 누적 출하 이정표는 Blackwell **600만**이다. 약 1시간 2분 지점에서 출하량을 설명한 뒤 패키지당 GPU 다이 2개와 지역 범위를 언급한다. 이를 600만 장의 설치 카드로 환산하면 고객 장비와 맞지 않을 수 있다. 최근인 2026년 11월 실적 발표에서는 Rubin NVL72의 양산 출하와 실명 운영사를 공개했지만 모델별 출하 대수표는 제공하지 않았다. [NVIDIA GTC 원본](https://www.nvidia.com/en-us/on-demand/session/gtcdc25-dc1204/) · [NVIDIA 분기 발표](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027)

같은 기준의 출하 추이는 Epoch AI의 11월 24일 자료로 계산했다. 아래는 NVIDIA 추적 AI 칩의 모델별 추정 중앙값을 합친 수치다. Epoch는 매출·가격·회사 발표로 고객 인도량을 추정한다. 2026년 4분기는 일부 기간만 수록돼 제외했다. [방법론과 원자료](https://epoch.ai/data/ai-chip-sales)

| 달력 기간 | NVIDIA 칩 인도 추정 | 집계 범위 |
| --- | ---: | --- |
| 2025년 | 4,484,387개 | 4개 분기 합 |
| 2026년 1분기 | 1,340,673개 | 1~3월 |
| 2026년 2분기 | 1,577,133개 | 4~6월 |
| 2026년 3분기 | 1,780,415개 | 7~9월. B300 약 142.5만 개 포함 |
| **2026년 1~9월** | **4,698,221개** | 전년 연간 인도 추정치를 이미 웃돎 |

**2022년 1분기부터 2026년 3분기까지** 같은 데이터의 NVIDIA 인도 누계는 **약 1,514.3만 개**다. 현재 세계 가동 재고를 구하려면 여기에 2022년 이전 설치분과 이후 신규 인도분을 더하고, 퇴역·반품·인수 후 서비스 대기분을 빼야 한다. 각 항목의 같은 날짜 세계 합계는 확인되지 않았다. 장비가 서비스에 올라와 있어도 실제 연산한 시간은 그다음 단계다. [Epoch AI 집계 범위](https://epoch.ai/data/ai-chip-sales)

NVIDIA FY2027 3분기는 **10월 25일 마감**이다. 데이터센터 매출 1,076억 달러 중 하이퍼스케일이 601억 달러(55.9%), AI 클라우드·산업·기업을 합친 부문이 475억 달러(44.1%)였다. 후자에는 기업 고객도 포함된다. 전체 매출의 14%, 11%, 11%를 차지한 직접 고객 세 곳의 이름은 공시하지 않았다. 중간에 서버 제조사나 유통사가 끼므로 클라우드 발표만으로 세 고객의 신원을 확정할 수 없다. [NVIDIA CFO 해설](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000088/q3fy27cfocommentary.htm) · [고객 집중도 공시](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000088/supplementalfinancialinfor.htm)

## 운영사와 실제 이용자

NVIDIA가 11월에 Rubin 랙 가동을 직접 확인한 운영사는 **CoreWeave, Google Cloud, Microsoft Azure, Oracle Cloud Infrastructure, Nebius**다. 랙 수는 미공개다. 같은 발표에서 SpaceXSI의 Rubin 가동은 향후 일정으로 기재했다. 한 회사가 직접 구매자, 인프라 운영자, 다른 클라우드의 임차인 역할을 동시에 할 수 있다. [NVIDIA 발표](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027)

| 공개된 경로 | 확인 수량 | 어떤 증거인가 |
| --- | ---: | --- |
| NVIDIA → OCI 미국 Abilene → OpenAI | Blackwell **10만 개 초과** | 해당 클러스터에서 GPT-6 Astra를 학습하고 서비스했다. [NVIDIA·Oracle 공동 발표](https://nvidianews.nvidia.com/news/nvidia-and-oracle-expand-nvidia-vera-rubin-to-multi-gigawatt-scale-and-bring-nvidia-vera-cpu-to-oracle-cloud-infrastructure) |
| NVIDIA → SpaceX/xAI Colossus 1 → Anthropic | **22만 개 초과** | H100·H200·GB200이 설치됐다. Anthropic은 전체 용량에 접근하는 계약을 발표했다. 실사용 시간은 미공개다. [운영사](https://x.ai/news/anthropic-compute-partnership) · [고객](https://www.anthropic.com/news/higher-limits-spacex) |
| NVIDIA → T-Systems 뮌헨 → 기업·공공 고객 | Blackwell **1만 개** | 2월부터 운영. 11월에는 최초 용량 예약이 모두 찼다고 밝혔다. 예약률과 하드웨어 사용률은 서로 다른 지표다. [운영 규모](https://www.telekom.com/en/newsroom/latest-updates/media-information/2026/06/t-systems-and-supplyon-bring-ai-to-europes-supply-chains) · [예약 현황](https://www.telekom.com/en/newsroom/latest-updates/media-information/2026/11/ai-demand-rises-deutsche-telekom-expands-ai-factory-in-munich) |
| NVIDIA → Jülich JUPITER Booster → 과학 연구 | GH200 **23,536개** | 5,884노드 × 4개. 11월 TOP500 5위로 연산 확인. [운영사 사양](https://www.fz-juelich.de/en/jsc/jupiter/tech/) · [TOP500](https://top500.org/lists/top500/list/2026/11/) |

네 시설의 공표 규모 합은 **353,536개 초과**다. 관측 시점이 다르고 칩 세대도 섞여 있다. 이 수치를 1~9월 출하량으로 나누면 분자에는 과거 설치 장비가 들어가고 분모에서는 공개되지 않은 과거 출하가 빠진다. 따라서 이 비율로 세계 가동률이나 남은 재고를 계산할 수 없다. 한국의 KISTI 한강에는 GPU 8,496개가 설치돼 11월 TOP500 12위를 기록했고, 정부가 발표한 공식 서비스 예정일은 12월 14일이었다. 설치와 서비스 사이의 차이를 보여 주므로 위 합계와 별도로 기록했다. [과기정통부](https://www.korea.kr/news/policyNewsView.do?newsId=148974819)

## 네오클라우드로 얼마나 갔고, 얼마나 대기 중인가

| 사업자 | 확인한 흐름 | 집계할 때의 의미 |
| --- | --- | --- |
| CoreWeave | 회사 소개 자료에 GPU **25만 개 이상**. 3분기 자료에는 가동 데이터센터 52곳, 가동 전력 **1.7GW 이상**, 계약 전력 **4.6GW 이상**. OpenAI와 2025년 9월까지 발표한 계약은 최대 224억 달러 | 보유 GPU는 여러 해 동안 쌓인 수량이다. 계약 전력에는 미래 증설이 포함돼 전력 차이를 구매 후 유휴 GPU로 환산할 수 없다. [보유 용량](https://www.coreweave.com/why-coreweave) · [분기 자료](https://investors.coreweave.com/files/content_files/CoreWeave-3Q-2026-Infographic.pdf) · [OpenAI 계약](https://investors.coreweave.com/news/news-details/2025/CoreWeave-Expands-Agreement-with-OpenAI-by-up-to-6-5B/default.aspx) |
| IREN → Microsoft | GB300 기반 Horizon 1의 50MW IT 용량을 8월에 인도. 별도로 B300 **5만 개 초과 구매계약** 발표 | 전체 구매계약과 인도를 개별 추적해야 한다. 11월에는 설계 변경·공급 일정으로 계약 ARR 목표 달성 시점을 연말에서 2027년 1월로 늦췄고 2월까지 가능하다고 밝혔다. [인도](https://www.iren.com/resources/news/nvidia-exemplar-cloud-nvidia-gb300-nvl72-status) · [구매계약](https://iren.com/resources/news/iren-expands-ai-cloud-capacity-to-150000-gpus) · [11월 공시](https://www.sec.gov/Archives/edgar/data/1878848/000187884826000065/irenreportsq1-fy27result.htm) |
| Nebius → Microsoft | 3분기와 11월까지 뉴저지에서 단계별 추가 인도. 잔여분은 2027년 2분기 일정 | 인도 단계는 확인되며 단계별 GPU 개수는 미공개다. [주주 서한](https://assets.nebius.com/assets/5bc733ff-bed7-415c-af10-74ce7881a764/Nebius-SHL-2026-Q3.pdf) |
| Axe Compute → 미국 조지아 | **B300 2,304개**를 보유한 사업체를 9월 30일 인수. 분기말 전량 서비스 투입 전 | 구매 완료와 미가동을 같은 날짜에 확인한 사례다. 11월 공시의 서비스 목표는 4분기였다. [Axe Compute SEC 공시](https://www.sec.gov/Archives/edgar/data/1446159/000117184326007509/exh_991.htm) |
| Giga Computing → Datasection → 일본 익명 고객 | 1월 6일 기준 발주 625서버 중 **48서버(B200 384개)** 인도. 해당 서비스 개시는 연기 | 나머지 577서버는 당시 납품 대기였다. 계약 서비스 개시 전이라도 개별 장비의 테스트·다른 사용까지 배제할 수 없다. [공급·개통 일정 공시](https://www.datasection.co.jp/en-financial-report/en-ir-20260106005.pdf) |

세계의 **구매 후 미가동 잔량**을 산출하려면 같은 기준일에 각 구매자가 인수한 장비에서 서비스 투입분과 반품·재양도분을 대조해야 한다. 고객사 합병으로 인수한 재고, 배송 대기 주문, 설치 후 검수, 정상 서비스 중 임차인이 쓰지 않은 시간은 서로 다른 상태다. 1월 일본과 9월 조지아의 숫자는 11월 잔량으로 합산하지 않았다.

## 중국향 선적과 중국 고객의 해외 임차

| 질문 | 공개 자료로 확인한 수치 |
| --- | --- |
| 중국에 실제 얼마나 출하했나 | FY27 3분기 **중국향 데이터센터 Hopper 제품 24억 달러**. 직전 분기에는 세계 데이터센터 매출의 1% 미만이었다. 이번 분기 중국·홍콩 본사 직접 고객의 **전 제품 매출 110.5억 달러**는 설치 국가 기준이 아니다. 제품 구성과 거래 단가는 미공개다. [3분기 CFO 해설](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000088/q3fy27cfocommentary.htm) · [2분기 10-Q](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm) · [지역 매출](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000088/supplementalfinancialinfor.htm) |
| 허가와 실제 인도의 차이는 어느 정도인가 | 11월 19일 공개된 **5월 11일 기준** BIS 표에서 수출자 NVIDIA, 최종 위치 중국, 승인·미출하인 17건의 합은 **579,868개**다. Alibaba·ByteDance·Tencent는 각각 75,000개다. AMD까지 포함한 전체 승인 879,868개에 이 NVIDIA 물량이 들어 있다. 10월 실적과 개별 허가를 연결할 수 없다. [허가 원표](https://democrats-foreignaffairs.house.gov/wp-content/uploads/2026/11/11.19.26-ECRA-Information-Disclosure-of-BIS-License-Decisions.pdf) · [미 하원 요약](https://democrats-foreignaffairs.house.gov/wp-content/uploads/2026/11/11.19.26-ECRA-Information-Disclosure-HFAC-Summary.pdf) |
| 간접 유입도 잡히나 | 미 법무부는 2025년 4월 말~5월 중순 **약 5.1억 달러 이상**의 서버가 중국에 전용됐다고 기소했다. 특정 사건의 서버 가액이며 해당 장비의 GPU 개수와 최종 가동 여부는 확인되지 않는다. [미 법무부 기소 발표](https://www.justice.gov/opa/pr/three-charged-conspiring-unlawfully-divert-cutting-edge-us-artificial-intelligence) |
| 해외 클라우드를 중국 고객이 얼마나 썼나 | 인도네시아에서 중국 INF Tech가 접근할 수 있었던 Blackwell **약 2,300개**가 현지 취재로 보도됐다. 일본 Datasection의 약 15,000개 규모 B200 설비에는 Tencent가 주요 고객으로 보도됐다. 후자의 전량을 Tencent에 배정할 근거는 없다. 어느 사례도 고객별 청구·실행 GPU·시간이나 11월 말 잔존 계약을 공개하지 않았다. [WSJ 원보도](https://www.wsj.com/tech/ai/china-ai-nvidia-chip-access-6a4fa63d) · [Carnegie 조사](https://carnegieendowment.org/research/2026/05/the-geopolitical-debates-over-controlling-cloud-compute) · [Datasection 구매 공시](https://www.datasection.co.jp/en-financial-report/en-ir-20250704002.pdf) |

실제 소진량의 단위는 **GPU·시간**이다. DeepSeek가 V3 최종 학습에 보고한 **278.8만 H800 GPU·시간**처럼 워크로드 자체가 공개되는 경우도 있다. 이 수치의 조달 경로가 해외 네오클라우드 임차였다는 근거는 없다. 중국으로 들어간 장비, 해외에 남은 장비, 중국 기업의 연산은 따로 추적해야 한다. [DeepSeek 기술보고서](https://arxiv.org/abs/2412.19437)

## TPU·Maia 대체와 기술 발전에 따른 GPU 절감

2026년 **같은 상반기** Epoch 모델은 NVIDIA AI 칩 291.8만 개, Google TPU 117.4만 개, Amazon Trainium 69.5만 개로 추정한다. NVIDIA는 매출 기반 인도량, Google은 Broadcom 매출 기반 생산·인도, Amazon은 설비 추적에 더 가까운 수치다. 칩마다 처리 가능한 작업·속도·메모리가 다르고 자체칩으로 새로 가능해진 작업도 있어, TPU 한 개를 NVIDIA 주문 한 개 감소로 처리할 수 없다. [Epoch AI 방법론](https://epoch.ai/data/ai-chip-sales)

- **Google TPU.** Anthropic은 Claude를 Google TPU, Amazon Trainium, NVIDIA GPU에서 학습·운영한다고 밝혔다. 최대 100만 TPU 접근 계획과 2027년부터의 추가 수 GW 계약도 공개했다. 실사용은 확인되며, TPU에 옮긴 작업이 원래 어떤 NVIDIA 주문으로 이어졌을지는 공개 자료로 식별되지 않는다. [2025년 용량 계획](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services) · [2026년 실제 사용 및 추가 계약](https://www.anthropic.com/news/google-broadcom-partnership-compute)
- **Microsoft Maia 200.** Teams·Copilot·Cowork 일부 기능을 상용 처리하며 Microsoft는 기존 선도 GPU 인프라 대비 와트당 토큰이 최대 1.7배라고 밝혔다. 전력당 성능 비교로부터 이전된 토큰 비율이나 취소된 GPU 주문 수를 구할 수 없다. [Microsoft 상용화 발표](https://blogs.microsoft.com/blog/2026/10/12/microsoft-to-expand-azure-maia-system-to-multi-gigawatt-deployments/)
- **하드웨어 세대 개선.** MLPerf의 DeepSeek-V3 671B 학습 벤치마크에서 GPU 1,024개로 GB300은 8.03분, Rubin은 4.14분이었다. 해당 벤치마크 구간의 GPU·시간은 약 **137.0 → 70.7**, **48.4% 감소**했다. 전체 모델 사전학습 시간이 아니다. [측정 결과](https://developer.nvidia.com/blog/nvidia-vera-rubin-nvl72-achieves-up-to-2x-blackwell-ultra-performance-in-mlperf-training-v6-1/) · [MLCommons](https://mlcommons.org/2026/11/mlperf-training-v6-1-results/)
- **소프트웨어 개선.** 동일 GB300 하드웨어에서 DeepSeek-R1 추론의 서버 시나리오 처리량은 6개월 사이 최대 **2.7배**로 높아졌다. 같은 토큰을 같은 서비스 조건으로 처리하면 필요한 GPU·시간은 최대 **63.0% 감소**한다. 이 값과 위 학습 절감률은 서로 다른 실험이어서 곱하지 않는다. [NVIDIA 추론 측정](https://developer.nvidia.com/blog/nvidia-platform-delivers-lowest-token-cost-enabled-by-extreme-co-design/)

시장 전체의 GPU·시간은 **작업량 배수 ÷ GPU당 처리량 배수**로 움직인다. 예를 들어 성능이 두 배가 되면 작업량 1.5배에서는 GPU·시간이 25% 줄고, 작업량 3배에서는 50% 늘어난다. 둘 다 시나리오다. 실제 순대체량 산출에는 고객별 이전 토큰 수, 서비스 품질·모델 조건에서의 비교 처리량, 기존 구매·증설 계획이 필요하다.

### 엑셀 수록 범위

공시·계약별 근거와 계산식에 더해 칩별 출하 추정 176행, 주 공급사가 NVIDIA로 표시된 과거 클러스터 249행, 대형 센터의 칩 수 기록 248행, 2026년 11월 TOP500 시스템 500행을 수록했다. 클러스터 이력에는 후속 단계와 중복 가능성이 있고 최초 가동일 최신값은 2025년 7월이다. 센터 이력에는 추정값과 미래 일정이 있다. TOP500은 제출된 HPL 성능 순위로, 세계 클라우드 전수조사와 모집단이 다르다. 원자료를 연결하거나 필터링할 때 이력 전후를 합산하지 않아야 한다. Epoch AI 데이터는 저자 표시 조건으로 재사용했으며 열 선택·번역·합계를 추가했다. [Epoch AI 출하](https://epoch.ai/data/ai-chip-sales) · [클러스터](https://epoch.ai/data/gpu-clusters-documentation/downloads) · [대형 센터](https://epoch.ai/data/data-centers-documentation/downloads) · [TOP500](https://top500.org/lists/top500/list/2026/11/)
