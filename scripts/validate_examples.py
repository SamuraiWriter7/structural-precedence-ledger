#!/usr/bin/env python3
"""Validate Structural Precedence Ledger records and registry.

Validation layers:

1. Structural Precedence Record JSON Schema validation.
2. Canonical Structure Registry JSON Schema validation.
3. Cross-entry semantic validation for the registry.
"""

from __future__ import annotations

import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

PRECEDENCE_SCHEMA_PATH = (
    ROOT
    / "schemas"
    / "structural-precedence-record.schema.json"
)

REGISTRY_SCHEMA_PATH = (
    ROOT
    / "schemas"
    / "canonical-structure-registry.schema.json"
)

EXAMPLES_DIR = ROOT / "examples"

REGISTRY_PATH = (
    ROOT
    / "registry"
    / "canonical-structures.yaml"
)


def load_json(path: Path) -> dict[str, Any]:
    """Load and return a JSON object."""

    with path.open("r", encoding="utf-8") as file:
        document = json.load(file)

    if not isinstance(document, dict):
        raise ValueError(
            f"JSON root must be an object: {path}"
        )

    return document


def load_yaml(path: Path) -> Any:
    """Load and return a YAML document."""

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def find_yaml_files(directory: Path) -> list[Path]:
    """Return sorted YAML files from one directory."""

    if not directory.exists():
        return []

    return sorted(
        {
            *directory.glob("*.yaml"),
            *directory.glob("*.yml"),
        }
    )


def format_schema_error_path(error: Any) -> str:
    """Format a JSON Schema error path using dot notation."""

    if not error.absolute_path:
        return "<root>"

    return ".".join(
        str(part)
        for part in error.absolute_path
    )


def normalize_label(value: str) -> str:
    """Normalize structure names and aliases for comparison.

    Unicode compatibility normalization, case folding, and removal
    of punctuation and whitespace are applied.

    Examples treated as equivalent:

    - "Canonical Registry"
    - "canonical-registry"
    - "Ｃａｎｏｎｉｃａｌ Ｒｅｇｉｓｔｒｙ"
    """

    normalized = unicodedata.normalize(
        "NFKC",
        value,
    ).casefold()

    return "".join(
        character
        for character in normalized
        if character.isalnum()
    )


def duplicate_values(
    values: list[Any],
) -> set[Any]:
    """Return values appearing more than once."""

    return {
        value
        for value, count in Counter(values).items()
        if count > 1
    }


def validate_schema_document(
    document_path: Path,
    schema_path: Path,
) -> tuple[bool, Any | None]:
    """Validate one YAML document against a JSON Schema."""

    print(
        "\n[validate] "
        f"{document_path.relative_to(ROOT)}"
    )

    try:
        schema = load_json(schema_path)
        document = load_yaml(document_path)

    except (
        OSError,
        json.JSONDecodeError,
        yaml.YAMLError,
        ValueError,
    ) as error:
        print(f"[parse-error] {error}")
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

    errors = sorted(
        validator.iter_errors(document),
        key=lambda item: list(item.absolute_path),
    )

    if errors:
        for error in errors:
            print(
                "[schema-error] "
                f"{format_schema_error_path(error)}: "
                f"{error.message}"
            )

        return False, document

    print("[schema-ok]")
    return True, document


def validate_unique_registry_values(
    entries: list[dict[str, Any]],
    errors: list[str],
) -> None:
    """Validate IDs, slugs, and origin bindings for uniqueness."""

    structure_ids = [
        entry["canonical_structure_id"]
        for entry in entries
    ]

    slugs = [
        entry["slug"]
        for entry in entries
    ]

    origin_bindings = [
        (
            entry["origin_binding"]["originator_id"],
            entry["origin_binding"]["precedence_record_id"],
        )
        for entry in entries
    ]

    for duplicate in sorted(
        duplicate_values(structure_ids)
    ):
        errors.append(
            "duplicate canonical_structure_id: "
            f"{duplicate}"
        )

    for duplicate in sorted(
        duplicate_values(slugs)
    ):
        errors.append(
            f"duplicate slug: {duplicate}"
        )

    for originator_id, record_id in sorted(
        duplicate_values(origin_bindings)
    ):
        errors.append(
            "duplicate origin binding: "
            f"{originator_id} + {record_id}"
        )

    if structure_ids != sorted(structure_ids):
        errors.append(
            "canonical_structure_id values "
            "must be sorted in ascending order"
        )


def validate_registry_labels(
    entries: list[dict[str, Any]],
    errors: list[str],
) -> None:
    """Detect canonical-name and alias collisions."""

    global_label_owner: dict[str, str] = {}

    for entry in entries:
        structure_id = entry["canonical_structure_id"]
        canonical_name = entry["canonical_name"]

        labels: list[tuple[str, str]] = []

        english_name = canonical_name.get("en")

        if isinstance(english_name, str):
            labels.append(
                ("canonical_name.en", english_name)
            )

        japanese_name = canonical_name.get("ja")

        if isinstance(japanese_name, str):
            labels.append(
                ("canonical_name.ja", japanese_name)
            )

        aliases = canonical_name.get(
            "aliases",
            [],
        )

        for alias_index, alias in enumerate(aliases):
            if not isinstance(alias, dict):
                continue

            alias_value = alias.get("value")

            if isinstance(alias_value, str):
                labels.append(
                    (
                        f"aliases.{alias_index}",
                        alias_value,
                    )
                )

        local_labels: dict[str, str] = {}

        for label_path, label_value in labels:
            normalized = normalize_label(
                label_value
            )

            if not normalized:
                errors.append(
                    f"{structure_id}: "
                    f"{label_path} becomes empty "
                    "after normalization"
                )
                continue

            previous_local = local_labels.get(
                normalized
            )

            if previous_local is not None:
                errors.append(
                    f"{structure_id}: "
                    f"label {label_value!r} duplicates "
                    f"local label {previous_local!r}"
                )
                continue

            local_labels[normalized] = label_value

            previous_owner = global_label_owner.get(
                normalized
            )

            if (
                previous_owner is not None
                and previous_owner != structure_id
            ):
                errors.append(
                    f"{structure_id}: "
                    f"label {label_value!r} collides "
                    f"with structure {previous_owner}"
                )
            else:
                global_label_owner[normalized] = (
                    structure_id
                )


def validate_registry_references(
    entries: list[dict[str, Any]],
    errors: list[str],
) -> None:
    """Validate related and supersession references."""

    entry_by_id = {
        entry["canonical_structure_id"]: entry
        for entry in entries
    }

    known_ids = set(entry_by_id)

    for entry in entries:
        structure_id = entry[
            "canonical_structure_id"
        ]

        discovery = entry.get(
            "discovery",
            {},
        )

        related_structures = discovery.get(
            "related_structures",
            [],
        )

        for related_id in related_structures:
            if related_id == structure_id:
                errors.append(
                    f"{structure_id}: "
                    "related_structures must not "
                    "contain itself"
                )

            elif related_id not in known_ids:
                errors.append(
                    f"{structure_id}: unknown "
                    "related structure "
                    f"{related_id}"
                )

        lifecycle = entry.get(
            "lifecycle",
            {},
        )

        status = lifecycle.get("status")

        supersedes = lifecycle.get(
            "supersedes",
            [],
        )

        superseded_by = lifecycle.get(
            "superseded_by",
            [],
        )

        if (
            status == "superseded"
            and not superseded_by
        ):
            errors.append(
                f"{structure_id}: "
                "superseded status requires "
                "at least one superseded_by entry"
            )

        if (
            status != "superseded"
            and superseded_by
        ):
            errors.append(
                f"{structure_id}: "
                "superseded_by is present, but "
                f"lifecycle status is {status!r}"
            )

        for target_id in supersedes:
            if target_id == structure_id:
                errors.append(
                    f"{structure_id}: "
                    "supersedes must not "
                    "reference itself"
                )
                continue

            if target_id not in known_ids:
                errors.append(
                    f"{structure_id}: unknown "
                    "supersedes target "
                    f"{target_id}"
                )
                continue

            target_lifecycle = (
                entry_by_id[target_id]
                .get("lifecycle", {})
            )

            reverse_links = (
                target_lifecycle
                .get("superseded_by", [])
            )

            if structure_id not in reverse_links:
                errors.append(
                    f"{structure_id}: "
                    f"{target_id} does not contain "
                    f"{structure_id} in superseded_by"
                )

        for target_id in superseded_by:
            if target_id == structure_id:
                errors.append(
                    f"{structure_id}: "
                    "superseded_by must not "
                    "reference itself"
                )
                continue

            if target_id not in known_ids:
                errors.append(
                    f"{structure_id}: unknown "
                    "superseded_by target "
                    f"{target_id}"
                )
                continue

            target_lifecycle = (
                entry_by_id[target_id]
                .get("lifecycle", {})
            )

            reverse_links = (
                target_lifecycle
                .get("supersedes", [])
            )

            if structure_id not in reverse_links:
                errors.append(
                    f"{structure_id}: "
                    f"{target_id} does not contain "
                    f"{structure_id} in supersedes"
                )


def validate_related_structure_symmetry(
    entries: list[dict[str, Any]],
    errors: list[str],
) -> None:
    """Require related-structure references to be reciprocal.

    This rule keeps the canonical registry internally navigable.

    If A lists B as related, B must also list A as related.
    """

    entry_by_id = {
        entry["canonical_structure_id"]: entry
        for entry in entries
    }

    for structure_id, entry in entry_by_id.items():
        related_structures = (
            entry
            .get("discovery", {})
            .get("related_structures", [])
        )

        for related_id in related_structures:
            related_entry = entry_by_id.get(
                related_id
            )

            if related_entry is None:
                continue

            reverse_related = (
                related_entry
                .get("discovery", {})
                .get("related_structures", [])
            )

            if structure_id not in reverse_related:
                errors.append(
                    f"{structure_id}: related structure "
                    f"{related_id} does not contain "
                    f"reciprocal reference {structure_id}"
                )


def registry_semantic_errors(
    registry_document: dict[str, Any],
) -> list[str]:
    """Return registry semantic validation errors."""

    errors: list[str] = []

    entries_value = registry_document.get(
        "entries"
    )

    if not isinstance(entries_value, list):
        return [
            "registry entries must be an array"
        ]

    entries: list[dict[str, Any]] = []

    for index, entry in enumerate(entries_value):
        if not isinstance(entry, dict):
            errors.append(
                f"entries.{index}: "
                "registry entry must be an object"
            )
            continue

        entries.append(entry)

    if errors:
        return errors

    validate_unique_registry_values(
        entries,
        errors,
    )

    validate_registry_labels(
        entries,
        errors,
    )

    validate_registry_references(
        entries,
        errors,
    )

    validate_related_structure_symmetry(
        entries,
        errors,
    )

    return errors


def validate_precedence_records() -> bool:
    """Validate all v0.1 precedence record examples."""

    print(
        "\n[target] structural-precedence-record"
    )

    print(
        "schema : "
        f"{PRECEDENCE_SCHEMA_PATH.relative_to(ROOT)}"
    )

    if not PRECEDENCE_SCHEMA_PATH.exists():
        print(
            "[fatal] Missing schema: "
            f"{PRECEDENCE_SCHEMA_PATH.relative_to(ROOT)}"
        )
        return False

    example_paths = find_yaml_files(
        EXAMPLES_DIR
    )

    if not example_paths:
        print(
            "[fatal] No YAML examples found in: "
            f"{EXAMPLES_DIR.relative_to(ROOT)}"
        )
        return False

    valid = True

    for example_path in example_paths:
        schema_valid, _ = validate_schema_document(
            example_path,
            PRECEDENCE_SCHEMA_PATH,
        )

        if not schema_valid:
            valid = False
            continue

        print("[semantic-ok]")

    return valid


def validate_canonical_registry() -> bool:
    """Validate the v0.2 canonical registry."""

    print(
        "\n[target] canonical-structure-registry"
    )

    print(
        "schema : "
        f"{REGISTRY_SCHEMA_PATH.relative_to(ROOT)}"
    )

    if not REGISTRY_SCHEMA_PATH.exists():
        print(
            "[fatal] Missing schema: "
            f"{REGISTRY_SCHEMA_PATH.relative_to(ROOT)}"
        )
        return False

    if not REGISTRY_PATH.exists():
        print(
            "[fatal] Missing registry: "
            f"{REGISTRY_PATH.relative_to(ROOT)}"
        )
        return False

    schema_valid, registry_document = (
        validate_schema_document(
            REGISTRY_PATH,
            REGISTRY_SCHEMA_PATH,
        )
    )

    if not schema_valid:
        return False

    if not isinstance(registry_document, dict):
        return False

    semantic_errors = registry_semantic_errors(
        registry_document
    )

    if semantic_errors:
        for error in semantic_errors:
            print(
                f"[semantic-error] {error}"
            )

        return False

    print("[semantic-ok]")
    return True


def main() -> int:
    """Validate precedence records and the canonical registry."""

    print(
        "=== Structural Precedence Ledger Validation ==="
    )

    precedence_valid = validate_precedence_records()
    registry_valid = validate_canonical_registry()

    if not precedence_valid or not registry_valid:
        print("\nValidation failed.")
        return 1

    validated_example_count = len(
        find_yaml_files(EXAMPLES_DIR)
    )

    print(
        "\nAll documents are valid. "
        f"Validated: {validated_example_count + 1}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
