# R5. Architektura systemu

> **48h-draft (2026-05-16) — FRAGMENT 1: SZKIELET.** Brak prozy. Tylko struktura nagłówków H1/H2/H3 z 1-zdaniowymi opisami zakresu per sub-sekcja. Po sign-off Magdy → FRAGMENT 2 (sekcje 5.1+5.2 z prozą i wykresami C4).
>
> Figury w wariancie SZKIELET (text-only listing nodów i strzałek). Polishing Mermaid post-sprint w Iteracji 7.

---

## 5.1 Wprowadzenie do architektury

> Cel R5 (CENTRALNY rozdział): opisanie warstwowej architektury systemu citation-grounded RAG z hidden-states halu probe, z naciskiem na pipeline treningu + MLOps (~37,5 % rozdziału). Wprowadzenie metody C4 [CYT: Brown 2018 C4 model] i czterech widoków systemowych: Context, Container, Inference Pipeline, Training Pipeline. Forward refs do R6 (parametryzacja modeli) i R7 (wyniki ewaluacji).

---

## 5.2 Widoki systemowe wg metody C4

### 5.2.1 Kontekst (Fig 5.1)

> System-as-blackbox + jego użytkownicy + zewnętrzne źródła. Aktorzy: Magda (developer + ewaluator), lab GPU operator (SP7 H200), Kojałowicz (promotor obserwator). Zewnętrzne systemy: ISAP (Sejm), UOKiK portal, EUR-Lex, fora konsumenckie (e-prawnik / forumprawne / Reddit / eporady24), HuggingFace Hub (dla publikacji 3 artefaktów). Granice systemu: Polish CitationBench v0.6 + pipeline citation-grounded RAG + halu detection.

### 5.2.2 Kontenery (Fig 5.2)

> Rozbicie systemu na deployable services: SGLang (Bielik 11B v3 serving), TEI (BGE-M3 + mDeBERTa serving), Qdrant (vector index), PostgreSQL (metadata + traces), FastAPI (REST API gateway), Prefect 3 (orchestration), MLflow (experiment tracking + model registry), Langfuse (LLM observability), LGTM stack (Loki + Grafana + Tempo + Mimir), Alertmanager, Gradio (UI). Relacje między kontenerami + technology stack notes.

### 5.2.3 Komponenty wewnątrz kluczowych kontenerów (Fig 5.3)

> Zoom-in na trzy kluczowe kontenery: (a) probe extraction component (PyTorch hooks layer 47 + mean-pool + sklearn LR), (b) 3-tier NLI verifier (mDeBERTa Tier 1 + HerBERT Tier 2 fallback + LLM judge Tier 3 ablation), (c) citation alignment component (claim extractor + NLI scorer + best-evidence selector). C4 Component level pokazuje internal modules tych kontenerów.

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

## 5.7 Interfejs użytkownika — Gradio (Fig 5.8 mockup)

> Front-end: Gradio 3 zakładki. (a) **Chat** — primary use case, zapytanie tekstowe → odpowiedź z citation badges + probe halu score per claim + linkowany evidence chunk. (b) **Inspect** — debugging view, pokazuje internal state pipeline'u (retrieved chunks z scores, claim extraction, NLI verdicts per Tier, probe activations). (c) **Compare** — A/B porównanie wersji pipeline'u (baseline vs probe-augmented + with/without verifier ablation). Mockup tekstowy figur 5.8 — polishing Gradio UI w Iteracji 6. Mandatory disclaimer: *„Nie udziela porad prawnych — w sprawach złożonych skontaktuj się z prawnikiem lub Rzecznikiem Konsumentów."*

---

## 5.8 Decyzje konstrukcyjne, kompromisy i podsumowanie

### 5.8.1 Decyzje konstrukcyjne (rationale)

> Tabela 5.X: top 10 decyzji konstrukcyjnych z uzasadnieniem. (a) Bielik 11B v3 jako generator + probe target — Apache 2.0, native polish, fertilność APT4 1,62 vs Mistral 3,22. (b) BGE-M3 frozen — multilingual coverage, MIT, brak fine-tune budget. (c) mDeBERTa Tier 1 — T1 PASS 80,6 %, polish explicit w training. (d) Post-hoc citation alignment domyślnie — generation-time czeka na T2 lab GPU verify. (e) Linear probe primary — Liang & Wang Dec 2025 + Dubanowska EMNLP 2025 evidence. (f) PyTorch hooks zamiast transformer-lens — natywny support 50L Mistral arch. (g) Wariant B strict policy — scope creep mitigation. (h) Prefect 3 — async natywny. (i) MLflow + Optuna — standard MLOps stack. (j) Single-machine deployment (NIE Kubernetes) — scope thesis vs production.

### 5.8.2 Kompromisy znane (trade-offs)

> Trzy kluczowe kompromisy: (a) Monolith vs microservices — wybrano monolith FastAPI z modułami, microservices = future work. (b) Hidden-states probe vs LLM-judge — probe szybszy (<100 ms vs 200-500 ms), tańszy, deterministyczny; LLM-judge dokładniejszy w edge cases (oracle baseline w R7 ablacji A3). (c) Polish-only vs multilingual — świadoma decyzja first-mover, cross-language transfer = future work.

### 5.8.3 Podsumowanie + transition do R6

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
