import socket
def net():
 try:
  socket.create_connection(("8.8.8.8",53),timeout=2)
  return True
 except: return False
print("ONLINE" if net() else "OFFLINE - lucrez local")
print("Roiul e in roiul/ - totul ok")

# [CRESTERE 2026-08-12T11:19:19.532774 Termux] Salut, Universul HYDRA e viu pe toate platformele

# [CRESTERE 2026-08-12T11:20:21.004388 sync] Sync auto reusit pe toate platformele

# [CRESTERE 2026-08-12T11:24:10.518721 Termux] exitls -l Creier_PSIE.py

# [CRESTERE 2026-08-12T11:24:11.842914 Termux] python Creier_PSIE.py

# [CRESTERE 2026-08-12T11:26:21.905674 Termux] git add . && git commit -m "seminte" && git push
