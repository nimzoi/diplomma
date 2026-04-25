# Agent B — quality audit pełny dataset JDG

> **Cel:** ocenić zasadność każdego zebranego dokumentu w kontekście budowy
> bazy wiedzy chatbota dla osób prowadzących JDG. Soczewka: persony i etapy
> życia JDG z `agent_a_personas.md`. Decyzje produkcyjne (drop / keep) wraz
> z uzasadnieniem; format/codebook check; ranking źródeł; opinia całościowa.
>
> Apply policy: rekomendacje typu **drop** trafiają do `data/quarantine/`
> (nie kasujemy wierszy z manifestu — `quality_flag=quarantine` + `notes`).

## Stan wyjściowy

- 452 dokumentów w `data/manifest.csv` (kontekst usera mówił 384 — ten plan
  bazuje na świeżym manifeście)
- 100 % `accepted` przed auditem, ~441 MB na dysku
- 56/67 pokrytych topiców (51 spec + 16 hot-2025/2026), gap 11 (wszystkie
  hot-2025/2026 — patrz sekcja "Coverage gaps")
- Per-source: govpl 96, kis 83, biznes_gov 63, pip 45, eli 37, podatki 28,
  zus 19, uodo 8, eurlex 5

## 1. Drop list (rekomendacja → quarantine)

**71 plików / ~84.2 MB / ~16 % datasetu.** Skupiska: 42× załączniki ze strony
`gov.pl/web/finanse/akty-prawne-budzet-panstwa` (czysty out-of-scope: projekty
ustaw budżetowych, generic title), 12× landing/feed pages (Rzecznik MŚP feed,
PARP/KAS landing, KNF edukacja), 9× PIP off-topic (delegowanie do UE, BHP
przemysłowe/rolnicze, POV pracownika, duplikat), 3× ZUS niche (niania POV
pracownika, duchowni, archaiczne raporty), 2× UODO niche (kampanie wyborcze,
szkoły), 1× eurlex (DSA — overkill VLOP), 1× biznes_gov (pusty title).

Format poniżej jest parseable przez `scripts/quarantine_from_audit.py`
(kolumny `relative_path,reason`, RFC 4180-quoted gdzie potrzeba).

```csv
relative_path,reason
raw/govpl_html/govpl_akty-prawne-budzet-panstwa.html,off-topic: landing page aktow prawnych budzetu panstwa
raw/govpl/govpl_attach_98f9f334-e52e-42b6-94ed-a4423608bf9d.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_9365b74e-4a21-46d4-9338-57aa5b5b1987.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_cd6072ca-9646-4ca0-9b92-b585847399db.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_1dd1fd0f-0866-4b4a-aff2-80ea03e4c79c.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_47d15e35-e8d3-41c2-bc8d-83b11b2d4d5a.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_deeaef02-a224-4343-b2ad-cd47ba6bc217.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_4cb9dcbf-9b95-4e15-a45e-9067c1501d51.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_4501acda-053b-41f4-9796-d3855326c431.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_a384f157-3c26-4604-8201-0dea3a0fd673.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_76878f6a-f663-4992-9045-c645b6f59e8e.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_7099a568-354f-4086-9d92-643f40359e00.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_0da7c48d-47aa-4bea-8bd3-f038eb032889.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_7bb1e6b6-90b7-4707-a386-def109ee7f14.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_7b1f4837-6ac3-4318-aa69-a79f3e1c699e.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_bd33eb54-d53b-4ba9-bd22-e179ba791695.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_ff330c30-f6f4-4a58-bc11-5e8830a8d985.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_fe463e27-5af3-45bf-aa9c-c5324cd8e9ac.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_80e0a9b5-2f87-467c-afb6-ff986e7b66c1.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_b22b786e-c5ed-414c-978c-745b0c2182a2.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_53787820-5494-4091-990c-2d5edac09cef.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_2849d306-3a4e-49e9-8a68-3ab7282cc01b.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_85057a27-8faf-4a9d-a423-8294818870d9.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_31986f12-449d-4e6f-9909-8fda1a135334.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_5f4951e1-f226-4a2b-873b-d10cd3a4a33d.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_cb78f4f2-9f9d-4e46-aba9-69c6a81942c3.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_c332415e-ce19-4908-8805-f38ca767c26d.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_1e070cce-84c4-403d-84d0-651f9f03eb7f.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_3a077686-6c4b-42de-a428-67732f97d4d3.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_2bdc2433-f9d5-4068-9ad8-fc6f26b0844d.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_1e8cf8d0-a8f8-4b35-9b5c-081984435719.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_a99d9057-05a2-4ab1-84c0-4f4ddf83fe6a.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_42755995-cf54-4159-ade0-f7393bfa5da3.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_e14f4344-32d2-40df-a030-4860586447d5.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_c51905c4-4bc5-42af-8eea-4f478b8a6030.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_276b7dff-ea9e-43ea-bec4-8bb843aaba4f.docx,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_71a14a0d-d7d9-4577-bd70-18af8f93bdcd.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_dcc2cec8-fcb5-486a-8fcd-5bd4a4263d14.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_f280785e-e86e-40ab-b420-a13875a6d156.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_8f28b0dc-b1fc-44ab-ba53-1d7118093342.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_d7fe25d6-03bb-4a86-80d7-551cf8d7bdd9.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_8c024fa8-04fe-4954-9251-8b0a0538f5f7.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl/govpl_attach_46f16381-0c35-4195-a673-96f63458ac70.pdf,"off-topic: zalacznik ze strony akty-prawne-budzet-panstwa MF (projekty ustaw budzetowych, nie merytoryka JDG)"
raw/govpl_html/govpl_konsultacje-podatkowe.html,"landing: opis procesu konsultacji, nie procedury JDG"
raw/govpl_html/govpl_indywidualne-dane-podatnikow-cit.html,"off-topic: publikacja danych CIT, dotyczy duzych podatnikow CIT"
raw/govpl_html/govpl_edukacja-finansowa.html,landing: ogolna edukacja KNF
raw/govpl_html/govpl_kas.html,"landing: strona glowna KAS, brak merytoryki JDG"
raw/govpl_html/govpl_agenci-rozliczeniowi.html,"off-topic: B2B platnosci miedzy bankami, nie JDG"
raw/govpl_html/govpl_dostawcy-uslug-platniczych.html,"off-topic: regulacja PSP/banki, nie JDG"
raw/govpl_html/govpl_edukacja-i-akcje-informacyjne-kas.html,landing: lista akcji informacyjnych KAS
raw/govpl_html/govpl_egzekucja-administracyjna.html,"landing: opis egzekucji administracyjnej, nie procedury JDG"
raw/govpl_html/govpl_rzecznikmsp.gov.pl.html,landing: strona glowna Rzecznika MSP
raw/govpl_html/govpl_aktualnosci.html,"feed: aktualnosci Rzecznika MSP, lista linkow"
raw/govpl_html/govpl_interwencje.html,"feed: interwencje Rzecznika MSP, lista linkow"
raw/govpl_html/govpl_www.parp.gov.pl.html,landing: strona glowna PARP
raw/pip/PORADNIK-DOTUBEZPIECZENIASAZ-1.pdf,"off-topic: delegowanie pracownikow do UE (14.4 MB), dla duzych firm"
raw/pip/srodkiochronyoddech.pdf,"off-topic: srodki ochrony oddechowej (przemysl), niche"
raw/pip/stres-w-pracy-przyklady-dobrych-praktykp38690.pdf,"redundant: poradnik dla pracownika, mamy 29STRESWPRACYPRACODAWCA dla pracodawcy"
raw/pip/nadgodziny-w-praktycep45815.pdf,duplicate: starsza wersja Nadgodziny-w-praktyce.pdf
raw/pip/zwolnienia-grupowep68798.pdf,off-topic: zwolnienia grupowe >20 pracownikow
raw/pip/Uprawnienia-rodzicielskie-pracujcych-ojcow.pdf,"POV pracownika: poradnik dla ojca-pracownika, nie dla pracodawcy"
raw/pip/prace-prasa-do-slomy.pdf,"off-topic: BHP rolnicze (prasa do slomy), nie typowa JDG"
raw/pip/prace-transportowe.pdf,off-topic: specjalistyczne BHP transportowe
raw/pip/uzytkowanie-maszyn-minimalne-wymagania-dotyczne-bhp.pdf,"off-topic: BHP maszyn przemyslowych (5.7 MB), nie typowa JDG"
raw/zus/55d7bce1-09a9-4c76-a03f-c8d5b7b0db10.pdf,"POV pracownika: poradnik dla niani, mamy juz Ubezpieczenie nian dla pracodawcy"
raw/zus/5bd51288-7bae-d65b-b2c0-5a13c5dffde2.pdf,archaiczne: raporty informacyjne ZUS sprzed 1999
raw/zus/d070a414-39a8-060e-fc88-3dec3bd22878.pdf,"off-topic: ubezpieczenia ksiezy, nie JDG"
raw/uodo/uodo_1447_poradnik_ochrona_danych_osobowych_w_kampanii_wyborczej.pdf,"off-topic: kampanie wyborcze, nie JDG"
raw/uodo/uodo_1384_poradnik_dla_szk.pdf,"off-topic: dla placowek oswiatowych, nie JDG"
raw/eurlex/celex_32022R2065.pdf,"overkill: DSA dotyczy bardzo duzych platform (VLOP/VLOSE), poza zakresem typowej JDG"
raw/biznes_gov/bizgov_Lista-uprawnie_.pdf.pdf,"pusty title, generic tag ceidg_rejestracja, niejasna zawartosc"
```

<!-- end drop list — 71 entries total -->

## 2. Coverage gaps vs personas

### 2.1. 11 hot-2025/2026 niepokrytych — mapowanie na persony i etapy

| topic_id | persona | etap | priorytet |
|---|---|---|---|
| `b2b_zmiana_na_uop` | P1 (programista B2B) | E7 (trudne sytuacje) | **wysoki** — kluczowy gap dla flagship persony |
| `dac7_platformy` | P4 (e-commerce/dropshipping) | E5 (2-3 lata), case 4 | **wysoki** — od 2024 obowiązek raportowy Allegro/Vinted/Booking |
| `kasa_fiskalna_online` | P4, P5 (rzemiosło) | E2 (zakładanie) | **wysoki** — większość branż handel/usługi B2C |
| `estonski_cit` | P3 (konsultant 200-500k) | E8 (zmiana formy) | **średni** — exit ramp dla skalujących się JDG |
| `przeksztalcenie_jdg_spzoo` | P3 | E8 | **średni** — naturalna kontynuacja `estonski_cit` |
| `pomoc_de_minimis` | wszystkie aplikujące o dotacje | E1, E5 | **średni** — limit 300k EUR / 3 lata, dotyczy ulg podatkowych |
| `crbr_beneficjent_rzeczywisty` | P3, P10 | E8 (przy spółce) | **niski** — tylko po przekształceniu w spółkę |
| `zatrudnianie_cudzoziemcow` | P10 (mikropracodawca) | E6 (skalowanie) | **wysoki** — duża liczba JDG zatrudnia |
| `faktoring_cesja_wierzytelnosci` | wszystkie z zatorami | E7 | **średni** — dotyka realnie B2B z dużymi klientami |
| `ulga_ekspansja_prototyp_robotyzacja` | P1 (dev mobile) | E5 | **niski** — niche, ale pasuje do osób z IP Box |
| `jpk_cit_jpk_kr` | P3 (przy sp. z o.o.) | po E8 | **niski** — JPK_CIT obowiązkowy od 2025 ale dla CIT-podatników |

### 2.2. Gaps zidentyfikowane przez personas (poza 11)

- **VAT-IM / Intrastat / WSTO** (P8 importer, P4 e-commerce) — taxonomy ma
  tylko `vat_ue` (2 docs). Brak konkretu dla "import z Chin", "Intrastat
  progi", "OSS/IOSS".
- **Ewidencja KPWI dla IP Box** (P1) — `pit_ip_box=17 docs` ale to głównie
  ustawa PIT + interpretacje KIS; brak formal poradnika "jak prowadzić
  ewidencję IP Box".
- **PPK obowiązek od 1 zatrudnionego** (P10, E6) — nie ma topic_id;
  pojawia się w manifest tylko marginalnie.
- **Najem prywatny + JDG / dwa reżimy** (P9) — brak konkretu o ryczałcie
  8.5/12.5% dla najmu prywatnego; mamy ogólny `pit_ryczalt`.
- **Sprzedaż auta firmowego po wykupie** (case 2) — niche ale częsty pain
  point; nie ma dedykowanego docu.
- **Koncesje / akcyza / zezwolenia** (E1, alkohol/paliwo/e-papierosy) —
  brak topic_id w taxonomy.
- **Sygnaliści / whistleblowing** — brak topic_id; obowiązek od 50 osób
  ale chatbot powinien znać próg.
- **AI Act / GPSR / DSA dla małych** — brak; po quarantine DSA znika
  całkowicie.
- **Działalność nierejestrowana — próg miesięczny 2025/2026** (P6) —
  `ceidg_dzialalnosc_nierejestrowana=10 docs`, trzeba sprawdzić aktualność
  progu (75% min wynagrodzenia, ~3500 zł/mies).

### 2.3. Rekomendacja

Po Kroku 3 (quarantine) gap **NIE zniknie automatycznie** — quarantine
usuwa szum, nie dodaje brakujących treści. Rekomendowany follow-up
(out-of-scope tej sesji): targetowana kolekcja na `biznes.gov.pl`
(procedury z hot-2025/2026), oraz `podatki.gov.pl/wyjasnienia` dla DAC7,
estońskiego CIT, JPK_CIT. To Opcja C z poprzedniej sesji.

## 3. Format / codebook check

### 3.1. Manifest

- Kolumny (20): `id, url, source, topic_ids, layer, format, fetched_at,
  http_status, content_type, bytes, relative_path, title, last_modified,
  is_official, eli_id, parent_url, discovery_source, sha256, quality_flag,
  notes` — spójne, wszystkie wiersze mają komplet kolumn.
- `id` = pierwsze 16 hex z `sha256` (deterministyczne, voice-checked
  na 4 próbkach).
- `quality_flag` przed auditem: 100 % `accepted`. Po Kroku 3 dodajemy
  wartość `quarantine` dla 71 wierszy (nie usuwamy wierszy).
- `topic_ids` — `;`-separated; obecnie 67 unikalnych (51 spec + 16
  hot-2025/2026).
- 1 wiersz z pustym/`.` tytułem (`bizgov_Lista-uprawnie_.pdf.pdf`) —
  trafia do quarantine.
- Default fallback `topic_ids=ceidg_rejestracja` w 23 HTML-ach
  biznes_gov/govpl_html — to **retag-grade**, nie quarantine (treść jest
  merytoryczna, problem jest w `topics.py` regexach).

### 3.2. Sidecary `.meta.json`

- Każdy plik w `data/raw/**` ma siostrzany `.meta.json` (próbka 6 plików
  `govpl/*` — wszystkie obecne, schemat zgodny z wierszem manifestu +
  pola `headers` (HTTP) i `content_audit` (validation flags)).
- Sidecary mają `link_text` (anchor text) — to dobre źródło dla retagu
  budget-attach (wszystkie mają pusty `link_text`, dlatego title był
  generic).

### 3.3. Skrypty `scripts/build_*.py` — reproducibility

- `build_source_registry.py` i `build_coverage_report.py` **liczą
  wszystkie wiersze z manifestu**, nie filtrują po `quality_flag`. Po
  zarekwarantowaniu 71 plików produkcyjny widok pokaże te same 452 w
  tabeli — to mylące. **Fix w Kroku 3**: dodać filtr
  `quality_flag in ('accepted',)` do produkcyjnego widoku, plus osobna
  sekcja "Quarantine" z liczbą zarekwarantowanych.
- Pozostałe skrypty `fetch_*.py` (głównie idempotentne, używają
  `discovery_source=seed`) — out-of-scope tej sesji, nie zmieniamy.
- `topics.py` — 67 topiców (51+16 hot), regexy lowercase. Catch-all
  fallback przez fakt że `ceidg_rejestracja` ma keyword "ceidg" w wielu
  URL-ach biznes.gov.pl — borderline, ale działa.

### 3.4. Quarantine już istniejące

- `data/quarantine/_failed/` — 22 elementy z fetch-time validation (404,
  brak PDF magic, WAF redirect). To nie jest częścią manifestu (nigdy
  nie było). Trzymamy jako jest.
- `data/quarantine/<source>/` — **nowy** layout dla Kroku 3 (per-source
  subfolder, plus `<basename>.reason.txt` obok każdego pliku).

## 4. Ranking źródeł (po quarantine)

| Source | Pre | Drop | Post | Retain % | Wartość merytoryczna |
|---|---:|---:|---:|---:|---|
| `eli` | 37 | 0 | 37 | 100 % | **Top tier.** MUST acts (KP, PIT, VAT, USS, Ordynacja, RODO). Zerowy szum. Referencyjne — tekst jednolity. |
| `kis` | 83 | 0 | 83 | 100 % | **Top tier.** Indywidualne interpretacje 2024-2026, najwartościowsze case studies (IP Box, ryczałt PKD, looking-through). |
| `podatki` | 28 | 0 | 28 | 100 % | **Top tier.** Broszury PIT-36/36L/28, instrukcje VAT, JPK. Flagship how-to dla podatków. |
| `biznes_gov` | 63 | 1 | 62 | 98 % | **High.** Procedury "co/jak/kiedy" — flagship dla zakładania, zawieszania, faktur. Catch-all tag częsty (retag-grade). |
| `zus` | 19 | 3 | 16 | 84 % | **High.** Formularze (DRA, RCA, IWA), poradnik dla rozpoczynających DG, Polski Ład. Niche dropy (niania POV, duchowni, archaiczne). |
| `pip` | 45 | 9 | 36 | 80 % | **Mid-high.** Poradniki BHP/UoP dla pracodawcy. 20 % to przemysłowe BHP / POV pracownika / duplikat. |
| `uodo` | 8 | 2 | 6 | 75 % | **Mid.** Top RODO-naruszenia + zatrudnienie. Niche (kampanie, szkoły) odpada. |
| `eurlex` | 5 | 1 | 4 | 80 % | **Mid.** RODO + Dyrektywa VAT + konsumencka + eIDAS. Referencyjne, ale w 95 % kanon krajowy wystarcza. |
| `govpl` | 96 | 55 | 41 | 43 % | **Niski (post-cleanup mid).** Pre-cleanup mocno zanieczyszczone budget-attach. Po quarantine 41 wartościowych docs (KSeF dokumentacja FA(2), Mały ZUS Plus, IP Box, kasy online, e-Doręczenia). |

**Wniosek:** core merytoryczny (eli + kis + podatki + biznes_gov + zus +
pip + uodo) trzyma 268/271 = ~99 % po quarantine. Główne ognisko
zanieczyszczenia było w `govpl` (43 % retain) — wynik agresywnego
fetch-all-attachments na podstronie budżetowej. Lekcja: dla `govpl`
trzeba węższego whitelisting URL-i / tagów `discovery_source`.

## 5. Opinia całościowa

**Czy dataset jest "good enough" dla chatbota wiedzy JDG?**

**Dla trybu MVP/Light (concierge-bot z linkami do źródeł):** TAK po
quarantine. 381 dokumentów × ~357 MB pokrywa 56/67 topiców, w tym wszystkie
51 z spec sec 4. Persony P1, P2, P5, P6, P7, P8, P9 są dobrze pokryte
(IP Box, ryczałt, VAT-UE, RODO, najem, BHP biuro). Persony P3, P4, P10
mają poważne luki w hot-2025/2026 (estoński CIT, DAC7, kasa online,
zatrudnianie cudzoziemców).

**Dla trybu Standard (RAG z generacją odpowiedzi):** wymagana ulga w
3 miejscach: (a) targetowana kolekcja 11 hot-2025/2026 topiców
(`biznes.gov.pl` procedury), (b) świeży snapshot stawek/limitów na
2026 (de minimis 300k EUR, mały ZUS+ 120k, ryczałt 12.5% najem >100k),
(c) retag 23 HTML-i z fallback `ceidg_rejestracja` na właściwe topiki.

**Dla trybu Pro (poradnictwo z disclaimerem prawnym):** dataset niewystarczający.
Brakuje całych obszarów (cło, akcyza, koncesje, e-Residency, AI Act,
sygnaliści) plus wymagany formal disclaimer + proces aktualizacji ≤30 dni
od zmiany prawa.

**Największe ryzyka:**

1. **Stale data risk** — Polski Ład 2022, składka zdrowotna 2025/2026,
   PKD 2025 — szybko się zmieniają. Bez procesu re-fetch dataset stanie
   się myląco-nieaktualny w 6-12 mies.
2. **Catch-all tag risk** — 23 HTML-e biznes_gov/govpl_html mają
   `ceidg_rejestracja` jako jedyny topic; jeśli RAG retrieval ma
   topic-bias, mogą one być over-recalled.
3. **Format-mix risk** — 201 PDF + 165 HTML + 18 DOCX. PDF z OCR
   jakością niższą niż HTML; DOCX wymaga osobnego loadera.
4. **eurlex/govpl-budget noise** — bez quarantine ~1/6 datasetu byłoby
   kompletnie nieprzydatne dla zapytań JDG.

**Rekomendacja działań w tej sesji:** wykonać quarantine (Krok 3),
zaktualizować raporty, zacommitować i wypchnąć. Hot-2025/2026 collection
zostawić jako follow-up (Opcja C, nowa sesja).




