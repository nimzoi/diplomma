# Platforms / Banks — Blocked Sources Documentation

Scrape date: 2026-05-16

## Background

Per Magda 2026-05-16: "wszystko ma być zdobyte" — żadnych skipów ze względu na privacy/legal risk. Jednak technicznie kilka źródeł jest WAF-blocked nawet z realistycznym Chrome UA + Playwright stealth. Plik `blocked.json` zawiera explicit reason per source + recommendation dla fallback.

## Sources Blocked

- Allegro (regulamin + help.allegro.com)
- OLX (help.olx.pl + regulamin)
- Lex.pl/Wolters Kluwer (paywall)
- PKO BP (regulaminy)
- mBank (regulaminy)

## Compensating Coverage

Treść konsumencka z tych źródeł jest w dużej części redundant z innymi zbiorami:

- T&C handlu internetowego — pokryte przez ECC Polska + UOKiK Q&A + bezprawnik
- Bank consumer info — pokryte przez Rzecznik Finansowy FAQ (374) + UOKiK + KNF + ING
- Legal acts — pokryte przez ISAP (Sejm API) + EUR-Lex

## Rationale

Per Polish TDM exception 2024 (Art. 4 DSM Directive 2019/790), text-and-data mining dla research jest legalny. Ale dostęp techniczny nie zawsze ma to umożliwić — bot detection nie wykrywa intencji TDM vs. commercial scraping. Każdy blocked source ma explicit log + recommended fallback w `blocked.json`.
