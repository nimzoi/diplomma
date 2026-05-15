---
description: Log a decision before acting (Decision before output pattern). Captures trade-offs for thesis defense.
---

Argument: $ARGUMENTS — krótki tytuł decyzji (np. "wybór chunking strategy dla
scientific content", "trigger logic dla drift detection")

## Cel

1. **Anti-paraliż** — zapis decyzji = jej zamknięcie, nie wracamy do niej
   chyba że spełnione kill criteria.
2. **Defense ammunition** — przy obronie pracy promotor zapyta "czemu X a nie Y" —
   masz gotową odpowiedź z trade-offami.

## Procedura

1. **Sprawdź czy decyzja jest faktycznie do zalogowania**:
   - Jeśli autorka jeszcze rozważa — zasugeruj `/validate` zamiast loga
   - Jeśli decyzja jest oczywista (trywialna) — odrzuć (nie zaśmiecaj logu)
   - Jeśli decyzja jest poważna i podjęta — kontynuuj
2. **Pozyskaj informacje** od autorki (jeśli nie podała):
   - Decyzja (1 zdanie)
   - Alternatywy rozważane (co najmniej 2 inne opcje)
   - Dlaczego ta opcja wygrywa (1-2 zdania)
   - Kill criteria — co musiałoby się stać, żeby tę decyzję podważyć?
3. **Znajdź następny wolny numer**:
   - Sprawdź `thesis_research/decisions/` na istniejące pliki `DEC-NNN_*.md`
   - Następny numer = max + 1, padding do 3 cyfr (DEC-001, DEC-002, ...)
4. **Zapisz** do `thesis_research/decisions/DEC-{NNN}_{slug}.md`:

```markdown
# DEC-{NNN}: {Tytuł decyzji}

**Data:** YYYY-MM-DD
**Status:** ACCEPTED | SUPERSEDED | DEPRECATED
**Autorka:** Magdalena Sochacka

## Kontekst

[1 paragraf — jaki problem, dlaczego potrzeba decyzji teraz]

## Opcje rozważane

| Opcja | Pros | Cons |
|-------|------|------|
| A: [nazwa] | ... | ... |
| B: [nazwa] | ... | ... |
| C: [nazwa] | ... | ... |

## Decyzja

**Wybrana:** [Opcja X — nazwa]

## Uzasadnienie

[1-3 paragraphs — dlaczego ta opcja]

## Konsekwencje

### Pozytywne
- ...

### Negatywne / koszty
- ...

## Kill criteria

Decyzja zostanie podważona jeśli:
- [konkretne kryterium 1]
- [konkretne kryterium 2]

## Powiązane

- (jeśli aplikuje) DEC-XXX: [nazwa]
- (jeśli aplikuje) Sekcja konspektu / brief: [referencja]
```

5. **Zwróć autorce**:
   - Ścieżka do pliku
   - 2-zdaniowe streszczenie
   - Sugestia kolejnego kroku (np. "decyzja zalogowana, zaczynamy implementację X")

## Reguły

- **NIE loguj decyzji której autorka faktycznie nie podjęła.** Loguj fakty, nie nadzieje.
- **Jeśli decyzja jest "tymczasowa eksploracja" — flag w nazwie pliku (`-tentative`)
  albo wskaż że to nie jest formalna decyzja.
- **Linkuj do poprzednich decyzji** jeśli ta nowa modyfikuje / supersedes wcześniejszą.
- Pisz w polskim, ale terminologia techniczna EN OK.
