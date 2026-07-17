#!/usr/bin/env python3
"""Validate v0.3 Structure Lineage Graph documents.

This validator performs:

1. JSON Schema validation.
2. Registry-to-graph identity validation.
3. Duplicate node, edge, structure, and evidence detection.
4. Relationship chronology validation.
5. Influence-evidence consistency validation.
6. Directed lineage cycle detection.
"""

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


# Relationships whose direction represents lineage.
#
# The source node is generally the newer or derivative structure.
# The target node is generally the older or referenced structure.
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


# These relationships are treated as structurally symmetric.
# Reverse duplicates are therefore rejected.
SYMMETRIC_TYPES = {
    "independent_convergence",
    "partial_convergence",
    "conceptual_analogy",
    "related_to",
}


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON document."""

    with path.open("r", encoding="utf-8") as file:
        document = json.load(file)

    if not isinstance(document, dict):
        raise ValueError(
            f"Expected a JSON object in {path}"
        )

    return document


def load_yaml(path: Path) -> Any:
    """Load a YAML document."""

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def find_yaml_files(directory: Path) -> list[Path]:
    """Return sorted YAML documents from a directory."""

    if not directory.exists():
        return []

    return sorted(
        {
            *directory.glob("*.yaml"),
            *directory.glob("*.yml"),
        }
    )


def parse_datetime(value: str) -> datetime:
    """Parse an ISO 8601 datetime string."""

    normalized = value.replace(
        "Z",
        "+00:00",
    )

    return datetime.fromisoformat(normalized)


def duplicate_values(
    values: list[Any],
) -> set[Any]:
    """Return values appearing more than once."""

    return {
        value
        for value, count in Counter(values).items()
        if count > 1
    }


def format_schema_error_path(
    error: Any,
) -> str:
    """Format a JSON Schema error path using dot notation."""

    if not error.absolute_path:
        return "<root>"

    return ".".join(
        str(part)
        for part in error.absolute_path
    )


def build_registry_index(
    registry_document: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Build an index of canonical registry entries."""

    entries = registry_document.get("entries")

    if not isinstance(entries, list):
        raise ValueError(
            "Registry document must contain an entries array."
        )

    registry_index: dict[str, dict[str, Any]] = {}

    for position, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(
                "Registry entry at index "
                f"{position} is not an object."
            )

        structure_id = entry.get(
            "canonical_structure_id"
        )

        if not isinstance(structure_id, str):
            raise ValueError(
                "Registry entry at index "
                f"{position} has no valid "
                "canonical_structure_id."
            )

        if structure_id in registry_index:
            raise ValueError(
                "Duplicate canonical structure ID "
                f"in registry: {structure_id}"
            )

        registry_index[structure_id] = entry

    return registry_index


def find_directed_cycle(
    adjacency: dict[str, set[str]],
) -> list[str] | None:
    """Return one cycle from a directed graph, if present."""

    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node_id: str) -> list[str] | None:
        if node_id in visiting:
            cycle_start = stack.index(node_id)

            return [
                *stack[cycle_start:],
                node_id,
            ]

        if node_id in visited:
            return None

        visiting.add(node_id)
        stack.append(node_id)

        for target_id in sorted(
            adjacency.get(node_id, set())
        ):
            cycle = visit(target_id)

            if cycle is not None:
                return cycle

        stack.pop()
        visiting.remove(node_id)
        visited.add(node_id)

        return None

    for node_id in sorted(adjacency):
        cycle = visit(node_id)

        if cycle is not None:
            return cycle

    return None


def validate_unique_values(
    label: str,
    values: list[Any],
    errors: list[str],
) -> None:
    """Append duplicate-value errors."""

    for duplicate in sorted(
        duplicate_values(values)
    ):
        errors.append(
            f"duplicate {label}: {duplicate}"
        )


def validate_registry_node(
    node: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    """Validate one canonical graph node against the registry."""

    if node.get("node_kind") != "canonical_structure":
        return

    node_id = node["node_id"]
    structure_id = node["canonical_structure_id"]

    registry_entry = registry.get(structure_id)

    if registry_entry is None:
        errors.append(
            f"{node_id}: unknown canonical structure "
            f"{structure_id}"
        )
        return

    canonical_name = (
        registry_entry
        .get("canonical_name", {})
        .get("en")
    )

    if node["name"] != canonical_name:
        errors.append(
            f"{node_id}: name {node['name']!r} "
            "does not match registry canonical name "
            f"{canonical_name!r}"
        )

    registry_publication_time = (
        registry_entry
        .get("origin_binding", {})
        .get("first_publication_at")
    )

    if not isinstance(registry_publication_time, str):
        errors.append(
            f"{node_id}: registry entry "
            f"{structure_id} has no valid "
            "first_publication_at"
        )
        return

    try:
        graph_time = parse_datetime(
            node["first_publication_at"]
        )

        registry_time = parse_datetime(
            registry_publication_time
        )

    except ValueError as error:
        errors.append(
            f"{node_id}: invalid publication datetime: "
            f"{error}"
        )
        return

    if graph_time != registry_time:
        errors.append(
            f"{node_id}: first_publication_at "
            "does not match registry; "
            f"graph={node['first_publication_at']}, "
            f"registry={registry_publication_time}"
        )


def validate_influence_audit(
    edge: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate relationship type against influence evidence."""

    edge_id = edge["edge_id"]
    relationship_type = edge["relationship_type"]
    audit = edge["influence_audit"]

    access_evidence = audit["evidence_of_access"]
    citation_evidence = audit["evidence_of_citation"]
    direct_evidence = (
        audit["evidence_of_direct_influence"]
    )

    if relationship_type == "direct_influence":
        if direct_evidence != "documented":
            errors.append(
                f"{edge_id}: direct_influence requires "
                "documented direct-influence evidence"
            )

    if relationship_type == "probable_influence":
        if access_evidence not in {
            "indirect",
            "documented",
        }:
            errors.append(
                f"{edge_id}: probable_influence requires "
                "indirect or documented access evidence"
            )

        if direct_evidence == "documented":
            errors.append(
                f"{edge_id}: documented direct influence "
                "must use relationship_type "
                "direct_influence"
            )

    if relationship_type == "independent_convergence":
        if direct_evidence in {
            "indirect",
            "documented",
        }:
            errors.append(
                f"{edge_id}: direct-influence evidence "
                "conflicts with independent_convergence"
            )

        if citation_evidence == "documented":
            errors.append(
                f"{edge_id}: documented citation "
                "conflicts with independent_convergence"
            )


def graph_semantic_errors(
    graph: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> list[str]:
    """Apply semantic rules not expressible in JSON Schema."""

    errors: list[str] = []

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    if not isinstance(nodes, list):
        return ["nodes must be an array"]

    if not isinstance(edges, list):
        return ["edges must be an array"]

    node_ids = [
        node["node_id"]
        for node in nodes
    ]

    edge_ids = [
        edge["edge_id"]
        for edge in edges
    ]

    canonical_structure_ids = [
        node["canonical_structure_id"]
        for node in nodes
        if node["node_kind"] == "canonical_structure"
    ]

    external_structure_ids = [
        node["external_structure_id"]
        for node in nodes
        if node["node_kind"] == "external_structure"
    ]

    evidence_ids = [
        evidence["evidence_id"]
        for edge in edges
        for evidence in edge.get("evidence", [])
    ]

    validate_unique_values(
        "node_id",
        node_ids,
        errors,
    )

    validate_unique_values(
        "edge_id",
        edge_ids,
        errors,
    )

    validate_unique_values(
        "canonical_structure_id node",
        canonical_structure_ids,
        errors,
    )

    validate_unique_values(
        "external_structure_id node",
        external_structure_ids,
        errors,
    )

    validate_unique_values(
        "graph evidence_id",
        evidence_ids,
        errors,
    )

    if node_ids != sorted(node_ids):
        errors.append(
            "node IDs must be sorted in ascending order"
        )

    if edge_ids != sorted(edge_ids):
        errors.append(
            "edge IDs must be sorted in ascending order"
        )

    node_by_id = {
        node["node_id"]: node
        for node in nodes
    }

    for node in nodes:
        validate_registry_node(
            node,
            registry,
            errors,
        )

    directed_edge_keys: list[
        tuple[str, str, str]
    ] = []

    symmetric_edge_keys: set[
        tuple[str, tuple[str, str]]
    ] = set()

    lineage_adjacency: dict[str, set[str]] = {
        node_id: set()
        for node_id in node_ids
    }

    for edge in edges:
        edge_id = edge["edge_id"]
        source_id = edge["source_node_id"]
        target_id = edge["target_node_id"]
        relationship_type = edge["relationship_type"]

        if source_id not in node_by_id:
            errors.append(
                f"{edge_id}: unknown source node "
                f"{source_id}"
            )
            continue

        if target_id not in node_by_id:
            errors.append(
                f"{edge_id}: unknown target node "
                f"{target_id}"
            )
            continue

        if source_id == target_id:
            errors.append(
                f"{edge_id}: self-edge is not allowed"
            )
            continue

        directed_edge_keys.append(
            (
                source_id,
                relationship_type,
                target_id,
            )
        )

        if relationship_type in SYMMETRIC_TYPES:
            symmetric_key = (
                relationship_type,
                tuple(sorted((source_id, target_id))),
            )

            if symmetric_key in symmetric_edge_keys:
                errors.append(
                    f"{edge_id}: duplicate symmetric "
                    f"relationship between "
                    f"{source_id} and {target_id}"
                )
            else:
                symmetric_edge_keys.add(
                    symmetric_key
                )

        source_node = node_by_id[source_id]
        target_node = node_by_id[target_id]

        try:
            source_publication_time = parse_datetime(
                source_node["first_publication_at"]
            )

            target_publication_time = parse_datetime(
                target_node["first_publication_at"]
            )

            assertion_time = parse_datetime(
                edge["asserted_at"]
            )

        except ValueError as error:
            errors.append(
                f"{edge_id}: invalid datetime: {error}"
            )
            continue

        if relationship_type in LINEAGE_TYPES:
            lineage_adjacency[source_id].add(
                target_id
            )

            # In v0.3, lineage edges point from the later
            # or derivative structure to the earlier source.
            if source_publication_time < target_publication_time:
                errors.append(
                    f"{edge_id}: source node {source_id} "
                    f"predates target node {target_id} "
                    f"for relationship "
                    f"{relationship_type}"
                )

        if assertion_time < source_publication_time:
            errors.append(
                f"{edge_id}: assertion predates "
                f"source-node publication"
            )

        if assertion_time < target_publication_time:
            errors.append(
                f"{edge_id}: assertion predates "
                f"target-node publication"
            )

        validate_influence_audit(
            edge,
            errors,
        )

    validate_unique_values(
        "directed edge",
        directed_edge_keys,
        errors,
    )

    cycle = find_directed_cycle(
        lineage_adjacency
    )

    if cycle is not None:
        errors.append(
            "lineage cycle detected: "
            + " -> ".join(cycle)
        )

    return errors


def validate_graph_document(
    graph_path: Path,
    schema: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> bool:
    """Validate one Structure Lineage Graph document."""

    print(
        "\n[validate] "
        f"{graph_path.relative_to(ROOT)}"
    )

    try:
        graph_document = load_yaml(
            graph_path
        )

    except (
        OSError,
        yaml.YAMLError,
    ) as error:
        print(
            f"[parse-error] {error}"
        )
        return False

    if not isinstance(graph_document, dict):
        print(
            "[parse-error] "
            "Graph root must be a YAML mapping."
        )
        return False

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    schema_errors = sorted(
        validator.iter_errors(graph_document),
        key=lambda error: list(error.path),
    )

    if schema_errors:
        for error in schema_errors:
            print(
                "[schema-error] "
                f"{format_schema_error_path(error)}: "
                f"{error.message}"
            )

        return False

    print("[schema-ok]")

    semantic_errors = graph_semantic_errors(
        graph_document,
        registry,
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
    """Validate all v0.3 lineage graph files."""

    print(
        "=== Structure Lineage Graph Validation ==="
    )

    required_paths = (
        SCHEMA_PATH,
        REGISTRY_PATH,
    )

    for required_path in required_paths:
        if not required_path.exists():
            print(
                "[fatal] Missing required file: "
                f"{required_path.relative_to(ROOT)}"
            )
            return 2

    graph_paths = find_yaml_files(
        GRAPHS_DIR
    )

    if not graph_paths:
        print(
            "[fatal] No graph YAML files found in: "
            f"{GRAPHS_DIR.relative_to(ROOT)}"
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
                "Registry root must be a YAML mapping."
            )

        registry = build_registry_index(
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

    for graph_path in graph_paths:
        valid = validate_graph_document(
            graph_path,
            schema,
            registry,
        )

        if not valid:
            failed = True

    if failed:
        print("\nValidation failed.")
        return 1

    print(
        "\nAll lineage graphs are valid. "
        f"Validated: {len(graph_paths)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
