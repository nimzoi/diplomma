# Assignment 4 — Reproducibility and Code Organization

## 1. Objective of the Assignment

The purpose of this assignment is to establish the technical and organizational foundation for the practical implementation phase.

At this stage, the student must demonstrate:

* Understanding of reproducible research standards
* Ability to structure a technical project professionally
* Awareness of software engineering discipline in data science projects
* Commitment to transparency and experimental traceability

An engineering thesis in Data Science is not evaluated solely on model performance, but also on the quality, clarity, and reproducibility of implementation. This assignment formalizes the technical environment in which all subsequent experiments will be conducted.

## 2. Scope of Work to Be Delivered

The student must provide:

* A structured repository (local and version-controlled)
* A documented environment specification
* A reproducibility protocol
* A brief technical description (2–3 pages) explaining architectural decisions

The submission must include the following components:

### A. Repository Structure and Modularity

The project must follow a logically organized structure. A recommended structure includes:

* **data/** — raw and processed datasets (with clear separation)
* **src/** — source code modules
* **models/** — trained models (or references to storage location)
* **notebooks/** — exploratory analysis (if used)
* **reports/** — generated outputs and figures
* **config/** — configuration files
* **README.md** — project documentation

**Expectations:**

* Clear separation between experimental scripts and reusable modules
* No hard-coded paths
* No implicit dependencies
* Modular design allowing reuse and extension

The structure must reflect pipeline clarity defined in Assignment 3.

### B. Environment and Dependency Management

The student must provide:

* **requirements.txt** or **environment.yml**
* Python version specification
* Explicit library versions
* Hardware description (CPU/GPU, RAM)

Additionally, describe:

* Random seed handling
* Determinism considerations
* External resource dependencies (if any)

The environment must allow the supervisor to replicate results without ambiguity. Reproducibility is a scientific requirement, not a convenience.

### C. Version Control and Experimental Traceability

The project must be maintained using Git or equivalent version control.

The student must demonstrate:

* Meaningful commit structure
* Version tagging (if relevant)
* Documentation of major experimental changes

Additionally, provide:

* Description of experiment tracking approach (e.g., logging system, structured result storage)
* Clear mapping between experiment configuration and reported results

Results presented in the thesis must be traceable to specific code states.

### D. Configuration and Experiment Management

Experiments must not rely on manual parameter modification inside scripts.

The student must:

* Implement configuration files (e.g., YAML, JSON, argument parsers)
* Separate model parameters from implementation logic
* Enable systematic parameter variation

The design should allow:

* Controlled comparison between models
* Reproducible reruns
* Scalability of experimental design

This enforces methodological discipline aligned with Assignment 3.

### E. Documentation and README Standards

The README file must include:

* Project objective (brief reference to research question)
* Installation instructions
* Execution instructions
* Description of pipeline stages
* Expected outputs

The documentation must enable a technically competent reader to:

1. Install dependencies
2. Run preprocessing
3. Train baseline model
4. Reproduce reported results

Clarity and precision are expected.

## 3. Academic Expectations for an Engineering Thesis

At the engineering level, implementation must demonstrate:

* Structured software design
* Clear separation of concerns
* Reproducibility and traceability
* Professional coding standards

The thesis is not evaluated as production software, but it must:

* Avoid chaotic notebook-only development
* Avoid undocumented scripts
* Avoid hidden preprocessing steps

The implementation environment must support scientific accountability.

## 4. Quality Evaluation Criteria

Assignment 4 will be evaluated based on:

1. Logical repository structure
2. Reproducibility completeness
3. Modularity and configurability
4. Documentation clarity
5. Consistency with the experimental design (Assignment 3)

Approval of this assignment confirms readiness for systematic experimentation.

## 5. Position Within the Seminar Continuum

* Assignment 3 defined what will be tested.
* Assignment 4 defines how it will be implemented and controlled.

From this point onward:

* All experiments must follow the defined structure
* Deviations require justification
* Informal experimentation is no longer acceptable

This stage marks the transition from conceptual design to disciplined engineering execution.
