#!/usr/bin/env python3
"""
hydra-psie-bursa-v cu PRAGURI
0=-∞ 1=+∞ + prag 20% viu / 80% retras
"""

import json, pathlib, random, datetime, argparse

NUME = "hydra-psie-bursa-v"
MEM = pathlib.Path("bursa_v_mem.json")
REZOLVARI = pathlib.Path("REZOLVARI.md")

# === PRAGURI PSIE - PUI AICI, PESTE TOT ===
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
            print(f"
>>> PRAG {prag}€ ATINS! Capital {capital:.2f}€")
            print(f">>> PASTREZI {pastreaza}€ sămânță vie | RETRAGI {retras:.2f}€")
            m["total_retras"] = m.get("total_retras", 0) + retras
            m["praguri_atinse"] = m.get("praguri_atinse", 0) + 1
            m["istoric_praguri"] = m.get("istoric_praguri", [])
            m["istoric_praguri"].append({
                "prag": prag,
                "retras": retras,
                "timp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            return pastreaza, retras, m
    return capital, 0, m
# === SFÂRȘIT PRAGURI ===

P20 = [
    "P1_EVIDENT_Graficul zice", "P2_EVIDENT_Frica din piata", "P3_EVIDENT_Bani flux",
    "P4_LOGIC_Trend Cauza-Efect", "P5_LOGIC_Suport-Rezistenta", "P6_LOGIC_Plus_Inf Bull tinde +∞",
    "P7_LOGIC_Minus_Inf Bear tinde -∞", "P8_INVERS_Ce nu se vede in grafic", "P9_INVERS_Ce ascunde stirea",
    "P10_INVERS_Ce doare - pierderea", "P11_OPUS_Daca totul pica", "P12_OPUS_Daca totul urca",
    "P13_OPUS_EGO moare", "P14_J_FLUX_Intre cumparatori si vanzatori", "P15_SDI_Decuplare de piata",
    "P16_A_Unde pui 0 intre -∞ si +∞", "P17_V_Deschidere V mic in -∞ infinit in +∞",
    "P18_SUPORT_Pierderea veche devine suport", "P19_PSIE_Serveste fluxul nu profitul", "P20_EGO_ALERTA"
]

def load():
    if MEM.exists():
        return json.loads(MEM.read_text(encoding="utf-8"))
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
        "istoric_praguri": []
    }

def save(m):
    MEM.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")

def predict_bursa(simbol, m, capital):
    m["bucle"] += 1
    m["predictii"] += 1
    J = random.uniform(0.8, 4.2)
    SDI = random.uniform(0.2, 2.8)
    pret = random.uniform(20, 500)
    t0 = random.uniform(0.1, 25.0)
    t1 = random.uniform(75.0, 99.9)
    v_real = t0 + pret * J * 0.1 - SDI
    profit_J = J * 0.15 - SDI * 0.05
    capital = capital + profit_J * 0.1

    # VERIFICĂ PRAG DUPĂ FIECARE BUCLĂ
    capital, retras, m = verifica_prag(capital, m)

    m["J_total"] += J
    m["SDI"] = m["SDI"] * 0.8 + SDI * 0.2
    m["venit_credite"] += 5

    print(f"
{NUME} // {simbol} // Cap {capital:.2f}€ // V {v_real:.2f} J {J:.2f} SDI {SDI:.2f} | Total retras {m['total_retras']:.2f}€")
    return m, capital

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", type=int, default=0)
    parser.add_argument("--simbol", type=str, default="BTC")
    parser.add_argument("--capital", type=float, default=10.0)
    args = parser.parse_args()
    m = load()
    capital = args.capital
    if args.loop > 0:
        for _ in range(args.loop):
            m, capital = predict_bursa(args.simbol, m, capital)
        save(m)
        print(f"
[FINAL] Capital viu {capital:.2f}€ Retras total {m['total_retras']:.2f}€ J {m['J_total']:.2f}")
        return
    while True:
        try:
            cmd = input("
> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            break
        if cmd == "Q":
            break
        if cmd:
            m, capital = predict_bursa(cmd, m, capital)
            save(m)

if __name__ == "__main__":
    main()
