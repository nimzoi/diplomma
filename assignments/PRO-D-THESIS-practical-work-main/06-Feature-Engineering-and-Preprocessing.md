# Assignment 6 — Feature Engineering and Preprocessing

## 1. Objective of the Assignment

The purpose of this assignment is to translate the analytical insights from Assignment 5 into a structured and justified preprocessing and feature engineering pipeline.

At this stage, the student must demonstrate:

* Methodological discipline in transforming raw data
* Ability to justify preprocessing decisions empirically
* Awareness of the interaction between data transformation and model behavior
* Understanding of leakage prevention and experimental fairness

Feature engineering is not a mechanical step. It is a design decision that directly influences the validity and interpretability of experimental results. In an engineering thesis, every transformation must be:

* Explicit
* Reproducible
* Justified

## 2. Scope of Work to Be Delivered

The student must submit:

* A structured methodological document (4–6 pages)
* A formal description of the preprocessing pipeline
* Justified transformation choices
* Evidence that the pipeline prevents data leakage

The document must contain the following components:

### A. Preprocessing Strategy Overview

Provide a high-level description of:

* Which transformations will be applied
* At which stage of the pipeline
* Which components remain constant across models

Explicitly connect this section to findings from Assignment 5. The student must clarify:

* Which issues identified in EDA require transformation
* Which aspects of the dataset remain unchanged

The goal is to show analytical continuity between data understanding and transformation design.

### B. Data Cleaning and Missing Value Strategy

Describe and justify:

* Handling of missing values (imputation, removal, model-based methods)
* Handling of duplicates
* Treatment of inconsistent entries

The student must explain:

* Why the chosen method is appropriate
* How it affects model generalization
* Whether alternative approaches were considered

Arbitrary or convenience-based decisions are unacceptable.

### C. Scaling, Normalization, and Encoding

Define and justify:

* Feature scaling strategy (standardization, normalization, robust scaling, none)
* Categorical encoding methods (one-hot, ordinal, target encoding, etc.)
* Treatment of high-cardinality features

The student must explicitly discuss:

* Which models require scaling
* Whether scaling is applied before or within cross-validation
* How transformation consistency across training and testing is ensured

Improper scaling is a common source of experimental bias and must be addressed rigorously.

### D. Feature Engineering and Transformation

This section represents the core design component.

Describe:

* Newly constructed features (if any)
* Dimensionality reduction (if applicable)
* Domain-specific transformations
* Feature selection methods

For each engineered feature, explain:

* Motivation
* Expected contribution
* Potential risks (overfitting, leakage, multicollinearity)

Feature engineering must align with the research hypothesis where relevant.

### E. Feature Selection Strategy

If feature selection is applied, specify:

* Method used (filter, wrapper, embedded)
* Selection criteria
* Validation protocol

The student must ensure that feature selection:

* Occurs only within training folds
* Does not introduce data leakage
* Is reproducible

Explain how feature selection impacts interpretability and computational cost.

### F. Pipeline Formalization and Reproducibility

Provide a formal description of how preprocessing is implemented in code:

* Integrated pipeline object (if applicable)
* Separation of training and inference transformations
* Configuration-driven parameterization

Demonstrate that:

* The entire transformation process can be reproduced
* Preprocessing is consistently applied across experiments
* No manual intervention occurs between training runs

This section must align with the engineering discipline defined in Assignment 4.

### G. Impact on Experimental Design

Conclude with a structured reflection addressing:

* How preprocessing choices influence baseline comparability
* Whether alternative preprocessing strategies will be compared experimentally
* How transformation decisions relate to the research question

This ensures conceptual continuity with Assignments 1–3.

## 3. Academic Expectations for an Engineering Thesis

At the engineering level, preprocessing must demonstrate:

* Analytical justification
* Controlled methodology
* Explicit documentation
* Reproducibility

The thesis is expected to:

* Clearly distinguish raw data from processed data
* Avoid leakage and evaluation bias
* Maintain fairness across model comparisons

It must avoid:

* Hidden transformations
* Undocumented feature engineering
* Data-dependent transformations outside training folds

## 4. Quality Evaluation Criteria

Assignment 6 will be evaluated based on:

1. Logical connection to EDA findings
2. Methodological justification of transformations
3. Leakage prevention rigor
4. Reproducibility and pipeline clarity
5. Alignment with research objectives

Approval of this assignment confirms readiness to implement baseline models under controlled conditions.

## 5. Position Within the Seminar Continuum

* Assignment 5 established empirical understanding of the data.
* Assignment 6 formalizes how the data is transformed.
* Assignment 7 will introduce baseline modeling under the defined preprocessing regime.

From this point onward:

* The preprocessing pipeline is considered fixed unless formally revised.
* Any changes must be documented and justified.
* Experimental comparability becomes mandatory.

Data transformation is the methodological bridge between understanding and modeling. Its rigor determines the credibility of all subsequent results.
