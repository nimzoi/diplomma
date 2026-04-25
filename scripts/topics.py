"""51 catalog topics from descriptions/data_collection_spec.md section 4.

Each topic carries lowercase keyword regexes used to assign topic_ids
to a fetched document based on its URL/title. Multi-topic match is allowed.
"""
from __future__ import annotations

import re
from typing import Iterable

# (id, group, keywords)
TOPICS: list[tuple[str, str, list[str]]] = [
    # ZUS
    ("zus_ulga_na_start", "zus", ["ulga na start", "art. 18 prawo przedsiebiorc"]),
    ("zus_preferencyjny", "zus", ["preferencyjn", "obnizone skladki", "obniżone składki"]),
    ("zus_maly_zus_plus", "zus", ["maly zus", "mały zus", "art. 18c", "mzp"]),
    ("zus_wakacje_skladkowe", "zus", ["wakacje skladkow", "wakacje składkow", " rws"]),
    ("zus_skladka_zdrowotna_jdg", "zus", ["skladka zdrowotn", "składka zdrowotn"]),
    ("zus_zua_zwua_dra", "zus", ["zua", "zwua", " dra ", "deklaracja rozliczeniow"]),
    ("zus_zasilek_chorobowy_jdg", "zus", ["zasilek chorobow", "zasiłek chorobow", "ubezpieczenie chorobowe"]),
    ("zus_podstawa_wymiaru", "zus", ["podstawa wymiaru skladek", "podstawa wymiaru składek"]),
    ("zus_zawieszenie_dzialalnosci", "zus", ["zawieszenie dzialalnosci", "zawieszenie działalnosci", "zawieszenie działalności"]),
    ("zus_emerytura_jdg", "zus", ["emerytur", "zbieg tytulow", "zbieg tytułów"]),

    # PIT i formy opodatkowania
    ("pit_skala", "pit", ["skala podatkowa", "pit-36", "pit 36"]),
    ("pit_liniowy", "pit", ["podatek liniowy", "pit-36l", "art. 30c"]),
    ("pit_ryczalt", "pit", ["ryczalt od przychod", "ryczałt od przychod", "pit-28", "ustawa o ryczalcie", "ustawa o ryczałcie"]),
    ("pit_stawki_ryczalt_pkd", "pit", ["stawka ryczaltu", "stawka ryczałtu", "stawki ryczaltu", "stawki ryczałtu"]),
    ("pit_karta_podatkowa", "pit", ["karta podatkow", "pit-16a"]),
    ("pit_ip_box", "pit", ["ip box", "kwalifikowane prawo wlasnosci", "kwalifikowane prawo własności"]),
    ("pit_kup", "pit", ["koszty uzyskania przychod", "art. 22 pit"]),
    ("pit_amortyzacja", "pit", ["amortyzacj", "ksrodków trwa", "kśt", "wykaz rocznych stawek"]),
    ("pit_kpir", "pit", ["kpir", "podatkowej ksiegi przychodow", "podatkowej księgi przychodów", "ksiega przychodow", "księga przychodów"]),
    ("pit_ewidencja_ryczalt", "pit", ["ewidencja przychod", "ewidencji przychod"]),
    ("pit_roczny", "pit", ["pit roczny", "rozliczenie roczne", "termin pit", "kalendarz pit", "pit-37", "pit-36", "pit-28", "pit-36l", "rozliczenie pit", "twoj e-pit", "twój e-pit", "pit-d", "pit-o", "broszura do pit", "broszura pit"]),

    # VAT + JPK + KSeF
    ("vat_rejestracja", "vat", ["rejestracja vat", "vat-r"]),
    ("vat_zwolnienie_200k", "vat", ["zwolnieni", "art. 113", "200 tys", "200 000"]),
    ("vat_jpk", "vat", ["jpk_v7", "jpk vat", "jednolity plik kontroln"]),
    ("vat_ksef", "vat", ["ksef", "krajowy system e-faktur", "faktur ustrukturyzowan"]),
    ("vat_stawki", "vat", ["stawki vat", "matryca vat"]),
    ("vat_ue", "vat", ["vat-ue", "vat ue", "wdt", "wnt", "wewnatrzwspolnotow", "wewnątrzwspólnotow"]),
    ("vat_marza", "vat", ["vat marza", "vat marża", "procedura marz"]),
    ("vat_biala_lista", "vat", ["biala lista", "biała lista", "wykaz podatnikow vat", "wykaz podatników vat"]),

    # CEIDG
    ("ceidg_rejestracja", "ceidg", ["rejestracja ceidg", "wniosek ceidg-1", "ceidg-1"]),
    ("ceidg_pkd", "ceidg", ["kody pkd", "klasyfikacja pkd", " pkd ", "pkd 2007", "pkd 2025", "pkd2025", "polskiej klasyfikacji dzialalnosci", "polskiej klasyfikacji działalności"]),
    ("ceidg_zawieszenie", "ceidg", ["zawieszenie dzialalnosci", "zawieszenie działalnosci", "zawieszenie działalności", "zawieszenia"]),
    ("ceidg_wznowienie", "ceidg", ["wznowienie dzialalnosci", "wznowienie działalności", "wznowienie", "wznowienia"]),
    ("ceidg_zamkniecie", "ceidg", ["zamkniecie dzialalnosci", "zamknięcie działalności", "wykreslenie ceidg", "wykreślenie ceidg", "wykreslenie wpisu", "wykreślenie wpisu", "likwidacja firmy", "likwidacja dzialalnosci"]),
    ("ceidg_zmiana_wpisu", "ceidg", ["zmiana wpisu ceidg", "zmiana wpisu w ceidg", "zmiana wpisu", "zmiana danych ceidg", "aktualizacja wpisu"]),
    ("ceidg_dzialalnosc_nierejestrowana", "ceidg", ["dzialalnosc nierejestrowan", "działalność nierejestrowan", "art. 5 prawo przedsiebiorc"]),

    # Prawo pracy
    ("kp_umowa_o_prace", "kp", ["umowa o prace", "umowa o pracę", "kodeks pracy art. 25"]),
    ("kp_umowa_zlecenie", "kp", ["umowa zlecen", "art. 734 kodeks"]),
    ("kp_umowa_o_dzielo", "kp", ["umowa o dzielo", "umowa o dzieło"]),
    ("kp_czas_pracy", "kp", ["czas pracy", "ewidencja czasu pracy", "nadgodzin"]),
    ("kp_urlop", "kp", ["urlop wypoczynkow", "urlop macierzyn", "wymiar urlopu", "urlop opiekun"]),
    ("kp_wypowiedzenie", "kp", ["wypowiedzenie umow", "okres wypowiedzenia", "wypowiedzenie", "rozwiazanie umowy", "rozwiązanie umowy", "rozwiazumowy", "zwolnienie od pracy", "zwolnienia grupowe", "ul-rozwiazumowy", "ustanie stosunku pracy"]),
    ("kp_swiadectwo_pracy", "kp", ["swiadectwo pracy", "świadectwo pracy"]),
    ("kp_bhp_biuro", "kp", ["bhp biuro", "bhp praca zdaln", "szkolenie wstepne bhp", "szkolenie wstępne bhp", " bhp ", "bhp ", "ergonomi", "wypadek przy pracy", "ryzyk", "ocena ryzyka"]),

    # RODO
    ("rodo_mala_firma", "rodo", ["rodo mal", "rodo mał", "rodo przedsiebiorc", "rodo przedsiębiorc"]),
    ("rodo_rejestr_czynnosci", "rodo", ["rejestr czynnosci przetwarzania", "rejestr czynności przetwarzania", "art. 30 rodo"]),
    ("rodo_iod", "rodo", ["iod", "inspektor ochrony danych"]),
    ("rodo_klauzula_informacyjna", "rodo", ["klauzula informacyjn", "art. 13 rodo"]),
    ("rodo_monitoring", "rodo", ["monitoring pracownik", "art. 22^2 kodeks", "art. 222 kodeks", "monitoring", "monitoringu", "transmis", "kamery"]),
    ("rodo_naruszenie", "rodo", ["naruszenie ochrony danych", "zgloszenie do uodo", "zgłoszenie do uodo", "72h", "72 godzin"]),
    ("rodo_rekrutacja", "rodo", ["rodo rekrutacj", "klauzula cv", "rekrutacj", "kandydat", "zatrudnieni"]),

    # 2025-2026 hot topics (per second agent's taxonomy)
    ("b2b_test_samozatrudnienia", "hot2025", ["test samozatrudn", "samozatrudn", "b2b vs uop", "art. 5b", "fikcyjna jdg", "reklasyfikacja umowy", "stosunek pracy ukryty", "podporzadkowanie pracownicze", "podporządkowanie pracownicze", "ukryte zatrudnienie", "kontrakt b2b", "umowa b2b"]),
    ("b2b_zmiana_na_uop", "hot2025", ["przejscie na uop", "przejście na uop", "wymuszenie uop", "obowiazek uop", "konwersja b2b uop", "przeksztalcenie kontraktu b2b w uop", "art. 22 kp", "domniemanie stosunku pracy", "presja pip", "art. 22 § 1", "art. 22 par", "ukryte zatrudnienie", "fikcyjne samozatrudnieni", "samozatrudnienie a stosunek pracy", "przeksztalcenie umowy", "przekształcenie umowy", "umowa o wspolprace zamiast", "umowa o współprace zamiast", "kontrola pip umow"]),
    ("polski_lad_skladka_zdrowotna_2026", "hot2025", ["polski lad", "polski ład", "skladka zdrowotna 2026", "skladka zdrowotna 2025", "ryczałtowa skladka zdrowotna", "reforma skladki"]),
    ("ksef_etapy_2026", "hot2025", ["ksef fa(3)", "ksef fa(2)", "ksef etap", "ksef obowiazek", "ksef zwolnieni", "ksef mikro", "faktury konsumenckie ksef"]),
    ("e_doreczenia_obowiazek", "hot2025", ["e-doreczeni", "e-doręczeni", "ade", "adres do doreczen elektroniczn"]),
    ("dac7_platformy", "hot2025", ["dac7", "dac 7", "dac-7", "platformy cyfrowe", "platforma cyfrowa", "allegro vinted booking raportowanie", "operator platformy", "operatorow platform", "operatorów platform", "sprzedawcy raportowani", "raportowanie platform", "dpi-1", "dpi 1", "digital platform information", "raportowanie sprzedaw", "raportujace transakcje"]),
    ("jpk_cit_jpk_kr", "hot2025", ["jpk_cit", "jpk_kr_pd", "jpk_kr", "jpk_st_kr", "jpk_pkpir", "jpk_ewp", "jpk_st", "elektroniczne ksiegi cit", "elektroniczne księgi cit", "elektroniczne ksiegi rachunkow", "elektroniczne księgi rachunkow", "ksiegi rachunkowe w podatku pit", "księgi rachunkowe w podatku pit", "ksiegi rachunkowe pit", "księgi rachunkowe pit", "cyfryzacji dokumentacji ksiegowej", "cyfryzacji dokumentacji księgowej", "struktury jpk w podatkach dochodow", "elektroniczne ksiegi i ewidencje podatkow", "elektroniczne księgi i ewidencje podatkow"]),
    ("ulga_ekspansja_prototyp_robotyzacja", "hot2025", ["ulga na ekspansj", "ulga na prototyp", "ulga na robotyzacj", "ulga b+r", "ulga prowzrostow", "ulga sponsoringow", "ulga na zatrudnieni innowacyjn", "ulga na ipo", "ulga konsolidacyjn", "ulga na innowacyjn", "podatkowe wsparcie ekspansj", "ulga ip box", "robotyzacja podatk", "art. 18ea", "art. 18eb", "art. 18ec", "art. 18ed", "art. 38eb", "art. 26ga", "art. 26gb", "art. 26ha", "art. 52jb"]),
    ("estonski_cit", "hot2025", ["estonski cit", "estoński cit", "ryczalt od dochodow spolek", "ryczałt od dochodów spółek", "ryczałt od dochodow spolek", "rds cit", "cit-8e", "cit 8e", "art. 28c", "art. 28j", "art. 28k", "art. 28m", "art. 28n", "art. 28o", "art. 28p", "art. 28q", "art. 28r", "art. 28s", "art. 28t", "rozdzial 6b ustawy o cit", "rozdział 6b ustawy o cit", "ukryte zyski estonsk", "ukryte zyski estońsk"]),
    ("pomoc_de_minimis", "hot2025", ["de minimis", "300 tys eur", "sudop", "pomoc publiczna kumulacj", "pomoc publiczna", "rozporzadzenie 2023/2831", "rozporządzenie 2023/2831", "rozporzadzenie 2831/2023", "art. 37 ust. 1 ustawy o postepowaniu", "kumulacja pomocy", "pomocy de minimis", "zaswiadczenie de minimis", "zaświadczenie de minimis", "pomoc de minimis"]),
    ("aml_giif_jdg", "hot2025", ["aml", "giif", "generalny inspektor informacji finans", "obowiazki przeciwdzialan"]),
    ("kasa_fiskalna_online", "hot2025", ["kasa fiskaln", "kasy fiskalne", "kasy rejestrujac", "kasa online", "kasa wirtualn", "kasa rejestruj", "kasa online ", "fiskalizacja", "centralne repozytorium kas", "ewidencja sprzedazy kas", "ulga na zakup kasy", "ulga na zakup kas", "kasa fiskalna online", "raportowanie kas", "online kas"]),
    ("zatrudnianie_cudzoziemcow", "hot2025", ["cudzoziemiec", "cudzoziemc", "ukrai", "oswiadczenie powierzeni", "powiadomienie pup", "praca cudzoziemca", "zezwolenie na prace", "zezwolenie na pracę", "zezwolenia na prace", "obywatel ukrainy", "umks", "udzielenie ochrony tymczasow", "specustawa", "uchodzc"]),
    ("crbr_beneficjent_rzeczywisty", "hot2025", ["crbr", "centralny rejestr beneficjent", "beneficjent rzeczywisty", "beneficjenci rzeczywisci", "beneficjenci rzeczywiści", "beneficjenta rzeczywist", "rejestr osob ktore kontroluja firmy", "rejestr osób które kontrolują firmy", "rejestr osob, ktore kontroluja firmy", "art. 58 ustawy aml", "ustawy o przeciwdziałaniu praniu pieniędzy", "ustawy o przeciwdzialaniu praniu pieniedzy"]),
    ("przeksztalcenie_jdg_spzoo", "hot2025", ["przeksztalcenie jdg", "przeksztalcenie spolki", "jdg w spolke", "jdg na sp. z o.o", "jdg w spolke", "jdg w spółkę", "jdg w spolce", "jdg w spółce", "przeksztalcic firme jednoosob", "przekształcić firmę jednoosob", "przeksztalcenie firmy jednoosobow", "przekształcenie firmy jednoosobow", "przeksztalcenie przedsiebiorcy", "przekształcenie przedsiębiorcy", "przeksztalcenie dzialalnosci gospodarczej", "przekształcenie działalności gospodarczej", "przeksztalcic firme", "przekształcić firmę", "art. 551 ksh", "art. 5841 ksh", "plan przeksztalcenia", "plan przekształcenia", "spolka kapitalowa jednoosobow"]),
    ("faktoring_cesja_wierzytelnosci", "hot2025", ["faktoring", "cesja wierzytelnosci", "cesja wierzytelności", "art. 509 kc", "split payment", "mechanizm podzielonej platnosci", "mechanizm podzielonej płatności", "mpp", "rachunek vat", "podzielona platnosc", "podzielona płatność", "split-payment", "rachunek vat ", "art. 108a", "art. 108b", "art. 108c", "wierzytelnoscia", "wierzytelnością", "kupno wierzytelnosci", "kupno wierzytelności", "factoring"]),
]


def _norm(s: str) -> str:
    return s.lower()


def assign_topics(*texts: str) -> list[str]:
    """Return list of topic ids whose keyword appears in any text."""
    blob = " ".join(_norm(t or "") for t in texts)
    ids: list[str] = []
    for tid, _grp, kws in TOPICS:
        for kw in kws:
            if kw in blob:
                ids.append(tid)
                break
    return ids


def all_topic_ids() -> list[str]:
    return [t[0] for t in TOPICS]


def topic_meta(tid: str) -> tuple[str, str, list[str]] | None:
    for t in TOPICS:
        if t[0] == tid:
            return t
    return None
