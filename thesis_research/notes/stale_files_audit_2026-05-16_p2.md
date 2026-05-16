# Stale files audit P2 (post-T1 PASS + v0.6 dataset)

**Data:** 2026-05-16 (evening, after Wariant B cleanup + T1 PASS + v0.6 build)
**Cel:** Systematyczny audit + fix WSZYSTKICH stale references po:
1. DEC-003 pivot (już wcześniej updated, ale nie wszędzie)
2. Wariant B cleanup (17,862 → 11,000 chunks; 240 → 5,402 halu pairs)
3. T1 mDeBERTa NLI sanity PASS 80.6% (2026-05-16 11:55)
4. Dataset v0.6 build (post-fix factual_fabrication=NEUTRAL)
5. Pre-cleanup R3/R4/R5 drafts → archive

**Post-audit prawda (CURRENT TRUTH 2026-05-16 evening):**
- **Polish CitationBench v0.6** = 11,000 chunks + 5,402 halu pairs (balanced 5/5 typów)
- **3+1 RQ** (NIE 5): RQ1 probe AUROC ≥0.70 / RQ2 LLM-judge kappa ≥0.50 / RQ3 3-tier NLI ≥85% citation precision / RQ4 (supporting) Wallat 2 metric
- **POC status:** T1 PASS 80.6%; T2/T3/T4 pending lab GPU
- **Drafts:** PUSTY (post-Wariant B → `_archive/v3.2-pre-clean/drafts/`)

---

## Pliki z stale references (per scope per Magdy task)

### A) Stale dataset numbers (5,150 / 8,434 / 17,862 / v0.4 / v0.5)

| File | Stale refs found | Replace z |
|---|---|---|
| `D:\diplomma\SETUP.md` | line 202: "scraped data (~5,150 items)" | "v0.6 = 11,000 unified chunks + 5,402 halu pairs" |
| `D:\diplomma\main_project\notebooks\README.md` | line 7: "REAL EDA na 5,150 scrape'owanych rekordach" | "v0 EDA na initial 5,150 scrape (pre-cleanup)" + note v0.6 current |
| `D:\diplomma\thesis_research\02_konspekt_v3.2_skeleton.md` | line 24: "1.5B/3B dla probe" outdated; korpus table line 120: scraped ELI 2,123 chunks (correct as historical) — ALE brak update do final v0.6 | Add "Confirmed v0.6 (post-cleanup): 11,000 chunks + 5,402 halu pairs" |
| `D:\diplomma\thesis_research\PLAN_cele_i_kroki.md` | reference do "100 par" (old gold target before UOKiK 60+50-100 = 110-160) — partial OK; "1.5B/3B" probe target old (now Bielik 11B confirmed primary) | Update D1 default + Iter. 0b POC outputs |
| `D:\diplomma\thesis_research\decisions\DEC-004_iter0b_poc_results.md` | Dataset references "v0.5 (11,000 chunks + 5,402 halu pairs)" — ALE v0.6 jest current; T2/T3/T4 nadal placeholder | Update v0.5→v0.6; add explicit "T1 PASS DONE 2026-05-16; T2/T3/T4 pending lab GPU" |

### B) Stale RQ count (5 RQ → 3+1)

| File | Stale refs found | Replace z |
|---|---|---|
| `D:\diplomma\CLAUDE.md` | line 27: "3 main + 2 supporting, NIE 5" — claims 3+2 ALE only RQ4 listed (no RQ5). Inconsistent. | "3 main + 1 supporting" + corresponds to current scope (drop RQ5 explicit) |
| `D:\diplomma\CLAUDE.md` | line 110: "RQ1-RQ5 (3 main + 2 supporting)" w mapping | "RQ1-RQ4 (3 main + 1 supporting)" |
| `D:\diplomma\CLAUDE.md` | line 117: "synteza RQ1-RQ4" — IS already correct! ALE mapping outside konspekt v3.2 RQ count | Confirm RQ4 supporting only; remove RQ5 implicit references |
| `D:\diplomma\thesis_research\02_konspekt_v3.2_skeleton.md` | line 80: "3 main + 2 supporting" — but only RQ4 listed; RQ5 deprecated explicit line 110 | Update line 80 → "3 main + 1 supporting" |

### C) Stale RQ thresholds (RQ1 ≥0.80 → ≥0.70 per DEC-003+D14 evidence)

| File | Stale refs found | Replace z |
|---|---|---|
| `D:\diplomma\CLAUDE.md` | line 30: "AUROC ≥0.80" RQ1; line 35: "≥75% agreement" RQ4 | RQ1 = AUROC ≥0.70 z bootstrap CI lower ≥0.60 (per D14 + Dubanowska EMNLP 2025) |
| `D:\diplomma\CLAUDE.md` | line 31: "≥85% precision" — split into Wallat faithfulness ≥85% + correctness ≥75% per RQ2 H2a/H2b | Update RQ2 to two-metric Wallat 2025 (H2a faithfulness, H2b correctness) |
| `D:\diplomma\CLAUDE.md` | line 35: "≥75% agreement" RQ4 | RQ4 (supporting): Wallat 2025 2-metric framework (faithfulness vs correctness) per task spec |
| `D:\diplomma\CLAUDE.md` | line 162: "AUROC <0.80" — old threshold | "AUROC <0.70 lub CI lower <0.60" |

### D) Stale references do drafts/

| File | Stale refs found | Replace z |
|---|---|---|
| `D:\diplomma\thesis_research\CLAUDE.md` | already correct (PUSTY noted) | Keep |
| `D:\diplomma\thesis_research\02_konspekt_v3.2_skeleton.md` | NIE referencuje drafts/ explicit | Add note "drafty PUSTE post-Wariant B → `_archive/v3.2-pre-clean/drafts/`" |
| `D:\diplomma\CLAUDE.md` | NIE referencuje drafts state | Add reference do drafts/ status (PUSTY post-Wariant B) |

### E) Stale stack mentions

| File | Stale refs found | Replace z |
|---|---|---|
| `D:\diplomma\CLAUDE.md` | line 74: "MoritzLaurer/mDeBERTa-...-2mil7" — correct; brak "T1 PASS confirmed 2026-05-16 80.6%" | Add T1 PASS confirmation note |
| `D:\diplomma\CLAUDE.md` | line 76: "Lynx 8B / 70B" listed; brak gliclass-multilang-ultra Tier 0 ablation | Add gliclass per nli_models_2026_update.md research output |
| `D:\diplomma\CLAUDE.md` | line 72: "Bielik 11B v3 jako probe target (primary, lab GPU SP7 H200; fallback 1.5B/3B dla local CPU dev)" — correct | Already correct |
| `D:\diplomma\thesis_research\PLAN_cele_i_kroki.md` | line 23: "Bielik (mały LLM 1.5B/3B)" — outdated, primary teraz 11B | Update to "Bielik 11B v3 primary (lab GPU); 1.5B/3B fallback local CPU dev" |
| `D:\diplomma\thesis_research\EXPLAINER_temat_dla_siebie.md` | line 65: "podsłuchujesz jego ostatnie 2-3 warstwy ukryte" — outdated (current = layer 47 per D10) | Update to "layer 47 (= ⌊0.95×50⌋) per Balcells et al. 2025" |
| `D:\diplomma\thesis_research\EXPLAINER_temat_dla_siebie.md` | line 80-83: "training data (1.5B/3B)" multiple mentions; line 130: "1.5B/3B" | Update to Bielik 11B v3 primary + 1.5B/3B fallback |
| `D:\diplomma\thesis_research\EXPLAINER_temat_dla_siebie.md` | line 142: "mDeBERTa NLI fine-tuned (lub HerBERT-large NLI custom fine-tune)" — wrong: mDeBERTa frozen Tier 1 PASS, NIE fine-tuned | Update to "mDeBERTa frozen Tier 1 PASS 80.6% (2026-05-16 sanity check; Tier 2 HerBERT custom fine-tune NIE wymagany)" |

### F) Stale farma / ChPL / reranker / 5RQ references

| File | Stale refs found | Replace z |
|---|---|---|
| `D:\diplomma\thesis_elements\CLAUDE.md` | line 4: "pipeline MLOps retrainingu rerankera dla polskojęzycznego RAG (psychiatria)" — outdated v3.0 | Update do v3.2 halu detection + consumer rights |
| `D:\diplomma\thesis_elements\CLAUDE.md` | line 21-25: chapter table mentions "rerankery + drift", "psychiatria", "sources_catalog" v3.1 paths | Update to v3.2 (halu detection + consumer rights, Bielik probe, citation grounding) |
| `D:\diplomma\thesis_elements\CLAUDE.md` | line 43: "Farmakologia jako domena, psychiatryczny eval" — v3.1 historical | Update to "polish consumer rights jako domena, ISAP/UOKiK/Reddit jako sources" |
| `D:\diplomma\thesis_elements\CLAUDE.md` | line 175-220: defense scaffolding 5 wymiarów farma + RQ5 cross-register + reranker | Update to v3.2: probe + verifier + citation alignment + 3 publishable HF artefakty + 5-wymiarowa kontrybucja per current konspekt |
| `D:\diplomma\thesis_elements\CLAUDE.md` | line 184-189: ablations A0-A4 dla rerankera (PLLuM, ATC psych) | Update to v3.2 ablations A0-A4 (probe target size, semantic entropy, mDeBERTa vs HerBERT vs LLM-judge, post-hoc vs generation-time) |
| `D:\diplomma\thesis_elements\CLAUDE.md` | line 195-200: error analysis rerankera (Terminology miss, Register mismatch) | Update to halu types per RQ1 (factual fabrication / entity confusion / temporal drift / negation flip / paragraph mis-citation / ambiguous claim) |
| `D:\diplomma\main_project\CLAUDE.md` | line 4: "pipeline MLOps retrainingu rerankera dla polskojęzycznego RAG (psychiatria)" — outdated v3.0 | Update do v3.2 halu detection pipeline (probe + verifier + citation alignment dla consumer rights) |
| `D:\diplomma\main_project\CLAUDE.md` | line 22-39: layout zawiera `reranker/`, `judge/`, `eval/` (ATC, ChPL, PLLuM mentions) | Update to v3.2 layout (`halu/`, `probe/`, `verifier/`, `citation/`, `scrape/{isap,uokik,reddit,legal_fora}/`) |
| `D:\diplomma\main_project\CLAUDE.md` | line 28: "ingest/ # corpus scraping (PTP, AOTMiT, URPL, IPiN)" | Update to "scrape/{isap,uokik,reddit,legal_fora}/ # consumer rights corpus" |
| `D:\diplomma\main_project\CLAUDE.md` | line 30: "embed/ # BGE-M3 wrapper (frozen)" — OK | Keep |
| `D:\diplomma\main_project\CLAUDE.md` | line 31: "reranker/ # polish-reranker-roberta-v3 fine-tuning" | Update to "probe/ # hidden-states halu probe (PyTorch hooks Bielik layer 47)" |
| `D:\diplomma\main_project\CLAUDE.md` | line 32: "judge/ # PLLuM-12B-instruct" | Update to "verifier/ # 3-tier NLI: mDeBERTa primary + HerBERT fallback + LLM judge ablation" |

### G) POC status placeholder

| File | Stale refs found | Replace z |
|---|---|---|
| `D:\diplomma\thesis_research\decisions\DEC-004_iter0b_poc_results.md` | linia 2: "Data: TBD"; status "TEMPLATE" — ALE T1 PASS jest już done | Update: Data 2026-05-16 (T1 done, reszta pending lab); Status: "PARTIAL — T1 PASS 80.6%; T2/T3/T4 pending lab GPU" |
| `D:\diplomma\thesis_research\PLAN_cele_i_kroki.md` | Iter. 0b checkpoint section — pending POC results sign-off | Update to reflect T1 PASS confirmation + remaining T2/T3/T4 wymaga lab GPU |

### H) Drafts state mentions

| File | Stale refs found | Replace z |
|---|---|---|
| `D:\diplomma\thesis_research\CLAUDE.md` | already correct - drafts PUSTY noted post-Wariant B | Keep |
| `D:\diplomma\thesis_elements\CLAUDE.md` | references do `02b_konspekt_v3_updates.md` (v3.1 archived path) | Update to `02_konspekt_v3.2_skeleton.md` |

---

## D1-D15 decisions list update plan

`PLAN_cele_i_kroki.md` § 4 has D1-D15. Status check:

| # | Status | Action |
|---|---|---|
| D1 | Probe target Bielik 11B v3 — confirmed primary | Update note "CONFIRMED 2026-05-16 (DEC-004 T3 pending lab GPU verify)" |
| D2 | mDeBERTa Tier 1 vs HerBERT Tier 2 | Update note "T1 PASS 80.6% 2026-05-16 — Tier 2 HerBERT NIE potrzebny TERAZ" |
| D3 | 5 typów halu | OK, keep |
| D4 | Reddit Pushshift / e-prawnik / forumprawne | OK, scrape DONE |
| D5 | Drift simulation type | Pending Iter. 5 |
| D6 | Citation post-hoc / generation-time | Pending Iter. 4 |
| D7 | Probe linear vs MLP | Pending Iter. 2 |
| D8 | Outlines vs xgrammar vs Instructor | Pending T2 lab GPU |
| D9 | Lab GPU H100/A100 | Pending T4 lab GPU verify |
| D10 | Layer 47 init | OK, confirmed plan |
| D11 | PyTorch hooks | OK, confirmed plan |
| D14 | RQ1/H1 threshold ≥0.70 | OK, current (per DEC-003) |
| D15 | obalcells fork | OK, plan |
| D12 | Bonus cross-model | OK, optional |
| D13 | Polish diakrytyki Outlines | Pending T2 lab GPU |

---

## Apply order (per Magdy budget time)

1. **D:\diplomma\CLAUDE.md** — root, most-read; fix RQ count + thresholds + stack notes (T1 PASS confirm + drafts state)
2. **D:\diplomma\thesis_research\02_konspekt_v3.2_skeleton.md** — RQ count fix + dataset numbers final + drafts state
3. **D:\diplomma\thesis_research\decisions\DEC-004_iter0b_poc_results.md** — Status PARTIAL + Data 2026-05-16 + dataset v0.5→v0.6 + Wariant A/B/C unchanged
4. **D:\diplomma\thesis_research\PLAN_cele_i_kroki.md** — D1+D2 status update + Iter. 0b POC results checkpoint update + probe target 11B primary
5. **D:\diplomma\thesis_research\EXPLAINER_temat_dla_siebie.md** — probe layer 47 + Bielik 11B primary + mDeBERTa frozen NIE fine-tuned + 1.5B/3B = fallback
6. **D:\diplomma\SETUP.md** — dataset path v0.6 + scraped data note v0.6 stats + read order include DEC-004
7. **D:\diplomma\main_project\notebooks\README.md** — clarify v0 = initial 5,150 (pre-cleanup); v0.6 current dataset
8. **D:\diplomma\main_project\CLAUDE.md** — full rewrite section "Stack pinning" plus "Planowany layout" v3.2 (halu/, probe/, verifier/, citation/, scrape/)
9. **D:\diplomma\thesis_elements\CLAUDE.md** — full rewrite chapter table + writing rules + defense scaffolding (5 wymiarów v3.2, halu types, ablations A0-A4 v3.2)

---

## NIE update (per task constraints)

- `_archive/*` — historical (audit trail)
- `notes/KRYTYCZNA_ocena_*` — already current
- `notes/scope_cleanup_decisions_*` — already current
- `notes/sources_z_v3.1_do_reuse_w_v3.2.md` — already current
- `research/*.md` — historical research outputs (each dated)
- `decisions/DEC-003_*.md` — immutable post sign-off (already updated header)
- `iter0b_poc/t*.py` — already current

---

## Final summary

**12 plików zmodyfikowanych** (9 audited per task + 1 typo fix DATASET_CARD + 2 slash commands found in cross-audit):

1. `D:\diplomma\CLAUDE.md` — RQ count 3+2→3+1, threshold ≥0.80→≥0.70 + bootstrap CI, RQ2 split into Wallat 2-metric H2a/H2b, korpus table → v0.6 (11,000 + 5,402), stack notes T1 PASS confirmed + gliclass Tier 0 ablation, DEC-004 added to log, drafts state PUSTY post-Wariant B
2. `D:\diplomma\thesis_research\02_konspekt_v3.2_skeleton.md` — header v3.2 evening + DEC-004 link, RQ count 3+2→3+1 + RQ5 deprecated note, korpus II.4.1 → v0.6 final stats, Tier 1 mDeBERTa T1 PASS 80.6% confirmed, Tier 2 reserved (NIE wymagany), Models table II.6 updated z confirmation/pending status, Iter. 0b status PARTIAL DONE
3. `D:\diplomma\thesis_research\decisions\DEC-004_iter0b_poc_results.md` — Status TEMPLATE → PARTIAL, Data TBD → 2026-05-16, dataset v0.5 → v0.6 + halu_injector fix note
4. `D:\diplomma\thesis_research\PLAN_cele_i_kroki.md` — header post-Wariant B + DEC-004 link, cele szczegółowe (probe target 11B + dataset v0.6 DONE + 3-tier confirmed), Iter. 0b checkpoints → DONE/PARTIAL with explicit lab GPU pending list, D1+D2 status update
5. `D:\diplomma\thesis_research\EXPLAINER_temat_dla_siebie.md` — header evening, probe layer 47 (Bielik 11B v3 not "ostatnie 2-3 warstwy"), 1.5B/3B → fallback only, mDeBERTa frozen NOT fine-tuned + T1 PASS confirmed, dataset corpus → v0.6 table replacing target estimates, limitations + fallback updated to current state
6. `D:\diplomma\SETUP.md` — header evening + Iter. 1 mention, dataset section lists v0.1-v0.6 with v0.6 marked CURRENT + counts, build command --version v0.6 --filter-policy strict, POC status section reflects T1 PASS + T2/T3/T4 pending, read order extended (DEC-004 + notes + DATASET_CARD), migration section v0.6 stats
7. `D:\diplomma\main_project\notebooks\README.md` — clarify EDA na 5,150 = pre-cleanup historical snapshot; v0.6 jako current; future notebooks updated
8. `D:\diplomma\main_project\CLAUDE.md` — **FULL REWRITE** (was v3.0 era reranker+psychiatria+ATC+ChPL+PLLuM): teraz v3.2 layout (halu/, probe/, verifier/, citation/, scrape/{isap,uokik,reddit,legal_fora}/) + iter0b_poc/ + data/processed/citationbench_v0.6_*/, anti-pattern dla farma/ChPL/reranker
9. `D:\diplomma\thesis_elements\CLAUDE.md` — **FULL REWRITE** (was v3.0 era farma+psychiatria+ChPL eval+reranker+ATC ablations PLLuM): teraz v3.2 chapter table + workflow rozdziału + ablations A0-A4 v3.2 (probe target / semantic entropy / mDeBERTa-vs-LLM / generation-time citation) + halu types 6-poziomowa + 5-wymiarowa kontrybucja v3.2 (probe + dataset + verifier + Gradio + methodology)
10. `D:\diplomma\main_project\data\processed\citationbench_v0.6_2026-05-16\DATASET_CARD.md` — typo fix `vv0.6` → `v0.6`
11. `D:\diplomma\.claude\commands\validate.md` — Pre-check sekcja: "farmakologia (psych jako eval subset), aktywne 5 RQ (RQ5 = cross-register ChPL↔Ulotka)" → "polish consumer rights + 3 main + 1 supporting RQ + DEC-003+DEC-004 references"; alternatywa cite source `02_konspekt_v3.2_skeleton.md`; reranker/farma/ChPL flag w scope creep
12. `D:\diplomma\.claude\commands\chapter.md` — Mapowanie table (v3.0 era farma+psychiatria+reranker → v3.2 halu detection chapter map); Read relevant context order updated do `02_konspekt_v3.2_skeleton.md` + DEC-003 + DEC-004 + notes/scope_cleanup + research outputs zamiast v3.0 paths (`02b_konspekt_v3_updates`, `02_konspekt_v3_FINAL.docx`, `sources_catalog.md`, `DEC-001` + `DEC-002`)

### Lint check verdict

`uv run ruff check main_project/src/halu/` — 16 errors (RUF022, RUF005, E501, RUF001) **wszystkie pre-existing** w source code (nie zmienianym przez ten audit). Tree clean per `git status main_project/src/halu/`.

### Top 5 najważniejszych fixes

1. **Konspekt + CLAUDE.md: RQ count 3+2 → 3+1** — krytyczna spójność (v3.2 ma RQ1+RQ2+RQ3 main + RQ4 supporting; RQ5 deprecated)
2. **CLAUDE.md: RQ1 threshold 0.80 → 0.70 z bootstrap CI** — per DEC-003 D14 + Dubanowska EMNLP 2025; mismatched do 2 miesięcy
3. **`thesis_elements/CLAUDE.md`: full rewrite z v3.0 (farma+reranker+psych+PLLuM+ATC) na v3.2** — najwięcej stale references; chapter table + ablations + defense scaffolding wszystko obrane v3.2
4. **`main_project/CLAUDE.md`: full rewrite z v3.0 reranker layout (PTP/AOTMiT/URPL/IPiN ingest, reranker/, judge/) na v3.2 layout** (halu/, probe/, verifier/, citation/, scrape/{isap,uokik,reddit,legal_fora}/) + anti-pattern explicit dla farma/ChPL/reranker
5. **Dataset numbers stale across 7 files: 5,150/2,123 hist → v0.6 = 11,000 + 5,402** + court_judgment 597 → 534 (real per file count)

### Flagged dla Magdy review (decision-grade)

**Brak** — wszystkie zmiany były factual stale-fix-y (RQ count z konspektu już active, threshold z DEC-003 już active, dataset numbers z DATASET_CARD już built, T1 PASS z DEC-004 już zaakceptowany). Żadne zmiany scope/strategy. Magda powinna sprawdzić przy okazji:
- czy rewrite `main_project/CLAUDE.md` dobrze opisuje aktualny layout (sprawdziłam `ls src/halu/` ale nie wszystkie subkatalogi probe/verifier/citation są jeszcze utworzone — to scaffolding plan)
- czy rewrite `thesis_elements/CLAUDE.md` chapter table treść per rozdział OK (mój 1-line per rozdz. przedstawia v3.2 scope)



