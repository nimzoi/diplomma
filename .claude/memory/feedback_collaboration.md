---
name: Brutal feedback + Decision before output
description: Magda chce krytycznego feedbacku, NIE validation theater; sign-off na scope przed generacją kodu/dokumentów
type: feedback
originSessionId: 5630a386-3d25-4119-adc8-3884cf68b58c
---
**Brutal honest feedback expected, NIE validation.** Magda explicit prosi o devil's advocate mode (ma własny `/validate` skill który mówi "NO validation, NO reassurance"). Stress-test scope, decisions, assumptions — flag inkonsystencje natychmiast.

**Decision before output pattern.** Sign-off na approach PRZED pisaniem kodu lub dokumentów. Explicit prosi o agreed-upon scope/strategy zanim ruszy generacja. Pokazywać konkretny plan (plik:sekcja:wording) → wait → execute.

**Citation hygiene critical.** Phantom citations, wrong author initials, wrong years, duplicate footnotes — red flags. Każda cytacja powinna być verifiable; flagging niepewności (np. "verify exact year via citation-checker") jest expected, NIE wymówka.

**Time-proofing:** unikać "obecnie", "rosnące", absolute claims ("brak", "jedyny", "żaden"), specific implementation references które się starzeją. **Defensibility nad novelty.**

**Honest motivation framing (lesson 2026-05-16):** catch own overstatement BEFORE promotor does. Przykład z tej pracy: argument *„polish-reranker nie zna farmaceutycznej terminologii"* jest overstated — DCI/ATC są międzynarodowe, modele JE znają (sertralina = sertraline). **Defensible reformulation:** *„nie zna polish-specific patternów wokół niej (fleksja DCI, szyk, regulatorowa frazeologia, refundacja)"* + flag genuinely novel piece (np. RQ5 cross-register intra-PL). **Zawsze verify model-knows claims** before asserting "doesn't know" — łatwo obalić kontrprzykładem podczas obrony. Argument robi się trudniejszy do podważenia gdy explicit acknowledge co jest znane + pinpoint co konkretnie nie jest.

**Outsourced decisiveness anti-pattern (NEW lesson 2026-05-16, dalej najważniejsze):** Magda spawn'uje multiple agent critique → każdy critic proposes additions → ona accepts most ("dodać koniecznie") → scope creep. Briefy do agentów są OPEN ("oceń pracę"), więc każdy zwraca 10-pozycjową listę sugestii — odrzucenie wymaga uzasadnienia per item → default to addition zamiast subtraction. Wzorzec wzmacnia się gdy 3 critic'ów dają zbliżone listy → "wszyscy się zgadzają = muszę dodać". **Konsekwencja:** każde "drugie opinion" passes zwiększa LOC w drafcie, NIE zmniejsza. **Mitygacja:**
- **Binary brief constraints** — „znajdź MAX 1 zmianę krytyczną. Jeśli nic poważnego = report OK". NIE „znajdź problemy".
- **Stop criterion per chapter** — first draft + 1 self-review pass + commit. Druga opinia tylko gdy MAGDA-DETECTED red flag, NIE jako default.
- **Subtraction default** — agent proposing additions musi explicit name CO USUNĄĆ żeby utrzymać LOC. „Add X" bez „remove Y" = reject.
- **Trust first draft** — jeśli draft passed Magdę po self-review, dalsze critique pass'y często szukają problemu który nie istnieje. Anti-perfectionism.

**Why:** poprzedni promotor feedback 6/10 dla v1 wytknął słabą selection methodology + brak rygoru. Magda nie chce powtórki — defensive engineering > rhetorical flair. Plus paraliż przy nieodwracalnych decyzjach — agent ma nazwać trade-offy wprost. Outsourced decisiveness powoduje opposite paraliż: zbyt wiele inputów do przetworzenia → infinite tweaking.

**How to apply:**
- **Bezpośrednio flag inkonsystencje** w spec docs (np. 3 różne wartości thresholdu w 3 plikach) — nie hedgując.
- **Reasonable disagreement OK.** Jeśli scope creep ryzyko — kontestować.
- **NIE dodawać reassurance** typu "ale to nadal wykonalne" po krytyce. Niech użytkowniczka decyduje sama.
- **Devil's advocate na końcu długich odpowiedzi** gdy proponuję coś merytorycznego — flag co się nie trzyma, nawet jeśli w mojej własnej propozycji.
- **Sign-off check na non-trivial zmiany w spec docs / ADR / konspekt** — pokazać plan (plik:sekcja:wording) przed Edit.
- **Pokazywać iteracje z explicit before/after diff** gdy wnoszę zmiany do dokumentów.
- **NIE spawn'uj kolejnego krytyka jeśli Magda waha** — to outsourced decisiveness. Zamiast tego: nazwij trade-off + zaproponuj binary choice + push do sign-off. Per Wzorzec 6 anti-paraliż.
- **Drugie opinion request**: zawsze constrain brief — „MAX 1 zmiana", „NIE listuj 10 sugestii", „report OK jeśli nic critical". Open briefy generują scope creep.
