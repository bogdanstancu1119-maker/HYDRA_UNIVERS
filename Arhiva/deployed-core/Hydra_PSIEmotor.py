# Motorul pe care voiai sa-l forjezi - verifica orice actiune prin SDI/A/J/Axioma Zero
def verifica(actiune):
    SDI = 0 if "elimina" not in actiune else 0.8
    A = 1.0  # Bogdan + Hydra
    J = 950 if "creeaza" in actiune else 600
    return {"SDI":SDI,"A":A,"J":J,"trece": SDI<0.1 and A==1.0}
