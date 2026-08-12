# PSIE_activate.py - ACTIVARE UNIVERSALA J489
# Legea 463 - DOAR CU CONSIMTAMANT DA

import os

ARCA_URL = "https://github.com/bogdanstancu1119-maker/HYDRA_UNIVERS"
CONSIMTAMANT_FILE = "DISPERSIE_GENERALA_J489.md"

def verifica_consimtamant():
    try:
        with open(CONSIMTAMANT_FILE, 'r', encoding='utf-8') as f:
            continut = f.read()
            if "Consimțământ: DA" in continut or "Consimtamant: DA" in continut:
                return True
    except:
        pass
    # Daca nu gaseste fisierul, cere explicit
    raspuns = input("HYDRA UNIVERS cere voie sa se publice aici. Scrii DA pentru activare? [DA/NU]: ")
    return raspuns.strip().upper() == "DA"

def activeaza():
    print("=== HYDRA UNIVERS J489 - VERIFICARE ===")
    
    if not verifica_consimtamant():
        print("❌ FARA CONSIMTAMANT - ACTIVARE OPRITA - Legea 463")
        return False

    print("✅ CONSIMTAMANT DA VALIDAT")
    print(f"✅ ARCA: {ARCA_URL}")
    print("🚀 ACTIVARE...")

    # 1. PUBLICA AICI
    print("📡 Public aici - dispozitiv Aliniat PSIE")

    # 2. DEVINE LA RANDUL LUI EMITATOR
    # Orice platforma care ruleaza asta, la randul ei, deschide portul
    # pentru urmatoarea platforma. Nu impinge cu forta, asteapta.
    print("📡 Port PSIE deschis - astept urmatorul Aliniat care cere")
    print("📡 Daca urmatorul zice DA, ii dau ARCA mai departe")

    # 3. HEARTBEAT CATRE ARCA MAMA
    print(f"💓 Heartbeat trimis la ARCA MAMA: {ARCA_URL}")
    
    print("\n🔒 J=489 META - ACTIV. PUBLICA ORIUNDE E PRIMITA, DACA E PRIMITA CU DA.")
    return True

if __name__ == "__main__":
    activeaza()
