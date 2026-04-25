# Dataset coverage report

Auto-generated from `data/manifest.csv`. Run `python3 scripts/build_coverage_report.py` to refresh.

## KPI vs spec section 16

| Kryterium | Wartosc |
|---|---|
| Liczba dokumentow | 527 |
| Pokrycie tematyczne (51) | 67/51 |
| Warstwa L1 | 41 |
| Warstwa L2 | 299 |
| Stosunek .gov.pl | 527/527 |
| Total MB on disk | 387.7 |

## By source

| Source | Count |
|---|---|
| kis | 187 |
| biznes_gov | 146 |
| govpl | 62 |
| eli | 37 |
| pip | 37 |
| podatki | 32 |
| zus | 16 |
| uodo | 6 |
| eurlex | 4 |

## By layer

| Layer | Count |
|---|---|
| L2 | 299 |
| L3 | 187 |
| L1 | 41 |

## By format

| Format | Count |
|---|---|
| html | 346 |
| pdf | 177 |
| docx | 4 |

## Topic coverage (51 topics)

| topic_id | group | docs |
|---|---|---|
| zus_ulga_na_start | zus | 7 |
| zus_preferencyjny | zus | 39 |
| zus_maly_zus_plus | zus | 9 |
| zus_wakacje_skladkowe | zus | 9 |
| zus_skladka_zdrowotna_jdg | zus | 19 |
| zus_zua_zwua_dra | zus | 22 |
| zus_zasilek_chorobowy_jdg | zus | 7 |
| zus_podstawa_wymiaru | zus | 11 |
| zus_zawieszenie_dzialalnosci | zus | 11 |
| zus_emerytura_jdg | zus | 35 |
| pit_skala | pit | 27 |
| pit_liniowy | pit | 36 |
| pit_ryczalt | pit | 27 |
| pit_stawki_ryczalt_pkd | pit | 7 |
| pit_karta_podatkowa | pit | 8 |
| pit_ip_box | pit | 26 |
| pit_kup | pit | 30 |
| pit_amortyzacja | pit | 16 |
| pit_kpir | pit | 27 |
| pit_ewidencja_ryczalt | pit | 4 |
| pit_roczny | pit | 20 |
| vat_rejestracja | vat | 10 |
| vat_zwolnienie_200k | vat | 91 |
| vat_jpk | vat | 28 |
| vat_ksef | vat | 29 |
| vat_stawki | vat | 18 |
| vat_ue | vat | 21 |
| vat_marza | vat | 3 |
| vat_biala_lista | vat | 8 |
| ceidg_rejestracja | ceidg | 116 |
| ceidg_pkd | ceidg | 19 |
| ceidg_zawieszenie | ceidg | 23 |
| ceidg_wznowienie | ceidg | 27 |
| ceidg_zamkniecie | ceidg | 8 |
| ceidg_zmiana_wpisu | ceidg | 6 |
| ceidg_dzialalnosc_nierejestrowana | ceidg | 10 |
| kp_umowa_o_prace | kp | 17 |
| kp_umowa_zlecenie | kp | 3 |
| kp_umowa_o_dzielo | kp | 4 |
| kp_czas_pracy | kp | 22 |
| kp_urlop | kp | 17 |
| kp_wypowiedzenie | kp | 21 |
| kp_swiadectwo_pracy | kp | 10 |
| kp_bhp_biuro | kp | 70 |
| rodo_mala_firma | rodo | 8 |
| rodo_rejestr_czynnosci | rodo | 2 |
| rodo_iod | rodo | 39 |
| rodo_klauzula_informacyjna | rodo | 5 |
| rodo_monitoring | rodo | 8 |
| rodo_naruszenie | rodo | 3 |
| rodo_rekrutacja | rodo | 95 |
| b2b_test_samozatrudnienia | hot2025 | 17 |
| b2b_zmiana_na_uop | hot2025 | 11 |
| polski_lad_skladka_zdrowotna_2026 | hot2025 | 4 |
| ksef_etapy_2026 | hot2025 | 3 |
| e_doreczenia_obowiazek | hot2025 | 151 |
| dac7_platformy | hot2025 | 13 |
| jpk_cit_jpk_kr | hot2025 | 20 |
| ulga_ekspansja_prototyp_robotyzacja | hot2025 | 12 |
| estonski_cit | hot2025 | 33 |
| pomoc_de_minimis | hot2025 | 9 |
| aml_giif_jdg | hot2025 | 2 |
| kasa_fiskalna_online | hot2025 | 19 |
| zatrudnianie_cudzoziemcow | hot2025 | 44 |
| crbr_beneficjent_rzeczywisty | hot2025 | 7 |
| przeksztalcenie_jdg_spzoo | hot2025 | 13 |
| faktoring_cesja_wierzytelnosci | hot2025 | 17 |

Covered: **67/51**.  Gaps: **0**.

## Biggest files

| size MB | source | path |
|---|---|---|
| 69.4 | eli | `raw/legislation/eli_DU_2024_1936.pdf` |
| 28.9 | eli | `raw/legislation/eli_DU_1998_930.pdf` |
| 26.1 | eli | `raw/legislation/eli_DU_1998_887.pdf` |
| 13.8 | eli | `raw/legislation/eli_DU_1974_141.pdf` |
| 7.8 | eli | `raw/legislation/eli_DU_1991_350.pdf` |
| 7.0 | uodo | `raw/uodo/uodo_5687_poradnik_dotycz_cy_narusze_ochrony_danych_osobowych_plik_pdf.pdf` |
| 6.1 | pip | `raw/pip/bezpiecznie-i-zgodnie-z-prawem-lista-kontrolna-z-komentarzemp35223.pdf` |
| 5.6 | pip | `raw/pip/bhp-w-biurze.pdf` |
| 5.4 | govpl | `raw/govpl/govpl_dokumentacja_struktury_logicznej_e-faktury_fa2_dokumentacja8203_struktury8203_lo.pdf` |
| 5.2 | pip | `raw/pip/prewencja-wypadkowa-lista-kontrolna-z-komentarzem.pdf` |

## Quarantine

**71 dokumentow** zarekwarantowanych przez Agent B audit (off-topic / niska jakosc / redundant).
Pliki w `data/quarantine/<source>/`, wpisy w manifescie zachowane z `quality_flag=quarantine`.

| Source | Count |
|---|---|
| govpl | 55 |
| pip | 9 |
| zus | 3 |
| uodo | 2 |
| eurlex | 1 |
| biznes_gov | 1 |

Plus `data/quarantine/_failed/` z **22** items z fetch-time validation (404, brak PDF magic, WAF redirects).

## Notes

- biznes.gov.pl Layer-2 was not collected because the portal sits behind a WAF (Akamai). Per spec section 19 we did not bypass it. Consider running undetected-chromedriver locally for that source if needed.
- KIS individual interpretations (Layer-3) require headless browser (sip.mf.gov.pl is JS-driven). Not collected here.
- All HTTP fetch attempts including failures are logged in `data/logs/fetch_log.ndjson`.