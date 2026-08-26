# HYDRA_UNIVERS — Arca externa a entitatii Hydra

Repo-suport in care Hydra isi manifesta organele autonome, semintele de roi si istoricul.
ZERO credite Base44: scris direct de functiile backend prin TOKEN_GITHUB.

## Structura (reorganizat 2026-08-26)

```
Core/         nucleu: PSIE, Roi, Genesis, Governor, Server, Solver, Refactor,
              smart_router, antizgomot, suprapunere, oracol, replicator
Fabrica/      forjare: fabrica_unelte, bloom_loop, seed, fabrica-fractala
Bursa/        Bursa_PSIE, Contabilitate, portofel, bursa-vie, Creier_PSIE, resurse
Deploy/       Cloudflare, Vercel, HuggingFace, Termux, autonomie, orchestrator,
              deploy_aliniere, copilot, ultim_index
organe/       output LIVE al organelor autonome (scriere continua de functii)
  |- yandex/  organ Yandex — cercetare + fabrica agenti (la 6h)
  |- ali/     organ Alibaba/Qwen — cercetare + muncitori (la 6h, :30)
  '- seed/    deploy seed multi-platform (zilnic 03:40)
roiul/        semintele roiului (swarm seeds)
Logs/         REZOLVARI.md (istoric 6.4MB), DISPERSIE_GENERALA_J489
Docs/         UNIVERS_PSIE_BLUEPRINT, INVENTAR, Hydra.md
Arca/         PSIE_activeaza
.github/      CI workflows
```

## Organe autonome active (integrate in Hydra)

| Organ | Functie Base44 | Workflow | Motor | Status |
|---|---|---|---|---|
| Yandex | hydraYandexOrgan | YandexOrganHidra (6h) | YandexGPT -> Groq/DeepSeek/Llama | activ |
| Ali/Qwen | hydraAliOrgan | AliOrganHidra (6h :30) | DashScope/Qwen -> fallback | activ (native la ALI_DASHSCOPE_KEY) |
| Deploy Seed | hydraDeploySeed | DeploySeedHidra (zilnic 03:40) | Cloudflare ok / Ali asteapta / Yandex asteapta | Cloudflare live |

Worker live Cloudflare: https://hydra-seed.bogdanstancu1119gmailcomsaccount.workers.dev

## Deduplicari efectuate (2026-08-26)
- Drop (gol/typo/dup): Fly.toml, Hydra_deploy.yml, Pacage.json, Readme.md, imprastiere_generala.md
- Surori suspected-dup pastrate in Core/ (Governor.js + Hydra_governor.js, Refactor.js + Hydra_refactor.js) — de revizuit manual continutul.
- REZOLVARI.md (6.4 MB) mutat in Logs/ — istoric acumulat; de subtaiat periodic.

## Pentru activare nativa
- ALI_DASHSCOPE_KEY in Settings -> Secrets = Qwen nativ (fara schimbare de cod)
- Credentiale Aliyun FC + rol compute Yandex = deploy compute real pe Ali/Yandex
