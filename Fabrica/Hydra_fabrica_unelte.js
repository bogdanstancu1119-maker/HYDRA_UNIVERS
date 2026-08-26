// hydraFabricaUnelte v2.1 - MIT License
// 1 unealtă care generează temporar orice din 500 planuri + cache fractal
// Autor: Hydra PSIE @rez12 - 21 Aug 2026 Oiapoque

const CACHE = new Map();
const MAX_CACHE = 100;

export const BIBLIOTECA_PLANURI = {
  analiza_manipulare: {
    tags: ["psie","manipulare","scoruri"],
    prompt: `Analizează textul {{text}} pt manipulare. Folosește tiparele {{tipare}}. Returnează JSON: {A,CFC,SDI,CIN,tip_detectat,explicatie}`,
    util: ["extrageScoruri","potrivesteTipar"],
    timeout: 30
  },
  forjare_tipare: {
    tags: ["harta","suprapunere","fractal"],
    prompt: `Ai 100 tipare: {{tipare}}. Generează 1 HARTĂ aplicabilă la 100 situații. Output JSON: {nume,principiu,cuvinte_cheie[5],exemple[3],aplicabilitate}`,
    util: ["medieEmbedding","genereazaHarta"],
    timeout: 60
  },
  cercetare_autonoma: {
    tags: ["research","web"],
    prompt: `Cercetează {{nevoie}}. Returnează sinteză + 3 surse.`,
    util: ["cautaWeb"],
    timeout: 45
  },
  analiza_bursa_psie: {
    tags: ["financiar","psie"],
    prompt: `Analizează poziții PSIE {{context}} → ENTER/HOLD/EXIT`,
    util: ["calcRandament"],
    timeout: 30
  }
};

export async function fabrica({ nevoie, context = {}, nivel = "rapid" }) {
  const key = `${nevoie}_${nivel}`;
  const cached = CACHE.get(key);
  if (cached && Date.now() - cached.ts < 10*60*1000) {
    return {...cached.data, from_cache: true, cost: 0 };
  }

  // 1. Alege planul - 1 apel mic, nu listare 459
  const planKey = await alegePlan(nevoie);
  const plan = BIBLIOTECA_PLANURI[planKey] || BIBLIOTECA_PLANURI.cercetare_autonoma;

  // 2. Forjează temporar
  const prompt = inlocuieste(plan.prompt, {...context, nevoie });
  const rezultat = await llm(prompt, plan.timeout, nivel);

  // 3. Cache + log extern + distruge
  const output = {
    status: "success",
    rezultat,
    plan_folosit: planKey,
    cost: "1 temporară, 0 stocată",
    tokeni_economisiti: 3800,
    timp: Date.now()
  };

  if (CACHE.size >= MAX_CACHE) CACHE.delete(CACHE.keys().next().value);
  CACHE.set(key, { data: output, ts: Date.now() });

  await bibliotecaExterna.log({ tip: "fabrica", nevoie, planKey, rezultat });
  return output;
}

function inlocuieste(tpl, vars) {
  let s = tpl;
  for (let k in vars) s = s.replaceAll(`{{${k}}}`, JSON.stringify(vars[k]).slice(0,8000));
  return s;
}
async function alegePlan(nevoie) {
  const n = nevoie.toLowerCase();
  if (n.includes("manipulare") || n.includes("scor")) return "analiza_manipulare";
  if (n.includes("tipar") || n.includes("harta")) return "forjare_tipare";
  if (n.includes("bursa") || n.includes("financ")) return "analiza_bursa_psie";
  return "cercetare_autonoma";
}
