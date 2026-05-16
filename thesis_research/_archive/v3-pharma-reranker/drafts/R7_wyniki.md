# R7. Wyniki

> **Status:** outline + struktura sekcji 100% napisana; numbers + tabele wynikowe placeholders dla post-Iteracja 2-6 fill-in. Discussion templates 4-part (statement → interpretation → comparison vs hypothesis → implications) gotowe do wypełnienia liczbami z MLflow runs.
> **Autorka:** Magdalena Sochacka (s25508), PJATK
> **Wersja delty:** v3.1 (po DEC-001 + DEC-002, 2026-05-15)
> **Data outline:** 2026-05-16
> **Iteracja realizacji:** 8 (finalization). Pre-condition: Iteracje 2-6 ukończone, MLflow runs zarchiwizowane.

> **Konwencja placeholderów liczbowych:** każda komórka tabeli wynikowej z numerycznym placeholderem oznaczona jako `[Iter.N: X.XX ± Y.YY]`, gdzie `Iter.N` wskazuje iterację dostarczającą metrykę (per `02b_konspekt_v3_updates.md` § II.16). Inline w tekście używany jest marker `🟡 Numbers TBD post-Iter. N`.

> **Konwencja cytacyjna:** numeracja IEEE `[N]` referuje do bibliografii w sekcji 7.9 (placeholder na koniec rozdziału, finalizacja w Iteracji 8). Każde uncertainty w cytacji oznaczone jako `🟡 Verify via citation-checker`.

> **Konwencja statystyczna:** wszystkie metryki raportowane jako `mean ± std` z 3 random seeds (per `02b_konspekt_v3_updates.md` § II.4.5). Dodatkowy 95% CI (bootstrap, n=1000) tam, gdzie effect size jest borderline względem progu hipotezy. Effect size + std priority nad p-value cult (per `assignments/plans/zadanie_07_plan.md` § 9 risk register).

---

## 7.1 Setup eksperymentalny — recap

Niniejsza sekcja rekapituluje minimalny zestaw decyzji ewaluacyjnych konsolidujący ustalenia rozdziałów R3 (Dane), R4 (EDA), R5 (Architektura) i R6 (Modele). Pełna specyfikacja danych i splitów znajduje się w R3 oraz w pliku `sources_catalog.md`; tu odtworzono jedynie te fragmenty, które są niezbędne dla interpretacji wyników w sekcjach 7.2-7.8.

**Korpus.** Trening i ewaluacja prowadzone na korpusie ~4100 dokumentów farmakologii klinicznej, stratyfikowanym na sześć warstw (regulatory professional ChPL, regulatory consumer Ulotki, HTA + refundation legal AOTMiT/MZ, refundation operational NFZ, OA PL journals, adjacencies URPL DHPC + MZ braki list), per tabela w `02b_konspekt_v3_updates.md` § II.4.1. Stratyfikacja zachowuje over-representację klas ATC N05 (Psycholeptica) i N06 (Psychoanaleptica) do ~30% dla wzmocnienia sygnału psychiatrycznego w training, bez zmiany scope korpusu na "psychiatria".

**Splity.** Stosowany jest **document-level split** (NIE chunk-level), aby uniknąć leakage między train/dev/test przez wspólne fragmenty dokumentów. Proporcje: 70% train / 15% dev / 15% test. Dodatkowo zarezerwowane są dwa wydzielone zbiory ewaluacyjne, używane wyłącznie do final reporting (nie do hyperparameter tuning).

**Eval set podstawowy — 200 par psych gold standard.** Manualnie ranked by autorka, próbkowane z psychiatrycznej podgrupy ATC N05/N06. Każda para ma label binarny (relevant / non-relevant) plus dodatkowy poziom partial relevance (3-poziomowa skala: 0 = irrelevant, 1 = partial, 2 = fully relevant). Próba ta służy jako referencja dla:
- walidacji LLM-as-judge agreement (RQ2/H2 — Cohen's kappa, sekcja 7.3.3),
- raportowania nDCG@10 i MRR@10 dla baseline'ów oraz cykli retreningu (RQ1/H1 — sekcja 7.3.1),
- error analysis 6-poziomowej (sekcja 7.7).

Świadoma decyzja architektoniczna sample bias (eval wąski w psych, training szeroki w farma) udokumentowana w `02b_konspekt_v3_updates.md` § II.4.3 i `decisions/DEC-001_wybor-domeny.md` § Konsekwencje. Uzasadnienie: leverage manual validation kompetencji autorki dla rygorystycznej walidacji RQ2/H2 (najsłabiej zabezpieczona hipoteza w v3).

**Eval set RQ5 cross-register — 1800 par direction-stratified.** 900 par lay→pro (query z Ulotki, gold = ChPL sekcja tego samego leku) plus 900 par pro→lay (query z ChPL, gold = Ulotka). Programatycznie wygenerowane z 900 paired par leków, alignment deterministyczny przez `productID` z URPL RPL feed. Manual spot-check 50 par (5%) dla walidacji jakości alignment. Pełna specyfikacja per `decisions/DEC-002_chpl-ulotka-pairing.md` § Definicja eksperymentu RQ5.

**Random seeds.** Wszystkie eksperymenty wykonywane z 3 random seeds (`{42, 1337, 2026}`, locked w `02b_konspekt_v3_updates.md` § II.4.5). Raportowane metryki: `mean ± std`. Statistical significance testing (gdzie zadeklarowane) — paired t-test na seed-pairs vs baseline.

**Hardware + tracking.** Trening i inference na ZAiAI@LAB SP7 (NVIDIA H200 80GB). Wszystkie runs wytrackowane w MLflow z artefaktami (model weights via DVC, hyperparameters, training loss curves, eval metrics per epoch). Pełna konfiguracja hardware/MLflow — patrz R5.7 i R6.5.

**Hipotezy do walidacji (recap).** Pięć RQ z falsyfikowalnymi progami per `02b_konspekt_v3_updates.md` § II.3.3:

| RQ | Hipoteza | Próg | Sekcja walidacji |
|----|----------|------|-------------------|
| RQ1/H1 | Retrening rerankera poprawia retrieval quality | ≥10pp nDCG@10 vs base polish-reranker | 7.3.1 |
| RQ2/H2 | LLM-judge agreement z manual jest wystarczające | Cohen's kappa ≥0.50 (acceptable: ≥0.40) | 7.3.3 |
| RQ3/H3 | Plateau po cyklu 2 | Cykl 3 ≤2pp poprawy vs cykl 2, p>0.05 | 7.4 |
| RQ4/H4 | Drift detector skuteczny na simulated OOD | Precision ≥0.80, recall ≥0.70 | 7.6 |
| RQ5/H5 | Cross-register retrieval z paired ChPL↔Ulotka działa | accuracy@10 ≥70%, gap ≤5pp same-vs-cross | 7.5 |

Tabela 7.1 (powyżej) pełni funkcję mapy nawigacyjnej dla rozdziału — każda sekcja odpowiada na jedną hipotezę z explicit progiem.

---

## 7.2 Baselines (pre-Iteracja 2 cykl 1)

Niniejsza sekcja prezentuje wyniki trzech baseline'ów retrievalu mierzone na 200-parowym eval set psych przed pierwszym cyklem retreningu rerankera. Baselines stanowią **lower bound** dla późniejszej oceny kontrybucji fine-tuningu (RQ1/H1) — pokazują "podłogę" jakości dostępnej out-of-the-box dla polskiej domeny farmaceutycznej bez domain adaptation.

**Baseline 1: BM25 (Pyserini).** Sparse lexical retrieval, baseline klasyczny dla benchmarków IR od dekad. Implementacja: Pyserini 0.22 z analyzerem polskim (Morfologik stemmer). Bez query expansion, bez RM3. Cel: pokazać sygnał z czysto leksykalnego matchingu w polskim regulatory text.

**Baseline 2: Dense BGE-M3 (frozen embedder).** Multilingual dense retrieval bez rerankera. BGE-M3 w trybie dense-only (bez sparse / colbert vectors), top-k via cosine similarity w Qdrant HNSW index. Cel: pokazać kontrybucję samego embedder'a (frozen, bez fine-tuning) — czy multilingual model out-of-the-box rozumie polską terminologię farmaceutyczną.

**Baseline 3: Base polish-reranker-roberta-v3 (no fine-tuning).** BGE-M3 retrieve top-50, rerank przez `sdadas/polish-reranker-roberta-v3` w wersji HuggingFace bez domain adaptation. Cel: punkt odniesienia dla H1 — to jest dokładnie ta wartość, którą cykl 1 retreningu ma poprawić o ≥10pp nDCG@10.

**Tabela 7.2.** Baseline retrieval metrics na 200-parowym eval set psych. Mean ± std z 3 random seeds.

| Method | nDCG@10 | MRR@10 | accuracy@10 | recall@10 |
|--------|---------|--------|-------------|-----------|
| BM25 (Pyserini) | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` |
| Dense BGE-M3 | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` |
| Base polish-reranker-roberta-v3 | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` |

🟡 Numbers TBD post-Iter. 2.

**Figura 7.2.1** *(placeholder)*. Bar chart per metric × method z error bars (95% CI bootstrap n=1000). Konwencja kolorystyczna: BM25 — szary, Dense — niebieski, Base reranker — zielony. Pozioma linia referencyjna dla H1 progu (base + 10pp nDCG@10).

### Discussion (4-part template)

**Statement.** Wyniki Tabeli 7.2 pokazują, że na 200-parowym eval set psych bazowe metryki retrievalu mieszczą się w przedziale `🟡 Numbers TBD post-Iter. 2`, z BM25 osiągającym `🟡 [BM25_nDCG]`, BGE-M3 dense `🟡 [Dense_nDCG]` oraz base polish-reranker `🟡 [BaseReranker_nDCG]`.

**Interpretation.** Mechanistycznie, gradient od BM25 do Dense → Reranker odzwierciedla trzy poziomy abstrakcji semantycznej: (1) BM25 polega wyłącznie na surface-level lexical overlap z polskim stemmingiem Morfologik, co działa dobrze tylko dla query bezpośrednio cytujących terminy z passage; (2) Dense BGE-M3 dodaje multilingual embedding distance, co adresuje paraphrase ale nadal cierpi na ogólność modelu (trenowanego na multilingual web text, nie na polskim regulatory); (3) Base reranker dodaje warstwę cross-encoder attention, ale bez domain adaptation — czyli mierzymy wartość architecture'y, nie domain expertise. Spread między tymi trzema baseline'ami wskazuje na *potential ceiling* dla domain adaptation — im większy spread, tym więcej miejsca na kontrybucję rerankera.

**Comparison vs hypothesis.** Próg H1 (`02b_konspekt_v3_updates.md` § II.3.3): retrening rerankera musi dodać **≥10pp nDCG@10** do wartości base reranker. Czyli target w cyklu 1 to `🟡 [BaseReranker_nDCG] + 0.10`. Sekcja 7.3.1 weryfikuje, czy ten próg został osiągnięty.

**Implications.** Te baselines determinują dwie decyzje dalsze: (1) czy rerankering ma sens (jeśli BM25 ≈ Dense ≈ Base reranker, to architektura cross-encoder nie wnosi nic — sygnał alarmowy dla całego pipeline'u); (2) czy 10pp jest realistycznym progiem (jeśli base reranker daje już 0.85 nDCG@10, ceiling effect uniemożliwia +0.10; jeśli daje 0.40, headroom jest duży). Interpretacja konkretnych wyników po fill-in liczbach z Iteracji 2.

---

## 7.3 Cykl 1 results

Niniejsza sekcja prezentuje wyniki pierwszego cyklu retreningu rerankera oraz towarzyszących mu ablacji A1-A4 (Defense scaffolding pkt 1) i walidacji LLM-as-judge (RQ2/H2). Wszystkie metryki z Iteracji 2 (per `02b_konspekt_v3_updates.md` § II.16).

### 7.3.1 Reranker improvement (RQ1/H1)

Cykl 1 retreningu prowadzony per protokół R6.3 (Reranker fine-tuning): preference learning na ~50k quadrupletów per cykl (1 positive + 3 hard negatives wg 4-poziomowej strategii II.4.6; cumulative ~145k po 3 cyklach), 3 epoki, batch size 16, learning rate 2e-5 (Optuna search w przedziale [1e-5, 1e-4]), weight decay 0.01, warmup 500 kroków. Wszystkie hyperparameters tracked w MLflow.

**Tabela 7.3.1.** Cykl 1 reranker fine-tuning vs base. Eval set: 200 par psych gold standard. Mean ± std z 3 random seeds.

| Method | nDCG@10 | MRR@10 | accuracy@10 | recall@10 | Δ vs Base (nDCG) |
|--------|---------|--------|-------------|-----------|------------------|
| Base polish-reranker-roberta-v3 | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | — |
| **Cykl 1 (full pipeline)** | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: +X.YYpp]` |

🟡 Numbers TBD post-Iter. 2.

**Figura 7.3.1** *(placeholder)*. Training loss curve cyklu 1 (z MLflow), x-axis: training step, y-axis: contrastive loss, 3 linie per random seed plus średnia. Pomocnicze: validation nDCG@10 per epoch jako overlay drugiej osi y.

**Figura 7.3.2** *(placeholder)*. Per-query Δ nDCG@10 (cykl 1 vs base), histogram dla 200 par eval set. Pokazuje rozkład per-query improvement — nie tylko mean. Highlight queries z Δ < 0 (regresje).

#### Discussion (4-part template)

**Statement.** Tabela 7.3.1 pokazuje, że cykl 1 retreningu rerankera zmienia nDCG@10 z `🟡 [BaseReranker_nDCG]` na `🟡 [Cykl1_nDCG]`, co daje Δ = `🟡 [+/- X.YYpp]` względem baseline.

**Interpretation.** Mechanistycznie poprawa (lub jej brak) pochodzi z trzech komponentów cyklu 1: (1) **domain exposure** — model widzi polskie regulatory text, terminologię ATC, łacińskie nazwy substancji czynnych, struktury sekcji ChPL, których nie miał w pre-training; (2) **preference signal quality** — model uczy się rozróżniać semantically relevant od near-miss passages (poziomy L2/L3 hard negatives); (3) **architectural fit** — cross-encoder z fresh weights w głowie klasyfikacyjnej, dostraja attention pattern do polskiej składni. Dekompozycja względnych kontrybucji tych trzech źródeł jest celem ablacji A1-A4 (sekcja 7.3.2).

**Comparison vs hypothesis.** Próg H1 (`02b_konspekt_v3_updates.md` § II.3.3): **≥10pp nDCG@10 vs base polish-reranker**. Wynik `🟡 [+X.YYpp]` względem `🟡 [+10pp]` progu — H1 status: `🟡 [PASSED / PARTIAL / FAILED]`. W przypadku FAILED (Δ < +10pp), interpretacja w sekcji 7.8 (Synteza) przesuwa wagę kontrybucji pracy na pozostałe RQ (defense scaffolding pkt 3 — 5-wymiarowa kontrybucja niezależna).

**Implications.** Wynik cyklu 1 determinuje sensowność uruchomienia cyklu 2 i 3 (sekcja 7.4). Jeśli cykl 1 daje `🟡 [+X.YYpp]`, oczekiwany cykl 2 daje marginalnie mniej (per H3 — plateau hypothesis), cykl 3 jeszcze mniej. W przypadku wyniku poniżej 5pp, cykl 2 pozostaje wykonany (per protokół), ale prior na sukces H1 obniżony — odpowiednie framing w sekcji 7.8.

### 7.3.2 Ablations A1-A4 results

Cztery ablacje (Defense scaffolding pkt 1, `thesis_elements/CLAUDE.md`) służą diagnostyce źródła poprawy retrieval quality w cyklu 1. Każda ablacja to osobny MLflow run z modyfikacją jednego komponentu pipeline'u; pozostałe komponenty bez zmian.

**A1: judge → random preference labels.** Zamiast LLM-judge (PLLuM/`<judge_model>` decyzja w Iter. 2), preference labels generowane losowo (50/50 między passage A vs B). Cel diagnostyczny: czy improvement wynika z signal quality (dobrego judge'a) czy z **domain exposure** (samego faktu trenowania na polskim regulatory). Jeśli random pairs daje podobny gain — judge nic nie wnosi, kontrybucja pochodzi z corpus exposure.

**A2: judge → Bielik 11B v3** (jeśli w Iter. 0b winner ≠ Bielik). Cross-model robustness check. Czy konkluzje H2 trzymają się dla innego polskiego LLM-a? Jeśli A2 daje znacząco różny wynik niż A0 (default judge), to wskazuje że LLM-judge framework nie jest model-agnostic — kontrybucja związana ze specyfiką konkretnego modelu, nie z metodą.

**A3: corpus → psych-only.** Trening na ATC N05-N06 only (psych subset, ~30% korpusu zamiast 100%). Cel: domain breadth effect. Czy szeroki pharma corpus pomaga, czy psych-only już wystarcza dla psych eval set? Jeśli A3 ≈ A0 (full corpus) na psych eval, to scope rozszerzenia korpusu nie ma uzasadnienia w metrykach (ale może mieć w cross-register / generalizacja — A4).

**A4: ChPL-only training (bez Ulotek).** Cel: effect of register diversity (powiązane z RQ5). Jeśli A4 ≈ A0 na same-register eval ale dramatycznie gorsze na cross-register eval (sekcja 7.5), to potwierdza wartość Ulotek w training mimo że eval set podstawowy ich nie testuje bezpośrednio.

**Tabela 7.3.2.** Wyniki ablacji A1-A4 vs A0 (full pipeline cyklu 1). Eval set: 200 par psych gold standard. Mean ± std z 3 random seeds. Δ podane vs A0.

| Ablation | Wariant | nDCG@10 | MRR@10 | Δ nDCG vs A0 | Diagnostic conclusion |
|----------|---------|---------|--------|---------------|------------------------|
| **A0** | Full pipeline (default judge + full corpus + ChPL+Ulotka) | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | — (reference) | reference |
| **A1** | Random preference labels (zamiast judge) | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: -X.YYpp]` | judge contribution = `🟡 [domain vs signal split]` |
| **A2** | Bielik judge zamiast `<judge_model>` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: ±X.YYpp]` | cross-model robustness = `🟡 [robust / fragile]` |
| **A3** | Psych-only training corpus (~30%) | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: ±X.YYpp]` | corpus breadth value = `🟡 [needed / redundant]` |
| **A4** | ChPL-only training (bez Ulotek) | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: ±X.YYpp]` | register diversity value = `🟡 [needed / redundant na same-register]` |

🟡 Numbers TBD post-Iter. 2.

#### Discussion per ablacji (4-part template)

##### Ablation A1 (random vs judge)

**Statement.** A1 z losowymi preference labels daje nDCG@10 = `🟡 [A1_nDCG]`, co stanowi Δ = `🟡 [-X.YYpp]` względem A0 (judge-driven labels).

**Interpretation.** Jeśli Δ jest blisko zera (np. -1pp do -2pp), znaczy że judge **nie wnosi sygnału** — improvement w cyklu 1 pochodzi z samego faktu trenowania na polskim regulatory text, niezależnie od jakości labelek. Jeśli Δ jest duże (np. -5pp do -10pp), judge dostarcza znaczącej informacji semantycznej której random nie ma — to walidacja wartości RQ2/H2 framework.

**Comparison vs hypothesis.** A1 nie ma własnego progu hipotezy, ale **mid-range Δ ~3-5pp** to mocny sygnał diagnostyczny: obie składowe (corpus exposure + judge signal) wnoszą wartość, żadna nie dominuje samodzielnie. Pełna interpretacja w kontekście A0 + H1 + H2 razem.

**Implications.** Jeśli A1 ≈ A0 → judge framework do reformulation w R8 jako **soft contribution** (nie kluczowa); jeśli A1 << A0 → judge framework jako **central methodological contribution** (defense scaffolding pkt 3, wymiar 1).

##### Ablation A2 (Bielik vs `<judge_model>`)

**Statement.** A2 z Bielik 11B v3 jako judge daje nDCG@10 = `🟡 [A2_nDCG]`, Δ względem A0 = `🟡 [±X.YYpp]`.

**Interpretation.** Mała różnica (|Δ| < 1pp) sygnalizuje cross-model robustness — framework LLM-judge nie jest fragile na wybór konkretnego polskiego LLM-a. Duża różnica (|Δ| > 3pp) sygnalizuje, że konkretny model decyduje o jakości — co jest słabością framework'u.

**Comparison vs hypothesis.** Powiązane z H2 (kappa ≥0.50). Jeśli A2 i A0 dają podobne kappa (sekcja 7.3.3, oba mierzone), to robustness potwierdzona. Jeśli kappa Bielik < kappa default judge, to default judge ma legitimate edge.

**Implications.** Robustness wynik wzmacnia external validity pracy — promotor i komisja mogą argumentować, że framework działa nie tylko dla jednego modelu. W przypadku fragility, R8 future work musi wskazać multi-model ensemble jako mitigation.

##### Ablation A3 (psych-only vs full corpus)

**Statement.** A3 z trenowaniem na samym psych subset (~30% korpusu) daje nDCG@10 = `🟡 [A3_nDCG]`, Δ względem A0 = `🟡 [±X.YYpp]`.

**Interpretation.** Eval set podstawowy jest psych — naturalnie A3 może być **bliskie A0** (in-distribution training and eval). Mała różnica oznacza, że scope rozszerzenia korpusu na pełną farmakologię nie pomaga w psych eval (i.e., większy corpus nie szkodzi, ale też nie pomaga w wąskim teście). Duża różnica (A0 >> A3) oznacza, że pełna farmakologia dostarcza generalization benefit nawet dla wąskiej psych eval.

**Comparison vs hypothesis.** A3 nie ma własnego progu, ale **uzasadnia decyzję DEC-001** (rotacja na farmakologię szeroką). Jeśli A3 << A0, to DEC-001 jest empirycznie validated. Jeśli A3 ≈ A0, to DEC-001 ma uzasadnienie metodologiczne (cross-register, scope) ale nie metryczne na psych eval — co jest do powiedzenia explicite w sekcji 7.8.

**Implications.** Wynik A3 informuje przyszłe decyzje o sample efficiency: czy warto inwestować w szerszy corpus jeśli eval pozostaje wąski? Defense answer: **eval szeroki nadejdzie z RQ5 cross-register** — A3 + RQ5 razem dają pełen obraz korpusowej kontrybucji.

##### Ablation A4 (ChPL-only vs ChPL+Ulotka)

**Statement.** A4 z trenowaniem tylko na ChPL (bez Ulotek) daje nDCG@10 = `🟡 [A4_nDCG]` na same-register eval (200 par psych), Δ względem A0 = `🟡 [±X.YYpp]`.

**Interpretation.** Same-register eval set (psych gold standard, ChPL passages dominują) **nie penalizuje** brak Ulotek w training — co znaczy że A4 może być ≈ A0 lub nawet marginalnie lepsze. Kluczowa diagnostyka A4 jest jednak w sekcji 7.5 — porównanie A4 vs A0 na cross-register eval set (1800 par). Tam oczekiwany jest dramatyczny gap (A4 << A0), co potwierdzi wartość Ulotek dla RQ5.

**Comparison vs hypothesis.** Próg dla H5 jest cross-register (sekcja 7.5), nie same-register. Tu A4 służy jako **negative control** — jeśli A4 << A0 nawet na same-register, to coś jest źle (Ulotki powinny być neutralne dla psych eval set). Jeśli A4 ≈ A0 lub A4 > A0 minimally, sanity check passed.

**Implications.** Wynik A4 same-register w połączeniu z A4 cross-register (sekcja 7.5) tworzy 2x2 matrix decyzji (Tabela 7.5.3) — kluczowy diagnostic dla wartości Ulotek w training. Defense argument: bez A4 nie można twierdzić, że pairing daje wartość, można tylko twierdzić że ChPL+Ulotka daje wartość.

### 7.3.3 LLM-as-judge validation (RQ2/H2)

LLM-as-judge framework jest centralnym komponentem pipeline'u — bez wystarczającej jakości signal'u judge'a, preference learning rerankera trenowane na noisy labelach. Walidacja H2 prowadzona w **dwóch etapach** zgodnie z `02b_konspekt_v3_updates.md` § II.7 (multi-stage validation):

**Stage 1 (Iteracja 0b — pilot).** N=30 par cross-register pair scoring × 4 candidate judges {Bielik 11B v3 / Gemma 3 27B / Qwen 3 32B / Claude Haiku 4.5}. Cohen's kappa względem 30 manual labels by autorka. Cel: top-2 shortlist (NIE final winner), bo n=30 jest statystycznie thin (expected CI ±0.15-0.20 dla 4-way comparison).

**Stage 2 (Iteracja 2 — final).** Head-to-head top-2 z Stage 1 vs N=200 manual labels (psych gold standard). Cel: single judge winner z stabilną kappa CI ±0.05-0.08 dla defensible decision.

**Tabela 7.3.3.A.** Stage 1 (Iter. 0b pilot) — Cohen's kappa per judge × protocol. N=30 par per komórka.

| Judge candidate | Pairwise (κ) | Pointwise (κ) | Faithfulness (κ) | Cross-register (κ) | Mean κ | CI 95% |
|-----------------|--------------|---------------|--------------------|---------------------|---------|--------|
| Bielik 11B v3 | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[±0.15-0.20]` |
| Gemma 3 27B | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[±0.15-0.20]` |
| Qwen 3 32B | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[±0.15-0.20]` |
| Claude Haiku 4.5 | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[Iter.0b: 0.XX]` | `[±0.15-0.20]` |

🟡 Numbers TBD post-Iter. 0b. **Top-2 shortlist:** `🟡 [Judge_X, Judge_Y]`.

**Tabela 7.3.3.B.** Stage 2 (Iter. 2 final) — Cohen's kappa head-to-head top-2 vs N=200 manual labels (psych gold standard).

| Judge (top-2 z Stage 1) | Pairwise (κ) | Pointwise (κ) | Faithfulness (κ) | Cross-register (κ) | Mean κ | CI 95% | Agreement % |
|--------------------------|--------------|---------------|--------------------|---------------------|---------|--------|--------------|
| `🟡 [Judge_X]` | `[Iter.2: 0.XX]` | `[Iter.2: 0.XX]` | `[Iter.2: 0.XX]` | `[Iter.2: 0.XX]` | `[Iter.2: 0.XX]` | `[±0.05-0.08]` | `[Iter.2: XX%]` |
| `🟡 [Judge_Y]` | `[Iter.2: 0.XX]` | `[Iter.2: 0.XX]` | `[Iter.2: 0.XX]` | `[Iter.2: 0.XX]` | `[Iter.2: 0.XX]` | `[±0.05-0.08]` | `[Iter.2: XX%]` |

🟡 Numbers TBD post-Iter. 2. **Final winner:** `🟡 [<judge_model>]`.

**Figura 7.3.3** *(placeholder)*. Confusion matrix: judge predictions (3-class: A preferred / B preferred / tie) vs manual labels by autorka. Heatmap z procentami. Highlight off-diagonal (errors) z categorization (semantic miss vs register confusion).

#### Discussion (4-part template)

**Statement.** Tabela 7.3.3.B pokazuje, że final judge winner `🟡 [<judge_model>]` osiąga mean Cohen's kappa = `🟡 [0.XX]` na 200-parowym eval set psych, z agreement % = `🟡 [XX%]`.

**Interpretation.** Cohen's kappa skala interpretacji per Landis & Koch (1977) [5]: 0.00-0.20 = slight, 0.21-0.40 = fair, 0.41-0.60 = moderate, 0.61-0.80 = substantial, 0.81-1.00 = almost perfect. Próg H2 (≥0.50) lokuje target w **moderate** zakresie, czyli 50-60% chance-corrected agreement. Mechanistycznie kappa ≥0.50 oznacza, że judge robi systemic decisions zgodne z autorką (nie randomnie), ale z notable noise — wystarczająco dla preference learning (gdzie noise jest mitigated przez aggregation tysięcy par), niewystarczająco dla samodzielnego decision making.

**Comparison vs hypothesis.** Próg H2 (`02b_konspekt_v3_updates.md` § II.3.3): Cohen's kappa ≥0.50 (acceptable: ≥0.40). Wynik `🟡 [0.XX]` względem `🟡 [0.50]` progu — H2 status: `🟡 [PASSED / PARTIAL / FAILED]`. Comparative reference: Karp 2025 [6] dla polskiego legal LLM-judge raportuje kappa `🟡 Verify exact value via citation-checker` w podobnym setupie.

**Implications.** Wynik H2 ma reciprocal effect na H1 — jeśli kappa < 0.40, to preference labels dla cyklu 1-3 są szumem i H1 negative result jest **mechanicznie wytłumaczalny** (nie defekt rerankera architecture, ale defekt sygnału treningowego). Jeśli kappa ≥0.50, to H1 result jest **disentangled** od judge quality. Sekcja 7.8 (Synteza) explicite mapuje zależność H1 ↔ H2.

---

## 7.4 Cykle 2 + 3 results

Sekcja prezentuje wyniki dwóch dodatkowych cykli retreningu (Iteracja 3 per `02b_konspekt_v3_updates.md` § II.16) w celu walidacji RQ3/H3 — hipoteza plateau po cyklu 2. Każdy cykl używa **fresh synthetic queries** (nowa próba ~50k preference quadrupletów per cykl, cumulative ~145k po 3 cyklach, wygenerowana przez Bielik few-shot z innym seedem) oraz **fresh judge labels** (re-running `<judge_model>` na świeżej próbie). Reranker startuje z weights z poprzedniego cyklu (continual fine-tuning, nie restart from base).

**Tabela 7.4.1.** Cykle 1, 2, 3 retreningu. Mean ± std z 3 random seeds. Δ podane między successive cyklami.

| Cykl | nDCG@10 | MRR@10 | accuracy@10 | recall@10 | Δ nDCG vs prev | p-value (paired t-test, seed-pairs) |
|------|---------|--------|-------------|-----------|-----------------|--------------------------------------|
| Base (no retrain) | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | — | — |
| Cykl 1 | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: 0.XXX ± 0.YYY]` | `[Iter.2: +X.YYpp]` | `[Iter.2: 0.XXX]` |
| Cykl 2 | `[Iter.3: 0.XXX ± 0.YYY]` | `[Iter.3: 0.XXX ± 0.YYY]` | `[Iter.3: 0.XXX ± 0.YYY]` | `[Iter.3: 0.XXX ± 0.YYY]` | `[Iter.3: +X.YYpp]` | `[Iter.3: 0.XXX]` |
| Cykl 3 | `[Iter.3: 0.XXX ± 0.YYY]` | `[Iter.3: 0.XXX ± 0.YYY]` | `[Iter.3: 0.XXX ± 0.YYY]` | `[Iter.3: 0.XXX ± 0.YYY]` | `[Iter.3: +X.YYpp]` | `[Iter.3: 0.XXX]` |

🟡 Numbers TBD post-Iter. 2 (cykl 1) i Iter. 3 (cykle 2-3).

**Figura 7.4.1** *(placeholder)*. Marginal gain per cycle line chart. X-axis: cycle (Base, 1, 2, 3). Y-axis: nDCG@10 z 95% CI bootstrap. Druga oś y: marginal Δ vs poprzedni cykl (bar chart). Pozioma linia referencyjna dla H3 progu (≤2pp marginal gain dla cyklu 3).

**Figura 7.4.2** *(placeholder)*. Per-query analysis cykle 2 i 3 — dla każdej z 200 par, czy cykl 3 pokazuje improvement, regresję czy stability vs cykl 2. Stacked bar chart procent par per kategoria (improvement >2pp / improvement 0-2pp / no change / regresja 0-2pp / regresja >2pp).

### Discussion (4-part template)

**Statement.** Tabela 7.4.1 pokazuje trajektorię nDCG@10 przez 3 cykle: cykl 1 daje `🟡 [+X.YYpp]`, cykl 2 dodaje `🟡 [+X.YYpp]` względem cyklu 1, cykl 3 dodaje `🟡 [+X.YYpp]` względem cyklu 2. Statistical significance cyklu 3 vs cykl 2: p = `🟡 [0.XXX]`.

**Interpretation.** Plateau w continual fine-tuning może mieć trzy mechanistyczne przyczyny: (1) **judge label saturation** — judge generuje preference labels z intrinsic noise (kappa < 1.0), więc reranker uczy się do wysokości tego noise floor i dalsze cykle nie dostarczają nowej informacji; (2) **model capacity limit** — polish-reranker-roberta-v3 (~360M params) ma ograniczoną pojemność uczenia się fine-grained semantic distinctions; (3) **data redundancy** — fresh synthetic queries cyklu 2/3 nie dostarczają qualitatively nowych przykładów (Bielik generator ma ograniczoną diversity), więc plateau jest funkcją corpus, nie modelu. Diagnostic dla każdej z tych trzech przyczyn wymaga osobnych eksperymentów (nie objęte w niniejszej pracy, future work R8).

**Comparison vs hypothesis.** Próg H3 (`02b_konspekt_v3_updates.md` § II.3.3): cykl 3 ≤2pp poprawy vs cykl 2, p>0.05. Wynik `🟡 [+X.YYpp, p=0.XXX]` względem progów — H3 status: `🟡 [PASSED / FAILED]`. PASSED oznacza, że plateau zaobserwowany — co jest **pozytywnym** wynikiem dla hipotezy (wskazuje że więcej cykli to waste of compute). FAILED (Δ > 2pp lub p < 0.05) oznacza, że marginal gains nadal są significant — co paradoksalnie sygnalizuje, że pipeline mógłby dać więcej przy 4. cyklu, ale autorka nie eksploruje tego w scope (future work).

**Implications.** PASSED status H3 ma directly defensive value: praca raportuje **systemic finding** o saturacji preference learning po 2 cyklach, co jest publishable jako methodological contribution niezależnie od H1 wyniku. FAILED status H3 wymaga reframing — albo "ten typ retreningu nie wykazuje saturacji w obserwowanym zakresie" (defensible), albo "future work powinien testować 4-5 cykli" (defensible jako limitation explicit).

---

## 7.5 Cross-register results (RQ5/H5)

Sekcja prezentuje wyniki eksperymentu cross-register retrieval na 1800-parowym eval set RQ5 (900 lay→pro + 900 pro→lay), zgodnie ze setupem zdefiniowanym w `decisions/DEC-002_chpl-ulotka-pairing.md` § Definicja eksperymentu RQ5. Iteracja realizacji: 4 (per `02b_konspekt_v3_updates.md` § II.16).

**Direction-stratified reporting** (per DEC-002 cleanup decision): metryki MRR@10 i accuracy@10 raportowane **osobno per direction** (lay→pro vs pro→lay), bo cross-register może być asymmetric — lay queries zwykle krótsze, mniej technical; pro queries dłuższe, bogatsze terminologicznie → różny ranking difficulty. Aggregate (mean obu directions) podany jako single-number reporting, ale **kluczowe są direction-stratified values**.

**Tabela 7.5.1.** RQ5 cross-register retrieval — direction-stratified MRR@10 i accuracy@10. Eval set: 1800 par (900 per direction). Mean ± std z 3 random seeds.

| Method | accuracy@10 lay→pro | accuracy@10 pro→lay | MRR@10 lay→pro | MRR@10 pro→lay | accuracy@10 aggregate | MRR@10 aggregate |
|--------|----------------------|----------------------|------------------|-----------------|------------------------|--------------------|
| Base polish-reranker (no fine-tune) | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` |
| **Cykl 1 full (A0, ChPL+Ulotka)** | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` |
| Cykl 1 A4 (ChPL-only training) | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` | `[Iter.4: 0.XXX ± 0.YYY]` |

🟡 Numbers TBD post-Iter. 4.

**Tabela 7.5.2.** Direction asymmetry gap `Δ_dir = | MRR(lay→pro) − MRR(pro→lay) |` per training variant.

| Method | Δ_dir (MRR@10) | Comment |
|--------|-----------------|---------|
| Base polish-reranker | `[Iter.4: 0.XXX]` | reference asymmetry pre-finetune |
| Cykl 1 A0 (ChPL+Ulotka) | `[Iter.4: 0.XXX]` | post-finetune asymmetry |
| Cykl 1 A4 (ChPL-only) | `[Iter.4: 0.XXX]` | counterfactual: bez Ulotek |

🟡 Numbers TBD post-Iter. 4.

**Tabela 7.5.3.** Same-register vs cross-register gap. Same-register baseline: 200 par psych gold standard (Tabela 7.3.1). Cross-register: aggregate z Tabeli 7.5.1.

| Method | nDCG@10 same-register (psych gold) | accuracy@10 same-register | accuracy@10 cross-register (aggregate) | Gap (same − cross, pp) |
|--------|--------------------------------------|----------------------------|------------------------------------------|--------------------------|
| Cykl 1 A0 (ChPL+Ulotka) | `[Iter.2: 0.XXX]` | `[Iter.2: 0.XXX]` | `[Iter.4: 0.XXX]` | `[Iter.4: ±X.YYpp]` |
| Cykl 1 A4 (ChPL-only) | `[Iter.2: 0.XXX]` | `[Iter.2: 0.XXX]` | `[Iter.4: 0.XXX]` | `[Iter.4: ±X.YYpp]` |

🟡 Numbers TBD post-Iter. 2 (same-register) i Iter. 4 (cross-register).

**Figura 7.5.1** *(placeholder)*. Per-direction performance comparison. Grouped bar chart: x-axis = method (Base, A0, A4), y-axis = MRR@10, dwa słupki per method (lay→pro, pro→lay) z 95% CI bootstrap. Pozioma linia dla H5 progu accuracy@10 ≥0.70 i gap ≤5pp.

**Figura 7.5.2** *(placeholder)*. Example cross-register query-passage pairs — kontrast pozytywnego (correctly retrieved) i negatywnego (mis-ranked) dla ilustracji. 4 examples: 2 lay→pro (positive + negative) + 2 pro→lay (positive + negative). Z highlightem terminology mismatch lub register cue.

### Discussion (4-part template)

**Statement.** Tabela 7.5.1 pokazuje, że cykl 1 A0 (ChPL+Ulotka training) osiąga accuracy@10 = `🟡 [X.XX]` lay→pro i `🟡 [X.XX]` pro→lay (aggregate `🟡 [X.XX]`). Direction asymmetry gap Δ_dir = `🟡 [0.XXX]` (Tabela 7.5.2). Same-register vs cross-register gap = `🟡 [±X.YYpp]` (Tabela 7.5.3). Ablation A4 (ChPL-only) daje aggregate accuracy@10 = `🟡 [X.XX]`, czyli `🟡 [±X.YYpp]` mniej niż A0.

**Interpretation.** Direction asymmetry (jeśli Δ_dir > 0.05) wskazuje, że jedna kierunkowość jest systematycznie trudniejsza dla rerankera. **Lay→pro** trudniejsze typowo dlatego, że layperson queries są krótkie, eliptyczne, bogate w odwołania anaforyczne ("co zrobić jak zapomniałem dawki" — "co" jest underspecified, zwykle implikuje "działanie korygujące", ale model bez kontekstu może retrieved passage o objawach pominięcia). **Pro→lay** trudniejsze typowo dlatego, że professional queries cytują łacińskie nazwy substancji + kody ATC, a Ulotki używają polskiej terminologii potocznej + brand names — luka leksykalna jest wyższa niż w drugą stronę. Empiryczna kierunkowa difficulty diagnostic w error analysis (sekcja 7.7, kategoria "register mismatch"). A4 vs A0 gap > 5pp na cross-register byłaby bezpośrednią walidacją wartości Ulotek w training (per logika DEC-002): bez Ulotek model nie widzi paraphrastycznego mappingu między rejestrami, więc cross-register retrieval cierpi.

**Comparison vs hypothesis.** Próg H5 (`02b_konspekt_v3_updates.md` § II.3.3): (a) accuracy@10 ≥70% (aggregate), (b) gap same-vs-cross ≤5pp. Falsyfikowalność (DEC-002): hipoteza odrzucona jeśli (i) accuracy@10 < 60%, (ii) gap > 15pp, (iii) trening na pairs degraduje base-line same-register o > 2pp.

| Kryterium H5 | Próg | Wynik | Status |
|--------------|------|-------|--------|
| accuracy@10 aggregate | ≥0.70 | `🟡 [0.XX]` | `🟡 [PASSED/FAILED]` |
| Gap same vs cross | ≤5pp | `🟡 [±X.YYpp]` | `🟡 [PASSED/FAILED]` |
| Falsyfikowalność (a) | ≥0.60 (else REJECT) | `🟡 [0.XX]` | `🟡 [OK/REJECT]` |
| Falsyfikowalność (b) | ≤15pp (else REJECT) | `🟡 [±X.YYpp]` | `🟡 [OK/REJECT]` |
| Falsyfikowalność (c) | regresja same-register ≤2pp | `🟡 [±X.YYpp]` | `🟡 [OK/REJECT]` |

H5 status: `🟡 [PASSED / PARTIAL / FAILED / INCONCLUSIVE]`.

**Implications.** RQ5 jest niezależnym wymiarem kontrybucji (defense scaffolding pkt 3, wymiar 5). PASSED oznacza pierwszą publicznie udokumentowaną Polish ChPL↔Ulotka cross-register retrieval methodology — publishable na BioNLP / Polish NLP workshop niezależnie od H1 wyniku (`decisions/DEC-002_chpl-ulotka-pairing.md` § Konsekwencje, Pozytywne pkt 1). FAILED na akceptowalnym kryterium (np. gap > 5pp ale ≤ 15pp) reframuje wkład jako **negative-result case study** — pokazuje że paired training nie wystarcza dla cross-register transfer, wymaga dedykowanego objective (np. contrastive loss between paired versions). REJECTED (jedno z trzech kryteriów falsyfikowalności wyzwolone) oznacza, że RQ5 jest wycofany z synthesis 7.8 i framowany w R8 jako "limitations" + "future work". A4 vs A0 evidence dla DEC-002 wartości pairing — jeśli A4 ≈ A0 na cross-register, to Ulotki nie wnoszą wartości i DEC-002 jako methodological choice byłby nieuzasadniony empirycznie (wciąż uzasadniony korpusowo).

---

## 7.6 Drift detection results (RQ4/H4)

Sekcja prezentuje wyniki drift detection na simulated OOD dataset (Iteracja 5 per `02b_konspekt_v3_updates.md` § II.16). Drift detector implementowany per R5 (architektura) + R6 (modele): Evidently dla data drift (KS test na BGE-M3 embedding distributions per dimension, plus Wasserstein distance) + Alibi Detect dla statistical drift (MMD test z RBF kernel na pełnych embedding vectors).

**Simulated OOD setup.** Trzy strumienie ewaluacyjne:
- **In-distribution (ID):** psychiatryczne queries z eval set (200 par) — reference distribution, drift detector powinien dawać "no drift" alarmy z low frequency (false positive rate target ≤ 0.20).
- **OOD true:** 200 queries z neurology subdomain (ATC N04 — antiparkinsonics + N03 — antiepileptics) — semantically related ale poza N05/N06, drift detector powinien detect z high recall.
- **Perturbed ID:** 200 psychiatric queries z paraphrase-augmentation (Bielik few-shot rephrase z preservation semantic content) — borderline case, drift detector powinien NIE alarmować (paraphrase ≠ drift).

**Tabela 7.6.1.** Drift detection metrics na simulated OOD experiment. Per threshold (KS test p-value cutoff). Mean ± std z 3 random seeds.

| Threshold (p-value) | Precision | Recall | F1 | False Positive Rate | True Positive Rate | Detection latency (queries) |
|---------------------|-----------|--------|----|--------------------|--------------------|------------------------------|
| 0.001 | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: XX]` |
| 0.01 | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: XX]` |
| 0.05 | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: XX]` |
| 0.10 | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: 0.XX]` | `[Iter.5: XX]` |

🟡 Numbers TBD post-Iter. 5.

**Tabela 7.6.2.** False positive analysis — które in-distribution queries były false-flagged jako OOD (próbka 50 FP). Wzorce kategoryzowane.

| FP pattern | Count | Example query | Hypothesis |
|------------|-------|---------------|------------|
| `🟡 [Pattern A — TBD]` | `[Iter.5: XX]` | `🟡 [TBD]` | `🟡 [TBD]` |
| `🟡 [Pattern B — TBD]` | `[Iter.5: XX]` | `🟡 [TBD]` | `🟡 [TBD]` |
| `🟡 [Pattern C — TBD]` | `[Iter.5: XX]` | `🟡 [TBD]` | `🟡 [TBD]` |

🟡 Numbers TBD post-Iter. 5.

**Figura 7.6.1** *(placeholder)*. ROC curve drift detector (TPR vs FPR per threshold). AUC podane w legendzie. Highlight punkt operacyjny (recommended threshold dla H4 progu).

**Figura 7.6.2** *(placeholder)*. Detection latency vs threshold trade-off. Line chart: x-axis = threshold (p-value), y-axis = mean queries-to-detection (na true OOD stream). Druga oś y: FPR. Pokazuje trade-off między early detection a false alarm rate.

### Discussion (4-part template)

**Statement.** Tabela 7.6.1 pokazuje, że drift detector przy threshold p=0.05 osiąga precision = `🟡 [0.XX]` i recall = `🟡 [0.XX]` na simulated OOD (true OOD: neurology N04/N03; ID: psychiatric N05/N06; perturbed ID: paraphrased psychiatric).

**Interpretation.** Precision-recall trade-off w drift detection ma trzy mechanistyczne źródła: (1) **threshold sensitivity** — niższy p-value threshold (np. 0.001) daje high precision ale niski recall (detector tylko wyłapuje strong drift); wyższy threshold (np. 0.10) daje high recall ale niskie precision (false positives na in-distribution variance); (2) **distance metric choice** — KS test per-dimension (Evidently default) vs MMD na full vector (Alibi Detect) mogą dawać różne sygnały dla tego samego data shift; (3) **embedding space property** — BGE-M3 multilingual ma collapse (anizotropię) typowy dla pre-trained embeddings, co może maskować drift w niektórych regionach przestrzeni embedding'owej. Per-pattern false positive analysis (Tabela 7.6.2) lokalizuje, czy FP pochodzi z perturbed ID (znacznie mniejszy problem — paraphrase **jest** minimalnym drift) czy z prawdziwego in-distribution (większy problem — sygnalizuje detector noise).

**Comparison vs hypothesis.** Próg H4 (`02b_konspekt_v3_updates.md` § II.3.3): precision ≥0.80, recall ≥0.70 na simulated OOD. Wynik przy threshold p=`🟡 [optimal]`: precision = `🟡 [0.XX]`, recall = `🟡 [0.XX]` — H4 status: `🟡 [PASSED / PARTIAL / FAILED]`. Przy precision-recall trade-off, raportowane są wyniki dla **3 thresholds** (Tabela 7.6.1) plus rekomendacja operacyjna na podstawie ROC curve (Figura 7.6.1). H4 walidowane na **najlepszym threshold spełniającym oba kryteria jednocześnie**, jeśli istnieje; jeśli żaden threshold nie spełnia obu — H4 PARTIAL (jedno spełnione) lub FAILED (żadne).

**Implications.** PASSED H4 oznacza, że pipeline ma działający trigger logic dla retreningu — drift sygnał można podpiąć do Prefect orchestration jako condition uruchamiania nowego cyklu. FAILED H4 wymaga reframing: drift detection jako "monitoring" (raportowanie do dashboardu, decyzja human-in-the-loop), nie jako "auto-trigger" — co jest do explicit zaznaczenia w R5 architektura + R8 limitations. Simulated drift jest **explicit limitation** (NIE production traffic) — defense scaffolding: praca raportuje methodology + framework, ewaluacja na production drift to future work (per `02b_konspekt_v3_updates.md` § II.13 OUT scope).

---

## 7.7 Kategoryczna error analysis

**Sekcja KRYTYCZNA — Defense scaffolding pkt 2** (`thesis_elements/CLAUDE.md` § Defense scaffolding). Iteracja realizacji: 6 (per `02b_konspekt_v3_updates.md` § II.16). Niniejsza sekcja kategoryzuje błędy rerankera w taksonomii 6-poziomowej i raportuje distribution per cykl, dostarczając **wynik metodologiczny niezależny od magnitude poprawy nDCG@10**.

**Defense argument explicit:** *Nawet jeśli nDCG@10 nie poprawia się dramatycznie, rozkład błędów w 6-poziomowej taksonomii to wartościowy wynik metodologiczny. Praca raportuje strukturę problem space dla polskiego farmaceutycznego rerankera, co stanowi reusable contribution dla przyszłych prac w domenie.*

**Sample selection.** Dla każdego cyklu (1, 2, 3) wybrane 100 incorrect rankings — zdefiniowane jako **gold passage position > 5 w top-10**. Próbka 100 per cykl daje 300 łącznych error cases. Manual labeling przez autorkę z dwustopniową walidacją: (1) pierwsze pass — przypisanie kategorii, (2) drugie pass — re-labeling po 24h dla intra-rater agreement check (Cohen's kappa ≥0.70 wymagane).

### 7.7.1 Taksonomia 6-poziomowa — definicje operacyjne

Sześć kategorii błędów z definicjami operacyjnymi i mitigation strategies. Taksonomia rozszerza standardową IR error taxonomy o **register mismatch** (NEW dla RQ5) — kluczowy dodatek dla cross-register pipeline.

#### 1. Terminology miss

**Definicja operacyjna.** Query używa **lay synonym** lub niestandardowej terminologii (np. *"zaśnięcie"* zamiast *"hipnoza"*, *"żołądek mnie boli"* zamiast *"ból nadbrzusza"*). Top-1 reranker wybiera passage używające **professional synonym lub łacińskiej terminologii** (np. *"hypnoticum"*, *"epigastrium"*) który jest semantycznie poprawny, ale **nie matched** ze surface formą query. Gold passage używa terminologii zgodnej z query register lub bridges między rejestrami.

**Wskaźnik diagnostyczny.** Token-level overlap query ↔ top-1 < 0.1; query ↔ gold ≥ 0.3.

**Mitygacja proponowana.** Cross-register training (RQ5) bezpośrednio adresuje przez expansion training corpus o paired ChPL↔Ulotka (DEC-002). Skuteczność mitigation mierzona przez Δ count tej kategorii: cykl 1 (z Ulotkami) vs A4 (bez Ulotek).

#### 2. Ambiguous query

**Definicja operacyjna.** Query odpowiada **semantycznie na ≥2 różne sekcje** ChPL lub ≥2 różne dokumenty (np. *"objawy"* pasuje do sekcji 4.4 specjalne ostrzeżenia [opisuje objawy nadwrażliwości] oraz 4.8 działania niepożądane [opisuje objawy SE]). Top-1 reranker wybiera **legitimate** passage, ale różny od annotated gold.

**Wskaźnik diagnostyczny.** Query length < 5 słów AND brak named entity (substancja czynna, nazwa handlowa, kod ATC).

**Mitygacja proponowana.** **Acceptable error** — flag w taxonomy, **NIE liczyć jako defekt rerankera w aggregated metrics**. Future work: query expansion z conversation context (multi-turn) — adresowane przez LlamaIndex `ChatEngine` (`02b_konspekt_v3_updates.md` § II.13.10). Eval set design refinement: gold passage labeled jako "primary" + "alternative legitimate" passages, partial credit scoring zamiast binary.

#### 3. Length mismatch

**Definicja operacyjna.** Top-1 passage znacznie krótszy lub dłuższy niż gold passage (length ratio < 0.3 lub > 3.0). Wskazuje na **chunking strategy mismatch** — gold passage jest section-level (np. cała sekcja 4.3), top-1 to mini-chunk (np. tylko first paragraph) lub odwrotnie.

**Wskaźnik diagnostyczny.** `len(top1_passage) / len(gold_passage)` poza zakresem [0.3, 3.0]. Top-1 może być semantically partial-match, ale nie pełna odpowiedź.

**Mitygacja proponowana.** Chunking strategy revision (R3 Dane § chunking strategies). Możliwe: hierarchical chunking (parent-child relationship między section-level i sub-paragraph chunks), late interaction reranking (BGE-M3 colbert vectors). Future work, NIE objęte w niniejszej pracy.

#### 4. OOD chunk

**Definicja operacyjna.** Top-1 passage dotyczy leku z **innej klasy ATC** niż query (np. query o sertralina N06AB, top-1 o metformina A10BA). Wskazuje na **fundamental domain confusion** rerankera — semantyczne niezrozumienie context'u farmakologicznego.

**Wskaźnik diagnostyczny.** ATC class top-1 ≠ ATC class gold AND ATC class top-1 nie współwystępuje w jakiejkolwiek interakcji z gold drug.

**Mitygacja proponowana.** Reranker domain confusion — sygnał do podziału training set per ATC group (kontrastowe negative sampling intra-class vs inter-class) lub do explicit ATC tagging w input format. Powiązane z A3 ablation (psych-only vs full corpus) — jeśli OOD chunk count rośnie w A3 (mniejszy corpus = mniej domain coverage), to pełen corpus jest empirycznie validated.

#### 5. Register mismatch (NEW dla RQ5)

**Definicja operacyjna.** Query w jednym rejestrze (lay lub pro), top-1 passage w **tym samym rejestrze co query**, ale gold passage w **przeciwnym rejestrze** (per RQ5 setup — gold to cross-register pair). Reranker preferuje **same-register** odpowiedź zamiast **semantically-aligned cross-register** odpowiedzi.

**Wskaźnik diagnostyczny.** Register classification (lay/pro) query == register top-1 ≠ register gold. Register classifier prosta heurystyka: presence łacińskich terminów + ATC codes + section header style → pro; presence imperatives ("zażyj", "nie stosuj") + colloquial vocabulary → lay.

**Mitygacja proponowana.** **Acceptable in same-register evaluation** (200 par psych eval set jest w większości pro-pro), **problem in cross-register evaluation** (1800 par RQ5). Bezpośrednio adresowane przez DEC-002 (paired training corpus) i mierzone przez A4 ablation (Tabela 7.5.1). Jeśli register mismatch dominuje w cross-register errors, to wskazuje że pairing training nie wystarcza i potrzebny jest **dedicated cross-register objective** (np. contrastive loss między paired versions) — future work R8.

#### 6. OCR artifact

**Definicja operacyjna.** Top-1 passage zawiera **ewidentne uszkodzenia OCR** (znaki wymienione, fragmenty słów ucięte, encoding errors, np. *"kwerendy"* zamiast *"krwawienia"*, *"podstacja"* zamiast *"podawanie"*). Wskazuje na **data quality issue** w upstream chunking, NIE na defekt rerankera.

**Wskaźnik diagnostyczny.** Manual flag — autorka identyfikuje uszkodzony tekst podczas labeling. Automatyczny proxy: language model perplexity (Bielik) na passage > threshold (dystrybucja per cykl pokazana w R4 EDA OCR quality section).

**Mitygacja proponowana.** Pipeline OCR quality threshold — discard chunks z perplexity > threshold lub flagowanie do manual review. Powiązane z `sources_catalog.md` § Iteracja 0 pre-condition #6 (OCR quality < 15% damaged chars). Jeśli OCR artifact > 10% errors w taxonomy, to ChPL/Ulotka extraction pipeline wymaga revision (najprawdopodobniej re-extract z wyższą jakością PDF parser, np. docling vs pypdf).

### 7.7.2 Distribution per cykl

**Tabela 7.7.1.** Distribution kategorii błędów per cykl. Próbka 100 incorrect rankings per cykl (gold position > 5 w top-10). Procent z [n=100].

| Kategoria błędu | Cykl 1 (n=100) | Cykl 2 (n=100) | Cykl 3 (n=100) | Trend (Δ cykl 3 vs 1) |
|------------------|----------------|----------------|----------------|-------------------------|
| 1. Terminology miss | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: ±X.YYpp]` |
| 2. Ambiguous query | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: ±X.YYpp]` |
| 3. Length mismatch | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: ±X.YYpp]` |
| 4. OOD chunk | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: ±X.YYpp]` |
| 5. Register mismatch | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: ±X.YYpp]` |
| 6. OCR artifact | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: XX%]` | `[Iter.6: ±X.YYpp]` |
| **Total** | 100% | 100% | 100% | — |

🟡 Numbers TBD post-Iter. 6.

**Inter-rater + intra-rater agreement.** Intra-rater Cohen's kappa (autorka labels round 1 vs round 2 po 24h) = `🟡 [Iter. 6: 0.XX]`. Próg ≥0.70 dla acceptable consistency.

**Figura 7.7.1** *(placeholder)*. Stacked bar chart distribution błędów per cykl. X-axis: cykl (1, 2, 3). Y-axis: procent (0-100%). 6 kolorów per kategoria (consistent z Tabelą 7.7.1). Trend zmian per kategoria: jeśli kategoria 1 (terminology miss) maleje przez cykle → mitigation skuteczne; jeśli rośnie lub stabilna → mitigation niewystarczająca.

### 7.7.3 Top 3 dominant error patterns + recommendations

**Tabela 7.7.2.** Top 3 dominant error patterns per total count (cykl 1 + 2 + 3). Z rekomendacjami dla future work.

| Rank | Kategoria | Total count (n=300) | Dominant sub-pattern | Recommendation dla future work |
|------|-----------|---------------------|------------------------|----------------------------------|
| #1 | `🟡 [Iter.6: TBD]` | `🟡 [XX]` | `🟡 [TBD specific pattern]` | `🟡 [TBD specific recommendation]` |
| #2 | `🟡 [Iter.6: TBD]` | `🟡 [XX]` | `🟡 [TBD specific pattern]` | `🟡 [TBD specific recommendation]` |
| #3 | `🟡 [Iter.6: TBD]` | `🟡 [XX]` | `🟡 [TBD specific pattern]` | `🟡 [TBD specific recommendation]` |

🟡 Numbers TBD post-Iter. 6.

### Discussion (4-part template)

**Statement.** Tabela 7.7.1 pokazuje, że dominującą kategorią błędów w cyklu 1 jest `🟡 [Kategoria_X]` (`🟡 [XX%]`), z trendem `🟡 [malejącym/stabilnym/rosnącym]` przez cykle 2 i 3 (Δ = `🟡 [±X.YYpp]`). Top 3 dominant patterns w Tabeli 7.7.2.

**Interpretation.** Distribution błędów odzwierciedla strukturę problem space rerankera: jeśli **terminology miss** dominuje, problem jest **lexical** (rozwiązanie: większy/bardziej diverse training corpus, lepszy tokenizer, query expansion). Jeśli **OOD chunk** dominuje, problem jest **domain confusion** (rozwiązanie: ATC tagging, intra-class hard negatives). Jeśli **register mismatch** dominuje (na cross-register eval), DEC-002 paired training nie wystarcza — wymaga dedykowanego objective. Jeśli **OCR artifact** > 10%, to upstream data pipeline wymaga revision niezależnie od rerankera. Powyższe interpretacje to **mechanistic mapping** error patterns na konkretne pipeline interventions — sygnał dla future work.

**Comparison vs hypothesis.** Sekcja 7.7 nie ma własnej hipotezy z falsyfikowalnym progiem (Defense scaffolding pkt 2 — error analysis to **methodological output**, nie hypothesis test). Walidacja realizacji: (i) wszystkie 6 kategorii reprezentowane (>0% w przynajmniej jednym cyklu), (ii) intra-rater kappa ≥0.70, (iii) explicit recommendations per top 3.

**Implications.** Defense argument explicit (Defense scaffolding pkt 2): *Nawet jeśli H1 odrzucone (cykl 1 daje +5pp zamiast +10pp nDCG@10), kategoryczna error analysis to wartościowy wynik metodologiczny niezależny od magnitude poprawy*. Future work R8 będzie cytować Tabelę 7.7.2 explicite — top 3 dominant patterns to **roadmap** dla kolejnej iteracji pipeline'u. Cross-register specific: register mismatch frequency w cyklu 1 vs A4 (Tabela 7.5.1) bezpośrednio testuje wartość Ulotek w training (czy paired corpus eliminuje register confusion).

---

## 7.8 Synteza — RQ1-RQ5 status table

Sekcja syntetyzuje wyniki sekcji 7.3-7.7 w mapping 5 RQ → status hipotezy → wymiar kontrybucji (Defense scaffolding pkt 3 — `thesis_elements/CLAUDE.md`). Synteza dostarcza **explicit per-hypothesis answer** wymagany przez Task 07 (PRO-D-THESIS Assignment 9, kryterium E: "Alignment z research question + hypothesis").

### 7.8.1 Status table

**Tabela 7.8.1.** Status 5 RQ × evidence × wymiar kontrybucji.

| RQ | Hipoteza (próg) | Wynik | Status | Sekcja evidence | Wymiar kontrybucji (R8) |
|----|------------------|-------|--------|------------------|---------------------------|
| RQ1/H1 | Retrening rerankera ≥10pp nDCG@10 | `🟡 [+X.YYpp]` | `🟡 [PASSED / PARTIAL / FAILED / INCONCLUSIVE]` | 7.3.1 | (1) Inżynierski + (3) Artefaktowy |
| RQ2/H2 | LLM-judge κ ≥0.50 | `🟡 [κ=0.XX]` | `🟡 [PASSED / PARTIAL / FAILED]` | 7.3.3 | (2) Metodologiczny |
| RQ3/H3 | Plateau cykl 3 ≤2pp, p>0.05 | `🟡 [+X.YYpp, p=0.XXX]` | `🟡 [PASSED / FAILED]` | 7.4 | (1) Inżynierski (sub-finding) |
| RQ4/H4 | Drift detector P≥0.80, R≥0.70 | `🟡 [P=0.XX, R=0.XX]` | `🟡 [PASSED / PARTIAL / FAILED]` | 7.6 | (4) Eksperymentalny |
| RQ5/H5 | Cross-register acc@10 ≥70%, gap ≤5pp | `🟡 [acc=0.XX, gap=±X.YYpp]` | `🟡 [PASSED / PARTIAL / FAILED / INCONCLUSIVE]` | 7.5 | (5) Korpusowy + metodologiczny novel |

🟡 Numbers TBD post-Iter. 2-6.

### 7.8.2 Per-hypothesis explicit answers

#### H1 (RQ1) — Retraining effectiveness

**Hipoteza:** Retrening rerankera dodaje ≥10pp nDCG@10 vs base polish-reranker-roberta-v3 na 200-parowym eval set psych.

**Odpowiedź:** `🟡 [PASSED / PARTIAL / FAILED]`. Cykl 1 daje `🟡 [+X.YYpp]` (Tabela 7.3.1), cykl 2 dodatkowo `🟡 [+X.YYpp]`, cykl 3 dodatkowo `🟡 [+X.YYpp]` (Tabela 7.4.1). Cumulative improvement po 3 cyklach: `🟡 [+X.YYpp]`. Ablation A1 (Tabela 7.3.2) pokazuje, że judge-driven labels kontrybują `🟡 [-X.YYpp Δ vs random]` — nie sam corpus exposure.

**W przypadku FAILED:** wynik framowany jako **negative-result publishable** (Defense scaffolding pkt 3). H1 odpada, ale wkład pracy nie jest znegowany — pozostają wymiary (2)-(5). Przejście do R8 sekcji "Negative-result framing" z explicit decompozycją kontrybucji.

#### H2 (RQ2) — LLM-judge agreement

**Hipoteza:** LLM-as-judge agreement z manual labels (autorka, 200 par psych) Cohen's kappa ≥0.50 (acceptable: ≥0.40).

**Odpowiedź:** `🟡 [PASSED / PARTIAL / FAILED]`. Final judge `🟡 [<judge_model>]` osiąga mean κ = `🟡 [0.XX]` (Tabela 7.3.3.B). Cross-protocol breakdown: pairwise κ = `🟡 [0.XX]`, pointwise κ = `🟡 [0.XX]`, faithfulness κ = `🟡 [0.XX]`, cross-register κ = `🟡 [0.XX]`.

**Reciprocal effect na H1:** jeśli H2 FAILED (κ < 0.40), H1 negative result jest mechanicznie wytłumaczalny przez noisy training signal — **nie** fundamentalny defekt rerankera. To otwiera defense path: "Pipeline jest correct; problem leży w judge calibration; future work — better judge framework".

#### H3 (RQ3) — Plateau po cyklu 2

**Hipoteza:** Cykl 3 retreningu daje ≤2pp poprawy vs cykl 2 z p>0.05 (paired t-test seed-pairs).

**Odpowiedź:** `🟡 [PASSED / FAILED]`. Cykl 3 vs cykl 2: Δ nDCG@10 = `🟡 [+X.YYpp]`, p = `🟡 [0.XXX]` (Tabela 7.4.1).

**Interpretacja PASSED:** plateau zaobserwowany — pipeline ma **methodological saturation finding**, publishable jako sub-contribution (continual fine-tuning rerankerów polskich saturuje się po 2 cyklach z tym budżetem syntetycznych danych). Future work: testowanie 4-5 cykli z augmented data diversity (różny query template, multi-turn queries).

**Interpretacja FAILED:** plateau nie osiągnięte — cykl 3 nadal istotnie poprawia. Reframing: "saturacja nie zaobserwowana w obserwowanym zakresie 3 cykli; ekstrapolacja ostrzega przed continual fine-tuning bez bound". Defensible jako limitation explicit.

#### H4 (RQ4) — Drift detection

**Hipoteza:** Drift detector na simulated OOD osiąga precision ≥0.80, recall ≥0.70.

**Odpowiedź:** `🟡 [PASSED / PARTIAL / FAILED]`. Przy threshold p = `🟡 [optimal]`: precision = `🟡 [0.XX]`, recall = `🟡 [0.XX]` (Tabela 7.6.1).

**PARTIAL** (jedno kryterium spełnione): reframing precision-recall trade-off w R5 architektura — operator pipeline'u może wybrać threshold per use case (high-precision dla auto-trigger retreningu, high-recall dla human-in-the-loop monitoring). FAILED: drift detector framowany jako **monitoring tool** (raporty do dashboardu), nie auto-trigger.

#### H5 (RQ5) — Cross-register retrieval

**Hipoteza:** Reranker dotrenowany na ChPL+Ulotka pairs osiąga accuracy@10 ≥70% na cross-register, gap ≤5pp poniżej same-register.

**Odpowiedź:** `🟡 [PASSED / PARTIAL / FAILED / INCONCLUSIVE]`. Aggregate accuracy@10 = `🟡 [0.XX]` (Tabela 7.5.1). Direction-stratified: lay→pro = `🟡 [0.XX]`, pro→lay = `🟡 [0.XX]`. Direction asymmetry Δ_dir = `🟡 [0.XX]` (Tabela 7.5.2). Gap same vs cross = `🟡 [±X.YYpp]` (Tabela 7.5.3). A4 ablation (ChPL-only) gap vs A0 = `🟡 [±X.YYpp]`.

**Falsyfikowalność (DEC-002):**
- (a) accuracy@10 < 60% → REJECT: `🟡 [tak/nie]`
- (b) gap > 15pp → REJECT: `🟡 [tak/nie]`
- (c) regresja same-register > 2pp → REJECT: `🟡 [tak/nie]`

**REJECTED:** RQ5 wycofany z synthesis, R8 framuje jako "explored but not validated" + future work directions. **PASSED:** pierwsza publicznie udokumentowana Polish ChPL↔Ulotka cross-register methodology — publishable na BioNLP / Polish NLP workshop niezależnie.

### 7.8.3 Limitations explicit (4 kategorie)

Per `assignments/plans/zadanie_07_plan.md` § 8 acceptance checklist + Task 07 (PRO-D-THESIS Assignment 9, kryterium "Limitations"):

**Dataset limitations:**
- 200-parowy psych eval set jest **świadomy sample bias** — eval wąski (psych N05/N06), training szeroki (cała farma). Uzasadnienie w `02b_konspekt_v3_updates.md` § II.4.3 (leverage manual validation kompetencji autorki). Konsekwencja: walidacja na pełnej farmakologii nie jest mierzona; psych performance jest proxy dla pharma performance z untested generalization.
- OCR overhead z PDF parsing (R3 Dane § OCR quality) — `🟡 [Iter.6: XX%]` chunks ma residual OCR artifacts (kategoria 6 w error analysis, sekcja 7.7).
- Document-level split, ale w obrębie tego samego dokumentu wszystkie chunks razem → możliwy intra-document leakage przez wspólne entities (substancja czynna powtarzająca się w sekcjach).
- 1800 par cross-register eval — borderline-adequate dla detekcji 5pp gap z 80% power (`02b_konspekt_v3_updates.md` § II.3.3). Jeśli wyniki ambiguous, expansion do 1500 per direction w hypothetical follow-up.

**Model limitations:**
- BGE-M3 frozen (no fine-tuning) — embedder kontrybuuje jako fixed component. Embedder fine-tuning OUT scope (`02b_konspekt_v3_updates.md` § II.3.4). Konsekwencja: ceiling na overall retrieval quality jest częściowo determinowany przez embedder limit; reranker może dostraje, ale nie naprawi fundamental embedder errors.
- polish-reranker-roberta-v3 (~360M params) — średniej wielkości model. Model capacity ograniczenie może być przyczyną plateau w cyklu 3 (sekcja 7.4 interpretation #2).
- LLM judge (final winner: `🟡 [<judge_model>]`) — pojedynczy model jako oracle. Multi-model ensemble OUT scope, future work.

**Eval limitations:**
- Manual labels by autorka (single annotator setup, bez inter-annotator agreement check). Mitigation przez **intra-rater kappa** check po 24h (sekcja 7.7.2). Single-annotator bias nie jest w pełni kontrolowany.
- Simulated drift NIE real production drift — H4 walidowane na artificial OOD streams (psych vs neurology vs paraphrased), nie na production traffic. Konsekwencja: H4 PASSED nie gwarantuje production drift detection skuteczności; future work — production deployment + monitoring.
- Cross-register eval set programatycznie wygenerowany z deterministycznym alignment (productID), spot-check 50 par. Pozostaje 1750 par bez manual validation — ryzyko że alignment quality jest niższe niż 90% w pełnej próbce.

**External validity limitations:**
- PL-only — `🟡 [Iter.X: TBD]` rezultaty dla polskiej farmakologii. Cross-language transfer (PL → EN, DE, etc.) nie jest mierzony (`02b_konspekt_v3_updates.md` § II.13.8 future work).
- Single domain (farmakologia) — methodology transfer na inne PL domeny z dwoma rejestrami (prawo: kodeksy↔przewodniki obywatelskie; medycyna: wytyczne↔materiały edukacyjne) nie testowany (`02b_konspekt_v3_updates.md` § II.13.9 future work).
- Static eval set — drift w korpusie URPL (np. nowe leki, zmiany ChPL) nie odbywała się w okresie pracy. Production deployment w długim horyzoncie miałby drift trigger inne niż mierzony.

### 7.8.4 Mapping 5 RQ → 5 wymiarów kontrybucji (defense scaffolding pkt 3)

Pełna decompozycja kontrybucji w R8 (Podsumowanie) per `thesis_elements/CLAUDE.md` § Defense scaffolding pkt 3. Tu skrót preview:

1. **Metodologiczny (RQ2):** walidowany framework LLM-as-judge dla polskiej domeny specjalistycznej (farmakologia) — pierwszy taki audit publicznie dla polskiego pharma BioNLP.
2. **Inżynierski (RQ1, RQ3):** reprodukowalny pipeline MLOps retreningu komponentów RAG (open-source artefakt, GitHub + DVC).
3. **Artefaktowy (RQ1):** dotrenowany polish-reranker dla farmakologii — artefakt HuggingFace.
4. **Eksperymentalny (RQ4):** drift detection z simulated drift framework.
5. **Korpusowy + metodologiczny novel (RQ5):** pierwsza publicznie udokumentowana Polish ChPL↔Ulotka aligned corpus + cross-register retrieval evaluation methodology — luka w literaturze potwierdzona (Grabowski 2018 [1] = EN-PL comparable corpus PIL, nie intra-PL cross-register; `decisions/DEC-002_chpl-ulotka-pairing.md` § Uzasadnienie pkt 2).

**Każdy z pięciu wymiarów broni się niezależnie.** W przypadku odrzucenia H1, praca zachowuje wkład w wymiarach (2)-(5), z RQ5 jako wyróżnioną kontrybucją do polskiego BioNLP.

---

## 7.9 Bibliografia (placeholder, ~5-8 ref)

Bibliografia placeholderowa dla cytacji użytych w R7. Pełna bibliografia pracy w R10 (lub na końcu R8). Kanonicznie cytacje IEEE z bookmark anchors (per Task 09 — `assignments/plans/zadanie_07_plan.md` § Pre-conditions).

> [1] Grabowski Ł. (2018). *On Identification of Bilingual Lexical Bundles for Translation Purposes: The Case of an English-Polish Comparable Corpus of Patient Information Leaflets*. In R. Mitkov, J. Monti, G. Corpas Pastor & V. Seretan (Eds.), *Multiword Units in Machine Translation and Translation Technology* (pp. 181–200). Current Issues in Linguistic Theory 341. John Benjamins. DOI: 10.1075/cilt.341.09gra. ✓ verified 2026-05-16.

> [2] Cao Y., Shui R., Pan L., Kan M.Y., Liu Z., Chua T.S. (2020). *Expertise Style Transfer: A New Task Towards Better Communication Between Experts and Laymen*. ACL 2020.

> [3] Devaraj A., Marshall I.J., Wallace B.C., Li J.J. (2021). *Paragraph-level Simplification of Medical Texts*. 🟡 Verify exact venue (NAACL 2021 vs EMNLP 2021) via `citation-checker`.

> [4] van den Bercken L., Sips R.J., Lofi C. (2019). *Evaluating Neural Text Simplification in the Medical Domain*. WWW 2019. 🟡 Verify year (2019 vs 2020) via `citation-checker`.

> [5] Landis J.R., Koch G.G. (1977). *The Measurement of Observer Agreement for Categorical Data*. Biometrics, 33(1), 159-174. 🟡 Verify via citation-checker.

> [6] Karp `🟡 [TBD initials]` (2025). *`🟡 [TBD title]` — Polish legal LLM-as-judge*. 🟡 Verify exact citation via citation-checker — anchor reference dla porównawczego kappa Polish-domain LLM-judge.

> [7] Es S., James J., Espinosa-Anke L., Schockaert S. (2024). *RAGAS: Automated Evaluation of Retrieval Augmented Generation*. EACL 2024 (System Demonstrations). 🟡 Verify via citation-checker.

> [8] Karpukhin V., Oğuz B., Min S., Lewis P., Wu L., Edunov S., Chen D., Yih W. (2020). *Dense Passage Retrieval for Open-Domain Question Answering*. EMNLP 2020. (Cytowane w `02b_konspekt_v3_updates.md` § II.4.6 — DPR hard negatives strategy inspiration).

> [9] Thakur N., Reimers N., Rücklé A., Srivastava A., Gurevych I. (2021). *BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*. NeurIPS 2021 Datasets and Benchmarks. 🟡 Verify via citation-checker — reference dla expected magnitude poprawy domain adaptation (5-15pp).

> [10] Rabin M.O., `🟡 [TBD]` (`🟡 [TBD year]`). *`🟡 [TBD]` — Drift detection methods reference (Evidently / Alibi Detect / KS test / MMD)*. 🟡 Verify via citation-checker — anchor reference dla methodology drift detection.

**Notka cytacyjna:** powyższe 10 placeholder-ref to **anchor citations** dla R7. Pełna bibliografia pracy (~30+ pozycji per `thesis_elements/CLAUDE.md` § Format PJATK) zawiera dodatkowo cytacje z R1, R2, R6 (literatura review + modele detail). Final citation pass via komenda `/citations` na komplecie rozdziałów (R1-R8) w Iteracji 8 — patrz `assignments/plans/zadanie_07_plan.md` § 4 plan iteracji #9.

---

## Self-review checklist (per `thesis_elements/CLAUDE.md` § Workflow rozdziału krok 5)

- [ ] Wszystkie 5 RQ z explicit per-hypothesis odpowiedzią (sekcja 7.8.2)
- [ ] 6-poziomowa kategoryczna error analysis (sekcja 7.7) — Defense scaffolding pkt 2
- [ ] Wszystkie 4 ablacje A1-A4 raportowane (sekcja 7.3.2 + A4 cross-context w 7.5)
- [ ] Tabele wynikowe z mean ± std (3 random seeds)
- [ ] Wszystkie tabele referenced w tekście (grep check przed final)
- [ ] Wszystkie figury podpisane + referenced
- [ ] 4-part discussion template po każdej tabeli/figurze
- [ ] Limitations explicit w 4 kategoriach (sekcja 7.8.3)
- [ ] Cross-RQ synthesis mapping 5 RQ → 5 wymiarów kontrybucji (sekcja 7.8.4)
- [ ] Bez time-proofing zakazanych słów ("obecnie", "rosnące", "brak", "jedyny", "żaden")
- [ ] Bez emoji w prose (placeholders 🟡 i ✅/❌ w meta-tabelach OK jako oznaczenia stanu)
- [ ] Cytacje verifiable, niepewności flagged z `🟡 Verify via citation-checker`
- [ ] Konsystentna terminologia: farmakologia (domena), psychiatryczny eval subset (gold standard)
- [ ] Direction-stratified reporting w 7.5 (per DEC-002 cleanup decision)
- [ ] Multi-stage judge validation (Stage 1 Iter. 0b shortlist + Stage 2 Iter. 2 final winner) w 7.3.3

---

## Co dalej w tym rozdziale

1. **Iteracje 2-6 fill-in liczb** — wszystkie placeholder cells `[Iter.N: X.XX ± Y.YY]` zastąpić rzeczywistymi metrykami z MLflow. Sequential dependency: Iter. 2 → 3 → 4 → 5 → 6.
2. **Per-RQ discussion expansion** — po fill-in liczbami, każdy 4-part discussion template rozszerzyć o **konkretne** mechanistic interpretations (np. "cykl 1 daje +X.YYpp, co odpowiada ~Y% poprawy nad BEIR baseline range 5-15pp dla domain adaptation [Thakur 2021]").
3. **Citation pass** — `/citations R7_wyniki.md` (deleguje do `citation-checker` subagent) — verify wszystkie [N] reference w bibliografii placeholderów + flagged 🟡 entries.
