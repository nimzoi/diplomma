# Plan zadania 08 — Podsumowanie, Wnioski, Future Work (R8)

**Institutional source:** `assignments/08.md` (Task 08, 10 pkt)
**PRO-D-THESIS practical:** `assignments/PRO-D-THESIS-practical-work-main/12-Conclusions-Limitations-Future-Work.md` (Assignment 12)
**Mapuje na rozdział:** R8 Podsumowanie + Wnioski + Future Work
**Iteracja realizacji:** 8 (finalization) — pre-condition: R1-R7 drafted

## 1. Czego instytucjonalnie wymaga Task 08

3 podsekcje:
1. **Overall Summary** — recap topic, objectives, scope, methods, stages
2. **Conclusions** — main findings, objectives achieved?, strengths, limitations, learning reflection
3. **Future Work** — improvements, extensions, real-world adaptation, additional studies

## 2. Czego wymaga PRO-D-THESIS Assignment 12

- A. **Direct answer to RQ** (restate RQ + H, concise answer, quantitative confirmation gdzie relevant)
- B. Summary of technical contribution (what implemented, what compared, what discipline)
- C. **Limitations** (mandatory + critical) — dataset/model/eval/external validity
- D. **Future Work** (realistic, derived from limitations, technically grounded)
- E. Final coherence verification checklist

## 3. Jak to wygląda w naszym v3.1

### Sekcja 8.1: Overall summary (~400 słów)

Recap:
- Topic: pipeline MLOps retreningu polskiego rerankera farmaceutycznego + cross-register RQ5
- 5 RQ + 5 H, każde z jasną odpowiedzią z R7
- Methods stack: SGLang + TEI + Prefect + MLflow + Langfuse + Evidently/Alibi + RAGAS
- 3 cykle retreningu + drift detection + cross-register evaluation
- Korpus ~4100 docs (6 strata farmacji + paired ChPL↔Ulotka)
- Eval gold standard 200 par psych subset

### Sekcja 8.2: Conclusions — KLUCZOWA SEKCJA — 5-wymiarowa kontrybucja (Defense scaffolding pkt 3)

**FORMAT z Defense scaffolding — zaszyj explicit paragraph:**

> *„Wkład pracy ma pięć niezależnych wymiarów. Empiryczna magnitude poprawy retrievalu (RQ1) jest tylko jednym z nich:*
>
> *1. **Metodologiczny:** walidowany framework LLM-as-judge dla polskiej domeny specjalistycznej (RQ2) — pierwszy taki audit publicznie dla farmakologii PL.*
> *2. **Inżynierski:** reprodukowalny pipeline MLOps retreningu komponentów RAG (open-source artefakt z DVC + MLflow + Prefect orchestration).*
> *3. **Artefaktowy:** dotrenowany polish-reranker dla farmakologii — artefakt HuggingFace dostępny społeczności PL NLP.*
> *4. **Eksperymentalny:** drift detection z simulated drift framework (RQ4) — reprodukowalny benchmark dla PL specialized RAG.*
> *5. **Korpusowy / metodologiczny novel:** pierwsza publicznie udokumentowana Polish ChPL↔Ulotka aligned corpus + cross-register retrieval evaluation (RQ5) — literature gap potwierdzony (Grabowski 2017 = EN-PL, nie intra-PL cross-register).*
>
> *Każdy z pięciu wymiarów broni się niezależnie. W przypadku odrzucenia H1 (retreningowy reranker nie osiąga założonej poprawy nDCG@10), praca zachowuje wkład w wymiarach (2)-(5), z RQ5 jako wyróżnioną kontrybucją do polskiego BioNLP."*

**Po paragraph: 5 RQ direct answers** (per A12 wymóg A):
- **RQ1 H1:** [supported / partial / rejected] na podstawie R7.1
- **RQ2 H2:** [supported / partial / rejected] na podstawie R7.2
- **RQ3 H3:** [supported / partial / rejected] na podstawie R7.3
- **RQ4 H4:** [supported / partial / rejected] na podstawie R7.4
- **RQ5 H5:** [supported / partial / rejected] na podstawie R7.5

### Sekcja 8.3: Limitations (mandatory per Task 08 + A12 critical)

4 kategorie explicit:

#### 8.3.1 Dataset limitations
- 5 świadomych biases z R3 + sources_catalog.md (license/ATC/recency/PL-only/source-type)
- Iteracja 0 feasibility findings (OCR overhead actual %)
- 200 par psych subset (świadomy bias DEC-001) — leverage manual validation kompetencji vs broad pharma coverage trade-off
- Brand vs generic — sampling po `productID` może produce duplicaty na DCI level

#### 8.3.2 Model limitations
- **BGE-M3 frozen** — no embedder fine-tuning (świadoma decyzja: hard negative mining = pain point danych)
- **polish-reranker base ~360M params** — no scale-up do 1B+ (compute constraint)
- **Judge model API vs local trade-off** — `<judge_model>` choice constraints (jeśli Claude Haiku → API dependency; jeśli open → local compute)
- 3 random seeds (nie 5-10) — variance estimates conservative

#### 8.3.3 Evaluation limitations
- Eval set 200 par psych subset — small N dla H2 Cohen's kappa confidence
- Simulated drift NIE real production traffic — H4 conclusions ograniczone
- Cross-register 1800 par programatycznie generated — alignment integrity rate (Iteracja 0 pre-condition) wpływa na quality
- Brak human evaluation końcowych odpowiedzi RAG (przekracza scope autorki — patrz R3 ethics)

#### 8.3.4 External validity
- Results **PL-only** — brak cross-language generalization claims
- **Single domain** (pharmacology) — brak cross-domain generalization claims
- **Single tooling stack** (SGLang/TEI/Prefect/MLflow) — alternative stacks (np. Ray Serve, Airflow) NIE compared

### Sekcja 8.4: Future work (4-5 directions, realistic + technical grounding)

1. **Cross-domain transfer** — czy methodology transferuje do innych PL specialized domain (legal, technical, scientific)? Test na 2-3 domenach.
2. **Cross-language register transfer** — czy lessons z PL ChPL↔Ulotka transferują do EN/DE SPC↔PIL? Mini-corpus 100 par per language.
3. **Real-time drift na produkcyjnym ruchu** — current simulated → real users (potrzebny partner organizacyjny)
4. **Hard negative mining dla embeddera** — BGE-M3 zostawiony frozen, future contrastive fine-tune
5. **Adversarial robustness rerankera** — explicit eval (z prompt injection literature v1 connection)

### Sekcja 8.5: Final coherence checklist (per A12 E)

- Czy każdy R1 RQ jest answered w R7 explicit z reference?
- Czy każdy experiment z R5+R6 raportowany w R7?
- Czy limitations w R8 są reprezentowane w odpowiednich rozdziałach (R3 bias, R5 risk, R7 negative findings)?
- Czy 5-wymiarowa kontrybucja jest spójna z 5 RQ (każdy wymiar mapuje do RQ)?

## 4. Plan iteracji z Claude (agent jako collaborator)

| # | Iteracja | Co Claude robi | Co Ty robisz |
|---|---|---|---|
| 1 | Outline R8 | Proponuje 5 podsekcji per Task 08 + A12 wymogi | Sign-off |
| 2 | Sekcja 8.1 Overall Summary | Drafts ~400 słów recap topic/objectives/methods/stages | Reviews accuracy |
| 3 | Sekcja 8.2 Conclusions + 5 wymiarów | Drafts kluczowy paragraph negative-result framing + 5 RQ direct answers | Reviews defensibility |
| 4 | Sekcja 8.3 Limitations 4 kategorie | Drafts dataset/model/eval/external validity explicit | Reviews honesty |
| 5 | Sekcja 8.4 Future work | Drafts 4-5 directions z technical grounding | Reviews realism |
| 6 | Sekcja 8.5 Final coherence | Drafts checklist + verification | Reviews completeness |
| 7 | Citation pass | `/citations` (R2 references) | Reviews findings |
| 8 | Writing rules check | Style audit (especially descriptive style, NIE szafowanie progami) | Final read-through |

## 5. Co musimy znaleźć / przygotować

### Pre-conditions
- R1-R7 drafted z konkretnymi wynikami
- 5 RQ answered (positive lub negative) z R7
- 5 świadomych biases z R3 (sources_catalog.md)
- Drift simulation results z R7.4
- Cross-register results z R7.5

### Artefakty
- Brak nowych figur/tabel zazwyczaj (R8 to narrative synthesis)
- **Opcjonalnie Tabela 8.1**: final mapping 5 RQ → 5 wymiarów kontrybucji → status

## 6. Writing rules application

- Reguła 1 classic structure: 5 podsekcji per Task 08 + A12
- Reguła 3 **academic style**: especially descriptive (NIE szafowanie progami) w 8.2 i 8.3
- Brak nowych cytacji zazwyczaj (R8 referuje do R2)

## 7. Defense scaffolding application

**Wszystkie 3 mikro-podszepty W R8 — ostatnia okazja:**

1. **Ablations A1-A4** wyniki summarized w 8.1 + reference do R7
2. **Kategoryczna error analysis** wzorce summarized w 8.2 (jako insight)
3. **5-wymiarowa kontrybucja** = **central w 8.2** ← KLUCZOWE — paragraph explicit z negative-result framing

## 8. Acceptance checklist

- [ ] 5 podsekcji (summary + conclusions + limitations + future work + coherence checklist)
- [ ] 5 RQ direct answers w 8.2 z explicit status (supported/partial/rejected)
- [ ] **5-wymiarowa kontrybucja explicit paragraph** w 8.2 z negative-result framing
- [ ] 4 kategorie limitations explicit (dataset/model/eval/external)
- [ ] 4-5 future work directions z technical grounding (NIE speculative)
- [ ] Coherence checklist completed
- [ ] Length ~500-800 słów (R8 zazwyczaj krótszy niż R1/R5/R7)

## 9. Risks / common pitfalls

- ❌ Repetition wyników z R7 → R8 syntetyzuje, NIE powtarza tabel
- ❌ Inflated claims novelty → balanced; *„pierwsza publiczna PL methodology"* OK, *„groundbreaking"* NIE
- ❌ Brak limitations → Task 08 + A12 **mandatory**, niespełnienie = obniżona ocena
- ❌ Future work jako *„completely new research"* → musi derive z naszych identyfikowanych limitations
- ❌ **Brak 5-wymiarowej kontrybucji explicit** → tracimy Defense scaffolding shield dla negative-result scenarios
- ❌ Inflation magnitude wyników → balance jeśli H1 partial/rejected, narrative powinno odzwierciedlać
