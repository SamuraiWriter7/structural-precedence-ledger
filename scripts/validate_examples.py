#!/usr/bin/env python3
"""Validate v0.3 structure lineage graphs."""

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
    / "structure-lineage-graph.schema.json"
)

REGISTRY_PATH = (
    ROOT
    / "registry"
    / "canonical-structures.yaml"
)

GRAPHS_DIR = ROOT / "graphs"


LINEAGE_TYPES = {
    "derived_from",
    "extends",
    "specializes",
    "generalizes",
    "implements",
    "integrates",
    "translates",
    "supersedes",
}


SYMMETRIC_TYPES = {
    "independent_convergence",
    "partial_convergence",
    "conceptual_analogy",
    "related_to",
}


def load_json(
    path: Path,
) -> dict[str, Any]:
    """Load a JSON document."""

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_yaml(
    path: Path,
) -> Any:
    """Load a YAML document."""

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file)


def parse_time(
    value: str,
) -> datetime:
    """Parse an ISO 8601 datetime."""

    return datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    )


def duplicates(
    values: list[Any],
) -> set[Any]:
    """Return values appearing more than once."""

    return {
        value
        for value, count
        in Counter(values).items()
        if count > 1
    }


def schema_error_path(
    error: Any,
) -> str:
    """Format a JSON Schema error path."""

    if not error.absolute_path:
        return "<root>"

    return ".".join(
        str(part)
        for part in error.absolute_path
    )


def find_cycle(
    adjacency: dict[str, set[str]],
) -> list[str] | None:
    """Return one directed lineage cycle."""

    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(
        node: str,
    ) -> list[str] | None:
        if node in visiting:
            start = stack.index(node)

            return (
                stack[start:]
                + [node]
            )

        if node in visited:
            return None

        visiting.add(node)
        stack.append(node)

        for target in sorted(
            adjacency.get(
                node,
                set(),
            )
        ):
            cycle = visit(target)

            if cycle:
                return cycle

        stack.pop()
        visiting.remove(node)
        visited.add(node)

        return None

    for node in sorted(adjacency):
        cycle = visit(node)

        if cycle:
            return cycle

    return None


def semantic_errors(
    graph: dict[str, Any],
    registry: dict[
        str,
        dict[str, Any],
    ],
) -> list[str]:
    """Apply cross-file graph rules."""

    errors: list[str] = []

    nodes = graph["nodes"]
    edges = graph["edges"]

    node_ids = [
        node["node_id"]
        for node in nodes
    ]

    edge_ids = [
        edge["edge_id"]
        for edge in edges
    ]

    canonical_ids = [
        node["canonical_structure_id"]
        for node in nodes
        if (
            node["node_kind"]
            == "canonical_structure"
        )
    ]

    external_ids = [
        node["external_structure_id"]
        for node in nodes
        if (
            node["node_kind"]
            == "external_structure"
        )
    ]

    evidence_ids = [
        evidence["evidence_id"]
        for edge in edges
        for evidence
        in edge["evidence"]
    ]

    for label, values in (
        (
            "node_id",
            node_ids,
        ),
        (
            "edge_id",
            edge_ids,
        ),
        (
            "canonical_structure_id",
            canonical_ids,
        ),
        (
            "external_structure_id",
            external_ids,
        ),
        (
            "evidence_id",
            evidence_ids,
        ),
    ):
        for duplicate in sorted(
            duplicates(values)
        ):
            errors.append(
                f"duplicate {label}: "
                f"{duplicate}"
            )

    if node_ids != sorted(node_ids):
        errors.append(
            "node IDs must be sorted"
        )

    if edge_ids != sorted(edge_ids):
        errors.append(
            "edge IDs must be sorted"
        )

    node_by_id = {
        node["node_id"]: node
        for node in nodes
    }

    for node in nodes:
        if (
            node["node_kind"]
            != "canonical_structure"
        ):
            continue

        node_id = node["node_id"]

        structure_id = (
            node[
                "canonical_structure_id"
            ]
        )

        entry = registry.get(
            structure_id
        )

        if entry is None:
            errors.append(
                f"{node_id}: "
                "unknown canonical structure "
                f"{structure_id}"
            )

            continue

        expected_name = (
            entry[
                "canonical_name"
            ]["en"]
        )

        expected_time = (
            entry[
                "origin_binding"
            ][
                "first_publication_at"
            ]
        )

        if node["name"] != expected_name:
            errors.append(
                f"{node_id}: "
                "name does not match registry"
            )

        if (
            parse_time(
                node[
                    "first_publication_at"
                ]
            )
            != parse_time(
                expected_time
            )
        ):
            errors.append(
                f"{node_id}: "
                "publication time does not "
                "match registry"
            )

    directed_keys: list[
        tuple[str, str, str]
    ] = []

    symmetric_keys: set[
        tuple[
            str,
            tuple[str, str],
        ]
    ] = set()

    adjacency = {
        node_id: set()
        for node_id in node_ids
    }

    for edge in edges:
        edge_id = edge["edge_id"]

        source_id = (
            edge["source_node_id"]
        )

        target_id = (
            edge["target_node_id"]
        )

        relation = (
            edge["relationship_type"]
        )

        if source_id not in node_by_id:
            errors.append(
                f"{edge_id}: "
                "unknown source node "
                f"{source_id}"
            )

            continue

        if target_id not in node_by_id:
            errors.append(
                f"{edge_id}: "
                "unknown target node "
                f"{target_id}"
            )

            continue

        if source_id == target_id:
            errors.append(
                f"{edge_id}: "
                "self-edge is not allowed"
            )

            continue

        directed_keys.append(
            (
                source_id,
                relation,
                target_id,
            )
        )

        if relation in SYMMETRIC_TYPES:
            symmetric_key = (
                relation,
                tuple(
                    sorted(
                        (
                            source_id,
                            target_id,
                        )
                    )
                ),
            )

            if (
                symmetric_key
                in symmetric_keys
            ):
                errors.append(
                    f"{edge_id}: "
                    "duplicate symmetric "
                    "relation"
                )
            else:
                symmetric_keys.add(
                    symmetric_key
                )

        if relation in LINEAGE_TYPES:
            adjacency[
                source_id
            ].add(
                target_id
            )

            source_time = parse_time(
                node_by_id[
                    source_id
                ][
                    "first_publication_at"
                ]
            )

            target_time = parse_time(
                node_by_id[
                    target_id
                ][
                    "first_publication_at"
                ]
            )

            if source_time < target_time:
                errors.append(
                    f"{edge_id}: "
                    "source predates target "
                    f"for {relation}"
                )

        assertion_time = parse_time(
            edge["asserted_at"]
        )

        for node_id in (
            source_id,
            target_id,
        ):
            publication_time = (
                parse_time(
                    node_by_id[
                        node_id
                    ][
                        "first_publication_at"
                    ]
                )
            )

            if (
                assertion_time
                < publication_time
            ):
                errors.append(
                    f"{edge_id}: "
                    "assertion predates "
                    f"{node_id}"
                )

        audit = (
            edge["influence_audit"]
        )

        access = (
            audit[
                "evidence_of_access"
            ]
        )

        citation = (
            audit[
                "evidence_of_citation"
            ]
        )

        direct = (
            audit[
                "evidence_of_direct_influence"
            ]
        )

        if (
            relation
            == "direct_influence"
            and direct
            != "documented"
        ):
            errors.append(
                f"{edge_id}: "
                "direct_influence requires "
                "documented direct evidence"
            )

        if (
            relation
            == "probable_influence"
        ):
            if access not in {
                "indirect",
                "documented",
            }:
                errors.append(
                    f"{edge_id}: "
                    "probable_influence "
                    "requires access evidence"
                )

            if direct == "documented":
                errors.append(
                    f"{edge_id}: "
                    "documented direct evidence "
                    "must use direct_influence"
                )

        if (
            relation
            == "independent_convergence"
        ):
            if direct in {
                "indirect",
                "documented",
            }:
                errors.append(
                    f"{edge_id}: "
                    "direct evidence conflicts "
                    "with independent_convergence"
                )

            if citation == "documented":
                errors.append(
                    f"{edge_id}: "
                    "documented citation conflicts "
                    "with independent_convergence"
                )

    for duplicate in sorted(
        duplicates(
            directed_keys
        )
    ):
        errors.append(
            "duplicate directed edge: "
            f"{duplicate[0]} "
            f"{duplicate[1]} "
            f"{duplicate[2]}"
        )

    cycle = find_cycle(
        adjacency
    )

    if cycle:
        errors.append(
            "lineage cycle detected: "
            + " -> ".join(cycle)
        )

    return errors


def validate_graph(
    path: Path,
    schema: dict[str, Any],
    registry: dict[
        str,
        dict[str, Any],
    ],
) -> bool:
    """Validate one graph document."""

    print(
        "\n[validate] "
        f"{path.relative_to(ROOT)}"
    )

    try:
        graph = load_yaml(path)

    except (
        OSError,
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
        validator.iter_errors(
            graph
        ),
        key=lambda item: list(
            item.path
        ),
    )

    if schema_errors:
        for error in schema_errors:
            print(
                "[schema-error] "
                f"{schema_error_path(error)}: "
                f"{error.message}"
            )

        return False

    print("[schema-ok]")

    errors = semantic_errors(
        graph,
        registry,
    )

    if errors:
        for error in errors:
            print(
                f"[semantic-error] "
                f"{error}"
            )

        return False

    print("[semantic-ok]")

    return True


def main() -> int:
    """Validate all lineage graphs."""

    print(
        "=== Structure Lineage "
        "Graph Validation ==="
    )

    for required_path in (
        SCHEMA_PATH,
        REGISTRY_PATH,
    ):
        if not required_path.exists():
            print(
                "[fatal] Missing file: "
                f"{required_path}"
            )

            return 2

    graph_paths = sorted(
        set(
            GRAPHS_DIR.glob(
                "*.yaml"
            )
        )
        | set(
            GRAPHS_DIR.glob(
                "*.yml"
            )
        )
    )

    if not graph_paths:
        print(
            "[fatal] "
            "No graph YAML files found."
        )

        return 2

    schema = load_json(
        SCHEMA_PATH
    )

    registry_document = load_yaml(
        REGISTRY_PATH
    )

    registry = {
        entry[
            "canonical_structure_id"
        ]: entry
        for entry
        in registry_document["entries"]
    }

    failed = False

    for graph_path in graph_paths:
        if not validate_graph(
            graph_path,
            schema,
            registry,
        ):
            failed = True

    if failed:
        print(
            "\nValidation failed."
        )

        return 1

    print(
        "\nAll lineage graphs "
        "are valid. "
        f"Validated: {len(graph_paths)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
