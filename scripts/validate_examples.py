#!/usr/bin/env python3
"""Validate Structural Precedence Ledger YAML examples against JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "schemas"
    / "structural-precedence-record.schema.json"
)
EXAMPLES_DIR = ROOT / "examples"


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file."""

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_yaml(path: Path) -> Any:
    """Load a YAML file."""

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def format_error_path(error: Any) -> str:
    """Convert a validation error path into readable dot notation."""

    if not error.absolute_path:
        return "<root>"

    return ".".join(
        str(part)
        for part in error.absolute_path
    )


def main() -> int:
    """Run validation for all YAML examples."""

    print("=== Structural Precedence Ledger Validation ===")
    print(
        "schema : "
        f"{SCHEMA_PATH.relative_to(ROOT)}"
    )

    if not SCHEMA_PATH.exists():
        print(
            f"[fatal] Schema not found: {SCHEMA_PATH}",
            file=sys.stderr,
        )
        return 2

    example_paths = (
        sorted(EXAMPLES_DIR.glob("*.yaml"))
        + sorted(EXAMPLES_DIR.glob("*.yml"))
    )

    if not example_paths:
        print(
            "[fatal] No YAML examples found.",
            file=sys.stderr,
        )
        return 2

    schema = load_json(SCHEMA_PATH)

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    failed = False

    for example_path in example_paths:
        print(
            "\n[validate] "
            f"{example_path.relative_to(ROOT)}"
        )

        instance = load_yaml(example_path)

        errors = sorted(
            validator.iter_errors(instance),
            key=lambda item: list(item.path),
        )

        if errors:
            failed = True

            for error in errors:
                print(
                    "[error] "
                    f"{format_error_path(error)}: "
                    f"{error.message}"
                )
        else:
            print("[schema-ok]")

    if failed:
        print("\nValidation failed.")
        return 1

    print("\nAll examples are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
