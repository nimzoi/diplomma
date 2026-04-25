# Diploma Thesis Tasks — Project Navigation

This document is the **navigation index** for the diploma thesis task set. It is not the main project readme; it explains how to find and use the individual task descriptions.

---

## How to Use This Repository

Tasks are ordered to follow the typical structure of an engineering thesis. Each task is in a separate file numbered **01** through **11**. Complete them in order where it makes sense; some tasks (e.g. data description and exploration) can be refined in parallel with writing.

- **Tasks 01–06** correspond to the main thesis chapters (introduction, literature review, data, preprocessing, architecture, models).
- **Task 07** is the results and discussion chapter (presentation of outcomes, interpretation, limitations).
- **Task 08** is the summary chapter (conclusions and future work).
- **Task 09** lists formal and editorial requirements (formatting, length, citations).
- **Task 10** is a **self-assessment checklist** (0 points, same deadline as Task 11) so you can verify completeness before final submission.
- **Task 11** is the final task: comprehensive summary of the entire thesis.

All tasks except Task 10 are graded (up to 10 points each). Task 10 is for your own checking only (0 points).

---

## Task Index (with links)

| #   | File   | Task description | Points |
|-----|--------|------------------|--------|
| 01  | [01.md](01.md) | **First chapter (Introduction)** — Background, motivation, aims, scope, thesis structure | 10 |
| 02  | [02.md](02.md) | **Literature review** — Conducting and writing the literature review, citing sources | 10 |
| 03  | [03.md](03.md) | **Describe and document different data types** — Tabular, text, image, audio, video; structure, metadata, ethics | 10 |
| 04  | [04.md](04.md) | **Data exploration, standardization, and normalization** — EDA, preprocessing pipeline, documentation | 10 |
| 05  | [05.md](05.md) | **IT system architecture** — System design, components, deployment, security | 10 |
| 06  | [06.md](06.md) | **Describing and preparing ML models** — Problem formulation, architecture, training, evaluation, interpretation | 10 |
| 07  | [07.md](07.md) | **Results, discussion and presentation** — Presenting outcomes, tables/figures, interpretation, limitations | 10 |
| 08  | [08.md](08.md) | **Summary chapter** — Overall summary, conclusions, future work | 10 |
| 09  | [09.md](09.md) | **Aggregated formal and editorial requirements** — Format, length, citations, bibliography, binding | 10 |
| 10  | [10.md](10.md) | **Self-assessment (0 points)** — Evaluation checklist; same deadline as Task 11; for self-check only | 0 |
| 11  | [11.md](11.md) | **Comprehensive summary of the entire thesis** — Final task; full-thesis overview and checklist | 10 |

**Deadlines:** To be set by the course (e.g. in the LMS). Task 10 has the **same deadline as Task 11**.

---

## Flow of tasks (overview)

```mermaid
flowchart LR
  A[01 Introduction] --> B[02 Literature]
  B --> C[03 Data types]
  C --> D[04 EDA / normalization]
  D --> E[05 Architecture]
  E --> F[06 ML models]
  F --> G[07 Results & discussion]
  G --> H[08 Summary chapter]
  H --> I[09 Formal requirements]
  I --> J[10 Self-assessment]
  J --> K[11 Comprehensive summary]
```

---

## Recommended Order of Work

1. **01** → **02** → **03** → **04** → **05** → **06** (main thesis body)
2. **07** (results and discussion — present and interpret outcomes)
3. **08** (summary chapter)
4. **09** (apply formal requirements throughout and before submission)
5. **10** (self-assessment; use before submitting Task 11)
6. **11** (comprehensive summary; final submission)

---

## Glossary (terms used in the tasks)

| Term | Meaning |
|------|--------|
| **EDA** | Exploratory Data Analysis — initial investigation of data (distributions, missing values, outliers, visualisations). |
| **Standardization** | Converting data to a consistent format, units, encoding, or scale (e.g. same date format, same image resolution). |
| **Normalization** | Scaling numerical values to a common range or distribution (e.g. min–max to [0,1], z-score). |
| **Codebook** | Data dictionary describing each variable: name, type, meaning, units, allowed values. |
| **Baseline** | A simple or reference model used for comparison (e.g. random guess, previous work, rule-based system). |
| **Footnote** | Reference or note at the bottom of the page; Task 09 may require citations as footnotes. |

---

## Pre-submission checklist

Before submitting your thesis, confirm:

- [ ] **Tasks 01–09 and 11** are completed and reflected in the thesis text.
- [ ] **Task 10** (self-assessment) has been filled in for your own verification (same deadline as Task 11).
- [ ] **Task 09** (formal requirements) is met: length, font, margins, citations, bibliography, binding.
- [ ] All **tables and figures** are numbered, captioned, and referenced in the text.
- [ ] **Bibliography** matches cited sources and follows the required style (see Task 09).

---

## Notes

- All task descriptions are in **English**.
- Keep your thesis text consistent with the structure and requirements described in these tasks.
- For submission and binding rules (length, font, margins, etc.), follow **Task 09** and your institution’s template.
- A one-page **thesis outline** mapping chapters to tasks is in [OUTLINE.md](OUTLINE.md).

---

## Publishing this repository to GitHub (PRO-D / PRO-final)

This folder is a **standalone Git repository**. To publish it as `PRO-D/PRO-final` on GitHub:

1. **Create the organization** (if it does not exist): GitHub → Your profile → Organizations → New organization → name it `PRO-D`.
2. **Create the repository**: In organization `PRO-D`, create a new repository named `PRO-final` (do not add a README or .gitignore).
3. **Push from this folder** (use the access token from `.env` in the parent directory):
   ```bash
   cd Zadania_PRO3_D
   git remote add origin https://<YOUR_GH_TOKEN>@github.com/PRO-D/PRO-final.git   # if not already added
   git push -u origin main
   ```
Replace `<YOUR_GH_TOKEN>` with the value of `GH_API_TOKEN` from `.env`.
