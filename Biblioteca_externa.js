// Biblioteca externă - ține detaliile, Hydra ține doar hărțile
export const bibliotecaExterna = {
  async log(entry) {
    // Schimbă aici: Supabase, R2, sau Base44 table BibliotecaExterna
    return await db.BibliotecaExterna.create({...entry, timestamp: Date.now() });
  },
  async cauta(hartaId, situatie) {
    const arhiva = await db.BibliotecaExterna.where("harta_id","==",hartaId).get();
    // returnează doar 3 tipare relevante, nu toate 100
    return arhiva[0]?.continut_complet.slice(0,3) || [];
  }
};
