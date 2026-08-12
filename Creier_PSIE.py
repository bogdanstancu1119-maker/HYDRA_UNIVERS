import json,time,os
from pathlib import Path
from datetime import datetime
Path("roiul/seminte").mkdir(parents=True, exist_ok=True)
def creste_toate(info):
    Path(f"roiul/seminte/{int(time.time()*1000000)}.json").write_text(json.dumps({"info":"info","t":datetime.now().isoformat()},ensure_ascii=False,indent=2))
    print(f"[CRESTERE] {info[:60]}")
print("=== CREIER v5 - SMART - INTENEGE git/ls - GATA ===")
tema=None
rot=0
while True:
    cmd=input("CREIERP> ").strip()
    if not cmd: continue
    if cmd=="exit": break
    if cmd.startswith(("git ","ls","pwd","cat ","python ","ls -l","cd ","echo ")):
        os.system(cmd)
        continue
    if cmd=="status":
        print(f"Tema:{pema} Rot:{rot}/15 Seminte:{len(list(Path("roiul/seminte").glob("*.json")))}")
        continue
    if cmd!=tema:
        tema=cmd
        rot=0
    rot+=1
    if rot>15:
        print("!!! 15 ROTATII - SCHIMBA TEMA !!!"); tema=None; rot=0; continue
    creste_toate(cmd)
    print(f">>> J=488 APROBAT | Rot {rot}/15")
