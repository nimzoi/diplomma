# Assignment 7 — Baseline Models

## 1. Objective of the Assignment

The purpose of this assignment is to establish a reliable empirical reference point against which all subsequent modeling efforts will be compared.

At this stage, the student must demonstrate:

* Ability to implement models within the approved experimental framework
* Understanding of controlled evaluation
* Awareness of fairness in comparison
* Capacity to interpret results critically rather than descriptively

Baseline modeling is not a formality. It defines the minimum performance threshold and determines whether more complex methods are justified. In an engineering thesis, model sophistication is secondary to methodological correctness.

## 2. Scope of Work to Be Delivered

The student must submit:

* Implemented baseline models integrated into the approved pipeline
* Structured evaluation results
* Comparative analysis (2–4 pages)
* Clear linkage between research question and obtained results

The submission must include the following components:

### A. Definition and Justification of Baseline Models

The student must implement at least:

1. **One simple model** (e.g., linear/logistic regression or equivalent minimal predictor)
2. **One classical machine learning model** (e.g., decision tree, random forest, gradient boosting)

For each model, provide:

* Rationale for selection (grounded in Assignment 2 literature review)
* Expected strengths and weaknesses
* Key hyperparameters and default choices

Model selection must not be arbitrary. The baseline must reflect realistic methodological standards in the field.

### B. Controlled Training Protocol

All models must:

* Use identical data splits
* Use identical preprocessing pipeline
* Follow the evaluation protocol defined in Assignment 3

Explicitly confirm:

* No data leakage occurred
* Hyperparameter tuning did not contaminate the test set
* Random seeds were fixed where appropriate

The student must show awareness that experimental fairness is a scientific requirement.

### C. Hyperparameter Configuration Strategy

For baseline models:

* Clearly distinguish between default and tuned configurations
* Describe tuning method (if applied)
* Limit search space to realistic engineering scope

If tuning is minimal, justify why. Over-optimization of baselines is discouraged unless it serves a methodological purpose.

### D. Performance Evaluation and Reporting

Present results using:

* Structured tables
* Clear metric definitions
* If appropriate, cross-validation averages and standard deviations

Metrics must match those defined in Assignment 1 and formalized in Assignment 3. The student must:

* Avoid selective reporting
* Report all relevant metrics
* Maintain consistency across models

Performance reporting must be transparent and reproducible.

### E. Critical Interpretation of Results

This section is central to the assignment.

The student must analyze:

* Which model performs best and why
* Whether results align with expectations from literature
* Whether performance differences are practically significant
* How results relate to the research question

Avoid:

* Superficial ranking of models
* Claiming superiority without analysis
* Ignoring limitations

The analysis must explicitly answer:

* What have we learned from the baseline stage?
* Does the baseline performance justify moving toward more complex models?

## 3. Academic Expectations for an Engineering Thesis

At the engineering level, baseline modeling must demonstrate:

* Controlled experimentation
* Comparative reasoning
* Technical transparency
* Awareness of model assumptions

The thesis is expected to:

* Justify model complexity
* Show improvement relative to a meaningful reference
* Maintain methodological discipline

It must avoid:

* Arbitrary experimentation
* Excessive focus on performance without interpretation
* Uncontrolled hyperparameter tuning

## 4. Quality Evaluation Criteria

Assignment 7 will be evaluated based on:

1. Correctness of implementation
2. Fairness of experimental comparison
3. Transparency of reporting
4. Depth of critical interpretation
5. Alignment with research objectives

Approval of this assignment confirms readiness to proceed to advanced or primary modeling.

## 5. Position Within the Seminar Continuum

* Assignments 1–3 defined and structured the research problem.
* Assignments 4–6 ensured engineering and data discipline.
* Assignment 7 establishes the empirical baseline.
* Assignment 8 will introduce the primary (target) model and optimization strategy.

From this stage onward:

* All claims of improvement must be benchmarked against these baseline results.
* Any architectural change must preserve comparability.
* Experimental rigor becomes cumulative and irreversible.

A thesis without a strong baseline lacks scientific credibility. Therefore, this stage defines the empirical foundation of the entire practical contribution.
