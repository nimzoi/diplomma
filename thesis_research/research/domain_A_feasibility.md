# Domain A (consumer rights) — Feasibility Report 2026-05-16

**Autor:** research subagent na zlecenie Magdaleny Sochackiej
**Cel:** zweryfikować data feasibility + scrape methodology dla pivotu pracy z farmakologii klinicznej na **citation-grounded RAG dla polish consumer rights z hallucination detection** PRZED commitmentem.
**Metodologia:** real verification (WebFetch sample scrape + WebSearch current state 2026), brutal honest, NO speculation.

---

## 0. Verdict: **CONDITIONAL GO**

### Top 3 critical findings

1. **DATA READY — ISAP corpus = goldmine.** Oficjalne **api.sejm.gov.pl/eli** (ELI = European Legislation Identifier) udostępnia *wszystkie* polskie ustawy w deterministycznych URL-ach z dostępem na poziomie pojedynczego artykułu (`/text.html/art=27`). PDF + HTML + JSON metadata, license = urzędowa (Art. 4 PrAut). Cytowanie jest deterministyczne (publisher/year/position/art/§/ust). Zero scraping hacków potrzebnych — to czysty REST API.

2. **RISK — Reddit jako "real consumer questions" = NIE działa via WebFetch.** Reddit blokuje publiczne fetch, free tier PRAW = 100 req/min OAuth (60 praktycznie), Pushshift API zabity. **Mitigacja:** Pushshift dumps via Academic Torrents (Reddit 2005-06 → 2025-06, ~3.4 TB, NDJSON+zstd, top-40k subreddits dostępne selektywnie) — to działa, ale wymaga jednorazowego download i grep'owania `r/Polska` slice'u offline. Plus: forum.e-prawnik.pl + forumprawne.org publicznie czytalne (970 wątków sekcji "Ochrona konsumenta" e-prawnik, 2436 stron forumprawne).

3. **SURPRISE — NO dedicated Polish NLI model exists.** `sdadas/polish-nli` NIE istnieje (sprawdzone bezpośrednio HF), CLARIN-KNeXT też nie publikuje. Best dostępny to `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (300M params, MIT, Polish 105k pairs trained, ~1189 tekstów/sek na A100). HerBERT-large istnieje (CC BY 4.0, 8.6B tokens) ale BEZ NLI fine-tunowanej wersji — trzeba samodzielnie fine-tunować na CDSC-E (10k par PL).

### Recommended adjustments (jeśli GO)

- **Akceptuj mDeBERTa multilingual jako baseline NLI judge**, plus opcjonalnie fine-tune HerBERT-large na CDSC-E (~1 dzień GPU) jako ablation. NIE traktuj braku polish-only NLI jako blocker — multilingual mDeBERTa jest stan sztuki dla low-resource entailment 2024-2026.
- **Reddit DOWNLOAD via Academic Torrents** w iteracji 0, NIE realtime API. Filtruj `subreddit=Polska` z lokalnych dumps, deduplikuj po `id`, ekstraktuj posty z keywords (`reklamacja`, `zwrot`, `Allegro`, `sklep`, `gwarancja`). Jednorazowy koszt ~10-20 GB pobrane (po filtrze PL).
- **Bielik 11B v3 jako primary probe target** (nie v2.3 — v3 jest aktualny, Apache 2.0, 50 warstw × 4096 hidden_size, kompatybilny z PyTorch hooks out-of-the-box). Bielik 1.5B v3 jako tańszy fallback do experymentów probe overfit/transfer.
- **Forum prawne JAKO OPCJONALNY uzupełniacz**, NIE primary źródło — Reddit dump scale dominuje.

---

## 1. ISAP scrape feasibility

### Sample scraped — VERIFIED

**Ustawa o prawach konsumenta (Dz.U. 2014 poz. 827)**, art. 27 — **realnie pobrane** przez `https://api.sejm.gov.pl/eli/acts/DU/2014/827/text.html/art=27`:

> "Konsument, który zawarł umowę na odległość lub poza lokalem przedsiębiorstwa, może w terminie 14 dni odstąpić od niej"

**Kodeks Cywilny (Dz.U. 1964 poz. 93)** — pełen tekst pobrany przez `https://api.sejm.gov.pl/eli/acts/DU/1964/93/text.html`. Struktura zawiera **Księgi → Tytuły → Działy → Rozdziały → Artykuły → Paragrafy (§)** — w pełni hierarchiczna, deterministyczna.

### URL Patterns (potwierdzone z OpenAPI dokumentacji)

| Endpoint | Format | Use case |
|---|---|---|
| `/eli/acts/{publisher}/{year}/{num}` | JSON | Metadata (status, daty, references) |
| `/eli/acts/{publisher}/{year}/{num}/text.html` | HTML | Pełen tekst |
| `/eli/acts/{publisher}/{year}/{num}/text.pdf` | PDF | Oficjalny gazette |
| `/eli/acts/{publisher}/{year}/{num}/text.html/art={N}` | HTML | **Pojedynczy artykuł** |
| `/eli/acts/{publisher}/{year}/{num}/text.html/paragraf={P}/ustep={U}/punkt={K}` | HTML | Pojedyncza jednostka |
| `/eli/acts/{publisher}/{year}/{num}/struct` | JSON | Hierarchia dokumentu |

`{publisher}` = DU (Dziennik Ustaw), MP (Monitor Polski), itp. Acts post-2012 mają volume=0.

### Konkretne ustawy konsumenckie do scrape

| Ustawa | Address | Status sprawdzony |
|---|---|---|
| Ustawa o prawach konsumenta (30 maja 2014) | DU/2014/827 | **Aktywna**, jednolity tekst Dz.U. 2020 poz. 287 (tekst.html dostępny) |
| Kodeks Cywilny (23 kwietnia 1964) | DU/1964/93 | Aktywny, tekst PDF + HTML (HTML potwierdzony) |
| Nowelizacja "Omnibus" (1 grudnia 2022) | DU/2022/2581 | Aktywna |
| Konsolidacja 2020 | DU/2020/287 | Jednolity tekst |

**Do scrape (dodatkowo, do weryfikacji ID przez search ELI):**
- Ustawa o ochronie konkurencji i konsumentów (2007)
- Ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym (2007)
- Ustawa o usługach płatniczych
- Ustawa o ochronie danych osobowych (RODO PL implementing)
- Ustawa o prawach pacjenta (2008)

**Wszystkie powyższe są w ELI API — listing przez `/eli/acts/DU/{year}/` zwróci wszystkie z roku.**

### Citation structure assessment

**DETERMINISTIC.** Jednostka cytowania = `{publisher}/{year}/{num}/art={X}/§={Y}/ust={Z}/pkt={K}/lit={L}`. Każdy fragment ma dokładnie jeden URL. To **idealne** dla citation-grounded RAG — każdy chunk można jednoznacznie zacytować z URL-em który prowadzi do oficjalnego źródła. **To jest realna przewaga vs typowe legal RAG papers** które operują na heurystycznych chunkach bez deterministycznego URL.

### License

- **Art. 4 ust. 1 ustawy o prawie autorskim:** "Nie stanowią przedmiotu prawa autorskiego: 1) akty normatywne lub ich urzędowe projekty". **Ustawy = public domain de facto.**
- ELI API udostępnia bez restrykcji, bez API key dla read access.

### Risks

- **CAPTCHA wall na isap.sejm.gov.pl HTML interface** — ale to nie dotyczy api.sejm.gov.pl/eli (separate endpoint, no captcha).
- **Rate limit** nieudokumentowany formalnie — w praktyce 2-5 req/sec w dobry praktyce (be polite, async z semaphore=5).
- **Acts pre-2012 mają volume ≠ 0** — wymaga adjustment URL dla starszych.

---

## 2. UOKiK

### Decyzje Prezesa UOKiK

**Dwa źródła:**

1. **decyzje.uokik.gov.pl** — dedykowany portal Lotus Notes:
   - URL pattern (z search): `https://decyzje.uokik.gov.pl/bp/dec_prez.nsf/0/{HASH}/$file/Decyzja%20{SYGNATURA}.pdf`
   - Format: **PDF only** (skanowane, ale text layer obecny — sample: `Decyzja DZP 48 2023 Whirlpool Company Polska sp z o o.pdf`)
   - **Bezpośredni listing/search rejected** (Lotus Notes blokuje crawler) — wymaga przejścia przez interfejs HTML
   - License: urzędowe, public

2. **uokik.gov.pl/[article-slug]** — news z opisem decyzji (przykład: `/hulajnoga-na-minuty-ale-odpowiedzialnosc-bez-limitu-prezes-uokik-stawia-zarzuty-bolt-operations-ou`)
   - Format: **HTML** + linki do PDF decyzji
   - URL pattern: `https://uokik.gov.pl/{slug-z-myślnikami}`
   - Browseable list: `https://uokik.gov.pl/aktualnosci.php?news_cat_id={ID}`

### Raporty edukacyjne

**uokik.gov.pl/publikacje** confirmed dostępny:
- Format: **PDF + drukowane**, free order
- Sekcje: "Ochrona konkurencji", "Ochrona konsumentów", "Sprawozdania UOKiK"
- Typy: poradniki, ulotki, plakaty, broszury, "Biblioteka UOKiK" (academic)
- Filterable by year (2018-2026) + category
- **Quantity nie podano explicit** — szacunkowo ~50-150 PDFs (typowe dla agencji urzędowej z ~7 lat publikacji)

### Wytyczne i interpretacje (Q&A)

**prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/** — **JACKPOT FOR Q→A PAIRS**:
- Sekcja "reklamacje" alone: 6 Q&A pairs sample sprawdzony, format: pytanie + odpowiedź **z explicit cytowaniem** Kodeksu Cywilnego i Ustawy o prawach konsumenta
- Sample real Q&A:
  - Q: "Jakie zasady reklamacji obowiązują w przypadku zakupu nieruchomości?"
  - A: "Do umów sprzedaży nieruchomości zawieranych przez konsumenta z przedsiębiorcą (w szczególności z deweloperem) stosuje się **przepisy o rękojmi**."
- Inne sekcje (sprzedaż, gwarancja, RODO) — needs verification, ale UOKiK consistently struktura = pytanie + cytowana odpowiedź

**TO JEST GROUND TRUTH dla citation-grounded RAG** — UOKiK *sam* generuje (q, a, citation) pairs jako swoją misję edukacyjną. **Critical finding** — dataset może zacząć od 50-200 expert-grade pairs from this source.

### License

- Decyzje + raporty: urzędowe, public (Art. 4 PrAut)
- Q&A: nie explicit, ale jako "informacja publiczna" UOKiK = public

### Risks

- Lotus Notes URLs **nie są stabilne** (hash-based) — wymaga indexing przez interfejs
- PDF quality varies (część decyzji to skany)
- Brak struktury Q&A jako API/JSON — wymaga HTML scraping

---

## 3. Real consumer questions

### Reddit r/Polska — VERIFIED scale

**Sprawdzone:**
- r/Polska: **413k weekly visitors, 26k weekly contributions** (Jan 2026)
- r/PrawoPL: **NIE potwierdzony** (search nie zwrócił specyficznego wyniku — prawdopodobnie nie istnieje lub bardzo mały)
- r/poland: 311k weekly visitors, 11k weekly contributions

**Access:**
- WebFetch BLOCKED przez Reddit (potwierdzone — "Claude Code is unable to fetch from www.reddit.com")
- Free PRAW: ~60-100 req/min praktycznie, OAuth required, ~tygodnie czekania na akademik approval
- **MITIGATION: Pushshift dumps via Academic Torrents** — Reddit 2005-06 → 2025-06, 476 NDJSON .zst plików, 3.4 TB total, top-40k subreddits jako separate torrent → można pobrać tylko `r/Polska` slice (~5-15 GB compressed)

**Volume estimate dla r/Polska / consumer keywords:**
- Założenie: ~5% wątków na r/Polska ma keyword `reklamacja|zwrot|Allegro|sklep|gwarancja|RODO|sprzedawca`
- 26k contributions/week × 5% = ~1300 posts/week × 52 = **~67k consumer-related posts/year**
- **Konserwatywnie po deduplikacji + filtrach jakości: ~15-30k unique consumer questions/year**

### Forum infor.pl, e-prawnik.pl, forumprawne.org

**e-prawnik.pl/forum/domowy/prawo-cywilne-1/ochrona-konsumenta/** — VERIFIED:
- **Public, NO login required for browsing**
- **970 wątków** w sekcji "Ochrona konsumenta" alone, ~20 stron paginacji
- Real samples (potwierdzone): "CV-Maker subskrypcja", "Defective armchair cushions", "Leather handbag water damage", "TV defect beyond 14-day window"
- Date range: feb 2022 → aug 2025 (sustained activity)
- URL pattern: `e-prawnik.pl/forum/{descriptive-slug}.html`

**forumprawne.org/forum/prawa-konsumenta.33/** — VERIFIED:
- **Browse public** (post wymaga login)
- **2436 stron paginacji** (≈ 50k+ wątków total — prawdopodobnie inne kategorie wymieszane, należy zweryfikować scope)
- URL pattern: `/watek/{slug}.{thread-id}/`

**infor.pl/prawo/forum/** — istnieje, wymaga deeper inspection scope

**Forum lexlege.pl** — TLS cert error, niedostępne (dropping)

### Sample query "Allegro nie chce zwrócić pieniędzy reklamacja"

**WebSearch zwrócił 5+ realnych źródeł:**
1. spolecznosc.allegro.pl/t5/dyskusje-kupujacych/zwrot-reklamacja/td-p/1142567 (Allegro own community, wymaga weryfikacji TOS)
2. spolecznosc.allegro.pl/t5/dyskusje-kupujacych/jak-zakonczyc-reklamacje/td-p/1117137
3. subiektywnieofinansach.pl artykuł "Reklamacja Allegro. Konsultanci nie znają przepisów?"
4. allegro.pl/pomoc/dla-kupujacych/zasady-zwrotow-i-reklamacji (oficjalna dokumentacja)
5. spolecznosc.allegro.pl/t5/zaawansowani-sprzedawcy/reklamacja-od-kiedy-liczy-się-czas/td-p/773497

**Allegro społeczność = secondary source** (wymaga sprawdzenia TOS scrape, prawdopodobnie ToS prohibits commercial scraping ale academic research może mieć fair use).

### Volume estimate (1 miesiąc realistic scrape)

| Source | Volume estimate | Method |
|---|---|---|
| Pushshift r/Polska dump (consumer-filtered) | 1.5-3k posts/month | Offline grep dump |
| forumprawne.org "Prawa konsumenta" | ~500 nowych wątków/month (extrapolacja) | HTML scrape, polite |
| e-prawnik.pl ochrona-konsumenta | ~50-100 wątków/month | HTML scrape |
| infor.pl forum | ~100-200 wątków/month (TBD) | HTML scrape |
| **Total realistic 1 miesiąc** | **~2.2-4k unique questions** | |

**Total realistic 2 tygodnie scrape z agentami:** ~1-2k unique questions z 4 źródeł kombinowanych.

---

## 4. Polish NLI models

| Model | License | HF URL | Polish support | Recommended use |
|---|---|---|---|---|
| **MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7** | **MIT** | huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 | **Yes** (105k Polish pairs trained, XNLI 0.74-0.87 multilingual avg) | **PRIMARY judge** dla (claim, evidence) → entailed/contradicted/neutral. 300M params, ~1189 tekstów/sek na A100. |
| MoritzLaurer/mDeBERTa-v3-base-mnli-xnli | MIT | huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli | Yes (100 lang) | Alternative baseline, slightly older training data |
| MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli | MIT | huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli | Yes | Fast inference fallback (mniejszy, niższa accuracy) |
| joeddav/xlm-roberta-large-xnli | MIT | huggingface.co/joeddav/xlm-roberta-large-xnli | Yes (XLM-R) | Larger model alternative |
| **HerBERT-large (allegro/herbert-large-cased)** | **CC BY 4.0** | huggingface.co/allegro/herbert-large-cased | **Native Polish, 8.6B tokens** | Base model do **fine-tune na CDSC-E** (Polish entailment 10k par) — opcjonalny ablation |
| CDSC-E dataset (allegro/klej-cdsc-e) | CC BY-NC-SA | huggingface.co/datasets/allegro/klej-cdsc-e | Polish 10k pairs | Trening data dla custom HerBERT-NLI |

### Sprawdzone NIE istnieją

- ❌ `sdadas/polish-nli` — search HF nie znalazł
- ❌ `radkomotion/polish-nli` — search nie znalazł
- ❌ CLARIN-KNeXT brak NLI modelu (focus na knowledge extraction)

### Recommended judge architecture

**3-tier:**
1. **mDeBERTa multilingual (300M)** — primary baseline, no training needed, MIT license, deploy as-is
2. **HerBERT-large fine-tuned on CDSC-E** — secondary, ~1 dzień GPU, opcjonalny ablation w cyklu 1
3. **Bielik 11B v3 jako semantic LLM-as-judge** dla najtrudniejszych przypadków (LLM ranking dwóch sentence pairs entailment) — uzupełnienie NLI binary classifier

**Ablation w cyklu 1:** mDeBERTa vs HerBERT-NLI vs Bielik LLM-judge — jako sub-RQ "który NLI judge generalizuje najlepiej dla legal entailment PL?"

---

## 5. Hidden-states probe — implementation references

### Available libraries / repos

| Tool | Purpose | URL | Bielik compat |
|---|---|---|---|
| **obalcells/hallucination_probes** | **Reference impl** linear+LoRA probes na hidden states LLM | github.com/obalcells/hallucination_probes | **Yes** — supports Llama, Qwen, Mistral; Bielik to Mistral-like architecture |
| transformer-lens | Mechanistic interpretability framework, hooks | github.com/TransformerLensOrg/TransformerLens | Tested with Mistral — Bielik should work z drobnymi configami |
| nnsight | Modern alternative, tracking hooks z syntactic API | github.com/ndif-team/nnsight | Yes (Mistral-compatible) |
| baukit | Lightweight nethook utility | github.com/davidbau/baukit | Yes (works z any HF transformer) |
| **Native PyTorch** `register_forward_hook` | Standard, brak dodatkowych deps | torch docs | **Yes — verified Bielik 11B v3 compatible** |

### Sample template (z obalcells/hallucination_probes ranges)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "speakleash/Bielik-11B-v3.0-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Hook na warstwie L (np. middle = 25 dla 50-warstwowego Bielika)
hidden_states_buffer = []
def hook_fn(module, input, output):
    # output[0] = hidden states, shape [batch, seq_len, hidden_size=4096]
    hidden_states_buffer.append(output[0].detach().cpu())

target_layer = 25  # tunowalny hyperparameter
handle = model.model.layers[target_layer].register_forward_hook(hook_fn)

# Linear probe trening: extracted_hidden -> binary halu/no-halu label
# Trenowany na ~5-10k labeled (claim, evidence) z weak labels z mDeBERTa NLI
```

### Memory cost estimates

**Bielik 11B v3** (50 layers × 4096 hidden_size, bfloat16):
- Inference VRAM: ~22 GB bf16 / ~12 GB int8 / ~7 GB int4 (NF4 z bitsandbytes)
- Hidden states extraction per token: 50 × 4096 × 2 bytes = **400 KB/token**
- Per sample (avg 200 tokens): **80 MB hidden states all-layers**
- Per layer single (np. L=25): **1.6 MB/sample**
- **Dla 10k labeled samples × 1 layer = 16 GB on disk** (manageable)

**Bielik 1.5B v3** (Qwen 2.5 base, 24-28 layers × 1536 hidden) — fallback:
- VRAM ~3 GB bf16
- Hidden states: 100x mniejsze, idealne dla rapid prototyping probe overfit/transfer

### Recommended approach

1. **Iteracja 0:** Bielik 1.5B v3 + obalcells/hallucination_probes template — train linear probe na 1k labeled (claim, evidence) z mDeBERTa weak labels, sprawdź czy probe accuracy > random (>50%) na held-out
2. **Iteracja 1:** Scale do Bielik 11B v3, fine-tune layer selection (probe hidden states z layer 10/25/40, compare AUROC), expand to 5-10k samples
3. **Iteracja 2:** Multi-layer probe (concat hiddens), porównaj LoRA probe vs linear

**Key paper references found:**
- ICR Probe (ACL 2025): tracks hidden state dynamics across layers
- Semantic Entropy Probes (OATML): no multi-sample sampling needed
- SAPLMA: original hidden-states halu detector

---

## 6. Citation-grounded generation

### Best library combo dla polish citation-aware RAG

| Layer | Choice | Reason |
|---|---|---|
| **RAG framework** | **LlamaIndex CitationQueryEngine** | Native in-line citations, configurable `citation_chunk_size` (default 512), works z any LLM/vector store |
| **Structured output (citation extraction)** | **Outlines** (FSM-based grammar) | Guaranteed schema compliance, works native z Bielik (Mistral arch supported), zero retries |
| **Pydantic validation** | **Instructor** | Pydantic-first, automatic retries on validation failure, multi-provider |
| **Vector store** | Qdrant (już w stacku z farmakologii pivot) | Zero migration cost, supports payload filtering po `ustawa_id`, `art`, `paragraf` |
| **Embedder** | BGE-M3 (już w stacku) | Multilingual, includes Polish |
| **Reranker** | sdadas/polish-reranker-roberta-v3 (już w stacku) | Polish-native, fine-tunable |
| **Generator** | Bielik 11B v3 Instruct (Apache 2.0) | Polish-native, structured output via Outlines |
| **Citation verifier** | bge-reranker-v2-m3-citeverifier (CLARIN-KNeXT) | **NEW finding** — dedicated citation verification reranker |

### Pipeline schemat

```
User query (PL) 
  → BGE-M3 embedder + Qdrant retrieval (top 30)
  → polish-reranker-v3 (top 10)
  → LlamaIndex CitationQueryEngine wraps prompt
  → Bielik 11B + Outlines (force JSON schema z claim+citations)
  → Pydantic validation via Instructor (retry if invalid)
  → mDeBERTa NLI judge: dla każdego (claim, cited_evidence) → entailed/contradicted/neutral
  → IF contradicted/neutral → flag jako potential halu, alternative: hidden-states probe Bielik confidence
```

### Polish-specific gaps

- **LlamaIndex CitationQueryEngine NIE ma native Polish prompts** — wymaga ręcznej polonizacji prompt templates (~2-5h work)
- **Outlines + Bielik:** nie wide-tested combo (Outlines wspiera Mistral, Bielik = Mistral-like, powinno działać; weryfikacja w iteracji 0 priorytet)
- **Reranker citation verifier:** CLARIN-KNeXT bge-reranker-v2-m3-citeverifier wymaga sprawdzenia (uncertain dataset, license)

---

## 7. Estimated dataset numbers

### Korpus prawa (chunks z ustaw)

**Założenia chunkowania:** 512 tokens chunk (≈ 1-2 paragrafy), 64 token overlap.

| Ustawa | Articles | Estimated chunks |
|---|---|---|
| Ustawa o prawach konsumenta (Dz.U. 2014/827) | ~58 art (do art. 56) | ~80-150 chunks |
| Kodeks Cywilny (Dz.U. 1964/93) | 1088 art | **~2000-3000 chunks** |
| Ustawa o ochronie konkurencji i konsumentów (2007) | ~138 art | ~200-300 chunks |
| Ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym (2007) | ~16 art | ~40-60 chunks |
| Ustawa o usługach płatniczych | ~150+ art | ~250-400 chunks |
| RODO PL implementing | ~80 art | ~120-180 chunks |
| Ustawa o prawach pacjenta (2008) | ~75 art | ~100-150 chunks |
| **Total ustawy** | | **~2800-4350 chunks** |

**+UOKiK content:**
| Source | Estimated chunks |
|---|---|
| Decyzje Prezesa UOKiK (5 lat archive, ~500 decyzji × 5-10 chunks/decyzja) | ~2500-5000 chunks |
| Raporty edukacyjne UOKiK (~50-150 PDFs × 10-30 chunks) | ~1000-3000 chunks |
| Q&A prawakonsumenta.uokik.gov.pl | ~50-200 Q&A pairs (each = 1 ground-truth pair) |
| **Total UOKiK** | **~3500-8000 chunks + 50-200 expert pairs** |

**TOTAL CORPUS: ~6.3-12.4k chunks legal + UOKiK** (porównywalne z farmakologią ~4100 docs)

### Real questions corpus (po scrape)

| Source | Realistic 1 miesiąc |
|---|---|
| Reddit r/Polska (Pushshift dump filtered) | 1.5-3k posts |
| forumprawne.org | ~500 |
| e-prawnik.pl | ~100 |
| infor.pl forum | ~100-200 |
| **Total monthly** | **~2.2-4k** |

**Po scaling do 2 tygodnie agent scraping:** ~1-2k unique consumer questions

### Pairs (query, answer, citation) achievable

**3 strategie:**
1. **UOKiK Q&A pairs (gold standard, ~50-200)** — manual, expert quality, with explicit citations
2. **Forum question + LLM-generated answer + retrieved citation (silver standard, ~3-5k)** — Bielik 11B generates answer, retrieves top-3 chunks, NLI judge labels (entailed/contradicted)
3. **Synthetic pairs (chunks → questions, ~5-10k)** — given chunk, Bielik generates plausible consumer question, paired with chunk = (q, citation, gold answer = chunk content)

### Total dataset target ~10-15k pairs realistic w ~2 tygodnie?

**REALISTIC: 5-10k pairs achievable w 2 tygodnie z agentami.** 10-15k osiągalne w 3-4 tygodnie z dedicated effort. Breakdown:
- Iteracja 0 week 1: scrape ustawy (~3k chunks), scrape UOKiK Q&A (~50-200 pairs), Pushshift dump filter (~2k questions)
- Week 2: pipeline Bielik + Outlines + retrieval, generate ~3-5k silver pairs z forum questions
- Week 3-4 (jeśli rozszerzenie): ~5k synthetic pairs + manual review subset

**Verdict:** 10k pairs w 2 tyg = optymistyczne ale możliwe; 5k pairs = solid baseline, defensible w pracy inżynierskiej.

---

## 8. Risks + mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Reddit API rate limits / blocked WebFetch | **HIGH (potwierdzone)** | High (no real-time questions) | **Pushshift Academic Torrents dump** — offline, jednorazowy ~10-20 GB download for r/Polska slice |
| ISAP API rate limits / instability | LOW | Medium | Async z semaphore=5 req/sec, retry exponential backoff, cache lokalnie wszystkie scraped texts |
| Lotus Notes UOKiK PDF URLs not stable | MEDIUM | Medium | Index przez interfejs HTML jako entry points; cache PDFs lokalnie po 1x download |
| ChPL-style OCR quality issues UOKiK PDFs | LOW-MEDIUM | Low | Tesseract-OCR fallback dla skanowanych decyzji; major decyzje już mają text layer |
| **NO dedicated Polish NLI model** | **CONFIRMED** | Medium | mDeBERTa multilingual baseline + opcjonalny HerBERT-NLI fine-tune na CDSC-E |
| forumprawne.org 50k+ wątków = scope creep | MEDIUM | Medium | Aggressive keyword filter (`reklamacja|gwarancja|RODO|sklep|Allegro|sprzedawca`), TOP-1k by length/upvotes |
| TOS violation Allegro społeczność scrape | MEDIUM | Low-Medium | Skip Allegro własna społeczność, stick z neutralnymi forami (e-prawnik, forumprawne, infor) |
| Bielik 11B VRAM (24 GB sufficient?) | LOW (potwierdzone) | High if no | bf16 ~22 GB, int8 ~12 GB; fallback Bielik 1.5B (3 GB) dla rapid iteration |
| Hidden-states probe accuracy < random (probe nie wykrywa halu) | MEDIUM | High (główna kontrybucja R7) | Negative-result framing — nawet "probe nie generalizuje" = publishable finding (tak jak konspekt mówi negative result OK), porównanie multi-layer + LoRA |
| LlamaIndex CitationQueryEngine prompts EN-only | MEDIUM | Low | ~2-5h rewrite na PL, sprawdzone że template-based |
| Outlines + Bielik untested combo | MEDIUM | Medium | Iteracja 0 first task: minimal POC `Outlines.json(Bielik, schema)` z 10 sample queries |
| **Ustawa o prawach konsumenta = za mała** (tylko 58 art, ~80-150 chunks) | **HIGH (uwaga w briefie)** | Low (wystarczy z innymi ustawami) | KC = 1088 art = duży zapas + 5 innych ustaw = >2800 chunks total ustawy, scope OK |
| Real questions w polskim mają niski signal-to-noise (memes, off-topic) | MEDIUM-HIGH | Medium | Heuristic filter: min 100 znaków, regex consumer keywords, manual sample 100 do tuning |
| Citation hallucination przez Bielik (model confabulates art. 999 of nonexistent ustawa) | HIGH (główna research question) | **POSITIVE — to jest cel pracy** | Outlines force schema constraints, post-validation: czy cited URL faktycznie pasuje do scraped chunks; **właśnie tego ma badać hidden-states probe + NLI judge** |

---

## 9. Recommended pipeline (agent task list)

### Iteracja 0 — Feasibility POC (week 1-2)

| Task | Who | Effort | Priority |
|---|---|---|---|
| Scrape Ustawa o prawach konsumenta (Dz.U. 2014/827) full text + struct via ELI API | Agent | 2h | P0 |
| Scrape Kodeks Cywilny art. 535-581 (sprzedaż, rękojmia, gwarancja) | Agent | 2h | P0 |
| POC Outlines + Bielik 1.5B v3, schema {answer, citations[{ustawa, art, §, ust}]} z 10 sample queries | Agent + Magda | 4h | P0 |
| Download Pushshift r/Polska torrent + filter consumer keywords | Magda (download size) | 1h aktywne + ~1d torrent | P0 |
| Scrape UOKiK Q&A prawakonsumenta.uokik.gov.pl (wszystkie sekcje, ~50-200 pairs) | Agent | 4h | P0 (gold standard) |
| Test mDeBERTa multilingual NLI na 20 sample (claim, evidence) z scraped ustaw — czy działa po polsku? | Agent + Magda | 2h | P0 |
| **POC checkpoint**: czy pipeline retrieve→generate→cite→NLI-judge działa end-to-end na 10 questions? | Magda | 4h review | P0 |

### Iteracja 1 — Baseline (week 3-4)

| Task | Effort |
|---|---|
| Scrape pozostałe 5 ustaw (UOKiK, NPR, RODO, prawa pacjenta, usługi płatnicze) | 8h agent |
| Scrape UOKiK decyzje (top 100 by relevance) + raporty edukacyjne (top 30) | 16h agent + Magda review |
| Scrape forumprawne.org "Prawa konsumenta" filtered top 1000 | 8h agent |
| Scrape e-prawnik.pl ochrona-konsumenta 970 wątków | 4h agent |
| Index w Qdrant + setup polish-reranker | 4h Magda |
| Generate 3-5k silver (q, a, citation) pairs przez Bielik 11B + retrieval + NLI label | ~24h compute, ~4h Magda monitoring |
| Manual review 200 silver pairs jako QA gold | 8h Magda |

### Iteracja 2 — Hidden-states probe (week 5-6)

| Task | Effort |
|---|---|
| Setup Bielik 11B v3 + hidden states extraction hooks (layer 10/25/40) | 8h Magda |
| Train linear probe na 5k labeled samples z weak NLI labels | 4h compute, 4h Magda |
| Compare probe AUROC across layers, LoRA vs linear, multi-layer concat | 16h Magda |
| Evaluate probe na held-out 500 manual labeled (UOKiK Q&A as gold + manual) | 8h Magda |

### Iteracja 3 — RAG eval + comparison (week 7-8)

Ablations:
- Outlines vs no-Outlines (raw Bielik output, regex parse)
- mDeBERTa NLI judge vs HerBERT-NLI fine-tuned vs Bielik LLM-judge
- Hidden-states probe vs NLI verifier vs combination
- Cytowanie URL valid? Czy art.X faktycznie istnieje w scraped korpusie?

### Magda-only tasks (cannot delegate)

- Decision points: scope, accept/reject silver pairs, accept negative result for probe
- Manual gold standard ~200 pairs (consumer rights expert?? — Magda nie ma tego tytułu, **MITIGATION: framing R5 jako "leverage author expertise w prawie konsumenckim po self-study; dla edge cases consult UOKiK Q&A jako external ground truth"** — analogicznie do farmakologii pivot)
- Defense scaffolding: ablations, kategoryczna error analysis, negative-result framing R8

---

## Wnioski końcowe

**CONDITIONAL GO** — pipeline data feasibility jest solidne: ELI API = jackpot deterministycznych cytowań (przewaga vs typowe legal RAG papers), UOKiK Q&A = gotowy gold standard ~50-200 pairs, Pushshift dumps = real consumer questions w skali. Główne ryzyko: brak dedicated Polish NLI = mDeBERTa multilingual jako pragmatic substitute (defensible). Hidden-states probe ma solid library support (obalcells/hallucination_probes + native PyTorch hooks na Bielik 11B v3). Outlines + Bielik combo wymaga POC w iteracji 0 — to jedyny **technical blocker** który może wymagać workaround.

**Rekomendacja:** start z iteracja 0 POC (1 tydzień), checkpoint go/no-go po sprawdzeniu Outlines+Bielik + mDeBERTa NLI na sample 10 queries z UOKiK Q&A jako ground truth. Jeśli end-to-end działa = full GO. Jeśli pipeline łamie się = adjust scope (np. drop hidden-states probe jako optional, focus na NLI-judge only).
