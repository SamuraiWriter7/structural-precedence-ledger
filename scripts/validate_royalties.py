#!/usr/bin/env python3
"""Validate v0.5 Royalty and Contribution Binding documents."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATH = (
    ROOT
    / "schemas"
    / "royalty-contribution-binding.schema.json"
)

REGISTRY_PATH = (
    ROOT
    / "registry"
    / "canonical-structures.yaml"
)

ROYALTIES_DIR = ROOT / "royalties"

MONETARY_STATUSES = {
    "simulated",
    "approved",
    "executed",
    "disputed",
}

WEIGHTED_MODES = {
    "fixed-share",
    "weighted-contribution",
}


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object."""

    with path.open("r", encoding="utf-8") as file:
        value = json.load(file)

    if not isinstance(value, dict):
        raise ValueError(
            f"JSON root must be an object: {path}"
        )

    return value


def load_yaml(path: Path) -> Any:
    """Load a YAML document."""

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def yaml_files(directory: Path) -> list[Path]:
    """Return YAML files from a directory."""

    if not directory.exists():
        return []

    return sorted(
        {
            *directory.glob("*.yaml"),
            *directory.glob("*.yml"),
        }
    )


def parse_time(value: str) -> datetime:
    """Parse an ISO 8601 datetime."""

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def duplicates(values: list[Any]) -> set[Any]:
    """Return duplicated values."""

    return {
        value
        for value, count in Counter(values).items()
        if count > 1
    }


def close(
    left: float,
    right: float,
) -> bool:
    """Compare shares or monetary amounts."""

    return math.isclose(
        left,
        right,
        rel_tol=1e-6,
        abs_tol=1e-6,
    )


def error_path(error: Any) -> str:
    """Format a JSON Schema error path."""

    if not error.absolute_path:
        return "<root>"

    return ".".join(
        str(part)
        for part in error.absolute_path
    )


def registry_index(
    document: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Build a canonical registry index."""

    entries = document.get("entries")

    if not isinstance(entries, list):
        raise ValueError(
            "Registry must contain an entries array."
        )

    result: dict[str, dict[str, Any]] = {}

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
                f"Registry entry {index} has no "
                "canonical_structure_id."
            )

        if structure_id in result:
            raise ValueError(
                f"Duplicate registry ID: {structure_id}"
            )

        result[structure_id] = entry

    return result


def validate_origin(
    document: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    """Compare origin binding with the registry."""

    structure_id = document[
        "canonical_structure_id"
    ]

    entry = registry.get(structure_id)

    if entry is None:
        errors.append(
            "unknown canonical_structure_id: "
            f"{structure_id}"
        )
        return

    actual = document["origin_binding"]

    expected = entry.get(
        "origin_binding",
        {},
    )

    checks = (
        (
            "originator_id",
            actual["originator_id"],
            expected.get("originator_id"),
        ),
        (
            "precedence_record_id",
            actual["precedence_record_id"],
            expected.get("precedence_record_id"),
        ),
        (
            "royalty_route_id",
            actual["royalty_route_id"],
            entry.get("royalty_route_id"),
        ),
    )

    for field, left, right in checks:
        if left != right:
            errors.append(
                f"{field} does not match registry: "
                f"binding={left!r}, registry={right!r}"
            )


def validate_participants_and_claims(
    document: dict[str, Any],
    errors: list[str],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    str | None,
    list[str],
]:
    """Validate participants and contribution claims."""

    participants = document["participants"]

    claims = document[
        "contribution_claims"
    ]

    policy = document["policy"]

    participant_ids = [
        item["participant_id"]
        for item in participants
    ]

    external_ids = [
        item["external_id"]
        for item in participants
        if "external_id" in item
    ]

    claim_ids = [
        item["claim_id"]
        for item in claims
    ]

    for label, values in (
        (
            "participant ID",
            participant_ids,
        ),
        (
            "participant external ID",
            external_ids,
        ),
        (
            "claim ID",
            claim_ids,
        ),
    ):
        for duplicate in sorted(
            duplicates(values)
        ):
            errors.append(
                f"duplicate {label}: {duplicate}"
            )

    participants_by_id = {
        item["participant_id"]: item
        for item in participants
    }

    claims_by_id = {
        item["claim_id"]: item
        for item in claims
    }

    originator_id = document[
        "origin_binding"
    ]["originator_id"]

    originators = [
        item
        for item in participants
        if (
            item["role"] == "originator"
            and item.get("external_id")
            == originator_id
        )
    ]

    origin_participant_id: str | None = None

    if len(originators) != 1:
        errors.append(
            "exactly one originator participant must "
            "match origin_binding.originator_id"
        )
    else:
        origin_participant_id = (
            originators[0]["participant_id"]
        )

    evidence_ids: list[str] = []

    for claim in claims:
        participant_id = claim[
            "participant_id"
        ]

        if participant_id not in participants_by_id:
            errors.append(
                f"{claim['claim_id']}: unknown "
                f"participant {participant_id}"
            )

        assessed_at = parse_time(
            claim["assessed_at"]
        )

        for evidence in claim["evidence"]:
            evidence_ids.append(
                evidence["evidence_id"]
            )

            if parse_time(
                evidence["recorded_at"]
            ) > assessed_at:
                errors.append(
                    f"{claim['claim_id']}: evidence "
                    f"{evidence['evidence_id']} was "
                    "recorded after assessment"
                )

    accepted = [
        item
        for item in claims
        if item["status"] == "accepted"
    ]

    accepted_weight = sum(
        item["weight"]
        for item in accepted
    )

    if (
        policy["mode"]
        in {
            "fixed-share",
            "weighted-contribution",
            "hybrid",
        }
        and accepted_weight <= 0
    ):
        errors.append(
            f"{policy['mode']} requires accepted "
            "positive contribution weight"
        )

    if (
        policy["mode"] == "fixed-share"
        and not close(
            accepted_weight,
            1.0,
        )
    ):
        errors.append(
            "fixed-share accepted weights "
            "must sum to 1.0"
        )

    if origin_participant_id is not None:
        has_origin_claim = any(
            item["participant_id"]
            == origin_participant_id
            and item["contribution_type"]
            == "origin"
            and item["status"] == "accepted"
            for item in claims
        )

        if not has_origin_claim:
            errors.append(
                "originator requires an "
                "accepted origin claim"
            )

    return (
        participants_by_id,
        claims_by_id,
        origin_participant_id,
        evidence_ids,
    )


def validate_receipts(
    document: dict[str, Any],
    claims_by_id: dict[str, dict[str, Any]],
    evidence_ids: list[str],
    errors: list[str],
) -> float:
    """Validate usage receipts."""

    policy = document["policy"]

    receipts = document[
        "usage_receipts"
    ]

    receipt_ids = [
        item["receipt_id"]
        for item in receipts
    ]

    for duplicate in sorted(
        duplicates(receipt_ids)
    ):
        errors.append(
            f"duplicate usage receipt ID: {duplicate}"
        )

    gross_total = 0.0

    for receipt in receipts:
        receipt_id = receipt["receipt_id"]

        for claim_id in receipt[
            "related_claim_ids"
        ]:
            if claim_id not in claims_by_id:
                errors.append(
                    f"{receipt_id}: unknown "
                    f"related claim {claim_id}"
                )

        for evidence in receipt["evidence"]:
            evidence_ids.append(
                evidence["evidence_id"]
            )

            if parse_time(
                evidence["recorded_at"]
            ) > parse_time(
                receipt["recorded_at"]
            ):
                errors.append(
                    f"{receipt_id}: evidence "
                    f"{evidence['evidence_id']} was "
                    "recorded after receipt creation"
                )

        if "gross_value" in receipt:
            gross_total += receipt[
                "gross_value"
            ]

            if "currency" not in receipt:
                errors.append(
                    f"{receipt_id}: gross_value "
                    "requires currency"
                )

            elif (
                policy.get("currency")
                and receipt["currency"]
                != policy["currency"]
            ):
                errors.append(
                    f"{receipt_id}: currency "
                    "does not match policy"
                )

    return gross_total


def validate_settlement(
    document: dict[str, Any],
    participants_by_id: dict[
        str,
        dict[str, Any],
    ],
    origin_participant_id: str | None,
    evidence_ids: list[str],
    receipt_gross: float,
    errors: list[str],
) -> None:
    """Validate settlement mathematics and routing."""

    policy = document["policy"]

    claims = document[
        "contribution_claims"
    ]

    settlement = document["settlement"]

    status = settlement["status"]

    for evidence in settlement["evidence"]:
        evidence_ids.append(
            evidence["evidence_id"]
        )

    if (
        policy["reserve_rate"] > 0
        and "reserve_route_uri" not in policy
    ):
        errors.append(
            "positive reserve_rate requires "
            "reserve_route_uri"
        )

    if policy["mode"] == "attribution-only":
        if (
            policy["gross_value_source"]
            != "none"
        ):
            errors.append(
                "attribution-only requires "
                "gross_value_source: none"
            )

        if status != "pending":
            errors.append(
                "attribution-only requires "
                "pending settlement"
            )

    if status == "pending":
        if settlement["allocations"]:
            errors.append(
                "pending settlement must not "
                "contain allocations"
            )

        forbidden_fields = (
            "settlement_id",
            "calculated_at",
            "currency",
            "gross_amount",
            "reserve_amount",
            "distributable_amount",
        )

        for field in forbidden_fields:
            if field in settlement:
                errors.append(
                    "pending settlement must not "
                    f"contain {field}"
                )

        return

    if status not in MONETARY_STATUSES:
        return

    required_fields = (
        "settlement_id",
        "calculated_at",
        "currency",
        "gross_amount",
        "reserve_amount",
        "distributable_amount",
    )

    missing = [
        field
        for field in required_fields
        if field not in settlement
    ]

    for field in missing:
        errors.append(
            f"{status} settlement requires {field}"
        )

    allocations = settlement[
        "allocations"
    ]

    if not allocations:
        errors.append(
            f"{status} settlement requires allocations"
        )

    if missing or not allocations:
        return

    if (
        policy.get("currency")
        and settlement["currency"]
        != policy["currency"]
    ):
        errors.append(
            "settlement currency does not "
            "match policy"
        )

    gross = settlement[
        "gross_amount"
    ]

    reserve = settlement[
        "reserve_amount"
    ]

    distributable = settlement[
        "distributable_amount"
    ]

    if not close(
        gross,
        reserve + distributable,
    ):
        errors.append(
            "gross_amount must equal reserve_amount "
            "plus distributable_amount"
        )

    if not close(
        reserve,
        gross * policy["reserve_rate"],
    ):
        errors.append(
            "reserve_amount does not match "
            "reserve_rate"
        )

    if (
        policy["gross_value_source"]
        == "usage-receipt"
        and not close(
            gross,
            receipt_gross,
        )
    ):
        errors.append(
            "gross_amount does not equal "
            "usage-receipt gross values"
        )

    allocation_ids = [
        item["participant_id"]
        for item in allocations
    ]

    for duplicate in sorted(
        duplicates(allocation_ids)
    ):
        errors.append(
            "duplicate settlement participant: "
            f"{duplicate}"
        )

    allocations_by_participant = {
        item["participant_id"]: item
        for item in allocations
    }

    for allocation in allocations:
        participant_id = allocation[
            "participant_id"
        ]

        participant = participants_by_id.get(
            participant_id
        )

        if participant is None:
            errors.append(
                "unknown settlement participant: "
                f"{participant_id}"
            )
            continue

        if not participant["active"]:
            errors.append(
                "inactive settlement participant: "
                f"{participant_id}"
            )

        if (
            status == "executed"
            and "route_uri" not in allocation
        ):
            errors.append(
                f"executed allocation for "
                f"{participant_id} requires route_uri"
            )

    total_share = sum(
        item["share"]
        for item in allocations
    )

    total_amount = sum(
        item["amount"]
        for item in allocations
    )

    if not close(total_share, 1.0):
        errors.append(
            "allocation shares must sum to 1.0"
        )

    if not close(
        total_amount,
        distributable,
    ):
        errors.append(
            "allocation amounts must sum "
            "to distributable_amount"
        )

    if origin_participant_id is not None:
        origin_allocation = (
            allocations_by_participant.get(
                origin_participant_id
            )
        )

        if origin_allocation is None:
            errors.append(
                "settlement must include "
                "the originator"
            )

        elif (
            origin_allocation["share"] + 1e-9
            < policy["origin_minimum_rate"]
        ):
            errors.append(
                "originator share is below "
                "origin_minimum_rate"
            )

    if policy["mode"] in WEIGHTED_MODES:
        weights: defaultdict[
            str,
            float,
        ] = defaultdict(float)

        for claim in claims:
            if claim["status"] == "accepted":
                weights[
                    claim["participant_id"]
                ] += claim["weight"]

        total_weight = sum(
            weights.values()
        )

        if total_weight > 0:
            for participant_id, weight in (
                weights.items()
            ):
                expected_share = (
                    weight / total_weight
                )

                allocation = (
                    allocations_by_participant.get(
                        participant_id
                    )
                )

                if allocation is None:
                    errors.append(
                        "weighted contributor "
                        f"{participant_id} "
                        "has no allocation"
                    )

                elif not close(
                    allocation["share"],
                    expected_share,
                ):
                    errors.append(
                        f"{participant_id}: share "
                        "does not match accepted weight"
                    )

            for participant_id, allocation in (
                allocations_by_participant.items()
            ):
                if (
                    participant_id not in weights
                    and allocation["share"] > 0
                ):
                    errors.append(
                        f"{participant_id}: allocation "
                        "has no accepted weight"
                    )


def semantic_errors(
    document: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> list[str]:
    """Apply v0.5 semantic rules."""

    errors: list[str] = []

    validate_origin(
        document,
        registry,
        errors,
    )

    scope = document["binding_scope"]

    if (
        isinstance(scope.get("from"), str)
        and isinstance(scope.get("to"), str)
        and parse_time(scope["to"])
        < parse_time(scope["from"])
    ):
        errors.append(
            "binding_scope.to must not predate "
            "binding_scope.from"
        )

    (
        participants_by_id,
        claims_by_id,
        origin_participant_id,
        evidence_ids,
    ) = validate_participants_and_claims(
        document,
        errors,
    )

    receipt_gross = validate_receipts(
        document,
        claims_by_id,
        evidence_ids,
        errors,
    )

    validate_settlement(
        document,
        participants_by_id,
        origin_participant_id,
        evidence_ids,
        receipt_gross,
        errors,
    )

    for duplicate in sorted(
        duplicates(evidence_ids)
    ):
        errors.append(
            "duplicate royalty evidence ID: "
            f"{duplicate}"
        )

    audit = document["audit"]

    if parse_time(
        audit["updated_at"]
    ) < parse_time(
        audit["created_at"]
    ):
        errors.append(
            "audit.updated_at must not "
            "predate audit.created_at"
        )

    return errors


def validate_document(
    path: Path,
    schema: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> tuple[
    bool,
    dict[str, Any] | None,
]:
    """Validate one royalty binding."""

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
                f"{error_path(error)}: "
                f"{error.message}"
            )

        return False, document

    print("[schema-ok]")

    errors = semantic_errors(
        document,
        registry,
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
    """Validate all royalty binding files."""

    print(
        "=== Royalty and Contribution "
        "Binding Validation ==="
    )

    for path in (
        SCHEMA_PATH,
        REGISTRY_PATH,
    ):
        if not path.exists():
            print(
                "[fatal] Missing required file: "
                f"{path.relative_to(ROOT)}"
            )
            return 2

    royalty_paths = yaml_files(
        ROYALTIES_DIR
    )

    if not royalty_paths:
        print(
            "[fatal] No royalty YAML files "
            "found in: "
            f"{ROYALTIES_DIR.relative_to(ROOT)}"
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

        registry = registry_index(
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

    for path in royalty_paths:
        valid, document = validate_document(
            path,
            schema,
            registry,
        )

        if document is not None:
            documents.append(document)

        if not valid:
            failed = True

    binding_ids = [
        item["binding_id"]
        for item in documents
        if isinstance(
            item.get("binding_id"),
            str,
        )
    ]

    settlement_ids = [
        item[
            "settlement"
        ]["settlement_id"]
        for item in documents
        if (
            isinstance(
                item.get("settlement"),
                dict,
            )
            and isinstance(
                item[
                    "settlement"
                ].get("settlement_id"),
                str,
            )
        )
    ]

    for label, values in (
        (
            "binding ID",
            binding_ids,
        ),
        (
            "settlement ID",
            settlement_ids,
        ),
    ):
        for duplicate in sorted(
            duplicates(values)
        ):
            print(
                "[semantic-error] "
                f"duplicate {label}: {duplicate}"
            )

            failed = True

    if failed:
        print("\nValidation failed.")
        return 1

    print(
        "\nAll royalty bindings are valid. "
        f"Validated: {len(royalty_paths)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
