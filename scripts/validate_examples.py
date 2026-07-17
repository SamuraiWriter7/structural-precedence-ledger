#!/usr/bin/env python3
"""Validate SPL records and the v0.2 canonical registry."""

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

TARGETS = (
    (
        "structural-precedence-record",
        ROOT
        / "schemas"
        / "structural-precedence-record.schema.json",
        ROOT / "examples",
    ),
    (
        "canonical-structure-registry",
        ROOT
        / "schemas"
        / "canonical-structure-registry.schema.json",
        ROOT / "registry",
    ),
)


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON document."""

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_yaml(path: Path) -> Any:
    """Load a YAML document."""

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def yaml_files(directory: Path) -> list[Path]:
    """Return all YAML files in one directory."""

    return sorted(
        set(directory.glob("*.yaml"))
        | set(directory.glob("*.yml"))
    )


def format_path(error: Any) -> str:
    """Format a JSON Schema error path."""

    if not error.absolute_path:
        return "<root>"

    return ".".join(
        str(part)
        for part in error.absolute_path
    )


def normalize_label(value: str) -> str:
    """Normalize canonical names and aliases."""

    value = unicodedata.normalize(
        "NFKC",
        value,
    ).casefold()

    return "".join(
        character
        for character in value
        if character.isalnum()
    )


def duplicate_values(
    values: list[Any],
) -> set[Any]:
    """Return values that appear more than once."""

    return {
        value
        for value, count in Counter(values).items()
        if count > 1
    }


def registry_semantic_errors(
    registry: dict[str, Any],
) -> list[str]:
    """Apply rules that JSON Schema cannot express."""

    errors: list[str] = []
    entries = registry.get("entries", [])

    if not isinstance(entries, list):
        return errors

    valid_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
    ]

    ids = [
        entry["canonical_structure_id"]
        for entry in valid_entries
        if isinstance(
            entry.get("canonical_structure_id"),
            str,
        )
    ]

    slugs = [
        entry["slug"]
        for entry in valid_entries
        if isinstance(
            entry.get("slug"),
            str,
        )
    ]

    bindings = [
        (
            entry
            .get("origin_binding", {})
            .get("originator_id"),

            entry
            .get("origin_binding", {})
            .get("precedence_record_id"),
        )
        for entry in valid_entries
        if isinstance(
            entry.get("origin_binding"),
            dict,
        )
    ]

    bindings = [
        binding
        for binding in bindings
        if all(
            isinstance(value, str)
            for value in binding
        )
    ]

    for duplicate in sorted(
        duplicate_values(ids)
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

    for duplicate in sorted(
        duplicate_values(bindings)
    ):
        errors.append(
            "duplicate origin binding: "
            f"{duplicate[0]} + {duplicate[1]}"
        )

    if ids != sorted(ids):
        errors.append(
            "canonical_structure_id values "
            "must be sorted"
        )

    known_ids = set(ids)

    entry_by_id = {
        entry["canonical_structure_id"]: entry
        for entry in valid_entries
        if isinstance(
            entry.get("canonical_structure_id"),
            str,
        )
    }

    label_owner: dict[str, str] = {}

    for entry in valid_entries:
        structure_id = entry.get(
            "canonical_structure_id"
        )

        names = entry.get(
            "canonical_name",
            {},
        )

        if (
            not isinstance(structure_id, str)
            or not isinstance(names, dict)
        ):
            continue

        labels: list[str] = []

        for language in ("en", "ja"):
            value = names.get(language)

            if isinstance(value, str):
                labels.append(value)

        aliases = names.get(
            "aliases",
            [],
        )

        if isinstance(aliases, list):
            labels.extend(
                alias["value"]
                for alias in aliases
                if (
                    isinstance(alias, dict)
                    and isinstance(
                        alias.get("value"),
                        str,
                    )
                )
            )

        local_seen: set[str] = set()

        for label in labels:
            normalized = normalize_label(label)

            if not normalized:
                errors.append(
                    f"{structure_id}: "
                    "empty normalized label"
                )
                continue

            if normalized in local_seen:
                errors.append(
                    f"{structure_id}: "
                    "duplicate local label "
                    f"{label!r}"
                )
                continue

            local_seen.add(normalized)

            previous = label_owner.get(
                normalized
            )

            if previous is not None:
                errors.append(
                    f"{structure_id}: "
                    f"label {label!r} "
                    f"collides with {previous}"
                )
            else:
                label_owner[normalized] = (
                    structure_id
                )

    for entry in valid_entries:
        structure_id = entry.get(
            "canonical_structure_id"
        )

        if not isinstance(structure_id, str):
            continue

        discovery = entry.get(
            "discovery",
            {},
        )

        related = (
            discovery.get(
                "related_structures",
                [],
            )
            if isinstance(discovery, dict)
            else []
        )

        for target in related:
            if target == structure_id:
                errors.append(
                    f"{structure_id}: "
                    "related self-reference"
                )

            elif target not in known_ids:
                errors.append(
                    f"{structure_id}: "
                    "unknown related target "
                    f"{target}"
                )

        lifecycle = entry.get(
            "lifecycle",
            {},
        )

        if not isinstance(lifecycle, dict):
            continue

        supersedes = lifecycle.get(
            "supersedes",
            [],
        )

        superseded_by = lifecycle.get(
            "superseded_by",
            [],
        )

        for relation_name, targets in (
            ("supersedes", supersedes),
            ("superseded_by", superseded_by),
        ):
            for target in targets:
                if target == structure_id:
                    errors.append(
                        f"{structure_id}: "
                        f"{relation_name} "
                        "self-reference"
                    )

                elif target not in known_ids:
                    errors.append(
                        f"{structure_id}: "
                        f"unknown {relation_name} "
                        f"target {target}"
                    )

        if (
            lifecycle.get("status")
            == "superseded"
            and not superseded_by
        ):
            errors.append(
                f"{structure_id}: "
                "superseded status requires "
                "superseded_by"
            )

        for target in supersedes:
            reverse = (
                entry_by_id
                .get(target, {})
                .get("lifecycle", {})
                .get("superseded_by", [])
            )

            if structure_id not in reverse:
                errors.append(
                    f"{structure_id}: "
                    f"{target} lacks reciprocal "
                    "superseded_by"
                )

        for target in superseded_by:
            reverse = (
                entry_by_id
                .get(target, {})
                .get("lifecycle", {})
                .get("supersedes", [])
            )

            if structure_id not in reverse:
                errors.append(
                    f"{structure_id}: "
                    f"{target} lacks reciprocal "
                    "supersedes"
                )

    return errors


def validate_document(
    target_name: str,
    schema_path: Path,
    document_path: Path,
) -> bool:
    """Validate one YAML document."""

    print(
        "\n[validate] "
        f"{document_path.relative_to(ROOT)}"
    )

    try:
        schema = load_json(schema_path)
        instance = load_yaml(document_path)

    except (
        OSError,
        json.JSONDecodeError,
        yaml.YAMLError,
    ) as error:
        print(
            f"[parse-error] {error}"
        )
        return False

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    schema_errors = sorted(
        validator.iter_errors(instance),
        key=lambda item: list(item.path),
    )

    if schema_errors:
        for error in schema_errors:
            print(
                "[schema-error] "
                f"{format_path(error)}: "
                f"{error.message}"
            )

        return False

    print("[schema-ok]")

    semantic_errors: list[str] = []

    if (
        target_name
        == "canonical-structure-registry"
        and isinstance(instance, dict)
    ):
        semantic_errors = (
            registry_semantic_errors(instance)
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
    """Validate all records and registries."""

    print(
        "=== Structural Precedence "
        "Ledger Validation ==="
    )

    failed = False
    validated = 0

    for (
        target_name,
        schema_path,
        directory,
    ) in TARGETS:
        print(
            f"\n[target] {target_name}"
        )

        print(
            "schema : "
            f"{schema_path.relative_to(ROOT)}"
        )

        if not schema_path.exists():
            print(
                "[fatal] Missing schema: "
                f"{schema_path}"
            )

            failed = True
            continue

        documents = yaml_files(directory)

        if not documents:
            print(
                "[fatal] No YAML documents in "
                f"{directory}"
            )

            failed = True
            continue

        for document_path in documents:
            validated += 1

            if not validate_document(
                target_name,
                schema_path,
                document_path,
            ):
                failed = True

    if failed:
        print("\nValidation failed.")
        return 1

    print(
        "\nAll documents are valid. "
        f"Validated: {validated}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
