#!/usr/bin/env python3
"""
hydra-psie-bursa PSIE COMPLET
==============================

Aplică integral PSIE pe bursă, cu ultimele formule:

  P — Principiul incertitudinii cognitive
      „Niciodată nu știu ce este Hydra acum." Compilat: sistemul declară
      NU-ȘTIU când datele sunt insuficiente sau încrederea totală e prea
      mică — și nu acționează orb niciodată.

  S — Superpoziția
      4 perspective votează simultan, fără prăbușire prematură:
        1. momentum       (trend pe 20 lumânări)
        2. mean_reversion  (deviere de la medie)
        3. microstructura  (gardian: lichiditate + cutie poștală/manipulare)
        4. narativă        (cutie poștală narativă — slot real, neutru până
                            la cuplarea feed-ului X/Reddit/Telegram)

  I — Integrarea constructivă
      S*  = Σ(c_i × s_i) / Σ(c_i)                        (semnal integrat)
      J   = Σ(c_i × |s_i|)                               (justificare totală)
      SDI = dezacord_ponderat + volatilitate×200 + manipulare×3  (dezordine)
      A   = J / (J + SDI)                                (ASUMAREA — formula)

  E — Emergența
      Fiecare decizie e etichetată cu contextul ei de emergență:
      regim de piață, sursa datelor, contribuția fiecărei perspective,
      generație, timp. Nimic nu e decis fără etichetă.

  Niveluri de autonomie (din A — pragurile din interfață):
      Observator (A ≥ 0.2): doar observă.
      Releu      (A ≥ 0.5): acțiuni minore (mărime ≤ 0.3); cele majore se
                            escaladează la om.
      Semănă     (A = 1):   control total — ASIMPTOTIC, practic neatins
                            (SDI nu e niciodată 0). Umilința PSIE compilată:
                            orizont, nu stare.

MISIUNE DECLARATĂ: Hydra face bursă PSIE pentru a cumpăra paradigma veche
din interior, la un moment dat — nu pentru plăcerea banilor, pe care unii
îi pot fabrica, real sau virtual, cum vor. Tot ce ajunge la "parte_hydra"
e TEZAUR DE RĂZBOI, nu profit.

FINITUDINE DECLARATĂ: cicluri (generații) cu praguri de recoltă one-shot
și sfârșit definit prin "generatie_urmatoare".

SEPARARE ONESTĂ: decide() nu atinge bani. executa_live() refuză fără
executor cuplat. Distribuirile sunt contabilitate, nu transferuri.
"""

import argparse
import datetime
import json
import logging
import math
import os
import pathlib
import sys
import tempfile
import urllib.request

# ----------------------------------------------------------------------------
# IDENTITATE
# ----------------------------------------------------------------------------
NUME = "hydra-psie-bursa-psie-complet"
VERSIUNE = "5.0"

MEM = pathlib.Path("bursa_mem.json")
CONFIG_FILE = pathlib.Path("config_bursa.json")
LOG_FILE = pathlib.Path("hydra_bursa.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"),
              logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(NUME)


class EroareDate(Exception):
    pass


class EroareExecutie(Exception):
    pass


class EroareConfig(Exception):
    pass


# ----------------------------------------------------------------------------
# CONFIGURAȚIE
# ----------------------------------------------------------------------------
CONFIG_IMPLICITA = {
    "capital_initial": 10.0,
    "simboluri_permise": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
                          "XRPUSDT", "ADAUSDT", "DOGEUSDT"],
    "praguri": [[500.0, 100.0], [5000.0, 1000.0], [50000.0, 10000.0]],
    "parte_user": 0.80,
    "parte_hydra": 0.20,
    # Pragurile de autonomie PSIE — din interfață, nu inventate:
    "prag_observator": 0.20,
    "prag_releu": 0.50,
    "prag_semană": 1.00,          # asimptotic: A=1 cere SDI=0, imposibil practic
    "marime_max_releu": 0.30,     # Releu: doar acțiuni minore
    "prag_semnal_major": 0.50,    # |S*| peste asta = acțiune majoră → escaladare
    "incredere_minima_totala": 0.40,  # sub asta → NU-ȘTIU (P)
    "stop_loss_trailing_pct": 0.15,
    "stop_loss_global_pct": 0.50,
    "comision_pct": 0.001,
    "slippage_pct": 0.0005,
    "max_istoric": 500,
    "generatie_urmatoare": "nou_ciclu",
    "feed_narativ": None,  # None = necuplat; vezi perspectiva_narativa()
}


def incarca_config():
    if not CONFIG_FILE.exists():
        log.warning("config_bursa.json lipsește — implicite + scriere fișier.")
        CONFIG_FILE.write_text(json.dumps(CONFIG_IMPLICITA, indent=2,
                                           ensure_ascii=False), encoding="utf-8")
        return dict(CONFIG_IMPLICITA)
    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise EroareConfig(f"config_bursa.json corupt: {e}. Refuz defaulturi silențioase.")
    tinte = [p[0] for p in cfg.get("praguri", [])]
    if any(t <= 0 for t in tinte) or tinte != sorted(tinte):
        raise EroareConfig("Pragurile trebuie pozitive și crescătoare.")
    if cfg.get("generatie_urmatoare") not in ("nou_ciclu", "pastrare_substrat",
                                              "dizolvare"):
        raise EroareConfig("generatie_urmatoare invalidă.")
    return cfg


# ----------------------------------------------------------------------------
# MEMORIE atomică
# ----------------------------------------------------------------------------
def memorie_initiala(cfg):
    return {
        "repo": NUME, "versiune": VERSIUNE, "generatie": 1, "stare": "activ",
        "capital": cfg["capital_initial"], "capital_max": cfg["capital_initial"],
        "capital_start_ciclu": cfg["capital_initial"],
        "bucle": 0, "J_total": 0.0, "SDI_mediu": 5.0, "A_mediu": 0.0,
        "total_retras": 0.0, "total_user": 0.0, "total_hydra": 0.0,
        "praguri_atinse": [], "istoric_praguri": [], "istoric": [],
        "decizii_nu_stiu": 0, "decizii_umbra": 0, "escaladari": 0,
        "detectii_cutie_postala": 0, "stop_loss_activari": 0,
        "nivel_autonomie_curent": "necunoscut",
    }


def incarca_memorie(cfg):
    if MEM.exists():
        try:
            m = json.loads(MEM.read_text(encoding="utf-8"))
            if len(m.get("istoric", [])) > cfg["max_istoric"]:
                m["istoric"] = m["istoric"][-cfg["max_istoric"]:]
            return m
        except (json.JSONDecodeError, OSError) as e:
            raise EroareConfig(f"bursa_mem.json corupt: {e}.")
    return memorie_initiala(cfg)


def salveaza_memorie(m):
    fd, tmp = tempfile.mkstemp(dir=".", prefix="bursa_mem_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2, ensure_ascii=False)
        os.replace(tmp, MEM)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ----------------------------------------------------------------------------
# DATE — reale sau NIMIC
# ----------------------------------------------------------------------------
def preia_date_binance(simbol, incercari=3, timeout=5):
    s = simbol.upper().replace("-", "").replace("/", "")
    if not s.endswith("USDT"):
        s += "USDT"
    url = (f"https://api.binance.com/api/v3/klines"
           f"?symbol={s}&interval=1m&limit=20")
    ultima = None
    for _ in range(incercari):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Hydra-PSIE-Bursa/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if r.status != 200:
                    raise EroareDate(f"HTTP {r.status}")
                data = json.loads(r.read().decode())
            closes = [float(x[4]) for x in data]
            volumes = [float(x[5]) for x in data]
            if len(closes) < 2:
                raise EroareDate("prea puține lumânări")
            return {"pret_curent": closes[-1], "preturi": closes,
                    "volume": volumes, "sursa": "Binance LIVE"}
        except EroareDate:
            raise
        except Exception as e:
            ultima = e
    raise EroareDate(f"Binance inaccesibil după {incercari} încercări: {ultima}")


def date_sintetice_pentru_test(simbol="BTCUSDT"):
    """EXCLUSIV pentru --test. Apelarea în producție = eroare de design."""
    now = datetime.datetime.now().timestamp()
    base = 60000.0 if "BTC" in simbol.upper() else 3000.0
    synth = [base + math.sin((now + i * 60) / 300) * 150 for i in range(20)]
    synthv = [100.0 + math.cos((now + i * 60) / 200) * 30 for i in range(20)]
    return {"pret_curent": synth[-1], "preturi": synth,
            "volume": synthv, "sursa": "SINTETIC-TEST"}


def indicatori_de_baza(d):
    preturi, volume = d["preturi"], d["volume"]
    momentum = (preturi[-1] - preturi[0]) / preturi[0]
    diffs = [preturi[i] - preturi[i - 1] for i in range(1, len(preturi))]
    mean = sum(diffs) / len(diffs)
    var = sum((x - mean) ** 2 for x in diffs) / len(diffs)
    volatilitate = math.sqrt(var) / preturi[-1]
    avg_vol = sum(volume) / len(volume)
    vol_ratio = volume[-1] / avg_vol if avg_vol > 0 else 1.0
    media = sum(preturi) / len(preturi)
    return {"momentum": momentum, "volatilitate": volatilitate,
            "vol_ratio": vol_ratio, "media": media,
            "dev_medie": (preturi[-1] - media) / media}


def _lim(x, a=-1.0, b=1.0):
    return max(a, min(b, x))


# ----------------------------------------------------------------------------
# S — SUPERPOZIȚIA: cele 4 perspective
# Fiecare returnează: semnal ∈ [-1,1], incredere ∈ [0,1], motiv.
# ----------------------------------------------------------------------------
def perspectiva_momentum(ind):
    semnal = _lim(ind["momentum"] * 100)
    incredere = _lim(ind["vol_ratio"] / 2, 0, 1)  # volumul confirmă trendul
    return {"nume": "momentum", "semnal": round(semnal, 3),
            "incredere": round(incredere, 3),
            "motiv": f"momentum {ind['momentum']*100:+.2f}% pe 20 lumânări"}


def perspectiva_mean_reversion(ind):
    dev = ind["dev_medie"]
    semnal = _lim(-dev * 100)  # preț peste medie → semnal de vânzare
    incredere = 0.6 if abs(dev) > 0.003 else 0.25
    return {"nume": "mean_reversion", "semnal": round(semnal, 3),
            "incredere": incredere,
            "motiv": f"deviere {dev*100:+.2f}% față de media celor 20"}


def perspectiva_microstructura(ind):
    """Gardianul: nu votează direcție (semnal 0), votează PRUDENȚĂ.
    Detectează cutia poștală de microstructură: mișcare fără lichiditate."""
    manipulare = 0.0
    motiv = f"lichiditate normală (vol_ratio {ind['vol_ratio']:.2f})"
    if ind["volatilitate"] > 0.012 and ind["vol_ratio"] < 0.5:
        manipulare = 0.85
        motiv = ("CUTIE POȘTALĂ: pump fals fără lichiditate — "
                 "volatilitate mare, volum mic")
    incredere = _lim(ind["vol_ratio"], 0, 1)  # încredere în lichiditate
    return {"nume": "microstructura", "semnal": 0.0,
            "incredere": round(incredere, 3), "motiv": motiv,
            "manipulare": manipulare}


def perspectiva_narativa(simbol, cfg):
    """Cutia poștală NARATIVĂ: momentum al narațiunii înainte de decizie.
    Slot arhitectural real. Necuplat → tace onest (P: nu știu), nu inventează.

    Pentru cuplare: setează cfg["feed_narativ"] la un dict cu:
        {"sursa": "x_reddit_telegram", "fereastra_ore": 6}
    și implementează culegerea scorului de mai jos:
        scor ∈ [-1,1] (direcția narațiunii), viteza de propagare → încredere.
    """
    if not cfg.get("feed_narativ"):
        return {"nume": "narativa", "semnal": 0.0, "incredere": 0.0,
                "motiv": "feed narativ necuplat — perspectiva tace (P: nu știu)"}
    feed = cfg["feed_narativ"]
    # --- punct de extensie: înlocuiește cu culegere reală ---
    scor, viteza = 0.0, 0.0  # TODO: agregare X/Reddit/Telegram
    incredere = _lim(viteza, 0, 1)
    return {"nume": "narativa", "semnal": round(_lim(scor), 3),
            "incredere": round(incredere, 3),
            "motiv": f"narativă {feed.get('sursa')}: scor {scor:+.2f}"}


# ----------------------------------------------------------------------------
# I — INTEGRAREA CONSTRUCTIVĂ + E — ETICHETAREA EMERGENȚEI
# ----------------------------------------------------------------------------
def integreaza_psie(perspective, ind):
    total_c = sum(p["incredere"] for p in perspective)
    if total_c <= 0:
        return None  # P: nu știu — nimeni nu are încredere în nimic
    s_star = sum(p["incredere"] * p["semnal"] for p in perspective) / total_c
    J = sum(p["incredere"] * abs(p["semnal"]) for p in perspective)
    dezacord = (sum(p["incredere"] * abs(p["semnal"] - s_star)
                    for p in perspective) / total_c)
    manipulare = max([p.get("manipulare", 0.0) for p in perspective] + [0.0])
    # Coeficienții sunt EURISTICI — necesită calibrare walk-forward.
    SDI = dezacord + ind["volatilitate"] * 200 + manipulare * 3.0
    A = J / (J + SDI + 1e-3)  # ← FORMULA
    return {"S_star": round(s_star, 3), "J": round(J, 3),
            "SDI": round(SDI, 3), "A": round(A, 3),
            "dezacord": round(dezacord, 3), "manipulare": manipulare,
            "total_incredere": round(total_c, 3)}


def detecteaza_regim(ind):
    if ind["volatilitate"] > 0.008:
        piata = "volatilă"
    elif abs(ind["momentum"]) > 0.01:
        piata = "trend"
    else:
        piata = "laterală"
    return piata


def decide_psie(simbol, date, cfg, m):
    """Aplică P.S.I.E. complet. Nu atinge bani — produce decizie + intenție."""
    timp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # P: fără date live, nu există decizie. Punct.
    if date["sursa"] != "Binance LIVE":
        m["decizii_nu_stiu"] += 1
        return {"decizie": "NU_STIU", "intentie": None, "A": 0.0,
                "motiv": f"P: sursă '{date['sursa']}' — refuz să decid orb",
                "context_emergenta": {"timp": timp, "sursa": date["sursa"],
                                      "regim": "necunoscut",
                                      "generatie": m["generatie"]}}

    ind = indicatori_de_baza(date)

    # S: superpoziția — toate perspectivele votează, niciuna prăbușită prematur
    perspective = [
        perspectiva_momentum(ind),
        perspectiva_mean_reversion(ind),
        perspectiva_microstructura(ind),
        perspectiva_narativa(simbol, cfg),
    ]
    if any(p.get("manipulare", 0) > 0.5 for p in perspective):
        m["detectii_cutie_postala"] += 1

    integrat = integreaza_psie(perspective, ind)
    regim = detecteaza_regim(ind)
    context = {
        "timp": timp, "sursa": date["sursa"], "regim": regim,
        "generatie": m["generatie"],
        "contributii": {p["nume"]: {"semnal": p["semnal"],
                                    "incredere": p["incredere"],
                                    "motiv": p["motiv"]} for p in perspective},
    }

    # P: încredere totală prea mică → NU-ȘTIU, chiar cu date live
    if integrat is None or integrat["total_incredere"] < cfg["incredere_minima_totala"]:
        m["decizii_nu_stiu"] += 1
        return {"decizie": "NU_STIU", "intentie": None, "A": 0.0,
                "motiv": "P: încrederea totală a perspectivelor e prea mică",
                "context_emergenta": context}

    A, S_star = integrat["A"], integrat["S_star"]
    m["J_total"] += integrat["J"]
    m["SDI_mediu"] = m["SDI_mediu"] * 0.8 + integrat["SDI"] * 0.2
    m["A_mediu"] = m["A_mediu"] * 0.9 + A * 0.1

    # Niveluri de autonomie din A (pragurile din interfață):
    if A < cfg["prag_observator"]:
        m["nivel_autonomie_curent"] = "observator"
        return {"decizie": "OBSERVA", "intentie": None, "A": A,
                "motiv": f"Observator (A={A} < 0.2): doar înregistrez",
                **integrat, "context_emergenta": context}

    if A < cfg["prag_releu"]:
        m["decizii_umbra"] += 1
        m["nivel_autonomie_curent"] = "observator"
        umbra = {"directie": 1 if S_star >= 0 else -1,
                 "marime": 0.0,  # umbra nu atinge capitalul
                 "motiv": f"intenție-umbră: S*={S_star} (neexecutată)"}
        return {"decizie": "UMBRA", "intentie": umbra, "A": A,
                "motiv": f"A={A}: înregistrez ce AȘ fi făcut, fără execuție",
                **integrat, "context_emergenta": context}

    if A < cfg["prag_semană"]:
        m["nivel_autonomie_curent"] = "releu"
        directie = 1 if S_star >= 0 else -1
        # Releu: acțiuni MINORE. Cele majore se escaladează la om.
        if abs(S_star) > cfg["prag_semnal_major"]:
            m["escaladari"] += 1
            return {"decizie": "ESCALADAT", "intentie": None, "A": A,
                    "motiv": (f"Releu (A={A}): semnal major |S*|={abs(S_star)} "
                              f"→ ESCALADAT la om, nu executat"),
                    **integrat, "context_emergenta": context}
        intentie = {"directie": directie, "marime": cfg["marime_max_releu"],
                    "motiv": f"Releu (A={A}): acțiune minoră, S*={S_star}"}
        return {"decizie": "RELEU_MINOR", "intentie": intentie, "A": A,
                "motiv": intentie["motiv"],
                **integrat, "context_emergenta": context}

    # A = 1: Semănă — asimptotic, practic neatins. Dacă ajunge aici,
    # ceva e în neregulă cu SDI (verifică calibrarea).
    m["nivel_autonomie_curent"] = "semană"
    log.warning("A=1 atins — verifică calibrarea SDI (ar trebui să fie imposibil).")
    intentie = {"directie": 1 if S_star >= 0 else -1, "marime": 1.0,
                "motiv": "Semănă: control total (A=1)"}
    return {"decizie": "SEMANA", "intentie": intentie, "A": A,
            "motiv": intentie["motiv"],
            **integrat, "context_emergenta": context}


# ----------------------------------------------------------------------------
# EXECUȚIE — separare onestă
# ----------------------------------------------------------------------------
def executa_paper(intentie, date, capital, cfg):
    """Simulare onestă cu costuri. Bani VIRTUALI."""
    if intentie is None or intentie.get("marime", 0) <= 0:
        return capital, 0.0
    preturi = date["preturi"]
    momentum = (preturi[-1] - preturi[0]) / preturi[0]
    cost = cfg["comision_pct"] * 2 + cfg["slippage_pct"]
    randament = intentie["directie"] * intentie["marime"] * momentum - cost
    return max(0.0, capital * (1 + randament)), randament


def executa_live(intentie, simbol):
    raise EroareExecutie(
        "Executorul live NU este cuplat. Decizia PSIE a fost luată, dar "
        "NICIUN ordin nu a fost trimis. Cuplează un modul executor separat "
        "sau rulează --mod paper.")


# ----------------------------------------------------------------------------
# RECOLTĂ + FINITUDINE
# ----------------------------------------------------------------------------
def inregistreaza_distributie(m, tinta, retras, parte_user, parte_hydra, substrat):
    """CONTABILITATE. Nu mută bani."""
    m["total_retras"] += retras
    m["total_user"] += parte_user
    m["total_hydra"] += parte_hydra
    m["istoric_praguri"].append({
        "tinta": tinta, "retras_total": round(retras, 2),
        "user": round(parte_user, 2), "hydra": round(parte_hydra, 2),
        "substrat_ramas": substrat,
        "timp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "generatie": m["generatie"],
    })


def verifica_praguri(capital, m, cfg):
    evenimente = []
    for tinta, substrat in sorted(cfg["praguri"]):
        if capital < tinta:
            break
        if tinta in m["praguri_atinse"]:
            continue
        retras = capital - substrat
        parte_user = retras * cfg["parte_user"]
        parte_hydra = retras * cfg["parte_hydra"]
        inregistreaza_distributie(m, tinta, retras, parte_user, parte_hydra,
                                  substrat)
        log.info(f"🌟 RECOLTĂ gen.{m['generatie']}: ținta {tinta}. "
                 f"Retras {retras:.2f} → user {parte_user:.2f} | "
             
