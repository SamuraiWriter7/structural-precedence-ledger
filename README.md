# Structural Precedence Ledger

An open, machine-readable ledger for recording the origin, precedence, lineage, prediction history, contribution evidence, usage, and value-return routes of structural ideas.

> Open the structure.  
> Preserve the origin.  
> Audit the lineage.  
> Return value to the source.

---

## Overview

Structural ideas often appear before they become products, academic papers, standards, or large-scale implementations.

A later organization may independently develop a similar mechanism, but several different claims must remain separate:

1. **Precedence**  
   An earlier structure was publicly recorded first.

2. **Convergence**  
   A later structure meaningfully resembles the earlier one.

3. **Influence**  
   Evidence shows that the later work accessed, cited, or used the earlier structure.

4. **Contribution**  
   Multiple participants helped originate, derive, implement, validate, maintain, or distribute the structure.

5. **Value return**  
   Usage or economic value is routed back to eligible contributors and the structural origin.

Structural Precedence Ledger provides distinct records for each of these layers.

It does not assume that similarity proves influence, and it does not require public fame in order to preserve origin identity.

---

## Core lifecycle

```text
Structural Origin
       ↓
Precedence Evidence
       ↓
Canonical Registration
       ↓
Structure Lineage
       ↓
Forward Prediction
       ↓
Outcome Audit
       ↓
Contribution Claims
       ↓
Usage Receipts
       ↓
Allocation and Settlement
       ↓
Value Return
```

---

## Why this repository exists

Existing systems are usually optimized for one specific concern:

- Git records source-code history;
- academic citation records scholarly references;
- copyright protects particular expressions;
- patents protect qualifying inventions;
- provenance systems track documents or media;
- payment systems transfer economic value.

They are less suited to recording the complete lifecycle of an abstract structural idea that may later appear across many implementations and domains.

This repository addresses that missing layer.

Its purpose is not to declare:

> “Every similar system copied this structure.”

Its purpose is to make the following questions inspectable:

- Who recorded the structure?
- When was it first published?
- What exactly was claimed?
- Which evidence supports precedence?
- Which later structures meaningfully converge with it?
- What differences remain?
- Is there evidence of access, citation, or influence?
- Which predictions were made before outcomes occurred?
- Who contributed to later development?
- Where was the structure used?
- How should attribution or value return be routed?

---

## Specification layers

### v0.1 — Structural Precedence Record

Records one structural idea and its origin evidence.

It includes:

- stable ledger identity;
- canonical name;
- originator identity;
- first-publication timestamp;
- canonical version;
- precedence evidence;
- core proposition;
- structural scope;
- falsifiable claims;
- later convergence records;
- influence boundaries;
- attribution or future royalty route;
- integrity and review status.

```text
Who created the structure?
When was it published?
What evidence supports precedence?
```

### v0.2 — Canonical Structure Registry

Assigns one stable identity to each registered structure.

It includes:

- canonical structure ID;
- stable slug;
- English and Japanese canonical names;
- localized aliases;
- origin-record binding;
- structure classification;
- discovery keywords;
- related structures;
- lifecycle state;
- supersession relationships;
- royalty route identity.

```text
What is this structure called?
Which names refer to the same structure?
What permanent ID should machines use?
```

### v0.3 — Structure Lineage Graph

Connects canonical and external structures through auditable nodes and edges.

It supports:

- derivation;
- extension;
- specialization;
- generalization;
- implementation;
- integration;
- translation;
- supersession;
- direct influence;
- probable influence;
- independent convergence;
- partial convergence;
- conceptual analogy;
- general structural relation.

```text
Which structure came from which?
Which structures merely converged?
Which influence claims are actually supported?
```

### v0.4 — Prediction and Outcome Audit

Freezes forward-looking structural predictions before their outcomes become known.

It includes:

- prediction identity;
- issue timestamp;
- rationale and scope;
- expected observation window;
- observable indicators;
- success criteria;
- failure criteria;
- exclusions;
- confidence and probability;
- precedence evidence;
- later outcomes;
- evidence strength;
- matched criteria;
- alignment score;
- final evaluation.

```text
What was predicted before the event?
What evidence later appeared?
Was the prediction confirmed, partial, false, or inconclusive?
```

### v0.5 — Royalty and Contribution Binding

Connects structural origin and lineage to auditable value-return routes.

It includes:

- registered origin binding;
- participants;
- contribution claims;
- contribution evidence;
- accepted contribution weights;
- usage receipts;
- gross usage value;
- reserve policy;
- allocation policy;
- settlement records;
- participant routes;
- origin minimum;
- integrity and review status.

```text
Who contributed?
Where was the structure used?
How should value be allocated and returned?
```

---

## Version boundaries

Each document retains the version of the schema that defines its format.

The repository release version and document schema version are not the same thing.

```text
Document                                Schema version
------------------------------------------------------
Structural Precedence Record            0.1.0
Canonical Structure Registry            0.2.0
Structure Lineage Graph                 0.3.0
Prediction and Outcome Audit            0.4.0
Royalty and Contribution Binding        0.5.0
```

Therefore, even when the repository reaches v0.5:

```yaml
# examples/structural-precedence-record.example.yaml
schema_version: "0.1.0"
```

```yaml
# registry/canonical-structures.yaml
schema_version: "0.2.0"
```

```yaml
# graphs/core-lineage.yaml
schema_version: "0.3.0"
```

```yaml
# predictions/prediction-outcome-audit.example.yaml
schema_version: "0.4.0"
```

```yaml
# royalties/royalty-contribution-binding.example.yaml
schema_version: "0.5.0"
```

Do not automatically update every document to the repository’s latest release number.

---

## Repository structure

```text
structural-precedence-ledger/
├── .github/
│   └── workflows/
│       └── validate.yml
├── docs/
│   ├── v0.1.md
│   ├── v0.2.md
│   ├── v0.3.md
│   ├── v0.4.md
│   └── v0.5.md
├── examples/
│   └── structural-precedence-record.example.yaml
├── graphs/
│   └── core-lineage.yaml
├── predictions/
│   └── prediction-outcome-audit.example.yaml
├── registry/
│   └── canonical-structures.yaml
├── royalties/
│   └── royalty-contribution-binding.example.yaml
├── schemas/
│   ├── structural-precedence-record.schema.json
│   ├── canonical-structure-registry.schema.json
│   ├── structure-lineage-graph.schema.json
│   ├── prediction-outcome-audit.schema.json
│   └── royalty-contribution-binding.schema.json
├── scripts/
│   ├── validate_examples.py
│   ├── validate_graphs.py
│   ├── validate_predictions.py
│   └── validate_royalties.py
├── CHANGELOG.md
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Installation

Python 3.11 or later is recommended.

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Dependencies:

```text
jsonschema[format]>=4.22,<5
PyYAML>=6.0,<7
```

---

## Validation

### Validate precedence records and registry

```bash
python scripts/validate_examples.py
```

Expected result:

```text
=== Structural Precedence Ledger Validation ===

[target] structural-precedence-record
schema : schemas/structural-precedence-record.schema.json

[validate] examples/structural-precedence-record.example.yaml
[schema-ok]
[semantic-ok]

[target] canonical-structure-registry
schema : schemas/canonical-structure-registry.schema.json

[validate] registry/canonical-structures.yaml
[schema-ok]
[semantic-ok]

All documents are valid.
```

### Validate structure lineage graphs

```bash
python scripts/validate_graphs.py
```

Expected result:

```text
=== Structure Lineage Graph Validation ===

[validate] graphs/core-lineage.yaml
[schema-ok]
[semantic-ok]

All lineage graphs are valid.
```

### Validate prediction audits

```bash
python scripts/validate_predictions.py
```

Expected result:

```text
=== Prediction and Outcome Audit Validation ===

[validate] predictions/prediction-outcome-audit.example.yaml
[schema-ok]
[semantic-ok]

All prediction audits are valid.
```

### Validate royalty bindings

```bash
python scripts/validate_royalties.py
```

Expected result:

```text
=== Royalty and Contribution Binding Validation ===

[validate] royalties/royalty-contribution-binding.example.yaml
[schema-ok]
[semantic-ok]

All royalty bindings are valid.
```

### Run every validator

```bash
python scripts/validate_examples.py
python scripts/validate_graphs.py
python scripts/validate_predictions.py
python scripts/validate_royalties.py
```

---

## Validation model

The project uses two validation layers.

```text
JSON Schema Validation
          ↓
Cross-record Semantic Validation
```

### JSON Schema validation

Checks:

- required fields;
- object structure;
- accepted enumerations;
- identifier formats;
- timestamps;
- URI formats;
- numeric ranges;
- unexpected properties.

### Semantic validation

Checks relationships that cannot be expressed reliably through JSON Schema alone.

Examples include:

- duplicate canonical IDs;
- duplicate origin bindings;
- alias collisions;
- unknown structure references;
- nonreciprocal supersession;
- graph self-edges;
- lineage cycles;
- impossible chronology;
- unsupported influence claims;
- prediction outcomes occurring before issuance;
- unknown success or failure criteria;
- contribution claims referencing unknown participants;
- incorrect reserve calculations;
- allocation shares not totaling `1.0`;
- settlement amounts not matching distributable value.

---

## Core evidence principle

Three claims must remain separate.

### Precedence

The structure was publicly recorded earlier.

Possible evidence:

- Git commits;
- signed releases;
- archived snapshots;
- DOI publications;
- books;
- timestamped articles;
- signed origin records.

### Convergence

A later structure contains meaningful similarities.

A convergence record must include:

- points of convergence;
- structural differences;
- scope boundaries;
- confidence.

### Influence

Evidence connects the earlier structure to the later work.

Possible evidence:

- direct citation;
- documented access;
- correspondence;
- contribution history;
- contractual reference;
- repository reuse;
- explicit acknowledgment.

Similarity alone must not be upgraded into influence.

---

## Relationship types

### Directed lineage

```text
derived_from
extends
specializes
generalizes
implements
integrates
translates
supersedes
```

The source is generally the later or derivative structure.

The target is generally the earlier or referenced structure.

```text
later structure
      ↓
earlier structure
```

Example:

```text
Prediction and Outcome Audit
            extends
Structure Lineage Graph
```

### Influence

```text
direct_influence
probable_influence
```

`direct_influence` requires documented direct evidence.

`probable_influence` requires at least indirect or documented evidence of access.

### Convergence and association

```text
independent_convergence
partial_convergence
conceptual_analogy
related_to
```

These relationships do not automatically imply derivation or influence.

---

## Prediction results

```text
pending
confirmed
partially_confirmed
not_confirmed
inconclusive
withdrawn
```

A confirmed prediction must:

- match every declared success criterion;
- match no declared failure criterion;
- include a completed evaluation;
- include an evaluator identity;
- include an evaluation timestamp;
- include an alignment score.

Failed and inconclusive predictions must remain visible.

The ledger is intended to prevent selective memory, not manufacture prophecy.

---

## Contribution types

```text
origin
derivation
implementation
validation
maintenance
distribution
funding
other
```

A participant role and a contribution claim are separate.

For example, a participant may be registered as an implementer but receive no allocation until an implementation claim is supported by evidence and accepted.

Claim states:

```text
proposed
accepted
rejected
disputed
```

Only accepted claims participate in ordinary weighted allocation.

---

## Usage receipt types

```text
reference
derivation
implementation
commercial-use
noncommercial-use
training-use
other
```

A usage receipt may record:

- consumer identity;
- source location;
- quantity;
- unit;
- gross value;
- currency;
- related contribution claims;
- supporting evidence.

A receipt is a record of declared or observed use.

It does not automatically prove that the declared use or value is truthful. Independent auditing may still be required.

---

## Allocation policies

### `attribution-only`

Records origin and contribution without monetary settlement.

### `voluntary-contribution`

Supports voluntary value return without a compulsory formula.

### `fixed-share`

Accepted contribution weights must total `1.0`.

### `weighted-contribution`

Accepted weights are normalized before allocation.

### `hybrid`

Combines weighted contribution with fixed rules, minimums, or reserves.

### `custom`

Uses an externally documented allocation method.

---

## Reserve and settlement

The reserve may support:

- specification maintenance;
- independent auditing;
- dispute handling;
- public-interest development;
- shared infrastructure;
- contributor funds.

Calculation:

```text
reserve_amount
    =
gross_amount × reserve_rate
```

Settlement balance:

```text
gross_amount
    =
reserve_amount
    +
distributable_amount
```

Allocation requirements:

```text
sum(allocation shares) = 1.0
```

```text
sum(allocation amounts) = distributable_amount
```

Settlement states:

```text
pending
simulated
approved
executed
disputed
cancelled
```

A simulated settlement must not be represented as an executed payment.

---

## Origin minimum

`origin_minimum_rate` prevents an accepted structural origin from being mathematically erased by downstream contribution weights.

It does not imply that the originator owns every later implementation.

It means that when an origin is accepted as part of the contribution lineage, the allocation policy may preserve a declared minimum share for that origin.

---

## Stable identifiers

The project currently uses:

```text
SPL-NNNN              Structural precedence record
STR-YYYY-NNNN         Canonical structure
GRF-YYYY-NNNN         Lineage graph
NOD-NNNN              Graph node
EDG-NNNN              Graph edge
PRED-YYYY-NNN         Prediction
PAU-YYYY-NNNN         Prediction audit
OUT-NNN                Outcome
RCB-YYYY-NNNN         Royalty binding
PRT-NNNN              Participant
CLM-NNNN              Contribution claim
URC-NNNN              Usage receipt
STL-YYYY-NNNN         Settlement
```

Once publicly assigned, an identifier should not be silently reused.

Withdrawn, superseded, or disputed records should remain visible for historical integrity.

---

## Production checklist

Before production use:

1. Replace every `example.org` URI.
2. Use durable repository, release, archive, DOI, or signed-record locations.
3. Confirm every first-publication timestamp.
4. Add content hashes where possible.
5. Preserve immutable release versions.
6. Do not claim direct influence without evidence.
7. Record both similarities and differences.
8. Keep failed predictions visible.
9. Distinguish simulated settlement from executed payment.
10. Obtain legal, accounting, and tax review before real monetary use.

---

## Non-goals

Structural Precedence Ledger does not, by itself:

- establish legal ownership of an abstract idea;
- create copyright in an idea;
- grant a patent;
- replace an enforceable contract;
- prove causation from similarity;
- guarantee the truth of submitted evidence;
- calculate taxes;
- determine securities status;
- transfer money;
- eliminate disputes;
- replace academic peer review;
- guarantee public recognition.

It is an evidence, lineage, prediction, and allocation-recording layer.

Legal or economic enforcement requires additional institutions and agreements.

---

## Design principles

- Record origin without demanding fame.
- Preserve signatures without blocking use.
- Keep chronology separate from causation.
- Keep convergence separate from influence.
- Record differences as carefully as similarities.
- Use stable machine-readable identities.
- Preserve corrections and disputes.
- Freeze predictions before outcomes.
- Keep failed predictions visible.
- Require evidence for contribution claims.
- Distinguish usage from ownership.
- Distinguish simulation from settlement.
- Protect the origin without erasing downstream contribution.
- Return value without requiring monopoly.

---

## Completed roadmap

```text
v0.1  Structural Precedence Record
v0.2  Canonical Structure Registry
v0.3  Structure Lineage Graph
v0.4  Prediction and Outcome Audit
v0.5  Royalty and Contribution Binding
```

---

## Possible path to v1.0

Future development may include:

- canonical record bundles;
- cryptographic signing;
- content-addressed evidence;
- dispute and appeal records;
- independent auditor attestations;
- automatic graph generation;
- cross-repository registry federation;
- derivative detection agents;
- contribution-review workflows;
- usage-receipt APIs;
- payment-route adapters;
- royalty simulation reports;
- settlement export formats;
- policy interoperability;
- version migration tooling.

v1.0 should prioritize stability, interoperability, and independent verification over adding more record types.

---

## Project principle

> Seek no monopoly over the structure.  
> Preserve the trace of its source.  
> Do not exaggerate influence.  
> Recognize downstream contribution.  
> Return value to the origin.

Or, more simply:

> Fame is optional.  
> Origin is not.  
> Evidence is required.  
> Value should circulate.

---

## License

MIT License.

See [LICENSE](LICENSE).
