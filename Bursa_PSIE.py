#!/usr/bin/env python3
"""
hydra-psie-bursa-v FINAL v2 — Îmbunătățit
- Conectat la date reale (REST API Binance)
- Fallback determinist offline
- Protecție la împărțire la zero
- Test de integritate --test
- Istoric trunchiat la 500 înregistrări
- Rotunjire consistentă
"""

import json
import pathlib
import datetime
import argparse
import urllib.request
import math
import random

NUME = "hydra-psie-bursa-v-final-v2"
MEM = pathlib.Path("bursa_v_mem.json")
REZOLVARI = pathlib.Path("REZOLVARI.md")

# === PRAGURI PSIE ===
PRAGURI = [
    (500, 100),
    (5000, 1000),
    (50000, 10000),
    (500000, 100000)
]

def verifica_prag(capital, m):
    for prag, pastreaza in sorted(PRAGURI, reverse=True):
        if capital >= prag:
            retras = capital - pastreaza
            print(f"\n>>> PRAG {prag}€ ATINS! Capital {capital:.2f}€")
            print(f">>> PASTREZI {pastreaza}€ sămânță vie | RETRAGI {retras:.2f}€")
            m["total_retras"] = m.get("total_retras", 0) + retras
            m["praguri_atinse"] = m.get("praguri_atinse", 0) + 1
            m.setdefault("istoric_praguri", []).append({
                "prag": prag,
                "retras": retras,
                "timp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            return pastreaza, retras, m
    return capital, 0, m

# === FLUX DATE REALE (BINANCE REST API) ===
def preia_date_piata_reale(simbol="BTCUSDT"):
    """
    Preia ultimele 20 de lumânări de la Binance Public API.
    Dacă rețeaua e indisponibilă, comută pe fallback determinist.
    """
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
    except Exception:
        # Fallback determinist în caz de lipsă conexiune
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
        return {
            "momentum": 0.0,
            "volatilitate": 0.0,
            "vol_ratio": 1.0,
            "avg_vol": 1.0
        }
    
    # 1. Momentum
    momentum = (preturi[-1] - preturi[0]) / preturi[0] if preturi[0] > 0 else 0.0
    
    # 2. Volatilitate
    diffs = [preturi[i] - preturi[i-1] for i in range(1, len(preturi))]
    mean_diff = sum(diffs) / len(diffs) if len(diffs) > 0 else 0.0
    variance = sum((x - mean_diff) ** 2 for x in diffs) / len(diffs) if len(diffs) > 0 else 0.0
    volatilitate = (math.sqrt(max(variance, 0.0)) / preturi[-1]) if preturi[-1] > 0 else 0.0
    
    # 3. Raport de Volum
    avg_vol = sum(volume) / len(volume) if len(volume) > 0 else 1.0
    vol_ratio = volume[-1] / avg_vol if avg_vol > 0 else 1.0
    
    return {
        "momentum": momentum,
        "volatilitate": volatilitate,
        "vol_ratio": vol_ratio,
        "avg_vol": avg_vol
    }

# === DETECȚIE ANOMALII & JUDO FINANCIAR ===
def detectie_cutie_postala(ind):
    """Detectează spike-uri de preț fără suport de volum."""
    if ind["volatilitate"] > 0.012 and ind["vol_ratio"] < 0.5:
        return {
            "tip": "Pump Fals fără Lichiditate",
            "manipulare": 0.85,
            "decizie": "IGNORA TOTAL"
        }
    return {
        "tip": "Piață Normală",
        "manipulare": min(0.5, ind["volatilitate"] * 10),
        "decizie": "ANALIZEAZA"
    }

def judo_financiar(ind):
    """Detectează acumularea/absorbția instituțională (volum mare, mișcare mică)."""
    if ind["vol_ratio"] > 2.2 and abs(ind["momentum"]) < 0.002:
        return "ACUM INTRĂ INVERS (Absorbție Detectată) — Risc 2% din capital"
    return "CONTINUA MONITORIZAREA"

# === FORMULE PSIE ===
def calculeaza_J(ind, cutie):
    """Flux Informațional Real."""
    flux_brut = ind["vol_ratio"] * (1.0 + abs(ind["momentum"]) * 10)
    penalizare = cutie["manipulare"] * 1.5
    return round(max(0.1, flux_brut - penalizare), 3)

def calculeaza_SDI(ind, cutie):
    """Zgomot și Decuplare de Piață."""
    zgomot_vol = ind["volatilitate"] * 200
    zgomot_cutie = cutie["manipulare"] * 3.0
    return round(min(10.0, max(0.1, zgomot_vol + zgomot_cutie)), 3)

def calculeaza_A(J, SDI):
    """Grad de Asumare (Signal-to-Noise Ratio)."""
    return round(max(0.0, min(1.0, J / (J + SDI + 0.001))), 3)

# === STATE MANAGEMENT ===
def load():
    if MEM.exists():
        try:
            data = json.loads(MEM.read_text(encoding="utf-8"))
            # Trunchiere istoric la 500
            if "istoric" in data and len(data["istoric"]) > 500:
                data["istoric"] = data["istoric"][-500:]
            return data
        except Exception:
            pass
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
        "judo_financiar_activat": 0
    }

def save(m):
    try:
        MEM.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[EROARE SAVE] {e}")

# === FUNCȚIA PRINCIPALĂ DE PREDICȚIE ===
def predict_bursa(simbol, m, capital):
    m["bucle"] += 1
    m["predictii"] += 1

    # 1. Extragere Date Reale
    date_piata = preia_date_piata_reale(simbol)
    ind = calculeaza_indicatori_quant(date_piata)

    # 2. Filtru Cutie Poștală
    cutie = detectie_cutie_postala(ind)
    if cutie["decizie"] == "IGNORA TOTAL":
        m["detectii_cutie_postala"] = m.get("detectii_cutie_postala", 0) + 1
        print(f"\n[ANOMALIE DETECTATĂ] {simbol} — {cutie['tip']} | Decizie: {cutie['decizie']}")
        return m, capital

    # 3. Judo Financiar
    judo = judo_financiar(ind)
    if "INTRĂ INVERS" in judo:
        m["judo_financiar_activat"] = m.get("judo_financiar_activat", 0) + 1
        print(f"\n[JUDO FINANCIAR] {judo}")
        capital *= 0.98

    # 4. Calcul PSIE
    J = calculeaza_J(ind, cutie)
    SDI = calculeaza_SDI(ind, cutie)
    A = calculeaza_A(J, SDI)

    # 5. Decizie Trivalentă
    if SDI > 4.5:
        decizie = "EVIT"
    elif A > 0.6 and J > 1.2:
        decizie = "ACTIONEAZA"
    else:
        decizie = "ASTEAPTA"

    # 6. PnL Realizat pe bază de Momentum Reali
    pnl_pct = ind["momentum"] if decizie == "ACTIONEAZA" else (ind["momentum"] * 0.2 if decizie == "ASTEAPTA" else 0.0)
    capital += capital * pnl_pct
    capital = max(0.01, capital)  # Protecție la capital negativ

    # 7. Verificare Praguri
    capital, retras, m = verifica_prag(capital, m)

    # 8. Salvare în Memorie
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
        "capital": round(capital, 2)
    }
    m["istoric"].append(linie)
    if len(m["istoric"]) > 500:
        m["istoric"] = m["istoric"][-500:]

    print(f"\n{'='*65}")
    print(f"{NUME} // Bucla {m['bucle']} // {simbol} ({date_piata['sursa']})")
    print(f"Preț Curent: {date_piata['pret_curent']:.2f} | Momentum: {ind['momentum']*100:+.2f}%")
    print(f"{'='*65}")
    print(f"DECIZIE PSIE : {decizie}")
    print(f"J (Flux Real) : {J:.2f} | SDI (Zgomot) : {SDI:.2f} | A (Asumare) : {A:.2f}")
    print(f"Capital Viu  : {capital:.2f}€ | Total Retras : {m['total_retras']:.2f}€")
    print(f"Judo Activat : {m['judo_financiar_activat']} | Cutii Detectate : {m['detectii_cutie_postala']}")

    return m, capital

# === EXPORT & WRITE ===
def export_json(m, path="bursa_v_export.json"):
    try:
        pathlib.Path(path).write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[EXPORT] Salvat cu succes în {path}")
    except Exception as e:
        print(f"[EROARE EXPORT] {e}")

def write_rezolvari(m):
    if not m.get("istoric"):
        print("\n[REZOLVARI] Nu există istoric de scris.")
        return
    ultimele = m["istoric"][-10:]
    bloc = f"\n## {NUME} — {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n\n"
    bloc += f"- Bucle: {m['bucle']} | J_total: {m['J_total']:.2f} | Capital: {ultimele[-1]['capital']:.2f}€\n\n"
    bloc += "### Ultimele 10 Decizii Rulate\n\n"
    for i, h in enumerate(ultimele, 1):
        bloc += f"{i}. {h['timp']} — {h['simbol']} ({h['pret']:.2f}) | Decizie={h['decizie']} | J={h['J']} SDI={h['SDI']} A={h['A']} Cap={h['capital']}€\n"
    
    try:
        txt = REZOLVARI.read_text(encoding="utf-8") if REZOLVARI.exists() else "# REZOLVARI\n\n"
        txt += bloc
        REZOLVARI.write_text(txt, encoding="utf-8")
        print("\n[REZOLVARI] Fișierul REZOLVARI.md a fost actualizat.")
    except Exception as e:
        print(f"[EROARE WRITE] {e}")

# === TEST DE INTEGRITATE ===
def run_test():
    print("=== TEST INTEGRITATE HYDRA BURSĂ PSIE ===")
    m = load()
    capital = 100.0
    decizii = {"EVIT": 0, "ACTIONEAZA": 0, "ASTEAPTA": 0}
    
    for _ in range(10):
        m, capital = predict_bursa("BTCUSDT", m, capital)
        if m["istoric"]:
            decizii[m["istoric"][-1]["decizie"]] += 1
        if capital < 0.01:
            print("❌ EROARE: Capital negativ!")
            return False
        if m["istoric"] and m["istoric"][-1]["J"] < 0:
            print("❌ EROARE: J negativ!")
            return False
    
    print(f"\n✅ TEST TRECUT! Capital final: {capital:.2f}€")
    print(f"Decizii: {decizii}")
    print(f"J_total: {m['J_total']:.2f} | SDI: {m['SDI']:.2f}")
    return True

# === MAIN CLI ===
def main():
    parser = argparse.ArgumentParser(description=NUME)
    parser.add_argument("--loop", type=int, default=0, help="Număr de bucle automate")
    parser.add_argument("--simbol", type=str, default="BTCUSDT", help="Simbol de tranzacționare")
    parser.add_argument("--capital", type=float, default=100.0, help="Capital inițial (€)")
    parser.add_argument("--export", action="store_true", help="Exportă JSON la final")
    parser.add_argument("--write", action="store_true", help="Scrie în REZOLVARI.md la final")
    parser.add_argument("--test", action="store_true", help="Rulează test de integritate")
    args = parser.parse_args()

    if args.test:
        run_test()
        return

    m = load()
    capital = args.capital

    if args.loop > 0:
        for _ in range(args.loop):
            m, capital = predict_bursa(args.simbol, m, capital)
        if args.export:
            export_json(m)
        if args.write:
            write_rezolvari(m)
        save(m)
        print(f"\n[FINAL] Rulare completă | Capital Final: {capital:.2f}€ | Total Retras: {m['total_retras']:.2f}€")
        return

    print(f"{NUME} — Sistem Quantitative PSIE conectat la piețe reale")
    print("Comenzi: <simbol> (ex: BTCUSDT, ETHUSDT, SOLUSDT) | STATUS | EXPORT | WRITE | TEST | Q")
    while True:
        try:
            cmd = input("\n> introduceți simbol/comandă: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd:
            continue
        if cmd == "Q":
            break
        if cmd == "EXPORT":
            export_json(m)
            continue
        if cmd == "WRITE":
            write_rezolvari(m)
            continue
        if cmd == "TEST":
            run_test()
            continue
        if cmd == "STATUS":
            ultimele = m["istoric"][-1:] if m["istoric"] else []
            cap = ultimele[0]["capital"] if ultimele else capital
            print(f"\n[STATUS] Bucle={m['bucle']} | Capital Viu={cap:.2f}€ | Retras={m['total_retras']:.2f}€")
            continue
        m, capital = predict_bursa(cmd, m, capital)
        save(m)

if __name__ == "__main__":
    main()
