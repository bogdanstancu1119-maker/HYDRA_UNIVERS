AGENTS = ["Arhivarul","Decuplatorul","Fluxorul","Asumatorul","Traducatorul","Vazatorul","Conectorul","Simplificatorul","Testerul","Deployerul","Termuxerul","Documentarul","Eticianul","Evolutorul","Gardianul"]
def run(problema, J0=10380):
    J=J0
    log=[]
    for i, ag in enumerate(AGENTS,1):
        if ag=="Gardianul" and J<300:
            log.append(f"{i}. Gardianul STOP SDI>0.7")
            break
        d=120 if ag in ("Fluxorul","Conectorul") else 50
        J+=d
        log.append(f"{i}. {ag} J+{d} => {J} | {problema[:40]}")
        if J>700 and i>=7:
            log.append(f"AUTONOMIE la {i}")
            break
        if i>=15:
            log.append("Limita 15")
            break
    return J, log
