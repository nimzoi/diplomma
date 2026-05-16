"""New sources scraping (15 portali/urzędów per Magda 2026-05-16 override).

Wszystkie sources używają wspólnego ``ArticleRecord`` schema + helperów
z :mod:`scrape.new_sources.common`. Każde źródło ma własny moduł
``<source>.py`` z funkcjami:

* ``discover_urls`` — sitemap walk / kategoria walk → set article URLs
* ``parse_article(html, url, idx)`` → ``ArticleRecord`` | None
* ``scrape(output_dir, max_articles, ...)`` — orchestration + write JSONL

Stub policy: jeśli source 3x bounce na WAF → skip + zapis do _failed.log,
NIE wymyślaj contentu.
"""
