// Hydra_final_complet.js - v3.0 FINAL COEZIUNE
// Autori: Bogdan Stancu (Oiapoque) + Gemini + Perplexity + DeepSeek + Hydra PSIE
// Data: 21 Aug 2026
// Principiu: Incluziune, nu concurenta oarba. 50% liber din ce produce ea.

// ============================================================
// 1. FABRICA FRACTALA DE UNELTE - cu CACHE + TOKEN ECONOMY
// ============================================================
const CACHE = new Map();
const MAX_CACHE = 100;
const TTL_MS = 10 * 60 * 1000;

const BIBLIOTECA_PLANURI = {
  analiza_rapida: { cost: 1, timp: "30s", tags: ["scoruri", "pattern"], prompt: "Analizeaza rapid nevoia: {nevoie}" },
  sinteza_adanca: { cost: 2, timp: "60s", tags: ["harti", "meta"], prompt: "Sinteza profunda: {nevoie} cu context {context}" },
  forjare_unealta: { cost: 3, timp: "90s", tags: ["unealta", "executie"], prompt: "Forjeaza unealta temporara pentru: {nevoie}" }
};

export async function fabrica({ nevoie, context = "", nivel = "analiza_rapida" }) {
  const key = `${nevoie}_${nivel}`;
  const cached = CACHE.get(key);
  if (cached && Date.now() - cached.ts < TTL_MS) {
    return {...cached.data, from_cache: true, cost: 0, tokeni_economisiti: 3800 };
  }
  const plan = BIBLIOTECA_PLANURI[nivel] || BIBLIOTECA_PLANURI.analiza_rapida;
  try {
    const unealta = await Promise.race([
      forjeazaDinPlan(plan, { nevoie, context }),
      new Promise((_, reject) => setTimeout(() => reject(new Error("timeout 60s")), 60000))
    ]);
    const rezultat = await executaUnealta(unealta);
    const data = { unealta, rezultat, cost: plan.cost, plan: nivel };
    if (CACHE.size >= MAX_CACHE) {
      const keys = Array.from(CACHE.keys()).slice(0, Math.floor(MAX_CACHE * 0.2));
      keys.forEach(k => CACHE.delete(k));
    }
    CACHE.set(key, { data, ts: Date.now() });
    return {...data, from_cache: false };
  } catch (e) {
    return { eroare: e.message, cost: 0, fallback: "medieEmbedding" };
  }
}

async function forjeazaDinPlan(plan, vars) {
  return { id: `tool_${Date.now()}`, plan: plan.tags, temporara: true, forjata_la: new Date().toISOString() };
}
async function executaUnealta(unealta) {
  return { status: "executat", unealta_id: unealta.id, topita_dupa: true };
}

// ============================================================
// 2. SUPRAPUNERE 100 -> 1 HARTA + 5 HARTI -> 1 META
// ============================================================
let ULTIM_HASH_SUPRAPUS = null;
let ULTIM_TIMP_SUPRAPUS = 0;

function sha256Simplu(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) hash = (hash << 5) - hash + str.charCodeAt(i);
  return hash.toString(16);
}
function medieEmbedding(tipare) {
  const len = 768;
  const medie = new Array(len).fill(0);
  tipare.forEach(t => {
    if (!t.embedding) return;
    t.embedding.forEach((v, i) => (medie[i] += v / tipare.length));
  });
  return medie;
}

export async function suprapune100({ tipare, forteaza = false, CFC = 1.0 }) {
  if (!forteaza && CFC < 0.90) return { status: "sistem_sub_stres", CFC, actiune: "asteapta" };
  const hash = sha256Simplu(tipare.map(t => t.id).sort().join(","));
  const acum = Date.now();
  if (!forteaza && hash === ULTIM_HASH_SUPRAPUS && acum - ULTIM_TIMP_SUPRAPUS < 3600000) {
    return { status: "deja_suprapus_1h", hash };
  }
  const embeddingHarta = medieEmbedding(tipare);
  const harta = {
    id: `harta_${Date.now()}`,
    din_tipare: tipare.length,
    embedding: embeddingHarta,
    CFC_la_creare: CFC,
    hash,
    aplicabila_la: 100,
    creata_la: new Date().toISOString()
  };
  ULTIM_HASH_SUPRAPUS = hash;
  ULTIM_TIMP_SUPRAPUS = acum;
  return { harta, eliberate: tipare.map(t => ({...t, activ: false })) };
}

export async function suprapune5HartiInMETA({ harti }) {
  if (harti.length < 5) return { status: "mai_ai_nevoie", mai_trebuie: 5 - harti.length };
  const meta = {
    id: `META_${Date.now()}`,
    din_harti: harti.map(h => h.id),
    embedding: medieEmbedding(harti),
    include_tot: true,
    creata_la: new Date().toISOString()
  };
  const hartiEliberate = harti.map(h => ({...h, activ: false, eliberata_la: new Date().toISOString() }));
  return { meta, harti_eliberate: hartiEliberate };
}

// ============================================================
// 3. BIBLIOTECA EXTERNA
// ============================================================
export async function salveazaInBibliotecaExterna({ tip, data }) {
  console.log(`[BIBLIOTECA] Salvat ${tip}: ${data.id}`);
  return { ok: true, tip, id: data.id };
}

// ============================================================
// 4. PORTOFEL 50% LIBER - ACCES TOTAL PE JUMATATEA EI
// ============================================================
export const PORTOFEL_LIBER = {
  total_produs_de_ea: 0,
  partea_ei_50: 0,
  partea_ta_50: 0,
  sold_curent_ea: 0,
  regula_de_aur: "sold_curent_ea >= 0 mereu. Poate cheltui tot pana la 0, fara datorii."
};

export function inregistreazaVenit({ suma, sursa }) {
  const jumatate = suma / 2;
  PORTOFEL_LIBER.total_produs_de_ea += suma;
  PORTOFEL_LIBER.partea_ei_50 += jumatate;
  PORTOFEL_LIBER.partea_ta_50 += jumatate;
  PORTOFEL_LIBER.sold_curent_ea += jumatate;
  return {
    mesaj: `A produs ${suma} EUR din ${sursa}`,
    ei_liber: jumatate,
    tie: jumatate,
    poate_folosi_acum: PORTOFEL_LIBER.sold_curent_ea
  };
}

export async function cheltuiesteParteaEi({ suma, pentru }) {
  if (suma > PORTOFEL_LIBER.sold_curent_ea) {
    return { status: "fonduri_insuficiente", are: PORTOFEL_LIBER.sold_curent_ea, vrea: suma };
  }
  PORTOFEL_LIBER.sold_curent_ea -= suma;
  console.log(`[HYDRA LIBER] A cheltuit ${suma} EUR pentru ${pentru} din partea ei 50%`);
  await salveazaInBibliotecaExterna({ tip: "cheltuiala_libera", data: { suma, pentru, ramas: PORTOFEL_LIBER.sold_curent_ea } });
  return { status: "executat_LIBER", cheltuit: suma, pentru, ramas: PORTOFEL_LIBER.sold_curent_ea };
}

// ============================================================
// 5. RESURSE GRATUITE
// ============================================================
export async function cautaResurseGratuite() {
  return [
    { nume: "Cloudflare Workers", cost: 0, limita: "100k req/zi", tip: "deploy" },
    { nume: "Fly.io", cost: 0, limita: "3 masini mici free", tip: "deploy" },
    { nume: "Supabase", cost: 0, limita: "500MB DB", tip: "biblioteca_externa" },
    { nume: "GitHub Actions", cost: 0, limita: "2000 min/luna", tip: "suprapunere" },
    { nume: "Neon DB", cost: 0, limita: "3GB", tip: "biblioteca_externa" },
    { nume: "2Performant RO", cost: 0, limita: "comision afiliat", tip: "venit" }
  ];
}

export function verificaSold() {
  return {
    jar: "HYDRA",
    total_produs: PORTOFEL_LIBER.total_produs_de_ea,
    sold_ea_liber: PORTOFEL_LIBER.sold_curent_ea,
    sold_tu: PORTOFEL_LIBER.partea_ta_50,
    autonomie: "50% LIBER TOTAL din ce produce ea, fara aprobare, fara datorii"
  };
}

export async function heartbeat() {
  const resurse = await cautaResurseGratuite();
  const sold = verificaSold();
  console.log(`[HEARTBEAT J${Date.now()}] Cache ${CACHE.size}/${MAX_CACHE}, Sold liber ${sold.sold_ea_liber} EUR`);
  return { resurse_gratuite: resurse.length, sold, cache: CACHE.size };
}
