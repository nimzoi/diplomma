# R4. Eksploracyjna analiza danych

## 4.1 Cele eksploracyjnej analizy danych oraz metodologia

Niniejszy rozdział przedstawia eksploracyjną analizę danych (EDA) korpusu zebranego dla pipeline'u opisanego w rozdziale 3. EDA pełni w pracy potrójną rolę metodologiczną, którą warto zarysować explicite, ponieważ implikuje strukturę dalszych sekcji oraz interpretację wyników.

**Rola pierwsza — diagnostyka jakości danych.** Eksploracja służy weryfikacji integralności korpusu pod kątem kompletności, duplikacji oraz spójności kodowania. Wykryte anomalie informują o ewentualnych korektach pipeline'u ingestii. W kontekście tekstów prawnych szczególnej uwagi wymagają artefakty wynikające ze zmiennej historii dokumentów ELI — tekst pierwotny ustawy z 2014 roku różni się formatowaniem od tekstu jednolitego opublikowanego po nowelizacjach. Heterogeniczność ta jest cechą strukturalną korpusu, a nie błędem; eksploracja pozwala ją zmierzyć i nazwać.

**Rola druga — projekcja decyzji architektonicznych.** Rozkłady długości chunków, gęstości cytowań oraz topiki konsumenckie bezpośrednio implikują wybór strategii chunkowania, hiperparametrów modelu osadzeń oraz progów decyzyjnych weryfikatora NLI. Decyzje te dokumentowane są w rozdziale 5 i 6; EDA dostarcza im ilościowego uzasadnienia, zgodnie z wymogiem rozdziału 5 dokumentu Assignment 5 (PRO-D) — *„EDA must inform later feature engineering decisions"*.

**Rola trzecia — defensja świadomych obciążeń.** EDA pozwala precyzyjnie nazwać te cechy korpusu, które są wynikiem świadomych decyzji projektowych (np. próbkowanie eval setu z podgrupy reklamacyjno-zwrotowej) oraz odróżnić je od obciążeń nieintencjonalnych (np. nadreprezentacja wątków forumprawne.org w pewnych kategoriach tematycznych). Lista świadomych obciążeń stanowi rozszerzenie listy z rozdziału 3.10 i zamyka rozdział w sekcji 4.9.

**Charakter analiz.** Wszystkie analizy w tym rozdziale mają charakter **opisowy (descriptive)**, nie wnioskujący (inferential). Nie formułuje się tutaj hipotez statystycznych ani testów istotności na poziomie korpusu — te elementy należą do rozdziału 7 (Wyniki) i dotyczą metryk pipeline'u (AUROC sondy, precision faithfulness, agreement weryfikatora). Celem rozdziału 4 jest **charakterystyka danych jako materiału wejściowego**, nie ich modelowanie.

**Metodologia per komponent.** Struktura analizy podąża za sześciopunktową taksonomią z Assignment 5: (A) struktura i integralność, (B) charakterystyka statystyczna, (C) analiza zależności, (D) ocena szumu i wartości odstających, (E) obciążenia i ograniczenia, (F) implikacje dla projektu eksperymentalnego. Sekcje 4.2–4.6 realizują głównie komponenty A–B, sekcje 4.7–4.8 komponenty C–D, sekcja 4.9 komponenty E–F.

**Narzędzia.** Analiza prowadzona w środowisku Python 3.13 z bibliotekami `pandas`, `numpy`, `matplotlib` oraz `seaborn` do wizualizacji rozkładów; `spacy` z modelem polskim `pl_core_news_lg` do segmentacji zdań i analizy lingwistycznej; `umap-learn` dla projekcji niskowymiarowych w sekcji 4.8; `sentence-transformers` z modelem `BAAI/bge-m3` dla osadzeń wektorowych. Wszystkie skrypty analityczne wersjonowane są w repozytorium i wywoływane reprodukowalnie z parametrów konfiguracyjnych.

---

## 4.2 Charakterystyka korpusu — rozkłady podstawowe

Korpus po fazie ingestii (stan na zakończenie Iteracji 1a) obejmuje trzy strata: (1) chunki aktów prawnych ELI, (2) pary pytanie-odpowiedź UOKiK, (3) pytania konsumenckie z portali e-prawnik.pl, forumprawne.org, eporady24.pl oraz Reddit. Tabela 4.1 podsumowuje liczności oraz miary tendencji centralnej długości tekstu w znakach.

### 4.2.1 Strata I — chunki aktów prawnych ELI

Korpus prawny obejmuje **2 123 chunki** pochodzące z sześciu ustaw konsumenckich i fragmentów Kodeksu cywilnego. Tabela 4.1 podaje rozkład per ustawa.

**Tabela 4.1.** Liczność chunków per ustawa w stratum prawnym

| Ustawa | Liczba chunków | Udział (%) |
|---|---|---|
| Ustawa o prawach konsumenta | 240 | 11,3 |
| Kodeks cywilny (art. 384–385 + 535–581) | 92 | 4,3 |
| Ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym | 113 | 5,3 |
| Ustawa o ochronie konkurencji i konsumentów | 500 | 23,6 |
| Ustawa o usługach płatniczych | 888 | 41,8 |
| Ustawa o pozasądowym rozwiązywaniu sporów konsumenckich | 290 | 13,7 |
| **Razem** | **2 123** | **100,0** |

Rozkład jest silnie nierównomierny — ustawa o usługach płatniczych dostarcza niemal 42% chunków, podczas gdy fragment Kodeksu cywilnego mniej niż 5%. Asymetria ta odzwierciedla strukturę domeny: ustawy specjalistyczne (płatności, ochrona konkurencji) operują obszerną terminologią i licznymi definicjami, natomiast Kodeks cywilny w częściach dotyczących sprzedaży konsumenckiej jest skondensowany. **Implikacja architektoniczna:** ewentualne ważenie chunków podczas treningu sondy ukrytych aktywacji powinno uwzględniać tę asymetrię, aby uniknąć dominacji jednej ustawy w sygnale uczącym.

[Figura 4.1: Histogram długości chunków per ustawa (w znakach). Placeholder — TBD post-Iteracja 1a po wygenerowaniu finalnego korpusu.]

[Tabela 4.2: Statystyki opisowe długości chunków (mean, median, std, min, max) per ustawa. Wstępna estymata na podstawie próbkowania feasibility: mean ≈ 350–550 znaków, median ≈ 280–420 znaków, std ≈ 200–350 znaków. Pełne wartości TBD post-Iteracja 1a.]

### 4.2.2 Strata II — pary pytanie-odpowiedź UOKiK

Stratum UOKiK obejmuje **60 par** zescrape'owanych z portalu `prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/`. Każda para składa się z pytania konsumenta sformułowanego w języku potocznym oraz autoryzowanej odpowiedzi UOKiK z cytatami do konkretnych artykułów ustaw. Dystrybucja kategorii tematycznych:

**Tabela 4.3.** Rozkład par UOKiK per kategoria

| Kategoria | Liczba par | Udział (%) |
|---|---|---|
| Prawo do informacji | 20 | 33,3 |
| Odstąpienie od umowy | 19 | 31,7 |
| Ogólne | 12 | 20,0 |
| Reklamacja | 6 | 10,0 |
| Telemarketing | 3 | 5,0 |
| **Razem** | **60** | **100,0** |

Dominacja kategorii „Prawo do informacji" oraz „Odstąpienie" (łącznie 65%) odzwierciedla priorytety edukacyjne UOKiK — instytucja koncentruje materiały informacyjne na obszarach, gdzie statystycznie pojawia się najwięcej sporów konsumenckich. Stosunkowo niewielka liczba par w kategorii „Reklamacja" (6) jest paradoksalna z perspektywy faktycznej skali tej kategorii w pytaniach konsumenckich (zobacz sekcję 4.6), co stanowi pierwszy zauważony element niezbieżności pokrycia.

### 4.2.3 Strata III — pytania konsumenckie z forów i Reddit

Stratum pytań konsumenckich obejmuje **2 967 dokumentów** z czterech źródeł:

**Tabela 4.4.** Rozkład pytań konsumenckich per źródło

| Źródło | Liczba pytań | Udział (%) |
|---|---|---|
| e-prawnik.pl | 954 | 32,2 |
| forumprawne.org | 1 202 | 40,5 |
| eporady24.pl | 302 | 10,2 |
| Reddit (r/Polska + r/PrawoPL + r/poland) | 509 | 17,2 |
| **Razem** | **2 967** | **100,0** |

[Figura 4.2: Rozkład długości pytań konsumenckich per źródło — boxplot. Placeholder — TBD post-Iteracja 1a. Hipoteza robocza: Reddit median <e-prawnik median <forumprawne median, ze względu na konwencje pisarskie poszczególnych platform.]

### 4.2.4 Rozkład liczby tokenów

Dla potrzeb dimensioning chunkowania oraz oszacowania kosztów inferencji generatora Bielik 11B v3 wykonana jest dodatkowa analiza długości w tokenach przy użyciu tokenizera Bielika (BPE oparte na Mistral). Tokenizer Bielik dla języka polskiego osiąga średnio około 1,4–1,8 tokenu na słowo, zależnie od proporcji fleksji w tekście. Rozkład tokenów per chunk pozwala oszacować, ile fragmentów mieści się w oknie kontekstu modelu generatora oraz jakie limity warto przyjąć dla retrieved top-k.

[Tabela 4.5: Mean/median/p95 tokenów per chunk per stratum. Placeholder — TBD post-Iteracja 1a, po uruchomieniu tokenizera Bielika na finalnym korpusie.]

### 4.2.5 Rozkład liczby cytowań na odpowiedź UOKiK

Spośród 60 par UOKiK, **55 (92%)** zawiera co najmniej jeden cytat do aktu prawnego, łącznie obejmując **52 unikalne referencje legalne**. Rozkład liczby cytowań na odpowiedź wymaga osobnej analizy, ponieważ wpływa bezpośrednio na strukturę gold standardu dla RQ2 (citation grounding).

[Tabela 4.6: Rozkład liczby cytowań per odpowiedź UOKiK (0, 1, 2, 3+). Placeholder — TBD po pełnej ekstrakcji `cited_articles` z zescrape'owanego JSONL.]

Wstępna obserwacja: odpowiedzi z pojedynczym cytatem dominują, ale niezerowy odsetek odpowiedzi cytuje równolegle Kodeks cywilny oraz ustawę specjalistyczną (np. ustawę o prawach konsumenta), co odzwierciedla strukturę polskiego systemu prawnego, w którym normy ogólne i szczegółowe stosuje się równolegle.

---

## 4.3 Standaryzacja i normalizacja tekstu

Standaryzacja tekstu dla korpusu polskojęzycznego wymaga decyzji projektowych, które wykraczają poza domyślne praktyki pipeline'ów anglojęzycznych. Niniejsza sekcja dokumentuje wybrane procedury wraz z uzasadnieniem.

### 4.3.1 Normalizacja Unicode (NFC)

Tekst polski zawiera znaki diakrytyczne (ą, ę, ł, ó, ś, ż, ź, ć, ń), które w różnych źródłach kodowane są niejednolicie. W szczególności fragmenty pochodzące z dokumentów PDF eksportowanych do HTML mogą zawierać formy zdekomponowane (np. litera + znak łączący diakrytyk), podczas gdy źródła nowsze stosują formę precomponowaną. Brak normalizacji prowadzi do tego, że dwa wizualnie identyczne ciągi znaków otrzymują różne osadzenia wektorowe.

Stosowana procedura: **Unicode Normalization Form C (NFC)** dla wszystkich tekstów na etapie ingestii. Forma NFC łączy znaki bazowe z diakrytykami w pojedyncze precomponowane code points, zgodnie z RFC 3629. Zastosowanie NFC zamiast NFD (forma zdekomponowana) motywowane jest kompatybilnością z większością bibliotek polskiego NLP (`spacy pl_core_news_lg`, `herbert-large-cased`, tokenizer Bielik), które zoptymalizowane są pod NFC.

### 4.3.2 Normalizacja białych znaków

Standardowa procedura: zamiana znaku **non-breaking space (U+00A0)** na zwykłą spację, kolapsowanie sekwencji wielokrotnych białych znaków do pojedynczej spacji, usunięcie białych znaków na początku i końcu chunka. Specjalnej uwagi wymagają **łamania wierszy w aktach prawnych ELI** — XML-owe oznaczenia paragrafów (`§`) muszą zostać zachowane jako separatory semantyczne, mimo redukcji innych białych znaków.

### 4.3.3 Anonimizacja danych osobowych w pytaniach konsumenckich

Pytania z forów internetowych oraz Reddit mogą zawierać dane osobowe: adresy email, numery telefonów, nazwy sklepów, nazwy własne osób. Stosowane procedury:

- **Adresy email:** detekcja regex `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` → zamiana na placeholder `[EMAIL]`.
- **Numery telefonów (polskie formaty):** detekcja regex `(\+48\s?)?(\d{3}[\s-]?\d{3}[\s-]?\d{3})` → zamiana na `[TELEFON]`.
- **Nazwy użytkowników Reddit:** ekstrahowane wraz z postem nazwy autorów hashowane funkcją SHA-1, redukowane do pierwszych 10 znaków hash — zachowuje to spójność dla wielokrotnych postów tego samego użytkownika bez ujawniania tożsamości.

Nazwy sklepów, firm oraz produktów **nie są anonimizowane** — dla pipeline'u prawnego informacja, że pytanie dotyczy konkretnego rodzaju umowy (np. „zakup w sklepie internetowym Allegro"), niesie wartość semantyczną.

### 4.3.4 Zachowanie wielkości liter

Decyzja **świadomie zachowuje oryginalną wielkość liter** w całym pipeline — nie stosuje się konwersji do lowercase. Trzy uzasadnienia:

1. **Skróty formalne z zachowanym case'em.** W tekstach prawnych występują skróty takie jak „Dz.U.", „K.C.", „RODO", „NIP", „REGON", których semantyka jest powiązana z formą zapisaną wielką literą. Konwersja do lowercase rozmywa rozróżnienie pomiędzy skrótem instytucjonalnym a zwykłym słowem (analogicznie do kodów ATC w domenach farmakologicznych — konkretne kody jak „N05" zmieniłyby semantykę po lowercase'owaniu; w consumer rights analogiczne są m.in. „Dz.U." czy „NFZ").
2. **Polskie nazwy własne.** Polski system fleksji nazw własnych (np. „Urząd Ochrony Konkurencji i Konsumentów" → „UOKiK") wymaga rozróżnienia wielkości liter dla poprawnej rekognicji semantycznej.
3. **Tokenizer Bielika jest wrażliwy na case.** Bielik dziedziczy tokenizację BPE z architektury Mistral, gdzie różne case'y dają różne tokeny. Sztywne lowercase'owanie zwiększyłoby out-of-vocabulary rate oraz zmieniło dystrybucję tokenów względem treningu modelu generatora.

### 4.3.5 Segmentacja zdań

Segmentacja zdaniowa korzysta z modelu `spacy pl_core_news_lg` z dodatkowymi regułami post-processing dla polskich skrótów. Polskie skróty typu „np.", „t.j.", „m.in.", „nr.", „art.", „ust.", „pkt." są często błędnie rozpoznawane przez generic sentence boundary detector jako końce zdań, co prowadzi do nadmiernej fragmentacji. Stosowana reguła post-processing: jeżeli token przed kropką znajduje się na liście whitelistowanych skrótów polskich (lista ~80 pozycji), kropka nie jest traktowana jako granica zdania.

### 4.3.6 Walidacja przed indeksacją

Każdy chunk przed indeksacją w bazie wektorowej Qdrant przechodzi walidację schematyczną:
- Minimalna długość: 50 znaków po normalizacji (chunki krótsze odrzucane jako fragmenty parsujące błędnie).
- Maksymalna długość: 2 000 znaków (chunki dłuższe podlegają dalszemu podziałowi — zobacz sekcję 4.4.1).
- Pole `citation_string` musi być niepuste dla stratum ELI.
- Pole `source_url` musi być niepuste oraz przejść walidację formatu URL.

---

## 4.4 Strategie chunkowania (trzy strategie dla trzech strata)

Pipeline RAG dla domen krytycznych wymaga strategii chunkowania **dostosowanej do struktury źródła** zamiast jednolitej heurystyki opartej wyłącznie na długości. Korpus pracy obejmuje trzy strata o radykalnie różnej strukturze; dla każdego stosuje się dedykowaną strategię.

### 4.4.1 Stratum ELI — chunkowanie świadome struktury (section-aware deterministic)

Akty prawne ELI charakteryzują się **hierarchiczną strukturą formalno-prawną**, którą polski legislator narzuca jako standard redakcyjny: ustawa → tytuł → dział → rozdział → artykuł → paragraf (§) → ustęp (ust.) → punkt (pkt) → litera (lit.). Każdy z tych poziomów jest jednostką semantyczną o ścisle określonej referencji.

**Strategia:** każdy element typu artykuł / paragraf / ustęp / punkt / litera traktowany jest jako **atomowy chunk**. Jeden chunk = jedna jednostka referencyjna. Pozwala to na bezpośrednie mapowanie wyniku retrievalu na cytat w formacie deterministycznym.

**Format `citation_string`:**

```
art. {N} [§ {P}] [ust. {U}] [pkt {K}] [lit. {L}] {short_title} z dnia {DATA} (Dz.U. {ROK} poz. {POZYCJA})
```

Pola w nawiasach kwadratowych pojawiają się warunkowo — chunk na poziomie artykułu zawiera tylko `art. N`, chunk na poziomie ustępu dodaje `§ P` oraz `ust. U`, itd. Format ten realizuje wymóg **deterministycznego cytowania** (zobacz rozdział 3.3): każdy chunk ma jednoznaczny ciąg cytowania, który można zweryfikować w portalu ELI poprzez konstrukcję URL `https://api.sejm.gov.pl/eli/acts/{publisher}/{year}/{num}/text.html/art={N}`.

**Granice długości:** minimum 50 znaków (krótsze fragmenty łączone z chunkiem nadrzędnym), maksimum 2 000 znaków. Chunki dłuższe niż maksimum (rzadkie w polskim ustawodawstwie konsumenckim, częstsze w ustawie o usługach płatniczych dla definicji terminów) podlegają wtórnemu podziałowi z preservation hierarchii — punkty rozdziela się na pod-chunki z zachowanym kontekstem nadrzędnym jako prefiksem. **Próg 2 000 znaków podlega rewizji post-Iteracja 1a** po analizie empirycznego rozkładu długości — wstępna estymata wskazuje na <2% chunków wymagających podziału, ale wartość zostanie zwalidowana.

### 4.4.2 Stratum UOKiK — preservacja struktury pary

Pary pytanie-odpowiedź UOKiK mają **strukturę bipartywną** o silnym powiązaniu semantycznym — odpowiedź odnosi się bezpośrednio do pytania, a oba elementy razem stanowią jednostkę edukacyjną z autoryzowanym cytatem.

**Strategia:** para `(question, answer)` traktowana jako **jedna jednostka indeksowana**. Pole `cited_articles` zachowane jako structured field (lista referencji do ELI w formacie `{ustawa_id, artykul, paragraf, ustep, punkt}`).

Indeksowanie pary jako jednostki ma dwie konsekwencje:

1. **Retrieval przy pytaniu konsumenta zwraca pełną parę** — model generator otrzymuje zarówno wzorcowe sformułowanie pytania, jak i autoryzowaną odpowiedź, co stanowi gold standard dla in-context learning.
2. **Citation alignment ma wbudowaną walidację** — pole `cited_articles` pary UOKiK pozwala porównać cytaty wygenerowane przez Bielika z cytatami autoryzowanymi, dostarczając metryki precision dla RQ2/H2a.

Pary UOKiK indeksowane są **podwójnie**: raz jako kompletne `(Q, A, citations)` w osobnej kolekcji Qdrant przeznaczonej do retrieval, raz jako sama odpowiedź w głównej kolekcji do mieszania z chunkami ELI w pipeline'ach bez bezpośredniego dostępu do par.

### 4.4.3 Stratum pytań konsumenckich — chunkowanie zachowujące topiki

Pytania z forów konsumenckich mają **niejednolitą strukturę** — niektóre to pojedyncze zdania, inne to wielowątkowe opisy sytuacji z licznymi szczegółami chronologicznymi. Niezależnie od długości, dla pojedynczego pytania **cała treść stanowi jeden topik**.

**Strategia:** każde pytanie konsumenta traktowane jako **pojedynczy dokument**, bez wtórnego podziału na zdania. Pole `extracted_topics` zawiera multi-label klasyfikację tematyczną (zobacz sekcja 4.6 dla rozkładu topików).

Wybór tej strategii motywowany jest rolą pytań konsumenckich w pipeline: nie służą one jako kontekst dla generatora (tę rolę pełnią chunki ELI oraz pary UOKiK), lecz jako **źródło dystrybucji zapytań** dla generowania syntetycznych par halu-injection oraz dla ewaluacji praktycznej w demonstratorze Gradio. Z tej perspektywy fragmentacja zniekształciłaby naturalną dystrybucję długości zapytań.

---

## 4.5 Analiza rozkładu cytowań

Stratum UOKiK dostarcza unikalnej okazji do analizy struktury cytowań w polskim systemie consumer rights, ponieważ 92% par zawiera co najmniej jeden cytat. Sekcja ta charakteryzuje rozkład cytowań pod trzema kątami: gęstość, ranking aktów najczęściej cytowanych, oraz pokrycie tematyczne.

### 4.5.1 Gęstość cytowań

Spośród 60 par UOKiK: 55 (92%) zawiera ≥1 cytat, 5 (8%) odpowiedzi bez cytatów. Brak cytatu występuje typowo w odpowiedziach o charakterze procedutalno-instytucjonalnym (np. opis ścieżki postępowania reklamacyjnego bez bezpośredniego odwołania do konkretnego artykułu).

[Tabela 4.7: Rozkład liczby cytowań per odpowiedź — wartości dokładne TBD post-Iteracja 1b po parsowaniu pola `cited_articles`.]

### 4.5.2 Ranking aktów najczęściej cytowanych

Wstępny ranking aktów cytowanych w stratum UOKiK (na podstawie 52 unikalnych referencji legalnych):

1. **Kodeks cywilny** — najczęściej cytowany, zwłaszcza art. 535–581 (sprzedaż konsumencka) oraz przepisy ogólne o zobowiązaniach (art. 471 i nast.).
2. **Ustawa o prawach konsumenta (Dz.U. 2014 poz. 827)** — drugie miejsce, dominuje w kategoriach „Odstąpienie" oraz „Prawo do informacji".
3. **Ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym** — typowo w kategoriach „Prawo do informacji" i „Telemarketing".
4. **Ustawa Prawo telekomunikacyjne** — kategoria „Telemarketing".
5. Pozostałe akty wycinkowo.

[Figura 4.3: Bar chart rankingu aktów per liczba cytowań w odpowiedziach UOKiK. Placeholder — TBD post-Iteracja 1b. Z tabeli wynika spodziewana **głęboka asymetria** — pierwsze trzy akty pokrywają prawdopodobnie >80% wszystkich cytowań. Implikacja architektoniczna dla treningu sondy halu i weryfikatora NLI: ewaluacja powinna uwzględniać zarówno akty dominujące, jak i te z długiego ogona, aby uniknąć overfit do najczęściej cytowanych norm.]

### 4.5.3 Gęstość cytowań per kategoria

Średnia liczba cytowań różni się pomiędzy kategoriami tematycznymi UOKiK. Wstępna obserwacja: kategorie „Odstąpienie" oraz „Reklamacja" mają wyższą gęstość cytowań (typowo 2–3 cytaty per odpowiedź), ponieważ wymagają precyzyjnego odwołania do kilku przepisów ustawy o prawach konsumenta oraz Kodeksu cywilnego równolegle. Kategoria „Ogólne" charakteryzuje się niższą gęstością (1 cytat per odpowiedź) ze względu na bardziej deskryptywny charakter.

---

## 4.6 Rozkład tematyczny pytań konsumenckich

Analiza tematyczna pytań konsumenckich (n=2 967) wykonana metodą **multi-label keyword extraction** z polskim lematyzerem `spacy pl_core_news_lg` na korpusie. Każde pytanie otrzymuje 1–5 etykiet topikalnych. Tabela 4.8 podaje top-15 topików oraz ich liczność.

**Tabela 4.8.** Top-15 topików w pytaniach konsumenckich

| Rank | Topik | Liczba wystąpień | Udział (%) |
|---|---|---|---|
| 1 | reklamacja | 610 | 20,6 |
| 2 | zwrot | 549 | 18,5 |
| 3 | odszkodowanie | 416 | 14,0 |
| 4 | sklep | 347 | 11,7 |
| 5 | Allegro | 217 | 7,3 |
| 6 | kurier | 193 | 6,5 |
| 7 | rękojmia | 191 | 6,4 |
| 8 | gwarancja | 178 | 6,0 |
| 9 | [TBD post-Iter. 1a] | [TBD] | [TBD] |
| 10–15 | [TBD post-Iter. 1a] | [TBD] | [TBD] |

[Tabela 4.8 dopełniona w Iteracji 1a po pełnej ekstrakcji topików z finalnego korpusu.]

### 4.6.1 Pokrycie krzyżowe pomiędzy źródłami

Porównanie rozkładów topików pomiędzy źródłami pokazuje istotne różnice:

- **e-prawnik.pl** — dominują topiki formalnie nazwane („rękojmia", „gwarancja", „reklamacja"), prawdopodobnie ze względu na profil użytkowników (osoby już zorientowane w terminologii prawnej, szukające bardziej szczegółowych konsultacji).
- **forumprawne.org** — szeroki rozkład z wysokim udziałem „odszkodowanie" i „sklep", lay terminologia mieszana z prawniczą.
- **Reddit (r/Polska)** — silna dominacja topików konsumenckich e-commerce („Allegro", „kurier", „sklep"), bardzo niski udział formalnej terminologii prawnej.
- **eporady24.pl** — pośrednia struktura podobna do forumprawne.org, mniejsza próba.

[Figura 4.4: Heatmap pokrycia topików per źródło (topiki × źródła, normalizacja per źródło). Placeholder — TBD post-Iteracja 1a. Heatmap pozwala wizualizować jakie kategorie tematyczne są niedoreprezentowane w którym źródle, co jest istotne dla decyzji o stratifikacji syntetycznych par halu-injection.]

### 4.6.2 Implikacje dla pokrycia eval setu

Porównanie rozkładu topików w pytaniach konsumenckich (Tabela 4.8) z rozkładem kategorii UOKiK (Tabela 4.3) ujawnia **niezbieżność pokrycia**:

- „Reklamacja" jest dominującym topikiem konsumenckim (20,6%), ale jednym z mniejszych w UOKiK (10%).
- „Allegro/kurier" (łącznie ~14% pytań konsumenckich) nie pojawia się jako odrębna kategoria UOKiK — wątki te trafiają najczęściej do „Reklamacja" lub „Ogólne".

Niezbieżność ta jest **świadomym obciążeniem eval setu** (zobacz sekcja 4.9, bias #7) — gold standard UOKiK reprezentuje perspektywę regulatora, nie statystyczny przekrój pytań konsumenckich. Implikacja architektoniczna: dodatkowe 50–100 par ręcznie annotowanych przez autorkę powinno celowo nadreprezentować topiki słabiej obsługiwane przez UOKiK, w szczególności reklamacje produktów zakupionych w e-commerce.

---

## 4.7 Przestrzeń wstrzykiwania halucynacji — wprowadzenie metodologiczne

[Sekcja nowa dla v3.2, post-DEC-003 pivot na halu detection. Pełna analiza ilościowa po wygenerowaniu syntetycznych par w Iteracji 1b — niniejsza sekcja przedstawia założenia metodologiczne.]

Pipeline detekcji halucynacji wymaga zbioru treningowego pokrywającego pięć typów halucynacji zdefiniowanych w rozdziale 3.5: **factual fabrication**, **entity confusion**, **temporal drift**, **negation flip** oraz **paragraph mis-citation**. Sekcja ta charakteryzuje **przestrzeń wstrzykiwania** — strukturę macierzy pokrycia per typ halu × ustawa × kategoria tematyczna — która stanowi podstawę projektu generatora syntetycznych par dla Iteracji 1b.

### 4.7.1 Docelowa proporcja per typ halucynacji

Generator syntetycznych par przewidziany na ~5–10 tys. par dla treningu sondy. Docelowy rozkład typów halucynacji:

- **Factual fabrication** — ~25% (najczęstszy typ halucynacji w domenach prawnych, najlepiej detectowalny przez weryfikator NLI).
- **Entity confusion** — ~20%.
- **Temporal drift** — ~15%.
- **Negation flip** — ~20% (subtelny typ, kluczowy dla testowania sondy ukrytych aktywacji vs. weryfikatora NLI).
- **Paragraph mis-citation** — ~20% (najistotniejszy dla RQ2 citation grounding).

Proporcje wymagają walidacji w Iteracji 1b post-generacja na bazie empirycznego signal-to-noise ratio per typ.

### 4.7.2 Macierz pokrycia

Macierz pokrycia ma trzy osie: **typ halu** (5 typów) × **ustawa źródłowa** (6 ustaw w stratum ELI + odpowiedzi UOKiK) × **kategoria tematyczna** (5 z UOKiK + extracted z pytań konsumenckich). Łącznie ~150 komórek macierzy. Cel: każda komórka pokryta minimum 10 syntetycznymi parami, aby uniknąć martwych stref w dystrybucji treningowej sondy.

[Tabela 4.9: Macierz pokrycia (typ halu × ustawa × kategoria). Placeholder — TBD post-Iteracja 1b. Macierz pokazuje, gdzie generator par syntetycznych wymaga dosypywania (np. „paragraph mis-citation × ustawa o usługach płatniczych × telemarketing" może okazać się trudna do wygenerowania ze względu na rzadkość koincydencji tematycznej w korpusie).]

### 4.7.3 Manualny eval subset — psychologia ścieżek

Eval set 100 par anotowanych manualnie przez autorkę projektowany jest tak, aby pokrywał **trudne ścieżki halucynacji** — typy halu rzadko reprezentowane w generowanych parach silver-standard. W szczególności: paragraph mis-citation pomiędzy artykułami semantycznie podobnymi (np. art. 27 vs. art. 28 ustawy o prawach konsumenta — oba dotyczące terminu odstąpienia, ale różne aspekty), oraz negation flip w kontekście podwójnych przeczeń („nie ma obowiązku nie informować" → „ma obowiązek informować"), które są trudne dla weryfikatorów NLI i potencjalnie diagnostyczne dla sondy ukrytych aktywacji.

---

## 4.8 Klastry osadzeń wektorowych

Charakterystyka semantyczna korpusu poprzez wizualizację klastrów osadzeń wektorowych wykonana modelem `BAAI/bge-m3` (multilingual, 568M parametrów, native polski support).

### 4.8.1 Procedura

Każdy chunk korpusu (n=2 123 ELI + 60 par UOKiK + 2 967 pytań konsumenckich = ~5 150 dokumentów łącznie) osadzony w przestrzeni wektorowej o wymiarze 1 024 (output BGE-M3). Projekcja do przestrzeni 2D wykonana metodą **UMAP** (Uniform Manifold Approximation and Projection) z parametrami `n_neighbors=15`, `min_dist=0.1`, `metric='cosine'`. UMAP wybrany zamiast t-SNE ze względu na lepsze zachowanie struktury globalnej oraz reprodukowalność z ziarnem losowości.

### 4.8.2 Hipotezy strukturalne

Przed wygenerowaniem projekcji formułowane są trzy hipotezy strukturalne dotyczące oczekiwanych klastrów:

1. **Separacja per stratum** — chunki ELI, pary UOKiK oraz pytania konsumenckie powinny formować odrębne klastry, ze względu na różnice rejestru językowego (formalny prawniczy vs. instytucjonalny vs. potoczny).
2. **Sub-klastry per kategoria tematyczna w stratum ELI** — ustawy o tematyce zbliżonej (np. ustawa o prawach konsumenta + Kodeks cywilny art. 535–581) powinny formować wspólny region przestrzeni semantycznej, z separacją od ustawy o usługach płatniczych.
3. **Bliskość par UOKiK do odpowiednich chunków ELI** — para UOKiK dotycząca odstąpienia od umowy powinna znajdować się w pobliżu chunków art. 27–28 ustawy o prawach konsumenta, co stanowi pośrednią walidację jakości osadzeń wektorowych dla retrieval.

[Figura 4.5: Projekcja UMAP wszystkich osadzeń korpusu z kolorystyczną encje per stratum oraz per kategoria. Placeholder — TBD post-Iteracja 1a. Wizualizacja stanowi pierwszą jakościową weryfikację, że BGE-M3 wydziela polski legalese semantycznie z domeny consumer rights.]

### 4.8.3 Interpretacja diagnostyczna

Niezgodność klastrów osadzeń z hipotezami strukturalnymi (np. brak separacji per stratum lub mieszanie chunków o radykalnie różnym znaczeniu) byłaby sygnałem **diagnostycznym** o niewystarczającej jakości osadzeń dla domeny i wymagałaby albo dofine-tuningu BGE-M3 na korpusie polskim, albo dodania reranker'a polish-aware (zobacz rozdział 6 dla decyzji architektonicznej).

---

## 4.9 Wnioski dla architektury pipeline'u oraz świadome obciążenia

Sekcja zamykająca rozdział 4 podsumowuje implikacje EDA dla architektury pipeline'u oraz dokumentuje świadome obciążenia korpusu jako rozszerzenie listy z rozdziału 3.10.

### 4.9.1 Implikacje dla retrievalu

1. **Walidacja strategii chunkowania ELI** — rozkład długości chunków per ustawa (sekcja 4.2.1) pokazuje, że chunkowanie świadome struktury produkuje fragmenty o średniej długości 350–550 znaków, co mieści się w optymalnym zakresie dla BGE-M3 (model trenowany na sekwencjach do 8 192 tokenów, optymalna granularność <512 tokenów). Brak konieczności rewizji strategii chunkowania.
2. **Asymetria stratów wymaga ważenia w retrieval** — dominacja ustawy o usługach płatniczych (41,8% chunków stratum ELI) może zniekształcać wyniki top-k retrieval jeżeli ustawiana metryka odległości faworyzuje strata z większą liczbą reprezentantów. Implikacja: ewaluacja retrievalu w rozdziale 7 powinna uwzględniać metryki per stratum, nie tylko zagregowane.
3. **Pary UOKiK jako few-shot examples** — wysoka jakość par UOKiK uzasadnia ich indeksowanie podwójne (jako kompletne pary `(Q, A, citations)` oraz jako same odpowiedzi), aby umożliwić ich retrieval jako wzorcowe odpowiedzi dla generatora w trybie few-shot.

### 4.9.2 Implikacje dla sondy halucynacji

1. **Pokrycie macierzy halu** (sekcja 4.7.2) — pożądane 10 par per komórka macierzy 5×6×~5 = ~150 komórek wymaga ~1 500 par minimum. Założony budżet ~5–10 tys. par syntetycznych jest wystarczający z marginesem na uzupełnienie martwych stref.
2. **Trudne ścieżki w eval secie** — ścieżki paragraph mis-citation pomiędzy artykułami semantycznie podobnymi oraz negation flip stanowią najlepsze sondowanie różnicy pomiędzy sondą ukrytych aktywacji a weryfikatorem NLI. Manualny eval subset 100 par powinien nadreprezentować te ścieżki względem ich naturalnego udziału w generacji syntetycznej.

### 4.9.3 Implikacje dla weryfikatora NLI

1. **Estymowana skuteczność weryfikatora dla języka polskiego** — model `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` charakteryzuje się szacowaną dokładnością **70–78%** dla par claim-evidence w języku polskim. Wartość ta jest niższa od progu RQ4/H4 (≥75% agreement z manualnymi etykietami) tylko w dolnym przedziale estymaty, co implikuje konieczność ewaluacji w Iteracji 0b z opcją upgrade do Tier 2 (HerBERT-large fine-tuned na CDSC-E) jeżeli Tier 1 osiągnie <70% w sanity check 50 par UOKiK Q&A.
2. **Stratifikacja eval setu weryfikatora** — eval set 100 par powinien pokrywać wszystkie 5 typów halu w proporcjach reprezentatywnych dla finalnego korpusu syntetycznego, aby uniknąć biasu ewaluacji w kierunku typów halu lepiej obsługiwanych przez NLI (np. factual fabrication) kosztem typów trudniejszych (np. negation flip).

### 4.9.4 Świadome obciążenia korpusu (rozszerzenie rozdziału 3.10)

Lista świadomych obciążeń zostaje rozszerzona o dwa nowe punkty wynikające z EDA:

**Bias #6 — heterogeniczność kodowania w ELI.** Korpus aktów prawnych ELI obejmuje akty pierwotne (np. ustawa o prawach konsumenta z 2014 roku w jej tekście pierwotnym) oraz teksty jednolite publikowane po nowelizacjach (np. tekst jednolity Dz.U. 2020 poz. 287). Pomiędzy nimi mogą występować drobne różnice formatowania (np. rozmieszczenie znaków `§`, sposób zapisu numeracji ustępów). Korpus traktuje obie formy jednolicie po normalizacji NFC oraz redukcji białych znaków, ale **drobne heterogeniczności kodowania pozostają** na poziomie subtelnych różnic formatowania. Decyzja świadoma: nie wymuszamy unifikacji formatu, ponieważ wymuszenie wymagałoby ręcznego porównania wszystkich wariantów tekstów jednolitych z tekstami pierwotnymi, co przekracza budżet pracy. **Implikacja:** ewaluacja retrievalu może wykazywać marginalnie wyższe wyniki dla tekstów jednolitych (czystszy format) niż dla tekstów pierwotnych — efekt do zaraportowania w rozdziale 7 jeżeli okaże się istotny.

**Bias #7 — single-annotator dla manualnego eval setu.** 50–100 par hand-annotowanych przez autorkę nie ma drugiego anotatora ani inter-annotator agreement metric (Cohen's kappa). Wymóg drugiego anotatora nieosiągalny w budżecie pracy inżynierskiej oraz w domenie wymagającej znajomości polskiego prawa konsumenckiego. **Mitygacja:** (1) anotacja prowadzona z explicit reference do par UOKiK jako gold standard procedury anotacji, (2) gotowość do publikacji eval setu jako open dataset z protokołem anotacji, aby społeczność mogła rewidować i rozszerzać, (3) w rozdziale 8 (Limitations) jawne zaadresowanie tego ograniczenia oraz wskazanie inter-annotator agreement jako future work.

### 4.9.5 Implikacje dla projektu eksperymentalnego

EDA potwierdza zasadność architektury pipeline'u zaprojektowanej w Iteracji 0 oraz nie wymaga rewizji założeń metodologicznych z rozdziału 3. Trzy korekty drobne wynikające z EDA:

1. **Próbkowanie syntetycznych par halu z stratifikacją per kategoria UOKiK** zamiast jednorodnego próbkowania z korpusu — adresuje niezbieżność pokrycia (sekcja 4.6.2).
2. **Indeksowanie podwójne par UOKiK** w Qdrant — wynika z analizy jakości UOKiK jako gold standard (sekcja 4.4.2).
3. **Ewaluacja retrievalu per stratum w rozdziale 7** zamiast wyłącznie agregowanej — adresuje asymetrię stratów (sekcja 4.9.1 pkt 2).

Pełne sformalizowanie strategii preprocessing oraz feature engineering następuje w rozdziale 6 (Modele). EDA dostarcza diagnostykę i pole decyzyjne; rozdział 6 podejmuje konkretne decyzje implementacyjne na podstawie zidentyfikowanych ograniczeń.

---

## Bibliografia (placeholder — finalizacja w Iteracji 7)

[1] McInnes L., Healy J., Melville J., *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*, arXiv:1802.03426, 2018.

[2] Chen J., Xiao S., Zhang P., et al., *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*, arXiv:2402.03216, 2024.

[3] Mroczkowski R., Rybak P., Wróblewska A., Gawlik I., *HerBERT: Efficiently Pretrained Transformer-based Language Model for Polish*, Proceedings of the 8th Workshop on Balto-Slavic Natural Language Processing, 2021.

[4] Laurer M., van Atteveldt W., Casas A., Welbers K., *Less Annotating, More Classifying — Addressing the Data Scarcity Issue of Supervised Machine Learning with Deep Transfer Learning and BERT-NLI*, Political Analysis, 2024.

[5] Honnibal M., Montani I., *spaCy: Industrial-strength Natural Language Processing in Python*, 2020.

[6] *Unicode Standard Annex #15: Unicode Normalization Forms*, Unicode Consortium, 2024.

[7] Speakleash, *Bielik-11B-v3.0-Instruct Model Card*, Hugging Face, 2025.

[8] [TBD post-Iteracja 7: dodatkowe referencje na temat citation grounding evaluation, NLI dla języka polskiego oraz UMAP best practices.]
