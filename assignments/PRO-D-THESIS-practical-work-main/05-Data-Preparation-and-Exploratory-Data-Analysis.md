# Assignment 5 — Data Preparation and Exploratory Data Analysis (EDA)

## 1. Objective of the Assignment

The purpose of this assignment is to develop a rigorous understanding of the dataset before model training begins.

At this stage, the student must demonstrate:

* Analytical awareness of data structure and limitations
* Ability to detect potential risks (bias, imbalance, leakage, noise)
* Capacity to interpret statistical properties rather than merely visualize them
* Understanding of how data characteristics influence modeling decisions

In an engineering thesis, EDA is not an exploratory exercise for intuition alone — it is a methodological step that justifies preprocessing and modeling strategies defined later in Assignment 6.

## 2. Scope of Work to Be Delivered

The student must submit:

* A structured EDA report (4–6 pages)
* Supporting visualizations and summary statistics
* A short methodological reflection connecting findings to experimental design

The document must contain the following components:

### A. Dataset Structure and Integrity Analysis

Provide a formal description of:

* Number of samples
* Number and types of features
* Target variable structure
* Data format and storage

Additionally:

* Verify consistency (duplicates, corrupted entries, invalid values)
* Report missing values per feature
* Identify potential anomalies

This section must go beyond counting — it must interpret whether detected issues threaten experimental validity.

### B. Statistical Characterization

Provide descriptive statistics appropriate to the problem type:

**For numerical features:**

* Mean, median, variance, distribution shape
* Skewness and potential transformations

**For categorical features:**

* Cardinality
* Class distribution

**For target variable:**

* Class imbalance (classification)
* Distribution spread (regression)

The student must explicitly discuss:

* Whether the dataset is balanced
* Whether preprocessing or resampling may be required
* Whether distributional assumptions affect model choice

Interpretation is mandatory — raw statistics without commentary are insufficient.

### C. Correlation and Dependency Analysis

Conduct analysis relevant to the problem context:

* Feature–feature correlations
* Feature–target relationships
* Multicollinearity detection (if applicable)

The student must assess:

* Redundant features
* Potential leakage risks
* Spurious correlations

This analysis should inform later feature engineering decisions (Assignment 6).

### D. Outlier and Noise Assessment

Identify:

* Statistical outliers
* Inconsistent patterns
* Potential labeling noise (if detectable)

Provide a reasoned decision: remove, transform, retain, or investigate further. The justification must consider impact on generalization and fairness.

### E. Bias and Limitation Analysis

This section is critical at the engineering level.

The student must reflect on:

* Sampling bias
* Domain limitations
* Representativeness
* Ethical implications (if relevant)

Demonstrate awareness that data limitations constrain generalizability of conclusions.

### F. Implications for Experimental Design

Conclude with a structured reflection:

* How does EDA influence preprocessing strategy?
* Does it confirm or challenge assumptions from Assignment 3?
* Are adjustments to the experimental design required?

This section must explicitly connect findings to the pipeline architecture. EDA is not isolated analysis — it informs methodological refinement.

## 3. Academic Expectations for an Engineering Thesis

EDA at the engineering level must demonstrate:

* Analytical discipline
* Structured reasoning
* Awareness of modeling implications
* Transparency of limitations

It must avoid:

* Purely visual storytelling
* Superficial interpretation
* Arbitrary preprocessing without analytical basis

The student must show that modeling decisions will be data-informed, not assumption-driven.

## 4. Quality Evaluation Criteria

Assignment 5 will be evaluated based on:

1. Depth of statistical analysis
2. Clarity of interpretation
3. Identification of risks and limitations
4. Logical linkage to experimental design
5. Technical correctness and rigor

Approval of this assignment confirms readiness to formalize preprocessing and feature engineering strategies.

## 5. Position Within the Seminar Continuum

* Assignment 3 defined the experimental architecture.
* Assignment 4 established engineering discipline.
* Assignment 5 validates and refines assumptions about the data.
* Assignment 6 will formalize preprocessing and feature engineering decisions based on this analysis.

Weak data understanding leads to flawed modeling conclusions. Therefore, this stage is analytically foundational for the remainder of the implementation phase.
