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

  function topoOrder(nodeKeys, flows){
    const indeg = {}, adj = {};
    nodeKeys.forEach(k => { indeg[k] = 0; adj[k] = []; });
    for (const f of flows){
      if (indeg[f.to] !== undefined && adj[f.from] !== undefined){
        indeg[f.to]++; adj[f.from].push(f.to);
      }
    }
    const q = nodeKeys.filter(k => indeg[k] === 0);
    const order = [];
    while (q.length){
      const k = q.shift();
      order.push(k);
      for (const nb of (adj[k]||[])){
        if (--indeg[nb] === 0) q.push(nb);
      }
    }
    const seen = new Set(order);
    for (const k of nodeKeys) if (!seen.has(k)) order.push(k);
    return order;
  }

  function simulate(opts){
    const {
      flows, nodeKeys, riskData,
      activeScenarios,
      reshoringStage='current_2026',
      t = 12
    } = opts;

    const reshoreFactor = riskData.reshoring_factor[reshoringStage] || {};
    const subOf = k => {
      const base = (riskData.nodes[k] && riskData.nodes[k].substitution) != null ? riskData.nodes[k].substitution : 0.5;
      const f = reshoreFactor[k];
      return f !== undefined ? base * f : base;
    };
    const bufOf = k => (riskData.nodes[k] && riskData.nodes[k].inventory_weeks) || riskData.default_buffer;

    // 시나리오 충격은 영구적인 baseline (직접 통제·사고로 인한 차단 — 시나리오가 켜진 동안 유지됨)
    const baselineFlowCut = {};
    const initialNodeShock = {};

    for (const sid of activeScenarios){
      const s = riskData.scenarios[sid];
      if (!s) continue;
      for (const [nk, v] of Object.entries(s.shock_nodes||{})){
        initialNodeShock[nk] = Math.max(initialNodeShock[nk]||0, v);
      }
      for (const [fk, v] of Object.entries(s.shock_flows||{})){
        baselineFlowCut[fk] = Math.max(baselineFlowCut[fk]||0, v);
      }
    }

    const {incoming, outgoing} = buildFlowIndex(flows);
    const order = topoOrder(nodeKeys, flows);

    const buffer = {};
    nodeKeys.forEach(k => { buffer[k] = bufOf(k); });

    const nodeStatusFinal = {};
    let flowCut = {};   // visible to caller as final week's flowCut
    for (let week = 1; week <= t; week++){
      // 매 주 baseline에서 다시 시작 + 현재 주의 노드 상태로부터 재계산
      flowCut = Object.assign({}, baselineFlowCut);
      for (const k of order){
        const directShock = initialNodeShock[k] || 0;
        const incs = incoming[k] || [];
        let cutScore = directShock;
        if (incs.length > 0){
          let total = 0, weighted = 0, maxCut = 0;
          for (const f of incs){
            const fk = `${f.from}→${f.to}`;
            let c = flowCut[fk] || 0;
            const upState = nodeStatusFinal[f.from] && nodeStatusFinal[f.from].status;
            if (upState === 'DOWN') c = Math.max(c, 1.0 * (1 - subOf(f.from)));
            else if (upState === 'IMPAIRED') c = Math.max(c, 0.5 * (1 - subOf(f.from)));
            flowCut[fk] = c;
            weighted += c;
            total += 1;
            if (c > maxCut) maxCut = c;
          }
          // Hybrid aggregation: a single critical input failure can impair the node,
          // but mean reflects diversification of input sources.
          // Use max for the worst-case single point of failure, with 75% weight,
          // plus mean for the overall pressure with 25% weight.
          const inflowCut = total ? (0.75 * maxCut + 0.25 * (weighted / total)) : 0;
          cutScore = Math.max(cutScore, inflowCut);
        }

        if (cutScore > 0.5){
          buffer[k] = (buffer[k] != null ? buffer[k] : bufOf(k)) - 1;
        } else if (cutScore < 0.1){
          buffer[k] = Math.min(bufOf(k), (buffer[k] != null ? buffer[k] : bufOf(k)) + 0.5);
        }

        let status;
        if (cutScore > 0.5 && buffer[k] <= 0) status = 'DOWN';
        else if (cutScore > 0.5) status = 'AT_RISK';
        else if (cutScore > 0.2) status = 'IMPAIRED';
        else status = 'NORMAL';

        nodeStatusFinal[k] = { status, buffer: buffer[k], cutScore };

        if (status === 'DOWN' || status === 'IMPAIRED'){
          for (const f of outgoing[k] || []){
            const fk = `${f.from}→${f.to}`;
            const propagate = (status === 'DOWN' ? 1.0 : 0.5) * (1 - subOf(k));
            flowCut[fk] = Math.max(flowCut[fk] || 0, propagate);
          }
        }
      }
    }

    const summary = aggregate(nodeStatusFinal, riskData);
    return { nodeStatus: nodeStatusFinal, flowCut, summary };
  }

  function aggregate(nodeStatus, riskData){
    let direct=0, cascaded=0, impaired=0;
    let mcDown=0, mcImpaired=0;
    for (const [k, s] of Object.entries(nodeStatus)){
      const info = riskData.nodes[k] || {};
      const mc = info.usd_b || 0;
      if (s.status === 'DOWN'){
        if (s.cutScore >= 0.95) { direct++; mcDown += mc; }
        else { cascaded++; mcDown += mc; }
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
    const { flows, nodeKeys, riskData, maxT=26 } = opts;
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
      const tmpScenarios = { _tmp: { name:'tmp', shock_nodes:{[k]:1.0}, shock_flows:{}, duration_weeks:maxT, probability_5y:1 } };
      const rdClone = Object.assign({}, riskData, { scenarios: Object.assign({}, riskData.scenarios, tmpScenarios) });

      // Binary search for the smallest t where NVIDIA is DOWN
      // Simpler approach: simulate at increasing t and find first DOWN
      let timeToNvDown = maxT + 1;     // never reaches
      let nvImpactAtMaxT = 0;
      let nvImpactAtMaxThalf = 0;
      // Check at t=4, 8, 12, 18, 26 to find earliest NVIDIA DOWN
      const checkpoints = [4, 8, 12, 18, 26];
      for (const ct of checkpoints){
        if (ct > maxT) break;
        const res = simulate({flows, nodeKeys, riskData: rdClone, activeScenarios:['_tmp'], t: ct});
        const nv = res.nodeStatus['nvidia'] && res.nodeStatus['nvidia'].status;
        const impact = Math.abs(res.summary.nvidia_revenue_pct);
        if (ct === maxT) nvImpactAtMaxT = impact;
        if (ct === 12) nvImpactAtMaxThalf = impact;
        if ((nv === 'DOWN' || res.nodeStatus['tsmc'] && res.nodeStatus['tsmc'].status === 'DOWN') && timeToNvDown > ct){
          timeToNvDown = ct;
        }
      }

      // Score: fastest impact dominates, with structural and reach as tie-breakers
      // - timeToNvDown=4 → speed=100
      // - timeToNvDown=8 → speed=70
      // - timeToNvDown=12 → speed=50
      // - timeToNvDown=18 → speed=30
      // - timeToNvDown=26 → speed=15
      // - never → speed=0
      const speedMap = {4:100, 8:70, 12:50, 18:30, 26:15};
      const speed = speedMap[timeToNvDown] !== undefined ? speedMap[timeToNvDown] : 0;
      const sub = (riskData.nodes[k] && riskData.nodes[k].substitution) || 0;
      const reach = downstreamReach(k);

      // Composite: speed dominates (×1000), then structural (sub × reach), then absolute impact
      const score = speed * 1000 + sub * Math.min(reach, 30) * 10 + nvImpactAtMaxT;

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

  return { simulate, centrality, buildFlowIndex, topoOrder };
}));
