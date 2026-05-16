# R5. Architektura systemu

> **48h-draft (2026-05-16).** Fragmenty 1+2 ukończone (szkielet + sekcje 5.1+5.2 z prozą i 3 wykresami C4 w wariancie szkielet). Fragmenty 3-5: pending. Polishing Mermaid post-sprint w Iteracji 7.

---

## 5.1 Wprowadzenie do architektury

Rozdział 5 dokumentuje warstwową architekturę systemu citation-grounded RAG z hidden-states halu probe. Jest **centralnym rozdziałem pracy** — uzasadnia decyzje konstrukcyjne, pokazuje rozdział odpowiedzialności między kontenerami serwisowymi oraz definiuje przepływ danych przez pipeline. Z dziewięciu sekcji rozdziału trzy (5.4, 5.5, 5.6) opisują warstwę treningową i MLOps — 33,3 % rozdziału — co odpowiada deklarowanemu naciskowi na pipeline jako produkt inżynierski, a nie wyłącznie na model end-to-end.

Architektura jest udokumentowana metodą **C4** [CYT: Brown 2018 C4 model] — standardem dokumentacji architektonicznej rozróżniającym cztery poziomy abstrakcji: Context (system w otoczeniu zewnętrznych aktorów), Container (deployable services), Component (moduły wewnątrz kontenerów) oraz Code (struktura klas i funkcji). Pierwsze trzy poziomy są wykorzystane w sekcji 5.2; poziom Code jest pominięty jako za szczegółowy dla rozdziału architektonicznego — zainteresowani znajdą go w kodzie źródłowym w katalogu `main_project/src/`. Uzupełnieniem C4 są dwa widoki dynamiczne: pipeline inferencji (sekcja 5.3) i pipeline treningu (sekcja 5.4), pokazujące przepływ danych w runtime'ie.

Wybór C4 jako metody dokumentacji motywowany jest trzema czynnikami. Po pierwsze C4 jest *industry standard* w dokumentacji systemów MLOps, znanym promotorowi Kojałowiczowi z praktyki klasycznych ML pipelines. Po drugie hierarchiczna struktura *gradual zoom-in* umożliwia czytelnikowi wybranie poziomu szczegółowości adekwatnego do potrzeb — komisja egzaminacyjna może zatrzymać się na poziomie Container, recenzent szczegółowy schodzi do Component. Po trzecie C4 jest *technology-agnostic* — diagramy nie zmieniają sensu jeśli SGLang zostanie zastąpiony przez vLLM lub Qdrant przez Weaviate, co jest pożądane dla pracy o cyklu życia kilkuletnim.

Wszystkie wykresy w rozdziale generowane są w notacji **Mermaid** [CYT: Mermaid documentation], która umożliwia version-controlled diagrams (tekst w git) oraz eksport do SVG dla finalnej wersji Worda. W niniejszym 48h-draft wykresy mają postać tekstowego szkieletu (listing nodów i strzałek) — polishing do pełnej notacji Mermaid zaplanowany jest w Iteracji 7 writing phase. Pełen kod źródłowy wykresów znajdzie się w `thesis_research/diagrams/r05_*.mmd`.

Decyzje konstrukcyjne i kompromisy omówione są w sekcji 5.9. Parametryzacja modeli (hyperparams, architektury, fine-tune procedures) przeniesiona jest do Rozdziału 6. Empiryczne wyniki ewaluacji raportowane są w Rozdziale 7.

---

## 5.2 Widoki systemowe wg metody C4

### 5.2.1 Kontekst systemu (Fig 5.1)

Widok kontekstowy traktuje system jako *blackbox* i pokazuje jego użytkowników oraz zewnętrzne systemy, z którymi się komunikuje. System obejmuje całość pipeline'u Polish CitationBench: scrape źródeł, preprocessing, halu injection, training probe + verifier, serving Bielika dla inferencji oraz UI Gradio. Granice systemu są jasne — wszystko od scrape do UI należy do systemu, wszystko poza nimi jest external.

**Aktorzy systemu:**

- **Autorka (Magda)** — primary user; pełni trzy role: *developer* (kod, scrape, hyperparam tuning), *ewaluator* (anotacja 140 par gold standard, manual spot-check silver labels), *operator* (deployment Gradio na laptopie + lab GPU dla heavy compute).
- **Operator lab GPU** — pośrednik dostępu do infrastruktury PJATK SP7 H200 80GB; dostarcza compute dla treningu probe (Bielik 11B forward pass z hooks) oraz fine-tune'u Tier 2 verifier (HerBERT-large + CDSC-E).
- **Promotor (Kojałowicz)** — observer; otrzymuje artefakty (repozytorium kodu, draft pracy, demo Gradio) async via DVC pull i GitHub repo, NIE bezpośrednio interaguje z systemem runtime.

**Zewnętrzne systemy (źródła danych + sink dla artefaktów):**

- **ISAP (Sejm)** — Polish statutes (27 ustaw konsumenckich), Sejm ELI API XML + PDF.
- **UOKiK Portal** — Q&A FAQ, decyzje Prezesa, poradniki PDF.
- **EUR-Lex** — UE dyrektywy konsumenckie (8), TSUE orzeczenia (29).
- **Orzeczenia.ms.gov.pl + SN.pl** — orzecznictwo sądów powszechnych + Sądu Najwyższego.
- **Fora prawne** — forumprawne.org, e-prawnik.pl, Reddit r/Polska, eporady24.pl jako real consumer questions.
- **HuggingFace Hub** — sink dla publikacji trzech artefaktów (Polish CitationBench v0.6 + probe model + mDeBERTa verifier card).

**Fig 5.1 — szkielet wykresu C4 Context:**

```
Aktorzy (lewa strona):
  [Magda — developer + ewaluator + operator]
  [Operator lab GPU PJATK SP7 H200]
  [Promotor Kojałowicz — observer]

System (centrum):
  [System: Polish CitationBench RAG + Halu Detection]
    boundary: scrape pipeline + preprocessing + halu injection + training +
              inference RAG + 3-tier NLI verifier + halu probe + Gradio UI

Zewnętrzne systemy (prawa strona):
  [ISAP Sejm] — polskie ustawy
  [UOKiK Portal] — Q&A + decyzje + poradniki
  [EUR-Lex] — UE dyrektywy + TSUE
  [Orzeczenia.ms.gov.pl + SN.pl] — orzecznictwo sądowe
  [Fora prawne] — real consumer questions
  [HuggingFace Hub] — publikacja 3 artefaktów

Strzałki:
  Magda → System : queries + anotacje + kod
  System → Magda : odpowiedzi z citation badges + halu scores + dashboardy
  Operator lab GPU → System : GPU compute dla treningu probe + verifier
  Promotor → System : async code review, observability
  System → ISAP, UOKiK, EUR-Lex, Orzeczenia, Fora : scrape requests (one-time, NFC normalized)
  System → HuggingFace Hub : push dataset + model cards (w Iteracji 6)
```

### 5.2.2 Kontenery (Fig 5.2)

Widok kontenerowy rozbija system na *deployable services* — jednostki które można uruchomić samodzielnie, z własnym procesem, własnym formatem komunikacji i własnym tech stack. W terminologii C4 *kontener* nie oznacza Docker container, lecz logiczną granicę deploymentu — może to być proces Pythona, baza danych, serwis HTTP lub kontener Docker (większość kontenerów w pracy faktycznie jest deployowana jako Docker container w configurations dla lab GPU).

System składa się z **dwunastu kontenerów** w pięciu logicznych grupach: serving modeli ML (2 kontenery: SGLang + TEI), storage (3: Qdrant + PostgreSQL + MinIO), orchestration + experiment tracking (2: Prefect 3 + MLflow), observability (3: Langfuse + LGTM stack + Alertmanager), oraz application + UI (2: FastAPI + Gradio).

**Tabela 5.1.** Kontenery systemowe (status: ✓ = istnieje w `src/`, 🚧 = scaffolding lub planowany w Iteracji 1+).

| Kontener | Grupa | Technologia | Rola | Status |
|---|---|---|---|---|
| SGLang | Serving | SGLang 0.4 + Bielik 11B v3 bf16 | High-throughput LLM serving generator + probe extraction | 🚧 Iter. 1 |
| TEI | Serving | text-embeddings-inference (HF) + BGE-M3 + mDeBERTa | Embeddings + NLI inference, low latency | 🚧 Iter. 1 (mDeBERTa T1 PASS lokal CPU) |
| Qdrant | Storage | Qdrant 1.10 | Vector index dla retrievalu (HNSW, 1 024-dim BGE-M3) | ✓ `src/halu/qdrant_indexer.py` scaffolding |
| PostgreSQL | Storage | PostgreSQL 17 + JSONB | Metadata + traces + run history | 🚧 Iter. 3 (z Langfuse) |
| MinIO | Storage | MinIO (S3-compat) | Artifact storage dla MLflow model registry | 🚧 Iter. 2 (z MLflow) |
| FastAPI | Application | FastAPI 0.115 + Uvicorn | REST API gateway agregujący wywołania | 🚧 Iter. 1 |
| Prefect 3 | Orchestration | Prefect 3 (async) | Workflow orchestration dla pipeline'u treningu + retraining | 🚧 Iter. 2 |
| MLflow | Experiment tracking | MLflow 2.15 + S3-compat MinIO | Experiment runs + model registry + artifact storage | 🚧 Iter. 2 |
| Langfuse | Observability | Langfuse 2.x | LLM-specific tracing (prompt/response, token usage, latency per komponent) | 🚧 Iter. 3 |
| LGTM stack | Observability | Loki + Grafana + Tempo + Mimir | Logi + dashboards + distributed traces + metryki time-series | 🚧 Iter. 3 |
| Alertmanager | Observability | Prometheus Alertmanager | Routing alertów z 3 severity levels | 🚧 Iter. 3 |
| Gradio | UI | Gradio 5.x | Front-end (3 zakładki: Chat / Inspect / Compare) | 🚧 Iter. 1 MVP, Iter. 6 polish |

Środowisko developerskie wykorzystuje Python 3.13 z menedżerem pakietów *uv* [CYT: Astral uv documentation], lintingu i formatowania *ruff* (jako pojedyncze źródło prawdy stylu), type checkingu *pyrefly* w trybie strict dla `src/`, oraz testów *pytest*. Pre-commit hooks zapewniają, że `ruff format` + `ruff check` + `pyrefly check` przechodzą przed każdym commitem.

**Fig 5.2 — szkielet wykresu C4 Container (12 kontenerów w 5 grupach):**

```
Granica systemu: Polish CitationBench RAG + Halu Detection

Grupa 1 "Serving" (2):
  [SGLang : Bielik 11B v3 bf16]
  [TEI : BGE-M3 + mDeBERTa]

Grupa 2 "Storage" (3):
  [Qdrant : vector index HNSW]
  [PostgreSQL : metadata + traces]
  [MinIO (S3-compat) : artifact storage]

Grupa 3 "Orchestration + Tracking" (2):
  [Prefect 3 : workflow orchestration]
  [MLflow : experiment tracking + model registry]

Grupa 4 "Observability" (3):
  [Langfuse : LLM tracing]
  [LGTM stack : Loki/Grafana/Tempo/Mimir]
  [Alertmanager : alert routing]

Grupa 5 "Application + UI" (2):
  [FastAPI : REST API gateway]
  [Gradio : UI 3 zakładki]

Aktorzy zewnętrzni:
  [Magda] [Operator lab GPU] [Promotor]

Strzałki głównych przepływów:
  [Gradio] → [FastAPI] : REST query
  [FastAPI] → [TEI] : BGE-M3 embedding query
  [FastAPI] → [Qdrant] : vector search top-k
  [FastAPI] → [SGLang] : Bielik generation + probe hooks
  [FastAPI] → [TEI] : mDeBERTa per claim NLI scoring
  [FastAPI] → [PostgreSQL] : log trace metadata
  [FastAPI] → [Langfuse] : LLM trace
  [Langfuse, LGTM, PostgreSQL] → [Grafana dashboards] : visualization
  [LGTM Mimir] → [Alertmanager] : metric rule triggers
  [Prefect 3] → [SGLang, TEI, MLflow] : training pipeline orchestration
  [MLflow] → [MinIO] : artifact storage
  [Magda] → [Gradio] : queries
  [Magda] → [Prefect 3 CLI] : retraining triggers
  [Operator lab GPU] → [SGLang + TEI] : GPU compute access
  [Promotor] → [GitHub repo + Gradio public URL] : async observation
```

### 5.2.3 Komponenty wewnątrz kluczowych kontenerów (Fig 5.3)

Widok komponentowy zaglądamy do wnętrza trzech kluczowych kontenerów — tych, których wewnętrzna struktura jest istotna dla zrozumienia kontrybucji metodologicznej pracy. Pozostałe kontenery (Qdrant, PostgreSQL, LGTM stack itd.) są standardowymi off-the-shelf systemami i ich wewnętrzna struktura nie wymaga dokumentacji w pracy.

Status oznaczeń: ✓ = istnieje w `src/halu/` lub `src/halu/<submodule>/`, 🚧 Iter. X = planowane do implementacji w iteracji X.

**Kontener 1 — FastAPI (komponenty pipeline'u inferencji + treningu):**

- `query_handler` 🚧 Iter. 1 — entry point z UI; przekazuje query do retrievera
- `retriever` ✓ `src/halu/retriever.py` scaffolding — embeds query (TEI BGE-M3), wykonuje search w Qdrant, zwraca top-k chunków z metadata
- `prompt_builder` 🚧 Iter. 1 — assembly kontekstu z retrieved chunks + Polish-specific system prompt
- `generator_client` 🚧 Iter. 1 — wywołuje SGLang dla Bielik 11B v3 generation (streaming response)
- `probe_extractor` 🚧 Iter. 1 (`src/probe/` scaffolding) — równolegle do generation, ekstraktuje hidden states z layer 47 via PyTorch hooks
- `claim_extractor` 🚧 Iter. 1 — rozkłada generated answer na atomic claims (sentence segmentation + claim prompt)
- `nli_verifier` 🚧 Iter. 1 (`src/verifier/` scaffolding) — orchestrates 3-tier verification (mDeBERTa Tier 1 → HerBERT Tier 2 jeśli low confidence → LLM judge Tier 3 w ablacji)
- `citation_aligner` 🚧 Iter. 1 (`src/citation/` scaffolding) — selekcjonuje best-supporting evidence per claim, przypisuje badge color
- `response_builder` 🚧 Iter. 1 — agreguje wynik dla UI

**Kontener 2 — Prefect 3 + Training Pipeline:**

- `data_loader` ✓ `src/halu/dataset_builder.py` (loaders) — wczytuje raw scrape z `data/raw/`
- `preprocessor` ✓ `src/halu/dataset_builder.py` z `chunk_filter` strict policy
- `halu_generator` ✓ `src/halu/halu_injector.py` z 5 typami templates + deterministic seed
- `eval_splitter` 🚧 Iter. 1 — stratified split train/val/test per source_type
- `probe_trainer` 🚧 Iter. 1 — train loop z PyTorch hooks Bielik forward pass + sklearn LR + Optuna HP search + 3 random seeds
- `verifier_trainer` 🚧 Iter. 5 (opcjonalny) — Tier 2 HerBERT-large + CDSC-E fine-tune jeśli wymagany
- `eval_runner` 🚧 Iter. 1 — eval na primary eval set 200 par gold + bootstrap CI 95 %
- `ab_gate` 🚧 Iter. 3 — decision logic dla promote/skip do MLflow Registry
- `mlflow_logger` 🚧 Iter. 2 — params + metrics + artifacts logging

**Kontener 3 — Halu Detection Stack (cross-container):**

- `probe_extractor` 🚧 Iter. 1 (`src/probe/`) — wewnątrz FastAPI runtime + Prefect training: PyTorch hooks layer 47 + mean-pool last 5 tokens + sklearn LogisticRegression linear primary + (opcjonalnie) 1-3 layer MLP nonlinear w ablacji
- `nli_verifier` 🚧 Iter. 1 (`src/verifier/`) — Tier 1 mDeBERTa primary ✓ T1 PASS 80,6 % na lokal CPU + Tier 2 HerBERT-large + CDSC-E fallback (reserved) + Tier 3 LLM judge ablation: confidence-based fallback chain z threshold 0,5
- `citation_aligner` 🚧 Iter. 1 (`src/citation/`) — claim extractor + best-evidence selector + halu score aggregator

**Fig 5.3 — szkielet wykresu C4 Component (3 zoom-ins):**

```
Zoom-in 1: FastAPI Container internals
  [query_handler]
    → [retriever]
      → [TEI: BGE-M3 embed]
      → [Qdrant: vector search top-k]
    → [prompt_builder]
    → [generator_client]
      → [SGLang: Bielik 11B v3]
    → (parallel) [probe_extractor]
      → [SGLang: hidden states layer 47]
    → [claim_extractor]
    → [nli_verifier]
      → [TEI: mDeBERTa Tier 1]
      → (fallback) [TEI: HerBERT Tier 2]
      → (ablation) [SGLang: LLM judge Tier 3]
    → [citation_aligner]
    → [response_builder]
    → output do UI

Zoom-in 2: Prefect 3 Training Pipeline internals
  [data_loader] z data/raw/
    → [preprocessor] dataset_builder.py + chunk_filter strict
    → [halu_generator] halu_injector.py 5 typów + seed 42
    → [eval_splitter] stratified by source_type
    → (parallel branch) [probe_trainer]
      → [PyTorch hooks Bielik layer 47]
      → [sklearn LR + Optuna HP search]
      → [3 random seeds + bootstrap CI 95%]
      → [MLflow logger]
    → (parallel branch) [verifier_trainer] (Tier 2 HerBERT + CDSC-E, opcjonalne)
    → [eval_runner] na primary eval set 200 par gold
    → [ab_gate] decision logic
    → [MLflow Registry] promote/skip

Zoom-in 3: Halu Detection Stack (cross-container)
  [probe_extractor] cross-container:
    - runtime: FastAPI runtime path
    - training: Prefect 3 training path
    - shared core: PyTorch hooks + sklearn LR linear primary
  [nli_verifier] cross-container Tier 1 → Tier 2 → Tier 3:
    - Tier 1: TEI mDeBERTa (production default, T1 PASS 80.6%)
    - Tier 2: TEI HerBERT-large + CDSC-E fine-tune (reserved fallback)
    - Tier 3: SGLang LLM judge (Bielik/PLLuM/Gemma 3/Claude Haiku ablation w R7)
    - confidence-based routing z threshold 0.5
  [citation_aligner]:
    - claim_extractor (sentence segmentation + claim prompt)
    - best_evidence_selector (highest NLI entailment score)
    - halu_score_aggregator (probe + verifier combined signal)
```

Trzy zoom-iny pokrywają wszystkie kontenery, których wewnętrzna struktura jest *contribution-specific* dla pracy. Standardowe off-the-shelf services (Qdrant, PostgreSQL, Loki, Grafana itd.) są używane zgodnie z domyślną konfiguracją i nie wymagają zoom-inu.

---

---

## 5.3 Pipeline inferencji RAG (Fig 5.4)

> Runtime view: zapytanie użytkownika → BGE-M3 query embedding → Qdrant retrieve top-k (k=5) → context assembly → Bielik 11B v3 generation (Outlines structured output dla generation-time citations w ablacji A4, post-hoc default) → claim extraction (sentence segmentation + claim prompt) → 3-tier NLI verifier per claim → citation badge assignment (zielony/żółty/czerwony) → response do UI. Plus parallel branch: probe scoring per claim (independent halu signal). Latency budget breakdown per komponent.

---

## 5.4 Pipeline treningu (Fig 5.5)

> Training view (MLOps part 1): raw data scrape (`data/raw/`) → preprocessing (`dataset_builder.py`) → halu injection (`halu_injector.py`, 5 typów, RNG seed=42) → eval split (stratified by source_type) → probe training loop (PyTorch hooks Bielik forward pass → extract layer 47 activations → mean-pool last 5 tokens → train sklearn LR z Optuna HP search → 3 random seeds) → MLflow tracking (params + metrics + artifacts) → eval na primary eval set (200 par gold) → A/B gate decision → MLflow Model Registry promote/skip. Plus parallel branch: Tier 2 HerBERT-large + CDSC-E fine-tune (opcjonalnie w Iteracji 5).

---

## 5.5 Continuous improvement loop (Fig 5.6)

> MLOps part 2: production traces z Langfuse → failure detection (probe alarms + verifier contradictions z low confidence) → preference dataset construction → probe retraining (cykl N+1) → eval na hold-out set → A/B test gating (canary deployment 5 % traffic) → promote do production lub rollback. 3 cykle per RQ3 z plateau analysis. Drift triggers: halu rate spike (>2σ baseline) lub embedding distribution shift (Alibi Detect KS p<0.01) → automatic retraining trigger.

---

## 5.6 Observability + drift detection (Fig 5.7)

> MLOps part 3: Langfuse LLM-specific traces (token usage, latency per komponent, prompt/response logging) → OpenTelemetry SDK distributed tracing → LGTM stack (Loki logs, Grafana dashboards, Tempo distributed traces, Mimir metrics time-series) → Evidently data drift na embeddings distributions (KS test) + halu rate distribution drift (chi-square per source_type) + Alibi Detect MMD na hidden activations distributions → Alertmanager rule engine z 3 severity levels (info / warning / critical). Per-metric alerting thresholds + escalation path.

---

## 5.7 Bezpieczeństwo, prywatność, compliance

> Krótka sekcja (~400-600 słów). (a) **Anonimizacja PII** — Reddit usernames sha1:10, forum regex redaction (PESEL/NIP/REGON/email/telefon polski +48), audit v0.6 confirms zero residual PII. (b) **Polish TDM exception (Wrzesień 2024)** jako legal basis dla scraping źródeł publicznych, opt-out signals verification per source. (c) **License compliance** — mixed-license corpus z explicit per-chunk attribution w polu `license`; Wikipedia CC BY-SA share-alike caveat raportowany w karcie HF dataset. (d) **Mandatory UI disclaimer** — Gradio explicit *„Nie udziela porad prawnych"*, fail-closed pattern jeśli LLM próbuje udzielać porady. (e) **EU AI Act note** — system klasyfikowany jako *informacyjny* (NIE high-risk legal advisory per Annex III), ale future production deployment wymagałby risk assessment per AI Act Title III. (f) **RODO art. 17 right to be forgotten** — local hashmap mapowania anonimowych ID do oryginalnych Reddit usernames umożliwia re-identyfikację dla usunięcia.

---

## 5.8 Interfejs użytkownika — Gradio (Fig 5.8 mockup)

> Front-end: Gradio 3 zakładki. (a) **Chat** — primary use case, zapytanie tekstowe → odpowiedź z citation badges + probe halu score per claim + linkowany evidence chunk. (b) **Inspect** — debugging view, pokazuje internal state pipeline'u (retrieved chunks z scores, claim extraction, NLI verdicts per Tier, probe activations). (c) **Compare** — A/B porównanie wersji pipeline'u (baseline vs probe-augmented + with/without verifier ablation). Mockup tekstowy figur 5.8 — polishing Gradio UI w Iteracji 6. Mandatory disclaimer: *„Nie udziela porad prawnych — w sprawach złożonych skontaktuj się z prawnikiem lub Rzecznikiem Konsumentów."*

---

## 5.9 Decyzje konstrukcyjne, kompromisy i podsumowanie

### 5.9.1 Decyzje konstrukcyjne (rationale)

> Tabela 5.X: top 10 decyzji konstrukcyjnych z uzasadnieniem. (a) Bielik 11B v3 jako generator + probe target — Apache 2.0, native polish, fertilność APT4 1,62 vs Mistral 3,22. (b) BGE-M3 frozen — multilingual coverage, MIT, brak fine-tune budget. (c) mDeBERTa Tier 1 — T1 PASS 80,6 %, polish explicit w training. (d) Post-hoc citation alignment domyślnie — generation-time czeka na T2 lab GPU verify. (e) Linear probe primary — Liang & Wang Dec 2025 + Dubanowska EMNLP 2025 evidence. (f) PyTorch hooks zamiast transformer-lens — natywny support 50L Mistral arch. (g) Wariant B strict policy — scope creep mitigation. (h) Prefect 3 — async natywny. (i) MLflow + Optuna — standard MLOps stack. (j) Single-machine deployment (NIE Kubernetes) — scope thesis vs production.

### 5.9.2 Kompromisy znane (trade-offs)

> Trzy kluczowe kompromisy: (a) Monolith vs microservices — wybrano monolith FastAPI z modułami, microservices = future work. (b) Hidden-states probe vs LLM-judge — probe szybszy (<100 ms vs 200-500 ms), tańszy, deterministyczny; LLM-judge dokładniejszy w edge cases (oracle baseline w R7 ablacji A3). (c) Polish-only vs multilingual — świadoma decyzja first-mover, cross-language transfer = future work.

### 5.9.3 Podsumowanie + transition do R6

> Recap 4 view stack (Context / Container / Inference / Training). MLOps stanowi 37,5 % rozdziału (sekcje 5.4 + 5.5 + 5.6). Wszystkie 7 figur Mermaid + 1 mockup Gradio. R6 dokumentuje parametryzację modeli (probe hyperparams Optuna, verifier fine-tune config jeśli Tier 2, generator config Bielik). R7 raportuje empirical results pipeline'u.

---

## Źródła robocze (do uzupełnienia per FRAGMENT)

- C4 model: Simon Brown [CYT: Brown 2018 C4 model]
- BGE-M3 [CYT: Chen 2024 BGE-M3 arXiv:2402.03216]
- mDeBERTa [CYT: MoritzLaurer mDeBERTa-v3-base-xnli HF]
- Bielik APT4 [CYT: Ociepa 2025 Bielik v3 APT4 arXiv:2604.10799]
- Prefect 3 official docs; MLflow; Langfuse; Evidently; Alibi Detect
- Outlines structured output [CYT: Uğur 2025 Guided Decoding RAG arXiv:2509.06631]
- Liang & Wang Dec 2025 + Dubanowska EMNLP 2025 — probe architecture rationale
