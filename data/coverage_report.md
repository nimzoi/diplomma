# Dataset coverage report

Auto-generated from `data/manifest.csv`. Run `python3 scripts/build_coverage_report.py` to refresh.

## KPI vs spec section 16

| Kryterium | Wartosc |
|---|---|
| Liczba dokumentow | 203 |
| Pokrycie tematyczne (51) | 51/51 |
| Warstwa L1 | 42 |
| Warstwa L2 | 161 |
| Stosunek .gov.pl | 203/203 |
| Total MB on disk | 337.2 |

## By source

| Source | Count |
|---|---|
| pip | 67 |
| podatki | 64 |
| eli | 37 |
| zus | 19 |
| uodo | 8 |
| eurlex | 5 |
| biznes_gov | 3 |

## By layer

| Layer | Count |
|---|---|
| L2 | 161 |
| L1 | 42 |

## By format

| Format | Count |
|---|---|
| pdf | 203 |

## Topic coverage (51 topics)

| topic_id | group | docs |
|---|---|---|
| zus_ulga_na_start | zus | 2 |
| zus_preferencyjny | zus | 1 |
| zus_maly_zus_plus | zus | 1 |
| zus_wakacje_skladkowe | zus | 1 |
| zus_skladka_zdrowotna_jdg | zus | 13 |
| zus_zua_zwua_dra | zus | 2 |
| zus_zasilek_chorobowy_jdg | zus | 3 |
| zus_podstawa_wymiaru | zus | 5 |
| zus_zawieszenie_dzialalnosci | zus | 2 |
| zus_emerytura_jdg | zus | 6 |
| pit_skala | pit | 48 |
| pit_liniowy | pit | 3 |
| pit_ryczalt | pit | 4 |
| pit_stawki_ryczalt_pkd | pit | 1 |
| pit_karta_podatkowa | pit | 2 |
| pit_ip_box | pit | 2 |
| pit_kup | pit | 1 |
| pit_amortyzacja | pit | 2 |
| pit_kpir | pit | 5 |
| pit_ewidencja_ryczalt | pit | 2 |
| pit_roczny | pit | 15 |
| vat_rejestracja | vat | 3 |
| vat_zwolnienie_200k | vat | 3 |
| vat_jpk | vat | 10 |
| vat_ksef | vat | 3 |
| vat_stawki | vat | 13 |
| vat_ue | vat | 2 |
| vat_marza | vat | 2 |
| vat_biala_lista | vat | 1 |
| ceidg_rejestracja | ceidg | 9 |
| ceidg_pkd | ceidg | 2 |
| ceidg_zawieszenie | ceidg | 3 |
| ceidg_wznowienie | ceidg | 4 |
| ceidg_zamkniecie | ceidg | 5 |
| ceidg_zmiana_wpisu | ceidg | 6 |
| ceidg_dzialalnosc_nierejestrowana | ceidg | 3 |
| kp_umowa_o_prace | kp | 15 |
| kp_umowa_zlecenie | kp | 3 |
| kp_umowa_o_dzielo | kp | 3 |
| kp_czas_pracy | kp | 5 |
| kp_urlop | kp | 22 |
| kp_wypowiedzenie | kp | 4 |
| kp_swiadectwo_pracy | kp | 2 |
| kp_bhp_biuro | kp | 33 |
| rodo_mala_firma | rodo | 10 |
| rodo_rejestr_czynnosci | rodo | 1 |
| rodo_iod | rodo | 2 |
| rodo_klauzula_informacyjna | rodo | 1 |
| rodo_monitoring | rodo | 2 |
| rodo_naruszenie | rodo | 2 |
| rodo_rekrutacja | rodo | 1 |

Covered: **51/51**.  Gaps: **0**.

## Biggest files

| size MB | source | path |
|---|---|---|
| 69.4 | eli | `raw/legislation/eli_DU_2024_1936.pdf` |
| 28.9 | eli | `raw/legislation/eli_DU_1998_930.pdf` |
| 26.1 | eli | `raw/legislation/eli_DU_1998_887.pdf` |
| 14.4 | pip | `raw/pip/PORADNIK-DOTUBEZPIECZENIASAZ-1.pdf` |
| 13.8 | eli | `raw/legislation/eli_DU_1974_141.pdf` |
| 7.8 | eli | `raw/legislation/eli_DU_1991_350.pdf` |
| 7.0 | uodo | `raw/uodo/uodo_5687_poradnik_dotycz_cy_narusze_ochrony_danych_osobowych_plik_pdf.pdf` |
| 6.1 | pip | `raw/pip/bezpiecznie-i-zgodnie-z-prawem-lista-kontrolna-z-komentarzemp35223.pdf` |
| 5.6 | pip | `raw/pip/uzytkowanie-maszyn-minimalne-wymagania-dotyczne-bhp.pdf` |
| 5.6 | pip | `raw/pip/bhp-w-biurze.pdf` |

## Quarantine (rejected files)

`data/quarantine/_failed/` has **22** rejected items (404, missing PDF magic, WAF redirects).

## Notes

- biznes.gov.pl Layer-2 was not collected because the portal sits behind a WAF (Akamai). Per spec section 19 we did not bypass it. Consider running undetected-chromedriver locally for that source if needed.
- KIS individual interpretations (Layer-3) require headless browser (sip.mf.gov.pl is JS-driven). Not collected here.
- All HTTP fetch attempts including failures are logged in `data/logs/fetch_log.ndjson`.