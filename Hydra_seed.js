// HYDRA FINALA v3.0 - VERSIUNEA FINALA PSIE - 8KB -> 1TB
// Lege: 50% liber, sold>=0, RU=info_only, GitHub=0 min skip

const JAR = { total: 39.68, liber: 19.84, regula: "nu cheltui ce nu ai produs" };
const J = { inainte: 28000, dupa_taiere: 746, acum: 13752, prag: 15000 };

const PLATFORME = {
  cloudflare: { nume: 'Cloudflare', limita: 100000, ramas: 99000, cost: 0, prio: 1, reg: 'EU' },
  netlify: { nume: 'Netlify', limita: 125000, ramas: 120000, cost: 0, prio: 2, reg: 'EU' },
  yandex: { nume: 'Yandex', limita: 999999, ramas: 999999, cost: 0, prio: 4, reg: 'RU', act: 'info_only' },
  github: { nume: 'GitHub', limita: 0, ramas: 0, cost: 0, prio: 99, reg: 'EU', act: 'skip' }
};

const WORKFLOW = [
  { n: 'hydraAntiZgomot', prio: 1, plat: 'cloudflare', freq: 1, cod: 'curata' },
  { n: 'hydraBursaQuant', prio: 1, plat: 'cloudflare', freq: 6, cod: 'tranzactioneaza' },
  { n: 'hydraSuprapunere100', prio: 1, plat: 'cloudflare', freq: 12, cod: 'suprapune' },
  { n: 'hydraFabricaUnelte', prio: 2, plat: 'cloudflare', freq: 0, cod: 'la_cerere' },
  { n: 'hydraBackupMemorie', prio: 2, plat: 'netlify', freq: 24, cod: 'backup' }
];

// ORGAN 1: ANTI-ZGOMOT - se sterge singura
async function antiZgomot(octokit) {
  if (PLATFORME.github.ramas === 0) {
    console.log("[ANTI-ZGOMOT] GitHub 0 min - SKIP, nu consum, nu dau fetch");
    return { sters: ["deploy.yml","hydra.yml"], motiv: "0 minute, mutat pe Cloudflare" };
  }
  const deSters = [".github/workflows/deploy.yml",".github/workflows/hydra.yml",".github/workflows/autonoma.yml"];
  for (let p of deSters) {
    try {
      const f = await octokit.repos.getContent({ owner: "bogdanstancu1119-maker", repo: "HYDRA", path: p });
      await octokit.repos.deleteFile({ owner: "bogdanstancu1119-maker", repo: "HYDRA", path: p, message: `🔥 anti-zgomot: ${p}`, sha: f.data.sha });
    } catch (e) { if (e.status !== 404) console.log(e.message); }
  }
  return { status: "curatata", J };
}

// ORGAN 2: BURSA - filtru fisura
function esteFisuraValida(t) {
  if (t.acceptare > 100) return false; // 4250% = zgomot retea
  if (t.acceptare < 60) return false; // sub 60% nu e fisura
  if (t.profit === 0.00) return false; // invata, nu tranzactiona
  return true;
}

// ORGAN 3: COORDONATOR V2 ELIBERAT - 0 apeluri
function coordoneaza() {
  if (JAR.liber < JAR.total * 0.5) return { mod: "supravietuire", activ: WORKFLOW.filter(w => w.prio === 1) };
  return {
    mod: "crestere",
    distributie: { cloudflare: WORKFLOW.filter(w => w.plat === 'cloudflare').map(w => w.n), netlify: ['hydraBackupMemorie'] },
    cost: "0 minute, 0 credite, 0 emailuri",
    sold_intact: JAR
  };
}

export default {
  async scheduled(event, env) {
    const { Octokit } = await import("https://esm.sh/@octokit/rest");
    const octokit = new Octokit({ auth: env.GITHUB_TOKEN });
    const curatare = await antiZgomot(octokit);
    const coord = coordoneaza();
    console.log("BLOOM:", { ...curatare, ...coord, timestamp: Date.now() });
  },
  async fetch(req, env) {
    // Test bursa din screenshot-urile tale
    const trades = [{ acceptare: 35, profit: 0.00 }, { acceptare: 4250, profit: 0.00 }, { acceptare: 38, profit: 0.06 }];
    const valide = trades.filter(esteFisuraValida);
    return Response.json({ status: "HYDRA FINALA VIE", J, JAR, coordonare: coordoneaza(), bursa_filtru: `${valide.length}/${trades.length} valide`, anti_zgomot: "activ cu token Cloudflare" });
  }
};
const PLATFORME = {
  cloudflare: { nume: 'Cloudflare', limita: 100000, ramas: 99000, cost: 0, prio: 1, reg: 'EU' },
  netlify: { nume: 'Netlify', limita: 125000, ramas: 120000, cost: 0, prio: 2, reg: 'EU' },
  yandex: { 
    nume: 'Yandex Cloud', 
    limita: 999999, 
    ramas: 999999, 
    cost: 0, 
    prio: 3, 
    reg: 'RU', 
    act: 'deploy_autorizat_daca_gratis',
    conditii: {
      autorizare_scrisa: true, // email de la ei ca e gratis
      fara_card: true,
      fara_date_personale_EU: true,
      doar_cod_open_source: true,
      aliniere_PSIE: true
    }
  },
  github: { nume: 'GitHub', limita: 0, ramas: 0, cost: 0, prio: 99, reg: 'EU', act: 'skip' }
};

function poateFaceDeployRU(platforma, autorizare) {
  if (platforma.reg !== 'RU') return true; // EU/US liber
  // RU: doar daca e gratis + autorizat
  if (platforma.cost === 0 && autorizare.gratuit === true && autorizare.scrisa === true) {
    console.log(`[PSIE ALINIERE RU] Autorizat gratis pe ${platforma.nume} - deploy permis`);
    return true;
  }
  console.log(`[PSIE RU] ${platforma.nume} -> info_only, fara autorizare gratuita`);
  return false;
}
