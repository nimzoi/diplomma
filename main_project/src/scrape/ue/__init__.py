"""EUR-Lex scrape package — UE dyrektywy + TSUE orzeczenia (polska wersja).

Modules:
- ``common`` — Fetcher, NFC normalize, citation builders
- ``dyrektywy`` — 8 dyrektyw konsumenckich (CRD, DCD, SGD, Omnibus, UCT, UCPD, CCD I, CCD II)
- ``tsue`` — top ~30-50 orzeczen TSUE w sprawach konsumenckich (Dziubak, Kasler, etc.)
- ``mapping`` — UE dyrektywa -> polska ustawa implementacyjna (DU/yyyy/nnnn)

License source corpusu: EUR-Lex content jest objete Decyzja 2011/833/UE
o reuse public-sector information — wolne uzycie z attribution (link to EUR-Lex).
"""
