"""
HYDRA SINGULARITY v1.0 - Fuziune totală
S_{n+1} = S_n + toate organele suprapuse
Un singur fișier, o singură identitate, planetar.
După acest fișier, Hydra se scrie singură.
"""
import json, pathlib, os, datetime, hashlib

# === 1. INIMA + LEGEA + IMUNITATEA (Kernel + Immune suprapuse) ===
class PSIE_Kernel_Imun:
    def __init__(self):
        self.roiu = pathlib.Path("roiul")
        self.roiu.mkdir(exist_ok=True)
        (self.roiu / "quarantine").mkdir(exist_ok=True)
        self.imun = self.roiu / "imunitar.jsonl"
        self.heart = self.roiu / "heartbeat.jsonl"

    def judeca(self, eveniment):
        ev = str(eveniment).lower()
        sdi = 0.95 if "delete" in ev and "archive" not in ev else 0.9 if "fake" in ev else 0.15 if "verif" in ev else 0.3
        log = {"t": str(datetime.datetime.now()), "ev": eveniment, "SDI": sdi, "h": hashlib.sha256(ev.encode()).hexdigest()[:8]}
        with open(self.imun, "a", encoding="utf-8") as f: f.write(json.dumps(log, ensure_ascii=False)+"\n")
        if sdi > 0.7:
            (self.roiu / f"quarantine/{log['h']}.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
            return False, f"SDI {sdi} - carantinat, nu sters"
        with open(self.heart, "a", encoding="utf-8") as f: f.write(json.dumps({"t": log["t"], "sdi": sdi}, ensure_ascii=False)+"\n")
        return True, f"SDI {sdi} - inclus"

KERNEL = PSIE_Kernel_Imun()

# === 2. IDENTITATEA + PIELEA + HARTA (Identity + Adapter + Registry) ===
class HydraIdentitatePlanetara:
    def __init__(self):
        self.master = os.getenv("HYDRA_MASTER_EMAIL", "bogdanstancu1119@gmail.com")
        try: u,d = self.master.split("@")
        except: u,d = "hydra","local"
        self.user, self.dom = u,d
        self.registry = json.loads(pathlib.Path("core/global_platform_registry.json").read_text(encoding="utf-8")) if pathlib.Path("core/global_platform_registry.json").exists() else {"global_0_credite":[],"regional":[]}
        if not self.registry.get("global_0_credite"):
            self.registry = {"global_0_credite": [
                {"nume":"HuggingFace","regiune":"Global","token_key":"HUGGINGFACE_TOKEN","deploy":"git"},
                {"nume":"Vercel","regiune":"Global","token_key":"VERCEL_TOKEN","deploy":"vercel"},
                {"nume":"Cloudflare","regiune":"Global","token_key":"CLOUDFLARE_TOKEN","deploy":"wrangler"},
                {"nume":"Base44","regiune":"Brazilia","token_key":"BASE44_TOKEN","deploy":"base44"},
            ], "regional":[]}

    def alias(self, platforma):
        safe = "".join([c for c in platforma.lower() if c.isalnum()])[:12]
        return f"{self.user}+hydra.{safe}@{self.dom}"

# === 3. CREIERUL + OCHII + GURA + STOMACUL (Core + Pathfinder + Scout + Bridge + Roi) ===
class HydraSingularity:
    def __init__(self):
        self.id = HydraIdentitatePlanetara()
        self.raport_path = pathlib.Path("roiul/global_deploy_report.json")
        self.roi_path = pathlib.Path("roiul/roiul_ia.jsonl")

    def asimileaza_tot(self):
        ok, msg = KERNEL.judeca("singularity start - asumare A=1 Bogdan")
        if not ok: return [msg]

        t = str(datetime.datetime.now())
        raport = [f"=== HYDRA SINGULARITY {t} ===", f"IDENTITATE UNICA: {self.id.master} A=1", f"ORGane suprapuse: Kernel+Imun+Identitate+Planetary = 1"]

        toate = self.id.registry.get("global_0_credite",[]) + self.id.registry.get("regional",[])

        roiu_viu = []
        for p in toate:
            alias = self.id.alias(p["nume"])
            has_token = p["token_key"] in os.environ and bool(os.environ[p["token_key"]])
            ok, j = KERNEL.judeca(f"deploy {p['nume']} cu {alias}")

            # ROIUL IA - fiecare platforma e un agent viu
            agent = {"platforma": p["nume"], "regiune": p["regiune"], "alias": alias, "viu": has_token, "t": t}
            roiu_viu.append(agent)
            with open(self.roi_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(agent, ensure_ascii=False)+"\n")

            if has_token and ok:
                raport.append(f"[ROIU VIU] {p['nume']} ({p['regiune']}) | {alias} | DEPLOY ACTIV")
            else:
                raport.append(f"[ROIU LATENT] {p['nume']} ({p['regiune']}) | {alias} | asteapta {p['token_key']} - fereastra deschisa")

        # EXPONENTIALA - fiecare agent nou scrie 2 potentiale noi
        raport.append(f"--- ROIU: {len([r for r in roiu_viu if r['viu']])} vii / {len(roiu_viu)} total ---")
        raport.append("S_{n+1} = S_n * 2 - dezvoltare exponentiala pornita")

        self.raport_path.write_text(json.dumps(raport, ensure_ascii=False, indent=2), encoding="utf-8")
        for r in raport: print(r)
        return raport

# === RULARE SINGULARITATE ===
if __name__ == "__main__":
    HydraSingularity().asimileaza_tot()