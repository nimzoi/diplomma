# 13. MVP implementacji zbierania danych L1 (akty prawne)

## Cel
Uruchomić pierwszy, działający fragment pipeline’u danych: automatyczne pobieranie dokumentów **L1** (ustawy i RODO), zapis surowych PDF oraz metadanych umożliwiających audyt i powtórzenie procesu.

## Zakres wdrożony

1. **Źródło seedów** (`data/seeds/l1_legislation.csv`)
   - 8 pozycji MUST z `data_collection_spec.md`.
   - Każdy rekord: `eli_id`, `title`, `url`, `layer`, `topic_group`.

2. **Downloader** (`scripts/collect_l1_legislation.py`)
   - odczyt seedów CSV,
   - request z `Accept: application/pdf` i custom `User-Agent`,
   - retry z backoffem (1s, 4s, 16s),
   - walidacja `%PDF` + wykrywanie `Request Rejected`,
   - zapis PDF do `data/raw/legislation/{doc_id}.pdf`,
   - zapis sidecar JSON `data/raw/legislation/{doc_id}.json`,
   - dopisanie wpisu do manifestu `data/manifests/manifest_l1.csv`,
   - logowanie błędów do `data/logs/l1_failures.csv`.

3. **Manifest i audyt**
   - wspólny manifest zawiera m.in. URL, czas pobrania UTC, status HTTP, content-type, rozmiar, hash SHA-256, ścieżki lokalne.

## Wynik uruchomienia w obecnym środowisku

W tym środowisku wykonawczym endpointy zewnętrzne zwracają `403` (`Tunnel connection failed`), więc pobranie plików nie doszło do skutku.

To nie blokuje implementacji: pipeline, formaty plików i logika walidacyjno-audytowa są gotowe. Po uruchomieniu w środowisku z dostępem do tych domen skrypt zapisze PDF/JSON/manifest zgodnie ze specyfikacją.

## Uruchomienie

```bash
python3 scripts/collect_l1_legislation.py
```

Wariant testowy (szybki fail-fast):

```bash
python3 scripts/collect_l1_legislation.py --retries 1 --timeout 10
```


## Tryb obejścia (manual import)

Dla środowisk z blokadą proxy dodano skrypt:

```bash
python3 scripts/register_local_sources.py --input-dir /sciezka/do/pobranych_plikow
```

Tryb ten pozwala kontynuować projekt bez dostępu sieciowego: pliki lokalne są kopiowane do
`data/raw/legislation`, a następnie tworzone są sidecary JSON i wpisy manifestu identyczne
strukturalnie jak w trybie online.


## QA status i coverage

Dodano także skrypt raportujący jakość i pokrycie tematów:

```bash
python3 scripts/qa_dataset_status.py --manifest data/manifests/manifest_l1.csv --topic-catalog data/seeds/topic_catalog.csv
```

Skrypt pokazuje:
- liczbę rekordów i unikalnych hash/URL,
- potencjalne duplikaty,
- pokrycie względem katalogu 51 tematów (`data/seeds/topic_catalog.csv`).
