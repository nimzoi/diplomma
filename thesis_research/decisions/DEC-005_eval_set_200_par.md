# DEC-005 — Zwiększenie eval set gold standard z 110-160 do 200 par

**Data:** 2026-05-16 (evening, 48h-sprint week)
**Status:** ACTIVE
**Supersedes:** brak (uzupełnienie konspektu v3.2 § II.4.3 + PLAN_cele_i_kroki.md Iter. 5)
**Related:** [DEC-003](DEC-003_pivot-na-halu-detection.md) (pivot scope), [DEC-004](DEC-004_iter0b_poc_results.md) (POC results)

---

## Kontekst

Konspekt v3.2 (sekcja II.4.3 *Eval set design*) oraz `PLAN_cele_i_kroki.md` (Iteracja 5, manual gold) deklarowały primary eval set jako **~110-160 par gold standard**:
- 60 par UOKiK Q&A ready-made (zerowy koszt anotacji)
- 50-100 par hand-annotated by autorka (zakres szacunkowy)

W trakcie pisania drafu R3 (48h-sprint, 2026-05-16) Magda zwiększyła własny commitment do liczby par hand-annotated z 50-100 do **140 par** ("mogę więcej, ogarnę"). W rezultacie drafty R3 i R4 wpisały gold standard jako **200 par** (60 UOKiK + 140 autorka), powstała inkonsystencja z konspektem.

Decyzja DEC-005 reconciliuje tę różnicę poprzez explicit zwiększenie target eval set do 200 par we wszystkich źródłach prawdy (konspekt v3.2 + PLAN_cele_i_kroki + drafty R3/R4).

## Decyzja

**Primary eval set = 200 par gold standard**, z dystrybucją:

| Komponent | Liczba par | Status | Pochodzenie |
|---|---:|---|---|
| UOKiK Q&A ready-made | 60 | ✓ DONE (55/60 z citations) | Scrape z `prawakonsumenta.uokik.gov.pl` (Iter. 0b) |
| Hand-annotated by autorka | 140 | 🚧 Iter. 5 weekend hyperfocus | Magda commitment 2026-05-16 |
| **Razem** | **200** | — | — |

## Uzasadnienie

### Argumenty pro (dlaczego 200 jest lepsze niż 110-160)

1. **Statistical power dla ablation analysis.** Ablation A2 (probe target 1,5B/3B/11B) i A3 (LLM-judge ablation) wymagają porównań between-conditions. Na n=110-160 confidence intervals dla AUROC są zbyt szerokie (±0,06-0,08), na n=200 zwężają się do ±0,04-0,05 [CYT: bootstrap CI scaling].
2. **Coverage 5 typów halu × 6 kategorii consumer = 30 cell stratification.** Przy 200 par mediana 6-7 par per cell pozwala na meaningful per-cell error analysis (R7 6-poziomowa taksonomia). Przy 110-160 mediana 4-5 par per cell — borderline dla rzetelnej analizy.
3. **Defense argument przeciwko Kojałowiczowi.** *„Czy 110 par to wystarczająco?"* jest naturalnym pytaniem komisji. 200 par stanowi jednoznacznie defensible próbę dla pracy inżynierskiej (vs <100 = słabe, 200+ = standardowe dla published benchmarks polish NLP per PolEval rozmiary).
4. **Magdy autonomia decyzyjna.** Autorka explicit zwiększyła swój commitment ("ogarnę więcej") — DEC-005 honoruje to bez wymuszania downsize'u back to 110-160.

### Argumenty contra (kompromisy)

1. **Czas anotacji.** 140 par hand-annotated × ~5-8 min per para = ~12-19 h pracy autorki. Vs 50-100 par × 5-8 min = 4-13 h. Dodatkowy nakład 8-15 h weekend hyperfocus burst.
2. **Ryzyko anotacja fatigue.** Po 100 parach quality decisions może spadać. Mitygacja: anotacja w ≥3 sesjach (max 40-50 par per sesja) + cross-check Tier 1 mDeBERTa dla par anotowanych w ostatniej godzinie sesji.
3. **Brak inter-annotator agreement (IAA).** Bez drugiego anotatora 200 par to dalej *single-annotator* gold standard. Per dyskusja w R3 § 3.5.4 mitygacja przez written guidelines + self-review 10 % próby (20 par) post-48h + cross-validation z Tier 1 mDeBERTa. IAA z drugim anotatorem = future work post-defense.

## Wpływ na inne dokumenty

Po sign-off DEC-005 zaktualizowano (commit `502f38a` + następne):
- `02_konspekt_v3.2_skeleton.md` § II.1 streszczenie, § II.4 strategia danych (3 wystąpienia), § II.12 iteration plan
- `PLAN_cele_i_kroki.md` § Iter. 5 done criterion + work item
- `drafts/R03_dane.md` § 3.1 Tab 3.1 + § 3.5.4 (already 200 par jako fait accompli)
- `drafts/R04_eda.md` (eval set distribution discussion)
- `drafts/PLACEHOLDERS.md` (zaktualizowane już wcześniej do 200)

## Kill criteria

DEC-005 jest revertable wstecz do 110-160 par jeśli:
- Anotacja przekracza realistycznie dostępny czas Iteracji 5 (>20 h) — wówczas downsize do osiągniętej liczby z explicit limitation note w R3
- Quality control wykazuje >15 % par wymagających re-anotacji (jakość degraded) — wówczas pause i revise guidelines

W tych przypadkach update tej decyzji + powrót do konspektu v3.2 110-160 jako fallback.

## Sign-off

- Autorka: Magda — 2026-05-16
- Promotor: mgr inż. Piotr Kojałowicz — TBD post-defense draft submission
