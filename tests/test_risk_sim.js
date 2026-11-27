const fs = require('fs');
const path = require('path');
const RiskSim = require('../risk_sim.js');

const page = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
const scmData = JSON.parse(page.match(/^const DATA = (.*);$/m)[1]);
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
  const opts = {nodeKeys:['tsmc','customer'], flows:[{from:'tsmc',to:'customer'}],
    riskData, activeScenarios:['S1_taiwan_strait'], t:12};
  const cur = RiskSim.simulate(opts);
  const acc = RiskSim.simulate({...opts, reshoringStage:'accelerated'});
  assert(acc.flowCut['tsmc→customer'] < cur.flowCut['tsmc→customer'],
    'T5: accelerated reshoring reduces the residual supply loss');
}

{
  const top = RiskSim.centrality({flows, nodeKeys, riskData, maxT: 26});
  assert(top.length === 10 && top.every((n,i) => !i || top[i-1].score >= n.score),
    'T6: Production ranking is sorted by score');
  for (const node of top){
    const scenarios = {alone:{shock_nodes:{[node.key]:1}, duration_weeks:26}};
    const result = RiskSim.simulate({flows, nodeKeys, riskData:{...riskData,scenarios},
      activeScenarios:['alone'], t:26});
    assert((result.firstNvDown ?? 27) === node.timeToNvDown, 'Ranked downtime: ' + node.key);
  }
  const legacy = require('../scm_nodes.json');
  const oldTop = RiskSim.centrality({flows:legacy.flows,nodeKeys:legacy.nodes.map(n=>n.key),riskData});
  assert(oldTop.some(n=>n.key === 'asml' || n.key === 'tsmc'), 'Original 52-flow regression');
}

{
  const edges = new Set(flows.map(f => f.from + '→' + f.to));
  assert(nodeKeys.length === 187 && edges.size === 922 &&
    nodeKeys.every(k => k in riskData.nodes), 'Production graph and risk inputs match');
  assert(Object.values(riskData.scenarios).every(s =>
    Object.keys(s.shock_flows).every(f => edges.has(f)) &&
    Object.keys(s.shock_nodes).every(k => nodeKeys.includes(k))), 'All scenario targets exist');
}

{
  const opts = {
    nodeKeys: ['supplier', 'partner', 'nvidia'],
    flows: [{from:'supplier',to:'partner'}, {from:'partner',to:'supplier'}, {from:'partner',to:'nvidia'}],
    riskData: {
      default_buffer:1, reshoring_factor:{current_2026:{}},
      nodes:{supplier:{substitution:0}, partner:{substitution:0}},
      scenarios:{shock:{duration_weeks:2, shock_nodes:{supplier:0.8}}}
    },
    activeScenarios:['shock']
  };
  const at = t => RiskSim.simulate({...opts, t});
  assert(Object.keys(at(0).nodeStatus).length === 3 && at(0).nodeStatus.nvidia.status === 'NORMAL',
    'Week zero contains the entire healthy network');
  const two = at(2);
  assert(two.firstNvDown === 2 && two.summary.direct === 1 && two.summary.cascaded === 2,
    'Partial direct shock and full cascade count by origin, including a feedback edge');
  const reversed = RiskSim.simulate({...opts, t:2, nodeKeys:opts.nodeKeys.slice().reverse()});
  assert(opts.nodeKeys.every(k => reversed.nodeStatus[k].status === two.nodeStatus[k].status) &&
    reversed.firstNvDown === two.firstNvDown, 'Cycle results are independent of node order');
  const single = {...opts, flows:[], t:3};
  assert(RiskSim.simulate(single).nodeStatus.supplier.status === 'NORMAL',
    'Direct shock stops after its specified duration');
  const top = RiskSim.centrality({...opts, maxT:3});
  assert(top.find(n => n.key === 'supplier').timeToNvDown === 2 && !top.some(n => n.key === 'nvidia'),
    'Rank upstream suppliers by the exact first NVIDIA downtime');
}

{
  const rows = [...page.matchAll(/^\| \d+ \| [^|]+ \| ([1-5]) \| ([1-5—]) \| ([1-5]) \| ([1-5]) \| (\d+|—) \| (Critical|High|Medium|Low|별도 평가) \|$/gm)];
  assert(rows.length === 45 && rows.every(([,a,b,c,d,score,grade]) => {
    if (b === '—') return score === '—' && grade === '별도 평가';
    const product = a*b*c*d;
    const expected = product >= 400 ? 'Critical' : product >= 200 ? 'High' : product >= 80 ? 'Medium' : 'Low';
    return product === Number(score) && grade === expected;
  }), 'Report matrix products, grade thresholds and unscored demand rows');
}

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail > 0 ? 1 : 0);
