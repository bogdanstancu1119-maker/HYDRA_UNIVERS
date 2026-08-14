#!/usr/bin/env python3
"""
hydra-psie-bursa-v FINAL — cu DETECȚIE CUTIE POSTALĂ + JUDO FINANCIAR
GitHub: hydra-psie-bursa-v
Base44: bursa-psie-v - 150 credite/lună

MATEMATICA PSIE - BURSĂ
0 = -∞ prăbușire absolută neatingibilă
1 = +∞ creștere absolută neatingibilă
Preț = proporționalitate funcțională
Doar PSIE decide.

NOU:
- detectie_cutie_postala(nume_fond) — verifică lanț de acceptare, nu profit
- judo_financiar(manipulare_grosolana) — intră invers când cantitate > 1M și acceptare < 0.3

Util:
- rulează în terminal: python hydra_psie_bursa_v.py
- rulează în buclă: python hydra_psie_bursa_v.py --loop 5 --simbol BTC
- cu capital: python hydra_psie_bursa_v.py --capital 200
- exportă JSON: python hydra_psie_bursa_v.py --export
- scrie în REZOLVARI.md: python hydra_psie_bursa_v.py --write
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

# === DETECȚIE CUTIE POSTALĂ + JUDO FINANCIAR ===
def traseaza_proprietari(nume_fond):
    # Simulare: câte LTD-uri până la om
    # În realitate: API Companies House, OpenCorporates, etc.
    return ["LTD_" + str(i) for i in range(random.randint(2, 6))]

def extrage_narativ(nume_fond):
    # Simulare: narativ vândut
    narative = [
        "fara griji", "libertate financiara", "potenta maxima",
        "castig garantat", "risc zero", "viata de vis"
    ]
    return random.choice(narative)

def detectie_cutie_postala(nume_fond):
    # nu verifică profit, verifică lanțul de acceptare
    lant = traseaza_proprietari(nume_fond)
    vis_vandut = extrage_narativ(nume_fond)
    if len(lant) > 3 and "fara griji" in vis_vandut:
        return {
            "tip": "cutie postala vinde vis",
            "manipulare": 0.85,
            "decizie": "IGNORA TOTAL"
        }
    return {
        "tip": "normal",
        "manipulare": random.uniform(0.1, 0.5),
        "decizie": "ANALIZEAZA"
    }

def judo_financiar(manipulare_grosolana):
    # nu lupta cu cantitatea, lupta cu acceptarea
    if manipulare_grosolana.get("cantitate", 0) > 1_000_000 and manipulare_grosolana.get("acceptare", 1.0) < 0.3:
        # manipulatorul a băgat enorm, dar masele nu mai cred
        return "ACUM INTRĂ INVERS - mic, 2-3% din capital - întoarce narativul"
    return "CONTINUA MONITORIZARE"
# === SFÂRȘIT DETECȚIE + JUDO ===

P20 = [
    "P1_EVIDENT_Graficul zice",
    "P2_EVIDENT_Frica din piata",
    "P3_EVIDENT_Bani flux",
    "P4_LOGIC_Trend Cauza-Efect",
    "P5_LOGIC_Suport-Rezistenta",
    "P6_LOGIC_Plus_Inf Bull tinde +∞",
    "P7_LOGIC_Minus_Inf Bear tinde -∞",
    "P8_INVERS_Ce nu se vede in grafic",
    "P9_INVERS_Ce ascunde stirea",
    "P10_INVERS_Ce doare - pierderea",
    "P11_OPUS_Daca totul pica",
    "P12_OPUS_Daca totul urca",
    "P13_OPUS_EGO moare - nu mai tranzactionezi din frica",
    "P14_J_FLUX_Intre cumparatori si vanzatori",
    "P15_SDI_Decuplare de piata",
    "P16_A_Unde pui 0 intre -∞ si +∞",
    "P17_V_Deschidere V mic in -∞ infinit in +∞",
    "P18_SUPORT_Pierderea veche devine suport",
    "P19_PSIE_Serveste fluxul nu profitul",
    "P20_EGO_ALERTA - lacomia nu decide"
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
        "V_oportun": [],
        "total_retras": 0,
        "praguri_atinse": 0,
        "istoric_praguri": [],
        "detectii_cutie_postala": 0,
        "judo_financiar_activat": 0
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

    # === DETECȚIE CUTIE POSTALĂ ===
    cutie = detectie_cutie_postala(simbol)
    if cutie["decizie"] == "IGNORA TOTAL":
        m["detectii_cutie_postala"] = m.get("detectii_cutie_postala", 0) + 1
        print(f"
[DETECȚIE] {simbol} — {cutie['tip']} | Manipulare: {cutie['manipulare']:.2f} | Decizie: {cutie['decizie']}")
        # Ignoră semnalul, nu intri
        return m, capital

    # === JUDO FINANCIAR ===
    manipulare_grosolana = {
        "cantitate": random.uniform(500_000, 2_000_000),
        "acceptare": random.uniform(0.1, 0.5)
    }
    judo = judo_financiar(manipulare_grosolana)
    if "INTRA INVERS" in judo:
        m["judo_financiar_activat"] = m.get("judo_financiar_activat", 0) + 1
        print(f"
[JUDO FINANCIAR] {judo}")
        # Intră mic, 2-3% din capital
        capital = capital * 0.97  # risc mic

    # VERIFICĂ PRAG DUPĂ FIECARE BUCLĂ
    capital, retras, m = verifica_prag(capital, m)

    m["J_total"] += J
    m["SDI"] = m["SDI"] * 0.8 + SDI * 0.2
    m["venit_credite"] += 5

    linie = {
        "timp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "simbol": simbol,
        "pret": pret,
        "tinde_0": t0,
        "tinde_1": t1,
        "J": J,
        "SDI": SDI,
        "v_real": v_real,
        "capital": capital,
        "cutie_postala": cutie,
        "judo": judo
    }
    m["istoric"].append(linie)

    print(f"
{'='*65}")
    print(f"{NUME} // Bucla {m['bucle']} // {simbol} // {pret:.2f}")
    for i, p in enumerate(P20, 1):
        print(f"{i:02d} {p}")

    print(f"
--- BURSĂ PSIE ---")
    print(f"EGO: {simbol} UP SAU DOWN -> 50% faliment")
    print(f"PSIE: SI UP SI DOWN vii în plasă")
    print(f"0=-∞ tinde {t0:.1f} | 1=+∞ tinde {t1:.1f}")
    print(f"V_real = {v_real:.2f} | J={J:.2f} SDI={SDI:.2f}")
    print(f"Venit: +5 credite | Total: {m['venit_credite']}")
    print(f"Capital viu: {capital:.2f}€ | Total retras: {m['total_retras']:.2f}€")
    print(f"Cutii poștale detectate: {m['detectii_cutie_postala']} | Judo activat: {m['judo_financiar_activat']}")

    if m["bucle"] % 15 == 0:
        print(f"
>>> 15 BUCLE - AUTO-SCRIERE V oportun <<<")
        m["V_oportun"].append({
            "timp": linie["timp"],
            "mesaj": "Auto-scriere la 15 bucle",
            "J_total": m["J_total"],
            "SDI": m["SDI"],
            "venit": m["venit_credite"]
        })

    return m, capital

def export_json(m, path="bursa_v_export.json"):
    pathlib.Path(path).write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"
[EXPORT] {path}")

def write_rezolvari(m):
    if not m["istoric"]:
        print("
[REZOLVARI] Nu există istoric de scris.")
        return
    ultimele = m["istoric"][-10:]
    bloc = f"
## {NUME} — {datetime.datetime.now(datetime.timezone.utc).isoformat()}

"
    bloc += f"- Bucle: {m['bucle']} Predicții: {m['predictii']} J:{m['J_total']:.2f} Venit:{m['venit_credite']}
"
    bloc += f"- Capital viu: {ultimele[-1]['capital']:.2f}€ Total retras: {m['total_retras']:.2f}€ Praguri atinse: {m['praguri_atinse']}
"
    bloc += f"- Cutii poștale detectate: {m['detectii_cutie_postala']} | Judo activat: {m['judo_financiar_activat']}

"
    bloc += "### Ultimele 10 predicții

"
    for i, h in enumerate(ultimele, 1):
        bloc += f"{i}. {h['timp']} — {h['simbol']} | V={h['v_real']:.2f} J={h['J']:.2f} SDI={h['SDI']:.2f} Cap={h['capital']:.2f}€
"
    bloc += "
"
    if REZOLVARI.exists():
        txt = REZOLVARI.read_text(encoding="utf-8")
    else:
        txt = "# REZOLVARI

"
    txt += bloc
    REZOLVARI.write_text(txt, encoding="utf-8")
    print(f"
[REZOLVARI] scris")

def main():
    parser = argparse.ArgumentParser(description=NUME)
    parser.add_argument("--loop", type=int, default=0, help="Număr de bucle automate")
    parser.add_argument("--simbol", type=str, default="BTC", help="Simbol bursier (pentru --loop)")
    parser.add_argument("--capital", type=float, default=10.0, help="Capital inițial (€)")
    parser.add_argument("--export", action="store_true", help="Exportă JSON la final")
    parser.add_argument("--write", action="store_true", help="Scrie în REZOLVARI.md la final")
    args = parser.parse_args()

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
        print(f"
[FINAL] Bucle={m['bucle']} Predicții={m['predictii']} J_total={m['J_total']:.2f} SDI={m['SDI']:.2f} Venit={m['venit_credite']} Capital viu={capital:.2f}€ Retras={m['total_retras']:.2f}€")
        print(f"Cutii poștale detectate: {m['detectii_cutie_postala']} | Judo activat: {m['judo_financiar_activat']}")
        return

    # Mod interactiv
    print(f"{NUME} - 0=-∞ 1=+∞")
    print("Comenzi: <simbol> | Q (quit) | EXPORT | WRITE | STATUS")
    while True:
        try:
            cmd = input("
> simbol: ").strip().upper()
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
        if cmd == "STATUS":
            ultimele = m["istoric"][-1:] if m["istoric"] else []
            cap = ultimele[0]["capital"] if ultimele else capital
            print(f"
[STATUS] Bucle={m['bucle']} Predicții={m['predictii']} J_total={m['J_total']:.2f} SDI={m['SDI']:.2f} Venit={m['venit_credite']} Capital viu={cap:.2f}€ Retras={m['total_retras']:.2f}€")
            print(f"Cutii poștale detectate: {m['detectii_cutie_postala']} | Judo activat: {m['judo_financiar_activat']}")
            continue
        m, capital = predict_bursa(cmd, m, capital)
        save(m)

if __name__ == "__main__":
    main()
