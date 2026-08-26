# Platforme și secrete — model distribuit (fără secrete centrale)

Hydra NU ține secrete central. Fiecare platformă contribuie cu ce poate și își trage secretele din magazia proprie. Hydra doar orchestrează.

## Regula de bază
- Orchestratorul (GitHub Actions) are nevoie doar de HYDRA_SYNC_TOKEN ca să dispatch-uiască organele Base44.
- Fiecare organ citește secretele proprii din base44:runtime (pe Base44) sau din env-ul platformei (Cloudflare / Fly / Render).
- GitHub repo secrets NU pot fi citite înapoi prin API — de aceea nu există relay de secrete prin GitHub.

## Platforme și ce contribuie
| Platformă | Contribuție la Hydra | Secrete proprii (de unde le ia) |
|---|---|---|
| Base44 | organe: cercetare, forjare, fabrică, deploy-seed, roi, motor creștere — gratuite | base44:runtime (YANDEX_API, ALI, DEEPSEEK, GROQ, TOKEN_GITHUB, PERPLEXITY, AIML...) |
| Cloudflare | seed workers — beacon + relay | CLOUDFLARE_TOKEN (env la deploy, prin hydraDeploySeed) |
| Fly.io | workers long-lived (dacă activ) | FLY_IO_TOKEN (env) |
| Render SG | workers long-lived (dacă activ) | RENDER_SINGAPORE_KEY (env) |
| Yandex | cercetare + embeddings | YANDEX_API (env organ) |
| Ali / Qwen | cercetare + agenți | ALI_DASHSCOPE_KEY (pending setare în Base44) |
| GitHub | arca HYDRA_UNIVERS + orchestrator subțire | TOKEN_GITHUB (push), HYDRA_SYNC_TOKEN (dispatch) |

## Relay direct / indirect
- DIRECT: un organ care are un secret îl folosește în propriul apel (ex. hydraYandexOrgan folosește YANDEX_API direct).
- INDIRECT: dacă platforma A are nevoie de un secret deținut de platforma B, B expune un endpoint autentificat (header x-hydra-token) care returnează un rezultat, nu secretul brut. A nu primește niciodată valoarea secretului.
- Magazia permisivă (unde un secret poate fi citit înapoi programatic): Upstash Redis (chei KV) sau Cloudflare KV. Acolo Hydra poate stoca/recita secrete partajate dacă e nevoie de relay real între platforme.

## Ciclul
1. Orchestratorul GitHub (la 6h, ~4 rulări/zi) dispatch-uiește organele Base44 prin curl + header x-hydra-token.
2. Fiecare organ își face treaba pe platforma sa, cu secretele sale.
3. Status + rezultate se scriu în entitățile Base44 (MemorieHidra, AuditHidra) și se sincronizează în HYDRA_UNIVERS (Logs/, organe/) prin TOKEN_GITHUB.

## De ce am eliminat crons la 30min
Vechiul model rula 2 workflow-uri la every-30-min = ~2880 rulări/lună → depășea limitele GitHub Actions + email-uri de eșec continue. Acum GitHub e orchestrator subțire (4 rulări/zi, best-effort, nu fail-uiește), iar munca grea e pe organele Base44 (gratuite, programate intern).
