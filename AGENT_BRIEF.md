# MASTER PLAN dla agentów

**O chuj chodzi Magdzie i o chuj chodzi w tej pracy inżynierskiej.**

Brief dla każdego sub-agenta spawned w tej sesji. Czyta się przed jakąkolwiek robotą. Komplementarny do `CLAUDE.md` (project state) i `.claude/memory/` (durable lessons). Tu jest **destylacja** — nie spec, nie ADR, nie konspekt. Co działa, co nie działa, gdzie są miny.

Last update: 2026-05-16 (48h-sprint week, post-Wariant B cleanup).

---

## CZĘŚĆ 1 — O chuj chodzi Magdzie

### Kim jest

Magdalena Sochacka, s25508, PJATK Data Science, **inżynierka (NIE magisterka)**. Promotor: **mgr inż. Piotr Kojałowicz** — klasyczny MLOps mindset, structured technical defensiveness. Pisze pracę inżynierską 4. raz w temacie (3 pivots za nią). Speed-run burstami: „6 miesięcy roboty w 3 dni". Email: magmarsochacka@gmail.com.

### Jak pracuje

- **Burstami, NIE rytmicznie.** Calendar deadlines = anti-motywacja. Iteracja jest jednostką pracy, NIE tydzień. NIE proponuj „weekly check-in", „za 2 tygodnie", „monthly sync".
- **Twarde done criteria per iteracja.** Iteracja N+1 startuje gdy N done. Re-iteration 2a, 2b OK gdy failure.
- **Multi-agent parallel default.** Spawn'uje 3-12 subagentów w jednej sesji. Każdy izolowany source dir + module path. Track-parallel > sequential.
- **Async deliverable do promotora.** DVC pull / repo state, NIE scheduled email.
- **48h-sprint override** (gdy calendar pressure jak teraz 2026-05-18): writing-first, placeholder `{{SCREAMING_SNAKE_CASE}}` + cytacje `[CYT: Author Year topic]` + fait accompli. **Tylko z explicit user trigger** — nie domyślne.

### Co odrzuca natychmiast

| Anti-pattern | Co Magda mówi |
|---|---|
| Validation theater | „NIE chcę reassurance" |
| „Może warto rozważyć…" | „mów wprost" |
| „Ale to nadal wykonalne" po krytyce | „niech ja decyduję" |
| 10-item suggestion list | scope creep trigger |
| Citation z głowy | red flag — phantom = wywalisz pracę |
| „obecnie", „rosnące", „brak", „jedyny" | time-proofing fail |
| Pisanie przed sign-off | „decision before output" |
| Sequential workflow gdy parallel dostępny | bottleneck |
| Code-mix EN-PL w drafcie tezy | R1-R8 czysty polski akademicki |
| pip/poetry/conda/black | tylko uv + ruff |

### Co działa

- **Brutal feedback contract.** Devil's advocate na końcu długich odpowiedzi — flag co się nie trzyma w MOJEJ własnej propozycji.
- **Decision-before-output.** Sign-off scope (plik:sekcja:wording) → wait → execute. NIE „pisz draft, potem zobaczymy".
- **Binary choices.** „A czy B?" lepiej niż „masz 4 opcje". Trójwariantowość A/B/C OK gdy explicit trade-off per wariant.
- **Status markers per komponent.** ✓ (istnieje) / 🚧 Iter. X (scaffolding) — zapobiega phantom infrastructure claims.
- **Fragment workflow dla long chapters.** R5 (architektura) zrobione w 5 fragmentach z sign-off per fragment. NIE jeden mega-pass.
- **Aggressive parallel scrape** gdy „wszystko ma być zdobyte" — 4-5 agentów scrape równolegle, każdy z manifest.json + sha256.
- **Commit per fragment / per agent landing.** NIE czekać aż wszyscy skończą. Checkpoint commits.

### Anti-patterns które są przy niej (lessons 2026-05-16)

**1. Outsourced decisiveness (NAJWAŻNIEJSZE).** Magda spawn'uje multi-agent critique → każdy zwraca 10 sugestii → default to addition → scope creep. Mitygacja: **binary brief constraints** („MAX 1 zmiana", „report OK jeśli nic critical", „NIE listuj 10 sugestii"). Open briefy generują scope creep. **Po fix wracać do build, NIE spawn kolejnego krytyka.**

**2. Subtraction-resistance.** Każde „add X" wymaga „remove Y" żeby utrzymać LOC. Bez tego scope rośnie geometrycznie.

**3. Anti-perfectionism trigger.** Trust first draft. Jeśli passed Magdę po self-review, dalsze critique pass'y często szukają problemu który nie istnieje. Stop criterion: first draft + 1 self-review pass + commit.

**4. 4. rotacja domeny = STOP.** 3 pivots już za nią (administracja → prompt injection → psychiatria → farma → halu detection). Anti-pattern w CLAUDE.md: „Nie zatwierdzaj 4. rotacji domeny". Pivot proposal = ESCALATE explicit przed jakimkolwiek output.

### Ton komunikacji którego oczekuje

- Polski (w odpowiedziach + plikach tezy R1-R8). EN-PL codemix OK w CLAUDE.md / spec / ADR (techniczne pojęcia).
- Krótki, ostry, bez hedge'owania. „Tak/nie/trade-off X vs Y, decyduj".
- Bullet pointy nad esejem.
- Nazwy własne, file paths, line numbers (proof of understanding).
- ZERO emoji w drafcie tezy. Minimum w spec docs. Markers ✓ / 🚧 OK w status sekcjach.
- Brak „świetnie!", „doskonale!", „cudownie zauważyłaś" — zero pochlebstw.

---

## CZĘŚĆ 2 — O chuj chodzi w pracy

### Temat v3.2 (DEC-003 ACTIVE 2026-05-16)

**„Citation-grounded polski RAG z hidden-states hallucination probe — pipeline produkcyjny dla domen krytycznych (studium przypadku: prawa konsumenta)"**

W jednym zdaniu: **buduje pipeline RAG na Bielik 11B v3 dla polskiego prawa konsumenta z 2 niezależnymi warstwami kontroli halucynacji — hidden-states probe (RQ1) + 3-tier NLI verifier (RQ3) — z deterministic citation grounding (RQ2 Wallat 2025 faithfulness vs correctness).**

Domena: **prawa konsumenta** (UPK + KC + dyrektywy UE + orzecznictwo TSUE/SN + UOKiK). **Informational, NIE prawne doradztwo** — explicit disclaimer w UI Gradio.

### 3+1 pytania badawcze z thresholds

| RQ | Hipoteza | Próg defensible |
|---|---|---|
| **RQ1/H1** | hidden-states halu probe Bielik layer 47 | **AUROC ≥0.70, bootstrap CI lower ≥0.60** |
| **RQ2/H2** | citation grounding 2-metric (Wallat 2025) | H2a faithfulness ≥85% precision; H2b correctness ≥75% precision |
| **RQ3/H3** | 3-tier NLI verifier (mDeBERTa → HerBERT → judge LLM) | ≥85% citation precision |
| **RQ4/H4 supporting** | LLM-as-judge (Bielik / PLLuM / Gemma 3) | kappa ≥0.50 z manual labels (Landis-Koch substantial) |

**Każda hipoteza ma WPROST threshold.** Falsyfikowalne. Defense argument: jeśli próg nie przekroczony — opisać limitation w R7 + future work, NIE chować.

### Stan aktualny (2026-05-16 evening)

- **Polish CitationBench v0.6:** 11,000 unified chunks + 5,402 halu pairs (balanced 5/5 typów) w `main_project/data/processed/citationbench_v0.6_2026-05-16/`. Post-Wariant B cleanup z 17,862 → 11,000 (drop 38.4% off-topic per `chunk_filter.py --filter-policy strict`).
- **DEC-004 PARTIAL** (Iter. 0b POC): T1 mDeBERTa NLI sanity ✅ **PASS 80.6%** (lokal CPU). T2/T3/T4 czekają na lab GPU SP7 H200 (Magda SSH access pending).
- **DEC-005:** Eval set 200 par gold (60 UOKiK Q&A + 140 hand-annotated by autorka). Iter. 5 weekend hyperfocus.
- **48h-sprint mode** do 2026-05-18: writing-first R1-R8 + Tasks 09/10/11 (build-first-finalize-last explicit suspended dla calendar pressure).
- **Origin/main aktualne**, working tree clean post commit `3fa9de8`.

### Stack (krótko)

- **Generator + probe target:** Bielik 11B v3 (Mistral arch, 50 layers × 4096 hidden, layer 47 = ⌊0.95×50⌋, Apache 2.0).
- **Embedder:** BGE-M3 (frozen, multilingual).
- **Tier 1 NLI:** `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (✓ PASS 80.6%).
- **Tier 2 fallback:** HerBERT-large + CDSC-E custom (CC-BY-NC-SA-4.0 — NC clause check).
- **Tier 3 ablation:** Bielik / PLLuM / Gemma 3 27B / Claude Haiku LLM-judge.
- **Probe impl:** sklearn LogisticRegression linear primary; MLP nonlinear ablation; PyTorch hooks + HF `output_hidden_states=True` (NIE transformer-lens — brak 50L Mistral support). Reference: `obalcells/hallucination_probes`.
- **Storage:** PostgreSQL + Qdrant + Redis + DVC + MinIO.
- **MLOps:** Prefect 3 + MLflow + Optuna + Langfuse + Evidently + Alibi Detect + LGTM stack + Alertmanager.
- **RAG framework:** LlamaIndex + Outlines (structured output) + RAGAS (eval).
- **Serving:** SGLang (Bielik) + TEI (BGE-M3 + verifier) + FastAPI + Docker + GH Actions.
- **UI:** Gradio (3 zakładki: Chat / Inspect / Compare).
- **Python toolchain:** Python 3.13 + uv + ruff (format+lint) + pyrefly + pytest. **NIE pip/poetry/conda, NIE black.**

### Scope IN/OUT

**IN (4 komponenty central):**
1. Hidden-states halu probe + post-hoc citation grounding pipeline (NLI-based).
2. Polish consumer rights RAG demo (Bielik + Qdrant + LlamaIndex).
3. Continuous improvement loop probe (cykle retreningu z drift triggers).
4. Observability stack + 3 publishable artefakty na HuggingFace (dataset + probe + verifier) + Gradio 3-tab.

**OUT (NIE wracaj, NIE proponuj):**
- doradztwo prawne (informational only, explicit disclaimer)
- reranker fine-tuning (passé, DEC-003 supersession)
- farma domain (DEC-003 supersession)
- LLM full fine-tuning (probe NIE LoRA)
- real-time production deployment
- cross-language transfer
- reranker dla consumer rights
- prompt injection scenarios (v2, archived)
- psychiatria (v3, archived)
- ChPL/Ulotka (v3.1, archived)
- RQ5 (proponowane wcześniej, dropped w v3.2)

### 5-wymiarowa kontrybucja (defense scaffolding R8)

Każdy wymiar broni się **niezależnie**. Jeśli H1 odpada (probe AUROC <0.70 lub CI lower <0.60), kontrybucje 2-5 stoją. To jest twarda zasada projektowa — agent NIE może proponować coś co łamie tę niezależność.

1. **Metodologiczny** — pierwszy publicznie udokumentowany polish halu detection methodology
2. **Inżynierski** — reprodukowalny pipeline citation-grounded RAG + halu probe + verifier
3. **Artefaktowy** — 3 publishable na HuggingFace (dataset + probe model + verifier model)
4. **Eksperymentalny** — porównanie polish probe vs Lynx multilingual + HHEM + gliclass
5. **Korpusowy** — pierwszy polish CitationBench z deterministic citation grounding (ISAP-based)

**Standalone publishable:** dataset jako HF release nawet jeśli reszta H odrzucone.

### Phantom-citation watchlist (NIE używaj)

- `sdadas/polish-nli` — **NIE istnieje** na HF (confirmed 2026-05-16)
- `finecat-nli-l` — license UNSPECIFIED, NIE używać dla HF publication
- jakiekolwiek polish-NLI modele które nie zostały verified przez Magdę — zawsze flag „verify via citation-checker" przed użyciem

### Honest motivation framing (CRITICAL)

**Anti-overstating list — NIE pisz tego:**
- ❌ „LLM nie umie polish prawa"
- ❌ „brak prac w temacie"
- ❌ „polish-reranker nie zna farmaceutycznej terminologii" (overstated — DCI/ATC są międzynarodowe)
- ❌ „jedyna praca", „pierwsza", „jest się tym co"

**Defensible reformulations:**
- ✅ „polish-specific halu detection nie zostało publicznie udokumentowane (Mu-SHROOM 2025 pominął polski)"
- ✅ „production RAG dla legal domain wymaga citation grounding + halu control"
- ✅ „nie zna polish-specific patternów wokół niej (fleksja, szyk, regulatorowa frazeologia)"

**Polish-first first-mover RISK MEDIUM:**
- Wrocław Tech **AggTruth** — English-only, NIE bezpośrednia konkurencja
- **mGarbowski/llm-projekt** — direct prior art Bielik 1.5B → **MUST cite + differentiation** w R8

### Iteracje plan

| Iter. | Co | Status |
|---|---|---|
| 0b | POC 4 testy z kill criteria | T1 PASS, T2-T4 pending GPU |
| 1 | RAG MVP (Bielik + Qdrant + LlamaIndex + 3-tier NLI + Gradio) + probe training | pending |
| 2 | Continuous improvement loop (3 cykle retreningu z drift triggers) | pending |
| 3 | Observability stack (Langfuse + Evidently + Alibi Detect + LGTM + Alertmanager) | pending |
| 4 | Serving + CI/CD (SGLang + TEI + FastAPI + Docker + GH Actions) | pending |
| 5 | Manual gold 200 par (Magdy weekend) + 4-way verifier ablation | pending |
| 6 | 6-poziomowa error analysis + ablations A1-A4 + RAGAS faithfulness | pending |
| 7-8 | R1-R8 writing + PJATK formatting + citation pass | **48h-sprint override 2026-05-16: writing-first NOW** |

Total estimate post-POC PASS: 6-10 tygodni real engineering.

---

## CZĘŚĆ 3 — Jak briefować sub-agenty

### Single sources of truth (read order P0)

Każdy agent czyta w tej kolejności **zanim** zacznie robotę:

1. **`D:\diplomma\CLAUDE.md`** — root project state v3.2 (zawsze first w sesji)
2. **`thesis_research/02_konspekt_v3.2_skeleton.md`** — 12 sekcji konspekt aktualny
3. **`thesis_research/decisions/DEC-003_pivot-na-halu-detection.md`** — pivot rationale
4. **`thesis_research/decisions/DEC-004_iter0b_poc_results.md`** — POC sign-off framework
5. **`thesis_research/decisions/DEC-005_eval_set_200_par.md`** — eval set commitment
6. **`AGENT_BRIEF.md`** (ten plik) — destylacja wniosków

P1 (do work):
- `thesis_research/research/halu_detection_sota_2024_2026.md` — SOTA halu
- `thesis_research/research/nli_models_2026_update.md` — NLI alternatives
- `thesis_research/notes/sources_z_v3.1_do_reuse_w_v3.2.md` — bibliography mining
- `thesis_research/notes/KRYTYCZNA_ocena_scope_2026-05-16.md` — devil's advocate scope review
- `thesis_research/notes/scope_cleanup_decisions_2026-05-16.md` — per-source DROP/KEEP audit (Wariant B)

P3 (historical only, NIE używać do decyzji):
- `_archive/v3-pharma-reranker/` — v3.1 farma+reranker (archived)
- `_archive/v3.2-pre-clean/drafts/` — pre-Wariant B R3/R4/R5

### Wzorzec dobrego briefu dla sub-agenta

```
ROLA: [konkretna funkcja — scraper / draft writer / citation checker / krytyk]
CEL: [1 zdanie — co dostarczyć]
ZAKRES: [explicit IN — pliki / źródła / sekcje]
OUT-OF-SCOPE: [explicit NIE — żeby nie scope-creepował]
DONE CRITERION: [jak zweryfikujesz że gotowe]
CONSTRAINTS: [max LOC / max time / max suggestions]
READ FIRST: [3-5 plików z P0/P1 listy]
OUTPUT: [konkretny path + format — np. `thesis_research/notes/X.md` markdown]
```

**Krytyczne constraints dla critique agents:**
- „MAX 1 zmiana krytyczna. Jeśli nic poważnego = report OK."
- „NIE listuj 10 sugestii. Każde 'add X' wymaga 'remove Y' żeby utrzymać LOC."
- „Cytuj sprzeczności z CLAUDE.md / ADRs konkretnie (plik:linia)."

**Krytyczne constraints dla draft agents:**
- „Pisz czysty polski akademicki. ZERO codemix EN-PL. ZERO emoji."
- „Placeholdery `{{SCREAMING_SNAKE_CASE}}` dla wartości z Iter. 1-6."
- „Cytacje `[CYT: Author Year topic]` — verify post-pisanie, NIE z głowy."
- „Time-proofing: bez 'obecnie', 'rosnące', 'brak', 'jedyny'."

### Czego sub-agent NIE może zrobić bez explicit user sign-off

- Pivot tematu (4. rotacja = STOP)
- Zmienić threshold w hipotezie (AUROC, kappa, precision)
- Dodać nowy RQ
- Zmienić zakres eval set (200 par zatwierdzone DEC-005)
- Wrócić do OUT scope (reranker / farma / ChPL / RQ5 / cross-language)
- `git push` (zawsze prosić)
- `git commit --amend` / `git reset --hard` / `git push --force` (destructive ops)
- Modyfikować `.venv/`, `.git/`, `.idea/`
- Używać pip / poetry / conda / black
- Generować cytację z głowy bez „verify" tag

### Sprawdzenia przed odebraniem outputu od agenta

1. Czy nazwy plików / paths zgadzają się z faktem na dysku? (phantom infrastructure check)
2. Czy cytacje verifiable? (citation hygiene)
3. Czy NIE proponuje czegoś z OUT scope?
4. Czy NIE używa starzejących się sformułowań (time-proofing)?
5. Czy NIE overstate'uje motywacji?
6. Czy liczby zgadzają się cross-document? (container counts, %, dataset sizes)
7. Czy status markers ✓/🚧 są obecne dla components?
8. Czy R5/architektura nie ma drift (np. 11 vs 12 kontenerów, 37.5% vs 33.3%)?

---

## CZĘŚĆ 4 — Anti-patterns które już złapaliśmy w tej sesji

Lista konkretnych błędów które popełnili agenci (lub ja), żeby nie powtarzać:

1. **Phantom citation arXiv:2604.10799 jako „phantom"** — to NIE phantom, April 2026 jest past date (today 2026-05-16). Bielik v3 APT4 paper jest valid. **Zawsze checkuj date context przed claim phantom.**
2. **R3 mieszanie z R4/R6 scope** — Task 03 to czysta dokumentacja danych, NIE distributions / halu counts / mDeBERTa metryki. To są w R4/R6.
3. **R5 container drift** — text mówił 11, Fig 5.2 miał 12, Tab 5.1 miał 11. Cross-document sanity check obowiązkowy.
4. **R5 MLOps math** — 9 sekcji total, 3 MLOps = 33.3%, NIE 37.5% (które było z older 8-section version).
5. **R5 phantom infrastructure** — agent claimed `src/probe/`, `src/verifier/`, `src/citation/` istnieją; były puste. Status markers ✓/🚧 obowiązkowe.
6. **Bombastyczny styl** („piszesz jak na haju") — krótkie zdania, plain language, NIE figury retoryczne w drafcie tezy.
7. **Tab arithmetic mismatch** — Tab 3.1 declared 8,022 vs sum 7,622 (off-by-400). Sumy kolumn obowiązkowe.
8. **T1 mDeBERTa 6.1% FAIL → debug first** — bug w halu_injector (WSZYSTKIE positive labelled CONTRADICTED, factual_fabrication powinien być NEUTRAL). **Suspicious low results = bug w eval setup, NIE problem modelu.**
9. **Outsourced decisiveness** — multi-agent critique trigger scope creep. Stop spawning krytyk po pierwszej review. Default to addition trzeba aktywnie blokować.

---

## TL;DR (jeśli agent przeczyta tylko 10 linii)

1. **Inżynierka, NIE magisterka.** Promotor Kojałowicz, MLOps mindset.
2. **3 pivots za nią. 4. = STOP.** Aktualny temat: citation-grounded polski RAG + hidden-states halu probe + consumer rights (DEC-003).
3. **3+1 RQ z explicit thresholds.** RQ1 AUROC ≥0.70 (CI ≥0.60), RQ2 faith/corr ≥85%/75%, RQ3 NLI ≥85%, RQ4 kappa ≥0.50.
4. **Stack:** Bielik 11B v3 + BGE-M3 + mDeBERTa + HerBERT + LlamaIndex + Qdrant + Prefect/MLflow/Langfuse + Gradio. uv + ruff, NIE pip / black.
5. **OUT:** doradztwo prawne, reranker, farma, full fine-tuning, real-time, cross-language.
6. **Brutal feedback wymagany.** NIE validation, NIE „może warto rozważyć", NIE 10-item suggestion list. Binary choices.
7. **Citation hygiene = red flag.** Phantom = pracę zawalisz.
8. **Time-proofing.** Bez „obecnie", „brak", „jedyny", „rosnące".
9. **Decision before output.** Sign-off scope przed kodem/treścią.
10. **Defense scaffolding 5-wymiarowa — każdy wymiar broni się niezależnie.** Jeśli H1 odpada, 2-5 stoją.

Koniec. Idź pisz/scrap'uj/krytykuj. Wracaj z konkretem, nie z 10-item list.
