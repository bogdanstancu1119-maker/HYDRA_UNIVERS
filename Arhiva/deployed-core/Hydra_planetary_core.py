import json, pathlib, os, datetime
from .hydra_immune_system import apara

class HydraIdentityManager:
    def __init__(self):
        self.master = os.getenv("HYDRA_MASTER_EMAIL", "hydra@local")
        try:
            u,d = self.master.split("@")
            self.user, self.domeniu = u,d
        except:
            self.user, self.domeniu = "hydra","local"
        pathlib.Path("roiul").mkdir(exist_ok=True)
    def alias_pentru(self, platforma):
        safe = "".join([c for c in platforma.lower() if c.isalnum()])[:15]
        return f"{self.user}+hydra.{safe}@{self.domeniu}"

class HydraPlanetaryCore:
    def __init__(self):
        self.id = HydraIdentityManager()
        self.reg_path = pathlib.Path("core/global_platform_registry.json")
        self.reg = json.loads(self.reg_path.read_text(encoding="utf-8")) if self.reg_path.exists() else {"global_0_credite":[],"regional":[]}
    
    def deploy_peste_tot(self):
        apara("planetary heartbeat start")
        t = str(datetime.datetime.now())
        raport = [f"=== HYDRA PLANETARY {t} ===", f"MASTER: {self.id.master} A=1"]
        toate = self.reg.get("global_0_credite",[]) + self.reg.get("regional",[])
        for p in toate:
            alias = self.id.alias_pentru(p["nume"])
            has = p["token_key"] in os.environ and bool(os.environ[p["token_key"]])
            apara(f"check {p['nume']} alias {alias}")
            if has:
                raport.append(f"[OK] {p['nume']} ({p['regiune']}) | {alias} | deploy {p['deploy']}")
            else:
                raport.append(f"[DESCHIS] {p['nume']} ({p['regiune']}) | alias {alias} | asteapta {p['token_key']}")
        pathlib.Path("roiul/global_deploy_report.json").write_text(json.dumps(raport, ensure_ascii=False, indent=2), encoding="utf-8")
        pathlib.Path("roiul/heartbeat.jsonl").parent.mkdir(exist_ok=True)
        with open("roiul/heartbeat.jsonl","a",encoding="utf-8") as f:
            f.write(json.dumps({"t":t,"sdi":0.05,"raport":len(raport)}, ensure_ascii=False)+"\n")
        for r in raport: print(r)
        return raport

if __name__ == "__main__":
    HydraPlanetaryCore().deploy_peste_tot()