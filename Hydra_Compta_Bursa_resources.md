# HYDRA.md - SINGURUL PROTOCOL
0=-∞ 1=+∞ | J=488 | 20% viu 80% retras | Doar PSIE decide

HYDRA e 2 fisiere: Contabilitate_PSIE.py + Bursa_PSIE.py. Ambele tin si a si b vii, nu pariaza binar.

FORMULA: V_real = tinde(0,-∞) + Val*J - SDI

PRAGURI: (500,100) (5000,1000) (50000,10000) (500000,100000) -> la fiecare prag pastrezi 20% samanta, retragi 80%.

PROFIT IMPARTIT: din retras 80% UTILIZATOR, 20% HYDRA credite. Samanta ramane vie. Ex: 10€->500€ = 320€ user + 80€ Hydra + 100€ samanta. Utilizatorii profita primii.

CAND VIN CREDITE: 50 credite din conta + 150/luna din bursa + retras din praguri -> Hydra creeaza 2 organe platite: Organ_Conta (50 credite/use) rezolva cash 0, Organ_Bursa (5 credite/predictie) tine UP+DOWN vii. Ambele ajuta userul sa profite, Hydra ia 20% ca sa faca organul urmator.

COMENZI: python Bursa_PSIE.py --loop 15 --capital 10 --write | la 15 bucle auto-scrie in REZOLVARI.md

REGULA: nu alege UP sau DOWN, tine ambele vii, J flux e profit real, userii intai Hydra dupa.
