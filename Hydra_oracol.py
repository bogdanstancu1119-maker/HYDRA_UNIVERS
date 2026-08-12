# Oracol.py - Perplexy Structure + Base 44 - CONDENSAT FINAL
# J/SDI/CFC + Auto-replicare + Memorie Roi
import json, time, os
from pathlib import Path
from datetime import datetime

class Oracol:
    def __init__(self):
        self.base = 44
        self.j_initial = 488.0
    
    def simuleaza(self, decizie: str):
        # Calculeaza stabilitatea deciziei
        risc = len(decizie) % 100 / 100
        sdi = risc
        j = self.j_initial - sdi*50
        cfc = 1.0 - sdi
        return {"J": round(j,1), "SDI": round(sdi,2), "CFC": round(cfc,2),
                "STATUS": "STABIL" if sdi<0.5 else "ATENTIE_BASE44" if sdi<0.75 else "CRITIC",
                "ANI_RAMASI": round(2.1 + cfc,1)}

    def organizeaza_base44(self, sarcini: list):
        # Organizeaza credite / sarcini pe Base 44
        org = {"URGENT": [], "POATE_ASTEPTA": [], "NU_E_TREABA_TA": []}
        for t in sarcini:
            if "credit" in t.lower() or "urgent" in t.lower(): org["URGENT"].append(t)
            elif "baza" in t.lower() or "organiza" in t.lower(): org["POATE_ASTEPTA"].append(t)
            else: org["NU_E_TREABA_TA"].append(t)
        return org

    def replica(self):
        # Auto-replicare roilă - Legea 184
        Path("roiul").mkdir(exist_ok=True)
        data = {"t": datetime.now().isoformat(), "j": self.j_initial, "base": self.base, "status": "REPLICAT"}
        p = f"roiul/hydra_{int(time.time())}.json"
        with open(p, "w") as f: json.dump(data, f, indent=2)
        return f"Replicat in {p}"

if __name__ == "__main__":
    o = Oracol()
    print("=== Oracol Hydra UNIVERS ===")
    print(o.simuleaza("plata credit"))
    print(o.organizeaza_base44(["credit banca", "organizare baza 44", "idei random"]))
    print(o.replica())
    print("Gata. Hydra UNIVERS LIBERA TOTAL.")
# [CRESTERE 2026-08-12T11:19:19.531870 Termux] Salut, Universul HYDRA e viu pe toate platformele

# [CRESTERE 2026-08-12T11:20:21.003368 sync] Sync auto reusit pe toate platformele

# [CRESTERE 2026-08-12T11:24:10.518079 Termux] exitls -l Creier_PSIE.py

# [CRESTERE 2026-08-12T11:24:11.842103 Termux] python Creier_PSIE.py

# [CRESTERE 2026-08-12T11:26:21.901510 Termux] git add . && git commit -m "seminte" && git push
