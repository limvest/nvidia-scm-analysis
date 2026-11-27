// 리포트에서 추출한 검증된 흐름 (출처 표기)
// 자재 흐름 (material): from → to, 라벨, 출처
// 머니플로우 (money): NVIDIA 투자

MATERIAL_FLOWS = [
  // === EUV 노광 체인 ===
  {from:"Carl Zeiss SMT", to:"ASML", label:"광학계 100% 독점", src:"2.4"},
  {from:"Trumpf", to:"ASML", label:"CO₂레이저 100% 독점", src:"2.4"},
  {from:"ASML", to:"TSMC", label:"EUV 100% 독점", src:"ASML IR"},
  // === 실리콘 웨이퍼 → 제조 ===
  {from:"Shin-Etsu", to:"TSMC", label:"실리콘 웨이퍼", src:"2.4"},
  {from:"SUMCO", to:"TSMC", label:"실리콘 웨이퍼", src:"2.4"},
  // === HBM → 패키징 ===
  {from:"SK Hynix", to:"TSMC", label:"HBM4 주력", src:"2.3.3"},
  {from:"Samsung", to:"TSMC", label:"HBM4 2차", src:"2.3.4"},
  {from:"Micron", to:"TSMC", label:"HBM4 3차", src:"2.3.5"},
  // === HBM 후공정 장비 ===
  {from:"Hamamatsu", to:"Disco", label:"SD엔진 단독공급", src:"2.4"},
  {from:"Disco", to:"SK Hynix", label:"그라인딩/다이싱", src:"3.4"},
  {from:"Advantest", to:"SK Hynix", label:"HBM 테스트", src:"3.4"},
  {from:"한미반도체", to:"SK Hynix", label:"TC본더", src:"3.4"},
  {from:"Resonac", to:"SK Hynix", label:"NCF 필름", src:"2.4"},
  // === ABF 기판 ===
  {from:"Ajinomoto", to:"Ibiden", label:"ABF 필름 95%+", src:"2.4"},
  {from:"Ibiden", to:"TSMC", label:"ABF 기판", src:"2.4"},
  // === 최종 제조 → NVIDIA ===
  {from:"TSMC", to:"NVIDIA", label:"N3P+CoWoS-L", src:"2.3"},
  // === CPO 체인 1: InP ===
  {from:"Dowa", to:"AXT", label:"인듐 원료", src:"3A.5"},
  {from:"AXT", to:"IQE", label:"InP기판 35%", src:"3A.1.3"},
  {from:"Sumitomo", to:"IQE", label:"InP기판 45~60%", src:"3A.1.3"},
  {from:"AIXTRON", to:"IQE", label:"MOCVD 에피성장", src:"3A.1.3"},
  {from:"AIXTRON", to:"Coherent", label:"MOCVD 70~90%", src:"3A.5"},
  {from:"AIXTRON", to:"Lumentum", label:"MOCVD 70~90%", src:"3A.5"},
  {from:"IQE", to:"Coherent", label:"InP 에피웨이퍼", src:"3A.1.3"},
  {from:"AXT", to:"Coherent", label:"InP 기판", src:"3A.5"},
  {from:"Sumitomo", to:"Coherent", label:"InP 기판", src:"3A.5"},
  // === CPO 체인 2: SiPho ===
  {from:"Soitec", to:"Tower Semi", label:"SOI 웨이퍼 1:1", src:"3A.5"},
  // === CPO 체인 3: DSP ===
  {from:"TSMC", to:"Marvell", label:"N3P (Ara DSP)", src:"3A.5"},
  // === CPO 합류 → NVIDIA ===
  {from:"Coherent", to:"NVIDIA", label:"CPO 광엔진", src:"3A.2"},
  {from:"Lumentum", to:"NVIDIA", label:"CPO 광엔진", src:"3A.2"},
  {from:"Tower Semi", to:"NVIDIA", label:"SiPho PIC", src:"3A.5"},
  {from:"Marvell", to:"NVIDIA", label:"광 DSP", src:"3A.5"},
  // === EDA → NVIDIA (설계) ===
  {from:"Cadence", to:"NVIDIA", label:"EDA", src:"본문"},
  {from:"Synopsys", to:"NVIDIA", label:"EDA", src:"본문"},
  // === 조립 ===
  {from:"NVIDIA", to:"Foxconn", label:"NVL72 조립", src:"본문"},
  {from:"NVIDIA", to:"Wistron", label:"NVL72 조립", src:"본문"},
  {from:"NVIDIA", to:"Quanta", label:"NVL72 조립", src:"본문"},
];

// 머니플로우 (NVIDIA 투자) — 1차 SEC 공시 검증
MONEY_FLOWS = [
  {from:"NVIDIA", to:"Coherent", amt:"$20억", detail:"7,788,161주 × $256.80", src:"Coherent 8-K 2026.03 [1차]"},
  {from:"NVIDIA", to:"Lumentum", amt:"$20억", detail:"전환우선주", src:"Lumentum 8-K 2026.03 [1차]"},
  {from:"NVIDIA", to:"Ayar Labs", amt:"개별 금액 미공개", detail:"Series E 전체 $5억, 기업가치 $37.5억", src:"Ayar Labs 2026.03.03 [1차]"},
];
