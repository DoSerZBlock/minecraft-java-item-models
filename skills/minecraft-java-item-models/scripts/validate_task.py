#!/usr/bin/env python3
import sys, re
from pathlib import Path
import tomllib

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
ALLOWED_PARTS = {"cube", "group", "bone", "plane", "mesh", "locator"}
ALLOWED_FORMATS = {
    "java_block_item", "geckolib_item", "geckolib_armor", "geckolib_entity",
    "bedrock_entity", "modded_entity", "generic_reference_only"
}

def vec3(v, label, errors):
    ok = isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) for x in v)
    if not ok:
        errors.append(f"{label} must be a numeric 3-vector")
    return ok

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_task.py <task.toml>")
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 2
    with path.open("rb") as f:
        data = tomllib.load(f)

    errors, warnings = [], []
    project = data.get("project", {})
    for k in ["id", "name", "target", "blockbench_format", "units", "phase"]:
        if not project.get(k): errors.append(f"project.{k} is required")
    fmt = project.get("blockbench_format")
    if fmt and fmt not in ALLOWED_FORMATS:
        warnings.append(f"unknown format in validator set: {fmt}")

    bounds = data.get("bounds", {})
    bmin, bmax = bounds.get("min"), bounds.get("max")
    if vec3(bmin, "bounds.min", errors) and vec3(bmax, "bounds.max", errors):
        for i, a in enumerate("xyz"):
            if bmin[i] >= bmax[i]: errors.append(f"bounds {a}: min must be < max")

    budget = data.get("budget", {})
    for k in ["max_cubes", "max_bones", "max_planes"]:
        if not isinstance(budget.get(k), int) or budget[k] < 0:
            errors.append(f"budget.{k} must be a non-negative integer")
    md = budget.get("min_detail_unit", 0)
    if not isinstance(md, (int, float)) or md < 0:
        errors.append("budget.min_detail_unit must be >= 0")

    tex = data.get("texture", {})
    for k in ["width", "height"]:
        if not isinstance(tex.get(k), int) or tex[k] <= 0:
            errors.append(f"texture.{k} must be a positive integer")
    for pname, pobj in tex.get("palette", {}).items():
        for c in pobj.get("colors", []):
            if not isinstance(c, str) or not HEX.match(c):
                errors.append(f"invalid color in palette {pname}: {c!r}")

    parts = data.get("parts", [])
    ids, cube_count, bone_count, plane_count = [], 0, 0, 0
    for i, p in enumerate(parts):
        pid, kind = p.get("id"), p.get("kind")
        if not pid:
            errors.append(f"parts[{i}].id is required"); continue
        if pid in ids: errors.append(f"duplicate part id: {pid}")
        ids.append(pid)
        if kind not in ALLOWED_PARTS: errors.append(f"part {pid}: unknown kind {kind!r}")
        if kind == "cube":
            cube_count += 1
            f, t = p.get("from"), p.get("to")
            if vec3(f, f"part {pid}.from", errors) and vec3(t, f"part {pid}.to", errors):
                for ax, name in enumerate("xyz"):
                    d = t[ax] - f[ax]
                    if d <= 0: errors.append(f"part {pid}: {name} dimension must be > 0")
                    elif not budget.get("allow_subpixel_geometry", False) and d + 1e-9 < md:
                        errors.append(f"part {pid}: {name} dimension {d} < min_detail_unit {md}")
                    if isinstance(bmin, list) and isinstance(bmax, list) and len(bmin)==3 and len(bmax)==3:
                        if f[ax] < bmin[ax] or t[ax] > bmax[ax]:
                            warnings.append(f"part {pid}: exceeds declared {name} bounds")
        elif kind == "bone": bone_count += 1
        elif kind == "plane": plane_count += 1
        if "pivot" in p: vec3(p["pivot"], f"part {pid}.pivot", errors)
        if "rotation" in p: vec3(p["rotation"], f"part {pid}.rotation", errors)
        if kind not in {"group", "bone", "locator"} and not p.get("purpose"):
            warnings.append(f"part {pid}: no purpose documented")

    idset = set(ids)
    for p in parts:
        parent = p.get("parent", "")
        if parent and parent not in idset:
            errors.append(f"part {p.get('id')}: parent '{parent}' does not exist")
    if cube_count > budget.get("max_cubes", 10**9): errors.append("cube budget exceeded")
    if bone_count > budget.get("max_bones", 10**9): errors.append("bone budget exceeded")
    if plane_count > budget.get("max_planes", 10**9): errors.append("plane budget exceeded")

    for ctx, obj in data.get("display", {}).items():
        for k in ["rotation", "translation", "scale"]:
            if k in obj: vec3(obj[k], f"display.{ctx}.{k}", errors)

    anim_ids = set()
    for i, a in enumerate(data.get("animations", [])):
        aid = a.get("id")
        if not aid: errors.append(f"animations[{i}].id is required"); continue
        if aid in anim_ids: errors.append(f"duplicate animation id: {aid}")
        anim_ids.add(aid)
        if not isinstance(a.get("length"), (int, float)) or a["length"] <= 0:
            errors.append(f"animation {aid}: length must be > 0")

    expected = data.get("output", {}).get("expected", [])
    if not expected: errors.append("output.expected must contain at least one path")
    if not data.get("qa", {}).get("required_views", []): warnings.append("qa.required_views is empty")

    print(f"Task: {path}")
    print(f"Format: {fmt}")
    print(f"Parts: {len(parts)} | cubes={cube_count} bones={bone_count} planes={plane_count}")
    print(f"Animations: {len(anim_ids)} | Expected outputs: {len(expected)}")
    for w in warnings: print("WARNING:", w)
    for e in errors: print("ERROR:", e)
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS: 0 errors, {len(warnings)} warning(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
