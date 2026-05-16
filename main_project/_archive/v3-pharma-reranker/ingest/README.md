# main_project/src/ingest/

Corpus scraping modules dla 6 strata farmakologii. Source of truth dla źródeł: [`thesis_research/sources_catalog.md`](../../../thesis_research/sources_catalog.md).

## Iteracja 0a — Feasibility (URPL probe)

Test pre-conditions DEC-001 kill criteria check przed pełnym scrape Iteracji 1.

### Phase 1 (synchronous, ~4h zegarowe wall-clock)

Pre-conditions #2-#6 z `sources_catalog.md` § Iteracja 0 — pre-conditions.

```bash
# 1. (Manualny one-off) discover URPL XML feed URL
#    Page: https://rejestry.ezdrowie.gov.pl/registry/rpl
#    Find: direct XML download link (daily snapshot)
#    Update: configs/sampling.yaml → urpl_xml_url

# 2. Smoke test: parse XML + sample, skip endpoint probing
cd D:/diplomma/main_project
uv run python -m src.ingest.iter0_urpl_probe --dry-run

# 3. Smoke test with limited probing (10 entries instead of 100)
uv run python -m src.ingest.iter0_urpl_probe --limit 10

# 4. Full probe (parse + 100 sample + endpoint probing + OCR detection)
uv run python -m src.ingest.iter0_urpl_probe

# Output: ../thesis_research/iter0_feasibility/
#   results.json
#   sample-list-{date}.csv
#   spot-check-psych-N05N06-{date}.csv
#   rpl-snapshot-{date}.xml
```

### Phase 2 (async, 24h background)

Pre-condition #1 — URPL uptime SLA. Designed dla background scheduling.

**Windows PowerShell:**
```powershell
cd D:\diplomma\main_project
Start-Job -ScriptBlock {
    Set-Location D:\diplomma\main_project
    uv run python -m src.ingest.iter0_uptime_probe `
        --url "<URPL_XML_URL>" `
        --hours 24 --interval-min 60
}
# Check status: Get-Job
# Receive output: Receive-Job -Id <N>
```

**Linux / WSL:**
```bash
cd /d/diplomma/main_project
nohup uv run python -m src.ingest.iter0_uptime_probe \
    --url "$URPL_XML_URL" \
    --hours 24 --interval-min 60 \
    > /tmp/uptime.log 2>&1 &
```

Output (append-only): `../thesis_research/iter0_feasibility/uptime.jsonl` + `uptime.summary.json` po finalizacji.

### Manual spot-check (Magda, ~60-90 min, IN parallel z phase 2)

Per `sources_catalog.md` § Strata 2 "Sprawdzanie pairing integrity" (competence-stratified, 10/10 psych subset).

1. Otwórz `../thesis_research/iter0_feasibility/spot-check-psych-N05N06-{date}.csv`
2. Per pair: pobierz ChPL + Ulotka PDF z URPL (CSV ma productID + nazwę leku)
3. Verify semantycznie: ChPL sekcja 4.1 (Wskazania) opisuje tę samą indykację co Ulotka sekcja 1 (Co to jest lek X)?
4. Update `../thesis_research/iter0_feasibility/iteration-0-feasibility-report.md` § Manual spot-check results table
5. Sign-off na alignment rate (czy 90% threshold met)

**Non-psych spot-check explicit OUT scope** (autorka nie ma competence farmakologicznej poza N05/N06) — dla pozostałych 90 par tylko proxy signal (productID match + data_modyfikacji ±1 day), flagged w R3 § 3.9 Świadome biases + R8 limitations.

## Iteracja 0b — Judge pilot selection (SEPARATE)

Patrz konspekt II.16 § Iteracja 0b. Wykonywane **po passing 0a kill criteria check**, nie w tym module.

## Iteracja 1 — Full corpus scrape (LATER)

Patrz konspekt II.16 § Iteracja 1. Wymaga passing 0a + 0b. Kod scrape per strata będzie dodany do `src/ingest/` jako osobne moduły (`urpl.py`, `aotmit.py`, `nfz.py`, `journals.py`).

## Dependencies

```toml
[project]
dependencies = [
    "requests>=2.32",
    "pdfplumber>=0.11",
    "numpy>=2.0",
    "pyyaml>=6.0",
]
```

Sync (z root projektu, NIE z main_project):

```bash
cd D:/diplomma
uv add requests pdfplumber numpy pyyaml
uv sync
```

## Gotchas

- **URPL XML schema** — heurystyka `parse_xml()` zakłada element names `productId`, `atcCode`, `dataModyfikacji`. Po pierwszym `--dry-run` zinspect XML (otwórz `rpl-snapshot-{date}.xml`) i adjust `parse_xml()` jeśli `Parsed 0 product entries`.
- **Encoding NFC** — polskie diakrytyki czasem droppują w ChPL; rozważ `unicodedata.normalize('NFC', text)` post-extraction (TODO w Iteracji 1).
- **Sample seed locked w `configs/sampling.yaml`** — `random_seed: 42`. **Nie zmieniaj** (DVC reproducibility, dokumentacja w `sources_catalog.md` § Strata 1).
- **`data_modyfikacji` Ulotki source** — ChPL ma w XML metadata; Ulotka może wymagać osobnego HTTP request lub być w response headers (Last-Modified). Po recon dostosuj `probe_product()`.
- **ChPL endpoint URL pattern** — assumed `/characteristic`, ale URPL może używać innego suffixu (`/chpl`, `/spc`). Adjust `CHPL_ENDPOINT_TEMPLATE` po manual recon.
- **OCR detection threshold** — `OCR_TEXT_MIN_CHARS=100` — pierwsze 3 strony. Niski threshold dla katalogu, ale jeśli HMM watershed widać że false positives, zwiększ.

## Reproducibility

```bash
# Recenzent może odtworzyć identyczną probe
cd D:/diplomma/main_project
uv run python -m src.ingest.iter0_urpl_probe --seed 42

# Lub z DVC-pulled snapshot (gdy DVC tracking aktywny)
dvc pull data/raw/rpl-snapshot-{date}.xml
uv run python -m src.ingest.iter0_urpl_probe --seed 42  # parses same XML
```
