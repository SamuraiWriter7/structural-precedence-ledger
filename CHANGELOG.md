# Changelog

All notable changes to Structural Precedence Ledger are documented in this file.

The format is based on Keep a Changelog.

The project uses semantic versioning for specification releases.

---

## [Unreleased]

### Planned

- Replace placeholder `example.org` URIs with durable production references.
- Add canonical precedence records for every registered structure.
- Add cryptographic content digests to published evidence.
- Add dispute and appeal record formats.
- Add independent auditor attestation support.
- Add cross-repository registry federation.
- Add migration guidance toward v1.0.
- Add real-world external convergence examples.
- Add additional royalty policy simulations.

---

## [0.5.0] - 2026-07-18

### Added

- Royalty and Contribution Binding specification.
- Royalty and Contribution Binding JSON Schema.
- Stable royalty-binding identifiers.
- Canonical structure binding.
- Binding-scope records.
- Registry-bound origin identities.
- Precedence-record bindings.
- Royalty-route bindings.
- Participant records.
- Participant external identities.
- Participant role classification.
- Participant activity state.
- Participant value-return routes.
- Contribution claims.
- Contribution-type classification.
- Contribution descriptions.
- Contribution evidence.
- Contribution weights.
- Claim assessment timestamps.
- Proposed claim state.
- Accepted claim state.
- Rejected claim state.
- Disputed claim state.
- Usage receipts.
- Usage-type classification.
- Consumer identities.
- Usage quantities and units.
- Gross usage values.
- Currency records.
- Usage-to-claim references.
- Usage evidence.
- Allocation policy modes.
- Attribution-only policy.
- Voluntary-contribution policy.
- Fixed-share policy.
- Weighted-contribution policy.
- Hybrid policy.
- Custom policy.
- Reserve rates.
- Reserve routes.
- Minimum-origin allocation rates.
- Settlement records.
- Stable settlement identifiers.
- Pending settlements.
- Simulated settlements.
- Approved settlements.
- Executed settlements.
- Disputed settlements.
- Cancelled settlements.
- Gross settlement values.
- Reserve values.
- Distributable values.
- Participant allocation shares.
- Participant allocation amounts.
- Settlement route records.
- Settlement evidence.
- Royalty-binding audit metadata.
- Royalty validation script.
- Initial simulated royalty example.
- GitHub Actions royalty validation.
- `Royalty and Contribution Binding` canonical registry entry.
- `Royalty and Contribution Binding` lineage-graph node.
- Lineage edges connecting v0.5 to v0.4 and v0.1.

### Semantic validation

- Reject unknown canonical structure IDs.
- Require originator identity to match the registry.
- Require precedence-record identity to match the registry.
- Require royalty-route identity to match the registry.
- Detect duplicate participant IDs.
- Detect duplicate participant external IDs.
- Detect duplicate claim IDs.
- Detect duplicate usage-receipt IDs.
- Detect duplicate evidence IDs.
- Detect duplicate royalty-binding IDs across documents.
- Detect duplicate settlement IDs across documents.
- Require exactly one participant matching the registered originator.
- Require an accepted origin contribution claim.
- Reject unknown participant references.
- Reject unknown claim references.
- Reject evidence recorded after claim assessment.
- Reject evidence recorded after receipt creation.
- Require accepted positive weight for weighted policies.
- Require fixed-share weights to total `1.0`.
- Require receipt currency when gross value is declared.
- Require receipt currency to match policy currency.
- Require settlement currency to match policy currency.
- Require positive reserve rates to specify reserve routes.
- Validate reserve calculations.
- Validate gross, reserve, and distributable balance.
- Validate usage-receipt gross-value totals.
- Require allocation shares to total `1.0`.
- Require allocation amounts to equal distributable value.
- Enforce minimum-origin allocation.
- Validate weighted allocation against accepted claims.
- Reject allocation to unknown participants.
- Reject allocation to inactive participants.
- Require routes for executed allocations.
- Validate audit chronology.
- Distinguish pending settlements from calculated settlements.
- Distinguish simulated settlement from executed payment.

### Registry

- Registered `Royalty and Contribution Binding` as `STR-2026-0005`.
- Added v0.5 to related-structure references.
- Added royalty, contribution, usage, allocation, settlement, and value-return discovery metadata.

### Graph

- Added `Royalty and Contribution Binding` as `NOD-0005`.
- Added `EDG-0006`: v0.5 extends Prediction and Outcome Audit.
- Added `EDG-0007`: v0.5 integrates Structural Precedence Ledger.
- Preserved graph schema version `0.3.0`.

### Documentation

- Added `docs/v0.5.md`.
- Added royalty policy documentation.
- Added contribution-claim documentation.
- Added usage-receipt documentation.
- Added reserve and settlement formulas.
- Added origin-minimum explanation.
- Added production-use warnings.
- Clarified that the specification does not itself transfer money.
- Clarified that monetary use requires separate legal, tax, and accounting review.

### Principles established

- Structural use should remain traceable.
- Contribution must be supported by evidence.
- Origin and downstream contribution may coexist.
- Usage receipts should precede settlement.
- Allocation policy must remain explicit.
- The origin must not be mathematically erased.
- Monetary execution must remain distinguishable from simulation.
- Value return must not depend solely on public fame.

---

## [0.4.0] - 2026-07-18

### Added

- Prediction and Outcome Audit specification.
- Prediction and Outcome Audit JSON Schema.
- Stable prediction-audit identifiers.
- Stable prediction identifiers.
- Prediction issuance timestamps.
- Prediction issuer identities.
- Open prediction state.
- Closed prediction state.
- Withdrawn prediction state.
- Forward-looking claims.
- Prediction rationale.
- Prediction scope.
- Expected observation windows.
- Observable indicators.
- Explicit success criteria.
- Explicit failure criteria.
- Prediction exclusions.
- Confidence labels.
- Numeric prediction probabilities.
- Prediction precedence evidence.
- Prediction withdrawal reasons.
- Outcome records.
- Stable outcome identifiers.
- Outcome observation timestamps.
- Outcome source references.
- Outcome relevance classification.
- Supporting outcomes.
- Contradicting outcomes.
- Mixed outcomes.
- Irrelevant outcomes.
- Weak evidence classification.
- Moderate evidence classification.
- Strong evidence classification.
- Indicator-to-outcome bindings.
- Evaluation timestamps.
- Evaluator identities.
- Pending evaluation state.
- Confirmed evaluation state.
- Partially confirmed evaluation state.
- Not-confirmed evaluation state.
- Inconclusive evaluation state.
- Withdrawn evaluation state.
- Alignment scores.
- Matched success criteria.
- Matched failure criteria.
- Evaluation reasoning.
- Evaluation limitations.
- Prediction-audit integrity metadata.
- Prediction validation script.
- Initial internal roadmap prediction audit.
- GitHub Actions prediction validation.
- `Prediction and Outcome Audit` canonical registry entry.
- `Prediction and Outcome Audit` lineage-graph node.
- Lineage edges connecting v0.4 to v0.3 and v0.1.

### Semantic validation

- Reject unknown canonical structure IDs.
- Detect duplicate audit IDs.
- Detect duplicate prediction IDs.
- Detect duplicate success-criterion IDs.
- Detect duplicate failure-criterion IDs.
- Detect duplicate outcome IDs.
- Detect duplicate prediction-evidence IDs.
- Detect duplicate outcome-source URIs.
- Reject observation windows beginning before prediction issuance.
- Reject observation-window end dates preceding start dates.
- Reject precedence evidence recorded after prediction issuance.
- Reject outcomes occurring before prediction issuance.
- Reject invalid observable-indicator indexes.
- Validate confidence labels against numeric probability.
- Reject unknown success-criterion references.
- Reject unknown failure-criterion references.
- Require open predictions to remain pending.
- Require closed predictions to use completed evaluations.
- Require withdrawn predictions to include withdrawal reasons.
- Require withdrawn prediction status and result to agree.
- Require completed evaluations to include evaluator identity.
- Require completed evaluations to include evaluation timestamp.
- Require completed evaluations to include alignment score.
- Reject evaluations occurring before prediction issuance.
- Reject evaluations occurring before recorded outcomes.
- Require confirmed results to match every success criterion.
- Reject confirmed results containing failure criteria.
- Require partial confirmation to match at least one success criterion.
- Prevent complete success from being labeled partially confirmed.

### Registry

- Registered `Prediction and Outcome Audit` as `STR-2026-0004`.
- Added v0.4 to related-structure references.
- Added prediction, outcome, forecast, criteria, confidence, and evaluation discovery metadata.

### Graph

- Added `Prediction and Outcome Audit` as `NOD-0004`.
- Added `EDG-0004`: v0.4 extends Structure Lineage Graph.
- Added `EDG-0005`: v0.4 integrates Structural Precedence Ledger.
- Preserved graph schema version `0.3.0`.

### Workflow

- Added required-file checks before validation.
- Added prediction-schema checks.
- Added prediction-example checks.
- Added dedicated prediction-validation step.

### Documentation

- Added `docs/v0.4.md`.
- Added prediction lifecycle documentation.
- Added outcome relevance documentation.
- Added confidence-range documentation.
- Added evaluation-result documentation.
- Clarified that failed and inconclusive predictions must remain visible.
- Clarified that hindsight resemblance is weaker than a timestamped prediction.
- Clarified independent schema-version boundaries.

### Principles established

- Predictions must be frozen before outcomes are known.
- Success and failure criteria must be declared in advance.
- Prediction confidence must be machine-readable.
- Failed predictions must remain visible.
- Outcome relevance and evidence strength are separate.
- Predictions must not be retrospectively rewritten.
- Prediction records do not replace scientific peer review.

---

## [0.3.0] - 2026-07-18

### Added

- Structure Lineage Graph specification.
- Structure Lineage Graph JSON Schema.
- Stable graph identifiers.
- Stable graph-node identifiers.
- Stable graph-edge identifiers.
- Canonical structure nodes.
- External structure nodes.
- Canonical registry bindings.
- External structure identities.
- Node publication timestamps.
- Node source references.
- Node keywords.
- Node content digests.
- Derivation relationships.
- Extension relationships.
- Specialization relationships.
- Generalization relationships.
- Implementation relationships.
- Integration relationships.
- Translation relationships.
- Supersession relationships.
- Direct influence relationships.
- Probable influence relationships.
- Independent convergence relationships.
- Partial convergence relationships.
- Conceptual analogy relationships.
- General related-structure relationships.
- Edge confidence values.
- Edge assertion timestamps.
- Edge assertion identities.
- Edge convergence descriptions.
- Edge difference descriptions.
- Edge evidence.
- Edge influence audits.
- Graph-level audit metadata.
- Registry-to-graph identity validation.
- Registry-to-graph timestamp validation.
- Directed-lineage cycle detection.
- Dedicated graph validation script.
- Initial core lineage graph.
- `Structure Lineage Graph` canonical registry entry.

### Semantic validation

- Detect duplicate node IDs.
- Detect duplicate edge IDs.
- Detect duplicate canonical structure nodes.
- Detect duplicate external structure nodes.
- Detect duplicate graph-evidence IDs.
- Require sorted node IDs.
- Require sorted edge IDs.
- Reject unknown canonical registry entries.
- Detect canonical-name mismatches.
- Detect first-publication timestamp mismatches.
- Reject missing source nodes.
- Reject missing target nodes.
- Reject graph self-edges.
- Reject duplicate directed edges.
- Reject reversed duplicate symmetric relationships.
- Reject lineage edges with impossible chronology.
- Reject assertions made before node publication.
- Require documented direct evidence for `direct_influence`.
- Require access evidence for `probable_influence`.
- Reject direct-influence evidence under `independent_convergence`.
- Reject documented citation under `independent_convergence`.
- Detect directed lineage cycles.

### Registry

- Registered `Structure Lineage Graph` as `STR-2026-0003`.
- Registered `Canonical Structure Registry` as `STR-2026-0002`.
- Connected the first three specification layers through related-structure references.

### Workflow

- Added graph-schema validation.
- Added graph-file validation.
- Added dedicated graph-validation step.
- Added required-file checks for graph resources.

### Documentation

- Added `docs/v0.3.md`.
- Added node-kind documentation.
- Added relationship-direction documentation.
- Added influence-boundary documentation.
- Added lineage-cycle policy.
- Added external-structure examples.
- Clarified that graph documents continue to use schema version `0.3.0` in later repository releases.

### Principles established

- Structures may be represented as lineage nodes.
- Relationships may be represented as auditable edges.
- Derivative direction must remain chronologically coherent.
- Similarity and influence are separate claims.
- Symmetric relationships must not be duplicated in reverse.
- Directed lineage must remain acyclic.
- External structures may be observed without canonical registration.

---

## [0.2.0] - 2026-07-18

### Added

- Canonical Structure Registry specification.
- Canonical Structure Registry JSON Schema.
- Stable canonical structure identifiers.
- Stable structure slugs.
- Canonical English names.
- Canonical Japanese names.
- Localized aliases.
- Originator bindings.
- Precedence-record bindings.
- Precedence-record URIs.
- First-publication timestamps.
- Structure-type classification.
- Domain classification.
- Discovery keywords.
- Related-structure references.
- Active lifecycle state.
- Deprecated lifecycle state.
- Superseded lifecycle state.
- Withdrawn lifecycle state.
- Supersession relationships.
- Optional royalty-route identifiers.
- Registry-level integrity metadata.
- Registry-level review metadata.
- Cross-entry semantic validation.
- Initial canonical registry.

### Semantic validation

- Detect duplicate canonical structure IDs.
- Detect duplicate slugs.
- Detect duplicate origin bindings.
- Detect canonical-name collisions.
- Detect alias collisions after Unicode normalization.
- Detect labels that normalize to empty values.
- Require canonical structure IDs to remain sorted.
- Reject unknown related-structure IDs.
- Reject related-structure self-references.
- Require reciprocal related-structure references.
- Reject unknown supersession targets.
- Reject supersession self-references.
- Require reciprocal supersession relationships.
- Require superseded structures to identify a successor.
- Reject `superseded_by` on structures not marked superseded.

### Documentation

- Added `docs/v0.2.md`.
- Added canonical-identifier format.
- Added canonical-name rules.
- Added alias rules.
- Added origin-binding rules.
- Added lifecycle documentation.
- Added supersession documentation.
- Clarified that one structure may have multiple names but one stable identity.
- Clarified that withdrawn IDs must not be silently reused.

### Principles established

- A structure may have many names but one stable identity.
- Canonical identity is separate from display naming.
- A canonical ID must remain stable across repository moves.
- A canonical ID must remain stable across translations.
- A withdrawn identifier must not be silently reused.
- Related structures do not automatically imply derivation.
- Supersession relationships must be reciprocal.
- Origin records should be verified before canonical registration.

---

## [0.1.0] - 2026-07-18

### Added

- Initial Structural Precedence Record specification.
- Structural Precedence Record JSON Schema.
- Stable ledger identifiers.
- Canonical English structure names.
- Canonical Japanese structure names.
- Structure aliases.
- Draft record status.
- Published record status.
- Superseded record status.
- Withdrawn record status.
- Stable originator identities.
- Originator display names.
- First-publication timestamps.
- Canonical structure URIs.
- Repository URIs.
- Canonical versions.
- Content digests.
- SHA-256 digest support.
- SHA-512 digest support.
- Core proposition summaries.
- Structural scope definitions.
- Falsifiable claims.
- Structural keywords.
- Timestamped precedence evidence.
- Git-commit evidence.
- Release evidence.
- Publication evidence.
- Archive-snapshot evidence.
- Book evidence.
- Signed-record evidence.
- Other evidence classification.
- Later convergence records.
- Convergence identifiers.
- Derivative names.
- Organization records.
- Later-publication timestamps.
- Source references.
- Direct influence classification.
- Probable influence classification.
- Independent convergence classification.
- Partial convergence classification.
- Conceptual analogy classification.
- Unrelated classification.
- Confidence levels.
- Convergence descriptions.
- Difference descriptions.
- Access evidence states.
- Citation evidence states.
- Direct-influence evidence states.
- Influence-audit notes.
- Prediction-reference field.
- Attribution and royalty-binding declaration.
- Attribution-only policy.
- Voluntary-contribution policy.
- License-bound policy.
- Royalty-route-pending policy.
- Custom policy.
- Integrity status.
- Review status.
- Reviewer records.
- Python validation script.
- GitHub Actions validation workflow.
- Initial YAML example.
- Initial normative documentation.
- MIT License.

### Documentation

- Added `docs/v0.1.md`.
- Added precedence-versus-influence distinction.
- Added convergence-difference requirement.
- Added stable-origin guidance.
- Added inspectable-evidence requirements.
- Added royalty-routing declaration.
- Added minimal record lifecycle.
- Added explicit non-goals.

### Principles established

- Precedence does not automatically demonstrate influence.
- Chronology may support precedence.
- Influence requires evidence.
- Structural convergence must document differences as well as similarities.
- Similar vocabulary alone is insufficient.
- Origin identity should remain stable after publication.
- Corrections should not silently erase history.
- Evidence should be externally inspectable.
- Royalty routing may be declared before automated settlement exists.
- The ledger does not replace copyright, patents, contracts, or citation systems.
