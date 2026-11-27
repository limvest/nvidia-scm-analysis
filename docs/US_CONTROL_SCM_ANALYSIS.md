# 미국 컨트롤 관점의 반도체 공급망 분석

**작성일:** 2026-05-23  
**프레임:** 미국 공급망 주권(Supply Chain Sovereignty) 정책이 공급망 기업별로 미치는 영향  

---

## 1. 상황 분석

### 트럼프의 3가지 정책 도구

트럼프의 목표는 동맹 구축이 아니라 **공급망 주권**이다. 일본·네덜란드·한국은 파트너가 아니라 레버리지 대상이다.

| 도구 | 메커니즘 | 최근 사례 |
|------|---------|---------|
| **CHIPS Act 보조금** (당근) | 미국 내 팹 건설 유도 | 2024년 약정 상한은 TSMC $6.6B, Intel $7.86B, Micron $6.1B, Samsung $4.745B |
| **관세** (채찍) | 해외 생산 비용과 투자 유인 변화 | TSMC 미국 투자 계획 $165B. 관세의 기여도는 추정 |
| **수출통제** (무기화) | 첨단 장비·메모리의 대중 수출 제한 | 네덜란드는 ASML 첨단 노광장비 수출을 허가제로 관리한다. 미국 규정은 품목·목적지·최종 용도에 따라 적용된다. |

### CHIPS Act 지원 약정 (2026.05 조사 기준)

| 기업 | 보조금 | 지역 | 핵심 내용 |
|------|--------|------|---------|
| Intel Foundry | 2024년 약정 **최대 $7.86B** | 애리조나·오하이오 | 2025년 지분 매입 재원에 미지급 보조금 $5.7B 포함 |
| TSMC Arizona | **최대 $6.6B** + 대출 한도 $5B | 애리조나 피닉스 | N4 수율 대만 동등 확인. $165B 투자 약속 |
| Samsung Austin | **최대 $4.745B** | 텍사스 테일러 | 팹 지연 중 |
| Micron | **$6.1B** | 아이다호·뉴욕 | HBM 2026 전량 완판. 아이다호 2027, 뉴욕 2030 |
| SK Hynix Indiana | **최대 $458M** | 인디애나 | 회사 투자 계획 $3.87B. 2028년 하반기 양산 목표 |
| GlobalFoundries | **$1.5B** | 뉴욕 Malta·버몬트 | DoD Trusted Foundry, 방산 독점 |
| Entegris | **최대 $77M** | 콜로라도 | 유일 미국계 대형 반도체 소재사 |

약정액과 지분 전환 조건은 [미 상무부 삼성전자 발표](https://www.nist.gov/news-events/news/2024/12/biden-harris-administration-announces-chips-incentives-award-samsung), [SK하이닉스 지원 내역](https://www.nist.gov/chips/sk-hynix-indiana-west-lafayette), [Entegris 지원 내역](https://www.nist.gov/chips/entegris-colorado-colorado-springs), [Intel 지분 계약 발표](https://www.intel.com/content/www/us/en/newsroom/news/corporate/intel-and-trump-administration-reach-historic-agreement.html)를 기준으로 했다.

### 수출통제 타임라인

수출통제 발표 자료는 [ASML의 2023년 공지](https://www.asml.com/news/press-releases/2023/statement-regarding-export-control-regulations-dutch-government), [BIS의 2024년 12월 조치](https://www.bis.gov/press-release/commerce-strengthens-export-controls-restrict-chinas-capability-produce-advanced-semiconductors-military), [2025년 파운드리 실사 조치](https://www.bis.gov/press-release/commerce-strengthens-restrictions-advanced-computing-semiconductors-enhance-foundry-due-diligence-prevent)에서 확인할 수 있다.

| 시점 | 조치 |
|------|------|
| 2019 | Huawei Entity List 등재 |
| 2020 | TSMC 대 화웨이 납품 차단 |
| 2022.10 | BIS 고급 AI칩·장비 대중 수출 통제 강화 |
| 2023.09 | 네덜란드가 기존 EUV 제한에 더해 첨단 액침 DUV 수출 허가제 시행 |
| 2024.12 | BIS가 반도체 제조장비 24종·소프트웨어 3종과 일부 HBM에 신규 통제 발표 |
| 2025 | BIS가 첨단 칩 제조에 대한 파운드리 고객 확인 의무 강화 |
| 2026 | Hua Hong에 장비 출하 중단 명령. 중국 국산 장비 WFE 점유율 6.5% 도달 |

---

## 2. US Control Score 기업 매핑

### 점수 기준

| 점수 | 기준 |
|------|------|
| **5** | 미국 본사 + 미국 제조 중심 + 미국 정부 직접 관여 |
| **4** | 미국 본사, 제조 일부 해외 — 핵심 IP·결정권 미국 |
| **3** | 외국 본사 + 미국 팹 건설 중 / 또는 미국 기술 종속 |
| **2** | 외국 기업, 미국 정렬(Five Eyes 등) — 부분 노출 |
| **1** | 미국 컨트롤 외부 — 관세·제재 위험권 |

### 전체 기업 매핑

**Score 5 — 완전 미국 통제**

| 기업 | 분류 | 핵심 포지션 | 비고 |
|------|------|------------|------|
| Intel Foundry (INTC) | 팹 | 미국 유일 선단공정 팹 | 2025년 8월 계약 당시 지분 9.9% |
| GlobalFoundries (GFS) | 팹 | DoD Trusted Foundry, 방산 독점 | Cayman 법인 기술적 각주 있음 |
| KLA (KLAC) | 장비 | 공정제어 장비 50%+ 독점 | 미국 내 연구개발·생산 |
| Corning (GLW) | 소재 | 광섬유 미국 내 생산, AI 인프라 | NC 히코리 공장 |

**Score 4 — 핵심 미국 기업**

| 기업 | 분류 | 핵심 포지션 | China% |
|------|------|------------|--------|
| Micron (MU) | 메모리 | 미국 유일 HBM 공급사 | 낮음 |
| Lam Research (LRCX) | 장비 | HBM 식각 장비 독점 | ~30-35% |
| Applied Materials (AMAT) | 장비 | CVD/PVD/CMP 최대 규모 | ~25-28% |
| Vertiv (VRT) | AI 인프라 | 데이터센터 전력·냉각 | <10% |
| Entegris (ENTG) | 소재 | 미국 유일 대형 반도체 소재사 | 제한적 |

**Score 3 — 조건부 미국 정렬**

| 기업 | 분류 | 포지션 | 이슈 |
|------|------|--------|------|
| TSMC Arizona (TSM) | 팹 | 최선단 공정 미국 내 | 본사 대만, 비용 프리미엄 |
| Wolfspeed (WOLF) | SiC | 100% 미국산 SiC 전력반도체 | 파산 후 재건 중 |
| Eaton (ETN) | AI 인프라 | 전력 인프라 AI 수혜 | 아일랜드 법인 |
| Amphenol (APH) | AI 인프라 | AI 서버 커넥터 독점 | 제조 아시아/멕시코 |
| MKS Instruments | 소재 | 팹 장비 서브시스템 | 간접 수혜 |

**Score 2 이하**

| 기업 | 이슈 |
|------|------|
| Celestica (CLS) | 캐나다 법인, Five Eyes 정렬이나 엄밀히 비미국 |
| ASML | 네덜란드, 미국 기술 라이선스 종속 → 레버리지 대상 |
| Lasertec, AGC, TEL, Hamamatsu | 일본 → Tier 2 레버리지 대상 |
| 中 반도체 기업 전반 | 제재·관세 직격 |

---

## 3. 시나리오 리스크

| 시나리오 | 확률 추정 | 승자 | 패자 |
|----------|---------|------|------|
| **S1: 미국 주도 디커플링 성공** (TSMC AZ N2 수율 대만 동등, Intel 18A 외부 고객 확보) | 35% | Micron, KLA, GFS, Corning, Intel | ASML, 일본 소재기업 일부 |
| **S2: 교착 상태** (현재 연장, 비용 프리미엄 지속, 단계적 이행) | 45% | Micron, KLA, Lam, Corning | Intel Foundry (손실 지속), Wolfspeed |
| **S3: 중국 반격 가속** (SMIC 7nm 자립, 화웨이 AI칩 경쟁력 회복) | 20% | GFS(방산 무관), KLA(중국 제외 시장 집중), Corning | Lam/AMAT(중국 완전 차단 시 매출 타격), TSMC AZ |

**모든 시나리오에서 살아남는 기업:** **KLA, Corning, GlobalFoundries** — 공통적으로 US Control 5/5, 대중 노출 낮음, 수요 구조적.


