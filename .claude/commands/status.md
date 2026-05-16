---
description: Where am I vs iteration plan z 02_konspekt_v3.2_skeleton.md + PLAN_cele_i_kroki.md (post-DEC-003 v3.2 halu detection). Iteration-based (NIE calendar weeks). Brutal honest.
---

## Procedura

1. **Sprawdź bieżącą iterację** — czytaj `thesis_research/PLAN_cele_i_kroki.md` + `02_konspekt_v3.2_skeleton.md`:
   - **Iteracja 0b POC:** 4 kill-criteria testy (T1 mDeBERTa NLI sanity ✓ PASS 80.6% / T2 Outlines+Bielik diakrytyki / T3 PyTorch hooks layer 47 / T4 lab GPU verify)
   - **Iteracja 1:** RAG MVP (Bielik + Qdrant + LlamaIndex + 3-tier NLI verifier + Gradio 3-tab) + halu probe training layer 47
   - **Iteracja 2:** Continuous improvement loop (3 cykle retraining z drift triggers)
   - **Iteracja 3:** Observability stack (Langfuse + Evidently + Alibi Detect + LGTM + Alertmanager)
   - **Iteracja 4:** Serving + CI/CD (SGLang + TEI + FastAPI + Docker + GH Actions)
   - **Iteracja 5:** Manual gold standard 200 par + 4-way verifier ablation (mDeBERTa + HerBERT + gliclass + LLM-judge)
   - **Iteracja 6:** 6-poziomowa error analysis + ablations A1-A4 + RAGAS faithfulness
   - **Iteracja 7-8:** R1-R8 writing + PJATK formatting + citation pass + defense scaffolding

2. **Scan repo state** (równolegle):
   - `main_project/` — pliki kodu? `git log --oneline -20` w main_project
   - `thesis_elements/` — które `R{NN}_*.docx` istnieją? rozmiar / liczba słów każdego?
   - `thesis_research/drafts/` — co tam jest?
   - `thesis_research/decisions/` — ile decyzji udokumentowanych?
   - `thesis_research/iteration-N-*-report.md` — czy istnieją raporty done criterion per iteracja?
   - `git log --oneline -20` w root — co się działo ostatnio?

3. **Match observation vs done criterion** (z II.16 02b_updates):
   - Czy done criterion bieżącej iteracji jest spełnione?
   - Czy są blokery przejścia do następnej iteracji?
   - Czy potrzebna sub-iteracja (np. 2a, 2b) w razie failure?

4. **Identify top 3 blockers** — konkretne, NIE ogólne ("brak czasu" się nie liczy; "judge kappa 0.32 — poniżej 0.50 progu, wymaga prompt rewriting" się liczy).

5. **Next concrete deliverable** — JEDNA rzecz, max 1-2h pracy autorki.

## Format output

```
## Status iteration check (YYYY-MM-DD)

**Current iteration:** Iteracja N — [nazwa]
**Done criterion status:** [in progress / met / blocked / sub-iteration needed]

### Repo snapshot
- main_project/: [lista modułów albo "pusty"]
- thesis_elements/: [lista rozdziałów + word count albo "pusty"]
- decisions/: [N decyzji + ostatnia data]
- Iteration reports: [których iteracji raporty istnieją w thesis_research/]
- Ostatni commit: [data + message]

### Done criterion z II.16 dla bieżącej iteracji
- [bullet 1]: ✅ / ⏳ / ❌
- [bullet 2]: ✅ / ⏳ / ❌
- ...

### Top 3 blockers
1. [konkret 1]
2. [konkret 2]
3. [konkret 3]

### Next concrete deliverable (max 2h)
[jedna rzecz, jasna definicja done]
```

## Reguła brutalności

Jeśli iteracja jest zablokowana albo done criterion nie spełnione — **NIE łagodź**. Powiedz wprost:
- "Done criterion Iteracji N nie spełnione w X kategoriach"
- "Najszybsza ścieżka unblock to Y, ale wymaga Z"
- "Realna decyzja: kontynuujesz z założonymi compromises (Plan A modify), expandujesz scope iteracji (Plan A extend), czy ucinasz scope (Plan A trim)?"

Anty-paraliż — nazwij trade-off i powiedz czy decyzja jest *wystarczająco dobra* per Decision before output wzorzec.

**Speed-run mode acknowledgement:** autorka pracuje w bursts ("6 miesięcy w 3 dni"). Brak deadline'ów per iteracja jest świadomy. Brak post-deadline excuses akceptowalne — ALE done criterion każdej iteracji jest twardy.
