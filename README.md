# diplomma

Repozytorium robocze do inżynierki o chatbocie JDG (Cache-Augmented RAG).

## Co jest gotowe teraz

Dodałem działające MVP dla **etapu danych źródłowych L1** (akty prawne):

- lista seedów `data/seeds/l1_legislation.csv`,
- downloader `scripts/collect_l1_legislation.py` (retry, backoff, walidacja `%PDF`, sidecar JSON, manifest CSV),
- podstawowa struktura katalogów danych (`data/raw`, `data/manifests`, `data/logs`).

## Szybki start

```bash
python3 scripts/collect_l1_legislation.py
```

Po uruchomieniu powstaną:

- `data/raw/legislation/*.pdf` – surowe dokumenty,
- `data/raw/legislation/*.json` – metadane per plik,
- `data/manifests/manifest_l1.csv` – zbiorczy manifest audytowy.

## Parametry skryptu

```bash
python3 scripts/collect_l1_legislation.py \
  --seeds data/seeds/l1_legislation.csv \
  --raw-dir data/raw/legislation \
  --manifest data/manifests/manifest_l1.csv \
  --timeout 45 \
  --retries 3
```

## Co dalej (kolejne kroki)

1. Dodać crawlery L2 (podatki.gov.pl / pip.gov.pl / uodo.gov.pl) bez WAF.
2. Dodać osobny tryb browserowy dla biznes.gov.pl / zus.pl.
3. Dodać deduplikację hash+URL i walidację pokrycia 51 tematów.


## Obejście przy blokadzie sieci/proxy

Jeśli środowisko blokuje pobieranie z Internetu (np. `403 CONNECT tunnel failed`), możesz
wrzucić pliki ręcznie i zarejestrować je do manifestu/sidecarów:

```bash
python3 scripts/register_local_sources.py --input-dir /sciezka/do/pliki
```

Skrypt skopiuje pliki do `data/raw/legislation/`, wygeneruje `*.json` sidecar i dopisze wiersz
do `data/manifests/manifest_l1.csv` (z `source_url=local://manual-import` jeśli brak w seedach).


## QA pokrycia i duplikatów

Po zebraniu danych uruchom raport jakości:

```bash
python3 scripts/qa_dataset_status.py --manifest data/manifests/manifest_l1.csv --topic-catalog data/seeds/topic_catalog.csv
```

Tryb `--strict` zwraca kod 1 jeśli brakuje tematów z katalogu (przydatne do CI).
