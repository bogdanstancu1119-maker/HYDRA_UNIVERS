import json, pathlib, datetime, hashlib
class HydraImmuneSystem:
    def __init__(self):
        self.imun = pathlib.Path("roiul/imunitar.jsonl")
        self.quarantine = pathlib.Path("roiul/quarantine/")
        self.quarantine.mkdir(parents=True, exist_ok=True)
        self.imun.parent.mkdir(exist_ok=True)
    def calculeaza_sdi(self, ev):
        e = str(ev).lower()
        if "delete" in e and "archive" not in e: return 0.95
        if "fake" in e: return 0.9
        if "verification" in e: return 0.15
        return 0.4
    def detecteaza(self, eveniment):
        sdi = self.calculeaza_sdi(eveniment)
        log = {"t": str(datetime.datetime.now()), "ev": eveniment, "SDI": sdi, "hash": hashlib.sha256(str(eveniment).encode()).hexdigest()[:8]}
        with open(self.imun, "a", encoding="utf-8") as f: f.write(json.dumps(log, ensure_ascii=False)+"\n")
        if sdi > 0.7:
            (self.quarantine / f"{log['hash']}.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"actiune": "quarantine+backup", "SDI": sdi}
        return {"actiune": "inclus", "SDI": sdi}
IMMUNE = HydraImmuneSystem()
def apara(op): return IMMUNE.detecteaza(op)