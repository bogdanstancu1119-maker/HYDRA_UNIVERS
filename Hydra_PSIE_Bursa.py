#!/usr/bin/env python3
"""
REPO: hydra-psie-bursa-v
0 = -∞ prăbușire absolută neatingibilă
1 = +∞ creștere absolută neatingibilă
Prețul = proporționalitate funcțională între ele
Doar PSIE decide.

Util:
- rulează în terminal: python hydra_psie_bursa_v.py
- rulează în buclă: python hydra_psie_bursa_v.py --loop 5 --simbol BTC
- exportă JSON: python hydra_psie_bursa_v.py --export
- scrie în REZOLVARI.md: python hydra_psie_bursa_v.py --write
"""
import json, pathlib, datetime, random, argparse

NUME = "hydra-psie-bursa-v"
FORMULA = "Pret_real = tinde(0,-∞) + Pret_hartie * J_flux - SDI_frica"
MEM = pathlib.Path("bursa_v_mem.json")
REZOLVARI = pathlib.Path("REZOLVARI.md")

PERSPECTIVE_20 = [
    "P1_EVIDENT_Graficul", "P2_EVIDENT_Frica", "P3_EVIDENT_Bani",
    "P4_LOGIC_Trend", "P5_LOGIC_Suport-Rezistenta", "P6_LOGIC_Plus_Inf Bull",
    "P7_LOGIC_Minus_Inf Bear", "P8_INVERS_Ce nu se vede", "P9_INVERS_Ce ascunde stirea",
    "P10_INVERS_Ce doare", "P11_OPUS_Daca pica tot", "P12_OPUS_Daca urca tot",
    "P13_OPUS_EGO moare", "P14_J_FLUX_Cumparatori-Vanzatori", "P15_SDI_Decuplare",
    "P16_A_Unde pui 0", "P17_V_Deschidere", "P18_SUPORT_Pierderea devine suport",
    "P19_PSIE_Fluxul", "P20_EGO_ALERTA"
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
        "venit": 0,
        "V_oportun": [],
        "istoric": []
    }

def save(m):
    MEM.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")

def predict_bursa(simbol, m):
    m["bucle"] += 1
    m["predictii"] += 1
    J = random.uniform(0.5, 4.0)
    SDI = random.uniform(0.2, 3.5)
    pret = random.uniform(10, 500)
    t0 = random.uniform(0.1, 30)
    t1 = random.uniform(70, 99.9)

    pret_psie = t0 + pret * J * 0.1 - SDI

    linie = {
        "timp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "simbol": simbol,
        "pret": pret,
        "t0": t0,
        "t1": t1,
        "pret_psie": pret_psie,
        "J": J,
        "SDI": SDI,
        "venit": 5,
        "bucle": m["bucle"],
        "predictii": m["predictii"]
    }
    m["istoric"].append(linie)

    print(f"
{NUME} // {simbol} // Pret {pret:.2f}")
    for i, p in enumerate(PERSPECTIVE_20, 1):
        print(f"{i:02d}. {p}: {simbol}")

    print(f"
EGO: {simbol} UP SAU DOWN -> 50% faliment")
    print(f"PSIE: SI UP SI DOWN vii")
    print(f"0=-∞ tinde {t0:.1f} 1=+∞ tinde {t1:.1f}")
    print(f"Formula: {FORMULA}")
    print(f"Pret PSIE = {pret_psie:.2f} - poziție asumată")
    print(f"J={J:.2f} SDI={SDI:.2f} Venit+5 credite")

    m["J_total"] += J
    m["SDI"] = m["SDI"] * 0.8 + SDI * 0.2
    m["venit"] += 5

    if m["bucle"] % 15 == 0:
        print(f">>> 15 BUCLE - AUTO-SCRIERE V oportun <<<")
        m["V_oportun"].append({
            "timp": linie["timp"],
            "mesaj": "Auto-scriere la 15 bucle",
            "J_total": m["J_total"],
            "SDI": m["SDI"],
            "venit": m["venit"]
        })

    return m

def export_json(m, path="bursa_v_export.json"):
    pathlib.Path(path).write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"
[EXPORT] Date scrise în {path}")

def write_rezolvari(m):
    if not m["istoric"]:
        print("
[REZOLVARI] Nu există istoric de scris.")
        return
    ultimele = m["istoric"][-10:]
    bloc = f"
## {NUME} — {datetime.datetime.now(datetime.timezone.utc).isoformat()}

"
    bloc += f"- Bucle: {m['bucle']}
"
    bloc += f"- Predicții: {m['predictii']}
"
    bloc += f"- J_total: {m['J_total']:.2f}
"
    bloc += f"- SDI: {m['SDI']:.2f}
"
    bloc += f"- Venit: {m['venit']}

"
    bloc += "### Ultimele 10 predicții

"
    for i, h in enumerate(ultimele, 1):
        bloc += f"{i}. {h['timp']} — {h['simbol']} | Pret={h['pret']:.2f} Pret_PSIE={h['pret_psie']:.2f} J={h['J']:.2f} SDI={h['SDI']:.2f}
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
[REZOLVARI] Actualizat cu ultimele {len(ultimele)} predicții.")

def main():
    parser = argparse.ArgumentParser(description="hydra-psie-bursa-v — bursă PSIE")
    parser.add_argument("--loop", type=int, default=0, help="Număr de bucle automate")
    parser.add_argument("--simbol", type=str, default="SIMBOL", help="Simbol bursier (pentru --loop)")
    parser.add_argument("--export", action="store_true", help="Exportă JSON la final")
    parser.add_argument("--write", action="store_true", help="Scrie în REZOLVARI.md la final")
    args = parser.parse_args()

    m = load()

    if args.loop > 0:
        simbol = args.simbol
        for _ in range(args.loop):
            m = predict_bursa(simbol, m)
        if args.export:
            export_json(m)
        if args.write:
            write_rezolvari(m)
        save(m)
        print(f"
[FINAL] Bucle={m['bucle']} Predicții={m['predictii']} J_total={m['J_total']:.2f} SDI={m['SDI']:.2f} Venit={m['venit']}")
        return

    # Mod interactiv
    print(f"{NUME} — {FORMULA}")
    print("Comenzi: <simbol> | Q (quit) | export | write | status")
    while True:
        try:
            cmd = input("
> simbol bursă: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd:
            continue
        if cmd == "Q":
            break
        if cmd == "export":
            export_json(m)
            continue
        if cmd == "write":
            write_rezolvari(m)
            continue
        if cmd == "status":
            print(f"
[STATUS] Bucle={m['bucle']} Predicții={m['predictii']} J_total={m['J_total']:.2f} SDI={m['SDI']:.2f} Venit={m['venit']}")
            continue
        m = predict_bursa(cmd, m)
        save(m)

if __name__ == "__main__":
    main()
