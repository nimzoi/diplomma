# Assignment 3 — Project Architecture and Experimental Plan

## 1. Objective of the Assignment

The purpose of this assignment is to translate the validated research problem (Assignment 1) and the identified research gap (Assignment 2) into a structured experimental plan.

At this stage, the student must demonstrate:

* Ability to operationalize abstract research questions
* Understanding of experimental comparability and fairness
* Awareness of reproducibility standards
* Capacity to design a technically coherent implementation pipeline

This assignment marks the transition from conceptual work to engineering execution. The quality of the experimental design directly determines the scientific value of the implementation phase.

## 2. Scope of Work to Be Delivered

The student must submit a structured document (4–6 pages) containing:

* A formal experimental framework
* A pipeline architecture diagram
* A dataset and evaluation protocol description
* A justified selection of baseline and comparative models
* A feasibility timeline

The document must contain the following components:

### A. Operationalization of the Research Question

The student must explicitly map:

* Research question → measurable experimental variables
* Hypothesis → evaluation metric(s)
* Research gap → comparison strategy

This section must answer:

* What exactly will be tested?
* What constitutes empirical evidence?
* What comparison validates the hypothesis?

The goal is to eliminate ambiguity before implementation begins.

### B. Dataset Description and Justification

Provide a structured dataset analysis including:

* Source and accessibility
* Size (number of samples, features, classes if applicable)
* Data type and structure
* Known biases or limitations
* Licensing and reproducibility considerations

Additionally:

* Justify why this dataset is appropriate for answering the research question.
* If multiple datasets are considered, explain the rationale.
* If data collection or preprocessing is required, describe the planned methodology at a high level.

An engineering thesis must demonstrate awareness of dataset constraints and their impact on generalization.

### C. Experimental Pipeline Architecture

Provide a formal diagram and structured explanation of the full pipeline:

**Data → Preprocessing → Feature Engineering → Model → Evaluation → Comparison**

The pipeline must:

* Reflect modular design
* Allow controlled comparison between models
* Ensure reproducibility

The student must clarify:

* Which components remain fixed across experiments
* Which components vary
* How data leakage will be prevented

The architecture should support systematic experimentation, not ad hoc implementation.

### D. Baseline and Comparative Models

Based on Assignment 2, define:

* At least one simple baseline model
* At least one classical machine learning model
* The proposed primary model (core contribution)

For each model specify:

* Rationale for inclusion
* Expected strengths and weaknesses
* Key hyperparameters

The selection must be literature-justified, not arbitrary. Comparability must be ensured through:

* Identical train/test splits
* Identical preprocessing steps where appropriate
* Controlled evaluation conditions

### E. Evaluation Protocol

Formally define:

* Train/validation/test split strategy
* Cross-validation procedure (if applicable)
* Primary and secondary metrics
* Statistical comparison approach (if relevant)

The evaluation design must prevent:

* Data leakage
* Inflated performance reporting
* Unfair hyperparameter optimization bias

The student must demonstrate understanding that evaluation is part of the research methodology, not a final reporting step.

### F. Risk Assessment and Feasibility Plan

Provide a short but realistic analysis covering:

* Computational requirements
* Estimated training time
* Possible technical bottlenecks
* Alternative fallback strategies

Include a high-level timeline for:

* Data preparation
* Baseline implementation
* Model optimization
* Evaluation and analysis

An engineering thesis must balance ambition with feasibility.

## 3. Academic Expectations for an Engineering Thesis

At the engineering level, experimental design must demonstrate:

* Structured reasoning
* Controlled comparison
* Awareness of methodological validity
* Engineering discipline

The thesis is expected to:

* Provide systematic evaluation
* Compare multiple approaches
* Justify implementation decisions

It is not required to:

* Conduct large-scale industrial benchmarking
* Perform exhaustive hyperparameter searches
* Introduce new theoretical frameworks

However, it must avoid:

* Informal experimentation
* Trial-and-error development without documentation
* Post hoc metric selection

## 4. Quality Evaluation Criteria

Assignment 3 will be assessed according to:

1. Logical coherence between research question and experimental design
2. Adequacy and justification of model selection
3. Rigor of evaluation protocol
4. Reproducibility considerations
5. Feasibility and technical realism

Approval of this assignment authorizes the student to begin full implementation (Block II).

## 5. Position Within the Seminar Continuum

* Assignment 1 defined the research problem.
* Assignment 2 validated and positioned it within existing knowledge.
* Assignment 3 operationalizes it into a structured engineering experiment.

From this point onward:

* Implementation decisions must follow the approved architecture.
* Deviations must be documented and justified.
* Experimental discipline becomes mandatory.

A poorly designed experiment cannot be repaired at the analysis stage. Therefore, this assignment represents the methodological contract for the practical phase.
