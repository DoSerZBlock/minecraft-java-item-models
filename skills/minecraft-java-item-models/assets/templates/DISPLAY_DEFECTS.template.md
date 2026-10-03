# DISPLAY_DEFECTS.template.md

Use one block per failed display view.

```text
DISPLAY-DEFECT-001
severity = blocking | major | minor
context = firstperson_righthand | firstperson_lefthand | thirdperson_righthand | thirdperson_lefthand | gui | ground | fixed
observation = exact visible problem
suspected_cause = rotation | translation | scale | base_geometry | origin | runtime
allowed_change = display_only | structural_revision
change_1 = measurable edit
change_2 = optional measurable edit
geometry_change = false
result = pending | pass | fail
```

Rules:
- No vague phrases such as "looks bad" or "make cooler".
- If `allowed_change = display_only`, do not edit base geometry.
- If geometry changes, re-run every display view.
