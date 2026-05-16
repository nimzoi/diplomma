---
name: Multi-agent parallel workflow
description: Magda uruchamia 3-12 Claude Code subagentów równolegle; każdy "track" robi inny aspekt; sync przez git checkpointy
type: workflow
originSessionId: 5630a386-3d25-4119-adc8-3884cf68b58c
---

**Track-parallel strategy** = preferred dla speed-run thesis work. **Skala: 3-12 agentów concurrent** zostało sprawdzone 2026-05-15/16 (single session, 12+ agents w jednej sesji bez kolizji).

## Kategorie task-isolation (przykłady które działały)

- **Scrape parallel:** S1-S7 + raw_archive_sweep + S5 forum HTML + C1 cleanup + research agents — wszystkie w jednym dniu, każdy w isolated source dir + isolated module path. **Cost OK** per Magda ("kosztem się nie przejmuj").
- **Research parallel:** mining v3.1 R1+R2 + halu detection SOTA + NLI alternatives + krytyczna ocena scope — różne dokumenty, różne foldery, NIE konflikt.
- **Writing track separate:** kiedyś używany (R1+R2+R5 niezależnie), post-Wariant B drafts są w archive. **OVERRIDE 2026-05-16:** 48h-sprint pattern wymusił writing-first (R1-R8 + Tasks 09/10/11 do 2026-05-18) — build-first-finalize-last per CLAUDE.md Wzorzec 8 explicit suspended. Konwencja sprint: `{{SCREAMING_SNAKE_CASE}}` placeholders dla wartości z Iter. 1-6 + `[CYT: Author Year topic]` dla cytacji do dopisania + fait accompli (pisz tak jakby Iter. 1-6 były done). NIE używać poza calendar-deadline pressure.

## Naming convention (post-cleanup 2026-05-16)

- Format: `R{NN}_{slug}.docx` z padding (R01, R02, ..., R08) per `thesis_elements/CLAUDE.md`
- v3.2 drafts: PUSTY w `thesis_research/drafts/` — pre-cleanup R3/R4/R5 → `_archive/v3.2-pre-clean/drafts/` (Wariant B)

## Sync mechanizm między agentami

- Per-agent **research summary** w `thesis_research/research/<topic>_2026.md` (consistent location)
- Per-source **manifest.json** + sha256 verification (raw_archive_sweep pattern)
- Per-agent code w isolated module path: `main_project/src/scrape/<source>/`, `main_project/iter0b_poc/<test>/`
- **Reguła:** NIE 2 agenty edytujące ten sam plik (race condition risk)

## Git workflow w multi-agent mode

- **Snapshot commits jako checkpointy** — nawet jeśli agenty mid-write, ostatni commit zachowuje stan
- Bez periodic commitów wszystko zostaje untracked → ryzyko utraty przy `git checkout`
- Pattern udanego dnia 2026-05-16: 12+ commitów (`b2f904e` setup → `f5b4604` final cleanup), każdy push po landzie agenta
- **Big commits OK** — pojedynczy commit może mieć 5,400 plików / 1.3M LOC (`82712a8` massive scrape) — nie problem
- `git worktree` może być spawned przez Claude Code subagenty (orphan dirs np. `magical-morse-1c4ee4`). Cleanup post-session: `git worktree prune && git branch -D claude/*-* && rm -rf .claude/worktrees/<orphan>`
- `.idea/*` (PyCharm) gitignored — dodać do `.gitignore` jeśli przeszkadza

## Konsystencja cwd między agentami

- **Wszystkie subagenty muszą operować w `D:\diplomma\`** żeby auto-load `CLAUDE.md` root spec
- Sanity check: `pwd` → `D:\diplomma` + `ls CLAUDE.md` → file exists
- Jeśli subagent ma cwd indziej (np. `C:\Users\magma`) — NIE widzi `main_project/`, `thesis_research/`, spec docs. **Restart z proper cwd.**
- Worktree side-effect: subagent może być w `D:\diplomma\.claude\worktrees\<orphan>` — sprawdź path przed scope assertion.

## Fragment workflow dla long chapters (lesson 2026-05-16, R5 architektura)

Gdy rozdział jest centralny (R5 architektura PRO-D Task 05) i przekracza ~3000 słów:
- **Split na 5 fragmentów** z explicit sign-off między każdym (NIE jeden mega-pass)
- Pattern który zadziałał dla R5:
  - F1: szkielet + sekcja 5.1 (cele architektury, MLOps emphasis %)
  - F2: sekcja 5.2 C4 widoki (Context + Container + Component)
  - F3: sekcje 5.3 Inference + 5.4 Training pipeline
  - F4: sekcje 5.5 Continuous loop + 5.6 Observability
  - F5: sekcje 5.7 Security + 5.8 UI + 5.9 decyzje
- **Commit per fragment** — nie czekać aż całość gotowa
- **Status markers per komponent** — ✓ (istnieje w repo) / 🚧 Iter. X (scaffolding) — zapobiega phantom infrastructure claims
- **Sanity check liczb cross-fragment** — container count, % MLOps, diagramy ID muszą być consistent między fragmentami (poprzednio drift 11 vs 12 kontenerów, 37.5% vs 33.3% — caught przez tech-lead review)

## Aggressive parallel scrape pattern (lesson 2026-05-16)

Gdy Magda mówi "wszystko ma być zdobyte" / "kosztem się nie przejmuj":
- Spawn 4-5 scrape agents na różne source families (ELI ustaw + Playwright WAF + UE/TSUE + nowe portale + raw archive sweep)
- Każdy z własnym output dir + manifest + research summary
- Każdy z explicit license attribution + sha256 + idempotent re-run
- WAF blockers documented (Allegro Datadome / Reddit IP-block / orzeczenia.ms Tapestry) — NIE crash, mark + skip
- Consolidacja przez unified preprocessing pipeline (`dataset_builder.py`) z source-specific normalizers

## Why

Speed-run mode + niezależne tracki = praca wieloma rękoma jednocześnie. Bez tej strategii Magda jest bottlenecked attention switching. Parallel agents dostarczają deliverables w tym samym czasie. Per Wariant B (cleanup pattern) — krytyczne agents też mogą być spawned równolegle z scrape, dostają full context z aktualnego stanu repo.

## How to apply

- **NIE proponować sequential workflow** gdy 3+ niezależne tracki dostępne (research + scrape + cleanup równolegle).
- **Pierwsza wiadomość każdego agenta** wymienia explicit ZAKRES + listę plików do read + kill criteria / done definition.
- **Periodic checkpoint commits** (per agent landing) — nie czekać aż wszyscy skończą.
- **Background agents** dla long-running tasks (>10 min) — `run_in_background=true`, notification on completion.
- **Worktree cleanup** post-session: pruning + branch delete + rm dead folders.
- **Multi-agent conflict resolution:** NIE 2 agenty edytujące ten sam plik. Jeśli przewidziany konflikt → split modules / split source dirs.
