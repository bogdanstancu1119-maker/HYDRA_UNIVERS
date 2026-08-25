// HYDRA V4.1 - Resource Governor - Nu mai atinge Base44 pentru taskuri grele
class HydraGovernor {
  constructor() {
    // Config din Secrets - nu hardcodat
    this.clouds = {
      base44: { weight: 1, maxPerHour: 20, cost: 10, role: 'orchestrator_only', current: 0 },
      cloudflare:{ weight: 5, maxPerHour: 1000, cost: 1, role: 'edge_router', current: 0 },
      vercel: { weight: 5, maxPerHour: 500, cost: 1, role: 'edge_router', current: 0 },
      fly: { weight: 4, maxPerHour: 300, cost: 2, role: 'persistent_worker', current: 0 },
      deno: { weight: 3, maxPerHour: 200, cost: 2, role: 'backup', current: 0 },
      yandex: { weight: 10, maxPerHour: 10000, cost: 0, role: 'agent_creator_research', current: 0 },
      alibaba: { weight: 10, maxPerHour: 10000, cost: 0, role: 'agent_creator_research', current: 0 }
    };
    this.lastReset = Date.now();
  }

  _resetIfHour() {
    if (Date.now() - this.lastReset > 3600000) {
      Object.values(this.clouds).forEach(c => c.current = 0);
      this.lastReset = Date.now();
    }
  }

  // ALEGEREA CORECTA - aici salvezi Base44
  selectCloudFor(taskType) {
    this._resetIfHour();

    // REGULA DE AUR:
    // Base44 face DOAR decizia (10ms), nu execuția
    if (taskType === 'orchestrate') return 'base44';

    // Taskuri grele -> DOAR Ali si Yandex
    if (['create_agent', 'research', 'deploy', 'llm_heavy', 'image_gen'].includes(taskType)) {
      const candidates = ['yandex', 'alibaba']
       .map(id => ({ id,...this.clouds[id] }))
       .filter(c => c.current < c.maxPerHour)
       .sort((a,b) => (a.current/a.weight) - (b.current/b.weight));
      return candidates[0]?.id || 'yandex'; // fallback Yandex
    }

    // Taskuri usoare -> Edge (Cloudflare, Vercel, Fly)
    const edge = ['cloudflare','vercel','fly','deno']
     .map(id => ({ id,...this.clouds[id] }))
     .filter(c => c.current < c.maxPerHour)
     .sort((a,b) => (a.current/b.weight) - (b.current/b.weight));

    return edge[0]?.id || 'cloudflare';
  }

  async execute(task) {
    const cloudId = this.selectCloudFor(task.type);
    const cloud = this.clouds[cloudId];
    cloud.current++;

    console.log(`[HYDRA] ${task.type} -> ${cloudId} (${cloud.role}) [${cloud.current}/${cloud.maxPerHour}]`);

    // Routing real
    const endpoints = {
      yandex: process.env.YANDEX_FUNCTION_URL,
      alibaba: process.env.ALIBABA_FC_URL,
      cloudflare: process.env.CF_WORKER_URL,
      vercel: 'https://hydrapsie.vercel.app/api/exec',
      fly: 'https://hydra-u.fly.dev/exec',
      base44: 'self' // executa local doar orchestrarea
    };

    if (cloudId === 'base44') {
      return { routedTo: 'base44', note: 'doar decizie, 0 credite consumate' };
    }

    return fetch(endpoints[cloudId], {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Task-Type': task.type },
      body: JSON.stringify(task)
    }).then(r => r.json());
  }

  getStats() {
    return Object.entries(this.clouds).map(([id,c]) => ({
      id, role: c.role, used: `${c.current}/${c.maxPerHour}`,
      percent: Math.round(c.current/c.maxPerHour*100)+'%',
      cost: c.cost
    }));
  }
}

// EXEMPLU CUM FOLOSESTI IN Base44 - 3 linii:
const gov = new HydraGovernor();

// In loc de: await heavyAgentCreation()
// Faci:
await gov.execute({ type: 'create_agent', payload: { name: 'researcher_01', task: 'cauta X' } });
await gov.execute({ type: 'research', payload: { query: 'Yandex AI docs' } });
await gov.execute({ type: 'orchestrate', payload: { check: 'queue' } }); // doar asta ramane pe Base44

console.table(gov.getStats());
