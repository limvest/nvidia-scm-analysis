// risk_sim.js — 단일 시점 propagation 엔진 (Node + browser 양립)
(function(root, factory){
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.RiskSim = factory();
}(typeof self !== 'undefined' ? self : this, function(){

  function buildFlowIndex(flows){
    const incoming = {}, outgoing = {};
    for (const f of flows){
      (incoming[f.to] = incoming[f.to] || []).push(f);
      (outgoing[f.from] = outgoing[f.from] || []).push(f);
    }
    return {incoming, outgoing};
  }

  // Order strongly connected components upstream first. Inside a feedback loop,
  // use last week's supply so results do not depend on JSON insertion order.
  function prepareGraph(nodeKeys, flows){
    const {incoming, outgoing} = buildFlowIndex(flows);
    const visited = new Set(), finished = [];
    function visit(key){
      if (visited.has(key)) return;
      visited.add(key);
      for (const edge of outgoing[key] || []) visit(edge.to);
      finished.push(key);
    }
    nodeKeys.forEach(visit);
    const component = new Map(), order = [];
    function collect(key, id){
      if (component.has(key)) return;
      component.set(key, id);
      order.push(key);
      for (const edge of incoming[key] || []) collect(edge.from, id);
    }
    finished.reverse().forEach(key => collect(key, key));
    const inputs = {};
    for (const key of order){
      inputs[key] = (incoming[key] || []).map(f => ({
        key: f.from + '→' + key, from: f.from,
        delayed: component.get(key) === component.get(f.from)
      }));
    }
    return {order, inputs};
  }

  function topoOrder(nodeKeys, flows){
    return prepareGraph(nodeKeys, flows).order;
  }

  function simulate(opts){
    const {flows, nodeKeys, riskData, activeScenarios, t = 12,
      reshoringStage = 'current_2026'} = opts;
    const {order, inputs} = opts.graph || prepareGraph(nodeKeys, flows);
    const factors = riskData.reshoring_factor[reshoringStage] || {};
    const scenarios = activeScenarios.map(id => riskData.scenarios[id]).filter(Boolean);
    const inventories = {}, residual = {};
    let nodeStatus = {}, supply = {}, flowCut = {}, directShock = {};
    let firstNvDown = null;
    for (const key of order){
      const info = riskData.nodes[key] || {};
      inventories[key] = info.inventory_weeks ?? riskData.default_buffer;
      residual[key] = (1 - (info.substitution ?? 0.5)) * (factors[key] ?? 1);
      nodeStatus[key] = {status: 'NORMAL', buffer: inventories[key], cutScore: 0};
    }
    for (let week = 1; week <= t; week++){
      const previous = supply;
      supply = {};
      directShock = {};
      flowCut = {};
      for (const scenario of scenarios){
        if (week > scenario.duration_weeks) continue;
        for (const [key, cut] of Object.entries(scenario.shock_nodes || {})){
          directShock[key] = Math.max(directShock[key] || 0, cut);
        }
        for (const [key, cut] of Object.entries(scenario.shock_flows || {})){
          flowCut[key] = Math.max(flowCut[key] || 0, cut);
        }
      }
      for (const key of order){
        const edges = inputs[key];
        let total = 0, worst = 0;
        for (const edge of edges){
          const upstream = edge.delayed ? previous : supply;
          const cut = Math.max(flowCut[edge.key] || 0, upstream[edge.from] || 0);
          flowCut[edge.key] = cut;
          total += cut;
          worst = Math.max(worst, cut);
        }
        const inflow = edges.length ? 0.75 * worst + 0.25 * total / edges.length : 0;
        const cutScore = Math.max(directShock[key] || 0, inflow);
        let buffer = nodeStatus[key].buffer;
        if (cutScore > 0.5) buffer = Math.max(0, buffer - 1);
        else if (cutScore < 0.1) buffer = Math.min(inventories[key], buffer + 0.5);

        let status = 'NORMAL';
        if (cutScore > 0.5) status = buffer === 0 ? 'DOWN' : 'AT_RISK';
        else if (cutScore > 0.2) status = 'IMPAIRED';
        nodeStatus[key] = {status, buffer, cutScore};
        if (status === 'DOWN') supply[key] = residual[key];
        else if (status === 'IMPAIRED') supply[key] = 0.5 * residual[key];
      }
      if (firstNvDown === null && nodeStatus.nvidia?.status === 'DOWN') firstNvDown = week;
    }
    return {nodeStatus, flowCut, firstNvDown, summary: aggregate(nodeStatus, riskData, directShock)};
  }

  function aggregate(nodeStatus, riskData, directShock){
    let direct=0, cascaded=0, impaired=0;
    let mcDown=0, mcImpaired=0;
    for (const [k, s] of Object.entries(nodeStatus)){
      const info = riskData.nodes[k] || {};
      const mc = info.usd_b || 0;
      if (s.status === 'DOWN'){
        if ((directShock[k] || 0) > 0.5) direct++;
        else cascaded++;
        mcDown += mc;
      } else if (s.status === 'IMPAIRED'){
        impaired++; mcImpaired += mc;
      }
    }
    const nv = nodeStatus['nvidia'] && nodeStatus['nvidia'].status;
    const tsmc = nodeStatus['tsmc'] && nodeStatus['tsmc'].status;
    const cohState = nodeStatus['coherent'] && nodeStatus['coherent'].status;
    const lumState = nodeStatus['lumentum'] && nodeStatus['lumentum'].status;
    let revImpact = 0;
    if (nv === 'DOWN' || tsmc === 'DOWN') revImpact = -100;
    else if (tsmc === 'IMPAIRED') revImpact = -50;
    else if (cohState === 'DOWN' || lumState === 'DOWN') revImpact = -15;
    else if (cohState === 'IMPAIRED' || lumState === 'IMPAIRED') revImpact = -8;
    return {
      direct, cascaded, impaired,
      marketcap_down_b: Math.round(mcDown*10)/10,
      marketcap_impaired_b: Math.round(mcImpaired*10)/10,
      nvidia_revenue_pct: revImpact
    };
  }

  function centrality(opts){
    const { flows, nodeKeys, riskData, maxT=26, reshoringStage='current_2026' } = opts;
    const graph = prepareGraph(nodeKeys, flows);
    // Precompute downstream reach (BFS) for tie-breaking only
    const outAdj = {};
    flows.forEach(f => { (outAdj[f.from] = outAdj[f.from] || []).push(f.to); });
    function downstreamReach(seed){
      const seen = new Set([seed]);
      const q = [seed];
      while (q.length){
        const n = q.shift();
        for (const nb of (outAdj[n]||[])){
          if (!seen.has(nb)){ seen.add(nb); q.push(nb); }
        }
      }
      return seen.size - 1;
    }

    // For each node, find time-to-NVIDIA-DOWN (lower = more critical)
    const scores = [];
    for (const k of nodeKeys){
      if (k === 'nvidia') continue;
      const tmpScenarios = { _tmp: { name:'tmp', shock_nodes:{[k]:1.0}, shock_flows:{}, duration_weeks:maxT, probability_5y:1 } };
      const rdClone = Object.assign({}, riskData, { scenarios: Object.assign({}, riskData.scenarios, tmpScenarios) });

      const result = simulate({flows, nodeKeys, graph, riskData: rdClone,
        activeScenarios: ['_tmp'], t: maxT, reshoringStage});
      const timeToNvDown = result.firstNvDown ?? maxT + 1;
      const speed = maxT + 1 - timeToNvDown;
      const nvImpactAtMaxT = Math.abs(result.summary.nvidia_revenue_pct);
      const sub = riskData.nodes[k]?.substitution ?? 0.5;
      const reach = downstreamReach(k);
      const score = speed * 1000 + (1 - sub) * Math.min(reach, 30) * 10 + nvImpactAtMaxT;

      scores.push({
        key: k,
        name: (riskData.nodes[k] && riskData.nodes[k].name) || k,
        score: Math.round(score * 10) / 10,
        timeToNvDown,
        speed,
        impactAtMaxT: nvImpactAtMaxT,
        substitution: sub,
        downstreamReach: reach
      });
    }

    scores.sort((a,b) => b.score - a.score);
    return scores.slice(0, 10);
  }

  return { simulate, centrality, buildFlowIndex, topoOrder, prepareGraph };
}));
