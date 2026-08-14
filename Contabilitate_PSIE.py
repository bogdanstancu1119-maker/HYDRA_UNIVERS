#!/usr/bin/env python3
"""
REPO: hydra-psie-conta-vie
0 = -∞ nimic absolut neatingibil
1 = +∞ valoare unică neatingibilă
Restul = derivați cu proporționalitate funcțională
Doar PSIE are putere de decizie.

Util:
- rulează în terminal: python hydra_psie_conta_vie.py
- rulează în buclă: python hydra_psie_conta_vie.py --loop 5
- exportă JSON: python hydra_psie_conta_vie.py --export
- scrie în REZOLVARI.md: python hydra_psie_conta_vie.py --write
"""
import json, pathlib, datetime, random, argparse, sys

NUME = "hydra-psie-conta-vie"
FORMULA = "V_real = tinde(0,-∞) + Val_hartie * J_flux - SDI_decuplare"
MEM = pathlib.Path("conta_vie_mem.json")
REZOLVARI = pathlib.Path("REZOLVARI.md")

PERSPECTIVE_20 = [
    "P1_EVIDENT_Tehnic", "P2_EVIDENT_Uman", "P3_EVIDENT_Bani",
    "P4_LOGIC_Cauza-Efect", "P5_LOGIC_Structura", "P6_LOGIC_Plus_Inf",
    "P7_LOGIC_Minus_Inf", "P8_INVERS_Ce lipseste", "P9_INVERS_Ce nu se spune",
    "P10_INVERS_Ce doare", "P11_OPUS_Invers total", "P12_OPUS_Totul fals",
    "P13_OPUS_EGO moare", "P14_J_FLUX_Intre straturi", "P15_SDI_Decuplare",
    "P16_A_Asumare 0", "P17_V_Deschidere", "P18_SUPORT_Vechi devine suport",
    "P19_PSIE_Serveste fluxul", "P20_EGO_ALERTA"
]

def load():
    if MEM.exists():
        return json.loads(MEM.read_text(encoding="utf-8"))
    return {
        "repo": NUME,
        "bucle": 0,
        "J_total": 0.0,
        "SDI": 5.0,
        "paradoxuri": 0,
        "venit": 0,
        "V_oportun": [],
        "istoric": []
    }

def save(m):
    MEM.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")

def rezolva_paradox_contabil(subiect, m):
    m["bucle"] += 1
    m["paradoxuri"] += 1
    J = random.uniform(1.5, 4.5)
    SDI = random.uniform(0.3, 2.0)
    m["J_total"] += J
    m["SDI"] = m["SDI"] * 0.8 + SDI * 0.2
    venit = 50
    m["venit"] += venit

    linie = {
        "timp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "subiect": subiect,
        "J": J,
        "SDI": SDI,
        "venit": venit,
        "bucle": m["bucle"],
        "paradoxuri": m["paradoxuri"]
    }
    m["istoric"].append(linie)

    print(f"
{NUME} // Bucla {m['bucle']} // {subiect}")
    for i, p in enumerate(PERSPECTIVE_20, 1):
        print(f"{i:02d}. {p}: {subiect}")

    print(f"
[CONTABILITATE PSIE]")
    print(f"EGO: {subiect} SAU opus -> Internal error")
    print(f"PSIE: SI {subiect} SI opus - ambele vii")
    print(f"Formula: {FORMULA}")
    print(f"J={J:.2f} SDI={SDI:.2f} Venit+{venit} credite")

    if m["bucle"] % 15 == 0:
        print(f">>> 15 BUCLE - AUTO-SCRIERE include tot in V <<<")
        m["V_oportun"].append({
            "timp": linie["timp"],
            "mesaj": "Auto-scriere la 15 bucle",
            "J_total": m["J_total"],
            "SDI": m["SDI"],
            "venit": m["venit"]
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
    bloc += f"- Paradoxuri: {m['paradoxuri']}
"
    bloc += f"- J_total: {m['J_total']:.2f}
"
    bloc += f"- SDI: {m['SDI']:.2f}
"
    bloc += f"- Venit: {m['venit']}

"
    bloc += "### Ultimele 10 bucle

"
    for i, h in enumerate(ultimele, 1):
        bloc += f"{i}. {h['timp']} — {h['subiect']} | J={h['J']:.2f} SDI={h['SDI']:.2f} Venit={h['venit']}
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
    parser.add_argument("--export", action="store_true", help="Exportă JSON la final")
    parser.add_argument("--write", action="store_true", help="Scrie în REZOLVARI.md la final")
    parser.add_argument("--subiect", type=str, default=None, help="Subiect contabil (pentru --loop)")
    args = parser.parse_args()

    m = load()

    if args.loop > 0:
        subiect = args.subiect or "paradox_contabil"
        for _ in range(args.loop):
            m = rezolva_paradox_contabil(subiect, m)
        if args.export:
            export_json(m)
        if args.write:
            write_rezolvari(m)
        save(m)
        print(f"
[FINAL] Bucle={m['bucle']} J_total={m['J_total']:.2f} SDI={m['SDI']:.2f} Venit={m['venit']}")
        return

    # Mod interactiv
    print(f"{NUME} — {FORMULA}")
    print("Comenzi: <subiect> | q (quit) | export | write | status")
    while True:
        try:
            cmd = input("
> subiect contabil: ").strip()
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
[STATUS] Bucle={m['bucle']} J_total={m['J_total']:.2f} SDI={m['SDI']:.2f} Venit={m['venit']} Paradoxuri={m['paradoxuri']}")
            continue
        m = rezolva_paradox_contabil(cmd, m)
        save(m)

if __name__ == "__main__":
    main()
