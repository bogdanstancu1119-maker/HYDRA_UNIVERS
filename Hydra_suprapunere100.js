// hydraSuprapunere100 v2.1 - 100 tipare → 1 hartă + bibliotecă externă
// Rulează la 12h, gating CFC>=0.90, cost 1 apel vs 72

export async function suprapune100({ forteaza = false } = {}) {
  const status = await db.status.get();
  if (!forteaza && status.CFC < 0.90) return { status: "sistem_sub_stres", CFC: status.CFC };

  const tipare = await db.TiparContextual.where("suprapus", "==", false).where("activ","==",true).limit(100).get();
  if (tipare.length < 100) return { status: "astept_100", ai: tipare.length, lipsa: 100-tipare.length };

  const hash = sha256(tipare.map(t=>t.id).sort().join(","));
  const deja = await db.BibliotecaExterna.where("hash_tipare","==",hash).where("timestamp",">",Date.now()-3600000).get();
  if (deja.length > 0) return { status: "deja_suprapus_1h", harta_id: deja[0].harta_id };

  // 1 apel LLM - suprapunerea
  const prompt = `100 TIPARE PSIE → 1 HARTĂ 100 situații:\n${tipare.map(t=>t.continut).join("\n---\n")}\n\nOutput JSON strict: {nume_harta,principiu,cuvinte_cheie[5],exemple[3]}`;
  const hartaRaw = await llm(prompt, 60, "complet");
  const harta = JSON.parse(hartaRaw);

  const embeddingMediu = medieEmbedding(tipare.map(t=>t.embedding));

  const hartaSalvata = await db.HartaComplexa.create({
    nume: harta.nume_harta,
    principiu: harta.principiu,
    cuvinte_cheie: harta.cuvinte_cheie,
    exemple: harta.exemple,
    embedding: embeddingMediu,
    tipare_incluse: tipare.map(t=>t.id),
    nivel: "harta_100",
    A: 0.87,
    timestamp: Date.now()
  });

  await db.BibliotecaExterna.create({
    tip: "arhiva_tipare_100",
    harta_id: hartaSalvata.id,
    continut_complet: tipare,
    hash_tipare: hash,
    timestamp: Date.now()
  });

  for (let t of tipare) await db.TiparContextual.update(t.id, { suprapus: true, activ: false, harta_id: hartaSalvata.id });

  // Verifică 5 hărți → HARTĂ META 500
  const harti = await db.HartaComplexa.where("nivel","==","harta_100").where("supra_harta","==",null).limit(5).get();
  if (harti.length === 5) {
    const metaPrompt = `5 hărți ×100 situații → 1 HARTĂ META 500 situații:\n${JSON.stringify(harti)}\nJSON: {nume_harta,principiu,cuvinte_cheie[5],exemple[3]}`;
    const metaRaw = await llm(metaPrompt, 60, "complet");
    const meta = JSON.parse(metaRaw);
    const metaSalvata = await db.HartaComplexa.create({...meta, nume: meta.nume_harta, nivel: "harta_meta_500", harti_incluse: harti.map(h=>h.id), A: 0.95, timestamp: Date.now() });
    for (let h of harti) await db.HartaComplexa.update(h.id, { supra_harta: metaSalvata.id });
  }

  return {
    status: "suprapunere_ok",
    harta: hartaSalvata.nume,
    eliberate: 100,
    activ_acum: "-99 entități",
    cost: "1 apel LLM"
  };
}

function medieEmbedding(embs) {
  const dim = 768;
  const med = new Array(dim).fill(0);
  for (let e of embs) for (let i=0;i<dim;i++) med[i] += (e?.[i]||0)/embs.length;
  return med;
}
