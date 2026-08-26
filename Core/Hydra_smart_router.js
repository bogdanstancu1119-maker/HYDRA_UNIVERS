class HydraSmartRouter {
  constructor(providers, opts = {}) {
    this.opts = { timeoutMs: opts.timeoutMs || 8000, persistKey: opts.persistKey || 'hydra_router_state' };
    this.providers = providers.map(p => ({
      id: p.id, endpoint: p.endpoint, weight: p.weight || 1,
      maxPerMinute: p.maxPerMinute || 60, cooldownMs: p.cooldownMs || 300000,
      requestLog: [], cooldownUntil: 0, failures: 0, avgLatency: 0
    }));
    this._loadState();
  }

  _cleanLogs(p) {
    const now = Date.now();
    p.requestLog = p.requestLog.filter(ts => now - ts < 60000);
  }

  _loadState() {
    try {
      const s = JSON.parse(localStorage?.getItem(this.opts.persistKey) || 'null');
      if (s) this.providers.forEach(p => {
        const old = s.find(o => o.id === p.id);
        if (old) { p.cooldownUntil = old.cooldownUntil; p.requestLog = old.requestLog || []; }
      });
    } catch {}
  }

  _saveState() {
    try {
      const toSave = this.providers.map(p => ({ id: p.id, cooldownUntil: p.cooldownUntil, requestLog: p.requestLog }));
      localStorage?.setItem(this.opts.persistKey, JSON.stringify(toSave));
    } catch {}
  }

  selectProvider() {
    const now = Date.now();
    const healthy = this.providers.filter(p => {
      this._cleanLogs(p);
      return now >= p.cooldownUntil && p.requestLog.length < p.maxPerMinute;
    });

    if (!healthy.length) throw new Error("HYDRA: Toate în cooldown/quota");

    // Load factor + latență - alege cel mai liber și rapid
    healthy.sort((a, b) => {
      const loadA = (a.requestLog.length / a.weight) + (a.avgLatency / 1000);
      const loadB = (b.requestLog.length / b.weight) + (b.avgLatency / 1000);
      return loadA - loadB;
    });

    return healthy[0];
  }

  async execute(payload, retry = 0) {
    const tried = new Set();
    while (tried.size < this.providers.length) {
      let provider;
      try { provider = this.selectProvider(); } catch (e) { throw e; }
      if (tried.has(provider.id)) continue;
      tried.add(provider.id);

      const start = Date.now();
      provider.requestLog.push(start);
      this._saveState();

      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), this.opts.timeoutMs);

      try {
        const res = await fetch(provider.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Hydra-Source': 'Base44-Router',
            'Authorization': `Bearer ${process.env['TOKEN_'+provider.id.toUpperCase()] || ''}`.trim()
          },
          body: JSON.stringify(payload),
          signal: controller.signal
        });

        clearTimeout(timer);
        const latency = Date.now() - start;
        provider.avgLatency = provider.avgLatency? (provider.avgLatency*0.7 + latency*0.3) : latency;

        if (res.status === 429 || res.status === 503) {
          provider.cooldownUntil = Date.now() + provider.cooldownMs * (1 + retry);
          provider.failures++;
          continue;
        }

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        provider.failures = 0;
        return { executedOn: provider.id, latency, data: await res.json() };

      } catch (err) {
        clearTimeout(timer);
        provider.cooldownUntil = Date.now() + provider.cooldownMs;
        provider.failures++;
        // continuă pe următoarea platformă
      }
    }
    throw new Error("HYDRA: Failover epuizat");
  }

  getStats() {
    return this.providers.map(p => ({
      id: p.id, load: p.requestLog.length, cooling: Date.now() < p.cooldownUntil,
      failures: p.failures, avgLatency: Math.round(p.avgLatency)
    }));
  }
    }
