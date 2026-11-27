# Node Note Accuracy Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 76개 노드의 `note` 필드를 회사 실제 개요 + SCM 리스크 내용으로 교체한다 — 주식티커만 있거나 Feynman/Rubin SCM 분석 텍스트가 잘못 들어간 케이스 전부.

**Architecture:** 8개 research subagent가 배치별로 병렬 조사 → 각 배치 결과를 JSON 파일로 저장 → Opus 상위 agent가 전체 76개 note 검수 → Python write-back 스크립트가 scm_full.html 업데이트 → index_template.html 동기화 → index.html 재빌드.

**Tech Stack:** Python 3, JSON, WebSearch, Claude Opus (검수), scm_full.html / index_template.html / build_data.py

---

## Note 포맷 스펙

모든 note는 다음 형식을 따른다:

```
[지표/팩트1] · [지표/팩트2] · [지표/팩트3] | [회사 설명 1문장] [NVIDIA SCM 관련성] [리스크]
```

**규칙:**
- `|` 앞: 핵심 수치·사실 3개 (시장점유율, 매출, 고객, 특이사항)
- `|` 뒤: 회사 소개 + NVIDIA 공급망에서의 역할 + 지정학/공급리스크 (총 2-3문장, 200자 이내)
- 전체 note 길이: 100~400자
- 언어: 한국어
- 출처 명시 가능: `(TrendForce 2025)` 등

**좋은 예시:**
```
EUV 리소그래피 장비 세계 유일 공급사 · High-NA EUV 양산 2025년 개시 · 중국에는 EUV 수출 금지 | ASML(네덜란드)은 EUV 리소그래피 장비 세계 유일 공급사(독점). 2025년 기준 시가총액 약 3,600억 달러. TSMC·삼성·SK Hynix 모두 EUV 의존. 네덜란드 수출규제 강화 시 첨단 반도체 공급망 전체 타격.
```

**피해야 할 것:**
- "Vera Rubin NVL72", "GB200", "CoWoS", "Feynman", "Rubin" 등 NVIDIA 제품명이 note 전체를 지배하는 경우
- 해당 회사가 아닌 NVIDIA의 전략을 설명하는 내용
- 주식 티커만 적힌 경우 (`TYO:6920` 등)
- 추측성 내용 ("~할 것으로 예상")

---

## File Structure

```
차트 /
├── scm_full.html                    ← 수정 대상 (DATA.nodes[].note)
├── index_template.html              ← 동기화 대상
├── index.html                       ← 재빌드 출력
├── build_data.py                    ← 재빌드 스크립트 (수정 없음)
└── docs/superpowers/plans/
    ├── 2026-05-23-node-note-accuracy.md   ← 이 파일
    └── note_work/
        ├── audit.json               ← Task 1 출력: 76개 노드 현황
        ├── batch_1_notes.json       ← Task 2 출력
        ├── batch_2_notes.json       ← Task 3 출력
        ├── batch_3_notes.json       ← Task 4 출력
        ├── batch_4_notes.json       ← Task 5 출력
        ├── batch_5_notes.json       ← Task 6 출력
        ├── batch_6_notes.json       ← Task 7 출력
        ├── batch_7_notes.json       ← Task 8 출력
        ├── batch_8_notes.json       ← Task 9 출력
        └── approved_notes.json      ← Task 10 출력 (Opus 검수 완료)
```

---

## Task 1: Audit — 수정 대상 노드 추출 및 배치 파일 생성

**Files:**
- Read: `차트 /scm_full.html`
- Create: `차트 /docs/superpowers/plans/note_work/audit.json`

- [ ] **Step 1: audit.json 생성 스크립트 실행**

```bash
# run from the repo root
python3 - <<'PYEOF'
import re, json, os

with open('scm_full.html', 'r', encoding='utf-8') as f:
    src = f.read()
m = re.search(r'const DATA = ({.*?});\s*\n', src, re.DOTALL)
data = json.loads(m.group(1))

mismatch_keywords = ['Feynman', 'Rubin', 'GB300', 'B300', 'NVL72', 'HBM4', 'CoWoS',
                     'NVIDIA Rubin', 'Vera Rubin', 'GB200', 'NVL', 'Blackwell']

to_fix = []
for n in data['nodes']:
    note = n.get('note') or ''
    if len(note) < 50:
        to_fix.append({'key': n['key'], 'name': n['name'], 'country': n.get('country'),
                       'sub': n.get('sub',''), 'problem': 'ticker_only', 'current_note': note})
    elif any(kw.lower() in note.lower() for kw in mismatch_keywords):
        to_fix.append({'key': n['key'], 'name': n['name'], 'country': n.get('country'),
                       'sub': n.get('sub',''), 'problem': 'mismatch_scm_text',
                       'current_note': note[:200]})

# 배치 할당
batches = [
    ['henkel','namics','soitec','amat','teradyne','asmpt','ibiden','unimicron','cadence','siemens_eda'],
    ['arm','rambus','tsmc','intel_f','gf','tsmc_coupe','skhynix','micron','samsung_m','marvell'],
    ['lumentum','credo','astera','mellanox','vishay','amphenol','samtec','ttm','nvidia','foxconn'],
    ['wistron','schneider','motivair','coolitsys','corning','lasertec','hoya','agc','mitsui_chem','jx_metals'],
    ['asahi_kasei','rohm','taiyo_yuden','nitto_denko','mgc','sumitomo_chem','fujimi','renesas','sk_materials','soulbrain'],
    ['oci_company','dongjin','lg_chem_semi','isc_korea','wonik_ips','koh_young','ase_group','nan_ya_pcb','walsin_tech','chroma_ate'],
    ['wus_pcb','taiwan_mask','powertech_tech','elite_material','asmi','basf_semi','evonik','wacker_chemie','infineon','stmicro'],
    ['nxp','jenoptik','china_re','jiangxi_copper','yunnan_tin','cmoc'],
]
key_to_batch = {}
for i, batch in enumerate(batches):
    for k in batch:
        key_to_batch[k] = i + 1

for item in to_fix:
    item['batch'] = key_to_batch.get(item['key'], 0)

os.makedirs('docs/superpowers/plans/note_work', exist_ok=True)
with open('docs/superpowers/plans/note_work/audit.json', 'w', encoding='utf-8') as f:
    json.dump(to_fix, f, ensure_ascii=False, indent=2)

print(f"audit.json 생성: {len(to_fix)}개 노드")
for i in range(1, 9):
    batch_nodes = [x for x in to_fix if x['batch'] == i]
    print(f"  Batch {i}: {len(batch_nodes)}개 — {[x['key'] for x in batch_nodes]}")
PYEOF
```

Expected output:
```
audit.json 생성: 76개 노드
  Batch 1: 10개 — ['henkel', 'namics', ...]
  ...
```

---

## Tasks 2–9: Research Subagents (배치별 병렬 실행)

**각 Task의 구조는 동일하다. Batch N의 노드들을 웹 검색으로 조사하여 `batch_N_notes.json`을 생성한다.**

### 공통 subagent 프롬프트 구조

각 research subagent는 다음 정보를 제공받는다:
- 배치 내 노드 목록 (key, name, country, sub, current_note)
- Note 포맷 스펙 (위 스펙 전문)
- 출력 형식: JSON 배열

각 subagent가 출력해야 하는 JSON:
```json
[
  {
    "key": "노드키",
    "name": "회사명",
    "proposed_note": "지표1 · 지표2 · 지표3 | 설명...",
    "sources": ["출처1", "출처2"],
    "confidence": "high|medium|low"
  }
]
```

---

### Task 2: Batch 1 Research — 패키징소재·EDA·기판 (EU/JP/US/HK)

노드: `henkel`, `namics`, `soitec`, `amat`, `teradyne`, `asmpt`, `ibiden`, `unimicron`, `cadence`, `siemens_eda`

**Files:**
- Create: `docs/superpowers/plans/note_work/batch_1_notes.json`

- [ ] **Step 1: Research subagent 실행**

subagent에게 전달할 프롬프트:

```
너는 NVIDIA Rubin SCM 분석 프로젝트의 research subagent다.
아래 10개 회사에 대해 웹 검색으로 조사하고, 각 회사의 note를 작성해라.

Note 포맷:
"[지표/팩트1] · [지표/팩트2] · [지표/팩트3] | [회사소개 1문장] [NVIDIA 공급망 역할] [리스크]"
- | 앞: 핵심 수치 3개 (시장점유율, 매출규모, 주요고객, 특허 등)
- | 뒤: 200자 이내 한국어 설명
- Feynman/Rubin/GB200 등 NVIDIA 제품명 위주로 쓰지 말 것 — 회사 자체 설명이 주

회사 목록:
1. henkel (Henkel, DE) — 반도체 패키징 소재(CUF, NCF, 언더필)
2. namics (Namics, JP) — 반도체 패키징 소재(언더필, 봉지재)
3. soitec (Soitec, EU) — SOI 웨이퍼 제조사
4. amat (Applied Materials, US) — 반도체 장비(PVD, CVD, CMP)
5. teradyne (Teradyne, US) — 반도체 테스트 장비
6. asmpt (ASMPT, HK) — 다이본더·와이어본더 후공정 장비
7. ibiden (Ibiden, JP) — ABF 패키지 기판
8. unimicron (Unimicron, TW) — 패키지 기판·PCB
9. cadence (Cadence Design Systems, US) — EDA 소프트웨어
10. siemens_eda (Siemens EDA, EU) — EDA 소프트웨어 (Calibre)

각 회사별로 웹 검색해서 최신 정보(2025-2026) 기준으로 작성할 것.
출력은 JSON 배열로:
[{"key":"henkel","name":"Henkel","proposed_note":"...","sources":["url1"],"confidence":"high"}]
```

- [ ] **Step 2: 결과를 `batch_1_notes.json`으로 저장**

```bash
# subagent 결과를 수동으로 파일에 저장
# 파일 위치: docs/superpowers/plans/note_work/batch_1_notes.json
```

---

### Task 3: Batch 2 Research — IP·파운드리·메모리 (US/TW/KR)

노드: `arm`, `rambus`, `tsmc`, `intel_f`, `gf`, `tsmc_coupe`, `skhynix`, `micron`, `samsung_m`, `marvell`

**Files:**
- Create: `docs/superpowers/plans/note_work/batch_2_notes.json`

- [ ] **Step 1: Research subagent 실행**

```
회사 목록:
1. arm (Arm Holdings, UK/US) — CPU·GPU IP 라이선서
2. rambus (Rambus, US) — 메모리 인터페이스 IP
3. tsmc (TSMC, TW) — 선단 파운드리 (N3/N2)
4. intel_f (Intel Foundry, US) — 18A 파운드리
5. gf (GlobalFoundries, US) — 성숙공정 파운드리 (FD-SOI)
6. tsmc_coupe (TSMC COUPE, TW) — TSMC 첨단패키징(CoWoS/SoIC) 전담
7. skhynix (SK Hynix, KR) — HBM 메모리
8. micron (Micron Technology, US) — HBM·DRAM
9. samsung_m (Samsung Memory, KR) — HBM·DRAM
10. marvell (Marvell Technology, US) — 커스텀 AI ASIC·네트워킹 반도체

Note 포맷 동일. tsmc/skhynix 등 이미 잘 알려진 회사도 회사 자체 정보 중심으로.
```

- [ ] **Step 2: 결과를 `batch_2_notes.json`으로 저장**

---

### Task 4: Batch 3 Research — 광학·인터커넥트·ODM (US)

노드: `lumentum`, `credo`, `astera`, `mellanox`, `vishay`, `amphenol`, `samtec`, `ttm`, `nvidia`, `foxconn`

**Files:**
- Create: `docs/superpowers/plans/note_work/batch_3_notes.json`

- [ ] **Step 1: Research subagent 실행**

```
회사 목록:
1. lumentum (Lumentum, US) — 광트랜시버·CPO 광엔진
2. credo (Credo Technology, US) — AEC 케이블·SerDes IP
3. astera (Astera Labs, US) — CXL·PCIe 스마트 컨트롤러
4. mellanox (Mellanox/NVIDIA, US) — InfiniBand NIC (NVIDIA 자회사)
5. vishay (Vishay, US) — 수동부품(저항·커패시터)
6. amphenol (Amphenol, US) — 고속 커넥터
7. samtec (Samtec, US) — 고속 보드간 커넥터
8. ttm (TTM Technologies, US) — 고다층 PCB
9. nvidia (NVIDIA, US) — AI GPU 설계·공급망 오케스트레이터
10. foxconn (Foxconn, TW) — AI 서버 시스템 통합·ODM

Note: nvidia, foxconn은 NVIDIA SCM에서의 역할 위주로. NVIDIA 제품명(Rubin 등)은 최소화.
```

- [ ] **Step 2: 결과를 `batch_3_notes.json`으로 저장**

---

### Task 5: Batch 4 Research — ODM·냉각·광섬유·JP 소재 (TW/EU/US/JP)

노드: `wistron`, `schneider`, `motivair`, `coolitsys`, `corning`, `lasertec`, `hoya`, `agc`, `mitsui_chem`, `jx_metals`

**Files:**
- Create: `docs/superpowers/plans/note_work/batch_4_notes.json`

- [ ] **Step 1: Research subagent 실행**

```
회사 목록:
1. wistron (Wistron, TW) — AI 서버 ODM
2. schneider (Schneider Electric, EU) — 데이터센터 전력·UPS
3. motivair (Motivair, US) — 액냉 CDU
4. coolitsys (CoolIT Systems, US) — 직접 액냉 모듈
5. corning (Corning, US) — 광섬유 케이블
6. lasertec (Lasertec, JP) — EUV 마스크 검사 장비
7. hoya (Hoya, JP) — EUV 포토마스크·마스크블랭크
8. agc (AGC, JP) — 합성석영·광학유리·반도체 소재
9. mitsui_chem (Mitsui Chemicals, JP) — 반도체 패키징 소재(MRS 필름 등)
10. jx_metals (JX Advanced Metals, JP) — 고순도 구리박·스퍼터링 타깃
```

- [ ] **Step 2: 결과를 `batch_4_notes.json`으로 저장**

---

### Task 6: Batch 5 Research — JP 소재·화학·장비 + KR 특수화학

노드: `asahi_kasei`, `rohm`, `taiyo_yuden`, `nitto_denko`, `mgc`, `sumitomo_chem`, `fujimi`, `renesas`, `sk_materials`, `soulbrain`

**Files:**
- Create: `docs/superpowers/plans/note_work/batch_5_notes.json`

- [ ] **Step 1: Research subagent 실행**

```
회사 목록:
1. asahi_kasei (Asahi Kasei, JP) — 반도체 소재(폴리이미드·SAP용 필름)
2. rohm (Rohm, JP) — SiC 전력반도체·GaN 디바이스
3. taiyo_yuden (Taiyo Yuden, JP) — MLCC·적층 인덕터
4. nitto_denko (Nitto Denko, JP) — 다이싱 테이프·반도체 필름
5. mgc (Mitsubishi Gas Chemical, JP) — BT 수지·과산화수소·마스크블랭크용 기판
6. sumitomo_chem (Sumitomo Chemical, JP) — 포토레지스트 원료·폴리머 소재
7. fujimi (Fujimi, JP) — CMP 슬러리
8. renesas (Renesas Electronics, JP) — MCU·SoC (차량용·산업용)
9. sk_materials (SK Materials, KR) — 반도체 특수가스(NF3, WF6, SF6)
10. soulbrain (Soulbrain Holdings, KR) — 반도체 공정 화학(HF, 에칭액, 전구체)
```

- [ ] **Step 2: 결과를 `batch_5_notes.json`으로 저장**

---

### Task 7: Batch 6 Research — KR 장비·소재 + TW 수동부품·검사

노드: `oci_company`, `dongjin`, `lg_chem_semi`, `isc_korea`, `wonik_ips`, `koh_young`, `ase_group`, `nan_ya_pcb`, `walsin_tech`, `chroma_ate`

**Files:**
- Create: `docs/superpowers/plans/note_work/batch_6_notes.json`

- [ ] **Step 1: Research subagent 실행**

```
회사 목록:
1. oci_company (OCI Company, KR) — 폴리실리콘·반도체 소재
2. dongjin (Dongjin Semichem, KR) — 포토레지스트·화학기계연마액
3. lg_chem_semi (LG Chem 반도체소재, KR) — 폴리이미드·반도체 소재
4. isc_korea (ISC Co., KR) — 러버 소켓(반도체 테스트 소켓)
5. wonik_ips (Wonik IPS, KR) — ALD·CVD 반도체 장비
6. koh_young (Koh Young Technology, KR) — 3D SPI·AOI 검사 장비
7. ase_group (ASE Technology/SPIL, TW) — 반도체 후공정 OSAT
8. nan_ya_pcb (Nan Ya PCB, TW) — 고밀도 PCB
9. walsin_tech (Walsin Technology, TW) — MLCC·저항기 (수동부품)
10. chroma_ate (Chroma ATE, TW) — 반도체·배터리·전력 테스트 장비
```

- [ ] **Step 2: 결과를 `batch_6_notes.json`으로 저장**

---

### Task 8: Batch 7 Research — TW PCB + EU 화학·반도체

노드: `wus_pcb`, `taiwan_mask`, `powertech_tech`, `elite_material`, `asmi`, `basf_semi`, `evonik`, `wacker_chemie`, `infineon`, `stmicro`

**Files:**
- Create: `docs/superpowers/plans/note_work/batch_7_notes.json`

- [ ] **Step 1: Research subagent 실행**

```
회사 목록:
1. wus_pcb (WUS Printed Circuit, TW) — 고밀도 PCB 제조
2. taiwan_mask (Taiwan Mask Corp (TMC), TW) — 포토마스크 제조
3. powertech_tech (Powertech Technology (PTI), TW) — 메모리 패키징 OSAT
4. elite_material (Elite Material (EMC), TW) — CCL(동박적층판) 제조
5. asmi (ASM International, EU) — ALD·에피택시 장비
6. basf_semi (BASF Electronic Materials, EU) — 반도체용 특수화학 (CMP 슬러리, 포토레지스트 원료)
7. evonik (Evonik Industries, EU) — 반도체 소재(고순도 실리카·특수 폴리머)
8. wacker_chemie (Wacker Chemie, EU) — 폴리실리콘·실리콘 웨이퍼 원료
9. infineon (Infineon Technologies, EU) — 전력반도체·MCU·RF
10. stmicro (STMicroelectronics, EU) — 전력반도체·MCU·차량용
```

- [ ] **Step 2: 결과를 `batch_7_notes.json`으로 저장**

---

### Task 9: Batch 8 Research — EU 반도체 + CN 채굴/원자재

노드: `nxp`, `jenoptik`, `china_re`, `jiangxi_copper`, `yunnan_tin`, `cmoc`

**Files:**
- Create: `docs/superpowers/plans/note_work/batch_8_notes.json`

- [ ] **Step 1: Research subagent 실행**

```
회사 목록:
1. nxp (NXP Semiconductors, EU) — 차량용·IoT 반도체
2. jenoptik (Jenoptik, EU) — 반도체 레이저·광학 장비
3. china_re (China Northern Rare Earth, CN) — 희토류 채굴·정련
4. jiangxi_copper (Jiangxi Copper, CN) — 구리 채굴·정련 (세계 최대)
5. yunnan_tin (Yunnan Tin Group, CN) — 주석 채굴·정련 (세계 최대)
6. cmoc (CMOC Group, CN) — 코발트·몰리브덴 채굴 (DR Congo)

CN 기업들은 수출통제·지정학 리스크 중심으로 note 작성.
```

- [ ] **Step 2: 결과를 `batch_8_notes.json`으로 저장**

---

## Task 10: Opus 검수 — 76개 note 일괄 검토

**Files:**
- Read: `docs/superpowers/plans/note_work/batch_1_notes.json` ~ `batch_8_notes.json`
- Create: `docs/superpowers/plans/note_work/approved_notes.json`

- [ ] **Step 1: 모든 배치 결과 병합**

```bash
# run from the repo root
python3 - <<'PYEOF'
import json, os

all_notes = []
for i in range(1, 9):
    path = f'docs/superpowers/plans/note_work/batch_{i}_notes.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            batch = json.load(f)
        all_notes.extend(batch)
        print(f"Batch {i}: {len(batch)}개 로드")
    else:
        print(f"Batch {i}: 파일 없음 — SKIP")

print(f"총 {len(all_notes)}개 note 병합 완료")
with open('docs/superpowers/plans/note_work/merged_notes.json', 'w', encoding='utf-8') as f:
    json.dump(all_notes, f, ensure_ascii=False, indent=2)
PYEOF
```

- [ ] **Step 2: Opus 검수 agent 실행**

Opus agent 프롬프트:
```
너는 NVIDIA Rubin SCM 분석의 최종 검수자다. 모델: claude-opus-4-7.

아래 76개 회사의 proposed_note를 검토하라. 각 note는 해당 회사에 대한 설명이어야 한다.

검수 기준:
1. 회사와 내용 일치 여부 (다른 회사 정보가 섞였는지)
2. 포맷 준수: "[지표] · [지표] · [지표] | [설명]" 구조
3. 사실 오류: 명백히 틀린 수치나 사실
4. 너무 짧음 (<80자) 또는 너무 길음 (>500자)
5. NVIDIA 제품명(Rubin/GB200/Feynman/CoWoS)이 note를 지배하는 경우

출력 형식:
{
  "approved": [{"key":"...", "note":"..."}, ...],
  "flagged": [{"key":"...", "current_note":"...", "issue":"...", "suggested_fix":"..."}, ...]
}

flagged된 항목은 suggested_fix에 수정된 note를 직접 작성해라.
```

- [ ] **Step 3: Opus 결과를 `approved_notes.json`으로 저장**

```bash
# Opus가 출력한 approved + flagged(수정안) 전부를 하나의 JSON으로 병합
python3 - <<'PYEOF'
import json

# Opus 검수 결과 (수동으로 붙여넣기 또는 파일로 저장 후 로드)
with open('docs/superpowers/plans/note_work/opus_review.json', 'r', encoding='utf-8') as f:
    review = json.load(f)

final = {}
for item in review.get('approved', []):
    final[item['key']] = item['note']
for item in review.get('flagged', []):
    if item.get('suggested_fix'):
        final[item['key']] = item['suggested_fix']
    else:
        # suggested_fix 없으면 original 유지 + 경고
        print(f"WARNING: {item['key']} flagged but no fix provided")

with open('docs/superpowers/plans/note_work/approved_notes.json', 'w', encoding='utf-8') as f:
    json.dump(final, f, ensure_ascii=False, indent=2)
print(f"approved_notes.json: {len(final)}개 저장")
PYEOF
```

Expected output:
```
approved_notes.json: 76개 저장
```

---

## Task 11: Write-back — scm_full.html 업데이트 및 최종 빌드

**Files:**
- Modify: `차트 /scm_full.html` (DATA.nodes[].note 업데이트)
- Modify: `차트 /index_template.html` (동기화)
- Modify: `차트 /index.html` (재빌드)

- [ ] **Step 1: scm_full.html note 업데이트**

```bash
# run from the repo root
python3 - <<'PYEOF'
import re, json

with open('scm_full.html', 'r', encoding='utf-8') as f:
    src = f.read()
m = re.search(r'const DATA = ({.*?});\s*\n', src, re.DOTALL)
data = json.loads(m.group(1))

with open('docs/superpowers/plans/note_work/approved_notes.json', 'r', encoding='utf-8') as f:
    approved = json.load(f)

updated = 0
for n in data['nodes']:
    if n['key'] in approved:
        n['note'] = approved[n['key']]
        updated += 1

print(f"업데이트: {updated}개 노드")

new_data_str = json.dumps(data, ensure_ascii=False, separators=(',',':'))
new_src = src[:m.start(1)] + new_data_str + src[m.end(1):]
with open('scm_full.html', 'w', encoding='utf-8') as f:
    f.write(new_src)
print("scm_full.html 저장 완료")
PYEOF
```

Expected output:
```
업데이트: 76개 노드
scm_full.html 저장 완료
```

- [ ] **Step 2: index_template.html 동기화**

```bash
# run from the repo root
python3 - <<'PYEOF'
import re, json

with open('scm_full.html', 'r', encoding='utf-8') as f:
    src = f.read()
with open('index_template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

m_src = re.search(r'const DATA = ({.*?});\s*\n', src, re.DOTALL)
data = json.loads(m_src.group(1))

m_tmpl = re.search(r'const DATA = ({.*?});\s*\n', tmpl, re.DOTALL)
new_data_str = json.dumps(data, ensure_ascii=False, separators=(',',':'))
new_tmpl = tmpl[:m_tmpl.start(1)] + new_data_str + tmpl[m_tmpl.end(1):]

with open('index_template.html', 'w', encoding='utf-8') as f:
    f.write(new_tmpl)
print(f"index_template.html 동기화: {len(data['nodes'])}개 노드, {len(data['flows'])}개 flows")
PYEOF
```

- [ ] **Step 3: index.html 재빌드**

```bash
python3 build_data.py
```

Expected output:
```
Parsing report...
  Sections: 116
Parsing Feynman files...
  Total: 121
Written: .../index.html (XXX KB)
```

- [ ] **Step 4: 최종 검증**

```bash
# run from the repo root
python3 - <<'PYEOF'
import re, json

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'const DATA = ({.*?});\s*\n', content, re.DOTALL)
data = json.loads(m.group(1))

short = [n for n in data['nodes'] if len(n.get('note','')) < 50]
ticker_pattern = ['TYO:','KOSDAQ:','KOSPI:','TWSE:','XETR:','NYSE:','NASDAQ:','SEHK:','SSE:','SZSE:']
still_ticker = [n for n in data['nodes'] if any(p in (n.get('note','')) for p in ticker_pattern)]

mismatch_kw = ['Feynman','GB200','NVL72','Blackwell','Vera Rubin','CoWoS']
still_mismatch = [n for n in data['nodes'] if any(kw in (n.get('note','')) for kw in mismatch_kw)]

print(f"노드 총계: {len(data['nodes'])}")
print(f"여전히 짧음 (<50자): {len(short)}개 — {[n['key'] for n in short]}")
print(f"여전히 티커: {len(still_ticker)}개 — {[n['key'] for n in still_ticker]}")
print(f"여전히 mismatch 키워드: {len(still_mismatch)}개 — {[n['key'] for n in still_mismatch]}")
print("✅ 성공 기준: 모두 0개")
PYEOF
```

Expected output:
```
노드 총계: 187
여전히 짧음 (<50자): 0개 — []
여전히 티커: 0개 — []
여전히 mismatch 키워드: 0개 — []
✅ 성공 기준: 모두 0개
```

---

## Self-Review Checklist

**스펙 커버리지:**
- [x] 76개 노드 전부 배치 할당됨 (8 배치)
- [x] audit.json 생성 (Task 1)
- [x] 8개 research subagent (Tasks 2-9)
- [x] Opus 검수 (Task 10)
- [x] write-back + 재빌드 (Task 11)
- [x] 최종 검증 스크립트 포함

**플레이스홀더 없음:**
- [x] 모든 Python 코드 완전 작성
- [x] 모든 bash 명령어 exact path 포함
- [x] 모든 expected output 명시

**타입 일관성:**
- [x] `approved_notes.json` 형식: `{key: note_string}` dict — Task 10 Step 3과 Task 11 Step 1에서 동일하게 사용
- [x] `batch_N_notes.json` 형식: `[{key, name, proposed_note, sources, confidence}]` 배열
