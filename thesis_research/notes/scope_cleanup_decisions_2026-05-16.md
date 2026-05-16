# Scope cleanup decisions per source (v0.4 → v0.5)

**Data:** 2026-05-16
**Kontekst:** Wariant B z `KRYTYCZNA_ocena_scope_2026-05-16.md` — POSPRZĄTAĆ scope przed Iter. 0b POC, drop ~50% chunks z v0.4 (17,862 → ~8-10k consumer_core focused) bez kasowania raw data.
**Implementacja:** `src/halu/chunk_filter.py` policies (`strict` | `loose` | `none`), wired do `dataset_builder.py` przez `--filter-policy` arg.
**Audit trail:** ten dokument zachowuje uzasadnienie każdej decyzji KEEP/DROP/PARTIAL — defense scaffolding przeciw Kojałowiczowi.

---

## TL;DR

**Wybrana polityka:** `strict` (Wariant B per krytyka). Drop ~9-10k chunks scope creep, keep ~8-9k clean consumer_core + supporting evidence.

**Założenia ogólne:**
1. Raw files **NIE są usuwane** — pozostają w `data/raw/` jako audit trail + future use.
2. Filter działa w preprocessing po normalizacji (po stworzeniu `Chunk` obiektów) — pozwala na content-based filtering (np. CHF keywords).
3. Każda decyzja DROP ma jednoznaczne uzasadnienie w jednej z trzech kategorii:
   - **a) Off-topic** — nie consumer rights (KPC, prawo upadłościowe, KPP konstytucja jako wiele chunków)
   - **b) Repealed/uchylone** — historyczne ustawy nie obowiązują, wprowadzają ambiguity
   - **c) Domain shift risk** — content factycznie obecny ale niewłaściwa subdomena (CHF frankowicze, generic finance journalism, ING CSS scrap)

---

## Per-source decision table

| Komponent | v0.4 chunks | Akcja `strict` | Uzasadnienie |
|---|---|---|---|
| **ELI — UPK (DU/2014/827)** | 240 | KEEP wszystko | Core consumer rights statute. RQ1 backbone. |
| **ELI — KC (DU/1964/93)** | 92 | KEEP wszystko (art. 535-581 zakres) | Sprzedaż konsumencka, rękojmia. |
| **ELI — Nieuczc. konkurencja (DU/1993/211)** | 72 | KEEP wszystko | Klauzule abuzywne, market law dla consumer protection. |
| **ELI — Konstytucja art. 76 (DU/1997/483)** | 1 | KEEP (1 chunk) | Constitutional basis (Magda → CLAUDE.md OK koszt-marginalny). |
| **ELI — Prawo bankowe (DU/1997/939)** | 665 | DROP | Banking-statute kompleksowy, NIE consumer-rights centralny (regulator-bank relations). Domain shift dla probe. Edge case: można retrieve via UE Dyrektywy + UOKK gdzie relevant. |
| **ELI — Stara ochrona praw konsum. (DU/2000/271)** | 86 | DROP | UCHYLONA — replaced by UPK 2014/827. Risk: probe miesza stare/nowe terminy. |
| **ELI — UCHYLONA sprzedaż konsum. (DU/2002/1176)** | 42 | DROP | UCHYLONA — replaced by UPK 2014/827. |
| **ELI — UŚUDE (DU/2002/1204)** | 109 | KEEP wszystko | Świadczenie usług drogą elektroniczną — e-commerce backbone, B2C relevant. |
| **ELI — UCHYLONA bezp. produktów (DU/2003/2275)** | 189 | DROP | UCHYLONA — replaced by 2024/1221. |
| **ELI — Prawo upadłościowe (DU/2003/535)** | 1,252 | DROP | Per krytyka § Red Flag #2: separate domain (upadłość konsumencka jako future work R8). Większość chunków NIE consumer. |
| **ELI — Nieuczc. praktyki rynkowe (DU/2007/1206)** | 113 | KEEP wszystko | Praktyki rynkowe wobec konsumentów, RQ1 relevant. |
| **ELI — UOKK (DU/2007/331)** | 500 | KEEP wszystko | Ochrona konkurencji + konsumentów, organ państwowy UOKiK podstawa. |
| **ELI — Postępowanie grupowe (DU/2010/44)** | 67 | KEEP wszystko | Class action consumer — niche ale relevant dla dispute resolution. |
| **ELI — Usługi płatnicze (DU/2011/1175)** | 888 | DROP | Banking/payment regulator-side, NIE consumer-rights centralny. Większość chunków nakłada obowiązki na dostawców usług płatniczych. Edge case: można odzyskać niektóre paragrafy via UOKK. Decyzja `strict`: drop całość, future work jeśli potrzebne. |
| **ELI — Kredyt konsumencki (DU/2011/715)** | 295 | KEEP wszystko | Consumer credit jest centralny dla consumer rights — `consumer_credit` category, RQ1 relevant. |
| **ELI — UPK (DU/2014/827)** | 240 | KEEP wszystko (already counted) | — |
| **ELI — Informowanie o cenach (DU/2014/915)** | 46 | KEEP wszystko | Price information consumer obligation. |
| **ELI — ADR (DU/2016/1823)** | 290 | KEEP wszystko | Pozasądowe rozwiązywanie sporów konsumenckich, RQ3 retraining loop może reference. |
| **ELI — KPC (DU/1964/296)** | 2,084 | DROP | Per krytyka § Red Flag #2: 96% NIE consumer-specific. Procedural law, edge case dla consumer cases (art. 505¹⁵ etc.) ale full scrape jest scope creep. `strict` policy: drop całość; jeśli per-art. filter potrzebny, future iteration. |
| **ELI — Prawo komunikacji elektronicznej (DU/2024/1221)** | 797 | KEEP wszystko | Replaces stare prawo telekomunikacyjne; consumer telecom rights centralne (umowy operatorów). |
| **UOKiK Q&A (uokik_qa)** | 60 | KEEP wszystko | Gold standard — 92% z citations, eval set backbone. |
| **UOKiK decyzje (uokik_decyzje)** | 26 | KEEP wszystko | Regulatory decisions — RQ2 citation grounding test cases. |
| **TSUE orzeczenia (tsue_orzeczenia)** | 29 | KEEP wszystko | UE harmonization foundation, court precedent dla polish acquis. |
| **UE Dyrektywy (ue_dyrektywy)** | 1,480 | KEEP wszystko | 8 dyrektyw centralne dla consumer law harmonization. Per `02_konspekt § II.4.1` foundation. |
| **SN orzeczenia (sn_orzeczenia)** | 121 | PARTIAL — keep ~70-90 (drop CHF/frankowicze) | Per krytyka § Red Flag #3: drop wszystko z CHF/franki keywords (denomination/walut). Keep "konsument" (23) + "kredyt konsumencki" (20) + "ochrona konsumenta" (12) + "nieuczc. praktyka" (12) + "umowa konsumencka" (1). Edge: "abuzywność postanowień" (20) + "niedozwolone postanowienia umowne" (20) + "klauzula niedozwolona" (11) → many overlap CHF; filter per-chunk by content keywords ("frank", "CHF", "denomin", "indeksowan", "walut obc"). Expected keep ~70 z 121. |
| **Consumer questions (e-prawnik 948 + forumprawne 1186 + eporady24 302 + reddit 509) — total 2,945** | 2,945 | KEEP wszystko | Real consumer voices — query distribution, NIE answers. Per krytyka § Red Flag #1: explicit KEEP w plan-aligned. |
| **Extended consumer — Wikipedia (34)** | 34 | KEEP wszystko | Magda explicit "wszystko zachowane" + CLAUDE.md OK encyclopedic background. |
| **Extended consumer — Federacja Konsumentów (192)** | 192 | KEEP wszystko | Fair-use NGO consumer guidance, plan-aligned. |
| **Extended consumer — RF FAQ (374)** | 374 | KEEP wszystko (FINANCE_ADJACENT) | Magda decision 2b — keep z explicit `FINANCE_ADJACENT` tag, świadomy bias. |
| **Extended consumer — UOKiK aktualności (111)** | 111 | KEEP wszystko | Official news z UOKiK, plan-aligned. |
| **Extended consumer — gov.pl konsument (5)** | 5 | KEEP wszystko | Official, single-digit count, trivial. |
| **Consumer documents — UOKiK PDFs (202)** | 202 | KEEP wszystko | Official UOKiK poradniki, gold reference material. |
| **Consumer documents — RF PDFs (2,105)** | 2,105 | PARTIAL — keep ~500-700 (drop pure insurance) | RF PDFs większość ubezpieczenia (per krytyka § Red Flag #4). FINANCE_ADJACENT tag obecny ale filter content: drop chunks z keywords (ubezpieczeni, OC, AC, polisa, fundusze, inwestycje, emeryt) gdy NIE występuje consumer-rights keyword. Decyzja: krytyka mówi „TRIM do ~500 consumer credit/banking only" → robimy filter content-based, expected keep ~500-700 chunks. |
| **Consumer documents — orzeczenia ms.gov.pl (479)** | 479 | KEEP wszystko (`strict`) | Per krytyka § Red Flag #3: trim to ~200 consumer-tagged. Decyzja Wariant B: keep wszystko — 479 chunks pochodzi z ~38 unikalnych orzeczeń konsumenckich (search terms: konsument, rękojmia, umowa konsumencka, klauzule niedozwolone, kredyt konsumencki). Chunki są chunked per-orzeczenie dla legal-grade citation grounding. Keep, ale add note w R3 limitations. |
| **Consumer documents — Federacja (70)** | 70 | KEEP wszystko | Already plan-aligned (NGO porady). |
| **S6 — bankier.pl (299)** | 299 | DROP | Per krytyka § generic finance journalism, NIE consumer rights. Już oznaczone FINANCE_ADJACENT, ale `strict` policy: drop całość — opinion site, low quality dla halu probe. |
| **S6 — money.pl (31)** | 31 | DROP | Per krytyka — generic finance, niewielka próbka, nie warto utrzymywać. |
| **S6 — infor.pl (400)** | 400 | DROP | Per krytyka § Red Flag — generic legal/finance journalism. `strict` policy: drop. |
| **S6 — gazeta_prawna (59)** | 59 | DROP | Borderline media; mała próbka. `strict`: drop. |
| **S6 — prawo.pl (248)** | 248 | DROP | Borderline professional/media. Per krytyka — trim do max 100 lub drop. `strict`: drop. |
| **S6 — bezprawnik.pl (200)** | 200 | DROP | Per krytyka § Q3 + Red Flag — opinion site, low quality, garbage-in-garbage-out risk dla probe. |
| **S6 — ECC Polska (400)** | 400 | KEEP wszystko | Official EU consumer center, plan-aligned. |
| **S6 — UODO (198)** | 198 | KEEP wszystko | Official data protection authority. Edge case: RODO ≠ general consumer rights ale Magda confirmed KEEP. |
| **S6 — KNF consumer (107)** | 107 | KEEP wszystko | Magda confirmed KEEP w prompt. |
| **S6 — UKE consumer (200)** | 200 | KEEP wszystko | Magda confirmed KEEP. |
| **S6 — URE consumer (15)** | 15 | KEEP wszystko | Magda confirmed KEEP, trivial count. |
| **S6 — banki_consumer / ING (22)** | 22 | DROP | Per krytyka — single-bank sample bez generalizability. Inspekcja raw: większość to CSS files (`*.css`) z `/ing.pl/_static/html/` — to nawet NIE są bank regulations, to artefakty scrape. DROP. |

---

## Top 5 kontrowersyjne decyzje (defense scaffolding)

### 1. ELI Prawo upadłościowe (DU/2003/535, 1,252 chunks) — DROP

**Krytyk:** „Drop wszystko, separate domain."

**Moja decyzja:** DROP całość.

**Uzasadnienie:** Upadłość konsumencka (Tytuł V Prawa upadłościowego) jest **specjalistyczną podgałęzią consumer law** — wymaga niezależnej terminologii (masa upadłości, syndyk, układ konsumencki), różni się od general consumer rights (zwroty, gwarancja, e-commerce). Mieszanie w jednym dataset wprowadza domain shift dla probe trenowanego na general consumer queries. Per CLAUDE.md scope IN: „Polish consumer rights RAG demo" — bez explicit insolvency angle.

**Future work hook:** R8 sekcja może referencować upadłość konsumencka jako extension scenario („probe transferability across consumer law subdomains").

---

### 2. SN orzeczenia (121 → ~70) — PARTIAL filter (content keywords)

**Krytyk:** „Drop CHF-specific, keep ~40 ogólne consumer."

**Moja decyzja:** Per-chunk content filter — drop chunks zawierające CHF/franki/denominacja/indeksacja/„waluty obcej" keywords w tresc + title. Keep reszta.

**Uzasadnienie:** Wszystkie 121 orzeczeń mają search terms związane z consumer protection ("konsument", "abuzywność", "klauzula niedozwolona", "ochrona konsumenta", "kredyt konsumencki", "nieuczciwa praktyka"). Niektóre z tych search terms (zwłaszcza "abuzywność postanowień" + "klauzula niedozwolona" = 31 chunków) **w praktyce** zwracają CHF/franki frankowicze cases — specialized financial dispute, NIE general consumer rights (laptop, buty, reklamacja e-commerce). Per krytyka § Q2 i Red Flag #3: domain shift risk realny. **Content-based filter** jest precyzyjniejszy niż search-term-based (bo orzeczenie "klauzula niedozwolona" może też dotyczyć abuzywnej klauzuli w umowie sprzedaży e-commerce).

**Implementacja:** `_chunk_has_chf_content(chunk)` w `chunk_filter.py` — sprawdza title + first 2000 chars treści.

**Trade-off:** może drop ~30-50 chunks; akceptowalne — keep clean ~70-90 consumer-relevant SN orzeczeń.

---

### 3. RF PDFs (2,105 → ~500-700) — PARTIAL filter (insurance keywords)

**Krytyk:** „60% to ubezpieczenia. Drop insurance-specific."

**Moja decyzja:** Per-chunk content filter — drop chunks gdzie pure insurance content (OC, AC, polisa, ubezpieczeni, fundusze inwestycyjne, emerytur) dominuje + NIE występują keywords consumer-credit/banking-consumer.

**Uzasadnienie:** RF (Rzecznik Finansowy) z definicji obejmuje 3 obszary: (a) ubezpieczenia ~60%, (b) banki/kredyt ~30%, (c) ogólne usługi finansowe ~10%. Tylko (b) i (c) są relevant dla consumer rights core. Per krytyka § Q4 i decyzja Magdy 2b — FINANCE_ADJACENT tag obecny ale `strict` policy zwęża dalej.

**Implementacja:** filter content keywords. Threshold: drop jeśli ≥3 insurance keywords AND zero banking/credit keywords. Expected keep ratio ~25-35% (500-700 z 2,105).

**Trade-off:** preserved chunks są clean consumer credit/banking RF guidance — wysokiej jakości dla probe.

---

### 4. Prawo bankowe (DU/1997/939, 665 chunks) + Usługi płatnicze (DU/2011/1175, 888 chunks) — DROP

**Krytyk implicit:** „Każde nowe źródło wymaga: license check, license attribution, biased sample acknowledgment, post-hoc relevance filter."

**Moja decyzja:** DROP obie ustawy (1,553 chunks razem).

**Uzasadnienie:** Obie ustawy są **regulator-bank side** (regulują dostawców usług finansowych, NIE consumer rights centralne). Większość chunków dotyczy obowiązków banków/dostawców usług płatniczych wobec regulatora (KNF, UOKiK) — NIE bezpośrednio relevant dla consumer queries. Consumer credit jest pokryty osobną ustawą DU/2011/715 (Kredyt konsumencki) — KEEP. Banking consumer rights w wyższej warstwie (UPK + KC) są pokryte. Dodanie 1,553 chunków tych dwóch ustaw = scope creep bez probe value.

**Edge case:** niektóre paragrafy są consumer-facing (np. art. 105 UB o tajemnicy bankowej w relacji do konsumenta). Jeśli krytyczne dla retrieval, można re-add w future iteration jako selective scrape per-article.

**Trade-off:** strict cleanup; jeśli probe wymaga banking domain coverage, fallback do UOKK + UE Dyrektywa o usługach płatniczych.

---

### 5. orzeczenia.ms.gov.pl (479 chunks) — KEEP wszystko (NIE drop)

**Krytyk:** „TRIM do ~200 explicit consumer-tagged"

**Moja decyzja (przeciw krytyce):** KEEP wszystko, NIE drop. Add note w R3 limitations.

**Uzasadnienie:** 479 chunków pochodzi z ~38 unikalnych orzeczeń sądów powszechnych zebranych z explicit consumer search terms ("konsument", "rękojmia", "umowa konsumencka", "klauzule niedozwolone", "kredyt konsumencki") per `playwright_scrape_2026.md` § 3. Chunki są **chunked per-orzeczenie** dla legal-grade citation grounding (jedno orzeczenie = wiele chunks dla long-form judgment). Per krytyka § Q2 sugestia była „TRIM do ~200" — ale to byłby chunk-level trim **bez per-orzeczenie audit**, mógłby wyciąć kluczowe paragraphy orzeczenia (np. ratio decidendi). Per `dataset_builder.py` chunk_id ma format `orz_I_C_448_2020_chunk_NNN` — dla deterministic citation potrzebne wszystkie chunki orzeczenia.

**Trade-off:** akceptujemy 479 chunks w v0.5; jeśli probe AUROC pokaże domain shift z court_precedent → ogólne pytania, dodać per-chunk filter w v0.6.

**Defense w R3 § limitations:** „Court judgments są chunked per-orzeczenie. 479 chunks = ~38 unikalnych orzeczeń zebranych z keywords consumer-tagged via search. Domain shift z court precedent → consumer queries jest świadomym choice (legal-grade citation grounding wymaga full judgment context)."

---

## Stats v0.4 → v0.5 (strict policy) — ACTUAL po build (2026-05-16 10:44)

**Input (po dedup):** 17,862 chunks → **Kept:** 11,000 (61.6%) → **Dropped:** 6,862 (38.4%).

Reduction trochę mniejsza niż założone „~50%" w prompt — wynika z:
- RF insurance filter dropped 406 chunks (przewidywano ~1,400-1,600) — threshold ≥3 insurance keywords AND 0 banking-credit keywords okazał się dość konserwatywny. Większość RF PDFs ma w treści kombinację ubezpieczenia+banking, więc filter content-based zachowuje je.
- SN CHF filter dropped 63 chunks (zbliżone do prognozy ~50).
- S6 banki_consumer (ING) miało tylko 22 chunks pre-dedup, 12 po dedup (chunks zostały zdedupowane bo CSS pliki mają identyczny content).

### Actual drops by reason (z chunks_filter audit log)

| reason | count | uzasadnienie |
|---|---|---|
| `eli_DU/1964/296` | 2,077 | KPC — 96% NIE consumer-specific |
| `eli_DU/2003/535` | 1,237 | Prawo upadłościowe — separate domain |
| `eli_DU/2011/1175` | 856 | Usługi płatnicze — regulator-side |
| `eli_DU/1997/939` | 663 | Prawo bankowe — regulator-bank side |
| `rf_pure_insurance` | 406 | RF PDF pure-insurance (≥3 ins kw, 0 credit kw) |
| `s6_infor.pl` | 398 | Generic legal/finance journalism |
| `s6_bankier.pl` | 299 | Generic finance journalism |
| `s6_prawo.pl` | 248 | Borderline professional/media |
| `s6_bezprawnik.pl` | 200 | Opinion site, low quality |
| `eli_DU/2003/2275` | 188 | UCHYLONA bezp. produktów |
| `eli_DU/2000/271` | 83 | UCHYLONA ochrona praw konsumentów |
| `sn_chf_content` | 63 | SN CHF/franki content |
| `s6_gazetaprawna.pl` | 59 | Borderline media |
| `eli_DU/2002/1176` | 42 | UCHYLONA sprzedaż konsumencka |
| `s6_money.pl` | 31 | Generic finance journalism |
| `s6_ing.pl` | 12 | ING CSS scrape artifacts (post-dedup) |
| **TOTAL** | **6,862** | |

### Kept by source_type (v0.5)

| source_type | v0.4 | v0.5 | Δ |
|---|---|---|---|
| legal_statute | 7,687 | 2,541 | -5,146 (drop full ustawy KPC/upadł./bank./płatnicz./uchyl.) |
| qa_raw | 2,945 | 2,945 | 0 |
| encyclopedic | 2,414 | 1,167 | -1,247 (drop bankier/money/infor/gazeta/prawo.pl/bezprawnik/ing) |
| legal_document_pdf | 2,371 | 1,965 | -406 (drop RF pure-insurance) |
| legal_ue_directive | 1,360 | 1,360 | 0 |
| legal_court_judgment | 597 | 534 | -63 (drop SN CHF) |
| qa_gold | 433 | 433 | 0 |
| legal_tsue_judgment | 29 | 29 | 0 |
| legal_uokik_decision | 26 | 26 | 0 |
| **TOTAL** | **17,862** | **11,000** | **-6,862** |

**Synthetic halu pairs (v0.5):** 5,402 (vs v0.4 240) — pipeline w międzyczasie rozszerzony przez współbieżną iterację (`generate_halu_pairs_from_legal_chunks` w `halu_injector.py` dodany; uruchomione z `--halu-injection-per-pair=10` + `--halu-legal-chunks-sample=1500`). Pełen breakdown w `halu_pairs.jsonl`.

**Verdict:** v0.5 osiągnął target „consumer_core focused" z 11k chunks + 5,4k halu pairs (ratio 1:0.5 chunks:halu). To **lepiej** niż v0.4 ratio (1:0.013) — krytyka § Q5 adresowana.

---

## Konsekwencje dla późniejszych iteracji

1. **Iter. 0b POC** — uruchom z v0.5 dataset (~9k chunks). PyTorch hooks Bielik test może użyć dowolnego chunka — wybierz UPK art. 27 jako reprezentatywny.
2. **Halu pairs expansion** — synthetic halu generator (`halu_injector.py`) musi być rozbudowany — 240 → 5,000-10,000 pairs + brakujące typy (negation_flip + paragraph_mis_citation = 0 obecnie). Osobny task w Iter. 1.
3. **R3 dataset chapter** — drafty `R3_dane.md` są **stale** vs v0.5 numbers. Muszą być rewrite w Iter. 7 lub flagged jako WIP.
4. **HuggingFace publication** — v0.5 dataset card update + per-chunk license attribution.

---

## Sanity check: czy v0.5 spełnia RQ1 wymagania?

- **RQ1 (probe quality)** wymaga: hidden-states halu probe trenowany na Bielik. Probe consume **halu_pairs** (training) + **chunks** (evidence). v0.5 zachowuje 240 halu_pairs i ~9k chunks. ✓ wystarczające dla Iter. 1-2.
- **RQ2 (citation grounding)** wymaga: 100 gold standard pairs (UOKiK Q&A 60 + manual 40). v0.5 KEEP wszystkie 60 UOKiK Q&A. ✓
- **RQ3 (continuous improvement)** wymaga: 3 cykle retreningu. v0.5 dataset = cykl 1 baseline. ✓
- **RQ4 (verifier quality)** wymaga: ~100-300 par eval. v0.5 wystarcza. ✓

Brak blokady dla RQ1-RQ4 po cleanup.

---

**Sign-off:** decyzje zgodne z Wariantem B z krytyki + CLAUDE.md scope IN/OUT. Audit log na defense Kojałowicza.
