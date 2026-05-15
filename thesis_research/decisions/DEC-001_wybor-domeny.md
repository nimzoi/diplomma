# DEC-001: Rotacja domeny — psychiatria → farmakologia szeroka

**Data:** 2026-05-15
**Status:** ACCEPTED
**Autorka:** Magdalena Sochacka
**Related:** DEC-002 (ChPL+Ulotka pairing — wynika z tej decyzji)

## Kontekst

Konspekt v3 FINAL (commit 2026-05-07) ustalał temat pracy z domeną **psychiatrii klinicznej** jako testbed dla pipeline MLOps retreningu rerankera. Decyzja domenowa była uzasadniona trzema argumentami:
1. Long-tail terminologia psychiatryczna
2. Open-access źródła (PTP, AOTMiT, URPL, IPiN, psychiatriapolska.pl)
3. Eksperckie kompetencje autorki dla manualnej walidacji eval setu

Pomiędzy 2026-05-07 a 2026-05-15 (czyli zanim ruszyła implementacja Tygodnia 0) autorka zgłosiła wątpliwości:
- Psychiatria odbierana jako "za blisko osobiście" — ryzyko nieprzyjemnego ramowania w obronie (*"czemu akurat psychiatria"* sugerowane jako pytanie kłopotliwe)
- Konspekt v3 FINAL pozycjonował domenę przez pryzmat *"eksperckich kompetencji autorki"* — sformułowanie eksponujące
- Brak dyferencji vs sytuacja v1 (administracja) — wtedy też domena była dobrana pod kompetencje, co zostało odrzucone przez promotora

W trakcie analizy alternatyw przeprowadzono dwa rundy researchu źródeł (sources research R1 + R2) potwierdzające że szersza farmakologia spełnia wszystkie kryteria projektowe + dodaje istotne benefity strukturalne (ChPL standaryzowane, paired Ulotki — szczegóły DEC-002).

## Opcje rozważane

| Opcja | Pros | Cons |
|-------|------|------|
| **A: Pozostać przy psychiatrii** | Silna manual validation; konspekt v3 napisany pod tę domenę; psych terminologia rzeczywiście long-tail | Eksponuje osobiście autorkę; konspekt v3 zawiera framing *"eksperckie kompetencje autorki"* trudny do obronienia bez sugerowania self-disclosure; węższa baza dla rerankingu (~3-6k psych docs) |
| **B: Farmakologia szeroka, psych jako eval subset** | Szerszy korpus (~4100 docs), ChPL deterministycznie strukturyzowane (10 sekcji × 14k leków), **psych jako eval subset zachowuje manual validation strength**; neutralne ramowanie zewnętrzne; URPL XML feed = trivial scraping | Trzeba przepisać II.4 (data strategy) konspektu; eval set design wymaga jawnego uzasadnienia (dlaczego psych subset a nie random pharma sample) |
| **C: Weterynaria / klimat / inna neutralna** | Zerowa ekspozycja osobista; w pełni neutralne ramowanie | **Brak manual validation strength** — autorka nie zna domeny; RQ2/H2 ryzykowne (kto oceni 200 par gold standard?); brak strukturalnych benefitów typu ChPL |
| **D: Cyber (Plan B z v3)** | Też neutralna; istnieją źródła (CERT, NASK, UODO) | Mniej standaryzowane niż farmakologia; mniej naturalnych Q&A pairs niż ChPL; różny rejestr techniczny ale nie cross-register |

## Decyzja

**Wybrana: Opcja B — farmakologia szeroka, psychiatryczny eval subset (ATC N05/N06).**

## Uzasadnienie

1. **Manual validation preserved.** Najsilniejszy argument za psychiatrią — kompetencje walidacyjne autorki dla 200-par gold standard — pozostaje aktywny przez **świadome próbkowanie eval setu z psych podgrupy (ATC N05-N06 = Psycholeptica i Psychoanaleptica)**. To leverage'uje kompetencje bez eksponowania domeny w ramach tytułu pracy.

2. **Strukturalne benefity farmakologii.** ChPL (Charakterystyka Produktu Leczniczego) jest **deterministycznie strukturyzowany** — standardowe 10 sekcji per lek (1. Nazwa, 2. Skład, 3. Postać, 4.1-4.9 wskazania/dawkowanie/przeciwwskazania/ostrzeżenia/interakcje/ciąża/wpływ/działania niepożądane/przedawkowanie, 5. Farmakologia, 6. Dane farmaceutyczne). Każda sekcja → naturalna para query→passage. Ze stratified sample 900 leków = **~8100 natural pairs bezpośrednio z headerów**. Dla psychiatry-only wytycznych PTP, ta strukturalna konsystencja nie istnieje.

3. **License story czystsza.** Wszystkie kluczowe źródła farmakologii (URPL, AOTMiT, MZ, NFZ) są **urzędowymi materiałami** zwolnionymi z ochrony prawnoautorskiej (Art. 4 ustawy o prawie autorskim). Plus OA czasopisma na licencjach CC BY-NC. License audit zajmuje minutę zamiast godzin. Dla psych mix konspekt v3 miał elementy o niejasnych licencjach (psychiatriapolska.pl licencja CC dopiero od 03.2025, niektóre PTP pozycje unclear).

4. **Skala korpusu.** URPL RPL XML feed ma ~14-18k zarejestrowanych produktów leczniczych. Stratified sample 900 z over-representacją N05/N06 daje silne pokrycie psychiatrycznej podgrupy + neutralną szerokość. Konspekt v3 zakładał 3000-6000 psych dokumentów — farmakologia szeroka osiąga to bez wysiłku.

5. **Ramowanie zewnętrzne.** "Polska farmakologia" jako temat jest **neutralne**. Pytanie "*dlaczego farmakologia*" ma standardową odpowiedź ("regulowana domena, dostępne źródła, deterministyczna struktura ChPL"). Pytanie "*dlaczego psychiatria*" wymaga uzasadnień bardziej osobistych.

6. **Enabling decision dla RQ5.** Farmakologia (przez URPL) udostępnia paired ChPL+Ulotka dla każdego leku. To enabluje DEC-002 (cross-register retrieval jako 5. RQ). Psychiatria-only nie ma tego strukturalnego benefitu.

## Konsekwencje

### Pozytywne

- ~4100-dokumentowy korpus realny w 1-2 tygodnie scrape (URPL XML feed = trivial)
- 8 zweryfikowanych źródeł (ChPL, Ulotki, AOTMiT, MZ, NFZ zarządzenia, Farmacja Polska, Lek w Polsce, AAMS, CIPMS) — zobacz `sources_catalog.md`
- Neutralne ramowanie zewnętrzne pracy
- Enabling cross-register RQ5 (DEC-002)
- Strukturalne pary z ChPL headers = ~8100 natural training pairs (vs ~1000-2000 dla psych wytycznych)
- Plan B (cybersec) deactivated — pharma stabilne

### Negatywne / koszty

- **Przepisanie II.4 konspektu** (cała sekcja Strategia danych) — wykonane w `02b_konspekt_v3_updates.md`
- Eval set design wymaga **explicit uzasadnienia** w R5 (dlaczego psych subset a nie random pharma sample); odpowiedź: leverage manual validation kompetencji + N05/N06 ATC są dobrze odgraniczone semantycznie
- **Brief dla agenta (sekcja 6)** ma psych framing — historical, nie aktywny
- Konspekt v3 sekcje II.1, II.2.1, II.3.4, II.7, II.13, II.15, II.16 wymagały dopisków w delta (wykonane)
- **Niektóre cytacje literatury** w R2 mogą wymagać dostosowania (psych NLP literature → pharma NLP literature) — koszt: maks 5 nowych źródeł

### Neutralne (nie zmieniają się)

- Stack technologiczny (II.11)
- Architektura pipeline (II.5)
- Konfiguracja modeli (II.6)
- Drift detection (II.8)
- Mapping PRO-D (II.9)
- Harmonogram (II.10) z drobną adaptacją Tygodnia 0
- Lista RQ1-RQ4 i ich falsyfikowalność (II.3.3)

## Kill criteria

Decyzja zostanie podważona jeśli:
- **URPL RPL XML feed niedostępny / wycofany** w trakcie Iteracji 0 feasibility. Wtedy zatrzymanie scrape i re-evaluation per ADR — **bez pre-committed fallback plan** (autorka świadomie zostawia decyzję na moment ewentualnej aktywacji).
- **OCR threshold** — DEPRECATED w tym ADR. Single source of truth: `sources_catalog.md` § "Iteracja 0 — Feasibility pre-conditions" → kill criteria (OCR overhead >25%). Wcześniejszy próg "OCR <80% text-layer w sample 200" pozostaje historyczny.
- **Promotor explicit odrzuca** farmakologię jako "za szeroką" lub "nie wystarczająco specjalistyczną". W tym przypadku reaktywacja Opcji A z silnym framing testbeda (już mamy w v3 FINAL II.2.2).

## Powiązane

- **DEC-002**: ChPL+Ulotka pairing jako 5. RQ — naturalne consequensja Opcji B, niemożliwe w pierwotnej Opcji A psychiatry-only
- Konspekt v3 FINAL: sekcje II.1, II.2.1, II.3.3, II.3.4, II.4, II.7, II.13, II.15, II.16 — superseded w `02b_konspekt_v3_updates.md`
- Konspekt v3 FINAL sekcje II.5, II.6, II.8, II.9, II.10, II.11, II.12, II.14 — pozostają w mocy
- `sources_catalog.md` — implementacja Opcji B na poziomie źródeł

## Audit trail

| Data | Wydarzenie |
|---|---|
| 2026-05-02 | v1 administracja rejected przez promotora |
| 2026-05-06 | v2 prompt injection rejected |
| 2026-05-07 | v3 psychiatria committed jako FINAL |
| 2026-05-10 | feasibility psychiatry confirmed (raport_feasibility_psychiatria.docx) |
| 2026-05-15 | autorka zgłasza wątpliwości; sources research R1 + R2 wykonany; **decyzja rotacji** |
