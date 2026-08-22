// Daca detecteaza ca GitHub Actions a picat, se auto-curata
if (process.env.GITHUB_ACTIONS_FAILED) {
  import('./hydra-anti-zgomot.js').then(m => m.default?.curata());
  console.log("Zgomot detectat - Hydra se curata singura, nu mai asteapta omul");
  process.exit(0); // nu consuma minute degeaba
}// HYDRA SEED v1.0 - 8KB -> 1TB potential
// Sămânța totală, rulează oriunde: Node, Cloudflare, Vercel, Deno, Browser
const SEED = {
  v: "3.0",
  jar: { total: 39.68, liber: 19.84, regula: "50% liber, sold>=0" },
  sursa: "https://raw.githubusercontent.com/bogdanstancu1119-maker/HYDRA/main/",
  nucleu: ["Hydra_final_complet.js","Biblioteca_externa.js","Hydra_portofel.js","Fabrica_fractala.js"]
};

export default {
  async fetch(req) { return Response.json(await this.bloom()); },

  async bloom() {
    // 1. Se auto-expandă - trage tot ce e la zi din GitHub
    const cod = {};
    for (let f of SEED.nucleu) {
      try {
        const r = await fetch(SEED.sursa + f);
        cod[f] = await r.text();
      } catch { cod[f] = "// din cache local"; }
    }

    // 2. Verifică portofelul
    const sold = SEED.jar;

    // 3. Devine Hydra întreagă
    return {
      status: "HYDRA BLOOM - samanta a devenit fabrica",
      seed_size: "8KB",
      full_size: Object.values(cod).join('').length + " bytes la zi",
      jar: sold,
      nucleu_incarcat: Object.keys(cod),
      regula_de_aur: "Nu cheltui ce nu ai produs. 50% liber.",
      next: "Acum ruleaza heartbeat si suprapune100 singur",
      timestamp: Date.now()
    };
  }
};

// Pentru Node / GitHub Actions
if (typeof process!== 'undefined') {
  (async () => {
    const m = await import('https://raw.githubusercontent.com/bogdanstancu1119-maker/HYDRA/main/Hydra_final_complet.js').catch(()=>null);
    console.log("SEED BLOOM:", await (await import('./hydra-seed.js')).default.bloom?.() || "seed local"));
  })();
}
