const fs = require('fs');
const path = require('path');
const RiskSim = require('../risk_sim.js');

const scmData = JSON.parse(fs.readFileSync(path.join(__dirname,'../scm_nodes.json'),'utf8'));
const riskData = JSON.parse(fs.readFileSync(path.join(__dirname,'../risk_data.json'),'utf8'));

const flows = scmData.flows;
const nodeKeys = scmData.nodes.map(n=>n.key);

let pass = 0, fail = 0;
function assert(cond, msg){
  if (cond){ pass++; console.log('PASS', msg); }
  else { fail++; console.log('FAIL', msg); }
}

{
  const r = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:[], t:12});
  const allNormal = Object.values(r.nodeStatus).every(s=>s.status==='NORMAL');
  assert(allNormal, 'T1: 시나리오 0개 -> 전부 NORMAL');
}

{
  const r = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S1_taiwan_strait'], t:12});
  assert(r.nodeStatus['tsmc'].status === 'DOWN', 'T2: S1@W12 -> TSMC=DOWN');
  assert(r.nodeStatus['nvidia'].status === 'DOWN' || r.summary.nvidia_revenue_pct <= -50,
    'T2b: S1@W12 -> NVIDIA major impact');
}

{
  const r = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S2_china_indium'], t:12});
  const axt = r.nodeStatus['axt'].status;
  assert(axt === 'IMPAIRED' || axt === 'DOWN' || axt === 'AT_RISK',
    'T3: S2@W12 -> AXT degraded (got ' + axt + ')');
}

{
  const r = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S4_aixtron_shock'], t:26});
  assert(r.nodeStatus['aixtron'].status === 'DOWN', 'T4: S4@W26 -> AIXTRON=DOWN');
  const iqe = r.nodeStatus['iqe'].status;
  assert(iqe !== 'NORMAL', 'T4b: S4@W26 -> IQE impacted (got ' + iqe + ')');
}

{
  // Use S5 at W6 so TSMC is still IMPAIRED (not DOWN), making reshoring matter
  const cur = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S5_japan_export'], t:6, reshoringStage:'current_2026'});
  const acc = RiskSim.simulate({flows, nodeKeys, riskData, activeScenarios:['S5_japan_export'], t:6, reshoringStage:'accelerated'});
  // Accelerated reshoring should reduce downstream cascade hits OR improve NVIDIA impact
  const curHits = cur.summary.direct + cur.summary.cascaded + cur.summary.impaired;
  const accHits = acc.summary.direct + acc.summary.cascaded + acc.summary.impaired;
  assert(accHits <= curHits || acc.summary.nvidia_revenue_pct >= cur.summary.nvidia_revenue_pct,
    'T5: accelerated reshoring 완화 (cur hits=' + curHits + ' nv=' + cur.summary.nvidia_revenue_pct + ' | acc hits=' + accHits + ' nv=' + acc.summary.nvidia_revenue_pct + ')');
}

{
  const top = RiskSim.centrality({flows, nodeKeys, riskData, maxT: 26});
  const keys = top.map(x=>x.key);
  assert(keys.includes('asml') || keys.includes('tsmc'),
    'T6: Centrality Top 10에 asml/tsmc 포함 (' + keys.join(',') + ')');
}

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail > 0 ? 1 : 0);
