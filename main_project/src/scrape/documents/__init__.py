"""Pełne dokumenty consumer rights — scraper long-form materiałów polskiej ochrony konsumenta.

Komplementarny do `src/scrape/uokik/scrape_qa.py` (Q&A) i `src/scrape/legal_fora/`
(forum questions). Zbiera EXCLUSIVELY long-form dokumenty (>500 słów):
  - PDF poradniki i broszury UOKiK
  - PDF analizy/raporty Rzecznika Finansowego
  - HTML długie artykuły Federacji Konsumentów
  - Court rulings z orzeczenia.ms.gov.pl (sygnatura + uzasadnienie)
  - PDF poradniki Federacji Konsumentów

Zob. `scrape_consumer_docs.py` dla CLI entry point.
"""
