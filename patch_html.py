import json, re

# Load new v3 data
with open("scm_nodes.json", encoding="utf-8") as f:
    data = json.load(f)

data_js = "const DATA = " + json.dumps(data, ensure_ascii=False) + ";"

with open("scm_full.html", encoding="utf-8") as f:
    html = f.read()

# 1. Replace const DATA block
html = re.sub(r'const DATA = \{.*?\};', data_js, html, flags=re.DOTALL)

# 2. Update detail panel HTML — add new rows after d-usd
old_detail = '''  <div class="drow">시가총액: <span id="d-usd"></span></div>
  <div class="dnote" id="d-note"></div>'''
new_detail = '''  <div class="drow">시가총액: <span id="d-usd"></span></div>
  <div class="drow" id="d-opm-row" style="display:none">OPM: <span id="d-opm"></span></div>
  <div class="drow" id="d-exp-row" style="display:none">NV 매출노출: <span id="d-exp"></span></div>
  <div class="drow" id="d-sw-row" style="display:none">전환비용: <span id="d-sw"></span></div>
  <div class="drow" id="d-ms-row" style="display:none">핵심 시장점유율: <span id="d-ms"></span></div>
  <div class="dnote" id="d-note"></div>'''
html = html.replace(old_detail, new_detail)

# 3. Add OPM filter button in header — after the search input
old_search = '''  <input id="search" placeholder="🔍 검색…">
  <span id="count"></span>'''
new_search = '''  <input id="search" placeholder="🔍 검색…">
  <button id="opm-btn" class="fb on" style="background:#8B5CF6;color:#fff;border:none;padding:3px 8px;border-radius:4px;cursor:pointer;font-size:10px">OPM 30%+ 독점</button>
  <span id="count"></span>'''
html = html.replace(old_search, new_search)

# 4. Update shownG/shownC init — add opmOnly filter var after them
old_filter_init = "let shownG=new Set(['Critical','High','Medium','']),shownC=new Set(['JP','KR','TW','NL','US','EU','CN','Other']),srch='';"
new_filter_init = "let shownG=new Set(['Critical','High','Medium','']),shownC=new Set(['JP','KR','TW','NL','US','EU','CN','Other']),srch='',opmOnly=false;"
html = html.replace(old_filter_init, new_filter_init)

# 5. Update vis() function to include opmOnly
old_vis = "function vis(n){return shownG.has(n.grade)&&shownC.has(nc(n.country))&&(!srch||n.name.toLowerCase().includes(srch)||n.note.toLowerCase().includes(srch))}"
new_vis = "function vis(n){return shownG.has(n.grade)&&shownC.has(nc(n.country))&&(!srch||n.name.toLowerCase().includes(srch)||n.note.toLowerCase().includes(srch))&&(!opmOnly||n.opm>=30)}"
html = html.replace(old_vis, new_vis)

# 6. Update showDetail to populate new fields
old_show = """  document.getElementById('d-usd').textContent=us||'비상장 / 추정불가';
  document.getElementById('d-note').textContent=n.note;"""
new_show = """  document.getElementById('d-usd').textContent=us||'비상장 / 추정불가';
  const opmRow=document.getElementById('d-opm-row');
  if(n.opm!=null){opmRow.style.display='';document.getElementById('d-opm').textContent=n.opm+'%'}else{opmRow.style.display='none'}
  const expRow=document.getElementById('d-exp-row');
  if(n.nv_exp!=null){expRow.style.display='';document.getElementById('d-exp').textContent=n.nv_exp+'%'}else{expRow.style.display='none'}
  const swRow=document.getElementById('d-sw-row');
  if(n.switch_mo!=null){swRow.style.display='';document.getElementById('d-sw').textContent=n.switch_mo===0?'교체 불가':n.switch_mo+'개월'}else{swRow.style.display='none'}
  const msRow=document.getElementById('d-ms-row');
  if(n.mkt_shr!=null){msRow.style.display='';document.getElementById('d-ms').textContent=n.mkt_shr+'%'}else{msRow.style.display='none'}
  document.getElementById('d-note').textContent=n.note;"""
html = html.replace(old_show, new_show)

# 7. Add OPM button event listener before render()
old_render_call = "document.getElementById('search').addEventListener('input',e=>{srch=e.target.value.trim().toLowerCase();render()});"
new_render_call = """document.getElementById('search').addEventListener('input',e=>{srch=e.target.value.trim().toLowerCase();render()});
document.getElementById('opm-btn').addEventListener('click',()=>{
  opmOnly=!opmOnly;
  document.getElementById('opm-btn').style.opacity=opmOnly?'1':'0.45';
  render();
});"""
html = html.replace(old_render_call, new_render_call)

with open("scm_full_legacy.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Done. Verifying...")
# Quick verify
with open("scm_full_legacy.html", encoding="utf-8") as f:
    h2 = f.read()
nodes_count = h2.count('"key":')
print(f"  key count in HTML: {nodes_count}")
print(f"  opm field present: {'\"opm\"' in h2}")
print(f"  opm-btn present: {'opm-btn' in h2}")
print(f"  d-opm-row present: {'d-opm-row' in h2}")
