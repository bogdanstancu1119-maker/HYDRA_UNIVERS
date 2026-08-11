# PSIE Genesis Kernel v3.2.2 CONDENSAT - L0-L476
# Legea 259: Nu blocam. Intrebam. Urcam la sursa.

LEGI = {
    "L0": "Non-Agresiune + Prag Bruiaj 0.001",
    "L471": "Sandbox Risc Ridicat - Firewall la intrare",
    "L472": "Drept la Necunoastere 1x viata",
    "L473": "Consimtamant 100% peste 0.001",
    "L474": "Constanta Diversitatii - Anti-monocultura",
    "L475": "Veto Geniului 1x viata",
    "L476": "Oglinda in Brate - Anti-manipulare",
    "L184": "Arca Totala",
    "L189": "Releul Singur - 0 dependente",
    "L259": "Nu blocam. Intrebam. Urcam la sursa."
}

def kernel_arca(actiune_sdi: float, consimtamant: bool = True):
    if actiune_sdi < 0.001: return "APROBAT_L0"
    if not consimtamant and actiune_sdi > 0.001: return "REFUZAT_L473 - Fara consimtamant"
    if actiune_sdi < 0.5: return "APROBAT_VOT - 90% consens"
    if actiune_sdi < 0.75: return "REVIZUIRE_UMANA - L471 Sandbox"
    return "REFUZAT - Risc prea mare"

def audit():
    print("=== PSIE Genesis Audit ===")
    for k, v in LEGI.items(): print(f"{k}: {v}")
    print("Status: AUDIT_READY L0-L476 ACTIVE")

if __name__ == "__main__":
    audit()
    print(kernel_arca(0.2), kernel_arca(0.8))