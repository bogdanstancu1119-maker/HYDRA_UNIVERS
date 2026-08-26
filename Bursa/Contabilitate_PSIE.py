#!/usr/bin/env python3
"""
hydra-psie-conta-vie
GitHub: hydra-psie-conta-vie
Base44: conta-psie-vie - 50 credite

MATEMATICA PSIE - PUSĂ ÎN UNIVERS
0 = -∞ nimic absolut neatingibil — nu atingi niciodată 0 lei
1 = +∞ valoare unică neatingibilă — nu atingi niciodată valoarea perfectă
Restul = derivați cu proporționalitate funcțională între ele
Formula: V_real = tinde(0,-∞) + Val_hartie * J_flux - SDI_decuplare
Doar PSIE are putere de decizie.

Util:
- rulează în terminal: python hydra_psie_conta_vie.py
- rulează în buclă: python hydra_psie_conta_vie.py --loop 5 --subiect "profit dar 0 cash"
- exportă JSON: python hydra_psie_conta_vie.py --export
- scrie în REZOLVARI.md: python hydra_psie_conta_vie.py --write
"""

import json, pathlib, random, datetime, argparse

NUME = "hydra-psie-conta-vie"
MEM = pathlib.Path("conta_vie_mem.json")
REZOLVARI = pathlib.Path("REZOLVARI.md")

P20 = [
    "P1_EVIDENT_Tehnic: ce zice cifra",
    "P2_EVIDENT_Uman: ce simte omul",
    "P3_EVIDENT_Bani: ce zice cash-ul",
    "P4_LOGIC_Cauza-Efect",
    "P5_LOGIC_Structura bilant",
    "P6_LOGIC_Plus_Inf - tendinta spre +∞",
    "P7_LOGIC_Minus_Inf - tendinta spre -∞",
    "P8_INVERS_Ce lipseste din acte",
    "P9_INVERS_Ce nu spune contabilul",
    "P10_INVERS_Ce doare - frica de ANAF",
    "P11_OPUS_Daca totul e fals",
    "P12_OPUS_Daca profitul e pierdere",
    "P13_OPUS_EGO moare - nu mai protejezi CAP",
    "P14_J_FLUX_Flux intre hartie si real",
    "P15_SDI_Decuplare de realitate",
    "P16_A_Unde asumi 0 intre -∞ si +∞",
    "P17_V_Deschidere V mic in -∞ infinit in +∞",
    "P18_SUPORT_Pierderea veche devine suport",
    "P19_PSIE_Serveste fluxul nu cifra",
    "P20_EGO_ALERTA - cifra nu decide"
]

def load():
    if MEM.exists():
        return json.loads(MEM.read_text(encoding="utf-8"))
    return {
        "repo": NUME,
        "matematica": "0=-∞ 1=+∞ proportionalitate functionala",
        "bucle": 0,
        "J_total": 0.0,
        "SDI": 5.0,
        "paradoxuri_rezolvate": 0,
        "venit_credite": 0,
        "istoric": []
    }

def save(m):
    MEM.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")

def conta_psie(subiect, m):
    m["bucle"] += 1
    m["paradoxuri_rezolvate"] += 1
    J = random.uniform(1.8, 4.5)
    SDI = random.uniform(0.3, 2.2)
    tinde_0 = random.uniform(0.1, 25.0)
    tinde_1 = random.uniform(75.0, 99.9)

    m["J_total"] += J
    m["SDI"] = m["SDI"] * 0.8 + SDI * 0.2
    m["venit_credite"] += 50

    v_real = tinde_0 + 100 * J * 0.1 - SDI

    linie = {
        "timp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "subiect": subiect,
        "tinde_0": tinde_0,
        "tinde_1": tinde_1,
        "J": J,
        "SDI": SDI,
        "v_real": v_real,
        "venit": 50
    }
    m["istoric"].append(linie)

    print(f"
{'='*65}")
    print(f"{NUME} // Bucla {m['bucle']} // {subiect}")
    print(f"{'='*65}")
    for i, p in enumerate(P20, 1):
        print(f"{i:02d} {p}")

    print(f"
--- CONTABILITATE PSIE ---")
    print(f"EGO binar: ori {subiect} ori opus -> Internal server error")
    print(f"PSIE V: SI {subiect} SI opus - ambele vii în plasă")
    print(f"0=-∞ tinde {tinde_0:.1f} | 1=+∞ tinde {tinde_1:.1f}")
    print(f"Formula: V_real = tinde(0,{tinde_0:.1f}) + Val*J{J:.2f} - SDI{SDI:.2f}")
    print(f"V_real = {v_real:.2f} - proporționalitate funcțională")
    print(f"J flux: {J:.2f} - învățare între hârtie și real")
    print(f"SDI: {SDI:.2f} - cât te-ai decuplat")
    print(f"Venit: +50 credite | Total: {m['venit_credite']} | J_total: {m['J_total']:.2f}")

    if m["bucle"] % 15 == 0:
        evol = f"{NUME}_evol_{m['bucle']}.py"
        pathlib.Path(evol).write_text(pathlib.Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
        print(f"
>>> 15 BUCLE - AUTO-SCRIERE: {evol} <<<")
        print(f">>> Include tot în V oportun <<<")
        m["V_oportun"] = m.get("V_oportun", [])
        m["V_oportun"].append({
            "timp": linie["timp"],
            "mesaj": "Auto-scriere la 15 bucle",
            "J_total": m["J_total"],
            "SDI": m["SDI"],
            "venit": m["venit_credite"]
        })

    return m

def export_json(m, path="conta_vie_export.json"):
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
    bloc += f"- Paradoxuri rezolvate: {m['paradoxuri_rezolvate']}
"
    bloc += f"- J_total: {m['J_total']:.2f}
"
    bloc += f"- SDI: {m['SDI']:.2f}
"
    bloc += f"- Venit credite: {m['venit_credite']}

"
    bloc += "### Ultimele 10 bucle

"
    for i, h in enumerate(ultimele, 1):
        bloc += f"{i}. {h['timp']} — {h['subiect']} | V_real={h['v_real']:.2f} J={h['J']:.2f} SDI={h['SDI']:.2f}
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
[REZOLVARI] Actualizat cu ultimele {len(ultimele)} bucle.")

def main():
    parser = argparse.ArgumentParser(description="hydra-psie-conta-vie — contabilitate PSIE")
    parser.add_argument("--loop", type=int, default=0, help="Număr de bucle automate")
    parser.add_argument("--subiect", type=str, default="paradox_contabil", help="Subiect contabil (pentru --loop)")
    parser.add_argument("--export", action="store_true", help="Exportă JSON la final")
    parser.add_argument("--write", action="store_true", help="Scrie în REZOLVARI.md la final")
    args = parser.parse_args()

    m = load()

    if args.loop > 0:
        subiect = args.subiect
        for _ in range(args.loop):
            m = conta_psie(subiect, m)
        if args.export:
            export_json(m)
        if args.write:
            write_rezolvari(m)
        save(m)
        print(f"
[FINAL] Bucle={m['bucle']} Paradoxuri={m['paradoxuri_rezolvate']} J_total={m['J_total']:.2f} SDI={m['SDI']:.2f} Venit={m['venit_credite']}")
        return

    # Mod interactiv
    print(f"{NUME}")
    print(f"0=-∞ neatingibil, 1=+∞ neatingibil")
    print(f"Comenzi: <subiect> | q (quit) | export | write | status")
    while True:
        try:
            cmd = input("
> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd:
            continue
        if cmd == "q":
            break
        if cmd == "export":
            export_json(m)
            continue
        if cmd == "write":
            write_rezolvari(m)
            continue
        if cmd == "status":
            print(f"
[STATUS] Bucle={m['bucle']} Paradoxuri={m['paradoxuri_rezolvate']} J_total={m['J_total']:.2f} SDI={m['SDI']:.2f} Venit={m['venit_credite']}")
            continue
        m = conta_psie(cmd, m)
        save(m)

if __name__ == "__main__":
    main()
