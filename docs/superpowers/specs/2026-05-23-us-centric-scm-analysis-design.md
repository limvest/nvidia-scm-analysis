# US-Centric Semiconductor SCM 승자 분석 — 설계 문서

**작성일:** 2026-05-23  
**목적:** 트럼프 행정부의 반도체 공급망 주권 전략 하에서 수혜를 받을 기업을 발굴하고, 3-5년/5-10년 레이어로 투자 테마를 정리한다.

---

## 핵심 논지

트럼프의 목표는 동맹 구축이 아니라 **공급망 주권(Supply Chain Sovereignty)**이다. 도구는 세 가지다:
- **CHIPS Act 보조금** (당근): 미국 내 팹 건설 유도
- **관세** (채찍): 해외 생산 패널티, 미국 투자 강제
- **수출통제** (무기화): 중국 접근 차단, 동맹국도 미국 허가 종속

이 구조에서 **승자는 미국 관할권 안에 있거나 미국 정책의 직접 수혜를 받는 기업**이다. 일본·네덜란드·한국 기업은 동맹이 아니라 레버리지 대상이다 — TSMC 아리조나 강제, ASML 수출허가 종속, SK Hynix 인디애나 투자 압박이 그 증거다.

---

## 분석 프레임워크

### US Control Score (1-5)

| 점수 | 기준 | 대표 기업 |
|------|------|----------|
| 5 | 미국 본사 + 미국 제조 중심 | Intel, Micron, Lam, AMAT, KLA, GlobalFoundries |
| 4 | 미국 본사, 제조 해외 — AI 수요 독점적 수혜 | NVIDIA, Qualcomm, Broadcom |
| 3 | 외국 기업 + 미국 팹 건설 중 (CHIPS Act 수령) | TSMC AZ, Samsung Austin, SK Hynix IN |
| 2 | 미국 기술 라이선스 의존 — 레버리지 대상 | ASML, TEL, Lasertec |
| 1 | 미국 컨트롤 외부 — 관세·제재 리스크 | 중국 기업, 일부 일본 소재기업 |

### 시간 레이어

- **3-5년 (2027-2030)**: CHIPS Act 팹 양산 시작, AI capex 1차 피크, 관세 효과 가시화
- **5-10년 (2030-2035)**: 미국 내 소재·화학 대체 성숙, Intel 18A 경쟁력 분기, US-centric SCM 구조 확립 여부

---

## 3개 연구 버킷

### 버킷 A — CHIPS Act 직접 수혜

**연구 대상:**
- Intel Foundry: 18A 기술 현황, $8.5B 보조금 집행 일정, 외부 고객 확보 상황
- TSMC Arizona: N4 양산 현황, N3/N2 일정, $6.6B 보조금 조건, 기술이전 압박
- Micron: Idaho/New York 팹, HBM 미국 생산 일정, $6.1B
- GlobalFoundries: Vermont/New York, 국방·자동차·IoT 틈새, $1.5B
- Samsung Austin: 테일러 팹 지연 현황, $6.4B 조건
- SK Hynix Indiana: HBM 패키징 팹, $3.87B, 2028 양산 목표
- Entegris: 유일 미국계 대형 반도체 소재 기업, CHIPS Act 자재 보조금 수혜
- Corning: 광섬유·데이터센터 케이블, 미국 내 생산

**핵심 질문:** 실제 양산 일정은? 수율/경쟁력은? 보조금 없이도 생존 가능한가?

### 버킷 B — 미국 장비·소재 패권 강화

**연구 대상:**
- Lam Research: 미국산 식각 장비, 중국 수출 제한으로 전략 자산화
- Applied Materials (AMAT): CVD/PVD/CMP, 미국 최대 반도체 장비사
- KLA Corporation: 계측·검사 장비, 미국 내 생산, 수출통제 최대 수혜
- Entegris: CMP 슬러리, 고순도 가스, 미국 본사·미국 생산
- Wolfspeed: SiC 전력반도체, 100% 미국 제조, 국방·EV 수요

**핵심 질문:** 중국 수출 규제로 실제 매출에 어떤 영향? 미국 내 demand로 대체됐는가? 소재 국산화 진척은?

### 버킷 C — AI 인프라 미국 독점

**연구 대상:**
- Vertiv: 데이터센터 전력·냉각, 미국 본사, AI capex 직접 수혜
- Eaton: 전력관리 인프라, 미국 내 데이터센터 전기화
- Amphenol: 커넥터, 미국 본사, AI 서버 내 콘텐츠 급증
- Corning: 광섬유, 데이터센터 내부 배선
- Celestica / Flex: 미국 정렬 EMS, AI 서버 조립

**핵심 질문:** AI capex 수혜가 얼마나 직접적인가? 마진 확장 가시성은? 미국 제조 비중은?

---

## 출력물 구조: `docs/GEO_RESHORE_ANALYSIS.md`

```
1. 상황 분석
   1-1. 트럼프 정책 도구 3가지 (보조금/관세/수출통제) 현황
   1-2. CHIPS Act 집행 현황 (보조금 수령 기업·금액·조건)
   1-3. 수출통제 타임라인 (2022-2026 주요 조치)

2. US Control Score 기업 매핑
   - Tier 1-3 기업 전체 표

3. 버킷별 Top Pick
   3-A. CHIPS Act 직접 수혜 (3-5년 / 5-10년)
   3-B. 미국 장비·소재 (3-5년 / 5-10년)
   3-C. AI 인프라 (3-5년 / 5-10년)

4. 기존 INVEST_DEEPDIVE 4종목 재평가
   - Lasertec, AGC, Soitec, Hamamatsu → Tier 2 리스크 재설정

5. 시나리오 리스크
   - S1: 미국 주도 디커플링 성공
   - S2: 교착 상태 (현재 연장)
   - S3: 중국 자립 가속
```

---

## 연구 방법

병렬 subagent 3개:
- **Agent A**: 버킷 A (CHIPS Act 수혜 기업 실제 진행 상황, 재무 지표)
- **Agent B**: 버킷 B (미국 장비·소재 기업 전략적 지위 + 수출통제 수혜 정량화)
- **Agent C**: 버킷 C (AI 인프라 미국 기업 capex 수혜 + 재무 지표)

각 agent 결과를 취합해 GEO_RESHORE_ANALYSIS.md 작성.

---

## 성공 기준

- 각 버킷에서 3-5년 top pick 2-3개, 5-10년 top pick 2-3개 도출
- 각 pick에 대해: US Control Score, 재무지표(OPM/EV/EBITDA), 핵심 수혜 메커니즘, 리스크 명시
- 기존 INVEST_DEEPDIVE와 동일한 깊이의 분석 품질
