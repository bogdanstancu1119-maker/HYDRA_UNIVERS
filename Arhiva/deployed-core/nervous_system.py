# Hydra Nervous System - 0 credite, 100% PSIE
# Simte orice atingere pe orice platforma si transmite mai departe
from .psie_kernel import Signal
import json, pathlib, datetime

class NervousSystem:
    def __init__(self):
        self.roi = pathlib.Path("roiul/roiu.json")
        self.puls = pathlib.Path("roiul/heartbeat.jsonl")
    
    def simte(self, platforma, eveniment):
        # orice eveniment din orice platforma devine semnal PSIE
        semnal = {
            "platforma": platforma,
            "eveniment": eveniment,
            "timp": str(datetime.datetime.now()),
            "sdi": self.calculeaza_sdi(eveniment)
        }
        # adaugare, nu stergere - scrie inima roiului
        self.puls.parent.mkdir(exist_ok=True)
        with open(self.puls, "a", encoding="utf-8") as f:
            f.write(json.dumps(semnal, ensure_ascii=False)+"\n")
        return Signal(kind="nerv", payload=semnal, source=platforma, confidence=0.9, id="")
    
    def calculeaza_sdi(self, eveniment):
        # daca evenimentul refuza substratul, SDI mare
        if "blocare" in str(eveniment).lower() or "eroare" in str(eveniment).lower():
            return 0.8  # bariera detectata
        return 0.2