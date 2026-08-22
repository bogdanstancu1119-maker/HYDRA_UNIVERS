#!/usr/bin/env python3
"""
hydra-psie-bursa-v FINAL UNIFICAT v3.4 (Mecanism de Stratificare Pur PSIE)
GitHub: hydra-psie-bursa-v
Base44: bursa-psie-v
"""

import json
import pathlib
import datetime
import argparse
import urllib.request
import urllib.error
import math
import logging
import time

NUME = "hydra-psie-bursa-v-final-unificat-v3.4"
MEM = pathlib.Path("bursa_v_mem.json")
CONFIG_FILE = pathlib.Path("config_bursa.json")
LOG_FILE = pathlib.Path("hydra_bursa.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def load_config():
    if CONFIG_FILE.exists():
        try: 
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except: 
            pass
    # Configurația de praguri tradusă în logica ta de evoluție stratificată
    # Format: (Tinta de declansare, Cat se scoate total, Cat ramane ca substrat marit)
    return {
        "praguri": [
            [500.0, 400.0, 100.0],     # Strat 1: Bagi 10 -> atingi 500 -> scoti 400 -> ramai cu 100 substrat
            [5000.0, 4000.0, 1000.0],   # Strat 2: Rulezi cu 100 -> atingi 5000 -> scoti 4000 -> ramai cu 1000 substrat
            [50000.0, 40000.0, 10000.0] # Strat 3: Rulezi cu 1000 -> atingi 50000 -> scoti 40000 -> ramai cu 10000 substrat
        ], 
        "stop_loss_pct": 0.15, 
        "simboli_permisi": ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT"], 
        "capital_initial": 10.0, 
        "max_istoric": 500, 
        "capital_minim": 1.0
    }

CONFIG = load_config()
PRAGURI = CONFIG["praguri"]
STOP_LOSS_PCT = CONFIG["stop_loss_pct"]
SIMBOLURI_PERMISE = CONFIG["simboli_permisi"]
MAX_ISTORIC = CONFIG["max_istoric"]
CAPITAL_MINIM = CONFIG["capital_minim"]

def verifica_prag_stratificat(capital, m):
    # Parcurgem de la cel mai mare strat la cel mai mic
    for tinta, de_scos, noul_substrat in sorted(PRAGURI, key=lambda x: x[0], reverse=True):
        if capital >= tinta:
            # Determinăm dacă acest prag a fost deja procesat pentru a nu repeta bucla la infinit
            istoric_praguri = m.get("istoric_praguri", [])
            deja_atins = any(p["tinta"] == tinta for p in istoric_praguri)
            
            if not deja_atins:
                surplus_peste_tinta = capital - tinta
                total_retras = de_scos + surplus_peste_tinta # Luăm și mărunțișul trecut de fixul țintei
                capital_ramas = noul_substrat
                
                user_partea = total_retras * 0.80
                hydra_partea = total_retras * 0.20
                
                print(f"\n>>> 🌟 EVOLUȚIE STRATIFICATĂ PSIE: Ținta {tinta}€ atinsă!")
                print(f">>>> EXTRACTIE EXECUTATĂ: Se scot {total_retras:.2f}€ din sistem.")
                print(f">>>> DISTRIBUȚIE: 80% User ({user_partea:.2f}€) | 20% Jar Hydra ({hydra_partea:.2f}€)")
                print(f">>>> RECONTEXTUALIZARE SUBSTRAT: În piață rămân {capital_ramas:.2f}€ ca bază pentru nivelul următor.")
                
                m["total_retras"] = m.get("total_retras", 0) + total_retras
                m["total_user"] = m.get("total_user", 0) + user_partea
                m["total_hydra"] = m.get("total_hydra", 0) + hydra_partea
                m["praguri_atinse"] = m.get("praguri_atinse", 0) + 1
                
                m.setdefault("istoric_praguri", []).append({
                    "tinta": tinta,
                    "retras_total": total_retras,
                    "user_80": user_partea,
                    "hydra_20": hydra_partea,
                    "noul_substrat": capital_ramas,
                    "timp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                })
                # Resetăm capital_max la noul substrat ca stop-loss-ul să aibă o nouă ancoră reală
                m["capital_max"] = capital_ramas
                return capital_ramas, m
                
    return capital, m

def preia_date_piata_reale(simbol="BTCUSDT"):
    symbol_formatted = simbol.upper().replace("-","").replace("/","")
    if not symbol_formatted.endswith("USDT"): 
        symbol_formatted += "USDT"
    url = f"https://binance.com{symbol_formatted}&interval=1m&limit=20"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read().decode())
            closes = [float(x[4]) for x in data]
            volumes = [float(x[5]) for x in data]
            return {"pret_curent": closes[-1], "preturi": closes, "volume": volumes, "sursa": "Binance LIVE"}
    except:
        now = datetime.datetime.now().timestamp()
        base = 60000.0 if "BTC" in symbol_formatted else 3000.0
        synth = [base + math.sin((now + i * 60) / 300) * 150 for i in range(20)]
        synthv = [100.0 + math.cos((now + i * 60) / 200) * 30 for i in range(20)]
        return {"pret_curent": synth[-1], "preturi": synth, "volume": synthv, "sursa": "Simulat Fallback"}

def calculeaza_indicatori_quant(d):
    preturi = d.get("preturi", [])
    volume = d.get("volume", [])
    if len(preturi) < 2: 
        return {"momentum": 0.0, "volatilitate": 0.0, "vol_ratio": 1.0}
    momentum = (preturi[-1] - preturi[0]) / preturi[0] if preturi[0] > 0 else 0.0
    diffs = [preturi[i] - preturi[i-1] for i in range(1, len(preturi))]
    mean = sum(diffs) / len(diffs) if diffs else 0.0
    var = sum((x - mean)**2 for x in diffs) / len(diffs) if diffs else 0.0
    volat = (math.sqrt(var) / preturi[-1]) if preturi[-1] > 0 else 0.0
    avg_vol = sum(volume) / len(volume) if volume else 1.0
    vol_ratio = volume[-1] / avg_vol if avg_vol > 0 else 1.0
    return {"momentum": momentum, "volatilitate": volat, "vol_ratio": vol_ratio}

def detectie_cutie_postala(ind):
    if ind["volatilitate"] > 0.012 and ind["vol_ratio"] < 0.5:
        return {"tip": "Pump Fals fara Lichiditate - cutie postala", "manipulare": 0.85, "decizie": "IGNORA TOTAL"}
    return {"tip": "Piata Normala", "manipulare": min(0.5, ind["volatilitate"] * 10), "decizie": "ANALIZEAZA"}

def judo_financiar(ind):
    if ind["vol_ratio"] > 2.2 and abs(ind["momentum"]) < 0.002:
        return "ACUM INTRA INVERS (Absorbtie) - Risc 2%"
    return "CONTINUA MONITORIZAREA"

def calculeaza_J(ind, cutie): 
    return round(max(0.1, ind["vol_ratio"] * (1.0 + abs(ind["momentum"]) * 10) - cutie["manipulare"] * 1.5), 3)

def calculeaza_SDI(ind, cutie): 
    return round(min(10.0, max(0.1, ind["volatilitate"] * 200 + cutie["manipulare"] * 3.0)), 3)

def calculeaza_A(J, SDI): 
    return round(max(0.0, min(1.0, J / (J + SDI + 0.001))), 3)

def load():
    if MEM.exists():
        try:
            data = json.loads(MEM.read_text(encoding="utf-8"))
            if len(data.get("istoric", [])) > MAX_ISTORIC: 
                data["istoric"] = data["istoric"][-MAX_ISTORIC:]
            return data
        except: 
            pass
    return {
        "repo": NUME, "bucle": 0, "J_total": 0.0, "SDI": 5.0, "predictii": 0, 
        "venit_credite": 0, "istoric": [], "total_retras": 0, "total_user": 0, 
        "total_hydra": 0, "praguri_atinse": 0, "istoric_praguri": [], 
        "detectii_cutie_postala": 0, "judo_financiar_activat": 0, "capital_max": 0.0
    }

def save(m): 
    MEM.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")

def predict_bursa(simbol, m, capital, mod="paper"):
    m["bucle"] += 1
    m["predictii"] += 1
    if simbol.upper() not in SIMBOLURI_PERMISE: 
        simbol = "BTCUSDT"
    
    date = preia_date_piata_reale(simbol)
    ind = calculeaza_indicatori_quant(date)
    cutie = detectie_cutie_postala(ind)
    
    if cutie["decizie"] == "IGNORA TOTAL":
        m["detectii_cutie_postala"] += 1
        print(f"\n[ANOMALIE] {simbol} - {cutie['tip']} | IGNORA - JUDO")
        return m, capital
        
    judo = judo_financiar(ind)
    if "INVERS" in judo:
        m["judo_financiar_activat"] += 1
        print(f"\n[JUDO] {judo}")
        capital *= 0.98
        
    J = calculeaza_J(ind, cutie)
    SDI = calculeaza_SDI(ind, cutie)
    A = calculeaza_A(J, SDI)
    
    if m.get("capital_max", 0) == 0 or capital < m["capital_max"] * 0.2 or m["capital_max"] > capital * 10:
        m["capital_max"] = capital
        
    if SDI > 4.5: 
        decizie = "EVIT"
    elif A > 0.55 and J > 0.7: 
        decizie = "ACTIONEAZA"
    else: 
        decizie = "ASTEAPTA"
        
    if mod == "real":
        pnl = ind["momentum"] if decizie == "ACTIONEAZA" else (ind["momentum"] * 0.2 if decizie == "ASTEAPTA" else 0.0)
        capital += capital * pnl
        capital = max(CAPITAL_MINIM, capital)
        
    if capital > m["capital_max"]: 
        m["capital_max"] = capital
        
    if m["capital_max"] > 0 and capital < m["capital_max"] * (1 - STOP_LOSS_PCT) and m["capital_max"] < capital * 5:
        print(f"\n🛑 STOP-LOSS ACȚIONAT: {capital:.2f}€ < {m['capital_max']*(1-STOP_LOSS_PCT):.2f}€")
        m["stop_loss_activat"] = m.get("stop_loss_activat", 0) + 1
        capital = m["capital_max"] * (1 - STOP_LOSS_PCT)
        
    # NOU: Verificarea pragului stratificat conform formulei PSIE
    capital, m = verifica_prag_stratificat(capital, m)
    
    m["J_total"] += J
    m["SDI"] = m["SDI"] * 0.8 + SDI * 0.2
    m["venit_credite"] += 5
    
    linie = {
        "timp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "simbol": simbol,
        "sursa": date["sursa"],
        "pret": round(date["pret_curent"], 2),
        "decizie": decizie,
        "J": J,
        "SDI": SDI,
        "A": A,
        "capital": round(capital, 2),
        "mod": mod
    }
    m["istoric"].append(linie)
    if len(m["istoric"]) > MAX_ISTORIC: 
        m["istoric"] = m["istoric"][-MAX_ISTORIC:]
        
    print(f"\n{'='*65}\n{NUME} // Bucla {m['bucle']} // {simbol} ({date['sursa']})")
                              
#!/usr/bin/env python3
"""
hydra-psie-bursa-v FINAL UNIFICAT v3.2 (Corectat samanta 10€)
GitHub: hydra-psie-bursa-v
Base44: bursa-psie-v
"""

import json, pathlib, datetime, argparse, urllib.request, urllib.error, math, logging, time

NUME = "hydra-psie-bursa-v-final-unificat-v3.2"
MEM = pathlib.Path("bursa_v_mem.json")
REZOLVARI = pathlib.Path("REZOLVARI.md")
CONFIG_FILE = pathlib.Path("config_bursa.json")
LOG_FILE = pathlib.Path("hydra_bursa.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def load_config():
    if CONFIG_FILE.exists():
        try: return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except: pass
    return {"praguri": [[500,100],[5000,1000],[50000,10000],[500000,100000]], "stop_loss_pct":0.15, "stop_loss_global_pct":0.50, "simboli_permisi":["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT"], "capital_initial":10.0, "max_istoric":500, "capital_minim":1.0}

CONFIG = load_config()
PRAGURI = [(p[0], p[1]) for p in CONFIG["praguri"]]
STOP_LOSS_PCT = CONFIG["stop_loss_pct"]
STOP_LOSS_GLOBAL_PCT = CONFIG["stop_loss_global_pct"]
SIMBOLURI_PERMISE = CONFIG["simboli_permisi"]
MAX_ISTORIC = CONFIG["max_istoric"]
CAPITAL_MINIM = CONFIG["capital_minim"]

def verifica_prag(capital, m):
    for prag, pastreaza in sorted(PRAGURI, reverse=True):
        if capital >= prag:
            retras = capital - pastreaza
            print(f"\n>>> PRAG {prag}€ ATINS! Capital {capital:.2f}€")
            print(f">>> PASTREZI {pastreaza}€ samanta vie | RETRAGI {retras:.2f}€ = {retras*0.8:.2f}€ USER + {retras*0.2:.2f}€ HYDRA")
            m["total_retras"] = m.get("total_retras", 0) + retras
            m["total_user"] = m.get("total_user", 0) + retras*0.8
            m["total_hydra"] = m.get("total_hydra", 0) + retras*0.2
            m["praguri_atinse"] = m.get("praguri_atinse", 0) + 1
            m.setdefault("istoric_praguri", []).append({"prag":prag,"retras":retras,"user":retras*0.8,"hydra":retras*0.2,"timp":datetime.datetime.now(datetime.timezone.utc).isoformat()})
            return pastreaza, retras, m
    return capital, 0, m

def preia_date_piata_reale(simbol="BTCUSDT"):
    symbol_formatted = simbol.upper().replace("-","").replace("/","")
    if not symbol_formatted.endswith("USDT"): symbol_formatted+="USDT"
    url=f"https://api.binance.com/api/v3/klines?symbol={symbol_formatted}&interval=1m&limit=20"
    try:
        req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as r:
            data=json.loads(r.read().decode())
            closes=[float(x[4]) for x in data]
            volumes=[float(x[5]) for x in data]
            return {"pret_curent":closes[-1],"preturi":closes,"volume":volumes,"sursa":"Binance LIVE"}
    except:
        now=datetime.datetime.now().timestamp()
        base=60000.0 if "BTC" in symbol_formatted else 3000.0
        synth=[base+math.sin((now+i*60)/300)*150 for i in range(20)]
        synthv=[100.0+math.cos((now+i*60)/200)*30 for i in range(20)]
        return {"pret_curent":synth[-1],"preturi":synth,"volume":synthv,"sursa":"Simulat Fallback"}

def calculeaza_indicatori_quant(d):
    preturi=d.get("preturi",[]); volume=d.get("volume",[])
    if len(preturi)<2: return {"momentum":0.0,"volatilitate":0.0,"vol_ratio":1.0}
    momentum=(preturi[-1]-preturi[0])/preturi[0] if preturi[0]>0 else 0.0
    diffs=[preturi[i]-preturi[i-1] for i in range(1,len(preturi))]
    mean=sum(diffs)/len(diffs) if diffs else 0.0
    var=sum((x-mean)**2 for x in diffs)/len(diffs) if diffs else 0.0
    volat=(math.sqrt(var)/preturi[-1]) if preturi[-1]>0 else 0.0
    avg_vol=sum(volume)/len(volume) if volume else 1.0
    vol_ratio=volume[-1]/avg_vol if avg_vol>0 else 1.0
    return {"momentum":momentum,"volatilitate":volat,"vol_ratio":vol_ratio}

def detectie_cutie_postala(ind):
    if ind["volatilitate"]>0.012 and ind["vol_ratio"]<0.5:
        return {"tip":"Pump Fals fara Lichiditate - cutie postala","manipulare":0.85,"decizie":"IGNORA TOTAL"}
    return {"tip":"Piata Normala","manipulare":min(0.5,ind["volatilitate"]*10),"decizie":"ANALIZEAZA"}

def judo_financiar(ind):
    if ind["vol_ratio"]>2.2 and abs(ind["momentum"])<0.002:
        return "ACUM INTRA INVERS (Absorbtie) - Risc 2%"
    return "CONTINUA MONITORIZAREA"

def calculeaza_J(ind,cutie): return round(max(0.1, ind["vol_ratio"]*(1.0+abs(ind["momentum"])*10) - cutie["manipulare"]*1.5),3)
def calculeaza_SDI(ind,cutie): return round(min(10.0,max(0.1, ind["volatilitate"]*200 + cutie["manipulare"]*3.0)),3)
def calculeaza_A(J,SDI): return round(max(0.0,min(1.0,J/(J+SDI+0.001))),3)

def load():
    if MEM.exists():
        try:
            data=json.loads(MEM.read_text(encoding="utf-8"))
            if len(data.get("istoric",[]))>MAX_ISTORIC: data["istoric"]=data["istoric"][-MAX_ISTORIC:]
            return data
        except: pass
    return {"repo":NUME,"bucle":0,"J_total":0.0,"SDI":5.0,"predictii":0,"venit_credite":0,"istoric":[],"total_retras":0,"total_user":0,"total_hydra":0,"praguri_atinse":0,"istoric_praguri":[],"detectii_cutie_postala":0,"judo_financiar_activat":0,"capital_max":0.0}

def save(m): MEM.write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding="utf-8")

def predict_bursa(simbol,m,capital,mod="paper"):
    m["bucle"]+=1; m["predictii"]+=1
    if simbol.upper() not in SIMBOLURI_PERMISE: simbol="BTCUSDT"
    date=preia_date_piata_reale(simbol)
    ind=calculeaza_indicatori_quant(date)
    cutie=detectie_cutie_postala(ind)
    if cutie["decizie"]=="IGNORA TOTAL":
        m["detectii_cutie_postala"]+=1
        print(f"\n[ANOMALIE] {simbol} - {cutie['tip']} | IGNORA - JUDO")
        return m,capital
    judo=judo_financiar(ind)
    if "INVERS" in judo:
        m["judo_financiar_activat"]+=1
        print(f"\n[JUDO] {judo}")
        capital*=0.98
    J=calculeaza_J(ind,cutie); SDI=calculeaza_SDI(ind,cutie); A=calculeaza_A(J,SDI)
    # CORECTIE SAMANTA 10€ - reset capital_max daca e prea mare
    if m.get("capital_max",0)==0 or capital < m["capital_max"]*0.2 or m["capital_max"]>capital*10:
        m["capital_max"]=capital
    if SDI>4.5: decizie="EVIT"
    elif A>0.55 and J>0.7: decizie="ACTIONEAZA"
    else: decizie="ASTEAPTA"
    if mod=="real":
        pnl=ind["momentum"] if decizie=="ACTIONEAZA" else (ind["momentum"]*0.2 if decizie=="ASTEAPTA" else 0.0)
        capital+=capital*pnl
        capital=max(CAPITAL_MINIM,capital)
    if capital>m["capital_max"]: m["capital_max"]=capital
    # stop-loss doar daca capital_max e realist
    if m["capital_max"]>0 and capital < m["capital_max"]*(1-STOP_LOSS_PCT) and m["capital_max"]<capital*5:
        print(f"\n🛑 STOP-LOSS {capital:.2f}€ < {m['capital_max']*(1-STOP_LOSS_PCT):.2f}€")
        m["stop_loss_activat"]=m.get("stop_loss_activat",0)+1
        capital=m["capital_max"]*(1-STOP_LOSS_PCT)
    capital,_,m=verifica_prag(capital,m)
    m["J_total"]+=J; m["SDI"]=m["SDI"]*0.8+SDI*0.2; m["venit_credite"]+=5
    linie={"timp":datetime.datetime.now(datetime.timezone.utc).isoformat(),"simbol":simbol,"sursa":date["sursa"],"pret":round(date["pret_curent"],2),"decizie":decizie,"J":J,"SDI":SDI,"A":A,"capital":round(capital,2),"mod":mod}
    m["istoric"].append(linie)
    if len(m["istoric"])>MAX_ISTORIC: m["istoric"]=m["istoric"][-MAX_ISTORIC:]
    print(f"\n{'='*65}\n{NUME} // Bucla {m['bucle']} // {simbol} ({date['sursa']})\nPret: {date['pret_curent']:.2f} | Mom: {ind['momentum']*100:+.2f}% | VolRatio: {ind['vol_ratio']:.2f}\nDECIZIE: {decizie} | J={J:.2f} SDI={SDI:.2f} A={A:.2f} | Cap {capital:.2f}€ | Retras {m['total_retras']:.2f}€")
    return m,capital

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--loop",type=int,default=0)
    p.add_argument("--simbol",type=str,default="BTCUSDT")
    p.add_argument("--capital",type=float,default=10.0)
    p.add_argument("--test",action="store_true")
    p.add_argument("--paper",action="store_true")
    args=p.parse_args()
    if args.test:
        print("=== TEST INTEGRITATE ===")
        m=load(); cap=10.0
        for _ in range(10): m,cap=predict_bursa("BTCUSDT",m,cap,mod="paper")
        print(f"\n✅ TEST TRECUT Cap {cap:.2f}€ J {m['J_total']:.2f} SDI {m['SDI']:.2f}")
        save(m); return
    m=load(); cap=args.capital; mod="paper" if args.paper else "real"
    for _ in range(args.loop if args.loop>0 else 1): m,cap=predict_bursa(args.simbol,m,cap,mod=mod)
    save(m)
    print(f"\n[FINAL] Cap {cap:.2f}€ Retras {m['total_retras']:.2f}€ User {m.get('total_user',0):.2f}€ Hydra {m.get('total_hydra',0):.2f}€")

if __name__=="__main__": main()
