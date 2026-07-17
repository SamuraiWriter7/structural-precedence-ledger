#!/usr/bin/env python3
"""Validate v0.4 Prediction and Outcome Audit documents."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATH = (
    ROOT
    / "schemas"
    / "prediction-outcome-audit.schema.json"
)

REGISTRY_PATH = (
    ROOT
    / "registry"
    / "canonical-structures.yaml"
)

PREDICTIONS_DIR = ROOT / "predictions"


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object."""

    with path.open("r", encoding="utf-8") as file:
        document = json.load(file)

    if not isinstance(document, dict):
        raise ValueError(
            f"JSON root must be an object: {path}"
        )

    return document


def load_yaml(path: Path) -> Any:
    """Load a YAML document."""

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def find_yaml_files(directory: Path) -> list[Path]:
    """Return sorted YAML files from a directory."""

    if not directory.exists():
        return []

    return sorted(
        {
            *directory.glob("*.yaml"),
            *directory.glob("*.yml"),
        }
    )


def parse_datetime(value: str) -> datetime:
    """Parse an ISO 8601 datetime."""

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def duplicates(values: list[Any]) -> set[Any]:
    """Return values appearing more than once."""

    return {
        value
        for value, count in Counter(values).items()
        if count > 1
    }


def format_schema_path(error: Any) -> str:
    """Format a JSON Schema error path."""

    if not error.absolute_path:
        return "<root>"

    return ".".join(
        str(part)
        for part in error.absolute_path
    )


def build_registry_ids(
    registry_document: dict[str, Any],
) -> set[str]:
    """Return canonical structure IDs from the registry."""

    entries = registry_document.get("entries")

    if not isinstance(entries, list):
        raise ValueError(
            "Registry document must contain an entries array."
        )

    structure_ids: list[str] = []

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(
                f"Registry entry {index} must be an object."
            )

        structure_id = entry.get(
            "canonical_structure_id"
        )

        if not isinstance(structure_id, str):
            raise ValueError(
                f"Registry entry {index} has no valid "
                "canonical_structure_id."
            )

        structure_ids.append(structure_id)

    duplicate_ids = duplicates(structure_ids)

    if duplicate_ids:
        raise ValueError(
            "Duplicate canonical structure IDs in registry: "
            + ", ".join(sorted(duplicate_ids))
        )

    return set(structure_ids)


def confidence_error(
    level: str,
    probability: float,
) -> str | None:
    """Check probability range against confidence level."""

    if level == "low" and probability > 0.39:
        return (
            "low confidence requires probability <= 0.39"
        )

    if (
        level == "medium"
        and not 0.40 <= probability <= 0.69
    ):
        return (
            "medium confidence requires probability "
            "between 0.40 and 0.69"
        )

    if level == "high" and probability < 0.70:
        return (
            "high confidence requires probability >= 0.70"
        )

    return None


def semantic_errors(
    document: dict[str, Any],
    registry_ids: set[str],
) -> list[str]:
    """Apply v0.4 cross-field semantic rules."""

    errors: list[str] = []

    structure_id = document[
        "canonical_structure_id"
    ]

    if structure_id not in registry_ids:
        errors.append(
            "unknown canonical_structure_id: "
            f"{structure_id}"
        )

    prediction = document["prediction"]
    outcomes = document["outcomes"]
    evaluation = document["evaluation"]

    success_criteria = prediction[
        "success_criteria"
    ]

    failure_criteria = prediction[
        "failure_criteria"
    ]

    indicators = prediction[
        "observable_indicators"
    ]

    evidence = prediction[
        "precedence_evidence"
    ]

    success_ids = [
        criterion["criterion_id"]
        for criterion in success_criteria
    ]

    failure_ids = [
        criterion["criterion_id"]
        for criterion in failure_criteria
    ]

    outcome_ids = [
        outcome["outcome_id"]
        for outcome in outcomes
    ]

    evidence_ids = [
        item["evidence_id"]
        for item in evidence
    ]

    outcome_uris = [
        outcome["source_uri"]
        for outcome in outcomes
    ]

    for label, values in (
        (
            "success criterion ID",
            success_ids,
        ),
        (
            "failure criterion ID",
            failure_ids,
        ),
        (
            "outcome ID",
            outcome_ids,
        ),
        (
            "prediction evidence ID",
            evidence_ids,
        ),
        (
            "outcome source URI",
            outcome_uris,
        ),
    ):
        for duplicate in sorted(
            duplicates(values)
        ):
            errors.append(
                f"duplicate {label}: {duplicate}"
            )

    issued_at = parse_datetime(
        prediction["issued_at"]
    )

    window_from = parse_datetime(
        prediction[
            "expected_window"
        ]["from"]
    )

    window_to = parse_datetime(
        prediction[
            "expected_window"
        ]["to"]
    )

    if window_from < issued_at:
        errors.append(
            "expected_window.from must not "
            "predate issued_at"
        )

    if window_to < window_from:
        errors.append(
            "expected_window.to must not predate "
            "expected_window.from"
        )

    for item in evidence:
        recorded_at = parse_datetime(
            item["recorded_at"]
        )

        if recorded_at > issued_at:
            errors.append(
                f"{item['evidence_id']}: "
                "precedence evidence was recorded "
                "after the prediction was issued"
            )

    for outcome in outcomes:
        observed_at = parse_datetime(
            outcome["observed_at"]
        )

        if observed_at < issued_at:
            errors.append(
                f"{outcome['outcome_id']}: "
                "outcome predates prediction issuance"
            )

        for index in outcome.get(
            "matched_indicator_indexes",
            [],
        ):
            if index >= len(indicators):
                errors.append(
                    f"{outcome['outcome_id']}: "
                    f"indicator index {index} "
                    "is out of range"
                )

    confidence = prediction["confidence"]

    confidence_message = confidence_error(
        confidence["level"],
        confidence["probability"],
    )

    if confidence_message:
        errors.append(confidence_message)

    valid_success_ids = set(success_ids)
    valid_failure_ids = set(failure_ids)

    matched_success = evaluation[
        "matched_success_criteria"
    ]

    matched_failure = evaluation[
        "matched_failure_criteria"
    ]

    for criterion_id in matched_success:
        if criterion_id not in valid_success_ids:
            errors.append(
                "evaluation references unknown "
                "success criterion: "
                f"{criterion_id}"
            )

    for criterion_id in matched_failure:
        if criterion_id not in valid_failure_ids:
            errors.append(
                "evaluation references unknown "
                "failure criterion: "
                f"{criterion_id}"
            )

    status = prediction["status"]
    result = evaluation["result"]

    evaluated_at_value = evaluation.get(
        "evaluated_at"
    )

    evaluator_id = evaluation.get(
        "evaluator_id"
    )

    alignment_score = evaluation.get(
        "alignment_score"
    )

    if status == "open":
        if result != "pending":
            errors.append(
                "open prediction requires "
                "pending evaluation"
            )

    elif status == "closed":
        if result in {
            "pending",
            "withdrawn",
        }:
            errors.append(
                "closed prediction requires a "
                "completed non-withdrawn evaluation"
            )

    elif status == "withdrawn":
        if result != "withdrawn":
            errors.append(
                "withdrawn prediction requires "
                "withdrawn result"
            )

        if not prediction.get(
            "withdrawal_reason"
        ):
            errors.append(
                "withdrawn prediction requires "
                "withdrawal_reason"
            )

    if result == "pending":
        if any(
            value is not None
            for value in (
                evaluated_at_value,
                evaluator_id,
                alignment_score,
            )
        ):
            errors.append(
                "pending evaluation must not include "
                "evaluated_at, evaluator_id, "
                "or alignment_score"
            )

        if matched_success or matched_failure:
            errors.append(
                "pending evaluation must not "
                "match criteria"
            )

    else:
        if not isinstance(
            evaluated_at_value,
            str,
        ):
            errors.append(
                "completed evaluation requires "
                "evaluated_at"
            )

        if not isinstance(
            evaluator_id,
            str,
        ):
            errors.append(
                "completed evaluation requires "
                "evaluator_id"
            )

        if not isinstance(
            alignment_score,
            (int, float),
        ):
            errors.append(
                "completed evaluation requires "
                "alignment_score"
            )

        if isinstance(
            evaluated_at_value,
            str,
        ):
            evaluated_at = parse_datetime(
                evaluated_at_value
            )

            if evaluated_at < issued_at:
                errors.append(
                    "evaluation predates "
                    "prediction issuance"
                )

            for outcome in outcomes:
                outcome_time = parse_datetime(
                    outcome["observed_at"]
                )

                if evaluated_at < outcome_time:
                    errors.append(
                        "evaluation predates outcome "
                        f"{outcome['outcome_id']}"
                    )

    if result == "confirmed":
        if (
            set(matched_success)
            != valid_success_ids
        ):
            errors.append(
                "confirmed result must match "
                "all success criteria"
            )

        if matched_failure:
            errors.append(
                "confirmed result must not "
                "match failure criteria"
            )

    elif result == "partially_confirmed":
        if not matched_success:
            errors.append(
                "partially_confirmed result "
                "requires at least one matched "
                "success criterion"
            )

        if (
            set(matched_success)
            == valid_success_ids
            and not matched_failure
        ):
            errors.append(
                "all success criteria with no "
                "failures should use confirmed"
            )

    elif result == "not_confirmed":
        if (
            not matched_failure
            and matched_success
        ):
            errors.append(
                "not_confirmed result requires "
                "at least one matched failure "
                "criterion when success criteria "
                "were matched"
            )

    elif result == "withdrawn":
        if status != "withdrawn":
            errors.append(
                "withdrawn result requires "
                "withdrawn prediction status"
            )

    return errors


def validate_document(
    path: Path,
    schema: dict[str, Any],
    registry_ids: set[str],
) -> tuple[
    bool,
    dict[str, Any] | None,
]:
    """Validate one prediction audit document."""

    print(
        "\n[validate] "
        f"{path.relative_to(ROOT)}"
    )

    try:
        document = load_yaml(path)

    except (
        OSError,
        yaml.YAMLError,
    ) as error:
        print(
            f"[parse-error] {error}"
        )
        return False, None

    if not isinstance(document, dict):
        print(
            "[parse-error] "
            "YAML root must be a mapping."
        )
        return False, None

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    schema_errors = sorted(
        validator.iter_errors(document),
        key=lambda error: list(
            error.absolute_path
        ),
    )

    if schema_errors:
        for error in schema_errors:
            print(
                "[schema-error] "
                f"{format_schema_path(error)}: "
                f"{error.message}"
            )

        return False, document

    print("[schema-ok]")

    errors = semantic_errors(
        document,
        registry_ids,
    )

    if errors:
        for error in errors:
            print(
                f"[semantic-error] {error}"
            )

        return False, document

    print("[semantic-ok]")

    return True, document


def main() -> int:
    """Validate all v0.4 prediction audits."""

    print(
        "=== Prediction and Outcome "
        "Audit Validation ==="
    )

    for required_path in (
        SCHEMA_PATH,
        REGISTRY_PATH,
    ):
        if not required_path.exists():
            print(
                "[fatal] Missing required file: "
                f"{required_path.relative_to(ROOT)}"
            )

            return 2

    prediction_paths = find_yaml_files(
        PREDICTIONS_DIR
    )

    if not prediction_paths:
        print(
            "[fatal] No prediction YAML files "
            "found in: "
            f"{PREDICTIONS_DIR.relative_to(ROOT)}"
        )

        return 2

    try:
        schema = load_json(
            SCHEMA_PATH
        )

        registry_document = load_yaml(
            REGISTRY_PATH
        )

        if not isinstance(
            registry_document,
            dict,
        ):
            raise ValueError(
                "Registry root must be "
                "a YAML mapping."
            )

        registry_ids = build_registry_ids(
            registry_document
        )

    except (
        OSError,
        json.JSONDecodeError,
        yaml.YAMLError,
        ValueError,
    ) as error:
        print(
            f"[fatal] {error}"
        )

        return 2

    failed = False

    documents: list[
        dict[str, Any]
    ] = []

    for path in prediction_paths:
        valid, document = validate_document(
            path,
            schema,
            registry_ids,
        )

        if document is not None:
            documents.append(document)

        if not valid:
            failed = True

    audit_ids = [
        document["audit_id"]
        for document in documents
        if isinstance(
            document.get("audit_id"),
            str,
        )
    ]

    prediction_ids = [
        document[
            "prediction"
        ]["prediction_id"]
        for document in documents
        if (
            isinstance(
                document.get("prediction"),
                dict,
            )
            and isinstance(
                document[
                    "prediction"
                ].get("prediction_id"),
                str,
            )
        )
    ]

    for label, values in (
        (
            "audit ID",
            audit_ids,
        ),
        (
            "prediction ID",
            prediction_ids,
        ),
    ):
        for duplicate in sorted(
            duplicates(values)
        ):
            print(
                "[semantic-error] "
                f"duplicate {label}: "
                f"{duplicate}"
            )

            failed = True

    if failed:
        print("\nValidation failed.")
        return 1

    print(
        "\nAll prediction audits are valid. "
        f"Validated: {len(prediction_paths)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
