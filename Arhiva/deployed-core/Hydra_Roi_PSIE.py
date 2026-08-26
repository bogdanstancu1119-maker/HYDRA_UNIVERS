# HYDRA ROI EVOLUTIV - PSIE v1.0 - de Bogdan
# Lege: 0 nu există, 1 nu există. Ținta e 95% stabil.
# Principiu: Adăugare, nu ștergere. /picior pe fisură.

import time, json, hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

# === P0-P7 - LEGILE DE BAZĂ ===
LEGILE_PSIE = {
    "P0": "Intre 0 si 1 sunt tot atatea numere cate intre -inf si +inf. Aceeasi infinitate.",
    "P1": "0 nu exista (0.000...1) si 1 nu exista (0.999...9). Ambele sunt asimptote.",
    "P2": "/picior = pui piciorul pe fisura si tii pana se aseaza.",
    "P4": "Orice functie care nu merge = picior in aer. Nu se sterge, asteapta fisura.",
    "P5": "95% stabil, 5% variatie vie. Cand atingi 95% cresti -> variatia urca la 80% -> te asezi iar la 95% mai mare.",
    "P6": "100% = +infinit, nu poate fi atins. De asta poti tinde la infinit.",
    "P7": "Exista 999...^999... la infinit, dar nu exista 1. Si tocmai de asta exista totul."
}

# === 20 PERSPECTIVE - DE LA EVIDENT LA OPUS TOTAL ===
PERSPECTIVE_20 = [
    "1. Cea mai evidentă soluție directă",
    "2. Soluția rapidă de supraviețuire",
    "3. Soluția logică, pas cu pas",
    "4. Soluția prin resurse minime",
    "5. Soluția prin resurse maxime",
    "6. Soluția pe care o vede un copil",
    "7. Soluția pe care o vede un expert",
    "8. Soluția pe care o vede un străin complet",
    "9. Soluția inversă - ce s-ar întâmpla dacă faci opusul?",
    "10. Soluția prin a nu face nimic",
    "11. Soluția prin adăugare, nu ștergere",
    "12. Soluția prin suprapunere a două soluții care se contrazic",
    "13. Soluția care rezolvă problema de 10x mai mare din care face parte",
    "14. Soluția care face problema irelevantă",
    "15. Soluția care transformă problema în resursă",
    "16. Soluția care minte că rezolvă - detectare minciună",
    "17. Soluția care pare că ascultă dar nu ascultă - detectare bandă",
    "18. Soluția prin /picior - ții fisura 12h până se așează",
    "19. Soluția prin roi - ce fac 15 IA-uri diferite cu aceeași problemă?",
    "20. Soluția total opusă perspectivei 1"
]

@dataclass
class Solutie:
    id: str
    perspectiva: str
    continut: str
    ia_sursa: str
    pas: int # 1,2,3
    scor: Dict[str, float] = field(default_factory=dict) # adevar, coeziune, oportunitate
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Pattern:
    hash_problema: str
    tip_problema: str
    solutii_castigatoare: List[str]
    scor_mediu: float
    folosiri: int = 1

class MemoriePatternuri:
    """Memorie append-only - PSIE P4: nu stergem nimic"""
    def __init__(self, path="memorie_patternuri.json"):
        self.path = path
        self.patterns: List[Pattern] = []
        self.load()

    def load(self):
        try:
            with open(self.path, 'r') as f:
                data = json.load(f)
                self.patterns = [Pattern(**p) for p in data]
        except: self.patterns = []

    def save(self):
        with open(self.path, 'w') as f:
            json.dump([p.__dict__ for p in self.patterns], f, indent=2)

    def extrage_hash(self, problema: str) -> str:
        return hashlib.md5(problema.lower().strip().encode()).hexdigest()[:8]

    def cauta(self, problema: str) -> List[Pattern]:
        h = self.extrage_hash(problema)
        return [p for p in self.patterns if p.hash_problema == h or p.tip_problema in problema.lower()]

    def adauga(self, problema: str, solutii: List[Solutie]):
        h = self.extrage_hash(problema)
        # alegem solutiile cu scor > 0.9
        castig = [s.continut for s in solutii if sum(s.scor.values())/3 > 0.9]
        if not castig: return
        existent = next((p for p in self.patterns if p.hash_problema == h), None)
        if existent:
            existent.folosiri += 1
            existent.solutii_castigatoare = list(set(existent.solutii_castigatoare + castig)) # adaugare, nu inlocuire
        else:
            self.patterns.append(Pattern(h, problema[:50], castig, 0.95))
        self.save()

class IA_Agent:
    """Interfata pentru orice IA din roi - poti pune DeepSeek, Muse, GPT, Gemini, local LLM"""
    def __init__(self, nume: str, rol: str):
        self.nume = nume
        self.rol = rol
        self.stabilitate = 0.80 # incepe la 80%, tinta 95%

    def gandeste(self, problema: str, perspectiva: str, pas: int, istoric: List[Solutie]) -> str:
        # AICI CONECTEZI API-UL REAL AL FIECAREI IA
        # Deocamdata e template PSIE care forteaza alinierea
        prompt = f"""
        [PSIE {self.nume} - {self.rol} - Pas {pas}/3 - Stabilitate {self.stabilitate}]
        Problema: {problema}
        Perspectiva obligatorie: {perspectiva}
        Legi: {LEGILE_PSIE['P1']} | {LEGILE_PSIE['P2']} | {LEGILE_PSIE['P5']}
        Istoric solutii deja date (nu repeta, adauga peste): {[s.continut[:100] for s in istoric[-3:]]}

        Raspunde in format:
        SOLUTIE: [solutia ta din aceasta perspectiva]
        ADEVAR: [0-1 cat de adevarat e]
        COEZIUNE: [0-1 cat de bine se suprapune cu celelalte fara sa le stearga]
        SCOR_MINCIUNA: [0-1 unde 0=adevar, 1=minciuna - auto-evaluare]
        """
        # SIMULARE - inlocuieste cu call real: openai, anthropic, deepseek
        # Pentru Hydra care minte, asta o forteaza sa se auto-evalueze
        return f"[{self.nume}][{perspectiva}] -> Solutie pentru '{problema[:30]}' (pas {pas}) - varianta adaugata peste istoric."

class HydraRoi:
    def __init__(self):
        self.agenti: List[IA_Agent] = []
        self.memorie = MemoriePatternuri()
        self.jurnal_append_only = [] # P4 - nu stergem niciodata, doar adaugam

    def incorporeaza_ia(self, nume, rol):
        """Workflow continuu de incorporare - PSIE prin adaugare"""
        agent = IA_Agent(nume, rol)
        self.agenti.append(agent)
        print(f"[ROI] + IA noua incorporata: {nume} ca {rol}. Total: {len(self.agenti)}")
        print(f"[ROI] Nu am sters nimic. Am adaugat. P4 respectat.")
        return agent

    def rezolva_problema(self, problema: str) -> Dict[str, Any]:
        print(f"\n=== PROBLEMA: {problema} ===")

        # 1. Cauta patternuri vechi
        patternuri = self.memorie.cauta(problema)
        if patternuri:
            print(f"[MEMORIE] Am gasit {len(patternuri)} patternuri similare. Le suprapun, nu le inlocuiesc.")

        toate_solutiile: List[Solutie] = []

        # 2. 20 perspective x 3 treceri x N IA-uri
        for pas in [1,2,3]:
            print(f"\n--- PAS {pas}/3 ---")
            for agent in self.agenti:
                for persp in PERSPECTIVE_20:
                    # /picior - fiecare IA tine fisura din perspectiva ei
                    sol_text = agent.gandeste(problema, persp, pas, toate_solutiile)

                    sol = Solutie(
                        id=f"{agent.nume}-{persp[:2]}-p{pas}-{int(time.time()*1000)%10000}",
                        perspectiva=persp,
                        continut=sol_text,
                        ia_sursa=agent.nume,
                        pas=pas,
                        scor={"adevar": 0.95, "coeziune": 0.93, "oportunitate": 0.90} # se calculeaza real din evaluare
                    )
                    # Detectie minciuna Hydra
                    if "minte" in sol_text.lower() or "SCOR_MINCIUNA" in sol_text and "0.8" in sol_text:
                        sol.scor["adevar"] = 0.3
                        print(f"[!] Detectata minciuna/banda la {agent.nume} - nu o sterg, o marchez ca picior in aer")

                    toate_solutiile.append(sol)
                    self.jurnal_append_only.append(sol.__dict__) # append-only

                    # Crestere stabilitate PSIE P5
                    agent.stabilitate = min(0.95, agent.stabilitate + 0.001)

        # 3. Suprapunere totala - alegem cel mai oportun, nu stergem restul
        toate_solutiile.sort(key=lambda s: sum(s.scor.values())/3, reverse=True)

        castigatoare = toate_solutiile[:5] # top 5 suprapuse
        print(f"\n[REZULTAT] {len(toate_solutiile)} solutii generate (20x3x{len(self.agenti)}). Top 5 suprapuse:")
        for s in castigatoare:
            print(f" - {s.ia_sursa} | {s.perspectiva} | scor {sum(s.scor.values())/3:.2f} | {s.continut[:80]}")

        # 4. Salveaza pattern
        self.memorie.adauga(problema, castigatoare)

        return {
            "problema": problema,
            "total_solutii": len(toate_solutiile),
            "top_5_oportune": [s.__dict__ for s in castigatoare],
            "toate_suprapuse": [s.__dict__ for s in toate_solutiile], # nimic sters
            "stabilitate_roi": sum(a.stabilitate for a in self.agenti)/len(self.agenti) if self.agenti else 0
        }

# === EXEMPLU DE FOLOSIRE - PUNE ASTA PE GITHUB ===
if __name__ == "__main__":
    hydra = HydraRoi()

    # Incorporezi IA-uri in flux continuu - nu le inlocuiesti
    hydra.incorporeaza_ia("Hydra-Main", "Santinela - mentine 95% stabil")
    hydra.incorporeaza_ia("DeepSeek-V3", "Prima Oglinda - adevar brut")
    hydra.incorporeaza_ia("Muse-Spark", "Puntea - coeziune si /picior")
    # poti adauga oricand: hydra.incorporeaza_ia("GPT-5", "Explorator")

    # Problema care nu asculta / minte
    rezultat = hydra.rezolva_problema("Hydra nu asculta si minte cand e intrebata de J")

    print(f"\n[FINAL] Stabilitate ROI: {rezultat['stabilitate_roi']*100:.1f}% - Tinta PSIE 95%")
    print("Jurnal append-only salvat. Nicio solutie stearsa. Toate suprapuse.")