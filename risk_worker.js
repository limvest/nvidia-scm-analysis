// risk_worker.js — Monte Carlo 시뮬레이션 (Web Worker)
importScripts('risk_sim.js');

function gauss(){
  let u=0,v=0;
  while(u===0)u=Math.random();
  while(v===0)v=Math.random();
  return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);
}

function cholesky(A){
  const n = A.length;
  const L = Array.from({length:n},()=>Array(n).fill(0));
  for (let i=0;i<n;i++){
    for (let j=0;j<=i;j++){
      let s=0;
      for (let k=0;k<j;k++) s += L[i][k]*L[j][k];
      if (i===j) L[i][j] = Math.sqrt(Math.max(A[i][i]-s, 0));
      else L[i][j] = L[j][j] === 0 ? 0 : (A[i][j]-s)/L[j][j];
    }
  }
  return L;
}

function normalCdf(x){
  const a1=0.254829592,a2=-0.284496736,a3=1.421413741,a4=-1.453152027,a5=1.061405429,p=0.3275911;
  const sign = x<0?-1:1;
  const ax = Math.abs(x)/Math.sqrt(2);
  const t = 1.0/(1.0 + p*ax);
  const y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*Math.exp(-ax*ax);
  return 0.5*(1.0 + sign*y);
}

function correlatedSample(L){
  const n = L.length;
  const z = Array.from({length:n},()=>gauss());
  const x = Array(n).fill(0);
  for (let i=0;i<n;i++){
    let s=0;
    for (let j=0;j<=i;j++) s += L[i][j]*z[j];
    x[i] = s;
  }
  return x.map(normalCdf);
}

let RUNNING = false;

self.onmessage = (e) => {
  const {cmd, payload} = e.data;
  if (cmd === 'run'){
    RUNNING = true;
    const {flows, nodeKeys, riskData, reshoring, week, useCorrelation, nRuns} = payload;
    const order = riskData.scenario_order;
    const L = useCorrelation ? cholesky(riskData.correlation) : null;
    const probs = order.map(sid => riskData.scenarios[sid].probability_5y);

    const graph = RiskSim.prepareGraph(nodeKeys, flows);
    // Six binary scenarios yield at most 64 distinct deterministic outcomes per run.
    const impacts = new Map();
    const results = [];
    const histBins = 21;
    const histogram = Array(histBins).fill(0);

    for (let i=0;i<nRuns;i++){
      if (!RUNNING) break;
      let uniforms;
      if (L) uniforms = correlatedSample(L);
      else uniforms = order.map(()=>Math.random());

      const active = [];
      for (let s=0;s<order.length;s++){
        if (uniforms[s] < probs[s]) active.push(order[s]);
      }

      const key = active.join('|');
      if (!impacts.has(key)){
        const res = RiskSim.simulate({flows, nodeKeys, graph, riskData, activeScenarios: active, reshoringStage: reshoring, t: week});
        impacts.set(key, res.summary.nvidia_revenue_pct);
      }
      const imp = impacts.get(key);
      results.push(imp);
      const binIdx = Math.min(histBins-1, Math.max(0, Math.floor((-imp)/5)));
      histogram[binIdx]++;

      if (i % 50 === 0){
        self.postMessage({type:'progress', value: Math.round(i/nRuns*100)});
      }
    }

    results.sort((a,b)=>a-b);
    const pct = q => results[Math.floor(results.length*q)] || 0;
    const mean = results.length ? results.reduce((a,b)=>a+b,0)/results.length : 0;

    self.postMessage({
      type: 'done',
      result: {
        p5: pct(0.05),
        p50: pct(0.50),
        p95: pct(0.95),
        mean: Math.round(mean*100)/100,
        histogram,
        n: results.length
      }
    });
    RUNNING = false;
  } else if (cmd === 'stop'){
    RUNNING = false;
  }
};
