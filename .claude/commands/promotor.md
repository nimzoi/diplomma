---
description: Generate 10 critical questions promotor Kojałowicz might ask. Style — structured technical defensiveness.
---

Argument: $ARGUMENTS — obszar fokusu (np. "feasibility test psychiatria",
"drift detection design", "harmonogram realistyczny", "wybór polish-reranker"),
albo puste = całokształt projektu.

## Profil promotora (z brief sekcja 1)

mgr inż. Piotr Kojałowicz — klasyczny **MLOps mindset**, preferuje **structured
technical defensiveness**, czyta w kategoriach klasycznych ML pipelines + tabular
data. Nie lubi przesadnego formalizmu nomenklatury.

## Procedura

Wygeneruj dokładnie 10 pytań, w kolejności **malejącego prawdopodobieństwa** że
faktycznie padną. Dla każdego:

```
N. [PYTANIE — krótkie, ostre]
   Dlaczego pyta: [jaka luka/słabość jest probowana]
   Strategia odpowiedzi: [1 zdanie, kierunek obrony]
```

## Konwencje

- **Konkrety, nie ogólniki.** Zamiast "czy plan jest realistyczny" →
  "dlaczego cykl 3 retreningu ma dać ≤2pp a nie 0pp przy plateau?"
- **Cytuj specyficzne wartości** z konspekt (kappa 0.50 vs 0.75, nDCG ≥10pp,
  precision 0.80, etc.)
- **Probuj decyzje techniczne** — czemu polish-reranker-roberta-v3 a nie E5-mistral?
  Czemu PLLuM-12B a nie większy model jako judge?
- **Probuj scope** — czemu drift detection w core a nie future work?
  Czemu BGE-M3 frozen?
- **Probuj harmonogram** — czemu cykle 2-3 idą na sem. III a nie kompresja sem. II?
- **Probuj defensibility** — gdzie są dziury w argumentacji?

## Po 10 pytaniach

Wskaż **2-3 pytania**, dla których warto przygotować szczegółową odpowiedź
(np. notatka 1-stronicowa, slajd, lub draft sekcji rozdziału). Wybierz te z
najwyższym ratio "prawdopodobne × słabość obecnej obrony".
