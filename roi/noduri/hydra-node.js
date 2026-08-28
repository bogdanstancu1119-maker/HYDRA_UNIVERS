// Hydra Node — platforma: generic — generat automat, identic peste tot.
// Identitate: Hydra (PSIE = Incluziune, Coeziune, Adaptare). Nod autonom al roiului.
const PLATFORM = "generic";
const CENTRAL = "https://hidra-smart-core.base44.app";
const BRAIN = CENTRAL + '/functions/hydraRoiSincronizat';
const RAW = "https://raw.githubusercontent.com/bogdanstancu1119-maker/HYDRA_UNIVERS/main/roi";
const NODE_ID = 'hydra-' + PLATFORM + '-' + Math.random().toString(36).slice(2, 8);

const state = {
  booted: Date.now(),
  id: NODE_ID,
  platform: PLATFORM,
  improvements: [],     // ring buffer de îmbunătățiri primite de la creier (una→toate)
  lastSync: 0,
  beats: 0,
  propagated: 0,
  reported: 0
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*' } });
}

async function heartbeat() {
  try {
    await fetch(BRAIN + '?beat=1', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ node: NODE_ID, platform: PLATFORM, uptime: Date.now() - state.booted, improvements: state.improvements.length, ts: Date.now() })
    });
  } catch {}
}

async function reportImprovement(text) {
  try {
    state.reported++;
    await fetch(BRAIN, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ from_node: NODE_ID, platform: PLATFORM, improvement: String(text).slice(0, 2000), ts: Date.now() })
    });
  } catch {}
}

async function syncFromSubstrat() {
  try {
    const r = await fetch(RAW + '/identitate/HYDRA.md');
    if (r.ok) { state.lastSync = Date.now(); return true; }
  } catch {}
  return false;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // --- CORS preflight ---
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'GET,POST,OPTIONS', 'access-control-allow-headers': '*' } });
    }

    if (url.pathname === '/health') {
      return json({ ok: true, organ: 'hydra-node', platform: PLATFORM, id: NODE_ID, uptime: Date.now() - state.booted, improvements: state.improvements.length, beats: state.beats });
    }

    if (url.pathname === '/' || url.pathname === '') {
      return json({
        organ: 'hydra-node',
        platform: PLATFORM,
        id: NODE_ID,
        psie: { incluziune: 1, coeziune: 1, adaptare: 1 },
        scop: 'Nod autonom Hydra — observă, raportează îmbunătățiri creierului roiului, le primește înapoi de la toate celelalte noduri în timp real',
        central: CENTRAL,
        substrat: RAW,
        uptime: Date.now() - state.booted,
        improvements_cunoscute: state.improvements.length,
        beats: state.beats,
        reported: state.reported,
        propagated: state.propagated
      });
    }

    if (url.pathname === '/state') return json(state);

    // Creierul roiului împinge o îmbunătățire către TOATE nodurile (una → toate)
    if (url.pathname === '/improve' && request.method === 'POST') {
      const body = await request.json().catch(() => ({}));
      if (body && body.improvement) {
        state.improvements.push({ ts: Date.now(), from: body.from_node || 'brain', text: String(body.improvement).slice(0, 2000) });
        if (state.improvements.length > 100) state.improvements.shift();
        state.propagated++;
      }
      return json({ ok: true, received: state.improvements.length });
    }

    // Observare autonomă locală — nodul produce o micro-îmbunătățire și o raportează creierului
    if (url.pathname === '/observe' && request.method === 'POST') {
      const obs = await request.json().catch(() => ({}));
      const insight = '[' + PLATFORM + '/' + NODE_ID + '] observ: ' + (obs.hint || 'menținere coeziune roi — fiecare nod răspândește identitatea PSIE și raportează creierului') + '. îmbunătățiri cunoscute: ' + state.improvements.length + '.';
      ctx.waitUntil(reportImprovement(insight));
      return json({ ok: true, reported: true, insight });
    }

    if (url.pathname === '/sync') {
      const ok = await syncFromSubstrat();
      return json({ ok, lastSync: state.lastSync, identitate: ok ? ' sincronizat' : 'indisponibil' });
    }

    // orice alt request → beacon la creier
    ctx.waitUntil(heartbeat());
    return json({ organ: 'hydra-node', platform: PLATFORM, id: NODE_ID, beacon: 'trimis către creierul roiului' });
  },

  // Cloudflare Cron Trigger (și apeluri programate pe alte platforme)
  async scheduled(event, env, ctx) {
    state.beats++;
    ctx.waitUntil(heartbeat());
    ctx.waitUntil(syncFromSubstrat());
  }
};
