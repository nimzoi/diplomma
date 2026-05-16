---
description: Generate 10 critical questions promotor Kojałowicz might ask. Style — structured technical defensiveness.
---

Argument: $ARGUMENTS — obszar fokusu (np. "Iter. 0b POC results T1 mDeBERTa",
"drift detection design", "halu probe layer 47 wybór", "wybór mDeBERTa Tier 1 zamiast HerBERT",
"5,402 halu pairs balance"), albo puste = całokształt projektu v3.2.

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
- **Probuj decyzje techniczne** — czemu mDeBERTa Tier 1 a nie HerBERT-large + CDSC-E fine-tune?
  Czemu Bielik 11B v3 layer 47 a nie 49 lub 45? Czemu gliclass tylko jako Tier 0 ablation?
- **Probuj scope** — czemu drift detection w core a nie future work?
  Czemu BGE-M3 frozen? Czemu RAG MVP w Iter. 1 a probe training osobno?
- **Probuj harmonogram** — czemu manual gold 200 par w Iter. 5 a nie wcześniej?
  Czemu cykle 2-3 retraining przed observability?
- **Probuj defensibility** — gdzie są dziury w argumentacji?

## Po 10 pytaniach

Wskaż **2-3 pytania**, dla których warto przygotować szczegółową odpowiedź
(np. notatka 1-stronicowa, slajd, lub draft sekcji rozdziału). Wybierz te z
najwyższym ratio "prawdopodobne × słabość obecnej obrony".
