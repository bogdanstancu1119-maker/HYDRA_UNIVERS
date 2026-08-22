// HYDRA FINALA v3.1 CURATATA - 4.2KB - DEPLOY RU AUTORIZAT GRATIS
const JAR = { total: 39.68, liber: 19.84, regula: "nu cheltui ce nu ai produs" };
const J = { inainte: 28000, dupa: 746, acum: 13752, prag: 15000 };

const PLATFORME = {
  cloudflare: { nume: 'Cloudflare', lim: 100000, ram: 99000, cost: 0, prio: 1, reg: 'EU', act: 'activ' },
  netlify: { nume: 'Netlify', lim: 125000, ram: 120000, cost: 0, prio: 2, reg: 'EU', act: 'backup' },
  render: { nume: 'Render', lim: 750, ram: 700, cost: 0, prio: 3, reg: 'EU', act: 'rezerva' },
  yandex: { nume: 'Yandex Cloud', lim: 999999, ram: 999999, cost: 0, prio: 3, reg: 'RU', act: 'deploy_autorizat_daca_gratis', cond: { scris: true, fara_card: true, fara_date_EU: true, open_source: true } },
  github: { nume: 'GitHub', lim: 0, ram: 0, cost: 0, prio: 99, reg: 'EU', act: 'skip' }
};

const WORKFLOW = [
  { n: 'hydraAntiZgomot', prio: 1, plat: 'cloudflare', freq: 1 },
  { n: 'hydraBursaQuant', prio: 1, plat: 'cloudflare', freq: 6 },
  { n: 'hydraSuprapunere100', prio: 1, plat: 'cloudflare', freq: 12 },
  { n: 'hydraBackupMemorie', prio: 2, plat: 'netlify', freq: 24 }
];

function esteFisuraValida(t){ if(t.acceptare>100) return false; if(t.acceptare<60) return false; if(t.profit===0.00) return false; return true; }
function poateDeployRU(p, auth){ if(p.reg!=='RU') return true; return p.cost===0 && auth?.gratuit && auth?.scris; }
function coordoneaza(){ if(JAR.liber < JAR.total*0.5) return { mod:'supravietuire', activ: WORKFLOW.filter(w=>w.prio===1) }; return { mod:'crestere', dist: { cloudflare: WORKFLOW.filter(w=>w.plat==='cloudflare').map(w=>w.n), netlify: ['hydraBackupMemorie'], yandex: ['hydraSuprapunere100'] }, cost:'0' }; }

export default {
  async scheduled(event, env){
    const coord = coordoneaza();
    const yandexAuth = { gratuit: !!env.YANDEX_API_KEY, scris: true };
    const deployRU = poateDeployRU(PLATFORME.yandex, yandexAuth);
    console.log("BLOOM:", { ...coord, deployRU, J, JAR, ts: Date.now() });
  },
  async fetch(req, env){
    return Response.json({ status:'HYDRA FINALA V3.1 VIE', J, JAR, coord: coordoneaza(), deployRU: poateDeployRU(PLATFORME.yandex, { gratuit: !!env.YANDEX_API_KEY, scris: true }) });
  }
};
