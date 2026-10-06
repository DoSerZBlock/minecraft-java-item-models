#!/usr/bin/env python3
"""Static validator for GrayDay VFX task contracts."""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = {
    "project",
    "design",
    "spatial",
    "geometry",
    "orientation",
    "motion",
    "timeline",
    "lifecycle",
    "effects",
    "budget",
    "runtime",
    "output",
    "qa",
}

ALLOWED_AXES = {"+x", "-x", "+y", "-y", "+z", "-z"}
ALLOWED_SPACES = {
    "world_space",
    "caster_space",
    "view_space",
    "target_space",
    "velocity_space",
}
ALLOWED_FORWARD_SOURCES = {"look_direction", "velocity", "target_vector", "fixed"}

FORBIDDEN_DOMAIN_KEYS = {
    "damage",
    "base_damage",
    "healing",
    "healing_amount",
    "mana_cost",
    "resource_cost",
    "cooldown",
    "cooldown_seconds",
    "crit",
    "crit_chance",
    "crit_multiplier",
    "stat_scaling",
    "spell_power_scaling",
}

REQUIRED_QA_CASES = {
    "horizontal",
    "pitch_up",
    "pitch_down",
    "side_observation",
    "impact",
    "timeout",
    "disconnect",
    "cleanup",
}


class ValidationError(Exception):
    pass


def require_table(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    if not isinstance(value, dict):
        raise ValidationError(f"missing or invalid table [{name}]")
    return value


def require_nonempty_string(table: dict[str, Any], key: str, where: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{where}.{key} must be a non-empty string")
    return value.strip()


def require_bool(table: dict[str, Any], key: str, where: str) -> bool:
    value = table.get(key)
    if not isinstance(value, bool):
        raise ValidationError(f"{where}.{key} must be boolean")
    return value


def require_positive_number(table: dict[str, Any], key: str, where: str) -> float:
    value = table.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValidationError(f"{where}.{key} must be > 0")
    return float(value)


def walk_keys(value: Any, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_lower = str(key).lower()
            current = f"{path}.{key}" if path else str(key)
            if key_lower in FORBIDDEN_DOMAIN_KEYS:
                errors.append(
                    f"{current} is RPG domain data and must remain in GrayDay_Core"
                )
            errors.extend(walk_keys(child, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(walk_keys(child, f"{path}[{index}]"))
    return errors


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    missing = sorted(REQUIRED_SECTIONS - data.keys())
    if missing:
        errors.append("missing required sections: " + ", ".join(missing))
        return errors

    errors.extend(walk_keys(data))

    try:
        project = require_table(data, "project")
        require_nonempty_string(project, "id", "project")
        require_nonempty_string(project, "vfx_family", "project")
        require_nonempty_string(project, "minecraft_version", "project")

        spatial = require_table(data, "spatial")
        for key in ("spawn_space", "orientation_space", "target_space"):
            value = require_nonempty_string(spatial, key, "spatial")
            if value not in ALLOWED_SPACES:
                errors.append(
                    f"spatial.{key} must be one of {sorted(ALLOWED_SPACES)}, got {value!r}"
                )

        geometry = require_table(data, "geometry")
        forward_axis = require_nonempty_string(
            geometry, "asset_forward_axis", "geometry"
        )
        up_axis = require_nonempty_string(geometry, "asset_up_axis", "geometry")
        if forward_axis not in ALLOWED_AXES:
            errors.append(f"geometry.asset_forward_axis invalid: {forward_axis!r}")
        if up_axis not in ALLOWED_AXES:
            errors.append(f"geometry.asset_up_axis invalid: {up_axis!r}")
        if forward_axis.lstrip("+-") == up_axis.lstrip("+-"):
            errors.append("asset_forward_axis and asset_up_axis cannot use the same axis")
        require_nonempty_string(geometry, "origin", "geometry")
        require_positive_number(geometry, "max_extent", "geometry")

        orientation = require_table(data, "orientation")
        source = require_nonempty_string(
            orientation, "runtime_forward_source", "orientation"
        )
        if source not in ALLOWED_FORWARD_SOURCES:
            errors.append(
                "orientation.runtime_forward_source must be one of "
                + ", ".join(sorted(ALLOWED_FORWARD_SOURCES))
            )
        follow_pitch = require_bool(
            orientation, "follow_pitch", "orientation"
        )
        require_bool(orientation, "follow_yaw", "orientation")
        require_bool(orientation, "follow_roll", "orientation")
        require_bool(orientation, "invert_forward", "orientation")
        if follow_pitch and source == "fixed":
            errors.append(
                "follow_pitch=true is inconsistent with runtime_forward_source='fixed'"
            )

        timeline = require_table(data, "timeline")
        cast_start = timeline.get("cast_start_sec")
        release = timeline.get("release_sec")
        if not isinstance(cast_start, (int, float)) or isinstance(cast_start, bool):
            errors.append("timeline.cast_start_sec must be numeric")
        if not isinstance(release, (int, float)) or isinstance(release, bool):
            errors.append("timeline.release_sec must be numeric")
        if isinstance(cast_start, (int, float)) and isinstance(release, (int, float)):
            if release < cast_start:
                errors.append("timeline.release_sec must be >= cast_start_sec")
        require_nonempty_string(timeline, "impact_trigger", "timeline")
        require_positive_number(
            timeline, "aftermath_duration_sec", "timeline"
        )

        lifecycle = require_table(data, "lifecycle")
        lifetime = require_positive_number(
            lifecycle, "max_lifetime_ticks", "lifecycle"
        )
        for key in (
            "dispose_on_impact",
            "dispose_on_cancel",
            "dispose_on_disconnect",
            "dispose_on_shutdown",
        ):
            if not require_bool(lifecycle, key, "lifecycle"):
                errors.append(f"lifecycle.{key} must be true for GrayDay VFX")

        budget = require_table(data, "budget")
        require_positive_number(budget, "max_models_per_cast", "budget")
        require_positive_number(budget, "max_particles_per_tick", "budget")
        require_positive_number(
            budget, "max_active_instances_per_player", "budget"
        )
        budget_lifetime = require_positive_number(
            budget, "max_lifetime_ticks", "budget"
        )
        require_bool(budget, "allow_per_viewer_particles", "budget")
        if budget_lifetime < lifetime:
            errors.append(
                "budget.max_lifetime_ticks cannot be lower than lifecycle.max_lifetime_ticks"
            )

        runtime = require_table(data, "runtime")
        expected_runtime_values = {
            "presentation_runtime": "GrayDay_VFX",
            "asset_source": "GrayDay_Assets",
            "rpg_domain_source": "GrayDay_Core",
        }
        for key, expected in expected_runtime_values.items():
            value = require_nonempty_string(runtime, key, "runtime")
            if value != expected:
                errors.append(f"runtime.{key} must be {expected!r}")
        require_nonempty_string(runtime, "model_provider", "runtime")
        require_nonempty_string(runtime, "model_id", "runtime")

        output = require_table(data, "output")
        expected = output.get("expected")
        if (
            not isinstance(expected, list)
            or not expected
            or not all(isinstance(item, str) and item.strip() for item in expected)
        ):
            errors.append("output.expected must be a non-empty string array")

        qa = require_table(data, "qa")
        cases = qa.get("required_cases")
        if not isinstance(cases, list) or not all(isinstance(x, str) for x in cases):
            errors.append("qa.required_cases must be a string array")
        else:
            missing_cases = sorted(REQUIRED_QA_CASES - set(cases))
            if missing_cases:
                errors.append(
                    "qa.required_cases missing: " + ", ".join(missing_cases)
                )
        blocking = qa.get("blocking_rules")
        if (
            not isinstance(blocking, list)
            or not blocking
            or not all(isinstance(x, str) and x.strip() for x in blocking)
        ):
            errors.append("qa.blocking_rules must be a non-empty string array")

    except ValidationError as exc:
        errors.append(str(exc))

    return errors


def validate_path(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        print(f"FAIL {path}: {exc}")
        return False

    errors = validate(data)
    if errors:
        print(f"FAIL {path}")
        for error in errors:
            print(f"  - {error}")
        return False

    print(f"PASS {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tasks", nargs="+", type=Path)
    args = parser.parse_args()

    ok = True
    for task in args.tasks:
        ok = validate_path(task) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
