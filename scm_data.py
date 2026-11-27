#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NVIDIA Vera Rubin SCM — 공급 흐름 기준 재정리 (v3)
5개 에이전트 심층 조사 결과 통합 (2026-05)

신규 필드:
  opm       : 영업이익률 % (최신치, None=미확보)
  nv_exp    : NVIDIA 공급망 매출 노출도 % 추정 (None=추정불가)
  switch_mo : 대체 공급사 재인증 소요 월 (0=대체 불가, None=미추정)
  mkt_shr   : 핵심 제품 시장점유율 % (None=미확보)

출처 등급:
  1차 = SEC/IR 공시 직접 확인
  2차 = 증권사/시장조사/언론 보도
  추정 = 간접 역산
"""
import json

NODES = [

  # ── Stage 0: 원자재·광물 ──────────────────────────────────────────
  {"key":"cn_in",      "name":"중국 인듐광산",        "stage":0,"sub":"광물",     "country":"CN","grade":"Critical","usd":None, "opm":None,"nv_exp":None,"switch_mo":0,  "mkt_shr":70, "gen":"Both","cpo":True,"note":"인듐 글로벌 정련 70%(USGS 2025·1차) · 2025.02 수출허가제 시행 · InP레이저 원료"},
  {"key":"cn_phos",    "name":"중국 적린",             "stage":0,"sub":"광물",     "country":"CN","grade":"Critical","usd":None, "opm":None,"nv_exp":None,"switch_mo":0,  "mkt_shr":80, "cpo":True,"note":"적린 글로벌 생산 80%+ · InP 합성 필수"},
  {"key":"dowa",       "name":"Dowa",                  "stage":0,"sub":"광물",     "country":"JP","grade":"",        "usd":3.8,  "opm":None,"nv_exp":1,   "switch_mo":24, "mkt_shr":None,"note":"인듐·갈륨 정련 → AXT 공급"},
  {"key":"sum_mining", "name":"Sumitomo Mining",        "stage":0,"sub":"광물",     "country":"JP","grade":"",        "usd":14.2, "opm":None,"nv_exp":1,   "switch_mo":None,"mkt_shr":None,"note":"귀금속·니켈·코발트 정련"},
  {"key":"umicore",    "name":"Umicore",                "stage":0,"sub":"광물",     "country":"EU","grade":"",        "usd":3.4,  "opm":None,"nv_exp":1,   "switch_mo":None,"mkt_shr":None,"note":"코발트·백금족 리사이클"},
  {"key":"heraeus",    "name":"Heraeus",                "stage":0,"sub":"광물",     "country":"EU","grade":"",        "usd":None, "opm":None,"nv_exp":1,   "switch_mo":None,"mkt_shr":None,"note":"귀금속 본딩와이어 (비상장)"},
  {"key":"tosoh",      "name":"Tosoh",                  "stage":0,"sub":"광물",     "country":"JP","grade":"",        "usd":5.1,  "opm":None,"nv_exp":1,   "switch_mo":None,"mkt_shr":None,"note":"고순도 금속산화물"},
  {"key":"albemarle",  "name":"Albemarle",              "stage":0,"sub":"광물",     "country":"US","grade":"",        "usd":6.5,  "opm":None,"nv_exp":1,   "switch_mo":None,"mkt_shr":None,"note":"리튬·희토류 정제"},
  {"key":"covestro",   "name":"Covestro",               "stage":0,"sub":"광물",     "country":"EU","grade":"",        "usd":6.2,  "opm":None,"nv_exp":1,   "switch_mo":None,"mkt_shr":None,"note":"PCB 폴리머 원료"},

  # ── Stage 1: 특수가스·화학·필름 ───────────────────────────────────
  {"key":"linde",      "name":"Linde",                  "stage":1,"sub":"특수가스", "country":"EU","grade":"",        "usd":237.9,"opm":29.8,"nv_exp":3,   "switch_mo":12, "mkt_shr":None,"note":"특수가스 글로벌 1위 · TSMC 애리조나 팹21 온사이트 $6억 투자 (1차: Linde IR)"},
  {"key":"air_liq",    "name":"Air Liquide",             "stage":1,"sub":"특수가스", "country":"EU","grade":"",        "usd":120.5,"opm":None,"nv_exp":3,   "switch_mo":12, "mkt_shr":None,"note":"특수가스 글로벌 2위"},
  {"key":"air_prod",   "name":"Air Products",            "stage":1,"sub":"특수가스", "country":"US","grade":"",        "usd":64.6, "opm":None,"nv_exp":2,   "switch_mo":12, "mkt_shr":None,"note":"특수가스·수소"},
  {"key":"showa_g",    "name":"Showa Denko (가스)",      "stage":1,"sub":"특수가스", "country":"JP","grade":"",        "usd":19.7, "opm":None,"nv_exp":2,   "switch_mo":18, "mkt_shr":None,"note":"전자용 특수가스"},
  {"key":"merck_e",    "name":"Merck KGaA",              "stage":1,"sub":"화학",     "country":"EU","grade":"High",    "usd":52.0, "opm":None,"nv_exp":5,   "switch_mo":18, "mkt_shr":None,"note":"EUV 포토레지·전자화학"},
  {"key":"jsr",        "name":"JSR",                    "stage":1,"sub":"포토레지", "country":"JP","grade":"High",    "usd":None, "opm":None,"nv_exp":5,   "switch_mo":36, "mkt_shr":27,  "note":"EUV 포토레지 글로벌 ~27% · 일본 정부(JIC·METI) $63억 인수 완료 2024.4 → 국가 통제 (1차: JIC 발표)"},
  {"key":"tok",        "name":"Tokyo Ohka (TOK)",        "stage":1,"sub":"포토레지", "country":"JP","grade":"High",    "usd":3.9,  "opm":None,"nv_exp":4,   "switch_mo":36, "mkt_shr":None,"note":"포토레지스트·현상액 · JSR+TOK+신에쓰 합산 EUV PR 90%+ (2차)"},
  {"key":"shin_pr",    "name":"Shin-Etsu (PR부문)",      "stage":1,"sub":"포토레지", "country":"JP","grade":"High",    "usd":None, "opm":None,"nv_exp":3,   "switch_mo":36, "mkt_shr":None,"note":"포토레지스트 3위 · 일본 PR 3사 합산 EUV 95%+ (2차)"},
  {"key":"entegris",   "name":"Entegris",               "stage":1,"sub":"화학",     "country":"US","grade":"High",    "usd":13.2, "opm":21.3,"nv_exp":8,   "switch_mo":18, "mkt_shr":23,  "note":"CMP 슬러리 ~23% 1위 · FY2025 조정OPM 21.3% EBITDA 27.7% (1차: SEC 8-K)"},
  {"key":"cabot",      "name":"Cabot Micro",             "stage":1,"sub":"화학",     "country":"US","grade":"",        "usd":1.9,  "opm":None,"nv_exp":2,   "switch_mo":12, "mkt_shr":None,"note":"CMP 슬러리 2위"},
  {"key":"stella",     "name":"Stella Chemifa",          "stage":1,"sub":"화학",     "country":"JP","grade":"",        "usd":0.5,  "opm":None,"nv_exp":2,   "switch_mo":24, "mkt_shr":None,"note":"고순도 HF · 12N+ 초순도급 일본 집중 · 2019 후 韓 의존도 50% 이하로 감소"},
  {"key":"kanto",      "name":"Kanto Chemical",          "stage":1,"sub":"화학",     "country":"JP","grade":"",        "usd":0.8,  "opm":None,"nv_exp":2,   "switch_mo":12, "mkt_shr":None,"note":"초고순도 시약"},
  {"key":"daikin",     "name":"Daikin (불소)",           "stage":1,"sub":"화학",     "country":"JP","grade":"",        "usd":None, "opm":None,"nv_exp":2,   "switch_mo":18, "mkt_shr":None,"note":"불소가스·불소폴리머"},
  {"key":"ajinomoto",  "name":"Ajinomoto (ABF필름)",     "stage":1,"sub":"필름",     "country":"JP","grade":"Critical","usd":31.2, "opm":12.6,  "nv_exp":40,  "switch_mo":72, "mkt_shr":95,  "note":"ABF필름 독점 95%+ · 2026년 3월 결산 연결 영업이익률 12.6% · Q3 2026 30% 가격인상 확정 · 독점 렌트 구조 · 대체 인증 5~7년"},
  {"key":"resonac",    "name":"Resonac (NCF필름)",       "stage":1,"sub":"필름",     "country":"JP","grade":"High",    "usd":19.7, "opm":None,"nv_exp":15,  "switch_mo":24, "mkt_shr":35,  "note":"NCF필름 상위3사(Resonac·Henkel·Namics) 합산 99% · HBM TCB공정 필수 · ¥150억 3.5~5배 증설 (1차: Resonac IR) · HBM4E 하이브리드본딩 전환시 수요 감소 리스크"},
  {"key":"henkel",     "name":"Henkel",                  "stage":1,"sub":"필름",     "country":"EU","grade":"",        "usd":32.0, "opm":None,"nv_exp":5,   "switch_mo":12, "mkt_shr":None,"note":"언더필·에폭시 접착 · NCF 3사 중 하나"},
  {"key":"namics",     "name":"Namics",                  "stage":1,"sub":"필름",     "country":"JP","grade":"",        "usd":None, "opm":None,"nv_exp":3,   "switch_mo":12, "mkt_shr":None,"note":"언더필 (Henkel 자회사) · NCF 3사 중 하나"},
  {"key":"fuji_mb",    "name":"Fujifilm (마스크블랭크)", "stage":1,"sub":"필름",     "country":"JP","grade":"",        "usd":None, "opm":None,"nv_exp":2,   "switch_mo":24, "mkt_shr":None,"note":"포토마스크 블랭크 → DNP/Toppan 원료"},

  # ── Stage 2: 웨이퍼 기재·InP기판 ─────────────────────────────────
  {"key":"shinetsu_si","name":"Shin-Etsu (Si웨이퍼)",   "stage":2,"sub":"Si웨이퍼", "country":"JP","grade":"High",    "usd":80.1, "opm":None,"nv_exp":8,   "switch_mo":60, "mkt_shr":30,  "note":"실리콘웨이퍼 글로벌 1위 ~27~33%(300mm) · 전자재료 영업이익 +11.8% YoY AI수요 직접언급 · ¥1.5조 +200K wafer/월 증설 2026~2028 (1차: Shin-Etsu IR)"},
  {"key":"sumco",      "name":"SUMCO",                   "stage":2,"sub":"Si웨이퍼", "country":"JP","grade":"High",    "usd":6.8,  "opm":None,"nv_exp":5,   "switch_mo":60, "mkt_shr":22,  "note":"실리콘웨이퍼 2위 ~21~24%(300mm) · FY2025 영업손실(신팹 감가상각 ¥100B/년) · 배당 재차 삭감 · 과점력 유지 (1차: SUMCO IR)"},
  {"key":"siltronic",  "name":"Siltronic",               "stage":2,"sub":"Si웨이퍼", "country":"EU","grade":"",        "usd":1.8,  "opm":None,"nv_exp":3,   "switch_mo":36, "mkt_shr":13,  "note":"실리콘웨이퍼 3위 · 신에쓰+SUMCO+Siltronic 3사 65%+ 과점"},
  {"key":"sk_siltron", "name":"SK Siltron",              "stage":2,"sub":"Si웨이퍼", "country":"KR","grade":"",        "usd":None, "opm":None,"nv_exp":3,   "switch_mo":36, "mkt_shr":None,"note":"실리콘웨이퍼 (SK그룹 비상장)"},
  {"key":"axt",        "name":"AXT",                    "stage":2,"sub":"InP기판",  "country":"US","grade":"Critical","usd":0.5,  "opm":-20, "nv_exp":10,  "switch_mo":0,  "mkt_shr":35,  "gen":"Both","cpo":True,"note":"InP기판 35% · FY2025 매출 $88.3M(-11%) 총이익률 13.1%(전년 24.3%→급락) 순손실 $18M · 베이징 생산+중국 수출허가 의존 → 실제 Q2·Q4 차단 경험 · 수주잔고 $60M+(사상최고)지만 허가가 병목 (1차: AXT 8-K)"},
  {"key":"sum_elec_inp","name":"Sumitomo Elec (InP)",    "stage":2,"sub":"InP기판",  "country":"JP","grade":"High",    "usd":52.6, "opm":None,"nv_exp":8,   "switch_mo":24, "mkt_shr":60,  "gen":"Both","cpo":True,"note":"InP기판 45~60% 1위 (2차: Goldman Sachs) · InP기판 타이트 2027까지 지속 예상"},
  {"key":"soitec",     "name":"Soitec",                  "stage":2,"sub":"SOI웨이퍼","country":"EU","grade":"High",    "usd":6.9,  "opm":15.2,"nv_exp":15,  "switch_mo":36, "mkt_shr":95,  "gen":"Both","cpo":True,"note":"SiPh 기반 SOI 웨이퍼 95%+ 독점(Bank of America 추정, 2차) · SmartCut 특허 ~4,300건 · FY2025 €891M(-9%) EBIT 15.2%(전년 25%→급락) · Photonics-SOI €100M · Rubin CPO·Feynman OIO 모두 SOI 기판 필수 → 구조적 이중 수혜 · 성장 20~30% 전망(BofA, 2차) (1차: Soitec IR)"},

  # ── Stage 3: 장비 핵심 부품 (장비사에 납품) ──────────────────────
  {"key":"carl_zeiss", "name":"Carl Zeiss SMT",          "stage":3,"sub":"ASML부품", "country":"EU","grade":"Critical","usd":None, "opm":None,"nv_exp":15,  "switch_mo":0,  "mkt_shr":100, "note":"EUV 광학계 100% 독점 → ASML · ASML 지분 24.9% 보유(€1B+€760M 추가투자) · 중국 EUV 복제 불가의 핵심 이유 (1차: ASML 공시)"},
  {"key":"trumpf",     "name":"Trumpf",                  "stage":3,"sub":"ASML부품", "country":"EU","grade":"Critical","usd":None, "opm":None,"nv_exp":12,  "switch_mo":0,  "mkt_shr":100, "note":"CO₂ EUV 레이저 100% → ASML · 비상장 · 독일 정부 전략자산 지정"},
  {"key":"cymer",      "name":"Cymer (ASML자회사)",      "stage":3,"sub":"ASML부품", "country":"US","grade":"Critical","usd":None, "opm":None,"nv_exp":10,  "switch_mo":0,  "mkt_shr":100, "note":"ArF 엑시머 레이저 → ASML 완전인수 · ASML 내재화"},
  {"key":"hamamatsu",  "name":"Hamamatsu Photonics",     "stage":3,"sub":"Disco부품","country":"JP","grade":"Critical","usd":4.9,  "opm":7.6,  "nv_exp":8,   "switch_mo":24, "mkt_shr":100, "note":"SD 레이저 단독 → Disco · FY2025 연결 영업이익률 7.6% · Disco-Hamamatsu 사실상 단독 공급 파트너십"},
  {"key":"mks",        "name":"MKS Instruments",         "stage":3,"sub":"장비부품", "country":"US","grade":"",        "usd":3.2,  "opm":None,"nv_exp":5,   "switch_mo":12, "mkt_shr":None,"note":"가스흐름제어·RF전원 → 각 장비사"},
  {"key":"ucl",        "name":"Ultra Clean Holdings",    "stage":3,"sub":"장비부품", "country":"US","grade":"",        "usd":3.8,  "opm":None,"nv_exp":4,   "switch_mo":12, "mkt_shr":None,"note":"가스전달시스템 → 각 장비사"},

  # ── Stage 4: 반도체·MOCVD 제조장비 ───────────────────────────────
  {"key":"asml",       "name":"ASML",                   "stage":4,"sub":"전공정장비","country":"NL","grade":"Critical","usd":613.6,"opm":34.5,"nv_exp":15,  "switch_mo":0,  "mkt_shr":100, "note":"EUV 리소그래피 100% 독점 · OPM 34.5% · Carl Zeiss 지분 24.9% · 중국 매출 49%→20~33% · 순현금 €10.6B · High-NA EUV 출하 개시 (1차: ASML 20-F/연차보고서)"},
  {"key":"amat",       "name":"Applied Materials",       "stage":4,"sub":"전공정장비","country":"US","grade":"High",    "usd":162.0,"opm":30.7,"nv_exp":12,  "switch_mo":18, "mkt_shr":80,  "note":"PVD 80%+ · CMP 64% · FY2025 Non-GAAP OPM 30.7% · 상위2고객 34%(TSMC+Samsung추정) · 中 31%→하락 중 · CoWoS 공정 채용 (1차: AMAT 10-K)"},
  {"key":"lam",        "name":"Lam Research",            "stage":4,"sub":"전공정장비","country":"US","grade":"High",    "usd":93.0, "opm":35.0,"nv_exp":12,  "switch_mo":24, "mkt_shr":50,  "note":"HAR 에칭 독점(100:1 종횡비) · ALD Moly 선도 · OPM 35%(사상최고) GM 50.6% · 中 <30% 목표 $600M 영향 (1차: Lam Q Sep25 Earnings)"},
  {"key":"kla",        "name":"KLA",                    "stage":4,"sub":"전공정장비","country":"US","grade":"High",    "usd":96.0, "opm":41.0,"nv_exp":10,  "switch_mo":0,  "mkt_shr":74,  "note":"결함검사·계측 73.8% 점유(사상최고) · OPM 41%(5대장비사 최고) · 수율 1pp=$100~300M → 경제적 교체 불가 · 中 33% $500M 영향 (1차: KLA FY2025, 2차: Dr.Castellano)"},
  {"key":"tel",        "name":"Tokyo Electron",          "stage":4,"sub":"전공정장비","country":"JP","grade":"High",    "usd":64.0, "opm":28.7,"nv_exp":12,  "switch_mo":0,  "mkt_shr":90,  "note":"Track(코팅/현상) 90% · EUV Track 100%(ASML EUV와 물리적 결합) · OPM 28.7% · FY2025 매출 ¥2,431B 사상최고 · 中 30~38% (1차: TEL IR FY2025)"},
  {"key":"screen",     "name":"Screen Holdings",         "stage":4,"sub":"전공정장비","country":"JP","grade":"",        "usd":4.8,  "opm":None,"nv_exp":4,   "switch_mo":18, "mkt_shr":10,  "note":"세정·스핀코팅 · TEL 이외 Track 10% 점유"},
  {"key":"axcelis",    "name":"Axcelis",                 "stage":4,"sub":"전공정장비","country":"US","grade":"",        "usd":2.5,  "opm":None,"nv_exp":3,   "switch_mo":18, "mkt_shr":None,"note":"이온주입 장비"},
  {"key":"hitachi_ht", "name":"Hitachi High-Tech",       "stage":4,"sub":"전공정장비","country":"JP","grade":"",        "usd":None, "opm":None,"nv_exp":3,   "switch_mo":18, "mkt_shr":None,"note":"SEM 검사 (Hitachi 자회사)"},
  {"key":"aixtron",    "name":"AIXTRON",                 "stage":4,"sub":"MOCVD장비","country":"EU","grade":"Critical","usd":6.9,  "opm":21.0,"nv_exp":15,  "switch_mo":24, "mkt_shr":90,  "gen":"Both","cpo":True,"note":"InP/GaAs MOCVD 90%+ 독점 · FY2024 €633.2M EBIT 21% · 수주잔고 €171M +30%YoY · 장비 리드타임 18~24개월=CPO 캐파의 실질 병목 · 2016 中 Fujian Grand Chip 인수 차단 (1차: AIXTRON IR)"},
  {"key":"veeco",      "name":"Veeco",                   "stage":4,"sub":"MOCVD장비","country":"US","grade":"",        "usd":3.5,  "opm":None,"nv_exp":5,   "switch_mo":24, "mkt_shr":10,  "note":"AIXTRON 대안 MOCVD · 시장점유 낮음"},

  # ── Stage 5: 후공정·테스트·포토마스크·유틸리티 장비 ──────────────
  {"key":"disco",      "name":"Disco",                   "stage":5,"sub":"후공정장비","country":"JP","grade":"Critical","usd":44.8, "opm":42.0,"nv_exp":20,  "switch_mo":18, "mkt_shr":None,"note":"그라인딩·다이싱 · FY2026 매출 ¥436.8B +11.1% AI/HBM 직접명시 · OPM ~42% · Hamamatsu SD레이저 단독 의존 (1차: Disco IR FY2026)"},
  {"key":"advantest",  "name":"Advantest",               "stage":5,"sub":"후공정장비","country":"JP","grade":"High",    "usd":122.0,"opm":44.2,"nv_exp":20,  "switch_mo":18, "mkt_shr":70,  "note":"HBM·GPU 테스트 1위 ~70% · FY2025 ¥1조1,286B(사상최고) FY2026 가이던스 ¥1조4,200B($9.5B +26%) · 시장규모 $125~130B (1차: Advantest IR)"},
  {"key":"teradyne",   "name":"Teradyne",                "stage":5,"sub":"후공정장비","country":"US","grade":"Medium",  "usd":17.0, "opm":None,"nv_exp":8,   "switch_mo":18, "mkt_shr":None,"note":"반도체 테스트 · Advantest 대안 · GPU테스트 시장 점유 낮으나 HBM 이외 부품 커버"},
  {"key":"hanmi",      "name":"한미반도체",              "stage":5,"sub":"후공정장비","country":"KR","grade":"High",    "usd":21.0, "opm":43.6,"nv_exp":15,  "switch_mo":12, "mkt_shr":71,  "note":"TC본더 점유 71.2% OPM 43.6% · ★독점 붕괴: SK하이닉스 2025년 가격인상 거부→ASMPT 7대 발주(~300억) + Hanwha Semitech 진입 · 2026 점유 20~30% 급락 예상 · Micron으로 반격 중 (1차: 한미반도체 사업보고서·2차보도)"},
  {"key":"asmpt",      "name":"ASMPT",                   "stage":5,"sub":"후공정장비","country":"HK","grade":"High",    "usd":9.3,  "opm":None,"nv_exp":8,   "switch_mo":12, "mkt_shr":None,"note":"와이어본더·다이본더 · SK하이닉스 TC본더 한미반도체 대안 진입(7대 발주) · 한미반도체 독점 붕괴 수혜 · HBM4E TC본더 공급 경쟁 가속 · 시장점유 2026 20~30% 목표(2차)"},
  {"key":"besi",       "name":"BESI",                    "stage":5,"sub":"후공정장비","country":"EU","grade":"High",    "usd":24.9, "opm":None,"nv_exp":10,  "switch_mo":18, "mkt_shr":67,  "gen":"Both","note":"하이브리드본딩 ~67% · FY2025 €591.3M 수주 €685M · 2026 HB매출 €476M 목표 · HBM5·SoIC 전환 핵심 장비사 · Cu-Cu 하이브리드본딩 차세대 병목 (1차: BESI IR)"},
  {"key":"formfactor", "name":"FormFactor",              "stage":5,"sub":"후공정장비","country":"US","grade":"Medium",  "usd":10.0, "opm":None,"nv_exp":10,  "switch_mo":12, "mkt_shr":None,"note":"프로브카드 · Q1 2026 고객: SK하이닉스 29.5% NVIDIA 10.2% (1차: FormFactor 10-Q)"},
  {"key":"cohu",       "name":"Cohu",                    "stage":5,"sub":"후공정장비","country":"US","grade":"",        "usd":1.4,  "opm":None,"nv_exp":4,   "switch_mo":12, "mkt_shr":None,"note":"테스트 핸들러"},
  {"key":"ks",         "name":"Kulicke & Soffa",          "stage":5,"sub":"후공정장비","country":"US","grade":"",        "usd":2.1,  "opm":None,"nv_exp":4,   "switch_mo":12, "mkt_shr":None,"note":"와이어본더"},
  {"key":"dnp",        "name":"Dai Nippon Printing",     "stage":5,"sub":"포토마스크","country":"JP","grade":"",        "usd":8.5,  "opm":None,"nv_exp":3,   "switch_mo":18, "mkt_shr":None,"note":"포토마스크 세계1위"},
  {"key":"toppan",     "name":"Toppan",                  "stage":5,"sub":"포토마스크","country":"JP","grade":"",        "usd":7.3,  "opm":None,"nv_exp":3,   "switch_mo":18, "mkt_shr":None,"note":"포토마스크 세계2위"},
  {"key":"photronics", "name":"Photronics",              "stage":5,"sub":"포토마스크","country":"US","grade":"",        "usd":1.0,  "opm":None,"nv_exp":2,   "switch_mo":18, "mkt_shr":None,"note":"포토마스크 세계3위"},
  {"key":"kurita",     "name":"Kurita Water",            "stage":5,"sub":"유틸리티", "country":"JP","grade":"",        "usd":4.2,  "opm":None,"nv_exp":2,   "switch_mo":12, "mkt_shr":None,"note":"반도체용 초순수"},
  {"key":"organo",     "name":"Organo",                  "stage":5,"sub":"유틸리티", "country":"JP","grade":"",        "usd":1.5,  "opm":None,"nv_exp":2,   "switch_mo":12, "mkt_shr":None,"note":"초순수·수처리"},
  {"key":"pall",       "name":"Pall (Danaher)",          "stage":5,"sub":"유틸리티", "country":"US","grade":"",        "usd":None, "opm":None,"nv_exp":2,   "switch_mo":12, "mkt_shr":None,"note":"여과·화학관리 (Danaher 자회사)"},

  # ── Stage 6: 가공기판·에피웨이퍼 ─────────────────────────────────
  {"key":"ibiden",     "name":"Ibiden (ABF기판)",        "stage":6,"sub":"ABF기판",  "country":"JP","grade":"High",    "usd":31.4, "opm":14.3,"nv_exp":60,  "switch_mo":18, "mkt_shr":75,  "note":"ABF기판 GPU 75%(Blackwell 기준·2차) · FY2026 ¥420B +13.7% OPM 14.3% · $3.3B 캐파증설(애리조나 포함) · Ajinomoto ABF필름이 원가 15~25% · 신팹 리드타임 24~36개월 (1차: Ibiden IR)"},
  {"key":"shinko",     "name":"Shinko Electric (기판)",  "stage":6,"sub":"기판",     "country":"JP","grade":"",        "usd":3.8,  "opm":None,"nv_exp":10,  "switch_mo":18, "mkt_shr":None,"note":"FC-BGA 기판 · Ibiden 대안"},
  {"key":"ats",        "name":"AT&S",                   "stage":6,"sub":"기판",     "country":"EU","grade":"",        "usd":1.0,  "opm":None,"nv_exp":5,   "switch_mo":24, "mkt_shr":None,"note":"고다층 기판 · 유럽 유일 · 청두 생산 확장 2026.5(지정학 재노출 역설)"},
  {"key":"unimicron",  "name":"Unimicron",               "stage":6,"sub":"기판",     "country":"TW","grade":"Medium",  "usd":3.2,  "opm":None,"nv_exp":20,  "switch_mo":18, "mkt_shr":25,  "note":"ABF기판 2위 ~25% · Ibiden 대안 · 대만 집중(Ibiden 차단 시 부분 대안)"},
  {"key":"kinsus",     "name":"Kinsus",                  "stage":6,"sub":"기판",     "country":"TW","grade":"",        "usd":1.1,  "opm":None,"nv_exp":5,   "switch_mo":18, "mkt_shr":None,"note":"IC기판"},
  {"key":"kyocera",    "name":"Kyocera (세라믹패키지)",  "stage":6,"sub":"기판",     "country":"JP","grade":"",        "usd":13.0, "opm":None,"nv_exp":3,   "switch_mo":24, "mkt_shr":None,"note":"세라믹 패키지·LTCC"},
  {"key":"ngk",        "name":"NGK Insulators",          "stage":6,"sub":"기판",     "country":"JP","grade":"",        "usd":5.0,  "opm":None,"nv_exp":3,   "switch_mo":24, "mkt_shr":None,"note":"세라믹 기판"},
  {"key":"iqe",        "name":"IQE",                    "stage":6,"sub":"InP에피",  "country":"EU","grade":"Critical","usd":0.5,  "opm":7,   "nv_exp":10,  "switch_mo":36, "mkt_shr":None,"gen":"Both","cpo":True,"note":"InP 에피웨이퍼 → Coherent/Lumentum · FY2024 £118M adj.EBITDA 7% · H1 2025 -31% YoY EBITDA 적자 전환 · 순부채 £23.5M 악화 · ★재무취약 Critical공급사 (1차: IQE 공시)"},

  # ── Stage 7: EDA·IP·설계도구 ─────────────────────────────────────
  {"key":"cadence",    "name":"Cadence",                 "stage":7,"sub":"EDA",      "country":"US","grade":"High",    "usd":98.9, "opm":44.6,"nv_exp":10,  "switch_mo":36, "mkt_shr":None,"note":"EDA+IP · FY2025 $5,297M Non-GAAP OPM 44.6% · 설계 워크플로 교체 36개월+ → 실질 교체 불가 · NVIDIA 개별비중 미공개 (1차: Cadence 10-K)"},
  {"key":"synopsys",   "name":"Synopsys",                "stage":7,"sub":"EDA",      "country":"US","grade":"High",    "usd":96.5, "opm":None,"nv_exp":10,  "switch_mo":36, "mkt_shr":None,"note":"EDA+IP+보안 · Ansys $35B 합병 완료 2025.7 → 칩설계~시스템시뮬레이션 통합 독점 확장 · FTC 조건부 승인(광학SW Keysight 매각) · 설계 워크플로 교체 36개월+"},
  {"key":"siemens_eda","name":"Siemens EDA",             "stage":7,"sub":"EDA",      "country":"EU","grade":"",        "usd":None, "opm":None,"nv_exp":5,   "switch_mo":36, "mkt_shr":None,"note":"Mentor 인수 (비상장 부문)"},
  {"key":"arm",        "name":"Arm Holdings",            "stage":7,"sub":"IP",       "country":"US","grade":"High",    "usd":160.0,"opm":None,"nv_exp":8,   "switch_mo":None,"mkt_shr":90,  "note":"Vera CPU 아키텍처 IP · 데이터센터 CPU 90%+ 라이선스 · FY2025 라이선스 $1,839M +28.5% 로열티 $2,168M +21% · Feynman Rosa CPU도 Arm 계승 (1차: ARM 20-F)"},
  {"key":"ansys",      "name":"Ansys",                   "stage":7,"sub":"EDA",      "country":"US","grade":"",        "usd":35.0, "opm":None,"nv_exp":5,   "switch_mo":None,"mkt_shr":None,"note":"시뮬레이션·열해석 · Synopsys에 합병 완료"},
  {"key":"rambus",     "name":"Rambus",                  "stage":7,"sub":"IP",       "country":"US","grade":"",        "usd":3.8,  "opm":None,"nv_exp":5,   "switch_mo":None,"mkt_shr":None,"note":"HBM 인터페이스 IP"},
  {"key":"imec",       "name":"IMEC",                    "stage":7,"sub":"R&D",      "country":"EU","grade":"",        "usd":None, "opm":None,"nv_exp":5,   "switch_mo":None,"mkt_shr":None,"note":"반도체 공동R&D(비영리) · ASML+NVIDIA+TSMC 참여 · IMEC-ASML 5년 파트너십 2025 갱신 · 기초연구IP=IMEC, 멤버사 라이선스 취득"},

  # ── Stage 8: 파운드리·메모리 ──────────────────────────────────────
  {"key":"tsmc",       "name":"TSMC",                   "stage":8,"sub":"파운드리", "country":"TW","grade":"Critical","usd":2111.7,"opm":50.8,"nv_exp":19,  "switch_mo":48, "mkt_shr":100, "note":"N3P+CoWoS-L GPU 100% · NVIDIA 매출비중 19%(2025·2위고객) · OPM 50.8% · CoWoS 60~63% NVIDIA독점 · 어닝콜 'fully booked 2025~2026' (1차: TSMC 연차보고서 SEC 6-K)"},
  {"key":"samsung_f",  "name":"Samsung Foundry",        "stage":8,"sub":"파운드리", "country":"KR","grade":"Medium",  "usd":None, "opm":-15, "nv_exp":5,   "switch_mo":36, "mkt_shr":None,"note":"FY2024 약 4조원 손실 · 2nm GAA 수율 미달로 NVIDIA·Qualcomm 일부 주문 TSMC 복귀 · CoWoS 대안(SAINT) 개발중 TSMC 대비 2~3년 격차 (2차: WCCFTech·TrendForce)"},
  {"key":"intel_f",    "name":"Intel Foundry",          "stage":8,"sub":"파운드리", "country":"US","grade":"",        "usd":595.6,"opm":-58, "nv_exp":1,   "switch_mo":60, "mkt_shr":None,"note":"FY2025 영업손실 $10.3B · 내부거래 90%+ · 18A High-NA EUV 도입중 · NVIDIA수주 가능성 2027년 이후 (1차: Intel 8-K IR)"},
  {"key":"umc",        "name":"UMC",                    "stage":8,"sub":"파운드리", "country":"TW","grade":"",        "usd":24.0, "opm":18.5,"nv_exp":2,   "switch_mo":None,"mkt_shr":None,"note":"성숙공정 28/22nm · FY2025 OPM 18.5% 총이익률 29.0% (1차: UMC 6-K)"},
  {"key":"gf",         "name":"GlobalFoundries",        "stage":8,"sub":"파운드리", "country":"US","grade":"High",    "usd":44.6, "opm":11.7,"nv_exp":20,  "switch_mo":0,  "mkt_shr":100, "gen":"Feynman","cpo":True,"note":"TeraPHY OIO 칩렛 유일 파운드리(45SPCLO 공정) · FY2025 OPM 11.7% Non-IFRS 15.7% · 2025.11 AMF(싱가포르) 인수로 SiPh 캐파 확대 · 비상장(Mubadala 소유) → 캐파·수율 외부 검증 불가 · Feynman 광인터커넥트 핵심 단일 파운드리 (1차: GF 6-K; AMF 인수 공시)"},
  {"key":"tsmc_coupe", "name":"TSMC COUPE",             "stage":8,"sub":"파운드리", "country":"TW","grade":"Critical","usd":None, "opm":None,"nv_exp":30,  "switch_mo":0,  "mkt_shr":100, "gen":"Feynman","cpo":True,"note":"Co-packaged Optics and Ushered Photonics Engine · NVLink 스위치 CPO 파운드리 · 2026 H2 양산 목표 · NVIDIA 단독 의존 · GF 45SPCLO 대비 후속 통합 플랫폼 · 대만 지정학=TSMC N3P와 동일 리스크 (TrendForce 2026.4; borecraft 2026.5, 2차)"},
  {"key":"tower",      "name":"Tower Semi",             "stage":8,"sub":"파운드리", "country":"IL","grade":"Medium",  "usd":33.2, "opm":9.2, "nv_exp":8,   "switch_mo":36, "mkt_shr":None,"cpo":True,"note":"SiPho PIC 파운드리 · Soitec SOI 1:1 의존 · NVIDIA $13억 SiPho 계약(1차: Tower IR) · Quintessent QD-on-Si 파운드리 파트너 · Q1 2025 OPM 9.2% (1차: Tower 6-K)"},
  {"key":"skhynix",    "name":"SK Hynix",               "stage":8,"sub":"메모리",   "country":"KR","grade":"Critical","usd":915.5,"opm":48.6,  "nv_exp":27,  "switch_mo":24, "mkt_shr":70,  "note":"HBM4 주공급 70%(Rubin) · FY2025 OPM 48.6% · Q1 2026 OPM 72%(역대최고) · NVIDIA 매출비중 ~27% · HBM 3년치 완판 (1차: SK하이닉스 IR·CNBC 2026.4.23)"},
  {"key":"micron",     "name":"Micron",                 "stage":8,"sub":"메모리",   "country":"US","grade":"High",    "usd":859.4,"opm":47.0,"nv_exp":17,  "switch_mo":24, "mkt_shr":20,  "note":"HBM4 Rubin 20% 공급 직접명시 · Q1 FY2026 OPM 47%(역대최고) 매출 $13.6B +57% · Vera Rubin용 HBM4 36GB 12-Hi 양산 명시 · 2026 HBM 완판 · HBM TAM $35B→$100B(2028) (1차: Micron 10-Q·8-K·FY2026)"},
  {"key":"samsung_m",  "name":"Samsung Memory",         "stage":8,"sub":"메모리",   "country":"KR","grade":"High",    "usd":None, "opm":None,"nv_exp":10,  "switch_mo":24, "mkt_shr":10,  "note":"HBM4 2차 공급(~10%) · SK하이닉스·Micron 대비 후발 · HBM4E 커스텀 2026.5~6 완료 목표 · HBM 수율 개선 중 (2차: TrendForce)"},
  {"key":"kioxia",     "name":"Kioxia",                 "stage":8,"sub":"메모리",   "country":"JP","grade":"",        "usd":None, "opm":None,"nv_exp":3,   "switch_mo":None,"mkt_shr":None,"note":"NAND 플래시"},
  {"key":"wd",         "name":"Western Digital",        "stage":8,"sub":"메모리",   "country":"US","grade":"",        "usd":20.0, "opm":None,"nv_exp":3,   "switch_mo":None,"mkt_shr":None,"note":"NAND"},

  # ── Stage 9: 칩·광엔진·광모듈 ────────────────────────────────────
  {"key":"broadcom",   "name":"Broadcom",               "stage":9,"sub":"칩",       "country":"US","grade":"High",    "usd":1962.9,"opm":None,"nv_exp":15,  "switch_mo":24, "mkt_shr":80,  "note":"DC이더넷 80%+ · AI매출 FY2025 $20B +74% Q1 FY2026 $8.4B +106% · ★ NVIDIA ConnectX-8가 PCIe SW 내장→Broadcom 시장잠식 중 · NVIDIA 공급자이면서 AI ASIC으로 경쟁(이중관계) (1차: Broadcom IR)"},
  {"key":"marvell",    "name":"Marvell (광DSP)",        "stage":9,"sub":"칩",       "country":"US","grade":"Medium",  "usd":167.0,"opm":None,"nv_exp":30,  "switch_mo":24, "mkt_shr":None,"cpo":True,"note":"Ara 광DSP · FY2026 $8.2B +42% · NVIDIA $20억 투자 2026.3.31 (1차: Marvell IR)"},
  {"key":"coherent",   "name":"Coherent",               "stage":9,"sub":"광엔진",   "country":"US","grade":"High",    "usd":74.0, "opm":None,"nv_exp":40,  "switch_mo":24, "mkt_shr":None,"gen":"Both","cpo":True,"note":"CPO 광엔진 · NVIDIA 보통주 직접매입(단순주주) · InP 2027년 soldout · CPO신매출 2026 H2 · 200G EML 대량출하 (1차: Coherent 10-K·2차보도)"},
  {"key":"lumentum",   "name":"Lumentum",               "stage":9,"sub":"광엔진",   "country":"US","grade":"High",    "usd":75.0, "opm":None,"nv_exp":35,  "switch_mo":24, "mkt_shr":None,"gen":"Both","cpo":True,"note":"CPO 광엔진 · NVIDIA $20억 전략투자+다년간구매약정 2026.3 · 시리즈A 전환우선주(경영권 보호조항 가능성) · Q3 FY2026 $808M +90%(역대최고) · 그린즈버러 InP팹 인수 2028 +$50억 캐파 · Feynman ELSFP ELS 공급 전환 (1차: Lumentum 10-K·IR)"},
  {"key":"sivers",     "name":"Sivers Photonics",       "stage":9,"sub":"광엔진",   "country":"EU","grade":"Critical","usd":0.13, "opm":None,"nv_exp":30,  "switch_mo":0,  "mkt_shr":100, "gen":"Feynman","cpo":True,"note":"SuperNova ELS(External Light Source) InP DFB 레이저 어레이 단독 공급 · CW-WDM 16파장 1300nm · Ayar Labs TeraPHY OIO의 유일한 광원 공급사 · 시총 ~$130M 소형주(STO:SIVE) · 2025.3 WIN Semi(대만) 외주 파트너십→대만 지정학 노출 · 시총≠중요도 역설의 극단 사례 (Sivers ECOC 2022; OFC 2023; WIN Semi 계약 2025.3)"},
  {"key":"credo",      "name":"Credo Technology",       "stage":9,"sub":"칩",       "country":"US","grade":"",        "usd":35.7, "opm":None,"nv_exp":10,  "switch_mo":18, "mkt_shr":None,"note":"고속 SerDes"},
  {"key":"astera",     "name":"Astera Labs",            "stage":9,"sub":"칩",       "country":"US","grade":"High",    "usd":20.0, "opm":None,"nv_exp":15,  "switch_mo":12, "mkt_shr":None,"gen":"Feynman","note":"CXL/PCIe 스마트 컨트롤러 · Feynman 메모리 풀링(CXL) 핵심 · Q1 2026 매출 $308.4M +93%YoY · Microsoft Azure M-series 실배포 · CXL 4.0 128GT/s 지원 (1차: Astera Labs IR 뉴스룸)"},
  {"key":"ayar",       "name":"Ayar Labs",              "stage":9,"sub":"광엔진",   "country":"US","grade":"High",    "usd":None, "opm":None,"nv_exp":20,  "switch_mo":None,"mkt_shr":None,"gen":"Feynman","cpo":True,"note":"OIO TeraPHY · NVIDIA·AMD·MediaTek 투자 · Series E $500M 기업가치 $37.5억 · ★SiPh기반으로 외부InP레이저 여전히 필요(InP 완전대체 아님) · 상용화 2026~2028 (2차)"},
  {"key":"innolight",  "name":"InnoLight",              "stage":9,"sub":"광모듈",   "country":"CN","grade":"High",    "usd":None, "opm":None,"nv_exp":30,  "switch_mo":12, "mkt_shr":50,  "cpo":True,"note":"NVIDIA 800G의 50%+ 공급 · 2024 $33억 +123% · ★100% 미국산 DSP(Broadcom·Marvell) 의존 · 태국·베트남 생산이전 중 · CPO 전환(2026~2030)으로 구조적 대체 예정 (2차)"},
  {"key":"lattice",    "name":"Lattice Semi",           "stage":9,"sub":"칩",       "country":"US","grade":"",        "usd":10.0, "opm":None,"nv_exp":5,   "switch_mo":12, "mkt_shr":None,"note":"저전력 FPGA"},
  {"key":"viavi",      "name":"Viavi Solutions",        "stage":9,"sub":"광테스트", "country":"US","grade":"",        "usd":2.5,  "opm":None,"nv_exp":5,   "switch_mo":None,"mkt_shr":None,"note":"광학 테스트"},
  {"key":"mellanox",   "name":"Mellanox (NVIDIA子)",    "stage":9,"sub":"칩",       "country":"US","grade":"Critical","usd":None, "opm":None,"nv_exp":100, "switch_mo":None,"mkt_shr":None,"note":"InfiniBand NIC (NVIDIA 완전인수)"},

  # ── Stage 10: 패시브·커넥터·PCB (→ ODM 조립 납품) ───────────────
  {"key":"murata",     "name":"Murata",                 "stage":10,"sub":"패시브",  "country":"JP","grade":"",        "usd":77.0, "opm":None,"nv_exp":5,   "switch_mo":12, "mkt_shr":None,"note":"MLCC·인덕터 세계1위 · NVL72 랙당 MLCC 441,000개($2,500~$4,600) · AI서버급 +15~35% 가격인상 2026.4 (2차)"},
  {"key":"tdk",        "name":"TDK",                    "stage":10,"sub":"패시브",  "country":"JP","grade":"",        "usd":37.5, "opm":None,"nv_exp":4,   "switch_mo":12, "mkt_shr":None,"note":"MLCC·페라이트"},
  {"key":"sem",        "name":"Samsung Electro-M",      "stage":10,"sub":"패시브",  "country":"KR","grade":"",        "usd":None, "opm":None,"nv_exp":4,   "switch_mo":12, "mkt_shr":None,"note":"MLCC"},
  {"key":"yageo",      "name":"Yageo",                  "stage":10,"sub":"패시브",  "country":"TW","grade":"",        "usd":8.0,  "opm":None,"nv_exp":3,   "switch_mo":12, "mkt_shr":None,"note":"저항·커패시터"},
  {"key":"vishay",     "name":"Vishay",                 "stage":10,"sub":"패시브",  "country":"US","grade":"",        "usd":3.2,  "opm":None,"nv_exp":2,   "switch_mo":12, "mkt_shr":None,"note":"저항·다이오드"},
  {"key":"amphenol",   "name":"Amphenol",               "stage":10,"sub":"커넥터",  "country":"US","grade":"High",    "usd":80.0, "opm":26.2,"nv_exp":15,  "switch_mo":0,  "mkt_shr":100, "note":"NVLink spine cartridge 단독설계·공급 · FY2025 $23.1B +52% OPM 26.2% +450bp · IT Datacom Q2 2025 +133%YoY · 커넥터 글로벌 1위 등극 (1차: Amphenol IR)"},
  {"key":"te_conn",    "name":"TE Connectivity",        "stage":10,"sub":"커넥터",  "country":"US","grade":"",        "usd":55.0, "opm":None,"nv_exp":5,   "switch_mo":12, "mkt_shr":None,"note":"고속 커넥터"},
  {"key":"samtec",     "name":"Samtec",                 "stage":10,"sub":"커넥터",  "country":"US","grade":"",        "usd":None, "opm":None,"nv_exp":5,   "switch_mo":12, "mkt_shr":None,"note":"고속 시그널 커넥터 (비상장)"},
  {"key":"molex",      "name":"Molex",                  "stage":10,"sub":"커넥터",  "country":"US","grade":"",        "usd":None, "opm":None,"nv_exp":4,   "switch_mo":12, "mkt_shr":None,"note":"커넥터 (Koch 비상장)"},
  {"key":"ipex",       "name":"I-PEX",                  "stage":10,"sub":"커넥터",  "country":"JP","grade":"",        "usd":None, "opm":None,"nv_exp":3,   "switch_mo":12, "mkt_shr":None,"note":"마이크로 커넥터 (비상장)"},
  {"key":"hirose",     "name":"Hirose Electric",        "stage":10,"sub":"커넥터",  "country":"JP","grade":"",        "usd":4.8,  "opm":None,"nv_exp":3,   "switch_mo":12, "mkt_shr":None,"note":"정밀 커넥터"},
  {"key":"ttm",        "name":"TTM Technologies",       "stage":10,"sub":"PCB",     "country":"US","grade":"",        "usd":2.0,  "opm":None,"nv_exp":8,   "switch_mo":18, "mkt_shr":None,"note":"고복잡 HDI PCB · 18층+ HDI 양산가능사 전세계 10개 미만 · 공급-수요 갭 30% 리드타임 8주 연장 (2차)"},
  {"key":"tripod",     "name":"Tripod Technology",      "stage":10,"sub":"PCB",     "country":"TW","grade":"",        "usd":2.3,  "opm":None,"nv_exp":8,   "switch_mo":18, "mkt_shr":None,"note":"서버 PCB · Q1 2026 역대 최고 (1차: Tripod IR)"},
  {"key":"meiko",      "name":"Meiko Electronics",      "stage":10,"sub":"PCB",     "country":"JP","grade":"",        "usd":1.2,  "opm":None,"nv_exp":5,   "switch_mo":18, "mkt_shr":None,"note":"정밀 PCB"},

  # ── Stage 11: NVIDIA ─────────────────────────────────────────────
  {"key":"nvidia",     "name":"NVIDIA",                 "stage":11,"sub":"통합",    "country":"US","grade":"",        "usd":5316.6,"opm":60.4,"nv_exp":100, "switch_mo":None,"mkt_shr":None,"note":"FY2026 매출 $215.9B +65% · DC 매출 90%+ · GAAP 총이익률 71.1% OPM 62% · R200 GPU ASP ~$55,000 · COGS ~$8,900(ASP의 16%) (1차: NVIDIA 10-K)"},

  # ── Stage 12: ODM조립·전원·냉각·광케이블 ────────────────────────
  {"key":"foxconn",    "name":"Foxconn",                "stage":12,"sub":"ODM",     "country":"TW","grade":"High",    "usd":109.9,"opm":3.2, "nv_exp":30,  "switch_mo":12, "mkt_shr":None,"note":"NVL72 주조립 · FY2025 OPM 3.20%(전년 2.92%) · 고가AI랙이 총이익률 오히려 희석 · ODM 3사 AI서버 75~80% 대만집중=TSMC와 동일 지정학 이중노출 (1차: Foxconn IR)"},
  {"key":"wistron",    "name":"Wistron",                "stage":12,"sub":"ODM",     "country":"TW","grade":"Medium",  "usd":14.1, "opm":None,"nv_exp":20,  "switch_mo":12, "mkt_shr":None,"note":"NVL72 조립 · Q4 2025 총이익률 5.62% 매출 NT$2.19조 +108%YoY · 완성랙 비중 확대로 마진 하락 역설 (1차: Wistron IR)"},
  {"key":"quanta",     "name":"Quanta Computer",        "stage":12,"sub":"ODM",     "country":"TW","grade":"Medium",  "usd":37.7, "opm":None,"nv_exp":20,  "switch_mo":12, "mkt_shr":None,"note":"NVL72 조립 · Q1 2026 매출 역대최고 총이익률 하락 (1차: Quanta IR)"},
  {"key":"celestica",  "name":"Celestica",              "stage":12,"sub":"ODM",     "country":"US","grade":"",        "usd":6.0,  "opm":None,"nv_exp":15,  "switch_mo":12, "mkt_shr":None,"note":"AI 서버 ODM"},
  {"key":"jabil",      "name":"Jabil",                  "stage":12,"sub":"ODM",     "country":"US","grade":"",        "usd":19.0, "opm":None,"nv_exp":10,  "switch_mo":12, "mkt_shr":None,"note":"EMS"},
  {"key":"flex",       "name":"Flex",                   "stage":12,"sub":"ODM",     "country":"US","grade":"",        "usd":10.5, "opm":None,"nv_exp":8,   "switch_mo":12, "mkt_shr":None,"note":"EMS"},
  {"key":"delta",      "name":"Delta Electronics",      "stage":12,"sub":"전원",    "country":"TW","grade":"",        "usd":167.3,"opm":None,"nv_exp":15,  "switch_mo":12, "mkt_shr":None,"note":"서버 PSU 1위"},
  {"key":"vertiv",     "name":"Vertiv",                 "stage":12,"sub":"전원냉각","country":"US","grade":"High",    "usd":124.2,"opm":20.4,"nv_exp":20,  "switch_mo":12, "mkt_shr":None,"note":"FY2025 Adj.OPM 20.4% Q4 23.2% · 총매출 $10.2B · FY2026 가이던스 $13.5~14B · Q4 수주 +252%YoY · Goldman Sachs 液냉 침투율 23%(2024)→57~76%(2026) · AI서버 액냉 핵심 인프라 (1차: Vertiv 8-K)"},
  {"key":"schneider",  "name":"Schneider Electric",     "stage":12,"sub":"전원",    "country":"EU","grade":"",        "usd":173.0,"opm":None,"nv_exp":10,  "switch_mo":12, "mkt_shr":None,"note":"전력배전·EMS · Motivair 지분 75% 인수 $8.5억 (2차)"},
  {"key":"eaton",      "name":"Eaton",                  "stage":12,"sub":"전원",    "country":"EU","grade":"",        "usd":90.0, "opm":None,"nv_exp":8,   "switch_mo":12, "mkt_shr":None,"note":"UPS·전력관리"},
  {"key":"motivair",   "name":"Motivair",               "stage":12,"sub":"냉각",    "country":"US","grade":"",        "usd":None, "opm":None,"nv_exp":15,  "switch_mo":None,"mkt_shr":None,"note":"CDU 액냉 (비상장) · Schneider에 75% 인수"},
  {"key":"asetek",     "name":"Asetek",                 "stage":12,"sub":"냉각",    "country":"EU","grade":"",        "usd":0.3,  "opm":None,"nv_exp":8,   "switch_mo":None,"mkt_shr":None,"note":"서버 액냉"},
  {"key":"coolitsys",  "name":"CoolIT Systems",         "stage":12,"sub":"냉각",    "country":"US","grade":"",        "usd":None, "opm":None,"nv_exp":10,  "switch_mo":None,"mkt_shr":None,"note":"직접액냉 CDU (비상장)"},
  {"key":"abb",        "name":"ABB",                    "stage":12,"sub":"전원",    "country":"EU","grade":"",        "usd":85.0, "opm":None,"nv_exp":5,   "switch_mo":None,"mkt_shr":None,"note":"전력변환"},
  {"key":"corning",    "name":"Corning",                "stage":12,"sub":"광케이블","country":"US","grade":"Medium",  "usd":165.1,"opm":20.2,"nv_exp":10,  "switch_mo":18, "mkt_shr":None,"note":"광섬유 세계1위 · Optical Comms FY2025 $6.27B +35% · Core OPM Q4 20.2%(Springboard 목표 1년 조기) · NVIDIA $32억 계약 Meta $60억 계약 · NVL72 랙=일반서버 대비 광섬유 36배 (1차: Corning IR)"},
  {"key":"sum_fiber",  "name":"Sumitomo Elec (광섬유)", "stage":12,"sub":"광케이블","country":"JP","grade":"",        "usd":52.6, "opm":None,"nv_exp":3,   "switch_mo":18, "mkt_shr":None,"note":"광섬유·광케이블"},
  {"key":"furukawa",   "name":"Furukawa Electric",      "stage":12,"sub":"광케이블","country":"JP","grade":"",        "usd":21.8, "opm":None,"nv_exp":3,   "switch_mo":18, "mkt_shr":None,"note":"광섬유·케이블"},
  {"key":"prysmian",   "name":"Prysmian",               "stage":12,"sub":"광케이블","country":"EU","grade":"",        "usd":49.8, "opm":None,"nv_exp":3,   "switch_mo":18, "mkt_shr":None,"note":"광케이블 유럽1위"},
  {"key":"sanmina",    "name":"Sanmina",                "stage":12,"sub":"ODM",     "country":"US","grade":"",        "usd":2.5,  "opm":None,"nv_exp":5,   "switch_mo":12, "mkt_shr":None,"note":"PCB+조립 통합"},
]

# ── 주요 공급 흐름 ──────────────────────────────────────────────────
FLOWS = [
  ("cn_in","axt","인듐원료"), ("cn_in","sum_elec_inp","인듐원료"), ("dowa","axt","인듐 정련"),
  ("carl_zeiss","asml","EUV 광학계 독점"), ("trumpf","asml","CO₂레이저 독점"), ("cymer","asml","ArF 레이저"),
  ("hamamatsu","disco","SD 레이저 독점"),
  ("ajinomoto","ibiden","ABF필름 95%"),
  ("jsr","tsmc","EUV 포토레지"), ("tok","tsmc","포토레지"), ("entegris","tsmc","오염제어"),
  ("shinetsu_si","tsmc","Si웨이퍼"), ("sumco","tsmc","Si웨이퍼"),
  ("soitec","tower","SOI웨이퍼 1:1"),
  ("asml","tsmc","EUV 독점"), ("asml","samsung_f","EUV"),
  ("tel","tsmc","Track 100%"),
  ("disco","skhynix","그라인딩·다이싱"), ("hanmi","skhynix","TC 본더"), ("advantest","skhynix","HBM 테스트"), ("resonac","skhynix","NCF 필름"),
  ("aixtron","iqe","MOCVD 에피"), ("axt","iqe","InP기판 35%"), ("sum_elec_inp","iqe","InP기판 45%+"),
  ("iqe","coherent","InP 에피웨이퍼"), ("aixtron","coherent","MOCVD 70%+"), ("aixtron","lumentum","MOCVD 70%+"),
  ("ibiden","tsmc","ABF기판"),
  ("skhynix","tsmc","HBM4 주력 70%"), ("micron","tsmc","HBM4 3차 20%"), ("samsung_m","tsmc","HBM4 2차"),
  ("tsmc","marvell","N3P(Ara DSP)"), ("tsmc","broadcom","N3P"),
  ("coherent","nvidia","CPO 광엔진"), ("lumentum","nvidia","CPO 광엔진"),
  ("tower","nvidia","SiPho PIC"), ("marvell","nvidia","광DSP"), ("broadcom","nvidia","PCIe SW"),
  ("tsmc","nvidia","N3P+CoWoS-L"),
  ("cadence","nvidia","EDA"), ("synopsys","nvidia","EDA"), ("arm","nvidia","CPU IP"),
  ("amphenol","nvidia","NVLink 단독"),
  ("nvidia","foxconn","NVL72 조립"), ("nvidia","wistron","NVL72 조립"), ("nvidia","quanta","NVL72 조립"),
]

# ── 투자 흐름 ──────────────────────────────────────────────────────
MONEY = [
  ("nvidia","coherent","$20억(보통주)"),
  ("nvidia","lumentum","$20억(전환우선주)"),
  ("nvidia","ayar","Series E 참여(금액 미공개)"),
  ("nvidia","marvell","$20억"),
]

# 신규 흐름 (F1~F5 연구 기반)
FLOWS += [
  ("soitec","gf","SOI 웨이퍼→TeraPHY"),
  ("gf","ayar","45SPCLO 유일 파운드리"),
  ("sivers","ayar","ELS InP 레이저 단독"),
  ("ayar","nvidia","OIO TeraPHY"),
  ("tsmc_coupe","nvidia","NVLink CPO 스위치"),
  ("astera","nvidia","CXL 컨트롤러"),
]

# ── 출력 ───────────────────────────────────────────────────────────
nodes_out = [{**{k:v for k,v in n.items() if k!="stage"}, "tier":n["stage"]} for n in NODES]
out = {
  "nodes": nodes_out,
  "flows": [{"from":f,"to":t,"label":l} for f,t,l in FLOWS],
  "money": [{"from":f,"to":t,"label":l} for f,t,l in MONEY],
}

with open("scm_nodes.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)

total = len(NODES)
print(f"총 {total}개 노드 · 흐름 {len(FLOWS)}개 · 투자 {len(MONEY)}개")
from collections import Counter
stages = Counter(n["stage"] for n in NODES)
for s in sorted(stages):
    names = [n["name"] for n in NODES if n["stage"]==s]
    opm_nodes = [n for n in NODES if n["stage"]==s and n["opm"] is not None]
    opm_str = f" | OPM확보: {len(opm_nodes)}개" if opm_nodes else ""
    print(f"  Stage {s:2d}: {stages[s]:2d}개{opm_str} — {', '.join(names[:4])}{'…' if len(names)>4 else ''}")
