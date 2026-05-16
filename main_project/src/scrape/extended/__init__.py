"""Extended consumer rights scrape — Iteracja 0 (2026-05-16).

Adapter scripts dla rozszerzenia Polish CitationBench dataset poza
oryginalne 4 źródła + UOKiK Q&A + ELI ustawy.

Adaptery:
- ``federacja_konsumentow`` — porady z federacja-konsumentow.org.pl
- ``rzecznik_finansowy`` — FAQ + porady z rf.gov.pl
- ``gov_pl_consumer`` — oficjalne strony gov.pl/web/gov dla konsumentów
- ``uokik_news`` — aktualnosci.php z uokik.gov.pl (urzędowe)
- ``wikipedia_consumer`` — Polish Wikipedia consumer-law articles (CC BY-SA 4.0)

Output: ``data/raw/extended_consumer_2026-05-16/<source>.jsonl`` +
``<source>_meta.json`` per adapter.

Schema rekordów:
- Q&A pairs → ``QAGoldPair`` (jeśli explicit answer + cited articles)
- Articles / chunks → ``EncyclopedicChunk`` (nowy, dla Wikipedia + porady)

Wszystkie scrape'y są rate-limited (1 req/s) i NFC-normalizują tekst.
"""
