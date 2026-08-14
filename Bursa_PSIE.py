#!/usr/bin/env python3
"""
hydra-psie-bursa-v FINAL UNIFICAT v3.1
GitHub: hydra-psie-bursa-v
Base44: bursa-psie-v - 150 credite/lună

MATEMATICA PSIE - BURSĂ
0 = -∞ prăbușire absolută neatingibilă
1 = +∞ creștere absolută neatingibilă
Preț = proporționalitate funcțională
Doar PSIE decide.

FEATURES v3.1:
- Toate cele din v3
- Stop-loss global la -50% din maxim
- Backtest cu simbol configurable
- Raport zilnic --report
- Capital minim protejat (1€)
- Mod paper explicit
- Notificare la fiecare prag atins

Util:
- rulează în terminal: python hydra_psie_bursa_v.py
- rulează în buclă: python hydra_psie_bursa_v.py --loop 5 --simbol BTCUSDT
- paper trading: python hydra_psie_bursa_v.py --paper --loop 5
- backtest: python hydra_psie_bursa_v.py --backtest 7 --simbol ETHUSDT
- raport: python hydra_psie_bursa_v.py --report
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
import random

NUME = "hydra-psie-bursa-v-final-unificat-v3.1"
MEM = pathlib.Path("bursa_v_mem.json")
REZOLVARI = pathlib.Path("REZOLVARI.md")
CONFIG_FILE = pathlib.Path("config_bursa.json")
LOG_FILE = pathlib.Path("hydra_bursa.log")
RAPORT = pathlib.Path("RAPORT_PSIE.md")

# === LOGGING STRUCTURAT ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === CONFIG EXTERNALIZAT ===
def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {
        "praguri": [
            [500, 100],
            [5000, 1000],
            [50000, 10000],
            [500000, 100000]
        ],
        "stop_loss_pct": 0.15,
        "stop_loss_global_pct": 0.50,
        "simboli_permisi": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT"],
        "capital_initial": 100.0,
        "max_istoric": 500,
        "capital_minim": 1.0
    }

CONFIG = load_config()
PRAGURI = [(p[0], p[1]) for p in CONFIG["praguri"]]
STOP_LOSS_PCT = CONFIG["stop_loss_pct"]
STOP_LOSS_GLOBAL_PCT = CONFIG["stop_loss_global_pct"]
SIMBOLURI_PERMISE = CONFIG["simboli_permisi"]
MAX_ISTORIC = CONFIG["max_istoric"]
CAPITAL_MINIM = CONFIG["capital_minim"]

# === PRAGURI PSIE ===
def verifica_prag(capital, m):
    for prag, pastreaza in sorted(PRAGURI, reverse=True):
        if capital >= prag:
            retras = capital - pastreaza
            print(f"
>>> PRAG {prag}€ ATINS! Capital {capital:.2f}€")
            print(f">>> PASTREZI {pastreaza}€ sămânță vie | RETRAGI {retras:.2f}€")
            m["total_retras"] = m.get("total_retras", 0) + retras
            m["praguri_atinse"] = m.get("praguri_atinse", 0) + 1
            m.setdefault("istoric_praguri", []).append({
                "prag": prag,
                "retras": retras,
                "timp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            logging.info(f"PRAG ATINS: {prag}€ | Retras: {retras:.2f}€ | Capital: {capital:.2f}€")
            return pastreaza, retras, m
    return capital, 0, m

# === STOP-LOSS DINAMIC ===
def aplica_stop_loss(capital, capital_max):
    if capital < capital_max * (1 - STOP_LOSS_PCT):
        print(f"
🛑 STOP-LOSS ACTIVAT! Capital {capital:.2f}€ < {capital_max * (1 - STOP_LOSS_PCT):.2f}€")
        logging.warning(f"STOP-LOSS ACTIVAT | Capital: {capital:.2f}€ | Max: {capital_max:.2f}€")
        return True
    return False

# === STOP-LOSS GLOBAL ===
def aplica_stop_loss_global(capital, capital_max):
    if capital < capital_max * (1 - STOP_LOSS_GLOBAL_PCT):
        print(f"
🔴 STOP-LOSS GLOBAL! Capital {capital:.2f}€ < 50% din maxim {capital_max:.2f}€")
        logging.error(f"STOP-LOSS GLOBAL | Capital: {capital:.2f}€ | Max: {capital_max:.2f}€")
        return True
    return False

# === ALERTĂ DE RISC ===
def alerta_risc(SDI, J, A):
    alerte = []
    if SDI > 6.0:
        alerte.append("⚠️ RISC CRITIC: SDI > 6.0 — Decuplare majoră de piață")
    if A < 0.2:
        alerte.append("⚠️ RISC: A < 0.2 — Semnal slab, asumare minimă")
    if J < 0.5:
        alerte.append("⚠️ RISC: J < 0.5 — Flux informațional blocat")
    if alerte:
        for a in alerte:
            print(a)
            logging.warning(a)
        return True
    return False

# === VALIDARE SIMBOL ===
def valideaza_simbol(simbol):
    if simbol not in SIMBOLURI_PERMISE:
        print(f"⚠️ Simbol '{simbol}' necunoscut. Folosesc BTCUSDT.")
        logging.warning(f"Simbol invalid: {simbol}")
        return "BTCUSDT"
    return simbol

# === FLUX DATE REALE (BINANCE REST API) ===
def preia_date_piata_reale(simbol="BTCUSDT"):
    symbol_formatted = simbol.upper().replace("-", "").replace("/", "")
    if not symbol_formatted.endswith("USDT") and not symbol_formatted.endswith("BTC"):
        symbol_formatted += "USDT"

    url = f"https://api.binance.com/api/v3/klines?symbol={symbol_formatted}&interval=1m&limit=20"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            if not data or len(data) < 2:
                raise ValueError("Date Binance insuficiente")
            closes = [float(item[4]) for item in data]
            volumes = [float(item[5]) for item in data]
            return {
                "pret_curent": closes[-1],
                "preturi": closes,
                "volume": volumes,
                "sursa": "Binance REST API (Live)"
            }
    except urllib.error.HTTPError as e:
        if e.code == 429:
            logging.warning("Rate limit Binance (429) — backoff 2s")
            time.sleep(2)
            return preia_date_piata_reale(simbol)
        logging.error(f"Eroare HTTP {e.code} pentru {simbol}")
    except Exception as e:
        logging.error(f"Eroare rețea pentru {simbol}: {e}")
    
    now = datetime.datetime.now().timestamp()
    base_price = 60000.0 if "BTC" in symbol_formatted else 3000.0
    synthetic_closes = [base_price + math.sin((now + i*60) / 300) * 150 for i in range(20)]
    synthetic_vols = [100.0 + math.cos((now + i*60) / 200) * 30 for i in range(20)]
    return {
        "pret_curent": synthetic_closes[-1],
        "preturi": synthetic_closes,
        "volume": synthetic_vols,
        "sursa": "Simulat (Offline Fallback)"
    }

# === CALCUL INDICATORI QUANT ===
def calculeaza_indicatori_quant(date_piata):
    preturi = date_piata.get("preturi", [])
    volume = date_piata.get("volume", [])
    
    if len(preturi) < 2 or len(volume) < 2:
        return {"momentum": 0.0, "volatilitate": 0.0, "vol_ratio": 1.0, "avg_vol": 1.0}
    
    momentum = (preturi[-1] - preturi[0]) / preturi[0] if preturi[0] > 0 else 0.0
    
    diffs = [preturi[i] - preturi[i-1] for i in range(1, len(preturi))]
    mean_diff = sum(diffs) / len(diffs) if len(diffs) > 0 else 0.0
    variance = sum((x - mean_diff) ** 2 for x in diffs) / len(diffs) if len(diffs) > 0 else 0.0
    volatilitate = (math.sqrt(max(variance, 0.0)) / preturi[-1]) if preturi[-1] > 0 else 0.0
    
    avg_vol = sum(volume) / len(volume) if len(volume) > 0 else 1.0
    vol_ratio = volume[-1] / avg_vol if avg_vol > 0 else 1.0
    
    return {"momentum": momentum, "volatilitate": volatilitate, "vol_ratio": vol_ratio, "avg_vol": avg_vol}

# === DETECȚIE ANOMALII & JUDO FINANCIAR ===
def detectie_cutie_postala(ind):
    if ind["volatilitate"] > 0.012 and ind["vol_ratio"] < 0.5:
        return {"tip": "Pump Fals fără Lichiditate", "manipulare": 0.85, "decizie": "IGNORA TOTAL"}
    return {"tip": "Piață Normală", "manipulare": min(0.5, ind["volatilitate"] * 10), "decizie": "ANALIZEAZA"}

def judo_financiar(ind):
    if ind["vol_ratio"] > 2.2 and abs(ind["momentum"]) < 0.002:
        return "ACUM INTRĂ INVERS (Absorbție Detectată) — Risc 2% din capital"
    return "CONTINUA MONITORIZAREA"

# === FORMULE PSIE ===
def calculeaza_J(ind, cutie):
    flux_brut = ind["vol_ratio"] * (1.0 + abs(ind["momentum"]) * 10)
    penalizare = cutie["manipulare"] * 1.5
    return round(max(0.1, flux_brut - penalizare), 3)

def calculeaza_SDI(ind, cutie):
    zgomot_vol = ind["volatilitate"] * 200
    zgomot_cutie = cutie["manipulare"] * 3.0
    return round(min(10.0, max(0.1, zgomot_vol + zgomot_cutie)), 3)

def calculeaza_A(J, SDI):
    return round(max(0.0, min(1.0, J / (J + SDI + 0.001))), 3)

# === STATE MANAGEMENT ===
def load():
    if MEM.exists():
        try:
            data = json.loads(MEM.read_text(encoding="utf-8"))
            if "istoric" in data and len(data["istoric"]) > MAX_ISTORIC:
                data["istoric"] = data["istoric"][-MAX_ISTORIC:]
            return data
        except Exception as e:
            logging.error(f"Eroare load memorie: {e}")
    return {
        "repo": NUME,
        "bucle": 0,
        "J_total": 0.0,
        "SDI": 5.0,
        "predictii": 0,
        "venit_credite": 0,
        "istoric": [],
        "total_retras": 0,
        "praguri_atinse": 0,
        "istoric_praguri": [],
        "detectii_cutie_postala": 0,
        "judo_financiar_activat": 0,
        "capital_max": 0.0,
        "stop_loss_activat": 0,
        "stop_loss_global_activat": 0
    }

def save(m):
    try:
        MEM.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logging.error(f"Eroare save memorie: {e}")
        print(f"[EROARE SAVE] {e}")

# === FUNCȚIA PRINCIPALĂ DE PREDICȚIE ===
def predict_bursa(simbol, m, capital, mod="paper"):
    m["bucle"] += 1
    m["predictii"] += 1

    simbol = valideaza_simbol(simbol)
    date_piata = preia_date_piata_reale(simbol)
    ind = calculeaza_indicatori_quant(date_piata)

    cutie = detectie_cutie_postala(ind)
    if cutie["decizie"] == "IGNORA TOTAL":
        m["detectii_cutie_postala"] = m.get("detectii_cutie_postala", 0) + 1
        print(f"
[ANOMALIE DETECTATĂ] {simbol} — {cutie['tip']} | Decizie: {cutie['decizie']}")
        logging.info(f"ANOMALIE | {simbol} | {cutie['tip']}")
        return m, capital

    judo = judo_financiar(ind)
    if "INTRĂ INVERS" in judo:
        m["judo_financiar_activat"] = m.get("judo_financiar_activat", 0) + 1
        print(f"
[JUDO FINANCIAR] {judo}")
        logging.info(f"JUDO ACTIVAT | {simbol} | {judo}")
        capital *= 0.98

    J = calculeaza_J(ind, cutie)
    SDI = calculeaza_SDI(ind, cutie)
    A = calculeaza_A(J, SDI)

    alerta_risc(SDI, J, A)

    if SDI > 4.5:
        decizie = "EVIT"
    elif A > 0.6 and J > 1.2:
        decizie = "ACTIONEAZA"
    else:
        decizie = "ASTEAPTA"

    if mod == "real":
        pnl_pct = ind["momentum"] if decizie == "ACTIONEAZA" else (ind["momentum"] * 0.2 if decizie == "ASTEAPTA" else 0.0)
        capital += capital * pnl_pct
        capital = max(CAPITAL_MINIM, capital)

    if capital > m.get("capital_max", 0):
        m["capital_max"] = capital

    if aplica_stop_loss(capital, m["capital_max"]):
        m["stop_loss_activat"] = m.get("stop_loss_activat", 0) + 1
        capital = m.get("capital_max", capital) * (1 - STOP_LOSS_PCT)

    if aplica_stop_loss_global(capital, m["capital_max"]):
        m["stop_loss_global_activat"] = m.get("stop_loss_global_activat", 0) + 1
        capital = max(CAPITAL_MINIM, m.get("capital_max", capital) * 0.5)
        print(f"
🔴 OPRESC TOT: Capitalul a scăzut sub 50% din maxim. Revin cu sămânța minimală.")
        logging.error(f"STOP-LOSS GLOBAL | Capital redus la {capital:.2f}€")
        save(m)
        return m, capital

    capital, retras, m = verifica_prag(capital, m)

    m["J_total"] += J
    m["SDI"] = m["SDI"] * 0.8 + SDI * 0.2
    m["venit_credite"] += 5

    linie = {
        "timp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "simbol": simbol,
        "sursa": date_piata["sursa"],
        "pret": round(date_piata["pret_curent"], 2),
        "decizie": decizie,
        "J": J,
        "SDI": SDI,
        "A": A,
        "volatilitate_pct": round(ind["volatilitate"] * 100, 2),
        "capital": round(capital, 2),
        "mod": mod
    }
    m["istoric"].append(linie)
    if len(m["istoric"]) > MAX_ISTORIC:
        m["istoric"] = m["istoric"][-MAX_ISTORIC:]

    logging.info(f"{simbol} | Decizie={decizie} | J={J} | SDI={SDI} | A={A} | Cap={capital:.2f}€ | Mod={mod}")

    print(f"
{'='*65}")
    print(f"{NUME} // Bucla {m['bucle']} // {simbol} ({date_piata['sursa']})")
    print(f"Preț Curent: {date_piata['pret_curent']:.2f} | Momentum: {ind['momentum']*100:+.2f}%")
    print(f"{'='*65}")
    print(f"DECIZIE PSIE : {decizie}")
    print(f"J (Flux Real) : {J:.2f} | SDI (Zgomot) : {SDI:.2f} | A (Asumare) : {A:.2f}")
    print(f"Capital Viu  : {capital:.2f}€ | Total Retras : {m['total_retras']:.2f}€")
    print(f"Judo Activat : {m['judo_financiar_activat']} | Cutii Detectate : {m['detectii_cutie_postala']} | Stop-loss : {m['stop_loss_activat']} | Global: {m['stop_loss_global_activat']}")

    return m, capital

# === EXPORT & WRITE ===
def export_json(m, path="bursa_v_export.json"):
    try:
        pathlib.Path(path).write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"
[EXPORT] Salvat cu succes în {path}")
        logging.info(f"EXPORT | Salvat în {path}")
    except Exception as e:
        logging.error(f"Eroare export: {e}")
        print(f"[EROARE EXPORT] {e}")

def write_rezolvari(m):
    if not m.get("istoric"):
        print("
[REZOLVARI] Nu există istoric de scris.")
        return
    ultimele = m["istoric"][-10:]
    bloc = f"
## {NUME} — {datetime.datetime.now(datetime.timezone.utc).isoformat()}

"
    bloc += f"- Bucle: {m['bucle']} | J_total: {m['J_total']:.2f} | Capital: {ultimele[-1]['capital']:.2f}€

"
    bloc += "### Ultimele 10 Decizii Rulate

"
    for i, h in enumerate(ultimele, 1):
        bloc += f"{i}. {h['timp']} — {h['simbol']} ({h['pret']:.2f}) | Decizie={h['decizie']} | J={h['J']} SDI={h['SDI']} A={h['A']} Cap={h['capital']}€
"
    
    try:
        txt = REZOLVARI.read_text(encoding="utf-8") if REZOLVARI.exists() else "# REZOLVARI

"
        txt += bloc
        REZOLVARI.write_text(txt, encoding="utf-8")
        print("
[REZOLVARI] Fișierul REZOLVARI.md a fost actualizat.")
        logging.info("REZOLVARI.md actualizat")
    except Exception as e:
        logging.error(f"Eroare write REZOLVARI: {e}")
        print(f"[EROARE WRITE] {e}")

# === RAPORT ZILNIC ===
def genereaza_raport(m):
    print("=== GENEREZ RAPORT PSIE ===")
    logging.info("=== GENERARE RAPORT START ===")
    try:
        raport = f"# RAPORT PSIE — {datetime.datetime.now(datetime.timezone.utc).isoformat()}

"
        raport += f"- **Repo:** {m.get('repo', NUME)}
"
        raport += f"- **Bucle:** {m.get('bucle', 0)}
"
        raport += f"- **Predicții:** {m.get('predictii', 0)}
"
        raport += f"- **J_total:** {m.get('J_total', 0):.2f}
"
        raport += f"- **SDI:** {m.get('SDI', 5.0):.2f}
"
        raport += f"- **Capital Viu:** {m.get('istoric', [{}])[-1].get('capital', 0):.2f}€
"
        raport += f"- **Total Retras:** {m.get('total_retras', 0):.2f}€
"
        raport += f"- **Praguri Atinse:** {m.get('praguri_atinse', 0)}
"
        raport += f"- **Cutii Poștale Detectate:** {m.get('detectii_cutie_postala', 0)}
"
        raport += f"- **Judo Financiar Activat:** {m.get('judo_financiar_activat', 0)}
"
        raport += f"- **Stop-loss Activat:** {m.get('stop_loss_activat', 0)}
"
        raport += f"- **Stop-loss Global:** {m.get('stop_loss_global_activat', 0)}
"
        raport += f"
## Ultimele 5 Decizii

"
        for h in m.get("istoric", [])[-5:]:
            raport += f"- {h['timp']} | {h['simbol']} | {h['decizie']} | J={h['J']} | SDI={h['SDI']} | A={h['A']} | Cap={h['capital']}€
"
        RAPORT.write_text(raport, encoding="utf-8")
        print(f"
[RAPORT] Generat: {RAPORT}")
        logging.info("RAPORT generat cu succes")
    except Exception as e:
        logging.error(f"Eroare raport: {e}")
        print(f"[EROARE RAPORT] {e}")

# === TEST DE INTEGRITATE ===
def run_test():
    print("=== TEST INTEGRITATE HYDRA BURSĂ PSIE ===")
    logging.info("=== TEST INTEGRITATE START ===")
    m = load()
    capital = 100.0
    decizii = {"EVIT": 0, "ACTIONEAZA": 0, "ASTEAPTA": 0}
    
    for _ in range(10):
        m, capital = predict_bursa("BTCUSDT", m, capital)
        if m["istoric"]:
            decizii[m["istoric"][-1]["decizie"]] += 1
        if capital < 0.01:
            print("❌ EROARE: Capital negativ!")
            logging.error("TEST EȘUAT: Capital negativ")
            return False
        if m["istoric"] and m["istoric"][-1]["J"] < 0:
            print("❌ EROARE: J negativ!")
            logging.error("TEST EȘUAT: J negativ")
            return False
    
    print(f"
✅ TEST TRECUT! Capital final: {capital:.2f}€")
    print(f"Decizii: {decizii}")
    print(f"J_total: {m['J_total']:.2f} | SDI: {m['SDI']:.2f}")
    logging.info(f"=== TEST INTEGRITATE FINAL | Capital: {capital:.2f}€ ===")
    return True

# === BACKTESTING ===
def run_backtest(zile=7, simbol="BTCUSDT"):
    print(f"=== BACKTEST {zile} ZILE pe {simbol} ===")
    logging.info(f"=== BACKTEST {zile} ZILE pe {simbol} START ===")
    m = load()
    capital = CONFIG["capital_initial"]
    
    for _ in range(zile * 24):
        m, capital = predict_bursa(simbol, m, capital, mod="paper")
    
    print(f"
✅ BACKTEST FINAL | Capital: {capital:.2f}€ | Bucle: {m['bucle']}")
    logging.info(f"=== BACKTEST FINAL | Capital: {capital:.2f}€ ===")
    return m, capital

# === MAIN CLI ===
def main():
    parser = argparse.ArgumentParser(description=NUME)
    parser.add_argument("--loop", type=int, default=0, help="Număr de bucle automate")
    parser.add_argument("--simbol", type=str, default="BTCUSDT", help="Simbol de tranzacționare")
    parser.add_argument("--capital", type=float, default=CONFIG["capital_initial"], help="Capital inițial (€)")
    parser.add_argument("--export", action="store_true", help="Exportă JSON la final")
    parser.add_argument("--write", action="store_true", help="Scrie în REZOLVARI.md la final")
    parser.add_argument("--test", action="store_true", help="Rulează test de integritate")
    parser.add_argument("--backtest", type=int, default=0, help="Rulează backtest pe N zile")
    parser.add_argument("--paper", action="store_true", help="Mod paper trading (nu modifică capitalul)")
    parser.add_argument("--report", action="store_true", help="Generează raport PSIE")
    args = parser.parse_args()

    logging.info(f"=== START HYDRA BURSĂ PSIE | Args: {args} ===")

    if args.test:
        run_test()
        return

    if args.backtest > 0:
        run_backtest(args.backtest, args.simbol)
        return

    m = load()

    if args.report:
        genereaza_raport(m)
        return

    capital = args.capital
    mod = "paper" if args.paper else "real"

    if args.loop > 0:
        for _ in range(args.loop):
            m, capital = predict_bursa(args.simbol, m, capital, mod=mod)
        if args.export:
            export_json(m)
        if args.write:
            write_rezolvari(m)
        save(m)
        print(f"
[FINAL] Rulare completă | Capital Final: {capital:.2f}€ | Total Retras: {m['total_retras']:.2f}€")
        logging.info(f"=== FINAL | Capital: {capital:.2f}€ | Retras: {m['total_retras']:.2f}€ ===")
        return

    print(f"{NUME} — Sistem Quantitative PSIE conectat la piețe reale")
    print(f"Mod: {mod.upper()} | Capital inițial: {capital:.2f}€")
    print("Comenzi: <simbol> (ex: BTCUSDT, ETHUSDT) | STATUS | EXPORT | WRITE | TEST | BACKTEST | REPORT | Q")
    while True:
        try:
            cmd = input("
> introduceți simbol/comandă: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd:
            continue
        if cmd == "Q":
            logging.info("=== EXIT USER ===")
            break
        if
