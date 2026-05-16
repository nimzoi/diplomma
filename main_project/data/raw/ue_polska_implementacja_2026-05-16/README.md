# UE dyrektywa -> polska ustawa implementacyjna mapping

Generated: 2026-05-16

## Cel
Mapping kazdej UE dyrektywy konsumenckiej (CELEX id) na polska ustawe implementacyjna
(ELI id z systemu ISAP).

## Defense argument
"Claim w polish jest grounded w polish ustawie ktora implementuje UE dyrektywe X"
— mapping pozwala na cross-language cross-register citation chains w halu probe
+ verifier reasoning.

## Struktura
`mapping.json` — dict `{ celex_id: { celex_id, direktywa_id, title_pl,
data_publikacji, data_wejscia_w_zycie, transposition_deadline, polska_ustawa,
polska_ustawa_title, polska_implementation_date, notes } }`

## Kompletność
8/8 dyrektyw zmapowanych. Dyrektywa 2023/2225 (CCD II) bez polskiej
ustawy — transpozycja w toku (deadline 20 listopada 2025).

## Źródła
- Daty implementacji: EUR-Lex per-directive metadata
- ELI ID polskich ustaw: cross-reference z ISAP api.sejm.gov.pl/eli
- Date wejscia w zycie polskich ustaw: ISAP `data_wejscia_w_zycie` field

## License
- UE dyrektywy: (c) UE, free reuse per Decyzja 2011/833/UE (attribution req.)
- Polskie ustawy: art. 4 ust. 1 ustawy o prawie autorskim (DU/1994/83) — akty
  normatywne nie sa przedmiotem prawa autorskiego (public domain de facto)
