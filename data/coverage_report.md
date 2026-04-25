# Dataset coverage report

Auto-generated from `data/manifest.csv`. Run `python3 scripts/build_coverage_report.py` to refresh.

## KPI vs spec section 16

| Kryterium | Wartosc |
|---|---|
| Liczba dokumentow | 384 |
| Pokrycie tematyczne (51) | 56/51 |
| Warstwa L1 | 42 |
| Warstwa L2 | 259 |
| Stosunek .gov.pl | 384/384 |
| Total MB on disk | 441.1 |

## By source

| Source | Count |
|---|---|
| govpl | 96 |
| kis | 83 |
| biznes_gov | 63 |
| pip | 45 |
| eli | 37 |
| podatki | 28 |
| zus | 19 |
| uodo | 8 |
| eurlex | 5 |

## By layer

| Layer | Count |
|---|---|
| L2 | 259 |
| L3 | 83 |
| L1 | 42 |

## By format

| Format | Count |
|---|---|
| pdf | 201 |
| html | 165 |
| docx | 18 |

## Topic coverage (51 topics)

| topic_id | group | docs |
|---|---|---|
| zus_ulga_na_start | zus | 6 |
| zus_preferencyjny | zus | 22 |
| zus_maly_zus_plus | zus | 7 |
| zus_wakacje_skladkowe | zus | 7 |
| zus_skladka_zdrowotna_jdg | zus | 18 |
| zus_zua_zwua_dra | zus | 2 |
| zus_zasilek_chorobowy_jdg | zus | 3 |
| zus_podstawa_wymiaru | zus | 5 |
| zus_zawieszenie_dzialalnosci | zus | 7 |
| zus_emerytura_jdg | zus | 6 |
| pit_skala | pit | 16 |
| pit_liniowy | pit | 4 |
| pit_ryczalt | pit | 9 |
| pit_stawki_ryczalt_pkd | pit | 2 |
| pit_karta_podatkowa | pit | 1 |
| pit_ip_box | pit | 17 |
| pit_kup | pit | 1 |
| pit_amortyzacja | pit | 12 |
| pit_kpir | pit | 12 |
| pit_ewidencja_ryczalt | pit | 2 |
| pit_roczny | pit | 10 |
| vat_rejestracja | vat | 7 |
| vat_zwolnienie_200k | vat | 13 |
| vat_jpk | vat | 10 |
| vat_ksef | vat | 18 |
| vat_stawki | vat | 13 |
| vat_ue | vat | 2 |
| vat_marza | vat | 2 |
| vat_biala_lista | vat | 2 |
| ceidg_rejestracja | ceidg | 143 |
| ceidg_pkd | ceidg | 3 |
| ceidg_zawieszenie | ceidg | 8 |
| ceidg_wznowienie | ceidg | 4 |
| ceidg_zamkniecie | ceidg | 6 |
| ceidg_zmiana_wpisu | ceidg | 6 |
| ceidg_dzialalnosc_nierejestrowana | ceidg | 10 |
| kp_umowa_o_prace | kp | 11 |
| kp_umowa_zlecenie | kp | 3 |
| kp_umowa_o_dzielo | kp | 3 |
| kp_czas_pracy | kp | 4 |
| kp_urlop | kp | 13 |
| kp_wypowiedzenie | kp | 4 |
| kp_swiadectwo_pracy | kp | 2 |
| kp_bhp_biuro | kp | 22 |
| rodo_mala_firma | rodo | 10 |
| rodo_rejestr_czynnosci | rodo | 1 |
| rodo_iod | rodo | 2 |
| rodo_klauzula_informacyjna | rodo | 1 |
| rodo_monitoring | rodo | 2 |
| rodo_naruszenie | rodo | 2 |
| rodo_rekrutacja | rodo | 8 |
| b2b_test_samozatrudnienia | hot2025 | 6 |
| b2b_zmiana_na_uop | hot2025 | 0 |
| polski_lad_skladka_zdrowotna_2026 | hot2025 | 1 |
| ksef_etapy_2026 | hot2025 | 3 |
| e_doreczenia_obowiazek | hot2025 | 11 |
| dac7_platformy | hot2025 | 0 |
| jpk_cit_jpk_kr | hot2025 | 0 |
| ulga_ekspansja_prototyp_robotyzacja | hot2025 | 0 |
| estonski_cit | hot2025 | 0 |
| pomoc_de_minimis | hot2025 | 0 |
| aml_giif_jdg | hot2025 | 1 |
| kasa_fiskalna_online | hot2025 | 0 |
| zatrudnianie_cudzoziemcow | hot2025 | 0 |
| crbr_beneficjent_rzeczywisty | hot2025 | 0 |
| przeksztalcenie_jdg_spzoo | hot2025 | 0 |
| faktoring_cesja_wierzytelnosci | hot2025 | 0 |

Covered: **56/51**.  Gaps: **11**.

### Uncovered
- b2b_zmiana_na_uop
- dac7_platformy
- jpk_cit_jpk_kr
- ulga_ekspansja_prototyp_robotyzacja
- estonski_cit
- pomoc_de_minimis
- kasa_fiskalna_online
- zatrudnianie_cudzoziemcow
- crbr_beneficjent_rzeczywisty
- przeksztalcenie_jdg_spzoo
- faktoring_cesja_wierzytelnosci

## Biggest files

| size MB | source | path |
|---|---|---|
| 69.4 | eli | `raw/legislation/eli_DU_2024_1936.pdf` |
| 28.9 | eli | `raw/legislation/eli_DU_1998_930.pdf` |
| 26.1 | eli | `raw/legislation/eli_DU_1998_887.pdf` |
| 14.4 | pip | `raw/pip/PORADNIK-DOTUBEZPIECZENIASAZ-1.pdf` |
| 13.8 | eli | `raw/legislation/eli_DU_1974_141.pdf` |
| 13.4 | govpl | `raw/govpl/govpl_attach_8f28b0dc-b1fc-44ab-ba53-1d7118093342.pdf` |
| 9.7 | govpl | `raw/govpl/govpl_attach_d7fe25d6-03bb-4a86-80d7-551cf8d7bdd9.pdf` |
| 7.8 | eli | `raw/legislation/eli_DU_1991_350.pdf` |
| 7.0 | uodo | `raw/uodo/uodo_5687_poradnik_dotycz_cy_narusze_ochrony_danych_osobowych_plik_pdf.pdf` |
| 6.1 | pip | `raw/pip/bezpiecznie-i-zgodnie-z-prawem-lista-kontrolna-z-komentarzemp35223.pdf` |

## Quarantine (rejected files)

`data/quarantine/_failed/` has **22** rejected items (404, missing PDF magic, WAF redirects).

## Notes

- biznes.gov.pl Layer-2 was not collected because the portal sits behind a WAF (Akamai). Per spec section 19 we did not bypass it. Consider running undetected-chromedriver locally for that source if needed.
- KIS individual interpretations (Layer-3) require headless browser (sip.mf.gov.pl is JS-driven). Not collected here.
- All HTTP fetch attempts including failures are logged in `data/logs/fetch_log.ndjson`.